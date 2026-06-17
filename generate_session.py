"""
Скрипт для генерации String Session.
Запусти локально один раз, скопируй полученную строку
и добавь в переменные окружения Railway как STRING_SESSION.
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from config import settings

print("🔑 Генерация String Session для Railway...")
print(f"📱 Аккаунт: {settings.phone}")
print()

with TelegramClient(StringSession(), settings.api_id, settings.api_hash) as client:
    client.start(phone=settings.phone)
    print(f"\n✅ Авторизация успешна! Аккаунт: {client.get_me().first_name}")
    print("\n" + "=" * 60)
    print("📋 СКОПИРУЙ ЭТУ СТРОКУ:")
    print("=" * 60)
    print(client.session.save())
    print("=" * 60)
    print("\n📌 Добавь её в Railway → Variables → STRING_SESSION")
    print("📌 И перезапусти проект!")
