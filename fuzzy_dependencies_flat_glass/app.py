# fuzzy_dependencies.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Нечёткие зависимости в производстве стекла", layout="wide")

# ============================================================
# ЛИНГВИСТИЧЕСКАЯ ШКАЛА
# ============================================================
LEVELS = {
    1: "Отсутствует",
    2: "Очень слабая",
    3: "Слабая",
    4: "Умеренная",
    5: "Заметная",
    6: "Сильная",
    7: "Очень сильная",
}

# ============================================================
# ПЕРЕМЕННЫЕ МОДЕЛИ
# ============================================================
X_NAMES = {
    "X1": "Скорость выработки ленты",
    "X2": "Скорость вращения роликов",
    "X3": "Температура расплава металла",
    "X4": "Температура кожуха дна",
    "X5": "Температура бортов ванны",
    "X6": "Стабильность положения ленты",
    "X7": "Расход электроэнергии",
    "X8": "Расход природного газа",
    "X9": "Расход защитной атмосферы",
    "X10": "Расход металла",
    "X11": "Квалификация оператора",
    "X12": "Состав бригады",
    "X13": "Сложность режима",
}

Z_NAMES = {
    "Z1": "Отключения электроэнергии",
    "Z2": "Отключения газа",
    "Z3": "Сбои подачи атмосферы",
    "Z4": "Внешняя среда",
    "Z5": "Износ оборудования",
}

# ============================================================
# ОПИСАНИЕ ЗАВИСИМОСТЕЙ (R1, R2)
# ============================================================
DEPENDENCIES = {
    "R1": {
        "input": "X13",
        "output": "X2",
        "description": "Влияние сложности режима на скорость вращения роликов утоняющих устройств",
        "default_points": {
            1: (1, 2, 2),   # X=1: эксперты (1,2,2)
            2: (2, 3, 3),
            3: (4, 4, 4),
            4: (6, 6, 5),
            5: (7, 7, 6)
        }
    },
    "R2": {
        "input": "X13",
        "output": "X3",
        "description": "Влияние сложности режима на температуру расплава металла",
        "default_points": {
            1: (1, 1, 2),
            2: (2, 3, 2),
            3: (4, 4, 5),
            4: (6, 5, 6),
            5: (7, 7, 6)
        }
    }
}

# ============================================================
# КЛАСС НЕЧЁТКОЙ ЗАВИСИМОСТИ
# ============================================================
class FuzzyDependency:
    def __init__(self, input_var, output_var):
        self.input_var = input_var
        self.output_var = output_var
        self.points = {}          # {x_value: (y1,y2,y3)}  x_value - целое 1..7
        self.degree = 2

    def set_point(self, x, scores):
        self.points[x] = scores

    def defuzzify(self, scores):
        return np.mean(scores)

    def get_xy_pairs(self):
        pairs = []
        for x, scores in sorted(self.points.items()):
            y = self.defuzzify(scores)
            pairs.append((float(x), y))
        return pairs

    def fit_polynomial(self):
        pairs = self.get_xy_pairs()
        if len(pairs) < 2:
            return None, None, None
        x_vals = np.array([p[0] for p in pairs])
        y_vals = np.array([p[1] for p in pairs])
        degree = min(self.degree, len(pairs)-1)
        coeffs = np.polyfit(x_vals, y_vals, degree)
        return coeffs, x_vals, y_vals

    def predict(self, x):
        coeffs, _, _ = self.fit_polynomial()
        if coeffs is None:
            return 4.0
        y = np.polyval(coeffs, x)
        return np.clip(y, 1.0, 7.0)

    def get_curve(self, n_points=200):
        coeffs, _, _ = self.fit_polynomial()
        if coeffs is None:
            return np.array([]), np.array([])
        x_curve = np.linspace(1, 7, n_points)
        y_curve = np.polyval(coeffs, x_curve)
        y_curve = np.clip(y_curve, 1, 7)
        return x_curve, y_curve

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ИНТЕРФЕЙСА
# ============================================================
def level_selector(label, key, default=4):
    return st.selectbox(
        label,
        options=list(LEVELS.keys()),
        format_func=lambda lvl: f"{lvl} — {LEVELS[lvl]}",
        index=default-1,
        key=key
    )

def render_dependency_tab(dep_id, dep_info):
    st.header(f"Зависимость {dep_id}: {dep_info['input']} → {dep_info['output']}")
    st.markdown(dep_info['description'])
    st.markdown(f"**Вход:** `{dep_info['input']}` – {X_NAMES[dep_info['input']]}")
    st.markdown(f"**Выход:** `{dep_info['output']}` – {X_NAMES[dep_info['output']]}")

    # Инициализация модели в session_state
    model_key = f"model_{dep_id}"
    if model_key not in st.session_state:
        model = FuzzyDependency(dep_info['input'], dep_info['output'])
        for x, scores in dep_info['default_points'].items():
            model.set_point(x, scores)
        st.session_state[model_key] = model

    model = st.session_state[model_key]

    # Степень полинома
    degree = st.slider("Степень аппроксимирующего полинома", 1, 4, 2, key=f"deg_{dep_id}")
    model.degree = degree

    # ------------------ Ввод экспертных оценок (5 точек) ------------------
    st.subheader("Экспертные оценки (5 точек)")
    st.caption("Для каждой из 5 точек задайте оценки трёх экспертов по шкале 1–7.")

    current_x_vals = sorted(model.points.keys())
    new_scores = {}

    for i, x in enumerate(current_x_vals, start=1):
        with st.expander(f"Точка {i}: X = {x} (лингвистически: {LEVELS[x]})", expanded=True):
            col1, col2, col3 = st.columns(3)
            current_scores = model.points[x]
            e1 = col1.selectbox(
                "Эксперт 1",
                options=list(LEVELS.keys()),
                format_func=lambda lvl: f"{lvl} — {LEVELS[lvl]}",
                index=current_scores[0]-1,
                key=f"{dep_id}_x{x}_e1"
            )
            e2 = col2.selectbox(
                "Эксперт 2",
                options=list(LEVELS.keys()),
                format_func=lambda lvl: f"{lvl} — {LEVELS[lvl]}",
                index=current_scores[1]-1,
                key=f"{dep_id}_x{x}_e2"
            )
            e3 = col3.selectbox(
                "Эксперт 3",
                options=list(LEVELS.keys()),
                format_func=lambda lvl: f"{lvl} — {LEVELS[lvl]}",
                index=current_scores[2]-1,
                key=f"{dep_id}_x{x}_e3"
            )
            new_scores[x] = (e1, e2, e3)

    # Обновляем модель при изменении оценок
    updated = False
    for x, scores in new_scores.items():
        if scores != model.points[x]:
            model.set_point(x, scores)
            updated = True
    if updated:
        st.session_state[model_key] = model

    # Кнопка сброса
    if st.button(f"Сбросить экспертные оценки {dep_id} к умолчаниям", key=f"reset_{dep_id}"):
        model = FuzzyDependency(dep_info['input'], dep_info['output'])
        for x, scores in dep_info['default_points'].items():
            model.set_point(x, scores)
        model.degree = degree
        st.session_state[model_key] = model
        st.success("Оценки сброшены. Перезагружаю страницу...")
        st.rerun()

    # Таблица с дефаззифицированными точками
    points_data = []
    for x in sorted(model.points.keys()):
        e1, e2, e3 = model.points[x]
        y_defuzz = model.defuzzify((e1, e2, e3))
        points_data.append({
            "X (уровень)": x,
            "Эксперт 1": e1,
            "Эксперт 2": e2,
            "Эксперт 3": e3,
            "Y после дефаззификации": round(y_defuzz, 2)
        })
    df_points = pd.DataFrame(points_data)
    st.markdown("### Дефаззифицированные точки")
    st.dataframe(df_points, use_container_width=True, hide_index=True)

    # ------------------ Калькулятор ------------------
    st.subheader("Расчёт значения по построенной зависимости")
    input_x = st.slider(
        f"Значение {model.input_var} (лингвистический уровень)",
        min_value=1.0, max_value=7.0, value=4.0, step=0.1,
        key=f"calc_{dep_id}"
    )
    y_pred = model.predict(input_x)
    nearest_lvl = int(round(y_pred))
    nearest_lvl = max(1, min(7, nearest_lvl))
    col1, col2 = st.columns(2)
    col1.metric("Числовое значение Y", f"{y_pred:.3f}")
    col2.metric("Лингвистическая интерпретация", f"{nearest_lvl} — {LEVELS[nearest_lvl]}")

    # ------------------ Построение графика (после калькулятора) ------------------
    pairs = model.get_xy_pairs()
    if len(pairs) >= 2:
        x_curve, y_curve = model.get_curve()
        x_points = [p[0] for p in pairs]
        y_points = [p[1] for p in pairs]

        fig = go.Figure()
        # Аппроксимирующая кривая
        fig.add_trace(go.Scatter(x=x_curve, y=y_curve, mode='lines', name='Аппроксимация'))
        # Точки дефаззификации
        fig.add_trace(go.Scatter(x=x_points, y=y_points, mode='markers+text',
                                 text=[f"P{i+1}" for i in range(len(points_data))],
                                 textposition="top center", marker=dict(size=12, color='red'),
                                 name='Точки (дефаззиф.)'))
        # Вертикальная линия для выбранного X
        fig.add_vline(x=input_x, line_dash="dash", line_color="green", annotation_text=f"X = {input_x:.1f}")
        # Горизонтальная линия для предсказанного Y
        fig.add_hline(y=y_pred, line_dash="dash", line_color="orange", annotation_text=f"Y = {y_pred:.2f}")
        # Точка пересечения (расчётное значение)
        fig.add_trace(go.Scatter(x=[input_x], y=[y_pred], mode='markers',
                                 marker=dict(size=14, symbol='star', color='gold'),
                                 name='Расчётная точка'))

        fig.update_layout(
            title=f"График зависимости {dep_id}",
            xaxis_title=f"{model.input_var} — {X_NAMES[model.input_var]} (лингвистические уровни)",
            yaxis_title=f"{model.output_var} — {X_NAMES[model.output_var]} (лингвистические уровни)",
            xaxis=dict(tickmode='array', tickvals=list(LEVELS.keys()), ticktext=list(LEVELS.values())),
            yaxis=dict(tickmode='array', tickvals=list(LEVELS.keys()), ticktext=list(LEVELS.values())),
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

        # Вывод полинома
        coeffs, _, _ = model.fit_polynomial()
        if coeffs is not None:
            terms = []
            for i, c in enumerate(coeffs):
                power = len(coeffs)-i-1
                if abs(c) < 1e-10:
                    continue
                if power == 0:
                    terms.append(f"{c:.4f}")
                elif power == 1:
                    terms.append(f"{c:.4f}·x")
                else:
                    terms.append(f"{c:.4f}·x^{power}")
            poly_str = " + ".join(terms)
            st.latex(f"y = {poly_str}")
    else:
        st.warning("Недостаточно точек для аппроксимации. Задайте хотя бы 2 точки.")

# ============================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ
# ============================================================
def main():
    st.title("🔮 Нечёткое моделирование зависимостей в производстве листового стекла")
    st.markdown("""
    Приложение строит аппроксимирующую зависимость между двумя логико-лингвистическими переменными  
    на основе экспертных оценок. Для каждой из 5 заданных точек три эксперта оценивают силу влияния  
    по шкале от 1 (отсутствует) до 7 (очень сильная). Значение Y для точки получается как среднее  
    экспертных оценок (дефаззификация). По полученным точкам строится полиномиальная кривая.
    """)

    tabs = st.tabs(["📘 Инструкция", "⚙️ Зависимость R1 (X13→X2)", "⚙️ Зависимость R2 (X13→X3)", "📊 Справочник"])

    with tabs[0]:
        st.subheader("Алгоритм работы")
        st.markdown("""
        1. **Выбор пары переменных** – для R1 и R2 заданы вход (сложность режима X13) и выход (скорость роликов X2 или температура расплава X3).
        2. **Экспертное оценивание** – для пяти фиксированных уровней входной переменной (X = 1,2,3,4,5) три эксперта задают уровень влияния на выходную переменную по шкале 1..7.
        3. **Дефаззификация** – для каждой точки вычисляется среднее арифметическое трёх экспертных оценок.
        4. **Аппроксимация** – по полученным пяти точкам строится полиномиальная кривая (степень выбирает пользователь).
        5. **Прогнозирование** – для любого значения входной переменной (1..7) можно вычислить значение выходной по построенной кривой.
        """)
        st.markdown("**Схема экспертного оценивания:**")
        st.code("""
           ┌─────────────┐
           │   X = 1..5  │ (лингвистический уровень)
           └──────┬──────┘
                  ▼
         ┌──────────────────┐
         │ Три эксперта дают│
         │ оценки Y1, Y2, Y3│
         └────────┬─────────┘
                  ▼
        ┌────────────────────┐
        │   Дефаззификация:  │
        │  Y = (Y1+Y2+Y3)/3  │
        └─────────┬──────────┘
                  ▼
         ┌──────────────────┐
         │   Точка (X, Y)   │
         └────────┬─────────┘
                  ▼
        ┌────────────────────┐
        │   Аппроксимация    │
        │ полиномом степени k│
        └────────────────────┘
        """)

    with tabs[1]:
        render_dependency_tab("R1", DEPENDENCIES["R1"])

    with tabs[2]:
        render_dependency_tab("R2", DEPENDENCIES["R2"])

    with tabs[3]:
        st.subheader("Лингвистическая шкала")
        df_scale = pd.DataFrame(list(LEVELS.items()), columns=["Уровень", "Значение"])
        st.dataframe(df_scale, use_container_width=True, hide_index=True)

        st.subheader("Переменные модели (X)")
        df_x = pd.DataFrame(list(X_NAMES.items()), columns=["Код", "Название"])
        st.dataframe(df_x, use_container_width=True, hide_index=True)

        st.subheader("Внешние возмущения (Z)")
        df_z = pd.DataFrame(list(Z_NAMES.items()), columns=["Код", "Название"])
        st.dataframe(df_z, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()