# ai_news_analyzer_v2.py - Продвинутая версия с дедупликацией и ранжированием

import os
import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

# Загружаем API ключи из .env файла
load_dotenv()

# Проверяем наличие необходимых переменных окружения
if not os.getenv('OPENAI_API_KEY'):
    print("❌ ОШИБКА: Не найден OPENAI_API_KEY в переменных окружения!")
    print("📝 Создайте файл .env в корне проекта и добавьте:")
    print("   OPENAI_API_KEY=your_openai_api_key_here")
    print("   OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1")
    print("   OPENAI_MODEL_NAME=gpt-4.1")
    exit(1)

# Проверяем дополнительные переменные
api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4')

print("✅ API ключи загружены успешно")
print(f"🔗 API Base: {api_base}")
print(f"🤖 Модель: {model_name}")

# Оптимальная конфигурация моделей
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)  # Анализ и критика
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)  # Простые задачи

# --- ШАГ 1: УЛУЧШЕННАЯ ФУНКЦИЯ ДЛЯ СБОРА СТАТЕЙ ---
# Теперь она возвращает структурированные данные

def collect_articles_from_rss_v2(rss_feed_urls: str) -> str:
    """Собирает статьи из RSS-лент и возвращает структурированные данные"""
    articles = []
    urls = [url.strip() for url in rss_feed_urls.split(',')]

    print(f"--- [ФУНКЦИЯ V2] Начинаю работу с {len(urls)} RSS-лентами ---")
    
    for url in urls:
        try:
            print(f"📡 Обрабатываю RSS-ленту: {url}")
            feed = feedparser.parse(url)
            source_name = feed.feed.title if hasattr(feed.feed, 'title') else url
            
            if not feed.entries:
                print(f"⚠️  RSS-лента {url} не содержит статей")
                continue
                
            # Берем до 15 новостей из каждой ленты
            for entry in feed.entries[:15]:
                print(f"📄 Скачиваю статью: {entry.title} ---")
                try:
                    response = requests.get(entry.link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Удаляем ненужные теги
                    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                        tag.decompose()
                    
                    # Пытаемся найти основной контент статьи
                    content = soup.find('article') or soup.find('div', class_='content') or soup.find('main') or soup.find('body')
                    if content:
                        text = content.get_text(separator='\n', strip=True)
                    else:
                        text = soup.get_text(separator='\n', strip=True)
                    
                    articles.append({
                        'source': source_name,
                        'title': entry.title,
                        'link': entry.link,
                        'text': text[:2000]  # Ограничиваем длину текста
                    })
                    
                except Exception as e:
                    print(f"❌ Не удалось скачать статью {entry.link}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Ошибка при обработке RSS-ленты {url}: {e}")
            continue

    if not articles:
        return "Не удалось получить статьи. Проверьте доступность RSS-лент."
        
    # Возвращаем JSON строку для передачи между агентами
    return json.dumps(articles, ensure_ascii=False, indent=2)

# Создаем экземпляр инструмента для скрапинга
scraper_tool = ScrapeWebsiteTool()

# --- ШАГ 2: ОБНОВЛЕННЫЙ СПИСОК АГЕНТОВ ---

# 1. Агент-сборщик
news_analyst = Agent(
    role='Ведущий аналитик новостей в сфере ИИ',
    goal="Собрать самые свежие публикации из предоставленных RSS-лент. Сфокусироваться на темах: видеоускорители (NVIDIA, AMD), софт для локального запуска ИИ (LM Studio, Ollama, Jan.ai), ноутбуки и мини-ПК для ИИ, одноплатные компьютеры для ИИ.",
    backstory="Вы — опытный IT-журналист, который отслеживает пульс индустрии искусственного интеллекта. Ваша задача — отделить зерна от плевел и найти самую важную информацию, проигнорировав маркетинговую 'воду'.",
    tools=[scraper_tool],
    llm=fast_llm,
    verbose=True
)

# 2. НОВЫЙ АГЕНТ: Дедупликатор и Ранжировщик
deduplication_agent = Agent(
    role="Аналитик данных и редактор новостей",
    goal="""Определить уникальные новостные сюжеты из общего потока статей.
    Сгруппировать дубликаты, подсчитать частоту упоминаний каждого сюжета.
    Отсортировать уникальные сюжеты по важности (частота упоминаний + оценка содержания)
    и составить из них ТОП-30.""",
    backstory="""Вы — главный редактор новостного агентства. Ваш нюх на важные истории
    безошибочен. Вы умеете видеть общую картину за потоком одинаковых пресс-релизов
    и определять, что действительно заслуживает внимания.""",
    llm=smart_llm,  # этому агенту нужна мощная модель для анализа
    verbose=True
)

# 3. Аналитик трендов
trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="Проанализировать ТОП-30 новостей и выделить 10 ключевых, повторяющихся трендов. Для каждого тренда указать ключевые компании, продукты и технологии. Оценить, является тренд текущим или будущим событием.",
    backstory="Вы — data-аналитик с глубоким пониманием рынка ИИ. Вы видите скрытые связи между разными новостями и можете предсказывать, какие технологии 'выстрелят' завтра.",
    llm=smart_llm,
    verbose=True
)

# 4. Критический аналитик
critical_analyst = Agent(
    role='Критический аналитик и скептик',
    goal="""Изучить предложенный список трендов и найти в них неочевидные связи, потенциальные риски
    и практические выводы для разработчиков и бизнеса. Оспорить поверхностные выводы.""",
    backstory="""Вы — опытный венчурный аналитик, который повидал сотни 'революционных' технологий.
    Ваша задача — отделить реальные сигналы от шума, найти подводные камни и дать
    практические, действенные рекомендации, а не просто пересказывать новости.""",
    llm=smart_llm,
    verbose=True
)

# 5. Стратегический обозреватель
strategic_reviewer = Agent(
    role='Стратегический обозреватель для принятия решений',
    goal="""На основе выделенных трендов и критического анализа сгенерировать краткий и емкий еженедельный отчет
    в формате Markdown для руководителя. Отчет должен быть структурированным, легким для чтения
    и содержать только самую суть для быстрого погружения в повестку дня.""",
    backstory="""Вы — 'правая рука' технического директора. Вы умеете переводить сложный технический
    язык на язык бизнеса и стратегии. Ваш отчет помогает руководству принимать верные решения.""",
    llm=fast_llm,
    verbose=True
)

# --- ШАГ 3: ОБНОВЛЕННЫЙ СПИСОК ЗАДАЧ ---

# Расширенный список RSS-лент
RSS_FEEDS = """
    https://www.theverge.com/rss/ai-artificial-intelligence/index.xml,
    http://feeds.arstechnica.com/arstechnica/index/,
    https://techcrunch.com/category/artificial-intelligence/feed/,
    https://venturebeat.com/category/ai/feed/,
    https://www.wired.com/feed/category/business/latest/rss
"""

# Задача 1: Сбор данных
task_fetch = Task(
    description=f"""Собрать и обработать статьи из следующих RSS-лент: {RSS_FEEDS}
    
    Используй функцию collect_articles_from_rss_v2 для получения структурированных данных статей.
    Сфокусируйся на статьях, связанных с ИИ, машинным обучением, нейросетями.""",
    expected_output="JSON-строка со списком словарей, где каждый словарь представляет одну статью с ключами 'source', 'title', 'link', 'text'.",
    agent=news_analyst
)

# НОВАЯ ЗАДАЧА 2: Дедупликация и ранжирование
task_deduplicate_and_rank = Task(
    description="""Проанализировать список статей, полученный на предыдущем шаге.
    1. Определи похожие статьи (дубликаты) по смыслу их заголовков и содержания.
    2. Сгруппируй статьи в уникальные новостные сюжеты.
    3. Для каждого сюжета подсчитай количество источников, в которых он упоминается.
    4. Отсортируй сюжеты по важности: сначала те, что упоминаются чаще всего, затем по новизне и значимости.
    5. Сформируй итоговый ТОП-30 новостей.""",
    expected_output="""Отчет в формате Markdown, содержащий:
    - Блок статистики: "Проанализировано X новостей, из них Y уникальных".
    - Пронумерованный ТОП-30 уникальных новостей. Для каждой новости указать:
      - Заголовок.
      - Список источников, где она была найдена (Source 1, Source 2, ...).
      - Краткое содержание (1-2 предложения).""",
    agent=deduplication_agent,
    context=[task_fetch]
)

# Остальные задачи теперь зависят от ТОП-30
task_analyze = Task(
    description="На основе ТОП-30 новостей, проанализируй и выдели 10 главных трендов.",
    expected_output="Структурированный список 10 трендов в формате Markdown.",
    agent=trend_analyst,
    context=[task_deduplicate_and_rank]
)

task_critique = Task(
    description="""Проведи критический анализ 10 трендов, полученных от предыдущего агента.
    Для каждого тренда ответь на следующие вопросы:
    1. Какое практическое применение это имеет для независимого разработчика или малого бизнеса ПРЯМО СЕЙЧАС?
    2. Какой самый большой риск или неочевидная проблема связана с этим трендом?
    3. Какая технология или компания здесь может проиграть, а какая — неожиданно выиграть?""",
    expected_output="Структурированный отчет с критическим анализом каждого из 10 трендов.",
    agent=critical_analyst,
    context=[task_analyze]
)

task_report = Task(
    description="""Создай финальный дайджест.
    1. Включи в начало отчета блок статистики из задачи дедупликации.
    2. Включи ТОП-30 новостей с указанием источников.
    3. После этого добавь детальный анализ 10 трендов с критическими выводами.
    4. Добавь общий вывод и рекомендации для руководства.""",
    expected_output="Финальный, глубокий и структурированный отчет в формате Markdown.",
    agent=strategic_reviewer,
    context=[task_deduplicate_and_rank, task_analyze, task_critique]
)

# --- ШАГ 4: СБОРКА И ЗАПУСК КОМАНДЫ ---

ai_news_crew = Crew(
    agents=[news_analyst, deduplication_agent, trend_analyst, critical_analyst, strategic_reviewer],
    tasks=[task_fetch, task_deduplicate_and_rank, task_analyze, task_critique, task_report],
    process=Process.sequential,
    verbose=True
)

# Запускаем работу!
try:
    print("🚀 Запускаю продвинутый анализ новостей v2...")
    result = ai_news_crew.kickoff()

    print("\n\n##################################")
    print("## ГОТОВЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ V2 ##")
    print("##################################\n")
    print(result)
    
except Exception as e:
    print(f"❌ Критическая ошибка при выполнении анализа: {e}")
    print("💡 Проверьте:")
    print("   - Правильность API ключей в файле .env")
    print("   - Доступность RSS-лент")
    print("   - Подключение к интернету") 