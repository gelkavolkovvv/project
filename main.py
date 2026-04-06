import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
import ollama

load_dotenv()

def call_ollama(prompt: str) -> str:
    """Вызов локальной Ollama модели"""
    try:
        # Используем ту модель, которую скачали
        response = ollama.chat(
            model='llama3.2',  # или 'phi3:mini', 'mistral', 'saiga'
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Ошибка при вызове Ollama: {e}")
        print("Убедитесь, что Ollama запущен (иконка в трее)")
        raise

# ------------------ Агент 1: Аналитик рынка ------------------
def agent_market_analyst(role: str) -> Dict[str, Any]:
    prompt = f"""
Ты — аналитик рынка IT. Верни ТОЛЬКО JSON без пояснений.
Для роли "{role}" составь skill_map: категория → список навыков.
Категории: languages, frameworks, infrastructure, soft_skills.
Пример правильного JSON:
{{
    "skill_map": {{
        "languages": ["Python"],
        "frameworks": ["FastAPI", "Django"],
        "infrastructure": ["Docker", "PostgreSQL"],
        "soft_skills": ["Communication", "Problem Solving"]
    }}
}}
Верни только JSON, без других слов и пояснений.
"""
    response = call_ollama(prompt)
    # Извлекаем JSON из ответа
    start = response.find('{')
    end = response.rfind('}') + 1
    if start != -1 and end != 0:
        response = response[start:end]
    return json.loads(response)

# ------------------ Агент 2: Оценщик зарплат ------------------
def agent_salary_estimator(skill_map: Dict) -> Dict[str, Any]:
    prompt = f"""
Ты — оценщик зарплат IT. Верни ТОЛЬКО JSON.
На основе skill_map: {json.dumps(skill_map, ensure_ascii=False)}

Сформируй JSON:
{{
    "salary_table": {{
        "Junior": {{"Москва": [70, 120, 160], "Регионы РФ": [50, 90, 130], "Remote USD": [1500, 2500, 3500]}},
        "Middle": {{"Москва": [150, 230, 350], "Регионы РФ": [120, 180, 270], "Remote USD": [3000, 4500, 6000]}},
        "Senior": {{"Москва": [300, 450, 650], "Регионы РФ": [250, 350, 500], "Remote USD": [5000, 7000, 9000]}},
        "Lead": {{"Москва": [500, 700, 950], "Регионы РФ": [400, 550, 750], "Remote USD": [8000, 11000, 15000]}}
    }},
    "market_trend": {{
        "trend": "growing",
        "reason": "Высокий спрос на эту специализацию"
    }},
    "top_employers": ["Яндекс", "Ozon Tech", "Тинькофф", "VK", "Сбер"]
}}
Верни только JSON.
"""
    response = call_ollama(prompt)
    start = response.find('{')
    end = response.rfind('}') + 1
    if start != -1 and end != 0:
        response = response[start:end]
    return json.loads(response)

# ------------------ Агент 3: Карьерный советник ------------------
def agent_career_advisor(skill_map: Dict, salary_table: Dict) -> Dict[str, Any]:
    prompt = f"""
Ты — карьерный советник. Верни ТОЛЬКО JSON.
skill_map: {json.dumps(skill_map, ensure_ascii=False)}
salary_table: {json.dumps(salary_table, ensure_ascii=False)}

Создай JSON:
{{
    "learning_path": {{
        "Foundation": {{
            "topics": ["Основы языка", "Алгоритмы", "Git"],
            "resources": [["Курс на Stepik", "course"], ["Официальная документация", "documentation"]],
            "milestone": "Написание первой программы"
        }},
        "Practice": {{
            "topics": ["Работа с БД", "API", "Тестирование"],
            "resources": [["Книга 'Clean Code'", "book"], ["Курс на Coursera", "course"]],
            "milestone": "Создание CRUD приложения"
        }},
        "Portfolio": {{
            "topics": ["Проектирование", "Деплой", "CI/CD"],
            "resources": [["Документация Docker", "documentation"], ["Курс по DevOps", "course"]],
            "milestone": "Публичный репозиторий с проектом"
        }}
    }},
    "gap_analysis": {{
        "quick_wins": ["Изучить Git", "Основы SQL"],
        "long_term": ["System Design", "Облачные технологии"]
    }},


"portfolio_project": {{
        "name": "Конкретное название проекта",
        "description": "Подробное описание проекта",
        "technologies": ["Технология1", "Технология2", "Технология3"]
    }}
}}
Верни только JSON.
"""
    response = call_ollama(prompt)
    start = response.find('{')
    end = response.rfind('}') + 1
    if start != -1 and end != 0:
        response = response[start:end]
    return json.loads(response)

# ------------------ Агент 4: Критик и верификатор ------------------
def agent_critic(full_report: Dict) -> Dict[str, Any]:
    prompt = f"""
Ты — критик. Проверь отчёт:
{json.dumps(full_report, ensure_ascii=False, indent=2)}

Верни JSON:
{{
    "quality_score": 85,
    "warnings": ["Предупреждение 1", "Предупреждение 2"],
    "is_consistent": true
}}
Верни только JSON.
"""
    response = call_ollama(prompt)
    start = response.find('{')
    end = response.rfind('}') + 1
    if start != -1 and end != 0:
        response = response[start:end]
    return json.loads(response)

# ------------------ Генерация отчётов ------------------
def generate_markdown_report(data: Dict, role: str) -> str:
    md = f"# Карьерный отчёт: {role}\n\n"
    md += f"*Сгенерировано: {data['generated_at']}*\n\n"

    md += "## Навыки (skill_map)\n"
    for cat, skills in data.get("skill_map", {}).items():
        md += f"- **{cat}**: {', '.join(skills)}\n"

    md += "\n## Зарплаты (salary_table)\n"
    for grade, regions in data.get("salary_table", {}).items():
        md += f"### {grade}\n"
        for reg, vals in regions.items():
            md += f"- {reg}: {vals[0]} – {vals[1]} – {vals[2]} тыс. руб./USD\n"

    md += f"\n## Тренд рынка\n{data['market_trend']['trend']}: {data['market_trend']['reason']}\n"
    md += f"\n## Топ работодателей\n{', '.join(data['top_employers'])}\n"

    md += "\n## Карьерный трек\n"
    for phase, details in data.get("learning_path", {}).items():
        md += f"### {phase}\n"
        md += f"- Темы: {', '.join(details['topics'])}\n"
        md += f"- Milestone: {details['milestone']}\n"

    md += "\n## GAP-анализ\n"
    md += f"**Быстрые победы**: {', '.join(data['gap_analysis']['quick_wins'])}\n"
    md += f"**Долгосрочные**: {', '.join(data['gap_analysis']['long_term'])}\n"

    md += "\n## Портфолио-проект\n"
    md += f"**{data['portfolio_project']['name']}**\n"
    md += f"{data['portfolio_project']['description']}\n"
    md += f"Технологии: {', '.join(data['portfolio_project']['technologies'])}\n"

    md += "\n## Верификация\n"
    md += f"- Качество: {data['quality_score']}/100\n"
    md += f"- Предупреждения: {', '.join(data['warnings'])}\n"
    md += f"- Согласованность: {data['is_consistent']}\n"
    return md

# ------------------ Основной цикл ------------------
def main(role: str):
    print(f" Анализируем роль: {role}")

    print("1 Агент: Аналитик рынка")
    res1 = agent_market_analyst(role)

    print("2 Агент: Оценщик зарплат")
    res2 = agent_salary_estimator(res1["skill_map"])

    print("3 Агент: Карьерный советник")
    res3 = agent_career_advisor(res1["skill_map"], res2["salary_table"])

    full = {
        "role": role,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        **res1,
        **res2,
        **res3
    }

    print("4️Агент: Критик")
    critic = agent_critic(full)
    full.update(critic)

    os.makedirs("reports", exist_ok=True)
    json_path = f"reports/report_{role.replace(' ', '_')}.json"
    md_path = f"reports/report_{role.replace(' ', '_')}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(generate_markdown_report(full, role))

    print(f" Отчёты сохранены:\n- {json_path}\n- {md_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", required=True, help="Название специальности")
    args = parser.parse_args()


main(args.role)




