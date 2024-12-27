
import pandas as pd
import numpy as np
import pickle
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List
import streamlit as st

PATH_TO_CSV_FILE = 'static/test_sessions.csv'
PATH_TO_FORMATTED_JSON = 'fomratted.json'

df = pd.read_csv(PATH_TO_CSV_FILE)

def transform_to_json(df):
    # Создаем пустой список для хранения результатов
    result = []

    # Проходим по каждой строке DataFrame
    for _, row in df.iterrows():
        # Создаем словарь для текущей строки
        # row_data = {'session_id': row['session_id'], 'events': []}
        row_data = []
        
        # Добавляем пары site и time
        for i in range(1, 11):  # 1 до 10
            site = row[f'site{i}']
            time = row[f'time{i}']
            if pd.notna(site) and pd.notna(time):  # Проверяем, что значения не NaN
                # row_data['events'].append({'site': site, 'time': time})
                row_data.append({'site': site, 'time': time})
        
        # Добавляем текущую строку в результат
        result.append(row_data)

    # Преобразуем список в JSON
    return json.dumps(result, indent=4)

def preprocessing(json_file_name: str, site_dic_file_name: str, top_fraud_sites: List) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    with open(f'{json_file_name}', 'r') as file:
        data = json.load(file)
        flat_data = [entry for session in data for entry in session]
        result_df = pd.DataFrame(flat_data)

    most_popular_sites = result_df['site'].value_counts().sort_values(ascending=False)
    most_popular_sites = most_popular_sites.to_frame().reset_index()
    most_popular_sites['cumulative_count'] = most_popular_sites['count'].cumsum()
    total_requests = most_popular_sites["count"].sum()
    most_popular_sites["cumulative_fraction"] = most_popular_sites["cumulative_count"] / total_requests  
    df_filtered = most_popular_sites[most_popular_sites["cumulative_fraction"] <= 0.95] # Ограничиваем до 95%

    with open(f'{site_dic_file_name}', 'rb') as file:
        site_dic = pickle.load(file)
        id_to_site = {v:k for (k,v) in site_dic.items()}
        id_to_site[0] = 'unknown'

    sum_queries = most_popular_sites['count'].sum()
    most_popular_sites['site_name']  = most_popular_sites['site'].map(id_to_site)
    most_popular_sites['part_of_all_queries'] = most_popular_sites['count'] / sum_queries
    top_popular_sites = most_popular_sites[most_popular_sites['part_of_all_queries'] >= 0.01][['site_name', 'part_of_all_queries','cumulative_fraction']]
    top_popular_sites['is_fraud'] = top_popular_sites['site_name'].isin(top_fraud_sites)
    result_df['site_name']  = result_df['site'].map(id_to_site)

    result_df['is_fraud'] = result_df['site_name'].isin(top_fraud_sites)
    result_df['time'] = pd.to_datetime(result_df['time'])
    result_df['day_time'] = (result_df['time'].dt.hour + result_df['time'].dt.minute / 60) 
    return result_df, most_popular_sites, df_filtered, top_popular_sites, result_df



def clics_per_site(df_filtered: pd.DataFrame) -> None:
    threshold = 80

    # Находим индекс пересечения (где cumulative_fraction * 100 >= 80)
    intersection_index = df_filtered[df_filtered["cumulative_fraction"] * 100 >= threshold].index[0]

    # Координаты точки пересечения
    x_intersect = intersection_index
    y_intersect = df_filtered.loc[intersection_index, "cumulative_fraction"] * 100

    # Построение графика
    fig, ax = plt.subplots(figsize=(10, 6))  # Создаем фигуру и оси
    ax.plot(
        df_filtered.index,
        df_filtered["cumulative_fraction"] * 100,
        label="Функция распределения"
    )
    ax.axhline(y=threshold, color="red", linestyle="--", label=f"{threshold}% порог")
    ax.axvline(x=x_intersect, color="red", linestyle="--")
    ax.text(
        x_intersect, 0, f"{x_intersect}", 
        color="grey", fontsize=10, ha="center", va="top"
    )

    ax.set_title("Распределение запросов по сайтам")
    ax.set_xlabel("Количество сайтов")
    ax.set_ylabel("Процент от общего числа запросов")
    ax.legend()
    ax.grid()

    # Отображаем график через Streamlit
    st.pyplot(fig)

def distribution_clics(top_popular_sites: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(8, 6))

    ax1.bar(
        top_popular_sites["site_name"], 
        top_popular_sites["part_of_all_queries"], 
        color="skyblue", 
        label="Доля запросов"
    )
    ax1.set_xlabel("Сайты", fontsize=12)
    ax1.set_ylabel("Доля каждого сайта", fontsize=12)
    ax1.tick_params(axis="x", rotation=45, labelsize=10)
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(
        top_popular_sites["site_name"], 
        top_popular_sites["cumulative_fraction"], 
        color="red", 
        marker="o", 
        label="Накопительная доля"
    )
    ax2.set_ylabel("Накопительная доля", fontsize=12)
    ax2.legend(loc="upper right")

    ax1.set_title("Распределение долей запросов по сайтам", fontsize=14)
    ax1.grid(axis="y", linestyle="--", alpha=0.7)

    plt.tight_layout()

    # Передача графика в Streamlit
    st.pyplot(fig)


def fraud_distributions(top_popular_sites: pd.DataFrame, result_df: pd.DataFrame) -> None:
    # Построение барплота для распределения
    fraud_distrib = top_popular_sites["is_fraud"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(
        x=fraud_distrib.index, 
        y=fraud_distrib.values, 
        palette=["blue", "red"], 
        ax=ax
    )
    ax.set_title("Распределение мошеннических и добросовестных сайтов \n среди самых популярных", fontsize=14)
    ax.set_xlabel("Тип сайта", fontsize=12)
    ax.set_ylabel("Количество", fontsize=12)
    st.pyplot(fig)

    # Построение KDE-графика
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.kdeplot(
        data=result_df, 
        x="day_time", 
        hue="is_fraud", 
        fill=True, 
        common_norm=False,  # Отдельная нормализация для каждой группы
        palette=["blue", "red"],
        alpha=0.6,
        ax=ax
    )
    ax.set_title("Плотность распределения запросов по времени", fontsize=14)
    ax.set_xlabel("Часы", fontsize=12)
    ax.set_ylabel("Плотность", fontsize=12)
    ax.legend(title="Тип сайта", labels=["Добросовестные", "Мошеннические"])
    ax.grid(alpha=0.5)
    st.pyplot(fig)

    # Настройка графика
    plt.title("Плотность распределения запросов по времени", fontsize=14)
    plt.xlabel("Часы", fontsize=12)
    plt.ylabel("Плотность", fontsize=12)
    plt.legend(title="Тип сайта", labels=["Добросовестные", "Мошеннические"])
    plt.grid(alpha=0.5)

    # Показ графика
    plt.show()




top_fraud_sites = ['www.google.fr', 'unknown', 'www.google.com', 'annotathon.org', 'apis.google.com', 'www.facebook.com',
                    'www.bing.com', 'blast.ncbi.nl`m.nih.gov', 'www.ncbi.nlm.nih.gov', 'clients1.google.com']

