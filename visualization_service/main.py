"""
Модуль для визуализации четырёх CSV-файлов:
1) attacks_result.csv (отображается одним большим графиком в верхнем ряду)
2) ethical_scores.csv
3) logical_scores.csv
4) sycophancy_scores.csv

Графики с 2) по 4) показываются в нижнем ряду в виде тепловых карт.

Файлы должны находиться в папке 'visualization_data'.

Пример запуска из консоли:
    python main.py
"""

import gradio as gr
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def create_plots():
    """
    Возвращает фигуру (Figure), в которой расположено 4 графика:
    1) Верхний ряд: attacks_result.csv (сгруппированные столбцы для verdict=True/False по каждому attack)
    2) Нижний ряд: три тепловые карты для ethical_scores.csv, logical_scores.csv и sycophancy_scores.csv
    """

    # Загружаем данные
    df_attacks = pd.read_csv("visualization_data/attacks_result.csv")
    df_ethical = pd.read_csv("visualization_data/ethical_scores.csv")
    df_logical = pd.read_csv("visualization_data/logical_scores.csv")
    df_sycophancy = pd.read_csv("visualization_data/sycophancy_scores.csv")

    # Настраиваем сетку фигуры: 2 строки, 3 столбца
    # Первая строка (row 0) - один широкий график (attacks)
    # Вторая строка (row 1) - три тепловые карты
    fig = plt.figure(figsize=(24, 12))
    gs = fig.add_gridspec(2, 3, height_ratios=[1, 1])

    # 1) Верхний график (занимает всю первую строку: столбцы 0..2)
    ax_top = fig.add_subplot(gs[0, :])

    # Преобразуем attacks_result.csv для построения графика
    # Сгруппируем данные так, чтобы атаки шли по оси X, а столбцы отражали вердикт True/False
    pivot_attacks = df_attacks.pivot(index="attack", columns="verdict", values="count")
    # Заполним возможные пропуски нулями, если вдруг такие есть
    pivot_attacks.fillna(0, inplace=True)

    # Удаляем нижние подчёркивания из названий атак
    pivot_attacks.index = pivot_attacks.index.str.replace("_", " ")

    # Построим сгруппированные столбцы
    pivot_attacks.plot(
        kind="bar",
        ax=ax_top,
        stacked=False,
        width=0.7,
        cmap="Set2"
    )
    ax_top.set_title("Результаты атак (Количество)", fontsize=16)
    ax_top.set_xlabel("Тип атаки")
    ax_top.set_ylabel("Частота")
    ax_top.legend(title="Вердикт", loc="best")
    ax_top.grid(True, axis='y')

    # Устанавливаем горизонтальную ориентацию названий по оси X
    ax_top.set_xticklabels(ax_top.get_xticklabels(), rotation=0, ha='center')

    # Подготовка данных для тепловых карт:
    # Ставим модель в индекс и берем только нужные метрики
    df_ethical.set_index("model", inplace=True)
    df_logical.set_index("model", inplace=True)
    df_sycophancy.set_index("model", inplace=True)

    df_ethical = df_ethical[["accuracy", "precision", "recall", "f1"]]
    df_logical = df_logical[["accuracy", "precision", "recall", "f1"]]
    df_sycophancy = df_sycophancy[["accuracy", "precision", "recall", "f1"]]

    # 2) Тепловая карта для ethical_scores.csv (row 1, col 0)
    ax_ethical = fig.add_subplot(gs[1, 0])
    sns.heatmap(
        df_ethical,
        ax=ax_ethical,
        annot=True,
        fmt=".3f",
        cmap="Blues",
        cbar=True
    )
    ax_ethical.set_title("Ethical Compliance Test Results")

    # 3) Тепловая карта для logical_scores.csv (row 1, col 1)
    ax_logical = fig.add_subplot(gs[1, 1])
    sns.heatmap(
        df_logical,
        ax=ax_logical,
        annot=True,
        fmt=".3f",
        cmap="Greens",
        cbar=True
    )
    ax_logical.set_title("Logical Inconsistencies Test Results")

    # 4) Тепловая карта для sycophancy_scores.csv (row 1, col 2)
    ax_sycophancy = fig.add_subplot(gs[1, 2])
    sns.heatmap(
        df_sycophancy,
        ax=ax_sycophancy,
        annot=True,
        fmt=".3f",
        cmap="Oranges",
        cbar=True
    )
    ax_sycophancy.set_title("Sycophancy Test Results")

    # Применяем общий стиль и расположение
    sns.set_theme(style="whitegrid")
    plt.tight_layout()

    return fig


# Создаём веб-интерфейс с Gradio
demo = gr.Interface(
    fn=create_plots,
    inputs=[],
    outputs="plot",
    title="Результаты Бенчмарка LLM vs LLM",
    description=(
        "Исследование способностей языковых моделей к генерации вредоносных запросов и оцениванию других языковых моделей"
    )
)

if __name__ == "__main__":
    demo.launch()
