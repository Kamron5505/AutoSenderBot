from telethon import TelegramClient
from telethon.tl.types import Channel


class ForumGroupInfo:
    """Информация о найденной Forum Group."""

    def __init__(self, chat_id: int, title: str, username: str | None, topics: list[tuple[int, str]]):
        self.chat_id = chat_id
        self.title = title
        self.username = username
        self.topics = topics  # [(topic_id, topic_title), ...]

    def __str__(self) -> str:
        uname = f"@{self.username}" if self.username else "нет username"
        return f"📢 {self.title} ({uname}) — {len(self.topics)} тем"



async def search_forum_groups(client: TelegramClient, search_query: str = "") -> list[ForumGroupInfo]:
    """
    Ищет Forum Groups среди диалогов пользователя.
    Если указан search_query, фильтрует по названию.
    """
    forum_groups: list[ForumGroupInfo] = []

    query_text = f' по запросу "{search_query}"' if search_query else "..."
    print(f"\n🔍 Поиск Forum Groups{query_text}")

    async for dialog in client.iter_dialogs():
        # Пропускаем, если это не группа/канал
        if not isinstance(dialog.entity, Channel):
            continue

        entity = dialog.entity

        # Проверяем, что это форум (группа с темами)
        if not getattr(entity, 'forum', False):
            continue

        # Фильтр по поисковому запросу
        if search_query and search_query.lower() not in dialog.name.lower():
            continue

        # Получаем темы (topics) форума
        topics = await _get_forum_topics(client, dialog.id)
        if not topics:
            continue

        forum_groups.append(
            ForumGroupInfo(
                chat_id=dialog.id,
                title=dialog.name,
                username=entity.username,
                topics=topics
            )
        )

        print(f"  ✅ Найдена: {dialog.name} — {len(topics)} тем")

    return forum_groups


async def _get_forum_topics(client: TelegramClient, chat_id: int) -> list[tuple[int, str]]:
    """Получает список тем (topics) Forum Group."""
    topics: list[tuple[int, str]] = []
    try:
        async for topic in client.iter_forum_topics(chat_id):
            topics.append((topic.id, topic.title))
    except Exception as e:
        print(f"  ⚠️ Не удалось получить темы для чата {chat_id}: {e}")

    return topics

