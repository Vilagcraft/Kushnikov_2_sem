import os
import matplotlib

# ----- НАСТРОЙКА MATPLOTLIB ДЛЯ СТАБИЛЬНОЙ РАБОТЫ НА RENDER -----
matplotlib.use('Agg')
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib_cache'

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# ---------------------- НАСТРОЙКА СТРАНИЦЫ ----------------------
st.set_page_config(
    page_title="Моделирование лингвистических опросов",
    page_icon="📊",
    layout="wide"
)

# ---------------------- ФУНКЦИЯ ПРИМЕНЕНИЯ СТИЛЯ В ЗАВИСИМОСТИ ОТ ТЕМЫ STREAMLIT ----------------------
def apply_theme_style():
    """Применяет стиль matplotlib в зависимости от текущей темы Streamlit."""
    try:
        theme = st.get_option("theme.base")
    except:
        theme = "light"
    
    if theme == "dark":
        plt.style.use('dark_background')
        plt.rcParams.update({
            'text.color': 'white',
            'axes.labelcolor': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'axes.edgecolor': 'white',
            'grid.color': 'gray',
            'grid.alpha': 0.3,
            'figure.facecolor': '#0e1117',
            'axes.facecolor': '#0e1117'
        })
    else:
        plt.style.use('default')
        plt.rcParams.update({
            'text.color': 'black',
            'axes.labelcolor': 'black',
            'xtick.color': 'black',
            'ytick.color': 'black',
            'axes.edgecolor': 'black',
            'grid.color': 'gray',
            'grid.alpha': 0.3,
            'figure.facecolor': 'white',
            'axes.facecolor': 'white'
        })

# ---------------------- ОПИСАНИЕ МОДЕЛИ ----------------------
with st.expander("📖 Описание модели", expanded=True):
    st.markdown("""
    **Цель моделирования**  
    Имитация опроса пользователей, оценивающих качество хранилища данных с помощью **лингвистической шкалы**:
    - Очень плохо (1)
    - Плохо (2)
    - Средне (3)
    - Хорошо (4)
    - Отлично (5)

    **Как это работает**  
    - Оценка каждого пользователя генерируется из **нормального распределения** с заданными параметрами (`среднее значение`, `стандартное отклонение`).
    - Опрос проводится **по тактам** – каждый такт моделирует новый опрос.
    - Пользователи разделены на **возрастные группы** (молодые, средние, пожилые). Для каждой группы можно настроить свои параметры.
    """)

# ---------------------- ЛИНГВИСТИЧЕСКАЯ ШКАЛА ----------------------
LINGUISTIC_SCALE = {
    1: "Очень плохо",
    2: "Плохо",
    3: "Средне",
    4: "Хорошо",
    5: "Отлично"
}

# ---------------------- ФУНКЦИЯ ГЕНЕРАЦИИ ОЦЕНОК ----------------------
def generate_ratings(n_users, mean, std, seed=None):
    if seed is not None:
        np.random.seed(seed)
    raw = np.random.normal(loc=mean, scale=std, size=n_users)
    ratings = np.round(raw).clip(1, 5).astype(int)
    freq = Counter(ratings)
    return ratings, freq

# ---------------------- БОКОВАЯ ПАНЕЛЬ ----------------------
st.sidebar.header("⚙️ Параметры моделирования")

num_ticks = st.sidebar.slider("Количество тактов", min_value=1, max_value=10, value=3, step=1)

use_seed = st.sidebar.checkbox("Использовать фиксированное начальное число", value=True)
seed_val = st.sidebar.number_input(
    "Начальное число для генератора случайных чисел (0–1000)",
    min_value=0, max_value=1000, value=42, step=1
) if use_seed else 0

st.sidebar.subheader("👥 Возрастные группы")
groups = {
    "Молодые (18-30)": {"mean": 2.8, "std": 1.0, "size": 20},
    "Средние (31-50)": {"mean": 3.2, "std": 1.0, "size": 20},
    "Пожилые (51+)": {"mean": 3.8, "std": 0.9, "size": 20}
}

group_colors = {
    "Молодые (18-30)": "#FFA500",
    "Средние (31-50)": "#2E8B57",
    "Пожилые (51+)": "#1E90FF"
}

for name in groups:
    with st.sidebar.expander(f"Настройки группы: {name}"):
        groups[name]["mean"] = st.number_input(
            f"Среднее значение (1.0–5.0)", min_value=1.0, max_value=5.0,
            value=groups[name]["mean"], step=0.1, key=f"mean_{name}"
        )
        groups[name]["std"] = st.number_input(
            f"Стандартное отклонение (0.3–2.0)", min_value=0.3, max_value=2.0,
            value=groups[name]["std"], step=0.1, key=f"std_{name}"
        )
        groups[name]["size"] = st.number_input(
            f"Размер группы", min_value=1, max_value=100,
            value=groups[name]["size"], step=1, key=f"size_{name}"
        )

# ---------------------- ЗАПУСК МОДЕЛИРОВАНИЯ ----------------------
if st.sidebar.button("🚀 Запустить моделирование", type="primary"):
    all_results = []
    avg_by_group = {name: [] for name in groups}
    tick_data = {}

    for tick in range(1, num_ticks + 1):
        current_seed = seed_val + tick if use_seed else None
        tick_data[tick] = {}
        for group_name, params in groups.items():
            ratings, freq = generate_ratings(
                params["size"], params["mean"], params["std"], current_seed
            )
            avg_score = np.mean(ratings)
            avg_by_group[group_name].append(avg_score)
            tick_data[tick][group_name] = (ratings, freq)

            dist_str = ", ".join(
                [f"{LINGUISTIC_SCALE[cat]}: {freq.get(cat, 0)}" for cat in sorted(LINGUISTIC_SCALE)]
            )
            all_results.append({
                "Такт": tick,
                "Возрастная группа": group_name,
                "Распределение оценок": dist_str,
                "Средний балл": round(avg_score, 2)
            })

    st.session_state['results'] = all_results
    st.session_state['avg_by_group'] = avg_by_group
    st.session_state['tick_data'] = tick_data
    st.session_state['num_ticks'] = num_ticks
    st.session_state['groups'] = list(groups.keys())
    st.session_state['run'] = True

# ---------------------- ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ ----------------------
if st.session_state.get('run', False):
    all_results = st.session_state['results']
    avg_by_group = st.session_state['avg_by_group']
    tick_data = st.session_state['tick_data']
    num_ticks = st.session_state['num_ticks']
    group_names = st.session_state['groups']

    st.header("📋 Результаты моделирования")

    # 1. Таблица
    st.subheader("📊 Таблица результатов по тактам и группам")
    df = pd.DataFrame(all_results)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # 2. Динамика средней оценки по группам
    st.subheader("📈 Динамика средней оценки по тактам")
    apply_theme_style()  # <-- применяем стиль перед графиком
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    for group_name, avgs in avg_by_group.items():
        color = group_colors.get(group_name, "gray")
        ax1.plot(range(1, num_ticks + 1), avgs, marker='o', label=group_name, color=color, linewidth=2)
    ax1.set_xlabel("Такт")
    ax1.set_ylabel("Средняя оценка (баллы)")
    ax1.set_title("Изменение средней оценки по тактам")
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend()
    st.pyplot(fig1)

    # 3. Детальная динамика по каждой группе
    st.subheader("📉 Детальная динамика по каждой группе")
    cols = st.columns(len(group_names))
    for idx, group_name in enumerate(group_names):
        avgs = avg_by_group[group_name]
        color = group_colors.get(group_name, "gray")
        apply_theme_style()  # <-- перед каждым маленьким графиком
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        ax2.plot(range(1, num_ticks + 1), avgs, marker='s', color=color, linewidth=2)
        ax2.set_xlabel("Такт")
        ax2.set_ylabel("Средний балл")
        ax2.set_title(group_name)
        ax2.grid(True, linestyle=':')
        with cols[idx]:
            st.pyplot(fig2)

    # 4. Общее распределение оценок (все такты, все группы)
    st.subheader("📊 Общее распределение оценок (все такты, все группы)")
    all_ratings = []
    for tick in tick_data:
        for group_name in tick_data[tick]:
            ratings, _ = tick_data[tick][group_name]
            all_ratings.extend(ratings)
    overall_counter = Counter(all_ratings)
    categories = [LINGUISTIC_SCALE[i] for i in range(1, 6)]
    counts = [overall_counter.get(i, 0) for i in range(1, 6)]

    apply_theme_style()
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    try:
        theme = st.get_option("theme.base")
    except:
        theme = "light"
    bar_color = "#3498db" if theme == "light" else "#5dade2"
    bars = ax3.bar(categories, counts, color=bar_color)
    ax3.set_xlabel("Оценка")
    ax3.set_ylabel("Количество голосов")
    ax3.set_title("Общее распределение оценок")
    ax3.set_ylim(0, max(counts) * 1.1 if max(counts) > 0 else 1)
    for bar, count in zip(bars, counts):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(count), ha='center', va='bottom')
    st.pyplot(fig3)

    # 5. Детализация по выбранному такту
    st.subheader("🔍 Детализация по выбранному такту")
    selected_tick = st.selectbox("Выберите такт для анализа", options=list(range(1, num_ticks + 1)))
    if selected_tick:
        st.write(f"### Такт {selected_tick}")

        tick_ratings = []
        group_details = []
        for group_name in group_names:
            ratings, freq = tick_data[selected_tick][group_name]
            tick_ratings.extend(ratings)
            group_details.append({
                "Группа": group_name,
                "Средний балл": round(np.mean(ratings), 2),
                **{LINGUISTIC_SCALE[i]: freq.get(i, 0) for i in range(1, 6)}
            })
        tick_counter = Counter(tick_ratings)

        categories_tick = [LINGUISTIC_SCALE[i] for i in range(1, 6)]
        counts_tick = [tick_counter.get(i, 0) for i in range(1, 6)]

        apply_theme_style()
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        bar_color_tick = "#e67e22" if theme == "light" else "#f39c12"
        bars = ax4.bar(categories_tick, counts_tick, color=bar_color_tick)
        ax4.set_xlabel("Оценка")
        ax4.set_ylabel("Количество голосов")
        ax4.set_title(f"Распределение оценок в такте {selected_tick}")
        ax4.set_ylim(0, max(counts_tick) * 1.1 if max(counts_tick) > 0 else 1)
        for bar, count in zip(bars, counts_tick):
            ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(count), ha='center', va='bottom')
        st.pyplot(fig4)

        st.write("#### Детализация по возрастным группам")
        group_df = pd.DataFrame(group_details)
        st.dataframe(group_df, use_container_width=True, hide_index=True)

else:
    st.info("👈 Настройте параметры в боковой панели и нажмите «Запустить моделирование».")
