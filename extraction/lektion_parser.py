"""Zerlegt den PDF-Rohtext in (Lektion, Abschnitt)-Buckets anhand der Fussmarker
'一 課文 TEXT' / '二 字與詞 SCHRIFTZEICHEN UND WOERTER' / '三 溫習 WIEDERHOLUNG' /
'四 應用 ANWENDUNG' und der Lektionsueberschrift '第X課'. Parst ausserdem aus den
gebuckten Zeilen der Abschnitte 課文/應用 Dialog-Triplets (Sprecher/Chinesisch,
Pinyin, Deutsch) sowie aus dem Abschnitt 字與詞 Vokabeleintraege
(Zeichen/Zhuyin/Pinyin/Deutsch)."""
import re

from zeichen_fix import fix_text

CN_NUM = {c: i + 1 for i, c in enumerate("一二三四五六七八九十")}
SECTION_MARKERS = [
    (re.compile(r"一\s*課文\s*TEXT"), "課文"),
    (re.compile(r"二\s*字與詞\s*SCHRIFTZEICHEN"), "字與詞"),
    (re.compile(r"三\s*溫習\s*WIEDERHOLUNG"), "溫習"),
    (re.compile(r"四\s*應用\s*ANWENDUNG"), "應用"),
]
LESSON_HEADER = re.compile(r"第([一二三四五六七八九十]{1,3})課")
BOILERPLATE = re.compile(
    r"^(五百字說華語|㈤百字說華語|Mit 500 Wörtern Chinesisch sprechen|中德文版|\d+)\s*$"
)


def _chinese_number_to_int(cn: str) -> int:
    if cn == "十":
        return 10
    if len(cn) == 1:
        return CN_NUM[cn]
    if "十" in cn:
        left, _, right = cn.partition("十")
        tens = CN_NUM[left] if left else 1
        ones = CN_NUM[right] if right else 0
        return tens * 10 + ones
    raise ValueError(f"Unbekannte chinesische Zahl: {cn}")


def split_into_buckets(raw_pages: list[str]) -> dict[int, dict[str, list[str]]]:
    buckets: dict[int, dict[str, list[str]]] = {}
    current_lesson = 1
    for raw_page in raw_pages:
        page = fix_text(raw_page)
        section = None
        for pattern, name in SECTION_MARKERS:
            if pattern.search(page):
                section = name
                break
        header_match = LESSON_HEADER.search(page)
        if header_match:
            current_lesson = _chinese_number_to_int(header_match.group(1))
        if section is None:
            continue
        lesson_bucket = buckets.setdefault(current_lesson, {})
        lines = [
            line.strip()
            for line in page.splitlines()
            if line.strip() and not BOILERPLATE.match(line.strip())
        ]
        lesson_bucket.setdefault(section, []).extend(lines)
    return buckets


DIALOGUE_LINE = re.compile(r"^([^：]{1,6})：(.+)$")
TRANSLATION_LINE = re.compile(r"^.+ : .+$")


def parse_dialogue(lines: list[str]) -> list[dict]:
    entries = []
    i = 0
    while i < len(lines) - 2:
        zh_match = DIALOGUE_LINE.match(lines[i])
        de_match = TRANSLATION_LINE.match(lines[i + 2])
        if zh_match and de_match:
            _, de_text = lines[i + 2].split(" : ", 1)
            entries.append(
                {
                    "sprecher": zh_match.group(1),
                    "zh": zh_match.group(2),
                    # Pinyin-Zeile wird ungeprueft uebernommen: sie enthaelt laut
                    # PDF-Struktur nie "：" oder " : ", kann also nie faelschlich
                    # als Dialog- oder Uebersetzungszeile matchen.
                    "pinyin": lines[i + 1],
                    "de": de_text,
                }
            )
            i += 3
        else:
            i += 1
    return entries


VOKABEL_LINE = re.compile(r"^([一-鿿]+)（([^；]+)；([^）]+)）(.+)$")


def parse_vokabular(lines: list[str]) -> list[dict]:
    entries = []
    for line in lines:
        match = VOKABEL_LINE.match(line)
        if match:
            entries.append(
                {
                    "zh": match.group(1),
                    "zhuyin": match.group(2).strip(),
                    "pinyin": match.group(3).strip(),
                    "de": match.group(4).strip(),
                }
            )
    return entries
