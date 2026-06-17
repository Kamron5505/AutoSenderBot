import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

from config import settings


class TelegramClientWrapper:
    """Обёртка над Telethon клиентом для удобной авторизации."""

    def __init__(self):
        self.client = TelegramClient(
            session=settings.session_name,
            api_id=settings.api_id,
            api_hash=settings.api_hash
        )

    async def start(self) -> TelegramClient:
        """Запускает клиент и выполняет авторизацию."""
        await self.client.start(
            phone=settings.phone,
            code_callback=self._get_code,
            password_callback=self._get_password
        )
        print(f"\n✅ Успешная авторизация! Аккаунт: {(await self.client.get_me()).first_name}")
        return self.client

    async def _get_code(self) -> str:
        """Запрашивает код подтверждения у пользователя."""
        print("\n📱 Код подтверждения отправлен в Telegram!")
        return input("🔑 Введи код из Telegram: ").strip()

    async def _get_password(self) -> str:
        """Запрашивает пароль двухфакторной аутентификации."""
        print("\n🔐 Требуется облачный пароль (2FA)!")
        return input("🔑 Введи пароль: ").strip()

    async def stop(self):
        """Останавливает клиент."""
        await self.client.disconnect()
        print("👋 Сессия завершена.")

    async def get_dialogs(self):
        """Получает список диалогов."""
        return await self.client.get_dialogs()
