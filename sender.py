"""
Модуль отправки сообщений в Telegram чаты с поддержкой премиум эмодзи.
"""

import asyncio
import random
import logging
from datetime import datetime

from telethon import TelegramClient
from telethon.errors import FloodWaitError, UserBannedInChannelError, ChatWriteForbiddenError
from telethon.tl import functions
from telethon.tl.types import (
    ReplyInlineMarkup, KeyboardButtonRow, KeyboardButtonUrl
)

from config import settings
from formatter import parse_message

log = logging.getLogger(__name__)


class SenderStats:
    """Статистика рассылки."""

    def __init__(self):
        self.success = 0
        self.failed = 0
        self.start_time: datetime | None = None

    def start(self):
        self.start_time = datetime.now()

    @property
    def elapsed(self) -> str:
        if not self.start_time:
            return "0:00"
        delta = datetime.now() - self.start_time
        minutes = delta.seconds // 60
        seconds = delta.seconds % 60
        return f"{minutes}:{seconds:02d}"

    def __str__(self) -> str:
        return f"✅ {self.success} успешно, ❌ {self.failed} ошибок ⏱ {self.elapsed}"


async def send_messages(client: TelegramClient) -> SenderStats:
    """
    Отправляет сообщение во все чаты из settings.CHATS_LIST.
    Использует форматирование через HTML-теги и премиум эмодзи.

    Returns:
        SenderStats со статистикой отправки
    """
    raw_message = settings.ad_message
    plain_text, entities = parse_message(raw_message)
    stats = SenderStats()
    stats.start()

    # Создаём кнопку "Stars Olish" один раз перед циклом
    markup = ReplyInlineMarkup(
        rows=[KeyboardButtonRow(
            buttons=[KeyboardButtonUrl(
                text="🌟 Stars Olish",
                url="https://t.me/starpayuzuauto_bot"
            )]
        )]
    )

    log.info("=" * 40)
    log.info("🚀 НАЧАЛО РАССЫЛКИ")
    log.info("=" * 40)

    for i, chat in enumerate(settings.chats_list, 1):
        # Проверка подключения
        if not client.is_connected():
            log.warning("⚠️ Соединение разорвано, переподключаемся...")
            await client.connect()

        try:
            peer = await client.get_input_entity(chat)

            # Отправляем сообщение с форматированием, без web-превью и с кнопкой
            await client(functions.messages.SendMessageRequest(
                peer=peer,
                message=plain_text,
                entities=entities,
                no_webpage=True,
                reply_markup=markup,
            ))

            log.info(f"[{i}/{len(settings.chats_list)}] ✅ {chat}")
            stats.success += 1

        except FloodWaitError as e:
            wait_seconds = e.seconds
            log.warning(f"[{i}/{len(settings.chats_list)}] ⏳ FloodWait {chat} — ждём {wait_seconds} сек.")
            if wait_seconds < 3600:  # Ждём только если меньше часа
                await asyncio.sleep(wait_seconds)
            else:
                log.error(f"❌ Слишком долгий FloodWait ({wait_seconds} сек), пропускаем {chat}")
                stats.failed += 1

        except (UserBannedInChannelError, ChatWriteForbiddenError) as e:
            log.error(f"[{i}/{len(settings.chats_list)}] 🚫 Нет доступа: {chat} — {e}")
            stats.failed += 1

        except Exception as e:
            log.error(f"[{i}/{len(settings.chats_list)}] ❌ {chat} — {e}")
            stats.failed += 1

        # Задержка между сообщениями
        if i < len(settings.chats_list):
            delay = random.randint(settings.delay_min, settings.delay_max)
            log.info(f"⏳ Пауза {delay} сек...")
            await asyncio.sleep(delay)

    log.info("=" * 40)
    log.info(f"🏁 РАССЫЛКА ЗАВЕРШЕНА: {stats}")
    log.info("=" * 40)

    return stats
