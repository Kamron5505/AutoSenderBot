"""
StarPayUz — авто-рассыльщик рекламы в Telegram группы с премиум эмодзи.

Запускает бесконечный цикл: отправляет сообщение во все чаты из CHATS_LIST,
затем ждёт INTERVAL секунд и повторяет.
"""

import asyncio
import logging
import sys
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings
from sender import send_messages

# ─── Настройка логирования ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("sender.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def cleanup_session_files():
    """Удаляет файлы сессии, которые могли остаться заблокированными."""
    session_name = settings.session_name
    patterns = [
        f"{session_name}.session",
        f"{session_name}.session-journal",
        f"{session_name}.session-wal",
        f"{session_name}.session-shm",
    ]
    removed = []
    for pattern in patterns:
        path = Path(pattern)
        if path.exists():
            try:
                path.unlink()
                removed.append(pattern)
            except Exception:
                pass
    return removed


async def main_loop():
    """Бесконечный цикл: подключение → рассылка → ожидание → повтор."""
    log.info("⭐️ StarPayUz Auto-Sender запущен!")
    log.info(f"📋 Чатов в списке: {len(settings.chats_list)}")
    log.info(f"⏱ Интервал между циклами: {settings.interval // 60} мин.")
    log.info(f"⏳ Задержка между сообщениями: {settings.delay_min}-{settings.delay_max} сек.")
    log.info("=" * 50)

    while True:
        if settings.string_session:
            client = TelegramClient(
                StringSession(settings.string_session),
                settings.api_id,
                settings.api_hash
            )
        else:
            client = TelegramClient(
                settings.session_name,
                settings.api_id,
                settings.api_hash
            )

        try:
            await client.connect()

            # Проверка авторизации
            if not await client.is_user_authorized():
                log.error("❌ Сессия не найдена!")
                log.error("ℹ️  Запусти скрипт локально для создания сессии:")
                log.error(f"   python auth.py")
                log.error("   Или удали файл сессии и запусти заново.")
                raise Exception("Session not authorized")

            me = await client.get_me()
            log.info(f"✅ Подключено: {me.first_name} (@{me.username or 'нет username'})")

            # Рассылка
            stats = await send_messages(client)

            # Ожидание до следующего цикла
            log.info(f"⏳ Ждём {settings.interval // 60} мин. {settings.interval % 60} сек. до следующей рассылки...")
            await asyncio.sleep(settings.interval)

        except KeyboardInterrupt:
            log.info("👋 Рассыльщик остановлен пользователем.")
            break
        except Exception as e:
            log.error(f"❌ Критическая ошибка: {e}")
            log.info("🔄 Перезапуск через 30 секунд...")
            await asyncio.sleep(30)
        finally:
            try:
                await client.disconnect()
            except Exception:
                pass


async def auth():
    """Создание новой сессии (однократный запуск)."""
    client = TelegramClient(
        settings.session_name,
        settings.api_id,
        settings.api_hash
    )

    try:
        await client.start(phone=settings.phone)
        me = await client.get_me()
        log.info(f"✅ Авторизация успешна! Аккаунт: {me.first_name}")
        log.info(f"📁 Файл сессии сохранён: {settings.session_name}.session")
        log.info("🚀 Теперь запускай: python main.py")
    except Exception as e:
        log.error(f"❌ Ошибка авторизации: {e}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auth":
        # Режим авторизации: python main.py --auth
        asyncio.run(auth())
    else:
        # Основной режим: python main.py
        try:
            asyncio.run(main_loop())
        except KeyboardInterrupt:
            log.info("👋 До свидания!")
        except Exception as e:
            log.error(f"❌ Фатальная ошибка: {e}")

            error_msg = str(e).lower()
            if "database is locked" in error_msg:
                print("\n🔧 Обнаружена ошибка 'database is locked'")
                removed = cleanup_session_files()
                if removed:
                    print(f"   🧹 Удалены: {', '.join(removed)}")
                    print("   ✅ Запусти снова: python main.py")
                else:
                    print("   ⚠️  Файлы сессии не найдены. Перезапусти терминал.")
            sys.exit(1)
