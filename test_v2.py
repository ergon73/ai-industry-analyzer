# test_v2.py - Тестовая версия v2 с дедупликацией

import os
import json
from crewai import Agent, Task, Crew, Process
from crewai_tools import BaseTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Загружаем API ключи
load_dotenv()

# Создаем модели
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

print(f"✅ Модель для анализа: {smart_llm.model_name}")
print(f"✅ Модель для простых задач: {fast_llm.model_name}")

# Тестовые данные для проверки дедупликации
test_articles = [
    {
        "source": "The Verge",
        "title": "OpenAI launches new GPT-4 model with improved capabilities",
        "link": "https://example.com/1",
        "text": "OpenAI has released a new version of GPT-4 with enhanced performance..."
    },
    {
        "source": "TechCrunch", 
        "title": "OpenAI introduces GPT-4 update with better reasoning",
        "link": "https://example.com/2",
        "text": "OpenAI announced an updated GPT-4 model that shows improved reasoning..."
    },
    {
        "source": "Ars Technica",
        "title": "Microsoft invests $10 billion in OpenAI partnership",
        "link": "https://example.com/3", 
        "text": "Microsoft has announced a $10 billion investment in OpenAI..."
    },
    {
        "source": "VentureBeat",
        "title": "AI coding tools market grows rapidly",
        "link": "https://example.com/4",
        "text": "The market for AI-powered coding tools is experiencing rapid growth..."
    }
]

# Агенты для тестирования
deduplication_agent = Agent(
    role="Аналитик данных и редактор новостей",
    goal="Определить уникальные новостные сюжеты и составить ТОП-10.",
    backstory="Вы — главный редактор новостного агентства с острым нюхом на важные истории.",
    llm=smart_llm,
    verbose=True
)

trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="Проанализировать ТОП-10 новостей и выделить 5 ключевых трендов.",
    backstory="Вы — data-аналитик с глубоким пониманием рынка ИИ.",
    llm=smart_llm,
    verbose=True
)

strategic_reviewer = Agent(
    role='Стратегический обозреватель',
    goal="Создать финальный дайджест с ТОП-10 и анализом трендов.",
    backstory="Вы — 'правая рука' технического директора.",
    llm=fast_llm,
    verbose=True
)

# Задачи
task_deduplicate = Task(
    description="""Проанализировать список статей и:
    1. Найти дубликаты по смыслу заголовков и содержания
    2. Сгруппировать в уникальные сюжеты
    3. Подсчитать количество источников для каждого сюжета
    4. Составить ТОП-10 по важности""",
    expected_output="Отчет с ТОП-10 уникальных новостей и статистикой.",
    agent=deduplication_agent
)

task_analyze = Task(
    description="На основе ТОП-10 новостей выдели 5 главных трендов.",
    expected_output="Список 5 трендов в формате Markdown.",
    agent=trend_analyst,
    context=[task_deduplicate]
)

task_report = Task(
    description="Создай финальный дайджест с ТОП-10 и анализом трендов.",
    expected_output="Финальный отчет в формате Markdown.",
    agent=strategic_reviewer,
    context=[task_deduplicate, task_analyze]
)

# Crew
test_crew = Crew(
    agents=[deduplication_agent, trend_analyst, strategic_reviewer],
    tasks=[task_deduplicate, task_analyze, task_report],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    try:
        print("🚀 Тестирую v2 с дедупликацией...")
        print(f"📊 Тестовые данные: {len(test_articles)} статей")
        
        # Передаем тестовые данные в первую задачу
        task_deduplicate.description += f"\n\nТестовые данные:\n{json.dumps(test_articles, ensure_ascii=False, indent=2)}"
        
        result = test_crew.kickoff()
        
        print("\n📊 РЕЗУЛЬТАТ ТЕСТА V2:")
        print(result)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}") 