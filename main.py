import argparse

from storage import save_tenders_to_csv, save_tenders_to_excel
from tender_parser import fetch_tenders


def main():
    parser = argparse.ArgumentParser(
        description="Сбор тендеров с b2b-center.ru"
    )
    parser.add_argument(
        "--max",
        type=lambda x: int(x) if int(x) > 0 else parser.error(" --max должно быть больше 0"),
        required=True,
        help="Сколько тендеров собрать"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="tenders.csv",
        help="Имя CSV-файла (по умолчанию tenders.csv)"
    )

    args = parser.parse_args()

    tenders = fetch_tenders(max_tenders=args.max)
    if not tenders:
        print("Нет данных для сохранения.")
        return

    save_tenders_to_csv(tenders, filename=args.output)
    save_tenders_to_excel(tenders, filename=args.output.replace(".csv", ".xlsx"))


if __name__ == "__main__":
    main()
