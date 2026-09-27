"""Zerlegt den PDF-Rohtext in (Lektion, Abschnitt)-Buckets anhand der Fußmarker
'一 課文 TEXT' / '二 字與詞 SCHRIFTZEICHEN UND WÖRTER' / '三 溫習 WIEDERHOLUNG' /
'四 應用 ANWENDUNG' und der Lektionsüberschrift '第X課'. Parst außerdem aus den
gebuckten Zeilen der Abschnitte 課文/應用 Dialog-Triplets (Sprecher/Chinesisch,
Pinyin, Deutsch), aus dem Abschnitt 字與詞 Vokabeleinträge
(Zeichen/Zhuyin/Pinyin/Deutsch) sowie aus dem Abschnitt 溫習 Sprecher/Chinesisch-
Paare ohne Pinyin und Übersetzung."""
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


# Diese Funktion arbeitet drei reale PDF-Eigenheiten aus, die die Zuordnung
# von Seiten zu (Lektion, Abschnitt) erschweren:
#   1. Der Abschnittsmarker steht auf der ERSTEN Seite eines Abschnitts, nicht
#      auf der letzten; unmarkierte Folgeseiten gehören zum zuletzt gesehenen
#      Abschnitt (current_section).
#   2. Das Inhaltsverzeichnis (目錄) listet ebenfalls "第X課"-Überschriften
#      für alle 30 Lektionen auf, aber ohne Abschnittsmarker; ein Header
#      allein (ohne Marker auf derselben Seite) darf die Lektionsnummer daher
#      nicht vorspulen.
#   3. Der Anhang (Vokabelindex/Umschriftentabelle) zählt die Lektionsnummer
#      wieder von vorne hoch, trägt aber nie einen Abschnittsmarker; sobald
#      die erkannte Nummer sinkt, wird nichts mehr weitergeschrieben.
#
# NICHT ausgeglichen wird eine vierte Eigenheit: Die Zuordnung erfolgt auf
# ganzen Seiten. Wechselt der Abschnitt MITTEN auf einer Seite (Rest von
# Abschnitt A steht oben, der Marker für Abschnitt B erscheint erst weiter
# unten auf derselben Seite), landet der Rest von A fälschlich im Bucket von
# B. Gemessene Auswirkung (verifiziert per len(wiederholung) - len(text) je
# Lektion als Proxy, Stand nach dem Multi-Line-Fix in parse_dialogue): 68
# fehlende Dialogzeilen, verteilt auf 17 der 30 Lektionen. Eine vollständige
# Behebung bräuchte zeilen-/koordinatenbasierte Textextraktion
# (get_text("dict") statt get_text()), was für dieses Projekt bewusst als
# YAGNI ausgeklammert wird, nicht aus Versehen fehlt.
def split_into_buckets(raw_pages: list[str]) -> dict[int, dict[str, list[str]]]:
    buckets: dict[int, dict[str, list[str]]] = {}
    current_lesson = 1
    current_section = None
    for raw_page in raw_pages:
        page = fix_text(raw_page)
        section = None
        for pattern, name in SECTION_MARKERS:
            if pattern.search(page):
                section = name
                break
        header_match = LESSON_HEADER.search(page)
        if header_match:
            new_lesson = _chinese_number_to_int(header_match.group(1))
            if new_lesson < current_lesson:
                # Der Anhang (z.B. Vokabelindex/Umschriftentabelle) zählt die
                # Lektionsnummer wieder von vorne hoch und trägt nie einen
                # Abschnittsmarker. Sobald die Nummer sinkt, ist der eigentliche
                # Lektionsteil vorbei; ab hier nichts mehr weiterschreiben.
                current_section = None
                continue
            # Das Inhaltsverzeichnis (目錄) listet ebenfalls "第X課"-Überschriften
            # für alle 30 Lektionen auf einmal auf, aber ohne Abschnittsmarker.
            # Eine echte Lektionsseite trägt Header UND ihren ersten Marker
            # immer gemeinsam; nur dann zählt die Lektionsnummer.
            if section is not None:
                current_lesson = new_lesson
        # Der Abschnittsmarker steht laut PDF-Layout auf der ERSTEN Seite eines
        # Abschnitts, nicht auf der letzten. Unmarkierte Folgeseiten gehören
        # also zum zuletzt gesehenen Abschnitt (current_section), nicht zu
        # einem erst später erscheinenden.
        if section is not None:
            current_section = section
        if current_section is None:
            continue
        lesson_bucket = buckets.setdefault(current_lesson, {})
        lines = [
            line.strip()
            for line in page.splitlines()
            if line.strip() and not BOILERPLATE.match(line.strip())
        ]
        lesson_bucket.setdefault(current_section, []).extend(lines)
    return buckets


DIALOGUE_LINE = re.compile(r"^([^：]{1,6})：(.+)$")
TRANSLATION_PREFIX = re.compile(r"^[^:：]+\s*:\s*")
CJK_CHAR = re.compile(r"[一-鿿]")


def parse_dialogue(lines: list[str]) -> list[dict]:
    entries = []
    i = 0
    n = len(lines)
    while i < n:
        zh_match = DIALOGUE_LINE.match(lines[i])
        # Pinyin-Zeile wird ungeprüft übernommen: sie enthält laut
        # PDF-Struktur nie "：", kann also nie fälschlich als Dialogzeile
        # matchen. Ein Match hier bedeutet, dass auf die vermeintliche
        # Chinesisch-Zeile keine Pinyin-Zeile folgt, also kein echtes Triplet
        # beginnt.
        if not zh_match or i + 1 >= n or DIALOGUE_LINE.match(lines[i + 1]):
            i += 1
            continue
        zh_parts = [zh_match.group(2)]
        pinyin_parts = [lines[i + 1]]
        j = i + 2
        # Ist der chinesische Satz zu lang für eine PDF-Zeile, läuft er in
        # eine zweite, unmarkierte Fortsetzungszeile (ohne Sprecherpräfix)
        # weiter, gefolgt von deren eigener Pinyin-Zeile, bevor die deutsche
        # Übersetzung kommt. Solche Chinesisch/Pinyin-Fortsetzungspaare
        # werden erkannt (chinesische Zeichen, kein Sprecherpräfix) und
        # angehängt: zh ohne Trennzeichen (chinesischer Fließtext kennt
        # keine Leerzeichen zwischen Wörtern), pinyin mit einem Leerzeichen
        # als Trenner (wie auch innerhalb einer Pinyin-Zeile üblich).
        while (
            j + 1 < n
            and CJK_CHAR.search(lines[j])
            and not DIALOGUE_LINE.match(lines[j])
            and not DIALOGUE_LINE.match(lines[j + 1])
        ):
            zh_parts.append(lines[j])
            pinyin_parts.append(lines[j + 1])
            j += 2
        if j >= n or DIALOGUE_LINE.match(lines[j]):
            i += 1
            continue
        de_text = TRANSLATION_PREFIX.sub("", lines[j])
        entries.append(
            {
                "sprecher": zh_match.group(1),
                "zh": "".join(zh_parts),
                "pinyin": " ".join(pinyin_parts),
                "de": de_text,
            }
        )
        i = j + 1
    return entries


VOKABEL_LINE = re.compile(r"^([一-鿿]+)（([^；]+)；([^）]+)）(?:\s*（[^）]+）)*(.+)$")


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


def parse_wiederholung(lines: list[str]) -> list[dict]:
    entries = []
    for line in lines:
        match = DIALOGUE_LINE.match(line)
        if match:
            entries.append({"sprecher": match.group(1), "zh": match.group(2)})
    return entries
