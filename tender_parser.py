import os
import time
import html
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from storage import clean_description

load_dotenv()

BASE_LIST_URL = os.getenv("BASE_LIST_URL")
BASE_DOMAIN = os.getenv("BASE_DOMAIN")
HEADERS = {"User-Agent": os.getenv("USER_AGENT")}


def parse_card_details(card_url: str) -> dict | None:
    """Парсит детали карточки тендера"""
    try:
        response = requests.get(card_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        title = html.unescape(
            soup.select_one("h1.h3").contents[0].strip()
        ) if soup.select_one("h1.h3") and soup.select_one("h1.h3").contents else ""

        raw_desc = soup.select_one("div.s2")
        description = clean_description(raw_desc.get_text("\n", strip=True)) if raw_desc else ""

        published = soup.select_one("tr#trade_info_date_begin span[itemprop='datePublished']")
        deadline = soup.select_one("tr#trade_info_date_end td:last-child")

        organizer = soup.select_one("tr#trade-info-organizer-name td a")
        customer = soup.select_one("tr#trade-info-organizer-name + tr td a")

        return {
            "Номер тендера": title,
            "Описание": description,
            "Дата публикации": published.get("content", "") if published else "",
            "Срок подачи": deadline.get_text(strip=True) if deadline else "",
            "Организатор": organizer.get_text(strip=True) if organizer else "",
            "Заказчик": customer.get_text(strip=True) if customer else "",
            "Ссылка": card_url,
        }

    except (AttributeError, IndexError) as e:
        print(f"Ошибка парсинга данных: {e} — {card_url}")
        return None


def fetch_all_cards(max_cards: int = 5) -> list[dict]:
    """Собирает список тендеров"""
    tenders = []
    page = 1

    while len(tenders) < max_cards:
        resp = requests.get(BASE_LIST_URL.format(page), headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        cards = soup.select("a.search-results-title")
        if not cards:
            break

        for a_tag in cards:
            if len(tenders) >= max_cards:
                break
            card_url = BASE_DOMAIN + a_tag.get("href", "")
            tender = parse_card_details(card_url)
            if tender:
                tenders.append(tender)
            time.sleep(0.5)

        page += 1

    return tenders
