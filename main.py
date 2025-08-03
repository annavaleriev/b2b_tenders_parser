import argparse
from tender_parser import fetch_all_cards
from storage import save_to_csv, save_to_excel


def main():
    parser = argparse.ArgumentParser(
        description="Сбор тендеров с b2b-center.ru"
    )
    parser.add_argument(
        "--max",
        type=int,
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

    tenders = fetch_all_cards(max_cards=args.max)
    if not tenders:
        return

    save_to_csv(tenders, filename=args.output)
    save_to_excel(tenders, filename=args.output.replace(".csv", ".xlsx"))


if __name__ == "__main__":
    main()
