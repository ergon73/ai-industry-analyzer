# tests/test_integration.py - Интеграционные тесты

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

class TestIntegration:
    """Интеграционные тесты для всего проекта"""
    
    def test_v1_file_exists(self):
        """Тест существования файла V1"""
        v1_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_news_analyzer.py")
        assert os.path.exists(v1_file), "Файл ai_news_analyzer.py не найден"
        
        # Проверяем размер файла
        file_size = os.path.getsize(v1_file)
        assert file_size > 1000, "Файл V1 слишком маленький"
    
    def test_v2_file_exists(self):
        """Тест существования файла V2"""
        v2_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ai_news_analyzer_v2.py")
        assert os.path.exists(v2_file), "Файл ai_news_analyzer_v2.py не найден"
        
        # Проверяем размер файла
        file_size = os.path.getsize(v2_file)
        assert file_size > 1000, "Файл V2 слишком маленький"
    
    def test_requirements_file(self):
        """Тест файла requirements.txt"""
        req_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "requirements.txt")
        assert os.path.exists(req_file), "Файл requirements.txt не найден"
        
        # Проверяем содержимое
        with open(req_file, 'r') as f:
            content = f.read()
            assert "crewai" in content, "crewai отсутствует в requirements.txt"
            assert "scikit-learn" in content, "scikit-learn отсутствует в requirements.txt"
    
    def test_readme_file(self):
        """Тест файла README.md"""
        readme_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
        assert os.path.exists(readme_file), "Файл README.md не найден"
        
        # Проверяем содержимое
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "AI News Analyzer" in content, "Название проекта отсутствует в README"
            assert "V2" in content, "Информация о V2 отсутствует в README"
    
    def test_project_overview_file(self):
        """Тест файла PROJECT_OVERVIEW.md"""
        overview_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "PROJECT_OVERVIEW.md")
        assert os.path.exists(overview_file), "Файл PROJECT_OVERVIEW.md не найден"
        
        # Проверяем содержимое
        with open(overview_file, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "AI News Analyzer" in content, "Название проекта отсутствует в обзоре"
            assert "V2" in content, "Информация о V2 отсутствует в обзоре"
    
    def test_v1_import_structure(self):
        """Тест структуры импортов V1"""
        try:
            # Импортируем основные компоненты V1
            import ai_news_analyzer
            
            # Проверяем наличие основных переменных
            assert hasattr(ai_news_analyzer, 'smart_llm'), "smart_llm не найден в V1"
            assert hasattr(ai_news_analyzer, 'fast_llm'), "fast_llm не найден в V1"
            
        except ImportError as e:
            pytest.fail(f"Ошибка импорта V1: {e}")
    
    def test_v2_import_structure(self):
        """Тест структуры импортов V2"""
        try:
            # Импортируем основные компоненты V2
            import ai_news_analyzer_v2
            
            # Проверяем наличие основных переменных
            assert hasattr(ai_news_analyzer_v2, 'smart_llm'), "smart_llm не найден в V2"
            assert hasattr(ai_news_analyzer_v2, 'fast_llm'), "fast_llm не найден в V2"
            
        except ImportError as e:
            pytest.fail(f"Ошибка импорта V2: {e}")
    
    def test_environment_setup(self):
        """Тест настройки окружения"""
        # Проверяем наличие .env файла
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        
        # Проверяем переменные окружения
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key is None:
            pytest.skip("OPENAI_API_KEY не установлен - пропускаем тест")
        
        assert len(api_key) > 0, "OPENAI_API_KEY пустой"
    
    def test_demo_files_exist(self):
        """Тест существования демонстрационных файлов"""
        demo_files = [
            "demo_v2.py",
            "test_v2.py", 
            "quick_test.py"
        ]
        
        for file_name in demo_files:
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), file_name)
            assert os.path.exists(file_path), f"Файл {file_name} не найден"
    
    def test_gitignore_file(self):
        """Тест файла .gitignore"""
        gitignore_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".gitignore")
        assert os.path.exists(gitignore_file), "Файл .gitignore не найден"
        
        # Проверяем содержимое
        with open(gitignore_file, 'r') as f:
            content = f.read()
            assert ".env" in content, ".env отсутствует в .gitignore"
            assert "__pycache__" in content, "__pycache__ отсутствует в .gitignore"
    
    def test_project_structure(self):
        """Тест структуры проекта"""
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        # Проверяем основные файлы
        required_files = [
            "ai_news_analyzer.py",
            "ai_news_analyzer_v2.py", 
            "requirements.txt",
            "README.md",
            "PROJECT_OVERVIEW.md",
            ".gitignore"
        ]
        
        for file_name in required_files:
            file_path = os.path.join(project_root, file_name)
            assert os.path.exists(file_path), f"Обязательный файл {file_name} не найден"
    
    def test_python_files_syntax(self):
        """Тест синтаксиса Python файлов"""
        import ast
        
        python_files = [
            "ai_news_analyzer.py",
            "ai_news_analyzer_v2.py",
            "demo_v2.py",
            "test_v2.py",
            "quick_test.py"
        ]
        
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        for file_name in python_files:
            file_path = os.path.join(project_root, file_name)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        source = f.read()
                        ast.parse(source)
                except SyntaxError as e:
                    pytest.fail(f"Синтаксическая ошибка в {file_name}: {e}")
    
    def test_model_configurations(self):
        """Тест конфигураций моделей"""
        try:
            from langchain_openai import ChatOpenAI
            
            # Тестируем конфигурации моделей
            smart_llm = ChatOpenAI(model_name="gpt-4.1", temperature=0.1)
            fast_llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.1)
            
            # Проверяем, что модели созданы с правильными параметрами
            assert smart_llm.model_name == "gpt-4.1", "Неверная модель для smart_llm"
            assert fast_llm.model_name == "gpt-4o-mini", "Неверная модель для fast_llm"
            assert smart_llm.temperature == 0.1, "Неверная температура для smart_llm"
            assert fast_llm.temperature == 0.1, "Неверная температура для fast_llm"
            
        except Exception as e:
            pytest.fail(f"Ошибка конфигурации моделей: {e}")

if __name__ == "__main__":
    pytest.main([__file__]) 