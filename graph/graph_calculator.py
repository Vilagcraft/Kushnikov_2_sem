from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import random
from typing import Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Реальные причины авиакатастроф (60 вершин)
AVIATION_RISKS = {
    "ROOT": "Безопасность авиационных перевозок",
    
    "TECH": "Технические неисправности",
    "HUMAN": "Ошибки пилотирования",
    "WEATHER": "Неблагоприятные погодные условия",
    "ORG": "Организационные недостатки",
    "TERROR": "Акты незаконного вмешательства",
    
    "ENGINE": "Отказ двигателя",
    "AVIONICS": "Отказ авионики",
    "FUEL": "Проблемы с топливной системой",
    "HYDRAULIC": "Отказ гидравлики",
    "LANDING": "Неисправность шасси",
    "CONTROL": "Отказ системы управления",
    
    "PILOT_ERROR": "Неправильные действия пилота",
    "SIT_AWARE": "Потеря ситуационной осведомленности",
    "CFIT": "Контролируемый полет в землю",
    "STALL": "Сваливание самолета",
    "GO_AROUND": "Ошибка при уходе на второй круг",
    
    "THUNDER": "Гроза и турбулентность",
    "ICING": "Обледенение",
    "FOG": "Туман и низкая видимость",
    "WIND": "Сдвиг ветра и боковой ветер",
    "SNOW": "Снегопад и гололед",
    
    "MAINTENANCE": "Некачественное техобслуживание",
    "TRAINING": "Недостаточная подготовка",
    "SCHEDULE": "Нарушение режима труда и отдыха",
    "DOCS": "Ошибки в документации",
    "SUPERVISION": "Недостаточный надзор",
    
    "HACKING": "Кибератака на системы",
    "SABOTAGE": "Диверсия",
    "HIJACK": "Угон воздушного судна",
    
    "ENG_OIL": "Масляное голодание двигателя",
    "ENG_FOD": "Попадание посторонних предметов",
    "ENG_FIRE": "Пожар двигателя",
    "ENG_BLADE": "Разрушение лопаток турбины",
    
    "AV_SENSOR": "Отказ датчиков",
    "AV_DISPLAY": "Отказ индикации",
    "AV_NAV": "Отказ навигации",
    
    "FUEL_LEAK": "Утечка топлива",
    "FUEL_CONTAM": "Загрязнение топлива",
    "FUEL_MIS": "Неверная заправка",
    
    "HYD_LEAK": "Утечка гидрожидкости",
    "HYD_PUMP": "Отказ гидронасоса",
    
    "LAND_GEAR": "Невыпуск шасси",
    "LAND_BRAKE": "Отказ тормозов",
    
    "CTRL_CABLE": "Обрыв тросов управления",
    "CTRL_COMP": "Разрушение элементов управления",
    
    "PILOT_FATIGUE": "Утомление пилота",
    "PILOT_MEDICAL": "Медицинские проблемы",
    "PILOT_STRESS": "Психологический стресс",
    "PILOT_COORD": "Нарушение координации в экипаже",
    
    "WEATHER_MICRO": "Микропорыв ветра",
    "WEATHER_WINDSHEAR": "Сдвиг ветра",
    "WEATHER_HAIL": "Град",
    
    "MAINT_HUMAN": "Ошибка техника",
    "MAINT_PROC": "Нарушение процедур",
    "MAINT_TOOL": "Неисправный инструмент",
    
    "TRAIN_SIM": "Недостаток тренажерной подготовки",
    "TRAIN_CHECK": "Ослабленный контроль",
    
    "SECURITY_SCREEN": "Нарушение досмотра",
    "SECURITY_PERSON": "Действия персонала аэропорта"
}

def random_percent():
    return round(random.uniform(0.10, 0.90), 3)

def random_range(center_prob=None):
    if center_prob is None:
        center_prob = random_percent()
    width = random.uniform(0.35, 0.70)
    min_val = max(0.05, center_prob - width/2)
    max_val = min(0.95, center_prob + width/2)
    if max_val - min_val < 0.30:
        max_val = min(0.95, min_val + 0.35)
    return (round(min_val, 3), round(max_val, 3))

# Структура графа
GRAPH_STRUCTURE = {
    "ROOT": {"id": "ROOT", "name": AVIATION_RISKS["ROOT"], "probability": random_percent(), "children": ["OR_ROOT"], "parent": None, "level": 0, "type": "root", "logic": None},
    "OR_ROOT": {"id": "OR_ROOT", "name": "1", "probability": None, "children": ["TECH", "HUMAN", "WEATHER", "ORG", "TERROR"], "parent": "ROOT", "level": 1, "type": "logic_or", "logic": "OR"},
    
    "TECH": {"id": "TECH", "name": AVIATION_RISKS["TECH"], "probability": random_percent(), "children": ["OR_TECH"], "parent": "AND_ROOT", "level": 2, "type": "category", "logic": None},
    "HUMAN": {"id": "HUMAN", "name": AVIATION_RISKS["HUMAN"], "probability": random_percent(), "children": ["OR_HUMAN"], "parent": "AND_ROOT", "level": 2, "type": "category", "logic": None},
    "WEATHER": {"id": "WEATHER", "name": AVIATION_RISKS["WEATHER"], "probability": random_percent(), "children": ["OR_WEATHER"], "parent": "AND_ROOT", "level": 2, "type": "category", "logic": None},
    "ORG": {"id": "ORG", "name": AVIATION_RISKS["ORG"], "probability": random_percent(), "children": ["OR_ORG"], "parent": "AND_ROOT", "level": 2, "type": "category", "logic": None},
    "TERROR": {"id": "TERROR", "name": AVIATION_RISKS["TERROR"], "probability": random_percent(), "children": ["OR_TERROR"], "parent": "AND_ROOT", "level": 2, "type": "category", "logic": None},
    
    "OR_TECH": {"id": "OR_TECH", "name": "1", "probability": None, "children": ["ENGINE", "AVIONICS", "FUEL", "HYDRAULIC", "LANDING", "CONTROL"], "parent": "TECH", "level": 3, "type": "logic_or", "logic": "OR"},
    "OR_HUMAN": {"id": "OR_HUMAN", "name": "1", "probability": None, "children": ["PILOT_ERROR", "SIT_AWARE", "CFIT", "STALL", "GO_AROUND"], "parent": "HUMAN", "level": 3, "type": "logic_or", "logic": "OR"},
    "OR_WEATHER": {"id": "OR_WEATHER", "name": "1", "probability": None, "children": ["THUNDER", "ICING", "FOG", "WIND", "SNOW"], "parent": "WEATHER", "level": 3, "type": "logic_or", "logic": "OR"},
    "OR_ORG": {"id": "OR_ORG", "name": "1", "probability": None, "children": ["MAINTENANCE", "TRAINING", "SCHEDULE", "DOCS", "SUPERVISION"], "parent": "ORG", "level": 3, "type": "logic_or", "logic": "OR"},
    "OR_TERROR": {"id": "OR_TERROR", "name": "1", "probability": None, "children": ["HACKING", "SABOTAGE", "HIJACK"], "parent": "TERROR", "level": 3, "type": "logic_or", "logic": "OR"},
    
    "ENGINE": {"id": "ENGINE", "name": AVIATION_RISKS["ENGINE"], "probability": random_percent(), "children": ["OR_ENGINE"], "parent": "OR_TECH", "level": 4, "type": "factor", "logic": None},
    "AVIONICS": {"id": "AVIONICS", "name": AVIATION_RISKS["AVIONICS"], "probability": random_percent(), "children": ["OR_AVIONICS"], "parent": "OR_TECH", "level": 4, "type": "factor", "logic": None},
    "FUEL": {"id": "FUEL", "name": AVIATION_RISKS["FUEL"], "probability": random_percent(), "children": ["OR_FUEL"], "parent": "OR_TECH", "level": 4, "type": "factor", "logic": None},
    "HYDRAULIC": {"id": "HYDRAULIC", "name": AVIATION_RISKS["HYDRAULIC"], "probability": random_percent(), "children": ["OR_HYDRAULIC"], "parent": "OR_TECH", "level": 4, "type": "factor", "logic": None},
    "LANDING": {"id": "LANDING", "name": AVIATION_RISKS["LANDING"], "probability": random_percent(), "children": ["OR_LANDING"], "parent": "OR_TECH", "level": 4, "type": "factor", "logic": None},
    "CONTROL": {"id": "CONTROL", "name": AVIATION_RISKS["CONTROL"], "probability": random_percent(), "children": ["OR_CONTROL"], "parent": "OR_TECH", "level": 4, "type": "factor", "logic": None},
    
    "PILOT_ERROR": {"id": "PILOT_ERROR", "name": AVIATION_RISKS["PILOT_ERROR"], "probability": random_percent(), "children": ["OR_PILOT_ERROR"], "parent": "OR_HUMAN", "level": 4, "type": "factor", "logic": None},
    "SIT_AWARE": {"id": "SIT_AWARE", "name": AVIATION_RISKS["SIT_AWARE"], "probability": random_percent(), "children": [], "parent": "OR_HUMAN", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "CFIT": {"id": "CFIT", "name": AVIATION_RISKS["CFIT"], "probability": random_percent(), "children": [], "parent": "OR_HUMAN", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "STALL": {"id": "STALL", "name": AVIATION_RISKS["STALL"], "probability": random_percent(), "children": [], "parent": "OR_HUMAN", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "GO_AROUND": {"id": "GO_AROUND", "name": AVIATION_RISKS["GO_AROUND"], "probability": random_percent(), "children": [], "parent": "OR_HUMAN", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    
    "THUNDER": {"id": "THUNDER", "name": AVIATION_RISKS["THUNDER"], "probability": random_percent(), "children": ["OR_THUNDER"], "parent": "OR_WEATHER", "level": 4, "type": "factor", "logic": None},
    "ICING": {"id": "ICING", "name": AVIATION_RISKS["ICING"], "probability": random_percent(), "children": [], "parent": "OR_WEATHER", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "FOG": {"id": "FOG", "name": AVIATION_RISKS["FOG"], "probability": random_percent(), "children": [], "parent": "OR_WEATHER", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "WIND": {"id": "WIND", "name": AVIATION_RISKS["WIND"], "probability": random_percent(), "children": [], "parent": "OR_WEATHER", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "SNOW": {"id": "SNOW", "name": AVIATION_RISKS["SNOW"], "probability": random_percent(), "children": [], "parent": "OR_WEATHER", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    
    "MAINTENANCE": {"id": "MAINTENANCE", "name": AVIATION_RISKS["MAINTENANCE"], "probability": random_percent(), "children": ["OR_MAINTENANCE"], "parent": "OR_ORG", "level": 4, "type": "factor", "logic": None},
    "TRAINING": {"id": "TRAINING", "name": AVIATION_RISKS["TRAINING"], "probability": random_percent(), "children": ["OR_TRAINING"], "parent": "OR_ORG", "level": 4, "type": "factor", "logic": None},
    "SCHEDULE": {"id": "SCHEDULE", "name": AVIATION_RISKS["SCHEDULE"], "probability": random_percent(), "children": [], "parent": "OR_ORG", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "DOCS": {"id": "DOCS", "name": AVIATION_RISKS["DOCS"], "probability": random_percent(), "children": [], "parent": "OR_ORG", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    "SUPERVISION": {"id": "SUPERVISION", "name": AVIATION_RISKS["SUPERVISION"], "probability": random_percent(), "children": [], "parent": "OR_ORG", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    
    "HACKING": {"id": "HACKING", "name": AVIATION_RISKS["HACKING"], "probability": random_percent(), "children": ["AND_HACKING"], "parent": "OR_TERROR", "level": 4, "type": "factor", "logic": None},
    "SABOTAGE": {"id": "SABOTAGE", "name": AVIATION_RISKS["SABOTAGE"], "probability": random_percent(), "children": ["AND_SABOTAGE"], "parent": "OR_TERROR", "level": 4, "type": "factor", "logic": None},
    "HIJACK": {"id": "HIJACK", "name": AVIATION_RISKS["HIJACK"], "probability": random_percent(), "children": [], "parent": "OR_TERROR", "level": 4, "type": "leaf", "logic": None, "is_leaf": True},
    
    "OR_ENGINE": {"id": "OR_ENGINE", "name": "1", "probability": None, "children": ["ENG_OIL", "ENG_FOD", "ENG_FIRE", "ENG_BLADE"], "parent": "ENGINE", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_AVIONICS": {"id": "OR_AVIONICS", "name": "1", "probability": None, "children": ["AV_SENSOR", "AV_DISPLAY", "AV_NAV"], "parent": "AVIONICS", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_FUEL": {"id": "OR_FUEL", "name": "1", "probability": None, "children": ["FUEL_LEAK", "FUEL_CONTAM", "FUEL_MIS"], "parent": "FUEL", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_HYDRAULIC": {"id": "OR_HYDRAULIC", "name": "1", "probability": None, "children": ["HYD_LEAK", "HYD_PUMP"], "parent": "HYDRAULIC", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_LANDING": {"id": "OR_LANDING", "name": "1", "probability": None, "children": ["LAND_GEAR", "LAND_BRAKE"], "parent": "LANDING", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_CONTROL": {"id": "OR_CONTROL", "name": "1", "probability": None, "children": ["CTRL_CABLE", "CTRL_COMP"], "parent": "CONTROL", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_PILOT_ERROR": {"id": "OR_PILOT_ERROR", "name": "1", "probability": None, "children": ["PILOT_FATIGUE", "PILOT_MEDICAL", "PILOT_STRESS", "PILOT_COORD"], "parent": "PILOT_ERROR", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_THUNDER": {"id": "OR_THUNDER", "name": "1", "probability": None, "children": ["WEATHER_MICRO", "WEATHER_WINDSHEAR", "WEATHER_HAIL"], "parent": "THUNDER", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_MAINTENANCE": {"id": "OR_MAINTENANCE", "name": "1", "probability": None, "children": ["MAINT_HUMAN", "MAINT_PROC", "MAINT_TOOL"], "parent": "MAINTENANCE", "level": 5, "type": "logic_or", "logic": "OR"},
    "OR_TRAINING": {"id": "OR_TRAINING", "name": "1", "probability": None, "children": ["TRAIN_SIM", "TRAIN_CHECK"], "parent": "TRAINING", "level": 5, "type": "logic_or", "logic": "OR"},
    
    "AND_HACKING": {"id": "AND_HACKING", "name": "&", "probability": None, "children": ["SECURITY_SCREEN"], "parent": "HACKING", "level": 5, "type": "logic_and", "logic": "AND"},
    "AND_SABOTAGE": {"id": "AND_SABOTAGE", "name": "&", "probability": None, "children": ["SECURITY_PERSON"], "parent": "SABOTAGE", "level": 5, "type": "logic_and", "logic": "AND"},
    
    "ENG_OIL": {"id": "ENG_OIL", "name": AVIATION_RISKS["ENG_OIL"], "probability": random_percent(), "children": [], "parent": "OR_ENGINE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "ENG_FOD": {"id": "ENG_FOD", "name": AVIATION_RISKS["ENG_FOD"], "probability": random_percent(), "children": [], "parent": "OR_ENGINE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "ENG_FIRE": {"id": "ENG_FIRE", "name": AVIATION_RISKS["ENG_FIRE"], "probability": random_percent(), "children": [], "parent": "OR_ENGINE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "ENG_BLADE": {"id": "ENG_BLADE", "name": AVIATION_RISKS["ENG_BLADE"], "probability": random_percent(), "children": [], "parent": "OR_ENGINE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "AV_SENSOR": {"id": "AV_SENSOR", "name": AVIATION_RISKS["AV_SENSOR"], "probability": random_percent(), "children": [], "parent": "OR_AVIONICS", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "AV_DISPLAY": {"id": "AV_DISPLAY", "name": AVIATION_RISKS["AV_DISPLAY"], "probability": random_percent(), "children": [], "parent": "OR_AVIONICS", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "AV_NAV": {"id": "AV_NAV", "name": AVIATION_RISKS["AV_NAV"], "probability": random_percent(), "children": [], "parent": "OR_AVIONICS", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "FUEL_LEAK": {"id": "FUEL_LEAK", "name": AVIATION_RISKS["FUEL_LEAK"], "probability": random_percent(), "children": [], "parent": "OR_FUEL", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "FUEL_CONTAM": {"id": "FUEL_CONTAM", "name": AVIATION_RISKS["FUEL_CONTAM"], "probability": random_percent(), "children": [], "parent": "OR_FUEL", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "FUEL_MIS": {"id": "FUEL_MIS", "name": AVIATION_RISKS["FUEL_MIS"], "probability": random_percent(), "children": [], "parent": "OR_FUEL", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "HYD_LEAK": {"id": "HYD_LEAK", "name": AVIATION_RISKS["HYD_LEAK"], "probability": random_percent(), "children": [], "parent": "OR_HYDRAULIC", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "HYD_PUMP": {"id": "HYD_PUMP", "name": AVIATION_RISKS["HYD_PUMP"], "probability": random_percent(), "children": [], "parent": "OR_HYDRAULIC", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "LAND_GEAR": {"id": "LAND_GEAR", "name": AVIATION_RISKS["LAND_GEAR"], "probability": random_percent(), "children": [], "parent": "OR_LANDING", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "LAND_BRAKE": {"id": "LAND_BRAKE", "name": AVIATION_RISKS["LAND_BRAKE"], "probability": random_percent(), "children": [], "parent": "OR_LANDING", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "CTRL_CABLE": {"id": "CTRL_CABLE", "name": AVIATION_RISKS["CTRL_CABLE"], "probability": random_percent(), "children": [], "parent": "OR_CONTROL", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "CTRL_COMP": {"id": "CTRL_COMP", "name": AVIATION_RISKS["CTRL_COMP"], "probability": random_percent(), "children": [], "parent": "OR_CONTROL", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "PILOT_FATIGUE": {"id": "PILOT_FATIGUE", "name": AVIATION_RISKS["PILOT_FATIGUE"], "probability": random_percent(), "children": [], "parent": "OR_PILOT_ERROR", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "PILOT_MEDICAL": {"id": "PILOT_MEDICAL", "name": AVIATION_RISKS["PILOT_MEDICAL"], "probability": random_percent(), "children": [], "parent": "OR_PILOT_ERROR", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "PILOT_STRESS": {"id": "PILOT_STRESS", "name": AVIATION_RISKS["PILOT_STRESS"], "probability": random_percent(), "children": [], "parent": "OR_PILOT_ERROR", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "PILOT_COORD": {"id": "PILOT_COORD", "name": AVIATION_RISKS["PILOT_COORD"], "probability": random_percent(), "children": [], "parent": "OR_PILOT_ERROR", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "WEATHER_MICRO": {"id": "WEATHER_MICRO", "name": AVIATION_RISKS["WEATHER_MICRO"], "probability": random_percent(), "children": [], "parent": "OR_THUNDER", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "WEATHER_WINDSHEAR": {"id": "WEATHER_WINDSHEAR", "name": AVIATION_RISKS["WEATHER_WINDSHEAR"], "probability": random_percent(), "children": [], "parent": "OR_THUNDER", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "WEATHER_HAIL": {"id": "WEATHER_HAIL", "name": AVIATION_RISKS["WEATHER_HAIL"], "probability": random_percent(), "children": [], "parent": "OR_THUNDER", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "MAINT_HUMAN": {"id": "MAINT_HUMAN", "name": AVIATION_RISKS["MAINT_HUMAN"], "probability": random_percent(), "children": [], "parent": "OR_MAINTENANCE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "MAINT_PROC": {"id": "MAINT_PROC", "name": AVIATION_RISKS["MAINT_PROC"], "probability": random_percent(), "children": [], "parent": "OR_MAINTENANCE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "MAINT_TOOL": {"id": "MAINT_TOOL", "name": AVIATION_RISKS["MAINT_TOOL"], "probability": random_percent(), "children": [], "parent": "OR_MAINTENANCE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "TRAIN_SIM": {"id": "TRAIN_SIM", "name": AVIATION_RISKS["TRAIN_SIM"], "probability": random_percent(), "children": [], "parent": "OR_TRAINING", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "TRAIN_CHECK": {"id": "TRAIN_CHECK", "name": AVIATION_RISKS["TRAIN_CHECK"], "probability": random_percent(), "children": [], "parent": "OR_TRAINING", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    
    "SECURITY_SCREEN": {"id": "SECURITY_SCREEN", "name": AVIATION_RISKS["SECURITY_SCREEN"], "probability": random_percent(), "children": [], "parent": "AND_HACKING", "level": 6, "type": "leaf", "logic": None, "is_leaf": True},
    "SECURITY_PERSON": {"id": "SECURITY_PERSON", "name": AVIATION_RISKS["SECURITY_PERSON"], "probability": random_percent(), "children": [], "parent": "AND_SABOTAGE", "level": 6, "type": "leaf", "logic": None, "is_leaf": True}
}

PROBABILITY_RANGES = {}
for node_id, node in GRAPH_STRUCTURE.items():
    if node.get("type") in ["logic_and", "logic_or"]:
        PROBABILITY_RANGES[node_id] = (None, None)
    else:
        prob = node.get("probability", random_percent())
        PROBABILITY_RANGES[node_id] = random_range(prob)

def generate_random_probabilities():
    probabilities = {}
    for node_id, node in GRAPH_STRUCTURE.items():
        if node.get("type") in ["logic_and", "logic_or"]:
            continue
        probabilities[node_id] = random_percent()
    return probabilities

def evaluate_graph(probabilities):
    result = {}
    
    # Первый проход: оцениваем все узлы по их собственным вероятностям
    for node_id, node_data in GRAPH_STRUCTURE.items():
        if node_data.get("type") in ["logic_and", "logic_or"]:
            result[node_id] = {
                "id": node_id, "name": node_data["name"], "probability": None,
                "min_range": None, "max_range": None,
                "self_in_range": True, "in_range": True,
                "children": node_data.get("children", []),
                "parent": node_data.get("parent"),
                "level": node_data.get("level", 0),
                "type": node_data.get("type", "logic"),
                "logic": node_data.get("logic", "OR"),
                "is_leaf": node_data.get("is_leaf", False)
            }
        else:
            prob = probabilities.get(node_id, node_data.get("probability", 0.50))
            min_val, max_val = PROBABILITY_RANGES.get(node_id, (0.10, 0.90))
            
            result[node_id] = {
                "id": node_id, "name": node_data["name"], "probability": prob,
                "min_range": min_val, "max_range": max_val,
                "self_in_range": min_val <= prob <= max_val,
                "in_range": min_val <= prob <= max_val,
                "children": node_data.get("children", []),
                "parent": node_data.get("parent"),
                "level": node_data.get("level", 0),
                "type": node_data.get("type", "node"),
                "logic": node_data.get("logic", None),
                "is_leaf": node_data.get("is_leaf", False)
            }
    
    # Применяем логику И/ИЛИ для логических узлов (снизу вверх)
    for node_id in sorted(GRAPH_STRUCTURE.keys(), key=lambda x: -GRAPH_STRUCTURE[x].get("level", 0)):
        node = result[node_id]
        if node.get("type") in ["logic_and", "logic_or"] and node.get("children"):
            children_status = []
            for child_id in node.get("children", []):
                if child_id in result and result[child_id].get("in_range") is not None:
                    children_status.append(result[child_id]["in_range"])
            
            logic = node.get("logic", "OR")
            if children_status:
                if logic == "AND":
                    node["in_range"] = all(children_status)
                elif logic == "OR":
                    node["in_range"] = any(children_status)
    
    # Наследование статуса: если родитель не в норме, то все потомки не в норме
    def propagate_status(node_id, parent_in_range):
        if node_id not in result:
            return
        node = result[node_id]
        
        # Если родитель неактивен, то узел становится неактивным
        if parent_in_range is False:
            node["in_range"] = False
        
        # Рекурсивно обрабатываем детей
        for child_id in node.get("children", []):
            if child_id in result:
                propagate_status(child_id, node["in_range"])
    
    propagate_status("ROOT", True)
    
    return result

@app.get("/")
async def main():
    return FileResponse("graph_index.html")

@app.get("/api/graph")
async def get_graph():
    return JSONResponse(content={
        "nodes": GRAPH_STRUCTURE,
        "total_nodes": len(GRAPH_STRUCTURE)
    })

@app.get("/api/documentation")
async def get_documentation():
    """Возвращает документацию по графовой модели"""
    doc = {
        "title": "Графовая модель безопасности авиационной системы",
        "version": "2.0",
        "description": "Модель представляет собой иерархическую структуру факторов, влияющих на безопасность авиационных перевозок. Каждый фактор имеет вероятность возникновения и разрешенный диапазон значений.",
        
        "node_types": {
            "root": {
                "name": "Корневой узел",
                "description": "Общая оценка безопасности авиационной системы",
                "symbol": "ROOT"
            },
            "category": {
                "name": "Категория факторов",
                "description": "Объединяет связанные риски в группы",
                "example": "Технические неисправности, Ошибки пилотирования"
            },
            "factor": {
                "name": "Промежуточный фактор",
                "description": "Конкретная группа рисков, имеющая свои подфакторы",
                "example": "Отказ двигателя, Недостаточная подготовка"
            },
            "leaf": {
                "name": "Конечный фактор риска",
                "description": "Базовый неделимый фактор, влияющий на безопасность",
                "example": "Масляное голодание двигателя, Утомление пилота"
            },
            "logic_and": {
                "name": "Логический узел И (&)",
                "description": "Активируется только если ВСЕ дочерние узлы находятся в норме",
                "symbol": "&"
            },
            "logic_or": {
                "name": "Логический узел ИЛИ (1)",
                "description": "Активируется если хотя бы ОДИН дочерний узел находится в норме",
                "symbol": "1"
            }
        },
        
        "logic_rules": {
            "AND": {
                "name": "Конъюнкция (И)",
                "description": "Узел считается активным (в норме) только когда все его дочерние узлы активны",
                "formula": "A = B1 ∧ B2 ∧ ... ∧ Bn",
                "example": "Безопасность полетов требует, чтобы все категории были в норме"
            },
            "OR": {
                "name": "Дизъюнкция (ИЛИ)",
                "description": "Узел считается активным (в норме), если активен хотя бы один дочерний узел",
                "formula": "A = B1 ∨ B2 ∨ ... ∨ Bn",
                "example": "Достаточно одной технической неисправности для активации категории"
            }
        },
        
        "probability_model": {
            "range": "5% - 95%",
            "description": "Вероятность возникновения фактора риска может варьироваться от 5% до 95%",
            "interpretation": {
                "low": "5-30% - низкая вероятность",
                "medium": "30-70% - средняя вероятность",
                "high": "70-95% - высокая вероятность"
            }
        },
        
        "visual_indicators": {
            "active_bright": {
                "meaning": "Узел находится в разрешенном диапазоне (в норме)",
                "color": "Фиолетовый/золотой/зеленый градиент"
            },
            "inactive_gray": {
                "meaning": "Узел выходит за пределы разрешенного диапазона (требует внимания)",
                "color": "Серый"
            },
            "logic_and": {
                "meaning": "Логический узел И - желтый",
                "color": "#fbbf24"
            },
            "logic_or": {
                "meaning": "Логический узел ИЛИ - зеленый",
                "color": "#34d399"
            }
        },
        
        "inheritance_rules": {
            "description": "Статус узла наследуется его потомками",
            "rule": "Если родительский узел не в норме, то все его дочерние узлы автоматически становятся не в норме (серыми)",
            "reason": "Проблема на верхнем уровне влияет на все подчиненные элементы"
        },
        
        "graph_statistics": {
            "total_nodes": 60,
            "root_nodes": 1,
            "logic_and_nodes": 3,
            "logic_or_nodes": 13,
            "category_nodes": 5,
            "factor_nodes": 17,
            "leaf_nodes": 21,
            "max_depth": 6
        },
        
        "usage_instructions": {
            "random_values": "Генерирует случайные вероятности для всех узлов (5%-95%)",
            "analyze": "Выполняет анализ текущего состояния графа с учетом логических связей",
            "reset": "Сбрасывает все значения к исходным",
            "click_node": "Нажмите на любой узел для просмотра детальной информации",
            "adjust_probability": "Используйте слайдер или введите значение для изменения вероятности"
        },
        
        "interpretation_guide": {
            "green_zone": "Узел в норме - фактор не создает угрозы безопасности",
            "red_zone": "Узел вне нормы - требуется анализ и возможные корректирующие действия",
            "bright_branch": "Вся ветвь в норме - система стабильна",
            "gray_branch": "Есть проблемные узлы - требуется внимание к данной области"
        }
    }
    return JSONResponse(content=doc)

@app.post("/api/evaluate")
async def evaluate(data: Dict[str, Any]):
    try:
        probabilities = data.get("probabilities", {})
        if not probabilities:
            probabilities = generate_random_probabilities()
        
        result = evaluate_graph(probabilities)
        
        return JSONResponse(content={
            "nodes": result,
            "root": "ROOT",
            "probabilities": probabilities,
            "total_nodes": len(result)
        })
    except Exception as err:
        print(f"Error: {err}")
        raise HTTPException(status_code=500, detail=str(err))

@app.post("/api/random")
async def random_values():
    probabilities = generate_random_probabilities()
    result = evaluate_graph(probabilities)
    
    return JSONResponse(content={
        "nodes": result,
        "root": "ROOT",
        "probabilities": probabilities,
        "total_nodes": len(result)
    })