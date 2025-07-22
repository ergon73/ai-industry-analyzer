# test_v4.py - Тестовая версия V4 с новыми возможностями

import os
import json
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Загружаем API ключи
load_dotenv()

# Создаем модели V4
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

print(f"[OK] Модель для анализа: {smart_llm.model_name}")
print(f"[OK] Модель для простых задач: {fast_llm.model_name}")

# Тестовые данные для проверки V4 возможностей
test_articles = [
    {
        "source": "NVIDIA Blog",
        "title": "New RTX 5000 series optimized for AI workloads",
        "link": "https://example.com/1",
        "text": "NVIDIA has unveiled the RTX 5000 series, specifically optimized for AI and machine learning workloads with improved CUDA performance..."
    },
    {
        "source": "Tom's Hardware", 
        "title": "Best mini-PCs for local AI development in 2024",
        "link": "https://example.com/2",
        "text": "Our comprehensive guide to the best mini-PCs for local AI development, featuring models from Intel NUC, ASUS PN, and more..."
    },
    {
        "source": "Hugging Face Blog",
        "title": "New Llama 3.1 model released with improved reasoning",
        "link": "https://example.com/3", 
        "text": "Hugging Face has released Llama 3.1, a new language model with significantly improved reasoning capabilities..."
    },
    {
        "source": "Google AI Blog",
        "title": "Gemini 2.0 introduces multimodal reasoning",
        "link": "https://example.com/4",
        "text": "Google's Gemini 2.0 model now supports advanced multimodal reasoning, combining text, images, and code..."
    },
    {
        "source": "TechCrunch",
        "title": "Local AI tools like Ollama gain enterprise adoption",
        "link": "https://example.com/5",
        "text": "Local AI tools such as Ollama and LM Studio are seeing increased adoption in enterprise environments..."
    }
]

# Агенты V4 для тестирования
deduplication_agent = Agent(
    role="Главный редактор и аналитик данных",
    goal="Определить уникальные новостные сюжеты и рассчитать рейтинг значимости для ТОП-5.",
    backstory="Вы — главный редактор новостного агентства с математическим складом ума.",
    llm=smart_llm,
    verbose=True
)

# Аналитик трендов с цепочкой мышления
trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="""Проанализировать ТОП-5 новостей и выделить 3 ключевых тренда.
    Использовать двухэтапный подход: сначала черновой анализ всех тем, затем синтез в тренды.""",
    backstory="""Вы — data-аналитик с глубоким пониманием рынка ИИ. Ваш подход — сначала собрать все данные, потом их проанализировать.""",
    llm=fast_llm,  # Оптимизация: fast_llm для структурирования данных
    verbose=True
)

# Критический аналитик с поиском возможностей
critical_analyst = Agent(
    role='Критический аналитик и венчурный эксперт',
    goal="""Провести критический анализ трендов и найти риски, возможности и 'низко висящие фрукты' для стартапов.""",
    backstory="""Вы — опытный венчурный аналитик, который умеет отделить реальные сигналы от шума и находить конкретные бизнес-возможности.""",
    llm=smart_llm,
    verbose=True
)

# AI-ЕВАНГЕЛИСТ с четкой структурой
ai_evangelist = Agent(
    role='Ведущий AI-евангелист и технический обозреватель',
    goal="""Написать увлекательный аналитический дайджест с четкой структурой абзацев.
    Структурировать каждый абзац по формуле: вывод → примеры → прогноз.""",
    backstory="""Вы — популярный техноблогер, известный умением глубоко разбираться в технологиях
    и рассказывать о них увлекательно для IT-специалистов. Ваш стиль — глубина, харизма и практическая польза.""",
    llm=smart_llm,
    verbose=True
)

# Задачи V4
task_deduplicate = Task(
    description="""Проанализируй список статей и:
    1. Найди дубликаты по смыслу заголовков и содержания
    2. Сгруппируй в уникальные сюжеты
    3. Рассчитай 'Рейтинг значимости' по формуле: (Количество источников * 5) + (Наличие ключевых компаний [NVIDIA, Google, Hugging Face] * 3)
    4. Составь ТОП-5 по рейтингу значимости""",
    expected_output="Отчет с ТОП-5 уникальных новостей, рейтингами значимости и статистикой.",
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
    3. Кто может проиграть, а кто выиграть?
    4. Какую 'низко висящую' возможность этот тренд открывает для стартапа?""",
    expected_output="Критический анализ каждого тренда по четырем вопросам.",
    agent=critical_analyst,
    context=[task_analyze]
)

# Задача AI-евангелиста с четкой структурой
task_report = Task(
    description="""Создай финальный дайджест в стиле популярного техноблога.
    
    1. Начни с яркого вступления
    2. Включи блок статистики
    3. Представь ТОП-5 новостей с развернутыми комментариями (3-4 предложения каждая)
    4. Для каждого из 3 трендов напиши развернутый аналитический абзац (5-7 предложений)
       **Структурируй каждый абзац так:**
       - Начни с главного вывода о тренде
       - Приведи 1-2 примера из новостей для подтверждения
       - Закончи прогнозом влияния этого тренда
    5. Заверши сильным заключением с прогнозом
    
    Пиши в стиле увлекательного техноблога для IT-специалистов.""",
    expected_output="Финальный отчет в стиле техноблога с четкой структурой абзацев.",
    agent=ai_evangelist,
    context=[task_deduplicate, task_analyze, task_critique]
)

# Crew V4
test_crew = Crew(
    agents=[deduplication_agent, trend_analyst, critical_analyst, ai_evangelist],
    tasks=[task_deduplicate, task_analyze, task_critique, task_report],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    try:
        print("[START] Тестирую V4 с новыми возможностями...")
        print("[INFO] Новые возможности V4:")
        print("   - Объективная система оценки значимости новостей")
        print("   - Поиск 'низко висящих фруктов' для стартапов")
        print("   - Расширенные источники (NVIDIA, Tom's Hardware)")
        print("   - Оптимизированное распределение моделей")
        print("   - Четкая структура аналитических абзацев")
        print(f"[INFO] Тестовые данные: {len(test_articles)} статей")
        
        # Передаем тестовые данные в первую задачу
        task_deduplicate.description += f"\n\nТестовые данные:\n{json.dumps(test_articles, ensure_ascii=False, indent=2)}"
        
        result = test_crew.kickoff()
        
        print("\n[INFO] РЕЗУЛЬТАТ ТЕСТА V4:")
        print(result)
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}") 