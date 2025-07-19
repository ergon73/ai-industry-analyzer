# tests/test_v1_basic.py - Базовые тесты для V1

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from dotenv import load_dotenv

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Загружаем переменные окружения
load_dotenv()

class TestV1Basic:
    """Базовые тесты для версии V1"""
    
    def test_environment_variables(self):
        """Тест наличия необходимых переменных окружения"""
        # Проверяем наличие API ключа
        api_key = os.getenv('OPENAI_API_KEY')
        assert api_key is not None, "OPENAI_API_KEY не найден в .env файле"
        assert len(api_key) > 0, "OPENAI_API_KEY пустой"
        
        # Проверяем базовые переменные
        api_base = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4')
        
        assert api_base is not None, "OPENAI_API_BASE не установлен"
        assert model_name is not None, "OPENAI_MODEL_NAME не установлен"
    
    def test_imports(self):
        """Тест импорта основных модулей"""
        try:
            from crewai import Agent, Task, Crew, Process
            from crewai_tools import ScrapeWebsiteTool
            from langchain_openai import ChatOpenAI
            from dotenv import load_dotenv
            assert True, "Все необходимые модули импортированы успешно"
        except ImportError as e:
            pytest.fail(f"Ошибка импорта: {e}")
    
    def test_model_creation(self):
        """Тест создания моделей"""
        try:
            from langchain_openai import ChatOpenAI
            
            # Создаем модели
            smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
            fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
            
            assert smart_llm.model_name == "gpt-4.1", "Неверная модель для smart_llm"
            assert fast_llm.model_name == "gpt-4o-mini", "Неверная модель для fast_llm"
            assert smart_llm.temperature == 0.1, "Неверная температура для smart_llm"
            assert fast_llm.temperature == 0.1, "Неверная температура для fast_llm"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания моделей: {e}")
    
    def test_agent_creation(self):
        """Тест создания агентов"""
        try:
            from crewai import Agent
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
            
            # Создаем тестового агента
            test_agent = Agent(
                role='Тестовый агент',
                goal='Тестовая цель',
                backstory='Тестовая история',
                llm=llm,
                verbose=False
            )
            
            assert test_agent.role == 'Тестовый агент', "Неверная роль агента"
            assert test_agent.goal == 'Тестовая цель', "Неверная цель агента"
            assert test_agent.backstory == 'Тестовая история', "Неверная история агента"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания агента: {e}")
    
    def test_task_creation(self):
        """Тест создания задач"""
        try:
            from crewai import Task, Agent
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
            agent = Agent(
                role='Тестовый агент',
                goal='Тестовая цель',
                backstory='Тестовая история',
                llm=llm,
                verbose=False
            )
            
            # Создаем тестовую задачу
            test_task = Task(
                description='Тестовое описание',
                expected_output='Тестовый вывод',
                agent=agent
            )
            
            assert test_task.description == 'Тестовое описание', "Неверное описание задачи"
            assert test_task.expected_output == 'Тестовый вывод', "Неверный ожидаемый вывод"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания задачи: {e}")
    
    def test_crew_creation(self):
        """Тест создания команды"""
        try:
            from crewai import Agent, Task, Crew, Process
            from langchain_openai import ChatOpenAI
            
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
            
            # Создаем тестового агента
            agent = Agent(
                role='Тестовый агент',
                goal='Тестовая цель',
                backstory='Тестовая история',
                llm=llm,
                verbose=False
            )
            
            # Создаем тестовую задачу
            task = Task(
                description='Тестовое описание',
                expected_output='Тестовый вывод',
                agent=agent
            )
            
            # Создаем команду
            crew = Crew(
                agents=[agent],
                tasks=[task],
                process=Process.sequential,
                verbose=False
            )
            
            assert len(crew.agents) == 1, "Неверное количество агентов"
            assert len(crew.tasks) == 1, "Неверное количество задач"
            assert crew.process == Process.sequential, "Неверный процесс"
            
        except Exception as e:
            pytest.fail(f"Ошибка создания команды: {e}")

if __name__ == "__main__":
    pytest.main([__file__]) 