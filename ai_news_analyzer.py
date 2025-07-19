# ai_news_analyzer.py

import os
import feedparser
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv
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

# --- ШАГ 1: СОЗДАНИЕ ФУНКЦИИ ДЛЯ СБОРА СТАТЕЙ ---
def collect_articles_from_rss(rss_feed_urls: str) -> str:
    """Собирает статьи из RSS-лент и возвращает их содержимое"""
    all_articles_content = ""
    urls = [url.strip() for url in rss_feed_urls.split(',')]

    print(f"--- [ФУНКЦИЯ] Начинаю работу с {len(urls)} RSS-лентами ---")

    for url in urls:
        try:
            print(f"📡 Обрабатываю RSS-ленту: {url}")
            feed = feedparser.parse(url)
            
            if not feed.entries:
                print(f"⚠️  RSS-лента {url} не содержит статей")
                continue
                
            # Берем только 3 последние новости из каждой ленты
            for entry in feed.entries[:3]:
                print(f"📄 Скачиваю статью: {entry.title} ---")
                try:
                    response = requests.get(entry.link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Удаляем ненужные теги
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.decompose()

                    # Пытаемся найти основной контент статьи
                    content = soup.find('article') or soup.find('div', class_='content') or soup.find('main') or soup.find('body')
                    if content:
                        text = content.get_text(separator='\n', strip=True)
                        all_articles_content += f"\n\n--- СТАТЬЯ: {entry.title} ---\n{text}"
                    else:
                        all_articles_content += f"\n\n--- СТАТЬЯ: {entry.title} ---\nНе удалось извлечь основной контент."

                except Exception as e:
                    print(f"❌ Не удалось скачать статью {entry.link}: {e}")
                    continue
        except Exception as e:
            print(f"❌ Ошибка при обработке RSS-ленты {url}: {e}")
            continue

    if not all_articles_content.strip():
        print("⚠️  Не удалось получить контент ни из одной статьи")
        return "Не удалось получить контент статей. Проверьте доступность RSS-лент."
        
    return all_articles_content

# Создаем инструмент для скрапинга веб-страниц
scraper_tool = ScrapeWebsiteTool()


# --- ШАГ 2: ОПРЕДЕЛЕНИЕ АГЕНТОВ С НОВЫМИ РОЛЯМИ ---

# Агент для сбора данных (использует быструю модель)
news_analyst = Agent(
    role='Ведущий аналитик новостей в сфере ИИ',
    goal=f"""Собрать самые свежие публикации из предоставленных RSS-лент.
    Сфокусироваться на темах: видеоускорители (NVIDIA, AMD), софт для локального запуска ИИ
    (LM Studio, Ollama, Jan.ai), ноутбуки и мини-ПК для ИИ, одноплатные компьютеры для ИИ.""",
    backstory="""Вы — опытный IT-журналист, который отслеживает пульс индустрии искусственного интеллекта.
    Ваша задача — отделить зерна от плевел и найти самую важную информацию, проигнорировав маркетинговую "воду".""",
    tools=[scraper_tool],  # Инструмент для скрапинга
    llm=fast_llm,  # Быстрая модель для простой задачи
    verbose=True
)

# Агент для анализа трендов (использует умную модель)
trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="""Проанализировать тексты всех собранных статей и выделить 10 ключевых, повторяющихся трендов.
    Для каждого тренда указать ключевые компании, продукты и технологии.
    Оценить, является тренд текущим или будущим событием.""",
    backstory="""Вы — data-аналитик с глубоким пониманием рынка ИИ. Вы видите скрытые связи
    между разными новостями и можете предсказывать, какие технологии "выстрелят" завтра.""",
    llm=smart_llm,  # Умная модель для анализа
    verbose=True
)

# НОВЫЙ АГЕНТ: Критический аналитик (использует умную модель)
critical_analyst = Agent(
    role='Критический аналитик и скептик',
    goal="""Изучить предложенный список трендов и найти в них неочевидные связи, потенциальные риски
    и практические выводы для разработчиков и бизнеса. Оспорить поверхностные выводы.""",
    backstory="""Вы — опытный венчурный аналитик, который повидал сотни 'революционных' технологий.
    Ваша задача — отделить реальные сигналы от шума, найти подводные камни и дать
    практические, действенные рекомендации, а не просто пересказывать новости.""",
    llm=smart_llm,  # Умная модель для критического анализа
    verbose=True
)

# Агент для финального отчета (использует быструю модель)
strategic_reviewer = Agent(
    role='Стратегический обозреватель для принятия решений',
    goal="""На основе выделенных трендов сгенерировать краткий и емкий еженедельный отчет (дайджест)
    в формате Markdown для руководителя. Отчет должен быть структурированным, легким для чтения
    и содержать только самую суть для быстрого погружения в повестку дня.""",
    backstory="""Вы — "правая рука" технического директора. Вы умеете переводить сложный технический
    язык на язык бизнеса и стратегии. Ваш отчет помогает руководству принимать верные решения.""",
    llm=fast_llm,  # Быстрая модель для форматирования
    verbose=True
)


# --- ШАГ 3: ОПРЕДЕЛЕНИЕ ЗАДАЧ ДЛЯ АГЕНТОВ ---

# Список RSS-лент для анализа (можно добавлять свои)
RSS_FEEDS = """
    https://www.theverge.com/rss/ai-artificial-intelligence/index.xml,
    http://feeds.arstechnica.com/arstechnica/index/,
    https://techcrunch.com/category/artificial-intelligence/feed/
"""

# Задача 1: Сбор данных (оптимизированная)
task_fetch_and_parse = Task(
    description=f"""Собрать и очистить тексты статей из следующих RSS-лент: {RSS_FEEDS}
    
    Используй функцию collect_articles_from_rss для получения контента статей.
    Сфокусируйся на статьях, связанных с ИИ, машинным обучением, нейросетями.""",
    expected_output="Полный текст всех статей, объединенный в один большой текстовый документ.",
    agent=news_analyst
)

# Задача 2: Анализ трендов
task_analyze_trends = Task(
    description="""Проанализировать предоставленный текст статей и составить список из 10 главных трендов.
    Каждый тренд должен быть представлен в виде:
    - Название тренда.
    - Ключевые слова/компании/продукты.
    - Статус (Происходит сейчас / Ожидается в будущем).""",
    expected_output="Структурированный список 10 трендов в формате Markdown.",
    agent=trend_analyst,
    context=[task_fetch_and_parse]
)

# НОВАЯ ЗАДАЧА 3: Критический анализ
task_critique_trends = Task(
    description="""Проанализируй список из 10 трендов, полученный от Аналитика трендов.
    Для каждого тренда ответь на следующие вопросы:
    1. Какое практическое применение это имеет для независимого разработчика или малого бизнеса ПРЯМО СЕЙЧАС?
    2. Какой самый большой риск или неочевидная проблема связана с этим трендом?
    3. Какая технология или компания здесь может проиграть, а какая — неожиданно выиграть?""",
    expected_output="""Структурированный отчет с критическим анализом каждого из 10 трендов,
    отвечающий на три поставленных вопроса по каждому пункту.""",
    agent=critical_analyst,
    context=[task_analyze_trends]
)

# ИЗМЕНЕННАЯ ЗАДАЧА 4: Финальный отчет
task_generate_report_final = Task(
    description="""Проанализируй первоначальный список трендов И критический разбор к нему.
    Твоя задача — создать финальный дайджест, объединив оба анализа.
    Для каждого тренда укажи его описание, а затем добавь раздел 'Практический вывод и риски'
    на основе критического анализа.""",
    expected_output="Финальный, глубокий и структурированный отчет в формате Markdown, включающий как описание трендов, так и их критическую оценку.",
    agent=strategic_reviewer,
    context=[task_analyze_trends, task_critique_trends]
)


# --- ШАГ 4: СБОРКА И ЗАПУСК КОМАНДЫ ---

ai_news_crew = Crew(
    agents=[news_analyst, trend_analyst, critical_analyst, strategic_reviewer],
    tasks=[task_fetch_and_parse, task_analyze_trends, task_critique_trends, task_generate_report_final],
    process=Process.sequential,
    verbose=True
)

# Запускаем работу!
try:
    print("🚀 Запускаю анализ новостей...")
    result = ai_news_crew.kickoff()

    print("\n\n##################################")
    print("## ГОТОВЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ ##")
    print("##################################\n")
    print(result)
    
except Exception as e:
    print(f"❌ Критическая ошибка при выполнении анализа: {e}")
    print("💡 Проверьте:")
    print("   - Правильность API ключей в файле .env")
    print("   - Доступность RSS-лент")
    print("   - Подключение к интернету")