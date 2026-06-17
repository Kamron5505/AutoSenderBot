import os
from pathlib import Path
from dotenv import load_dotenv


class Settings:
    """Загрузка конфигурации из .env файла."""

    def __init__(self, env_path: str | None = None):
        if env_path is None:
            env_path = Path(__file__).parent.parent / ".env"

        load_dotenv(env_path)

        # Telegram API credentials
        self.api_id: int = int(os.getenv("API_ID", "0"))
        self.api_hash: str = os.getenv("API_HASH", "")

        # Номер телефона для авторизации
        self.phone: str = os.getenv("PHONE", "")
        self.session_name: str = os.getenv("SESSION_NAME", "railway_session")

        # String Session для Railway (вместо файла)
        self.string_session: str | None = os.getenv("STRING_SESSION") or None

        # Интервал между полными циклами рассылки (в секундах)
        self.interval: int = int(os.getenv("INTERVAL", "300"))

        # Задержка между отправками в один чат (мин/макс, секунды)
        self.delay_min: int = int(os.getenv("DELAY_MIN", "5"))
        self.delay_max: int = int(os.getenv("DELAY_MAX", "15"))

        # Список чатов (из файла chats.txt, одна группа на строку)
        self.chats_list: list[str] = self._load_chats(env_path)

        # Текст рекламного сообщения с HTML-тегами (из файла message.txt)
        self.ad_message: str = self._load_message(env_path)

    def validate(self) -> list[str]:
        """Проверяет, все ли необходимые настройки заполнены."""
        errors = []
        if not self.api_id or self.api_id == 0:
            errors.append("API_ID не указан. Получи его на https://my.telegram.org")
        if not self.api_hash:
            errors.append("API_HASH не указан. Получи его на https://my.telegram.org")
        if not self.phone:
            errors.append("PHONE не указан. Укажи номер телефона в формате +998971051000")
        if not self.chats_list:
            errors.append("chats.txt пуст. Укажи хотя бы один чат в файле chats.txt (по одному на строку)")
        if not self.ad_message:
            errors.append("AD_MESSAGE пуст. Проверь файл message.txt")
        return errors

    def _load_chats(self, env_path: str) -> list[str]:
        """Загружает список чатов из chats.txt (одна группа на строку)."""
        chats_file = Path(env_path).parent / "chats.txt"
        if chats_file.exists():
            try:
                lines = chats_file.read_text(encoding="utf-8").strip().split("\n")
                return [line.strip() for line in lines if line.strip()]
            except Exception:
                pass
        # Fallback
        return ["@forum_nft_uzbekistan", "@gift_kurs"]

    def _load_message(self, env_path: str) -> str:
        """Загружает сообщение из message.txt."""
        msg_file = Path(env_path).parent / "message.txt"
        if msg_file.exists():
            try:
                return msg_file.read_text(encoding="utf-8").strip()
            except Exception:
                pass
        # Fallback: пробуем из AD_MESSAGE в .env
        msg = os.getenv("AD_MESSAGE", "")
        return msg or "⚡️ StarPayUz ⭐️"
