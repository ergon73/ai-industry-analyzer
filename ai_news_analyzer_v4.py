# ai_news_analyzer_v4.py - Продвинутая версия с объективной оценкой и глубоким анализом

import os
import sys
import feedparser
import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import warnings

# Настраиваем кодировку для Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Фильтруем предупреждения
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*PydanticDeprecatedSince20.*")

from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from langchain_openai import ChatOpenAI

# Загружаем API ключи из .env файла
load_dotenv()

# Проверяем наличие необходимых переменных окружения
if not os.getenv('OPENAI_API_KEY'):
    print("[ОШИБКА] Не найден OPENAI_API_KEY в переменных окружения!")
    print("[ИНФО] Создайте файл .env в корне проекта и добавьте:")
    print("   OPENAI_API_KEY=your_openai_api_key_here")
    print("   OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1")
    print("   OPENAI_MODEL_NAME=gpt-4.1")
    exit(1)

# Проверяем дополнительные переменные
api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4')

print("[OK] API ключи загружены успешно")
print(f"[INFO] API Base: {api_base}")
print(f"[INFO] Модель: {model_name}")

# Оптимальная конфигурация моделей V4
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)  # Анализ и критика
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)  # Простые задачи

# --- ШАГ 1: УЛУЧШЕННАЯ ФУНКЦИЯ ДЛЯ СБОРА СТАТЕЙ V4 ---

def collect_articles_from_rss_v4(rss_feed_urls: str) -> str:
    """Собирает статьи из RSS-лент и возвращает структурированные данные"""
    articles = []
    urls = [url.strip() for url in rss_feed_urls.split(',')]

    print(f"--- [ФУНКЦИЯ V4] Начинаю работу с {len(urls)} RSS-лентами ---")
    
    for url in urls:
        try:
            print(f"[INFO] Обрабатываю RSS-ленту: {url}")
            feed = feedparser.parse(url)
            source_name = feed.feed.title if hasattr(feed.feed, 'title') else url
            
            if not feed.entries:
                print(f"[WARN] RSS-лента {url} не содержит статей")
                continue
                
            # Берем до 25 новостей из каждой ленты (увеличили для V4)
            for entry in feed.entries[:25]:
                print(f"[INFO] Скачиваю статью: {entry.title} ---")
                try:
                    response = requests.get(entry.link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    response.raise_for_status()
                    # Используем XML парсер для RSS и HTML парсер для веб-страниц
                    if 'xml' in response.headers.get('content-type', '').lower():
                        soup = BeautifulSoup(response.content, 'xml')
                    else:
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
                        'text': text[:3000]  # Увеличили лимит для V4
                    })
                    
                except Exception as e:
                    print(f"[ERROR] Не удалось скачать статью {entry.link}: {e}")
                    continue
                    
        except Exception as e:
            print(f"[ERROR] Ошибка при обработке RSS-ленты {url}: {e}")
            continue

    if not articles:
        return "Не удалось получить статьи. Проверьте доступность RSS-лент."
        
    # Возвращаем JSON строку для передачи между агентами
    return json.dumps(articles, ensure_ascii=False, indent=2)

# Создаем экземпляр инструмента для скрапинга
scraper_tool = ScrapeWebsiteTool()

# --- ШАГ 2: ОБНОВЛЕННЫЙ СПИСОК АГЕНТОВ V4 ---

# 1. Агент-сборщик (оставляем fast_llm для простых задач)
news_analyst = Agent(
    role='Ведущий аналитик новостей в сфере ИИ',
    goal="Собрать самые свежие публикации из предоставленных RSS-лент. Сфокусироваться на темах: видеоускорители (NVIDIA, AMD), софт для локального запуска ИИ (LM Studio, Ollama, Jan.ai), ноутбуки и мини-ПК для ИИ, одноплатные компьютеры для ИИ, новые модели на Hugging Face, практические кейсы ML.",
    backstory="Вы — опытный IT-журналист, который отслеживает пульс индустрии искусственного интеллекта. Ваша задача — отделить зерна от плевел и найти самую важную информацию, проигнорировав маркетинговую 'воду'.",
    tools=[scraper_tool],
    llm=fast_llm,
    verbose=True
)

# 2. Дедупликатор и Ранжировщик (smart_llm для сложной аналитики)
deduplication_agent = Agent(
    role="Главный редактор и аналитик данных",
    goal="""Определить уникальные новостные сюжеты из общего потока статей.
    Сгруппировать дубликаты, подсчитать частоту упоминаний каждого сюжета.
    Рассчитать объективный 'Рейтинг значимости' для каждого сюжета.
    Отсортировать уникальные сюжеты по рейтингу и составить из них ТОП-30.""",
    backstory="""Вы — главный редактор новостного агентства с математическим складом ума.
    Ваш нюх на важные истории безошибочен, но вы также умеете применять объективные
    критерии оценки. Вы видите общую картину за потоком одинаковых пресс-релизов
    и определяете, что действительно заслуживает внимания.""",
    llm=smart_llm,  # Улучшенная модель для сложной аналитики
    verbose=True
)

# 3. Аналитик трендов (fast_llm для структурирования данных)
trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="""Проанализировать ТОП-30 новостей и выделить 10 ключевых, повторяющихся трендов.
    Использовать двухэтапный подход: сначала черновой анализ всех тем, затем синтез в тренды.
    Для каждого тренда указать ключевые компании, продукты и технологии.""",
    backstory="""Вы — data-аналитик с глубоким пониманием рынка ИИ. Вы видите скрытые связи
    между разными новостями и можете предсказывать, какие технологии 'выстрелят' завтра.
    Ваш подход — сначала собрать все данные, потом их проанализировать.""",
    llm=fast_llm,  # Оптимизация: fast_llm для структурирования данных
    verbose=True
)

# 4. Критический аналитик (smart_llm для глубокого анализа)
critical_analyst = Agent(
    role='Критический аналитик и венчурный эксперт',
    goal="""Изучить предложенный список трендов и найти в них неочевидные связи, потенциальные риски,
    практические выводы для разработчиков и бизнеса, а также конкретные возможности для стартапов.
    Оспорить поверхностные выводы и найти 'низко висящие фрукты'.""",
    backstory="""Вы — опытный венчурный аналитик, который повидал сотни 'революционных' технологий.
    Ваша задача — отделить реальные сигналы от шума, найти подводные камни и дать
    практические, действенные рекомендации. Вы также умеете находить конкретные
    бизнес-возможности, которые можно протестировать быстро.""",
    llm=smart_llm,
    verbose=True
)

# 5. AI-ЕВАНГЕЛИСТ (smart_llm для качественного текста)
strategic_reviewer = Agent(
    role='Ведущий AI-евангелист и технический обозреватель',
    goal="""Написать увлекательный и подробный аналитический дайджест.
    Перевести сухие факты трендов и рисков в живой рассказ о будущем технологий.
    Объяснить сложные темы простым, но не примитивным языком для IT-специалистов.
    Структурировать каждый абзац по четкой формуле.""",
    backstory="""Вы — популярный техноблогер и обозреватель, известный своим умением
    глубоко разбираться в технологиях и рассказывать о них так, чтобы это было
    интересно и разработчикам, и менеджерам. Ваш стиль — это глубина, харизма
    и практическая польза. Вы не просто констатируете факты, а объясняете,
    'что всё это значит для нас'.""",
    llm=smart_llm,  # Умная модель для качественного текста
    verbose=True
)

# --- ШАГ 3: РАСШИРЕННЫЙ СПИСОК RSS-ЛЕНТ V4 ---

RSS_FEEDS = """
    # Основные техно-СМИ
    https://www.theverge.com/rss/ai-artificial-intelligence/index.xml,
    http://feeds.arstechnica.com/arstechnica/index/,
    https://techcrunch.com/category/artificial-intelligence/feed/,
    https://venturebeat.com/category/ai/feed/,
    https://www.wired.com/feed/category/business/latest/rss,
    # Нишевые и блоги
    https://huggingface.co/blog/feed.xml,
    https://blog.google/technology/ai/rss/,
    https://aws.amazon.com/blogs/machine-learning/feed/,
    # Новые источники для V4 - железо и локальный ИИ
    https://blogs.nvidia.com/feed/,
    https://www.tomshardware.com/rss
"""

# --- ШАГ 4: ОБНОВЛЕННЫЙ СПИСОК ЗАДАЧ V4 ---

# Задача 1: Сбор данных
task_fetch = Task(
    description=f"""Собрать и обработать статьи из следующих RSS-лент: {RSS_FEEDS}
    
    Используй функцию collect_articles_from_rss_v4 для получения структурированных данных статей.
    Сфокусируйся на статьях, связанных с ИИ, машинным обучением, нейросетями, локальным ИИ, железом для ИИ.""",
    expected_output="JSON-строка со списком словарей, где каждый словарь представляет одну статью с ключами 'source', 'title', 'link', 'text'.",
    agent=news_analyst
)

# Задача 2: Дедупликация и ранжирование с объективной оценкой
task_deduplicate_and_rank = Task(
    description="""Проанализируй список статей. Твоя задача — выступить в роли главного редактора.
    
    1. **Найди дубликаты:** Определи похожие статьи и сгруппируй их в уникальные новостные сюжеты.
    
    2. **Оцени значимость:** Для каждого сюжета рассчитай 'Рейтинг значимости' по формуле:
       - (Количество источников * 5) + (Наличие в названии ключевых компаний [OpenAI, Google, NVIDIA, Mistral, AMD, Intel] * 3)
       - Дополнительные баллы за упоминание локального ИИ, железа для ИИ, практических кейсов
    
    3. **Отсортируй:** Ранжируй сюжеты по убыванию их 'Рейтинга значимости'.
    
    4. **Сформируй ТОП:** Представь итоговый ТОП-30 новостей.""",
    expected_output="""Отчет в Markdown, содержащий:
    - Статистику: "Проанализировано X новостей, из них Y уникальных".
    - Пронумерованный ТОП-30. Для каждой новости указать:
      - Заголовок.
      - **Рейтинг значимости (число).**
      - Список источников.
      - Краткое содержание (1-2 предложения).""",
    agent=deduplication_agent,
    context=[task_fetch]
)

# Задача 3: Анализ трендов с цепочкой мышления
task_analyze = Task(
    description="""Проанализируй ТОП-30 новостей. Твоя работа состоит из двух шагов:
    
    Шаг 1: 'Черновой анализ'. Внимательно прочти все тексты и выпиши списком все повторяющиеся
    темы, технологии, компании и продукты. Не бойся дублирования на этом этапе.
    
    Шаг 2: 'Синтез трендов'. На основе чернового анализа сгруппируй похожие темы
    и сформулируй 10 главных трендов. Каждый тренд должен быть четко назван и содержать:
    - Название тренда
    - Описание
    - Ключевые компании/продукты
    - Статус (Происходит сейчас / Ожидается в будущем)""",
    expected_output="""Структурированный список 10 трендов в формате Markdown.
    Для каждого тренда указать его название, описание, ключевые компании и статус.""",
    agent=trend_analyst,
    context=[task_deduplicate_and_rank]
)

# Задача 4: Критический анализ с поиском возможностей
task_critique = Task(
    description="""Проведи глубокий критический анализ 10 трендов.
    Для каждого тренда ответь на вопросы:
    
    1. **Практическое применение:** Какое практическое применение это имеет для независимого разработчика или малого бизнеса ПРЯМО СЕЙЧАС?
    
    2. **Риски:** Какой самый большой риск или неочевидная проблема связана с этим трендом?
    
    3. **Победители и проигравшие:** Какая технология или компания здесь может проиграть, а какая — неожиданно выиграть?
    
    4. **Низко висящие фрукты:** Какую конкретную 'низко висящую' возможность этот тренд открывает для стартапа, которую можно протестировать в течение месяца?""",
    expected_output="Структурированный отчет с развернутым критическим анализом каждого тренда по четырем вопросам.",
    agent=critical_analyst,
    context=[task_analyze]
)

# Задача 5: Написание развернутого дайджеста с четкой структурой
task_report = Task(
    description="""Создай финальный дайджест в стиле популярного техноблога.
    
    1. **Вступление:** Начни с яркого вступления, задающего тон всей статье.
    
    2. **Статистика:** Включи блок статистики (проанализировано/уникальных новостей).
    
    3. **ТОП-30 новостей:** Представь ТОП-30 новостей, но для каждой добавь **один абзац (3-4 предложения)** с кратким анализом 'Почему это важно'.
    
    4. **Тренды:** Для каждого из 10 трендов напиши **развернутый аналитический абзац (5-7 предложений)**.
       **Структурируй каждый абзац так:**
       - Начни с главного вывода о тренде
       - Приведи 1-2 примера из новостей для подтверждения
       - Закончи прогнозом влияния этого тренда, объединяя в нем риски и возможности из критического анализа
    
    5. **Заключение:** Заверши статью сильным заключением с прогнозом на ближайший квартал.
    
    Пиши в стиле увлекательного техноблога для IT-специалистов.""",
    expected_output="""Финальный отчет в формате Markdown, стилизованный под
    аналитическую статью в техноблоге с развернутыми комментариями и выводами.""",
    agent=strategic_reviewer,
    context=[task_deduplicate_and_rank, task_analyze, task_critique]
)

# --- ШАГ 5: СБОРКА И ЗАПУСК КОМАНДЫ V4 ---

ai_news_crew = Crew(
    agents=[news_analyst, deduplication_agent, trend_analyst, critical_analyst, strategic_reviewer],
    tasks=[task_fetch, task_deduplicate_and_rank, task_analyze, task_critique, task_report],
    process=Process.sequential,
    verbose=True
)

# Запускаем работу!
try:
    print("[START] Запускаю продвинутый анализ новостей V4...")
    print("[INFO] Новые возможности V4:")
    print("   - Объективная система оценки значимости новостей")
    print("   - Поиск 'низко висящих фруктов' для стартапов")
    print("   - Расширенные источники (NVIDIA, Tom's Hardware)")
    print("   - Оптимизированное распределение моделей")
    print("   - Четкая структура аналитических абзацев")
    
    result = ai_news_crew.kickoff()

    print("\n\n##################################")
    print("## ГОТОВЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ V4 ##")
    print("##################################\n")
    print(result)
    
except Exception as e:
    print(f"[ERROR] Критическая ошибка при выполнении анализа: {e}")
    print("[INFO] Проверьте:")
    print("   - Правильность API ключей в файле .env")
    print("   - Доступность RSS-лент")
    print("   - Подключение к интернету") 