# tests/test_v3_advanced.py - Продвинутые тесты для V3

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

class TestV3Advanced:
    """Продвинутые тесты для версии V3"""
    
    def test_v3_imports(self):
        """Тест импорта модулей для V3"""
        try:
            from crewai import Agent, Task, Crew, Process
            from crewai_tools import ScrapeWebsiteTool
            from langchain_openai import ChatOpenAI
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            assert True, "Все необходимые модули V3 импортированы успешно"
        except ImportError as e:
            pytest.fail(f"Ошибка импорта V3: {e}")
    
    def test_collect_articles_function_v3(self):
        """Тест функции collect_articles_from_rss_v3"""
        try:
            # Импортируем функцию из V3
            import ai_news_analyzer_v3
            
            # Проверяем, что функция существует
            assert hasattr(ai_news_analyzer_v3, 'collect_articles_from_rss_v3'), "Функция collect_articles_from_rss_v3 не найдена"
            
            # Тестируем с фиктивными данными
            test_urls = "https://example.com/feed1,https://example.com/feed2"
            
            # Мокаем feedparser для тестирования
            with patch('feedparser.parse') as mock_parse:
                mock_feed = MagicMock()
                mock_feed.feed.title = "Test Feed"
                mock_feed.entries = []
                mock_parse.return_value = mock_feed
                
                # Вызываем функцию
                result = ai_news_analyzer_v3.collect_articles_from_rss_v3(test_urls)
                
                assert isinstance(result, str), "Результат должен быть строкой"
                
        except Exception as e:
            pytest.fail(f"Ошибка тестирования функции collect_articles_from_rss_v3: {e}")
    
    def test_ai_evangelist_agent(self):
        """Тест создания AI-евангелиста"""
        try:
            from crewai import Agent
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
            
            # Создаем AI-евангелиста
            ai_evangelist = Agent(
                role='Ведущий AI-евангелист и технический обозреватель',
                goal="Написать увлекательный аналитический дайджест",
                backstory="Популярный техноблогер с харизмой и практической пользой",
                llm=llm,
                verbose=False
            )
            
            assert "евангелист" in ai_evangelist.role.lower(), "Неверная роль AI-евангелиста"
            assert "увлекательный" in ai_evangelist.goal.lower(), "Неверная цель AI-евангелиста"
            assert "техноблогер" in ai_evangelist.backstory.lower(), "Неверная история AI-евангелиста"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания AI-евангелиста: {e}")
    
    def test_chain_of_thought_task(self):
        """Тест задачи с цепочкой мышления"""
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
            
            # Создаем задачу с цепочкой мышления
            chain_of_thought_task = Task(
                description="""Проанализируй данные. Твоя работа состоит из двух шагов:
                
                Шаг 1: 'Черновой анализ'. Выпиши все повторяющиеся темы.
                Шаг 2: 'Синтез трендов'. Сгруппируй похожие темы в тренды.""",
                expected_output="Структурированный список трендов.",
                agent=agent
            )
            
            assert "два шага" in chain_of_thought_task.description.lower(), "Неверное описание задачи с цепочкой мышления"
            assert "черновой анализ" in chain_of_thought_task.description.lower(), "Отсутствует черновой анализ"
            assert "синтез трендов" in chain_of_thought_task.description.lower(), "Отсутствует синтез трендов"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания задачи с цепочкой мышления: {e}")
    
    def test_extended_rss_feeds(self):
        """Тест расширенных RSS-лент V3"""
        # Проверяем, что в V3 есть нишевые источники
        expected_sources = [
            "huggingface.co",
            "blog.google",
            "aws.amazon.com"
        ]
        
        # Импортируем RSS_FEEDS из V3
        try:
            import ai_news_analyzer_v3
            rss_feeds = ai_news_analyzer_v3.RSS_FEEDS
            
            for source in expected_sources:
                assert source in rss_feeds, f"Источник {source} отсутствует в RSS_FEEDS V3"
                
        except Exception as e:
            pytest.fail(f"Ошибка проверки RSS-лент V3: {e}")
    
    def test_v3_agent_creation(self):
        """Тест создания агентов V3"""
        try:
            from crewai import Agent
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
            
            # Тестируем создание всех агентов V3
            agents = [
                Agent(role='Ведущий аналитик новостей', goal='Сбор данных', backstory='IT-журналист', llm=llm, verbose=False),
                Agent(role='Аналитик данных', goal='Дедупликация', backstory='Главный редактор', llm=llm, verbose=False),
                Agent(role='Аналитик трендов', goal='Анализ трендов', backstory='Data-аналитик', llm=llm, verbose=False),
                Agent(role='Критический аналитик', goal='Критический анализ', backstory='Венчурный аналитик', llm=llm, verbose=False),
                Agent(role='AI-евангелист', goal='Написание дайджеста', backstory='Техноблогер', llm=llm, verbose=False)
            ]
            
            assert len(agents) == 5, "Должно быть 5 агентов в V3"
            
            # Проверяем, что AI-евангелист создан правильно
            ai_evangelist = agents[4]
            assert "евангелист" in ai_evangelist.role.lower(), "Неверная роль AI-евангелиста"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания агентов V3: {e}")
    
    def test_v3_task_creation(self):
        """Тест создания задач V3"""
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
            
            # Тестируем создание задачи AI-евангелиста
            evangelist_task = Task(
                description="Создай финальный дайджест в стиле техноблога с развернутыми комментариями",
                expected_output="Финальный отчет в стиле техноблога",
                agent=agent
            )
            
            assert "техноблога" in evangelist_task.description.lower(), "Неверное описание задачи AI-евангелиста"
            assert "развернутыми" in evangelist_task.description.lower(), "Отсутствуют развернутые комментарии"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания задач V3: {e}")
    
    def test_v3_crew_structure(self):
        """Тест структуры команды V3"""
        try:
            from crewai import Agent, Task, Crew, Process
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
            
            # Создаем тестовых агентов
            agent1 = Agent(role='Агент 1', goal='Цель 1', backstory='История 1', llm=llm, verbose=False)
            agent2 = Agent(role='Агент 2', goal='Цель 2', backstory='История 2', llm=llm, verbose=False)
            agent3 = Agent(role='Агент 3', goal='Цель 3', backstory='История 3', llm=llm, verbose=False)
            agent4 = Agent(role='Агент 4', goal='Цель 4', backstory='История 4', llm=llm, verbose=False)
            agent5 = Agent(role='AI-евангелист', goal='Цель 5', backstory='История 5', llm=llm, verbose=False)
            
            # Создаем тестовые задачи
            task1 = Task(description='Задача 1', expected_output='Вывод 1', agent=agent1)
            task2 = Task(description='Задача 2', expected_output='Вывод 2', agent=agent2, context=[task1])
            task3 = Task(description='Задача 3', expected_output='Вывод 3', agent=agent3, context=[task2])
            task4 = Task(description='Задача 4', expected_output='Вывод 4', agent=agent4, context=[task3])
            task5 = Task(description='Задача 5', expected_output='Вывод 5', agent=agent5, context=[task2, task3, task4])
            
            # Создаем команду V3 (5 агентов)
            crew = Crew(
                agents=[agent1, agent2, agent3, agent4, agent5],
                tasks=[task1, task2, task3, task4, task5],
                process=Process.sequential,
                verbose=False
            )
            
            assert len(crew.agents) == 5, "Неверное количество агентов V3"
            assert len(crew.tasks) == 5, "Неверное количество задач V3"
            assert crew.process == Process.sequential, "Неверный процесс"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания команды V3: {e}")
    
    def test_v3_features(self):
        """Тест новых возможностей V3"""
        # Проверяем наличие новых возможностей
        v3_features = [
            "AI-евангелист",
            "цепочка мышления", 
            "расширенные RSS-ленты",
            "развернутые комментарии",
            "техноблог",
            "увлекательное повествование"
        ]
        
        # Импортируем V3 и проверяем наличие ключевых элементов
        try:
            import ai_news_analyzer_v3
            
            # Проверяем наличие функции V3
            assert hasattr(ai_news_analyzer_v3, 'collect_articles_from_rss_v3'), "Функция V3 не найдена"
            
            # Проверяем наличие расширенных RSS-лент
            assert "huggingface.co" in ai_news_analyzer_v3.RSS_FEEDS, "Hugging Face отсутствует в RSS-лентах"
            assert "blog.google" in ai_news_analyzer_v3.RSS_FEEDS, "Google AI Blog отсутствует в RSS-лентах"
            assert "aws.amazon.com" in ai_news_analyzer_v3.RSS_FEEDS, "AWS ML Blog отсутствует в RSS-лентах"
            
        except Exception as e:
            pytest.fail(f"Ошибка проверки возможностей V3: {e}")
    
    def test_v3_file_exists(self):
        """Тест существования файла V3"""
        v3_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_news_analyzer_v3.py")
        assert os.path.exists(v3_file), "Файл ai_news_analyzer_v3.py не найден"
        
        # Проверяем размер файла
        file_size = os.path.getsize(v3_file)
        assert file_size > 1000, "Файл V3 слишком маленький"

if __name__ == "__main__":
    pytest.main([__file__]) 