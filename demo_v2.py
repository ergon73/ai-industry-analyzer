# demo_v2.py - Демонстрация возможностей v2

import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Загружаем API ключи
load_dotenv()

# Создаем модели
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

print("🚀 ДЕМОНСТРАЦИЯ AI NEWS ANALYZER V2")
print("=" * 50)

# Демонстрационные агенты
deduplication_agent = Agent(
    role="Аналитик данных и редактор новостей",
    goal="Продемонстрировать возможности дедупликации и ранжирования.",
    backstory="Вы — главный редактор с острым нюхом на важные истории.",
    llm=smart_llm,
    verbose=True
)

trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="Показать качество анализа на основе отобранных новостей.",
    backstory="Вы — data-аналитик с глубоким пониманием рынка ИИ.",
    llm=smart_llm,
    verbose=True
)

# Демонстрационные задачи
task_demo = Task(
    description="""Продемонстрируй возможности v2:
    1. Объясни преимущества дедупликации
    2. Покажи как работает ранжирование ТОП-30
    3. Опиши статистические возможности""",
    expected_output="Демонстрационный отчет возможностей v2.",
    agent=deduplication_agent
)

task_analysis = Task(
    description="Покажи пример анализа трендов на основе ТОП-30.",
    expected_output="Пример анализа трендов.",
    agent=trend_analyst,
    context=[task_demo]
)

# Crew
demo_crew = Crew(
    agents=[deduplication_agent, trend_analyst],
    tasks=[task_demo, task_analysis],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    try:
        print("🎯 Запускаю демонстрацию v2...")
        result = demo_crew.kickoff()
        
        print("\n📊 ДЕМОНСТРАЦИОННЫЙ РЕЗУЛЬТАТ:")
        print(result)
        
        print("\n✅ Демонстрация завершена!")
        print("💡 Для полного анализа запустите: python ai_news_analyzer_v2.py")
        
    except Exception as e:
        print(f"❌ Ошибка демонстрации: {e}") 