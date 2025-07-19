# 🚀 Установка и настройка AI Industry Analyzer

## 📋 Предварительные требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Git (для клонирования репозитория)

## 🔧 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/ergon73/ai-industry-analyzer.git
cd ai-industry-analyzer
```

### 2. Создание виртуального окружения

#### Для Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Для macOS/Linux:
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 🔑 Настройка API ключей

### 1. Создание файла .env

Создайте файл `.env` в корне проекта:

```bash
# Windows
copy env_example .env

# macOS/Linux
cp env_example .env
```

### 2. Настройка API ключей

Отредактируйте файл `.env` и добавьте ваши API ключи:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4.1
```

#### Где получить API ключ:

1. Перейдите на [platform.openai.com](https://platform.openai.com/api-keys)
2. Создайте новый API ключ
3. Скопируйте ключ в файл `.env`

#### Альтернативные провайдеры:

Если вы используете прокси-сервер (например, для России):

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1
OPENAI_MODEL_NAME=gpt-4.1
```

## 🧪 Тестирование установки

### Быстрая проверка:

```bash
python -c "import crewai; print('✅ CrewAI установлен')"
python -c "import langchain_openai; print('✅ LangChain OpenAI установлен')"
```

### Запуск тестов:

```bash
# Все тесты
python run_tests.py

# Отдельные тесты
python -m pytest tests/test_v1_basic.py -v
python -m pytest tests/test_v2_advanced.py -v
python -m pytest tests/test_v3_advanced.py -v
```

## 🚀 Запуск

### V1 - Базовая версия:
```bash
python ai_news_analyzer.py
```

### V2 - Продвинутая версия:
```bash
python ai_news_analyzer_v2.py
```

### V3 - Персонализированная версия:
```bash
python ai_news_analyzer_v3.py
```

### Тестовые версии:
```bash
# Тест V2
python test_v2_fixed.py

# Тест V3
python test_v3.py
```

## 📊 Что анализирует система

### RSS-ленты по умолчанию:

#### V1 и V2:
- The Verge (AI раздел)
- Ars Technica
- TechCrunch (AI раздел)
- VentureBeat (AI раздел) - V2
- Wired (Business раздел) - V2

#### V3 (дополнительно):
- Hugging Face Blog
- Google AI Blog
- AWS ML Blog

### Темы анализа:
- 🎯 Новости по ИИ-технологиям
- 🏢 Компании в сфере ИИ (OpenAI, Google, NVIDIA, etc.)
- 📈 Тренды машинного обучения
- 🔬 Исследования в области ИИ
- 💻 Инструменты для разработчиков ИИ
- 🖥️ Железо для ИИ (GPU, специализированные чипы)

## 💰 Оптимизация стоимости

### Модели по умолчанию:
- `gpt-4o-mini` - для простых задач (сбор данных, форматирование)
- `gpt-4.1` - для сложного анализа и критики

### Ожидаемые расходы:
- **V1**: ~$2-5 за анализ
- **V2**: ~$3-7 за анализ (с дедупликацией)
- **V3**: ~$4-10 за анализ (с расширенными возможностями)

## 🔧 Настройка RSS-лент

Вы можете изменить список RSS-лент в соответствующих файлах:

```python
# В ai_news_analyzer.py, ai_news_analyzer_v2.py, ai_news_analyzer_v3.py
RSS_FEEDS = """
    https://your-rss-feed-1.com/feed,
    https://your-rss-feed-2.com/feed
"""
```

## 🐛 Устранение неполадок

### Ошибка "ModuleNotFoundError":
```bash
# Убедитесь, что виртуальное окружение активировано
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Переустановите зависимости
pip install -r requirements.txt
```

### Ошибка "OPENAI_API_KEY not found":
```bash
# Проверьте файл .env
cat .env  # macOS/Linux
type .env  # Windows

# Убедитесь, что API ключ правильный
```

### Ошибка "Connection timeout":
- Проверьте интернет-соединение
- Попробуйте другой API Base URL
- Проверьте доступность RSS-лент

### Ошибка "Rate limit exceeded":
- Подождите несколько минут
- Проверьте лимиты вашего API ключа
- Рассмотрите использование другого API ключа

## 📈 Мониторинг использования

### Проверка токенов:
```bash
# Добавьте в код для отладки
print(f"Использовано токенов: {llm.get_num_tokens_from_messages(messages)}")
```

### Логирование:
```bash
# Включите verbose режим в агентах
verbose=True
```

## 🔄 Обновления

### Обновление зависимостей:
```bash
pip install --upgrade -r requirements.txt
```

### Обновление кода:
```bash
git pull origin master
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. Проверьте раздел "Устранение неполадок"
2. Запустите тесты: `python run_tests.py`
3. Создайте issue на GitHub с описанием проблемы
4. Укажите версию Python и операционную систему

## 🎯 Рекомендации

### Для ежедневного использования:
- Используйте V1 для быстрого анализа
- Запускайте утром для получения дайджеста

### Для глубокого анализа:
- Используйте V2 для полной аналитики
- Запускайте еженедельно

### Для персонализированного опыта:
- Используйте V3 для увлекательных дайджестов
- Идеально для IT-специалистов

## 📚 Дополнительные ресурсы

- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [LangChain Documentation](https://python.langchain.com/)
- [pytest Documentation](https://docs.pytest.org/)

---

**Удачного использования AI Industry Analyzer!** 🚀 