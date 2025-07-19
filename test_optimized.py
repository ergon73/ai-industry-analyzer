# test_optimized.py - Тестовая версия оптимизированного анализатора

import os
import feedparser
import requests
from bs4 import BeautifulSoup
from crewai import Agent, Task, Crew, Process
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Загружаем API ключи
load_dotenv()

# Создаем модели
smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)

# Функция для сбора статей из RSS
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
                
            # Берем только 2 последние новости для теста
            for entry in feed.entries[:2]:
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
        return "Не удалось получить контент статей. Проверьте доступность RSS-лент."
        
    return all_articles_content

# Создаем инструмент для скрапинга
scraper_tool = ScrapeWebsiteTool()

# Агенты
news_analyst = Agent(
    role='Ведущий аналитик новостей в сфере ИИ',
    goal="Собрать самые свежие публикации из RSS-лент.",
    backstory="Вы — опытный IT-журналист, который отслеживает пульс индустрии ИИ.",
    tools=[scraper_tool],
    llm=fast_llm,
    verbose=True
)

trend_analyst = Agent(
    role='Аналитик технологических трендов',
    goal="Проанализировать тексты статей и выделить 5 ключевых трендов.",
    backstory="Вы — data-аналитик с глубоким пониманием рынка ИИ.",
    llm=smart_llm,
    verbose=True
)

critical_analyst = Agent(
    role='Критический аналитик и скептик',
    goal="Найти неочевидные связи, риски и практические выводы для разработчиков.",
    backstory="Вы — опытный венчурный аналитик, который повидал сотни 'революционных' технологий.",
    llm=smart_llm,
    verbose=True
)

strategic_reviewer = Agent(
    role='Стратегический обозреватель',
    goal="Создать финальный дайджест, объединив анализ и критику.",
    backstory="Вы — 'правая рука' технического директора.",
    llm=fast_llm,
    verbose=True
)

# RSS-ленты для теста
RSS_FEEDS = """
    https://www.theverge.com/rss/ai-artificial-intelligence/index.xml,
    https://techcrunch.com/category/artificial-intelligence/feed/
"""

# Задачи
task_fetch_and_parse = Task(
    description=f"""Собрать статьи из RSS-лент: {RSS_FEEDS}
    
    Используй функцию collect_articles_from_rss для получения контента статей.
    Сфокусируйся на статьях, связанных с ИИ, машинным обучением, нейросетями.""",
    expected_output="Полный текст всех статей.",
    agent=news_analyst
)

task_analyze_trends = Task(
    description="Проанализировать тексты статей и выделить 5 главных трендов.",
    expected_output="Список 5 трендов в формате Markdown.",
    agent=trend_analyst,
    context=[task_fetch_and_parse]
)

task_critique_trends = Task(
    description="""Проанализируй список трендов и ответь на вопросы:
    1. Какое практическое применение для разработчика ПРЯМО СЕЙЧАС?
    2. Какой самый большой риск?
    3. Кто может проиграть, а кто выиграть?""",
    expected_output="Критический анализ каждого тренда.",
    agent=critical_analyst,
    context=[task_analyze_trends]
)

task_generate_report_final = Task(
    description="Создать финальный дайджест, объединив анализ и критику.",
    expected_output="Финальный отчет в формате Markdown.",
    agent=strategic_reviewer,
    context=[task_analyze_trends, task_critique_trends]
)

# Crew
ai_news_crew = Crew(
    agents=[news_analyst, trend_analyst, critical_analyst, strategic_reviewer],
    tasks=[task_fetch_and_parse, task_analyze_trends, task_critique_trends, task_generate_report_final],
    process=Process.sequential,
    verbose=True
)

# Запуск
if __name__ == "__main__":
    try:
        print("🚀 Запускаю оптимизированный анализ новостей...")
        result = ai_news_crew.kickoff()

        print("\n\n##################################")
        print("## ГОТОВЫЙ АНАЛИТИЧЕСКИЙ ОТЧЕТ ##")
        print("##################################\n")
        print(result)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}") 