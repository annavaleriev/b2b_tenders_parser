import os
import time
import html
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from storage import clean_tender_description

load_dotenv()

BASE_LIST_URL = os.getenv("BASE_LIST_URL")
BASE_DOMAIN = os.getenv("BASE_DOMAIN")
HEADERS = {"User-Agent": os.getenv("USER_AGENT")}


def parse_tender_details(tender_url: str) -> dict | None:
    """Парсит детали карточки тендера"""
    try:
        response = requests.get(tender_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        tender_title = html.unescape(
            soup.select_one("h1.h3").contents[0].strip()
        ) if soup.select_one("h1.h3") and soup.select_one("h1.h3").contents else ""

        description_block = soup.select_one("div.s2")
        description = clean_tender_description(
            description_block.get_text("\n", strip=True)) if description_block else ""

        published_date = soup.select_one("tr#trade_info_date_begin span[itemprop='datePublished']")
        deadline_date = soup.select_one("tr#trade_info_date_end td:last-child")

        organizer_name = soup.select_one("tr#trade-info-organizer-name td a")
        customer_name = soup.select_one("tr#trade-info-organizer-name + tr td a")

        return {
            "Номер тендера": tender_title,
            "Описание": description,
            "Дата публикации": published_date.get("content", "") if published_date else "",
            "Срок подачи": deadline_date.get_text(strip=True) if deadline_date else "",
            "Организатор": organizer_name.get_text(strip=True) if organizer_name else "",
            "Заказчик": customer_name.get_text(strip=True) if customer_name else "",
            "Ссылка": tender_url,
        }

    except (AttributeError, IndexError) as e:
        print(f"Ошибка парсинга данных: {e} — {tender_url}")
        return None


def fetch_tenders(max_tenders: int = 5) -> list[dict]:
    """Собирает список тендеров"""
    tenders = []
    page = 1

    while len(tenders) < max_tenders:
        response = requests.get(BASE_LIST_URL.format(page), headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        tender_links = soup.select("a.search-results-title")
        if not tender_links:
            break

        for tender_link in tender_links:
            if len(tenders) >= max_tenders:
                break
            tender_url = BASE_DOMAIN + tender_link.get("href", "")
            tender_data = parse_tender_details(tender_url)
            if tender_data:
                tenders.append(tender_data)
            time.sleep(0.5)

        page += 1

    return tenders
