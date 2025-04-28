import streamlit as st
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
import joblib

# Загрузка модели и скейлера
model = joblib.load("xgb_model.pkl")
scaler = joblib.load("scaler.pkl")

st.title("Предсказание: сдаст ли Влад экзамен?")

# Интерфейс ввода данных
st.sidebar.header("🔎 Введите данные")
Контрольная_1 = st.sidebar.slider("Оценка за контрольную 1", 0, 10, 7)
Контрольная_2 = st.sidebar.slider("Оценка за контрольную 2", 0, 10, 7)
Контрольная_3 = st.sidebar.slider("Оценка за контрольную 3", 0, 10, 7)
Сон = st.sidebar.selectbox("Сон накануне", ["Хороший", "Плохой"])
Настроение = st.sidebar.selectbox("Настроение", ["Хорошее", "Плохое"])
Энергетики = st.sidebar.selectbox("Пил энергетики накануне?", ["Да", "Нет"])
Посещаемость = st.sidebar.slider("Посещаемость занятий (%)", 0, 100, 80)
Время_подготовки = st.sidebar.slider("Время подготовки (часы)", 0, 20, 5)

# Кнопка запуска предсказания
if st.sidebar.button("🚀 Запустить предсказание"):
    # Подготовка данных
    input_dict = {
        "Контрольная 1": Контрольная_1,
        "Контрольная 2": Контрольная_2,
        "Контрольная 3": Контрольная_3,
        "Сон накануне": 1 if Сон == "Хороший" else 0,
        "Настроение": 1 if Настроение == "Хорошее" else 0,
        "Энергетиков накануне": 1 if Энергетики == "Да" else 0,
        "Посещаемость занятий": Посещаемость,
        "Время подготовки": Время_подготовки,
    }

    df_input = pd.DataFrame([input_dict])

    # Генерация новых признаков
    df_input["Средний балл"] = df_input[["Контрольная 1", "Контрольная 2", "Контрольная 3"]].mean(axis=1)
    df_input["Сумма баллов"] = df_input[["Контрольная 1", "Контрольная 2", "Контрольная 3"]].sum(axis=1)
    df_input["Эффективность_подготовки"] = df_input["Сумма баллов"] / (df_input["Время подготовки"] + 1)

    # Масштабирование признаков
    expected_features = [
        "Контрольная 1",
        "Контрольная 2",
        "Контрольная 3",
        "Сон накануне",
        "Настроение",
        "Энергетиков накануне",
        "Посещаемость занятий",
        "Время подготовки",
        "Средний балл",
        "Сумма баллов",
        "Эффективность_подготовки"
    ]

    scaled_input = scaler.transform(df_input[expected_features])

    # Предсказание
    pred_prob = model.predict_proba(scaled_input)[0][1]
    pred = model.predict(scaled_input)[0]

    # Вывод результатов
    st.subheader("📊 Итоговое предсказание")
    if pred:
        st.success(f"✅ Влад скорее всего сдаст экзамен! Уверенность: **{pred_prob:.2%}**")
    else:
        st.error(f"❌ Влад, увы, скорее не сдаст. Уверенность: **{1 - pred_prob:.2%}**")

    # Анализ данных
    st.subheader("📉 Анализ введенных данных")
    st.dataframe(df_input)

    st.subheader("Основные показатели")
    st.metric(label="Средний балл", value=f"{df_input['Средний балл'].values[0]:.2f}")
    st.metric(label="Сумма баллов", value=f"{df_input['Сумма баллов'].values[0]:.2f}")
    st.metric(label="Эффективность подготовки", value=f"{df_input['Эффективность_подготовки'].values[0]:.2f}")