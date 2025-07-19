# test_v3.py - Тестовая версия V3 с новыми возможностями

import os
import json
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Загружаем API ключи
load_dotenv()

# Создаем модели
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

print(f"✅ Модель для анализа: {smart_llm.model_name}")
print(f"✅ Модель для простых задач: {fast_llm.model_name}")

# Тестовые данные для проверки V3 возможностей
test_articles = [
    {
        "source": "Hugging Face Blog",
        "title": "New Llama 3.1 model released with improved reasoning",
        "link": "https://example.com/1",
        "text": "Hugging Face has released Llama 3.1, a new language model with significantly improved reasoning capabilities..."
    },
    {
        "source": "Google AI Blog", 
        "title": "Gemini 2.0 introduces multimodal reasoning",
        "link": "https://example.com/2",
        "text": "Google's Gemini 2.0 model now supports advanced multimodal reasoning, combining text, images, and code..."
    },
    {
        "source": "AWS ML Blog",
        "title": "Amazon Bedrock adds Claude 3.5 Sonnet support",
        "link": "https://example.com/3", 
        "text": "AWS Bedrock now supports Claude 3.5 Sonnet, enabling enterprise customers to access Anthropic's latest model..."
    },
    {
        "source": "The Verge",
        "title": "NVIDIA announces RTX 5000 series for AI workloads",
        "link": "https://example.com/4",
        "text": "NVIDIA has unveiled the RTX 5000 series, specifically optimized for AI and machine learning workloads..."
    },
    {
        "source": "TechCrunch",
        "title": "Local AI tools like Ollama gain enterprise adoption",
        "link": "https://example.com/5",
        "text": "Local AI tools such as Ollama and LM Studio are seeing increased adoption in enterprise environments..."
    }
]

# Агенты V3 для тестирования
deduplication_agent = Agent(
    role="Аналитик данных и редактор новостей",
    goal="Определить уникальные новостные сюжеты и составить ТОП-5.",
    backstory="Вы — главный редактор новостного агентства с острым нюхом на важные истории.",
    llm=smart_llm,
    verbose=True
)

# Аналитик трендов с цепочкой мышления
trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="""Проанализировать ТОП-5 новостей и выделить 3 ключевых тренда.
    Использовать двухэтапный подход: сначала черновой анализ всех тем, затем синтез в тренды.""",
    backstory="""Вы — data-аналитик с глубоким пониманием рынка ИИ. Ваш подход — сначала собрать все данные, потом их проанализировать.""",
    llm=smart_llm,
    verbose=True
)

# Критический аналитик
critical_analyst = Agent(
    role='Критический аналитик и скептик',
    goal="""Провести критический анализ трендов и найти риски, возможности и практические выводы.""",
    backstory="""Вы — опытный венчурный аналитик, который умеет отделить реальные сигналы от шума.""",
    llm=smart_llm,
    verbose=True
)

# AI-ЕВАНГЕЛИСТ (НОВЫЙ ПОДХОД)
ai_evangelist = Agent(
    role='Ведущий AI-евангелист и технический обозреватель',
    goal="""Написать увлекательный аналитический дайджест в стиле техноблога.
    Перевести факты в живой рассказ о будущем технологий.""",
    backstory="""Вы — популярный техноблогер, известный умением глубоко разбираться в технологиях
    и рассказывать о них увлекательно для IT-специалистов. Ваш стиль — глубина, харизма и практическая польза.""",
    llm=smart_llm,
    verbose=True
)

# Задачи V3
task_deduplicate = Task(
    description="""Проанализировать список статей и:
    1. Найти дубликаты по смыслу заголовков и содержания
    2. Сгруппировать в уникальные сюжеты
    3. Подсчитать количество источников для каждого сюжета
    4. Составить ТОП-5 по важности""",
    expected_output="Отчет с ТОП-5 уникальных новостей и статистикой.",
    agent=deduplication_agent
)

# Задача с цепочкой мышления
task_analyze = Task(
    description="""Проанализируй ТОП-5 новостей. Твоя работа состоит из двух шагов:
    
    Шаг 1: 'Черновой анализ'. Выпиши все повторяющиеся темы, технологии, компании и продукты.
    
    Шаг 2: 'Синтез трендов'. На основе чернового анализа сгруппируй похожие темы
    и сформулируй 3 главных тренда с названиями и описаниями.""",
    expected_output="Структурированный список 3 трендов в формате Markdown.",
    agent=trend_analyst,
    context=[task_deduplicate]
)

task_critique = Task(
    description="""Проведи критический анализ 3 трендов. Для каждого ответь:
    1. Практическое применение для разработчика ПРЯМО СЕЙЧАС?
    2. Самый большой риск?
    3. Кто может проиграть, а кто выиграть?""",
    expected_output="Критический анализ каждого тренда.",
    agent=critical_analyst,
    context=[task_analyze]
)

# Задача AI-евангелиста
task_report = Task(
    description="""Создай финальный дайджест в стиле популярного техноблога.
    
    1. Начни с яркого вступления
    2. Включи блок статистики
    3. Представь ТОП-5 новостей с развернутыми комментариями (3-4 предложения каждая)
    4. Для каждого из 3 трендов напиши развернутый абзац (5-7 предложений)
    5. Заверши сильным заключением с прогнозом
    
    Пиши в стиле увлекательного техноблога для IT-специалистов.""",
    expected_output="Финальный отчет в стиле техноблога с развернутыми комментариями.",
    agent=ai_evangelist,
    context=[task_deduplicate, task_analyze, task_critique]
)

# Crew V3
test_crew = Crew(
    agents=[deduplication_agent, trend_analyst, critical_analyst, ai_evangelist],
    tasks=[task_deduplicate, task_analyze, task_critique, task_report],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    try:
        print("🚀 Тестирую V3 с новыми возможностями...")
        print("🎯 Новые возможности V3:")
        print("   - AI-евангелист для увлекательного повествования")
        print("   - Цепочка мышления для глубокого анализа трендов")
        print("   - Расширенные RSS-ленты с нишевыми источниками")
        print("   - Развернутые комментарии к каждой новости и тренду")
        print(f"📊 Тестовые данные: {len(test_articles)} статей")
        
        # Передаем тестовые данные в первую задачу
        task_deduplicate.description += f"\n\nТестовые данные:\n{json.dumps(test_articles, ensure_ascii=False, indent=2)}"
        
        result = test_crew.kickoff()
        
        print("\n📊 РЕЗУЛЬТАТ ТЕСТА V3:")
        print(result)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}") 