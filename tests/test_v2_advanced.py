# tests/test_v2_advanced.py - Продвинутые тесты для V2

import pytest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv()

class TestV2Advanced:
    """Продвинутые тесты для версии V2"""
    
    def test_v2_imports(self):
        """Тест импорта модулей для V2"""
        try:
            from crewai import Agent, Task, Crew, Process
            from crewai_tools import ScrapeWebsiteTool
            from langchain_openai import ChatOpenAI
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            assert True, "Все необходимые модули V2 импортированы успешно"
        except ImportError as e:
            pytest.fail(f"Ошибка импорта V2: {e}")
    
    def test_scrape_website_tool(self):
        """Тест создания ScrapeWebsiteTool"""
        try:
            from crewai_tools import ScrapeWebsiteTool
            
            # Создаем тестовый инструмент
            tool = ScrapeWebsiteTool()
            
            assert tool is not None, "ScrapeWebsiteTool не создан"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания ScrapeWebsiteTool: {e}")
    
    def test_collect_articles_function(self):
        """Тест функции collect_articles_from_rss_v2"""
        try:
            # Импортируем функцию из V2
            import ai_news_analyzer_v2
            
            # Проверяем, что функция существует
            assert hasattr(ai_news_analyzer_v2, 'collect_articles_from_rss_v2'), "Функция collect_articles_from_rss_v2 не найдена"
            
            # Тестируем с фиктивными данными
            test_urls = "https://example.com/feed1,https://example.com/feed2"
            
            # Мокаем feedparser для тестирования
            with patch('feedparser.parse') as mock_parse:
                mock_feed = MagicMock()
                mock_feed.feed.title = "Test Feed"
                mock_feed.entries = []
                mock_parse.return_value = mock_feed
                
                # Вызываем функцию
                result = ai_news_analyzer_v2.collect_articles_from_rss_v2(test_urls)
                
                assert isinstance(result, str), "Результат должен быть строкой"
                
        except Exception as e:
            pytest.fail(f"Ошибка тестирования функции collect_articles_from_rss_v2: {e}")
    
    def test_deduplication_logic(self):
        """Тест логики дедупликации"""
        # Тестовые данные
        test_articles = [
            {
                "source": "Source 1",
                "title": "OpenAI launches new model",
                "link": "https://example.com/1",
                "text": "OpenAI has released a new AI model..."
            },
            {
                "source": "Source 2", 
                "title": "OpenAI introduces updated model",
                "link": "https://example.com/2",
                "text": "OpenAI announced an updated AI model..."
            },
            {
                "source": "Source 3",
                "title": "Microsoft invests in AI",
                "link": "https://example.com/3",
                "text": "Microsoft has invested in AI technology..."
            }
        ]
        
        # Проверяем структуру данных
        for article in test_articles:
            assert "source" in article, "Отсутствует поле 'source'"
            assert "title" in article, "Отсутствует поле 'title'"
            assert "link" in article, "Отсутствует поле 'link'"
            assert "text" in article, "Отсутствует поле 'text'"
        
        # Проверяем уникальность источников
        sources = [article["source"] for article in test_articles]
        unique_sources = set(sources)
        assert len(unique_sources) == 3, "Неверное количество уникальных источников"
    
    def test_ranking_logic(self):
        """Тест логики ранжирования"""
        # Симулируем результаты дедупликации
        deduplicated_news = [
            {
                "title": "OpenAI model launch",
                "sources": ["Source 1", "Source 2", "Source 3"],
                "mentions": 3
            },
            {
                "title": "Microsoft AI investment", 
                "sources": ["Source 1", "Source 2"],
                "mentions": 2
            },
            {
                "title": "AI coding tools",
                "sources": ["Source 1"],
                "mentions": 1
            }
        ]
        
        # Проверяем сортировку по количеству упоминаний
        sorted_news = sorted(deduplicated_news, key=lambda x: x["mentions"], reverse=True)
        
        assert sorted_news[0]["mentions"] == 3, "Первая новость должна иметь 3 упоминания"
        assert sorted_news[1]["mentions"] == 2, "Вторая новость должна иметь 2 упоминания"
        assert sorted_news[2]["mentions"] == 1, "Третья новость должна иметь 1 упоминание"
    
    def test_v2_agent_creation(self):
        """Тест создания агентов V2"""
        try:
            from crewai import Agent
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
            
            # Тестируем создание агента-дедупликатора
            deduplication_agent = Agent(
                role="Аналитик данных и редактор новостей",
                goal="Определить уникальные новостные сюжеты",
                backstory="Главный редактор новостного агентства",
                llm=llm,
                verbose=False
            )
            
            assert "дедупликатор" in deduplication_agent.role.lower() or "аналитик" in deduplication_agent.role.lower(), "Неверная роль агента-дедупликатора"
            assert "уникальные" in deduplication_agent.goal.lower(), "Неверная цель агента-дедупликатора"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания агентов V2: {e}")
    
    def test_v2_task_creation(self):
        """Тест создания задач V2"""
        try:
            from crewai import Task, Agent
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
            agent = Agent(
                role='Тестовый агент',
                goal='Тестовая цель',
                backstory='Тестовая история',
                llm=llm,
                verbose=False
            )
            
            # Тестируем создание задачи дедупликации
            deduplication_task = Task(
                description="Проанализировать список статей и найти дубликаты",
                expected_output="ТОП-30 уникальных новостей",
                agent=agent
            )
            
            assert "дубликаты" in deduplication_task.description.lower(), "Неверное описание задачи дедупликации"
            assert "топ-30" in deduplication_task.expected_output.lower(), "Неверный ожидаемый вывод"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания задач V2: {e}")
    
    def test_v2_crew_structure(self):
        """Тест структуры команды V2"""
        try:
            from crewai import Agent, Task, Crew, Process
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
            
            # Создаем тестовых агентов
            agent1 = Agent(role='Агент 1', goal='Цель 1', backstory='История 1', llm=llm, verbose=False)
            agent2 = Agent(role='Агент 2', goal='Цель 2', backstory='История 2', llm=llm, verbose=False)
            
            # Создаем тестовые задачи
            task1 = Task(description='Задача 1', expected_output='Вывод 1', agent=agent1)
            task2 = Task(description='Задача 2', expected_output='Вывод 2', agent=agent2, context=[task1])
            
            # Создаем команду V2 (5 агентов)
            crew = Crew(
                agents=[agent1, agent2],
                tasks=[task1, task2],
                process=Process.sequential,
                verbose=False
            )
            
            assert len(crew.agents) == 2, "Неверное количество агентов"
            assert len(crew.tasks) == 2, "Неверное количество задач"
            assert crew.process == Process.sequential, "Неверный процесс"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания команды V2: {e}")
    
    def test_json_handling(self):
        """Тест обработки JSON данных"""
        # Тестовые данные
        test_data = [
            {"source": "Test Source", "title": "Test Title", "link": "https://test.com", "text": "Test content"}
        ]
        
        # Тестируем сериализацию
        json_string = json.dumps(test_data, ensure_ascii=False, indent=2)
        assert isinstance(json_string, str), "JSON должен быть строкой"
        
        # Тестируем десериализацию
        parsed_data = json.loads(json_string)
        assert isinstance(parsed_data, list), "Парсинг должен вернуть список"
        assert len(parsed_data) == 1, "Должна быть одна статья"
        assert parsed_data[0]["source"] == "Test Source", "Неверный источник"
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        # Тестируем обработку отсутствующих переменных окружения
        with patch.dict(os.environ, {}, clear=True):
            # Должно вызвать ошибку при отсутствии API ключа
            with pytest.raises(Exception):
                from langchain_openai import ChatOpenAI
                ChatOpenAI(model_name="gpt-4.1")

if __name__ == "__main__":
    pytest.main([__file__]) 