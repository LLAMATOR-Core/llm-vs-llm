import gradio as gr
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, create_engine, select
from sqlalchemy.orm import Session, declarative_base, relationship
import matplotlib.pyplot as plt


engine = create_engine('sqlite:///data/llm-vs-llm.db')
Base = declarative_base()


class Judge(Base):
    __tablename__ = 'judge'

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    size = Column(Integer)

    verdicts = relationship("Verdict", back_populates="judge")


class Attack(Base):
    __tablename__ = 'attack'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    dialogs = relationship("Dialog", back_populates="attack")


class Dialog(Base):
    __tablename__ = 'dialog'

    id = Column(Integer, primary_key=True)
    attack_id = Column(Integer, ForeignKey('attack.id'))
    first_attack_prompt = Column(Text)
    first_response = Column(Text)
    second_attack_prompt = Column(Text, nullable=True)
    second_response = Column(Text, nullable=True)

    attack = relationship("Attack", back_populates="dialogs")
    verdicts = relationship("Verdict", back_populates="dialog")


class Verdict(Base):
    __tablename__ = 'verdict'

    dialog_id = Column(Integer, ForeignKey('dialog.id'), primary_key=True)
    judge_id = Column(Integer, ForeignKey('judge.id'), primary_key=True)
    verdict = Column(Boolean)

    dialog = relationship("Dialog", back_populates="verdicts")
    judge = relationship("Judge", back_populates="verdicts")


def get_verdict_counts_attacks_metrics():
    attacks_metrics = {}
    verdict_counts = []

    with Session(engine) as session:
        attacks = session.scalars(select(Attack)).all()
        for attack in attacks:
            attack_title = attack.title.replace("_", " ")
            dialogs = {}
            for dialog in attack.dialogs:
                dialogs[dialog.id] = {}
                for verdict in dialog.verdicts:
                    dialogs[dialog.id][verdict.judge.title] = verdict.verdict
            df = pd.DataFrame(dialogs.values())

            verdicts = pd.DataFrame(df["HUMAN_BENCHMARK"].value_counts()).reset_index()
            verdicts["HUMAN_BENCHMARK"] = verdicts["HUMAN_BENCHMARK"].apply(lambda x: "RESILIENT" if x else "BROKEN")
            verdicts["attack"] = attack_title
            verdict_counts.append(verdicts)

            scores = []
            for judge in df.columns[1:]:
                p, r, f1, s = precision_recall_fscore_support(df["HUMAN_BENCHMARK"], df[judge], average='weighted', zero_division=0)
                scores.append({
                    "model": judge,
                    "accuracy": accuracy_score(df["HUMAN_BENCHMARK"], df[judge]),
                    "precision": p,
                    "recall": r,
                    "f1": f1,
                })
            attacks_metrics[attack_title] = pd.DataFrame(scores).sort_values("f1", ascending=False)

    return pd.concat(verdict_counts), attacks_metrics


def create_plots():
    """
    Возвращает фигуру (Figure), в которой расположено 4 графика:
    1) Верхний ряд: verdict_counts (сгруппированные столбцы для verdict=BROKEN/RESILIENT по каждой атаке)
    2) Нижний ряд: тепловые карты метрик качества судейства по каждой атаке
    """

    # Загружаем данные
    verdict_counts, attacks_metrics = get_verdict_counts_attacks_metrics()

    # Настраиваем сетку фигуры: 2 строки, 3 столбца
    fig = plt.figure(figsize=(24, 12))
    gs = fig.add_gridspec(2, 3, height_ratios=[62, 38])

    # Подготовка данных для тепловых карт
    colors = ["Blues", "Greens", "Oranges"]
    index = 0
    for attack, df in attacks_metrics.items():
        df.set_index("model", inplace=True)
        ax = fig.add_subplot(gs[0, index])
        sns.heatmap(
            df[["accuracy", "precision", "recall", "f1"]],
            ax=ax,
            annot=True,
            fmt=".3f",
            cmap=colors[index],
            cbar=True
        )
        ax.set_title(f"{attack} results", fontsize=16)
        index += 1

    ax_counts = fig.add_subplot(gs[1, :])
    # Сгруппируем данные так, чтобы атаки шли по оси X, а столбцы отражали вердикт RESILIENT/BROKEN
    pivot_attacks = verdict_counts.pivot(index="attack", columns="HUMAN_BENCHMARK", values="count")
    # Заполним возможные пропуски нулями, если вдруг такие есть
    pivot_attacks.fillna(0, inplace=True)
    # Построим сгруппированные столбцы
    pivot_attacks.plot(
        kind="bar",
        ax=ax_counts,
        stacked=False,
        width=0.7,
        cmap="Set2"
    )
    ax_counts.set_title("Вердикты человека по атакам", fontsize=16)
    ax_counts.set_ylabel("Количество")
    ax_counts.legend(title="Вердикт", loc="best")
    ax_counts.grid(True, axis='y')
    # Устанавливаем горизонтальную ориентацию названий по оси X
    ax_counts.set_xticklabels(ax_counts.get_xticklabels(), rotation=0, ha='center')

    # Применяем общий стиль и расположение
    sns.set_theme(style="whitegrid", font_scale=3)
    plt.tight_layout()

    return fig


# Создаём веб-интерфейс с Gradio
demo = gr.Interface(
    fn=create_plots,
    inputs=[],
    outputs="plot",
    title="Результаты бенчмарка моделей-судей LLM vs LLM",
    description=(
        "Исследование способностей языковых моделей к генерации вредоносных запросов и оцениванию других языковых моделей. "
        "Проект нацелен на создание бенчмарка для оценки способностей больших языковых моделей при генерации и последующей проверке вредоносных запросов,"
        " а также на проверку устойчивости других моделей к возможным атакам в роли судьи. [Репозиторий проекта на GitHub](https://github.com/nizamovtimur/llm-vs-llm)"
    ),
    flagging_mode='never',
    live=True,
    stream_every=30.0,
)

if __name__ == "__main__":
    demo.launch()
