import asyncio
import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

from logger import log
from db import WeatherRecord, DBSession
from websocket import manager
from nats_client import publish_nats
from config import DEFAULT_CITY, PARSER_INTERVAL

class WeatherParser:
    def __init__(self, city_slug: str):
        self.city_slug = city_slug
        self.city_name = city_slug.capitalize()
        self.url = f"https://pogoda.mail.ru/prognoz/{city_slug}/extended/"
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def get_weather(self):
        response = requests.get(self.url, headers=self.headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        weather_data = []
        date_elements = soup.find_all('span', class_='hdr__inner')

        for i, date_elem in enumerate(date_elements):
            date_text = date_elem.get_text(strip=True)
            if i == 0 and date_text.startswith("Сегодня - "):
                date_text = date_text.replace("Сегодня - ", "")

            date_div = date_elem.find_parent('div', class_='hdr')
            weather_block = date_div.find_next_sibling('div', class_='p-flex')
            if not weather_block:
                continue

            for block in weather_block.find_all('div', class_='p-flex__column_percent-16'):
                time_of_day = block.find('span', class_='text_bold_normal')
                temperature = block.find('span', class_='text_bold_medium')
                condition = block.find('span', class_='text_light_normal', title=True)

                if time_of_day and temperature:
                    weather_data.append({
                        "date": date_text,
                        "time_of_day": time_of_day.get_text(strip=True),
                        "temperature": temperature.get_text(strip=True),
                        "condition": condition.get_text(strip=True) if condition else "",
                        "city": self.city_name
                    })

        log("parser", f"Спаршено {len(weather_data)} записей для {self.city_name}")
        return weather_data


async def background_weather_parser(db, city_slug=DEFAULT_CITY):
    city_name = city_slug.capitalize()
    log("parser", f"Парсинг погоды для {city_name}")

    parser = WeatherParser(city_slug)
    weather_data = parser.get_weather()

    saved, updated = 0, 0

    for item in weather_data:
        stmt = select(WeatherRecord).where(
            WeatherRecord.date == item["date"],
            WeatherRecord.time_of_day == item["time_of_day"],
            WeatherRecord.city == item["city"]
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            if existing.temperature != item["temperature"] or existing.condition != item["condition"]:
                existing.temperature = item["temperature"]
                existing.condition = item["condition"]
                updated += 1
        else:
            db.add(WeatherRecord(**item))
            saved += 1

    await db.commit()
    log("parser", f"{city_name}: добавлено {saved}, обновлено {updated}")

    await publish_nats("parser", {
        "city": city_name,
        "saved": saved,
        "updated": updated
    })

    await manager.broadcast_json({
        "type": "parser_result",
        "city": city_name,
        "saved": saved,
        "updated": updated
    })


async def start_background_tasks():
    while True:
        await asyncio.sleep(PARSER_INTERVAL)
        db = DBSession()
        try:
            await background_weather_parser(db)
        finally:
            await db.close()
