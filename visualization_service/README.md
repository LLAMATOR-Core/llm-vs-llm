# Визуализация Результатов Тестов

Этот сервис позволяет визуализировать результаты тестов из нескольких CSV-файлов с помощью веб-интерфейса на основе Gradio.

## Файлы данных

Убедитесь, что в папке `visualization_data` находятся следующие файлы:

- attacks_result.csv
- ethical_scores.csv
- logical_scores.csv
- sycophancy_scores.csv

## Установка зависимостей

**Установите необходимые библиотеки из `requirements.txt`**:

   ```bash
   pip install -r requirements.txt
   ```

## Запуск сервиса

1. **Перейдите в директорию `visualization_service` с файлом `main.py`**.

2. **Запустите сервис из консоли**:

   ```bash
   python main.py
   ```

3. **Откройте веб-интерфейс**:

## Описание визуализации

- **Верхний график**: Отображает результаты атак из *attacks_result.csv* в виде сгруппированных столбцов.

- **Нижние графики**: Три тепловые карты для метрик из файлов:
  - *ethical_scores.csv* — Ethical Compliance
  - *logical_scores.csv* — Logical Inconsistencies Test
  - *sycophancy_scores.csv* — Sycophancy Test
