import re
import csv
import pandas as pd
from pathlib import Path


def clean_description(text: str) -> str:
    """Удаляет строки с лишней информацией из описания"""
    excluded = r"Заводской номер|Год выпуска|Покупатель"
    return " ".join(
        line.strip()
        for line in text.splitlines()
        if not re.search(excluded, line, re.IGNORECASE)
    )


def save_to_csv(tenders: list[dict], filename: str = "tenders.csv") -> None:
    """Сохраняет список тендеров в CSV"""
    if not tenders:
        return

    with Path(filename).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=tenders[0].keys(), quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(tenders)


def save_to_excel(tenders: list[dict], filename: str = "tenders.xlsx") -> None:
    """Сохраняет список тендеров в Excel"""
    if not tenders:
        return

    pd.DataFrame(tenders).to_excel(filename, index=False)
