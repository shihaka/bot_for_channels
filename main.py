import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from aiohttp import web

from channels import CHANNELS

# --- Тише логов ---
logging.getLogger("aiogram").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.basicConfig(level=logging.WARNING)

GREETING = (
    "Привет! 👋 Меня зовут Кирилл! Рад познакомиться!\n"
    "Здесь ты найдёшь несколько моих каналов с инструментами и решениями\n"
    "✅ Готовые шаблоны Excel / Google Sheets\n"
    "✅ Инструкции по созданию Telegram-ботов\n"
    "✅ Лайфхаки по 3D-моделированию\n"
    "✅ Полезные инструменты и мысли для продуктивности\n"
    "Нужна помощь? → Пиши мне в ЛС: @shihaleevka — сделаю под твою задачу.\n\n"
    "Выбери раздел ниже 👇 \n"

)

router = Router()

def build_channels_keyboard():
    kb = InlineKeyboardBuilder()
    for name, url in CHANNELS:
        kb.add(InlineKeyboardButton(text=name, url=url))
    # по 2 кнопки в ряд (можете изменить на 1, 3, 4 и т.д.)
    kb.adjust(2)
    return kb.as_markup()

@router.message(CommandStart())
async def on_start(message: Message):
    await message.answer(GREETING, reply_markup=build_channels_keyboard())

# --- aiohttp health-check для UptimeRobot / Replit unsleep ---
async def health(_request):
    return web.Response(text="healthy")

async def index(_request):
    return web.Response(text="OK")

async def start_health_server():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/health", health)

    port = int(os.environ.get("PORT", "8080"))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()

async def main():
    token = os.environ.get("TELEGRAM_API")
    if not token:
        raise RuntimeError("Переменная окружения TELEGRAM_API не задана.")

    # health-сервер запускаем в фоне
    await start_health_server()

    print("Бот запущен...")  # как вы просили

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    # Long polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
