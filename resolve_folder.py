"""
Скрипт для извлечения чатов из папки Telegram (Folder/Filter).
Использует API для получения dialog filters и разрешения peer ID в username.
"""
import asyncio
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()


async def main():
    ss = os.getenv('STRING_SESSION')
    if not ss:
        print("STRING_SESSION not found in .env")
        return

    client = TelegramClient(
        StringSession(ss),
        int(os.getenv('API_ID', '0')),
        os.getenv('API_HASH', '')
    )
    await client.connect()

    if not await client.is_user_authorized():
        print("Not authorized")
        await client.disconnect()
        return

    me = await client.get_me()
    print(f"Connected: {me.first_name}")

    # Получаем dialog filters (папки)
    from telethon.tl.functions.messages import GetDialogFiltersRequest
    result = await client(GetDialogFiltersRequest())
    filters = result.filters

    print(f"\nAvailable folders: {len(filters)}")
    for f in filters:
        if hasattr(f, 'title') and hasattr(f, 'include_peers'):
            title = f.title
            count = len(f.include_peers) if f.include_peers else 0
            print(f"  - '{title}' -> {count} chats")

    # Ищем папку "Forum" (или любую с ~72 чатами)
    target_filter = None
    for f in filters:
        if hasattr(f, 'title') and hasattr(f, 'include_peers'):
            title = f.title
            count = len(f.include_peers) if f.include_peers else 0
            # Берём папку с最大的 чатами (это Forum с 90)
            if count > 50:
                target_filter = f
                print(f"\nUsing folder: '{title}' ({count} chats)")
                break

    if not target_filter:
        # Если нет подходящей папки, берём все dialogs
        print("\nNo suitable folder found. Exporting all dialogs...")
        dialogs = await client.get_dialogs(limit=None)
        usernames = []
        for d in dialogs:
            if d.entity and hasattr(d.entity, 'username') and d.entity.username:
                uname = d.entity.username
                if not uname.startswith('username_'):
                    usernames.append(f"@{uname}")
        
        usernames.sort()
        with open("chats.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(usernames))
        print(f"\nSaved {len(usernames)} chats to chats.txt")
        await client.disconnect()
        return

    # Разрешаем peer ID в username
    usernames = []
    peers = target_filter.include_peers

    print(f"\nResolving {len(peers)} peers to usernames...")
    for i, peer in enumerate(peers):
        try:
            entity = await client.get_entity(peer)
            if hasattr(entity, 'username') and entity.username:
                uname = f"@{entity.username}"
                usernames.append(uname)
                print(f"  [{i+1}/{len(peers)}] {uname} ({entity.title if hasattr(entity, 'title') else entity.first_name})")
            else:
                # Peer без username — пропускаем
                name = entity.title if hasattr(entity, 'title') else entity.first_name
                print(f"  [{i+1}/{len(peers)}] SKIP (no username): {name}")
        except Exception as e:
            print(f"  [{i+1}/{len(peers)}] ERROR: {e}")

    # Сортируем и сохраняем
    usernames.sort()
    with open("chats.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(usernames))

    print(f"\n{'='*50}")
    print(f"Saved {len(usernames)} chats to chats.txt")
    print(f"{'='*50}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
