import json
import logging
from datetime import datetime, timezone
from fastapi.encoders import jsonable_encoder
from nats.aio.client import Client as NATS

from logger import log
from config import NATS_URL, NATS_SUBJECT

nats = NATS()
NATS_ENABLED = False

# 1. Настраиваем логгер для библиотеки NATS
nats_logger = logging.getLogger('nats.aio.client')
nats_logger.setLevel(logging.CRITICAL)  # Подавляем все сообщения, кроме критических

async def connect_nats(handler):
    global NATS_ENABLED
    try:
        # 2. Подключаемся с таймаутом, чтобы не ждать вечно
        await nats.connect(
            NATS_URL,
            connect_timeout=2,  # Быстрый отказ при подключении
            reconnect_time_wait=1,  # Быстрые попытки реконнекта
            max_reconnect_attempts=3  # Всего 3 попытки
        )
        await nats.subscribe(NATS_SUBJECT, cb=handler)
        NATS_ENABLED = True
        log("nats", "Подключен и подписка активна")
    except Exception as e:
        NATS_ENABLED = False
        log("error", f"NATS недоступен ({e}). Интеграция отключена.")

async def publish_nats(event: str, item: dict):
    if not NATS_ENABLED:
        return

    payload = {
        "event": event,
        "item": jsonable_encoder(item),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    try:
        await nats.publish(NATS_SUBJECT, json.dumps(payload).encode())
        await nats.flush()
        log("nats", f"Опубликовано событие: {event}")
    except Exception as e:
        log("error", f"NATS publish error: {e}")