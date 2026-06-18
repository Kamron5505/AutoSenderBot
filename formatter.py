"""
Парсер HTML-подобных тегов в форматированные сообщения Telegram.

Поддерживает:
- <b>текст</b> — жирный текст
- <blockquote>текст</blockquote> — цитата
- <emoji id=123>текст</emoji> — премиум эмодзи (по document_id)

Пример:
    <b>🔥 Акция!</b>
    <blockquote><emoji id=5409294383398818032>⭐️</emoji> 50 Stars — 10,000 so'm</blockquote>
"""

import re
from telethon.tl import types


def parse_message(raw: str) -> tuple[str, list]:
    """
    Парсит HTML-подобные теги в тексте и возвращает (plain_text, entities).

    Рекурсивно обрабатывает вложенные теги (эмодзи внутри цитаты и т.д.).
    """
    token_re = re.compile(
        r'<b>(.*?)</b>|<blockquote(?:\s+\w+)?>(.*?)</blockquote>|<emoji id="?(\d+)"?>(.*?)</emoji>',
        re.DOTALL
    )

    def process(text_chunk: str, current_offset: int) -> tuple[str, list]:
        local_entities = []
        last_idx = 0
        res_text = ""

        for m in token_re.finditer(text_chunk):
            before = text_chunk[last_idx:m.start()]
            res_text += before
            current_offset += len(before.encode("utf-16-le")) // 2

            if m.group(1) is not None:  # <b>текст</b>
                inner_raw = m.group(1)
                inner_text, inner_ents = process(inner_raw, current_offset)
                length = len(inner_text.encode("utf-16-le")) // 2

                local_entities.append(
                    types.MessageEntityBold(offset=current_offset, length=length)
                )
                local_entities.extend(inner_ents)
                res_text += inner_text
                current_offset += length

            elif m.group(2) is not None:  # <blockquote>текст</blockquote>
                inner_raw = m.group(2)
                inner_text, inner_ents = process(inner_raw, current_offset)
                length = len(inner_text.encode("utf-16-le")) // 2

                local_entities.append(
                    types.MessageEntityBlockquote(offset=current_offset, length=length)
                )
                local_entities.extend(inner_ents)
                res_text += inner_text
                current_offset += length

            elif m.group(3) is not None:  # <emoji id=N>текст</emoji>
                emoji_id = int(m.group(3))
                inner_raw = m.group(4)
                inner_text, inner_ents = process(inner_raw, current_offset)
                length = len(inner_text.encode("utf-16-le")) // 2

                local_entities.append(
                    types.MessageEntityCustomEmoji(
                        offset=current_offset,
                        length=length,
                        document_id=emoji_id
                    )
                )
                local_entities.extend(inner_ents)
                res_text += inner_text
                current_offset += length

            last_idx = m.end()

        after = text_chunk[last_idx:]
        res_text += after
        return res_text, local_entities

    plain_text, all_entities = process(raw, 0)
    return plain_text, all_entities
