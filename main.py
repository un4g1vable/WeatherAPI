import time
import asyncio
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from logger import log
from db import engine, SQLModel
from websocket import manager
from nats_client import connect_nats
from services import start_background_tasks
from api import router
import json

app = FastAPI(
    title="Weather Monitoring API",
    version="1.0",
    description="Weather Monitoring API — сервис для сбора, хранения и мониторинга погодных данных."
)

@app.on_event("startup")
async def startup():
    log("system", "Запуск Weather Monitoring API")

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async def nats_handler(msg):
        data = json.loads(msg.data.decode())
        log("nats", f"Получено событие: {data.get('event')}")
        await manager.broadcast_json({
            "type": "nats_event",
            **data
        })

    await connect_nats(nats_handler)

    asyncio.create_task(start_background_tasks())
    log("system", "Фоновая задача запущена")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    log("http", f"{request.method} {request.url.path} {response.status_code} ({time.time() - start_time:.3f}s)")
    return response

app.include_router(router)

@app.websocket("/ws/weather")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
