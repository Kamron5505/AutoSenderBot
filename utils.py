import os
import sys
from pathlib import Path


def clear_screen():
    """Очищает экран терминала."""
    os.system('cls' if sys.platform == 'win32' else 'clear')


def print_header(title: str):
    """Выводит красивый заголовок."""
    width = 60
    print("\n" + "╔" + "═" * width + "╗")
    print(f"║ {title:^{width-2}} ║")
    print("╚" + "═" * width + "╝")
    print()


def print_menu(options: list[tuple[str, str]]):
    """Выводит меню с опциями."""
    for key, desc in options:
        print(f"  [{key}] {desc}")
    print()


def confirm_action(prompt: str) -> bool:
    """Запрашивает подтверждение у пользователя."""
    while True:
        answer = input(f"{prompt} (д/н): ").strip().lower()
        if answer in ('д', 'да', 'y', 'yes', ''):
            return True
        if answer in ('н', 'нет', 'n', 'no'):
            return False
        print("  Пожалуйста, ответь 'д' или 'н'")


def get_env_path() -> str:
    """Возвращает путь к .env файлу."""
    return str(Path(__file__).parent / ".env")


def check_env_file() -> bool:
    """Проверяет существование .env файла."""
    env_path = Path(__file__).parent / ".env"
    return env_path.exists()
