# ml-service/main.py
from fastapi import FastAPI, UploadFile, HTTPException
import pandas as pd
import pickle
from io import BytesIO

app = FastAPI()

# Загрузка модели и словаря сайтов
with open('./static/site_dic.pkl', 'rb') as file:
    site_dic = pickle.load(file)
id_to_site = {v: k for (k, v) in site_dic.items()}
id_to_site[0] = 'unknown'

with open('./static/log_reg_model.pkl', 'rb') as file:
    loaded_model = pickle.load(file)

top_alice_sites = ['i1.ytimg.com', 's.youtube.com', 'www.youtube.com', 'www.facebook.com', 'www.google.fr',
                   'r4---sn-gxo5uxg-jqbe.googlevideo.com', 'apis.google.com', 'r1---sn-gxo5uxg-jqbe.googlevideo.com',
                   's.ytimg.com', 'r2---sn-gxo5uxg-jqbe.googlevideo.com']

top_fraud_sites = ['www.google.fr', 'unknown', 'www.google.com', 'annotathon.org', 'apis.google.com', 'www.facebook.com',
                   'www.bing.com', 'blast.ncbi.nlm.nih.gov', 'www.ncbi.nlm.nih.gov', 'clients1.google.com']


def time_features(train_sessions):
    train_sessions['weekday'] = train_sessions['time1'].dt.dayofweek
    train_sessions['hour'] = train_sessions['time1'].dt.hour
    train_sessions['month'] = train_sessions['time1'].dt.month
    train_sessions['morning'] = ((train_sessions.hour >= 6) & (train_sessions.hour < 12)).astype(int)
    train_sessions['evening'] = ((train_sessions.hour >= 18) & (train_sessions.hour < 24)).astype(int)
    train_sessions['time_diff'] = (train_sessions['time10'] - train_sessions['time1']).dt.total_seconds()
    train_sessions['time_diff'] = train_sessions['time_diff'].fillna(0).astype(int)


def calculate_top_site_fraction(session, top_sites):
    session_sites = session.dropna().values
    top_sites_count = sum(site in top_sites for site in session_sites)
    return (top_sites_count / len(session_sites)) * 10 if len(session_sites) > 0 else 0


def preproc_pred(test_sessions):
    sites = [col for col in test_sessions.columns if col.startswith('site')]
    sites_names = [str(elem) + "_name" for elem in sites]

    for site in sites:
        test_sessions[f'{site}_name'] = test_sessions[site].map(id_to_site).fillna('unknown')

    test_sessions[sites] = test_sessions[sites].fillna(0).astype(int)

    time_col = ['time%s' % i for i in range(1, 11)]
    test_sessions[time_col] = test_sessions[time_col].apply(pd.to_datetime)
    time_features(test_sessions)

    test_sessions['unique_sites_count'] = test_sessions[sites].nunique(axis=1)
    test_sessions['alice_top10_fraction'] = test_sessions[sites_names].apply(lambda row: calculate_top_site_fraction(row, top_alice_sites), axis=1)
    test_sessions['fraud_top10_fraction'] = test_sessions[sites_names].apply(lambda row: calculate_top_site_fraction(row, top_fraud_sites), axis=1)

    time_columns_to_drop = test_sessions.columns[test_sessions.columns.str.startswith('time')]
    time_columns_to_drop = time_columns_to_drop[time_columns_to_drop != 'time_diff']
    test_sessions.drop(columns=time_columns_to_drop, inplace=True)
    test_sessions.drop(columns=test_sessions.columns[test_sessions.columns.str.endswith('_name')], inplace=True)
    test_sessions.drop(['hour'], axis=1, inplace=True)
    test_sessions.drop(sites, axis=1, inplace=True)

    time_diff_column = test_sessions.pop('time_diff')
    test_sessions['time_diff'] = time_diff_column

    return loaded_model.predict_proba(test_sessions)


@app.post("/predict/")
async def predict(file: UploadFile):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a CSV.")

    try:
        # Чтение CSV в DataFrame
        content = await file.read()
        test_sessions = pd.read_csv(BytesIO(content))

        # Предикты
        predictions = [prediction[1] for prediction in preproc_pred(test_sessions)]
        return {"predictions": predictions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
