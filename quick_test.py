# quick_test.py - Быстрый тест с gpt-4.1

import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Загружаем API ключи
load_dotenv()

# Создаем модели
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

print(f"✅ Модель для анализа: {smart_llm.model_name}")
print(f"✅ Модель для простых задач: {fast_llm.model_name}")

# Простой тест агентов
trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="Проанализировать и выделить 3 ключевых тренда в ИИ.",
    backstory="Вы — data-аналитик с глубоким пониманием рынка ИИ.",
    llm=smart_llm,
    verbose=True
)

critical_analyst = Agent(
    role='Критический аналитик',
    goal="Найти риски и практические выводы для разработчиков.",
    backstory="Вы — опытный венчурный аналитик.",
    llm=smart_llm,
    verbose=True
)

# Задачи
task_analyze = Task(
    description="Выдели 3 главных тренда в ИИ на основе текущих новостей.",
    expected_output="Список 3 трендов в формате Markdown.",
    agent=trend_analyst
)

task_critique = Task(
    description="Проанализируй каждый тренд и найди риски и практические выводы.",
    expected_output="Критический анализ трендов.",
    agent=critical_analyst,
    context=[task_analyze]
)

# Crew
test_crew = Crew(
    agents=[trend_analyst, critical_analyst],
    tasks=[task_analyze, task_critique],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    try:
        print("🚀 Тестирую gpt-4.1 для анализа...")
        result = test_crew.kickoff()
        print("\n📊 РЕЗУЛЬТАТ ТЕСТА:")
        print(result)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}") 