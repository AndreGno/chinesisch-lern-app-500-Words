# Chinesisch-Lernwebseite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Aus `D:\(x)Taiwan CN DE Lernen\500MPDF-s_G-H-Y.pdf` (30 Lektionen, chinesisch-deutsches
Lehrbuch) eine interaktive, statische Lernwebseite bauen, inkl. extrahiertem Original-Audio
und vier Übungsformen (Karteikarten, Satzbau, Hörverständnis, Ausspracheübung), hostbar auf
GitHub Pages.

**Architecture:** Zweistufig. (1) Einmaliges Python-Tooling (`extraction/`) liest die PDF aus,
bereinigt kaputte Zeichen, extrahiert 247 eingebettete Original-MP3s und erzeugt
`data/lektion-01.json … lektion-30.json` + `data/vokabular.json`. (2) Eine reine
HTML/CSS/Vanilla-JS-Website (`index.html`, `lektion.html`, `js/*.js`) liest diese JSON-Dateien
zur Laufzeit im Browser und rendert Lektionen + Übungen. Kein Build-Schritt, kein Backend.

**Tech Stack:** Python 3.12 + PyMuPDF (Extraktion, einmalig, nicht Teil der Live-Seite),
Vanilla JavaScript (ES-Module) + HTML + CSS (Live-Seite), `pytest` (Python-Tests),
Node.js `node:test` (JS-Logik-Tests für SRS-Algorithmus), Git + GitHub Pages (Deployment).

---

## Bereits verifizierte Fakten (Grundlage dieses Plans)

- Quelle: `D:\(x)Taiwan CN DE Lernen\500MPDF-s_G-H-Y.pdf`, 237 Seiten, 30 Lektionen.
- 247 eindeutige MP3-Dateien sind im PDF eingebettet (Filespec-Objekte mit `.mp3`-Namen,
  echte Streams über `EF /F <n> 0 R`), Extraktion mit PyMuPDF bereits erfolgreich getestet
  (Gesamtgröße ca. 9,96 MB).
- Der Rohtext enthält 32 verschiedene kaputte Unicode-Zeichen (Block "Ideographic Annotation"
  U+3190–U+319F und "Parenthesized/Circled Ideograph" U+3220–U+32FF), die als Ersatz für
  normale chinesische Zeichen im Font verwendet wurden. Vollständige, verifizierte
  Zuordnungstabelle (durch Kontextvergleich mit dem PDF-Originaltext geprüft):

  | Zeichen | Codepoint | Korrekt | Zeichen | Codepoint | Korrekt |
  |---|---|---|---|---|---|
  | ㆗ | U+3197 | 中 | ㈥ | U+3225 | 六 |
  | ㆒ | U+3192 | 一 | ㊢ | U+32A2 | 寫 |
  | ㆙ | U+3199 | 甲 | ㊛ | U+329B | 女 |
  | ㆚ | U+319A | 乙 | ㈪ | U+322A | 月 |
  | ㈲ | U+3232 | 有 | ㊚ | U+329A | 男 |
  | ㈻ | U+323B | 學 | ㆕ | U+3195 | 四 |
  | ㈤ | U+3224 | 五 | ㈧ | U+3227 | 八 |
  | ㆖ | U+3196 | 上 | ㈴ | U+3234 | 名 |
  | ㆝ | U+319D | 天 | ㆞ | U+319E | 地 |
  | ㈩ | U+3229 | 十 | ㈰ | U+3230 | 日 |
  | ㆟ | U+319F | 人 | ㈦ | U+3226 | 七 |
  | ㆓ | U+3193 | 二 | ㈨ | U+3228 | 九 |
  | ㆘ | U+3198 | 下 | ㈬ | U+322C | 水 |
  | ㆔ | U+3194 | 三 | ㊧ | U+32A7 | 左 |
  | ㆛ | U+319B | 丙 | ㊨ | U+32A8 | 右 |
  | ㉂ | U+3242 | 自 | ㊩ | U+32A9 | 醫 |

- Jede Lektionsseite trägt am Fußende einen Abschnitts-Marker, der angibt, zu welchem der
  vier Teile die Seite gehört: `一 課文 TEXT`, `二 字與詞 SCHRIFTZEICHEN UND WÖRTER`,
  `三 溫習 WIEDERHOLUNG`, `四 應用 ANWENDUNG`. Lektionsgrenzen erkennt man an
  `第X課` (X = chinesisches Zahlzeichen 一 bis 三十).
- Format je Abschnitt (verifiziert an Lektion 1, Seiten 7–19 der PDF):
  - **課文 / 應用**: Dreizeilen-Block je Satz: `Sprecher：Chinesischer Satz`, dann eine
    Pinyin-Zeile (Silben durch mehrere Leerzeichen getrennt), dann
    `Deutscher Sprecher : Deutsche Übersetzung`.
  - **字與詞**: Vokabeleinträge im Format `Zeichen（Zhuyin；Pinyin）Deutsche Bedeutung`,
    gefolgt von 0–n Beispielsatz-Dreizeilenblöcken (wie oben, aber ohne `Sprecher：`-Präfix).
  - **溫習**: nur `Sprecher：Chinesischer Satz`-Zeilen, keine Pinyin-/Deutsch-Zeilen.
  - Bopomofo/Zhuyin ist **nur** in `字與詞`-Vokabeleinträgen als Text vorhanden, nicht pro
    Dialogzeile in 課文/應用/溫習 (im Original ist es dort eine grafische Ruby-Annotation,
    kein extrahierbarer Text). **Anpassung gegenüber dem ursprünglichen Datenmodell im
    Design-Dokument**: Dialogzeilen (`text`/`anwendung`) bekommen kein `zhuyin`-Feld, nur
    `woerter`-Einträge haben `zhuyin`.
- Bekannte Ausnahme: Seite 118 (Vokabular mit Bildern, z.B. "毛筆") folgt einem anderen
  Layout. Solche Ausreißer werden nach dem automatischen Lauf manuell im JSON korrigiert
  (siehe Task 8), nicht automatisch geparst.

---

## Datei-Struktur

```
ChinesischLernApp/
├── extraction/
│   ├── requirements.txt
│   ├── zeichen_fix.py
│   ├── test_zeichen_fix.py
│   ├── extract_audio.py
│   ├── test_extract_audio.py
│   ├── lektion_parser.py
│   ├── test_lektion_parser.py
│   ├── run_extraction.py          # orchestriert: Audio + alle 30 Lektionen -> data/
│   └── fixtures/
│       └── lektion_01_raw.py       # echter Rohtext von Seite 7-19 als Test-Fixture
├── data/
│   ├── lektion-01.json … lektion-30.json
│   └── vokabular.json
├── audio/                          # 247 extrahierte mp3s
├── index.html
├── lektion.html
├── css/style.css
├── js/
│   ├── app.js
│   ├── lektion.js
│   ├── srs.js
│   ├── srs.test.js
│   ├── karteikarten.js
│   ├── satzbau.js
│   ├── hoerverstehen.js
│   ├── aussprache.js
│   └── fortschritt.js
├── package.json                    # nur für `node --test` (JS-Unit-Tests)
└── docs/superpowers/{specs,plans}/
```

---

## Phase A: Datenextraktion (Python, einmalig)

### Task 1: Projekt-Grundgerüst

**Files:**
- Create: `extraction/requirements.txt`
- Create: `package.json`
- Create: `.gitignore`

- [ ] **Step 1: Ordner anlegen und Basisdateien schreiben**

`extraction/requirements.txt`:
```
pymupdf==1.28.2
pytest==8.3.3
```

`package.json`:
```json
{
  "name": "chinesisch-lern-app",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test js/"
  }
}
```

`.gitignore`:
```
__pycache__/
*.pyc
.venv/
node_modules/
```

- [ ] **Step 2: Python-Umgebung installieren**

Run: `pip install -r extraction/requirements.txt`
Expected: pymupdf und pytest installieren sich ohne Fehler (pymupdf ist bereits systemweit
vorhanden, siehe vorherige Session-Diagnose).

- [ ] **Step 3: Commit**

```bash
git add extraction/requirements.txt package.json .gitignore
git commit -m "chore: project scaffolding for extraction tooling and JS tests"
```

---

### Task 2: Zeichen-Fix-Tabelle

**Files:**
- Create: `extraction/zeichen_fix.py`
- Test: `extraction/test_zeichen_fix.py`

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`extraction/test_zeichen_fix.py`:
```python
from zeichen_fix import fix_text


def test_fixes_title_page():
    assert fix_text("㈤百字說華語") == "五百字說華語"
    assert fix_text("㆗德文版") == "中德文版"


def test_fixes_dialogue_markers():
    assert fix_text("㆙：這是什麼？") == "甲：這是什麼？"
    assert fix_text("㆚：這是㆒枝筆。") == "乙：這是一枝筆。"


def test_fixes_numbers_and_dates():
    assert fix_text("星期㆔㆘午從兩點㆖到㆕點") == "星期三下午從兩點上到四點"
    assert fix_text("㈩㈦") == "十七"


def test_leaves_normal_text_untouched():
    assert fix_text("王先生您早，謝謝。") == "王先生您早，謝謝。"
```

- [ ] **Step 2: Test ausführen, Fehlschlag prüfen**

Run: `cd extraction && pytest test_zeichen_fix.py -v`
Expected: FAIL mit `ModuleNotFoundError: No module named 'zeichen_fix'`

- [ ] **Step 3: Implementierung schreiben**

`extraction/zeichen_fix.py`:
```python
"""Ersetzt kaputte Font-Codepoints (Ideographic Annotation / Parenthesized/Circled
Ideograph) durch die eigentlich gemeinten CJK-Unified-Ideographs. Siehe Design-Dokument
und Plan-Kopf fuer die verifizierte Herleitung jedes Eintrags."""

BROKEN_CHAR_MAP = {
    "\u3197": "中", "\u3192": "一", "\u3199": "甲", "\u319a": "乙",
    "\u3232": "有", "\u323b": "學", "\u3224": "五", "\u3196": "上",
    "\u319d": "天", "\u3229": "十", "\u319f": "人", "\u3193": "二",
    "\u3198": "下", "\u3194": "三", "\u3225": "六", "\u32a2": "寫",
    "\u329b": "女", "\u322a": "月", "\u329a": "男", "\u3195": "四",
    "\u3227": "八", "\u3234": "名", "\u319e": "地", "\u3230": "日",
    "\u3226": "七", "\u3228": "九", "\u322c": "水", "\u32a7": "左",
    "\u32a8": "右", "\u319b": "丙", "\u3242": "自", "\u32a9": "醫",
}


def fix_text(text: str) -> str:
    for broken, correct in BROKEN_CHAR_MAP.items():
        text = text.replace(broken, correct)
    return text
```

- [ ] **Step 4: Test ausführen, Erfolg prüfen**

Run: `cd extraction && pytest test_zeichen_fix.py -v`
Expected: PASS (4 Tests)

- [ ] **Step 5: Commit**

```bash
git add extraction/zeichen_fix.py extraction/test_zeichen_fix.py
git commit -m "feat: add character-fix table for broken PDF font codepoints"
```

---

### Task 3: Audio-Extraktion

**Files:**
- Create: `extraction/extract_audio.py`
- Test: `extraction/test_extract_audio.py`

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`extraction/test_extract_audio.py`:
```python
from pathlib import Path

from extract_audio import extract_all_audio

PDF_PATH = Path(r"D:\(x)Taiwan CN DE Lernen\500MPDF-s_G-H-Y.pdf")


def test_extracts_expected_number_of_mp3s(tmp_path):
    written = extract_all_audio(pdf_path=PDF_PATH, out_dir=tmp_path)
    assert len(written) == 247


def test_extracted_files_are_valid_mp3(tmp_path):
    written = extract_all_audio(pdf_path=PDF_PATH, out_dir=tmp_path)
    sample_name = next(iter(written))
    data = (tmp_path / sample_name).read_bytes()
    # MP3-Frame beginnt mit 0xFFFB/0xFFFA (MPEG-1 Layer 3) oder "ID3"-Tag
    assert data[:3] == b"ID3" or data[:2] == b"\xff\xfb" or data[:2] == b"\xff\xfa"


def test_filenames_follow_lektion_pattern(tmp_path):
    written = extract_all_audio(pdf_path=PDF_PATH, out_dir=tmp_path)
    assert "01-01.mp3" in written
    assert "30-09.mp3" in written
```

- [ ] **Step 2: Test ausführen, Fehlschlag prüfen**

Run: `cd extraction && pytest test_extract_audio.py -v`
Expected: FAIL mit `ModuleNotFoundError: No module named 'extract_audio'`

- [ ] **Step 3: Implementierung schreiben**

`extraction/extract_audio.py`:
```python
"""Extrahiert alle im PDF eingebetteten MP3-Dateien (echte Sound-Streams, referenziert
ueber Filespec-Objekte mit /F <name>.mp3 und /EF <</F <stream_xref> 0 R>>)."""
import re
from pathlib import Path

import pymupdf


def extract_all_audio(pdf_path: Path, out_dir: Path) -> dict[str, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf_path))
    written: dict[str, int] = {}
    for xref in range(1, doc.xref_length()):
        try:
            keys = doc.xref_get_keys(xref)
        except Exception:
            continue
        if "F" not in keys or "EF" not in keys:
            continue
        fname = doc.xref_get_key(xref, "F")[1]
        if not fname.lower().endswith(".mp3") or fname in written:
            continue
        ef_raw = doc.xref_get_key(xref, "EF")[1]
        match = re.search(r"(\d+)\s+0\s+R", ef_raw)
        if not match:
            continue
        stream_xref = int(match.group(1))
        if not doc.xref_is_stream(stream_xref):
            continue
        data = doc.xref_stream(stream_xref)
        (out_dir / fname).write_bytes(data)
        written[fname] = len(data)
    return written


if __name__ == "__main__":
    result = extract_all_audio(
        pdf_path=Path(r"D:\(x)Taiwan CN DE Lernen\500MPDF-s_G-H-Y.pdf"),
        out_dir=Path(__file__).parent.parent / "audio",
    )
    print(f"{len(result)} Audiodateien extrahiert.")
```

- [ ] **Step 4: Test ausführen, Erfolg prüfen**

Run: `cd extraction && pytest test_extract_audio.py -v`
Expected: PASS (3 Tests)

- [ ] **Step 5: Commit**

```bash
git add extraction/extract_audio.py extraction/test_extract_audio.py
git commit -m "feat: add embedded MP3 extraction from PDF filespec streams"
```

---

### Task 4: Lektions-Rohtext einlesen und in Buckets aufteilen

**Files:**
- Create: `extraction/fixtures/lektion_01_raw.py`
- Create: `extraction/lektion_parser.py` (Teil 1: `split_into_buckets`)
- Test: `extraction/test_lektion_parser.py` (Teil 1)

- [ ] **Step 1: Echtes Fixture aus der PDF einfrieren**

`extraction/fixtures/lektion_01_raw.py` — enthält die verifizierten Rohtexte der Seiten
7 bis 19 (Lektion 1 komplett) als Liste von Strings, exakt wie von
`page.get_text()` zurückgegeben (inkl. kaputter Zeichen, wird von `zeichen_fix` bereinigt).
Diese Datei wird per Skript erzeugt, nicht abgetippt:

```python
# Wird einmalig per Skript erzeugt (siehe Step 1b), danach eingefroren und committed.
```

- [ ] **Step 1b: Fixture-Erzeugungsskript einmalig ausführen**

Run:
```bash
python - <<'EOF'
import pymupdf
doc = pymupdf.open(r"D:\(x)Taiwan CN DE Lernen\500MPDF-s_G-H-Y.pdf")
pages = [doc[i].get_text() for i in range(7, 19)]
with open("extraction/fixtures/lektion_01_raw.py", "w", encoding="utf-8") as f:
    f.write("PAGES = ")
    f.write(repr(pages))
    f.write("\n")
EOF
```
Expected: Datei `extraction/fixtures/lektion_01_raw.py` mit `PAGES = [...]` (12 Strings) wird
geschrieben.

- [ ] **Step 2: Fehlschlagenden Test schreiben**

`extraction/test_lektion_parser.py`:
```python
from fixtures.lektion_01_raw import PAGES
from lektion_parser import split_into_buckets


def test_splits_lektion_1_into_four_sections():
    buckets = split_into_buckets(PAGES)
    assert set(buckets[1].keys()) == {"課文", "字與詞", "溫習", "應用"}


def test_text_section_contains_expected_dialogue():
    buckets = split_into_buckets(PAGES)
    joined = "\n".join(buckets[1]["課文"])
    assert "王先生，您早。" in joined
    assert "Guten Morgen, Herr Wang!" in joined


def test_woerter_section_contains_vocab_entry():
    buckets = split_into_buckets(PAGES)
    joined = "\n".join(buckets[1]["字與詞"])
    assert "先生" in joined


def test_wiederholung_section_has_no_translation_lines():
    buckets = split_into_buckets(PAGES)
    joined = "\n".join(buckets[1]["溫習"])
    assert "Guten Morgen" not in joined
```

- [ ] **Step 3: Test ausführen, Fehlschlag prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v`
Expected: FAIL mit `ModuleNotFoundError: No module named 'lektion_parser'`

- [ ] **Step 4: Implementierung schreiben**

`extraction/lektion_parser.py`:
```python
"""Zerlegt den PDF-Rohtext in (Lektion, Abschnitt)-Buckets anhand der Fussmarker
'一 課文 TEXT' / '二 字與詞 SCHRIFTZEICHEN UND WOERTER' / '三 溫習 WIEDERHOLUNG' /
'四 應用 ANWENDUNG' und der Lektionsueberschrift '第X課'."""
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
```

- [ ] **Step 5: Test ausführen, Erfolg prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v`
Expected: PASS (4 Tests)

- [ ] **Step 6: Commit**

```bash
git add extraction/fixtures/lektion_01_raw.py extraction/lektion_parser.py extraction/test_lektion_parser.py
git commit -m "feat: split PDF pages into per-lesson/per-section text buckets"
```

---

### Task 5: Dialogzeilen-Parser (課文 / 應用)

**Files:**
- Modify: `extraction/lektion_parser.py` (Funktion `parse_dialogue` ergänzen)
- Modify: `extraction/test_lektion_parser.py`

- [ ] **Step 1: Fehlschlagenden Test ergänzen**

An `extraction/test_lektion_parser.py` anhängen:
```python
from lektion_parser import parse_dialogue


def test_parse_dialogue_extracts_speaker_zh_pinyin_de():
    lines = [
        "李太太：王先生，您早。",
        "Lǐ tài tai Wáng xiān shēng nín zǎo",
        "Frau Li : Guten Morgen, Herr Wang!",
    ]
    result = parse_dialogue(lines)
    assert result == [
        {
            "sprecher": "李太太",
            "zh": "王先生，您早。",
            "pinyin": "Lǐ tài tai Wáng xiān shēng nín zǎo",
            "de": "Guten Morgen, Herr Wang!",
        }
    ]


def test_parse_dialogue_handles_multiple_lines():
    lines = [
        "李太太：王先生，您早。",
        "Lǐ tài tai Wáng xiān shēng nín zǎo",
        "Frau Li : Guten Morgen, Herr Wang!",
        "王先生：早，李太太，您早。",
        "Wáng xiān shēng zǎo Lǐ tài tai nín zǎo",
        "Herr Wang : Guten Morgen, Frau Li!",
    ]
    result = parse_dialogue(lines)
    assert len(result) == 2
    assert result[1]["sprecher"] == "王先生"
```

- [ ] **Step 2: Test ausführen, Fehlschlag prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v -k parse_dialogue`
Expected: FAIL mit `ImportError: cannot import name 'parse_dialogue'`

- [ ] **Step 3: Implementierung ergänzen**

An `extraction/lektion_parser.py` anhängen:
```python
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
                    "pinyin": lines[i + 1],
                    "de": de_text,
                }
            )
            i += 3
        else:
            i += 1
    return entries
```

- [ ] **Step 4: Test ausführen, Erfolg prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v -k parse_dialogue`
Expected: PASS (2 Tests)

- [ ] **Step 5: Commit**

```bash
git add extraction/lektion_parser.py extraction/test_lektion_parser.py
git commit -m "feat: parse dialogue triplets (speaker/zh/pinyin/de) from text sections"
```

---

### Task 6: Vokabel-Parser (字與詞)

**Files:**
- Modify: `extraction/lektion_parser.py` (Funktion `parse_vokabular` ergänzen)
- Modify: `extraction/test_lektion_parser.py`

- [ ] **Step 1: Fehlschlagenden Test ergänzen**

Anhängen an `extraction/test_lektion_parser.py`:
```python
from lektion_parser import parse_vokabular


def test_parse_vokabular_extracts_entry():
    lines = ["先生（ㄒㄧㄢ ㄕㄥ；xiān sheng）der Mann, der Herr"]
    result = parse_vokabular(lines)
    assert result == [
        {
            "zh": "先生",
            "zhuyin": "ㄒㄧㄢ ㄕㄥ",
            "pinyin": "xiān sheng",
            "de": "der Mann, der Herr",
        }
    ]


def test_parse_vokabular_ignores_non_matching_lines():
    lines = ["先生（ㄒㄧㄢ ㄕㄥ；xiān sheng）der Mann, der Herr", "王先生", "Wáng xiān shēng"]
    result = parse_vokabular(lines)
    assert len(result) == 1
```

- [ ] **Step 2: Test ausführen, Fehlschlag prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v -k parse_vokabular`
Expected: FAIL mit `ImportError: cannot import name 'parse_vokabular'`

- [ ] **Step 3: Implementierung ergänzen**

An `extraction/lektion_parser.py` anhängen:
```python
VOKABEL_LINE = re.compile(r"^([\u4e00-\u9fff]+)（([^；]+)；([^）]+)）(.+)$")


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
```

- [ ] **Step 4: Test ausführen, Erfolg prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v -k parse_vokabular`
Expected: PASS (2 Tests)

- [ ] **Step 5: Commit**

```bash
git add extraction/lektion_parser.py extraction/test_lektion_parser.py
git commit -m "feat: parse vocabulary entries (zh/zhuyin/pinyin/de) from word sections"
```

---

### Task 7: 溫習-Parser

**Files:**
- Modify: `extraction/lektion_parser.py` (Funktion `parse_wiederholung` ergänzen)
- Modify: `extraction/test_lektion_parser.py`

- [ ] **Step 1: Fehlschlagenden Test ergänzen**

```python
from lektion_parser import parse_wiederholung


def test_parse_wiederholung_extracts_speaker_and_zh_only():
    lines = ["王先生：李太太，您早。", "李太太：早，王先生，您早。"]
    result = parse_wiederholung(lines)
    assert result == [
        {"sprecher": "王先生", "zh": "李太太，您早。"},
        {"sprecher": "李太太", "zh": "早，王先生，您早。"},
    ]
```

- [ ] **Step 2: Test ausführen, Fehlschlag prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v -k parse_wiederholung`
Expected: FAIL mit `ImportError: cannot import name 'parse_wiederholung'`

- [ ] **Step 3: Implementierung ergänzen**

```python
def parse_wiederholung(lines: list[str]) -> list[dict]:
    entries = []
    for line in lines:
        match = DIALOGUE_LINE.match(line)
        if match:
            entries.append({"sprecher": match.group(1), "zh": match.group(2)})
    return entries
```

- [ ] **Step 4: Test ausführen, Erfolg prüfen**

Run: `cd extraction && pytest test_lektion_parser.py -v -k parse_wiederholung`
Expected: PASS (1 Test)

- [ ] **Step 5: Commit**

```bash
git add extraction/lektion_parser.py extraction/test_lektion_parser.py
git commit -m "feat: parse Wiederholung section (speaker + chinese line only)"
```

---

### Task 8: Audio-Zuordnung, Zusammenbau und Voll-Lauf über alle 30 Lektionen

**Files:**
- Create: `extraction/build_lesson_json.py`
- Test: `extraction/test_build_lesson_json.py`
- Create: `extraction/run_extraction.py`
- Create (generiert): `data/lektion-01.json` … `data/lektion-30.json`, `data/vokabular.json`
- Create (generiert): `audio/*.mp3`

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`extraction/test_build_lesson_json.py`:
```python
from build_lesson_json import assign_audio, build_lesson


def test_assign_audio_matches_by_order():
    entries = [{"zh": "A"}, {"zh": "B"}, {"zh": "C"}]
    result = assign_audio(entries, lektion_nummer=1)
    assert result[0]["audio"] == "audio/01-01.mp3"
    assert result[1]["audio"] == "audio/01-02.mp3"
    assert result[2]["audio"] == "audio/01-03.mp3"


def test_build_lesson_combines_sections():
    buckets = {
        "課文": ["李太太：您早。", "Lǐ tài tai nín zǎo", "Frau Li : Guten Morgen!"],
        "字與詞": ["早（ㄗㄠˇ；zǎo）frueh"],
        "溫習": ["李太太：您早。"],
        "應用": [],
    }
    lesson = build_lesson(1, buckets)
    assert lesson["nummer"] == 1
    assert lesson["text"][0]["audio"] == "audio/01-01.mp3"
    assert lesson["woerter"][0]["zh"] == "早"
    assert lesson["wiederholung"][0]["zh"] == "您早。"
    assert lesson["anwendung"] == []
```

- [ ] **Step 2: Test ausführen, Fehlschlag prüfen**

Run: `cd extraction && pytest test_build_lesson_json.py -v`
Expected: FAIL mit `ModuleNotFoundError: No module named 'build_lesson_json'`

- [ ] **Step 3: Implementierung schreiben**

`extraction/build_lesson_json.py`:
```python
"""Baut aus den geparsten Abschnitten pro Lektion ein vollstaendiges JSON-Objekt und
ordnet Audiodateien den Dialogzeilen ueber ihre Reihenfolge zu (Annahme: Sound-Clips im
PDF liegen in Lesereihenfolge vor, wird beim manuellen Review gegengehoert)."""
from lektion_parser import parse_dialogue, parse_vokabular, parse_wiederholung


def assign_audio(entries: list[dict], lektion_nummer: int) -> list[dict]:
    result = []
    for i, entry in enumerate(entries, start=1):
        result.append({**entry, "audio": f"audio/{lektion_nummer:02d}-{i:02d}.mp3"})
    return result


def build_lesson(nummer: int, buckets: dict[str, list[str]]) -> dict:
    text = assign_audio(parse_dialogue(buckets.get("課文", [])), nummer)
    return {
        "nummer": nummer,
        "text": text,
        "woerter": parse_vokabular(buckets.get("字與詞", [])),
        "wiederholung": parse_wiederholung(buckets.get("溫習", [])),
        "anwendung": parse_dialogue(buckets.get("應用", [])),
    }
```

- [ ] **Step 4: Test ausführen, Erfolg prüfen**

Run: `cd extraction && pytest test_build_lesson_json.py -v`
Expected: PASS (2 Tests)

- [ ] **Step 5: Commit**

```bash
git add extraction/build_lesson_json.py extraction/test_build_lesson_json.py
git commit -m "feat: assemble per-lesson JSON with order-based audio assignment"
```

- [ ] **Step 6: Orchestrierungsskript schreiben**

`extraction/run_extraction.py`:
```python
"""Einmaliger Voll-Lauf: extrahiert Audio + alle 30 Lektionen als JSON."""
import json
from pathlib import Path

import pymupdf

from build_lesson_json import build_lesson
from extract_audio import extract_all_audio
from lektion_parser import split_into_buckets

PDF_PATH = Path(r"D:\(x)Taiwan CN DE Lernen\500MPDF-s_G-H-Y.pdf")
ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
AUDIO_DIR = ROOT / "audio"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    written = extract_all_audio(PDF_PATH, AUDIO_DIR)
    print(f"{len(written)} Audiodateien nach {AUDIO_DIR} extrahiert.")

    doc = pymupdf.open(str(PDF_PATH))
    raw_pages = [doc[i].get_text() for i in range(len(doc))]
    buckets_by_lesson = split_into_buckets(raw_pages)

    all_vokabeln = []
    for nummer in sorted(buckets_by_lesson):
        lesson = build_lesson(nummer, buckets_by_lesson[nummer])
        out_path = DATA_DIR / f"lektion-{nummer:02d}.json"
        out_path.write_text(
            json.dumps(lesson, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        for eintrag in lesson["woerter"]:
            all_vokabeln.append({**eintrag, "lektion": nummer})
        print(f"Lektion {nummer:02d}: {out_path.name} geschrieben "
              f"({len(lesson['text'])} Dialogzeilen, {len(lesson['woerter'])} Vokabeln)")

    (DATA_DIR / "vokabular.json").write_text(
        json.dumps(all_vokabeln, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"vokabular.json geschrieben ({len(all_vokabeln)} Eintraege gesamt).")


if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Voll-Lauf ausführen**

Run: `cd extraction && python run_extraction.py`
Expected: Konsolenausgabe listet 30 Lektionsdateien mit Dialogzeilen-/Vokabelzahlen > 0
für jede Lektion; `data/` enthält 31 JSON-Dateien, `audio/` enthält 247 mp3-Dateien.

- [ ] **Step 8: Stichprobenkontrolle (manuell, nicht automatisierbar)**

Für mindestens Lektion 1, eine mittlere Lektion (z.B. 15) und die letzte Lektion (30):
`data/lektion-NN.json` neben der PDF-Seite öffnen und prüfen, ob Dialogzeilen, Vokabeln
und Audiozuordnung plausibel sind. Bekannter Sonderfall: die Bild-Vokabular-Seite (PDF-Seite
118, "毛筆"-Dialog) wird vermutlich falsch/unvollständig geparst — dort das erzeugte JSON
von Hand nachbessern statt den Parser dafür zu verallgemeinern (YAGNI: ein Einzelfall
rechtfertigt keine Sonderlogik im Parser).

- [ ] **Step 9: Commit der generierten Daten**

```bash
git add extraction/run_extraction.py data/ audio/
git commit -m "feat: run full extraction pipeline for all 30 lessons"
```

---

## Phase B: Frontend-Grundgerüst

### Task 9: HTML/CSS-Grundgerüst und Datenlader

**Files:**
- Create: `css/style.css`
- Create: `js/app.js`

- [ ] **Step 1: Grund-CSS schreiben**

`css/style.css`:
```css
:root {
  --rot: #b3202c;
  --gold: #c9a227;
  --bg: #faf7f2;
  --karte-bg: #ffffff;
  --text: #2a2320;
  --radius: 12px;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "Segoe UI", system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
}

h1, h2, .zh {
  font-family: "Noto Sans TC", "Segoe UI", sans-serif;
}

header.kopf {
  background: var(--rot);
  color: white;
  padding: 1.5rem 1rem;
  text-align: center;
}

header.kopf h1 { margin: 0; font-size: 1.5rem; }

main {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}

.lektion-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.lektion-karte {
  background: var(--karte-bg);
  border-radius: var(--radius);
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  text-decoration: none;
  color: var(--text);
  border-top: 4px solid var(--gold);
}

.lektion-karte .zh { font-size: 1.3rem; margin: 0 0 0.25rem; }
.lektion-karte .de { font-size: 0.9rem; opacity: 0.75; margin: 0; }

.fortschritt-balken {
  height: 6px;
  background: #eee;
  border-radius: 3px;
  margin-top: 0.5rem;
  overflow: hidden;
}
.fortschritt-balken > span {
  display: block;
  height: 100%;
  background: var(--rot);
}

@media (max-width: 480px) {
  main { padding: 0.5rem; }
}
```

- [ ] **Step 2: Datenlader schreiben**

`js/app.js`:
```javascript
export async function ladeLektionsListe() {
  const nummern = Array.from({ length: 30 }, (_, i) => i + 1);
  const lektionen = await Promise.all(
    nummern.map(async (n) => {
      const id = String(n).padStart(2, "0");
      const res = await fetch(`data/lektion-${id}.json`);
      return res.json();
    })
  );
  return lektionen;
}

export async function ladeLektion(nummer) {
  const id = String(nummer).padStart(2, "0");
  const res = await fetch(`data/lektion-${id}.json`);
  if (!res.ok) throw new Error(`Lektion ${nummer} nicht gefunden`);
  return res.json();
}
```

- [ ] **Step 3: Manuell im Browser prüfen**

Da `fetch()` bei `file://`-URLs in den meisten Browsern durch CORS blockiert wird,
lokalen Server starten:

Run: `python -m http.server 8000` (im Projektroot)
Öffnen: `http://localhost:8000/index.html` (Ergebnis erst nach Task 10 sichtbar)

- [ ] **Step 4: Commit**

```bash
git add css/style.css js/app.js
git commit -m "feat: base stylesheet and lesson data loader"
```

---

### Task 10: Startseite mit Lektionsübersicht

**Files:**
- Create: `index.html`
- Modify: `js/app.js` (Rendering-Funktion ergänzen)

- [ ] **Step 1: `index.html` schreiben**

```html
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>五百字說華語 — Interaktiv</title>
  <link rel="stylesheet" href="css/style.css" />
</head>
<body>
  <header class="kopf">
    <h1>五百字說華語 <span style="font-weight:normal">— Mit 500 Wörtern Chinesisch sprechen</span></h1>
  </header>
  <main>
    <div id="lektion-grid" class="lektion-grid">Lade Lektionen…</div>
  </main>
  <script type="module" src="js/main.js"></script>
</body>
</html>
```

- [ ] **Step 2: Rendering-Funktion und Einstiegspunkt schreiben**

An `js/app.js` anhängen:
```javascript
export function ladeFortschritt() {
  try {
    return JSON.parse(localStorage.getItem("fortschritt") || "{}");
  } catch {
    return {};
  }
}

export function rendereLektionsGrid(lektionen, fortschritt, container) {
  container.innerHTML = "";
  for (const lektion of lektionen) {
    const gelernt = fortschritt[`lektion-${lektion.nummer}`]?.gelesenAnteil ?? 0;
    const a = document.createElement("a");
    a.href = `lektion.html?id=${lektion.nummer}`;
    a.className = "lektion-karte";
    a.innerHTML = `
      <p class="zh">第${lektion.nummer}課</p>
      <p class="de">${lektion.text[0]?.de ?? ""}</p>
      <div class="fortschritt-balken"><span style="width:${gelernt * 100}%"></span></div>
    `;
    container.appendChild(a);
  }
}
```

`js/main.js`:
```javascript
import { ladeLektionsListe, ladeFortschritt, rendereLektionsGrid } from "./app.js";

const lektionen = await ladeLektionsListe();
const fortschritt = ladeFortschritt();
rendereLektionsGrid(lektionen, fortschritt, document.getElementById("lektion-grid"));
```

- [ ] **Step 3: Im Browser prüfen**

Run: `python -m http.server 8000`
Öffnen: `http://localhost:8000/index.html`
Erwartet: 30 Kacheln mit chinesischem Lektionstitel (第N課) und deutscher erster
Dialogzeile, ohne Konsolenfehler (F12 → Console prüfen).

- [ ] **Step 4: Commit**

```bash
git add index.html js/app.js js/main.js
git commit -m "feat: render lesson overview grid on the home page"
```

---

### Task 11: Lektionsseite mit 4 Tabs und Audio-Player

**Files:**
- Create: `lektion.html`
- Create: `js/lektion.js`

- [ ] **Step 1: `lektion.html` schreiben**

```html
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Lektion — 五百字說華語</title>
  <link rel="stylesheet" href="css/style.css" />
</head>
<body>
  <header class="kopf"><h1 id="lektion-titel">Lade…</h1></header>
  <main>
    <nav id="tabs"></nav>
    <section id="tab-inhalt"></section>
  </main>
  <script type="module" src="js/lektion-main.js"></script>
</body>
</html>
```

- [ ] **Step 2: Rendering-Logik schreiben**

`js/lektion.js`:
```javascript
const TABS = [
  { key: "text", label: "課文 Text" },
  { key: "woerter", label: "字與詞 Wörter" },
  { key: "wiederholung", label: "溫習 Wiederholung" },
  { key: "anwendung", label: "應用 Anwendung" },
];

export function rendereTabs(lektion, container, onWahl) {
  container.innerHTML = "";
  for (const tab of TABS) {
    const btn = document.createElement("button");
    btn.textContent = tab.label;
    btn.addEventListener("click", () => onWahl(tab.key));
    container.appendChild(btn);
  }
}

export function rendereDialogListe(eintraege) {
  return eintraege
    .map(
      (e) => `
      <div class="dialog-zeile">
        <p class="zh">${e.sprecher ? e.sprecher + "：" : ""}${e.zh}</p>
        ${e.pinyin ? `<p class="pinyin">${e.pinyin}</p>` : ""}
        ${e.de ? `<p class="de">${e.de}</p>` : ""}
        ${e.audio ? `<audio controls src="${e.audio}"></audio>` : ""}
      </div>`
    )
    .join("");
}

export function rendereWoerterListe(eintraege) {
  return eintraege
    .map(
      (e) => `
      <div class="wort-zeile">
        <p class="zh">${e.zh} <span class="zhuyin">${e.zhuyin}</span></p>
        <p class="pinyin">${e.pinyin}</p>
        <p class="de">${e.de}</p>
      </div>`
    )
    .join("");
}

export function rendereTabInhalt(lektion, tabKey, container) {
  if (tabKey === "text" || tabKey === "anwendung") {
    container.innerHTML = rendereDialogListe(lektion[tabKey]);
  } else if (tabKey === "woerter") {
    container.innerHTML = rendereWoerterListe(lektion.woerter);
  } else if (tabKey === "wiederholung") {
    container.innerHTML = lektion.wiederholung
      .map((e) => `<p class="zh">${e.sprecher}：${e.zh}</p>`)
      .join("");
  }
}
```

`js/lektion-main.js`:
```javascript
import { ladeLektion } from "./app.js";
import { rendereTabs, rendereTabInhalt } from "./lektion.js";

const params = new URLSearchParams(location.search);
const nummer = Number(params.get("id")) || 1;
const lektion = await ladeLektion(nummer);

document.getElementById("lektion-titel").textContent =
  `第${lektion.nummer}課 — ${lektion.text[0]?.de ?? ""}`;

const inhaltEl = document.getElementById("tab-inhalt");
rendereTabs(lektion, document.getElementById("tabs"), (tabKey) =>
  rendereTabInhalt(lektion, tabKey, inhaltEl)
);
rendereTabInhalt(lektion, "text", inhaltEl);
```

- [ ] **Step 3: Im Browser prüfen**

Öffnen: `http://localhost:8000/lektion.html?id=1`
Erwartet: 4 Tab-Buttons, Standardansicht zeigt Dialogzeilen mit Audio-Player pro Zeile;
Klick auf Play spielt die extrahierte MP3 ab.

- [ ] **Step 4: Commit**

```bash
git add lektion.html js/lektion.js js/lektion-main.js
git commit -m "feat: render lesson page with 4 tabs and per-line audio playback"
```

---

## Phase C: Übungen

### Task 12: SRS-Algorithmus (vereinfachtes SM-2)

**Files:**
- Create: `js/srs.js`
- Test: `js/srs.test.js`

- [ ] **Step 1: Fehlschlagenden Test schreiben**

`js/srs.test.js`:
```javascript
import test from "node:test";
import assert from "node:assert/strict";
import { reviewCard, istFaellig } from "./srs.js";

test("erste korrekte Wiederholung setzt Intervall auf 1 Tag", () => {
  const karte = { interval: 0, repetitions: 0, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 2);
  assert.equal(ergebnis.interval, 1);
  assert.equal(ergebnis.repetitions, 1);
});

test("zweite korrekte Wiederholung setzt Intervall auf 6 Tage", () => {
  const karte = { interval: 1, repetitions: 1, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 2);
  assert.equal(ergebnis.interval, 6);
});

test("falsche Antwort setzt Wiederholungen zurueck", () => {
  const karte = { interval: 10, repetitions: 3, easeFactor: 2.5 };
  const ergebnis = reviewCard(karte, 0);
  assert.equal(ergebnis.repetitions, 0);
  assert.equal(ergebnis.interval, 1);
});

test("istFaellig erkennt ueberfaellige Karten", () => {
  assert.equal(istFaellig({ dueDate: "2020-01-01" }, "2026-01-01"), true);
  assert.equal(istFaellig({ dueDate: "2030-01-01" }, "2026-01-01"), false);
  assert.equal(istFaellig({}, "2026-01-01"), true);
});
```

- [ ] **Step 2: Test ausführen, Fehlschlag prüfen**

Run: `node --test js/srs.test.js`
Expected: FAIL — `js/srs.js` existiert nicht (Import-Fehler)

- [ ] **Step 3: Implementierung schreiben**

`js/srs.js`:
```javascript
export function reviewCard(karte, qualitaet) {
  let { interval, repetitions, easeFactor } = karte;
  if (qualitaet < 1) {
    repetitions = 0;
    interval = 1;
  } else {
    repetitions += 1;
    easeFactor = Math.max(
      1.3,
      easeFactor + (0.1 - (3 - qualitaet) * (0.08 + (3 - qualitaet) * 0.02))
    );
    if (repetitions === 1) interval = 1;
    else if (repetitions === 2) interval = 6;
    else interval = Math.round(interval * easeFactor);
  }
  const faellig = new Date();
  faellig.setDate(faellig.getDate() + interval);
  return {
    ...karte,
    interval,
    repetitions,
    easeFactor,
    dueDate: faellig.toISOString().slice(0, 10),
  };
}

export function istFaellig(karte, heute = new Date().toISOString().slice(0, 10)) {
  return !karte.dueDate || karte.dueDate <= heute;
}
```

- [ ] **Step 4: Test ausführen, Erfolg prüfen**

Run: `node --test js/srs.test.js`
Expected: PASS (4 Tests)

- [ ] **Step 5: Commit**

```bash
git add js/srs.js js/srs.test.js
git commit -m "feat: add simplified SM-2 spaced-repetition module with tests"
```

---

### Task 13: Karteikarten-UI

**Files:**
- Create: `js/karteikarten.js`
- Modify: `lektion.html` (Übungen-Tab ergänzen)
- Modify: `js/lektion.js` (5. Tab "Übungen" registrieren)

- [ ] **Step 1: Karteikarten-Logik schreiben**

`js/karteikarten.js`:
```javascript
import { reviewCard, istFaellig } from "./srs.js";

const SPEICHER_SCHLUESSEL = "karteikarten-status";

function ladeStatus() {
  try {
    return JSON.parse(localStorage.getItem(SPEICHER_SCHLUESSEL) || "{}");
  } catch {
    return {};
  }
}

function speichereStatus(status) {
  localStorage.setItem(SPEICHER_SCHLUESSEL, JSON.stringify(status));
}

export function faelligeVokabeln(vokabular, status) {
  return vokabular.filter((v) => {
    const karte = status[v.zh] ?? {};
    return istFaellig(karte);
  });
}

export function rendereKarteikarten(vokabular, container) {
  const status = ladeStatus();
  const faellig = faelligeVokabeln(vokabular, status);
  let index = 0;

  function zeigeKarte() {
    if (index >= faellig.length) {
      container.innerHTML = "<p>Für heute keine fälligen Karten mehr. 太好了!</p>";
      return;
    }
    const wort = faellig[index];
    container.innerHTML = `
      <div class="karteikarte">
        <p class="zh">${wort.zh}</p>
        <button id="aufdecken">Aufdecken</button>
        <div id="rueckseite" hidden>
          <p class="pinyin">${wort.zhuyin} · ${wort.pinyin}</p>
          <p class="de">${wort.de}</p>
          <div class="bewertung">
            <button data-q="0">Nochmal</button>
            <button data-q="1">Schwer</button>
            <button data-q="2">Gut</button>
            <button data-q="3">Leicht</button>
          </div>
        </div>
      </div>`;
    container.querySelector("#aufdecken").addEventListener("click", () => {
      container.querySelector("#rueckseite").hidden = false;
    });
    container.querySelectorAll(".bewertung button").forEach((btn) => {
      btn.addEventListener("click", () => {
        const qualitaet = Number(btn.dataset.q);
        const alteKarte = status[wort.zh] ?? { interval: 0, repetitions: 0, easeFactor: 2.5 };
        status[wort.zh] = reviewCard(alteKarte, qualitaet);
        speichereStatus(status);
        index += 1;
        zeigeKarte();
      });
    });
  }

  zeigeKarte();
}
```

- [ ] **Step 2: In `js/lektion.js` den Übungen-Tab ergänzen**

`TABS`-Array um Eintrag erweitern (nach `anwendung`):
```javascript
  { key: "uebungen", label: "Übungen" },
```

In `rendereTabInhalt` ergänzen (als weiterer `else if`-Zweig, importiert aus
`karteikarten.js`):
```javascript
  } else if (tabKey === "uebungen") {
    import("./karteikarten.js").then(({ rendereKarteikarten }) => {
      rendereKarteikarten(lektion.woerter, container);
    });
  }
```

- [ ] **Step 3: Im Browser prüfen**

Öffnen: `http://localhost:8000/lektion.html?id=1`, Tab "Übungen" klicken.
Erwartet: Karteikarte mit chinesischem Zeichen, "Aufdecken" zeigt Pinyin+Deutsch,
Bewertungsklick blättert zur nächsten fälligen Karte; Reload zeigt reduzierte Kartenzahl
(Status bleibt in localStorage erhalten).

- [ ] **Step 4: Commit**

```bash
git add js/karteikarten.js js/lektion.js
git commit -m "feat: add flashcard exercise using spaced-repetition module"
```

---

### Task 14: Satzbau (Drag & Drop)

**Files:**
- Create: `js/satzbau.js`
- Modify: `js/lektion.js` (Übungen-Tab um Satzbau ergänzen)

- [ ] **Step 1: Logik schreiben**

`js/satzbau.js`:
```javascript
function mische(array) {
  const kopie = [...array];
  for (let i = kopie.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [kopie[i], kopie[j]] = [kopie[j], kopie[i]];
  }
  return kopie;
}

export function zerlegeInZeichen(satz) {
  return satz.replace(/[，。？！]/g, "").split("");
}

export function rendereSatzbau(dialogZeilen, container) {
  const satzListe = dialogZeilen.filter((z) => z.zh.length >= 3);
  let index = 0;

  function zeigeAufgabe() {
    if (index >= satzListe.length) {
      container.innerHTML = "<p>Alle Sätze geschafft! 做得好!</p>";
      return;
    }
    const zielSatz = satzListe[index];
    const teile = mische(zerlegeInZeichen(zielSatz.zh));
    container.innerHTML = `
      <p class="de">${zielSatz.de ?? ""}</p>
      <div id="ziel" class="satzbau-ziel"></div>
      <div id="bausteine" class="satzbau-bausteine"></div>
      <button id="pruefen">Prüfen</button>
      <p id="ergebnis"></p>
    `;
    const zielEl = container.querySelector("#ziel");
    const bausteineEl = container.querySelector("#bausteine");
    teile.forEach((zeichen) => {
      const btn = document.createElement("button");
      btn.textContent = zeichen;
      btn.addEventListener("click", () => {
        zielEl.append(zeichen);
        btn.disabled = true;
      });
      bausteineEl.appendChild(btn);
    });
    container.querySelector("#pruefen").addEventListener("click", () => {
      const eingabe = zielEl.textContent;
      const korrekt = zerlegeInZeichen(zielSatz.zh).join("");
      container.querySelector("#ergebnis").textContent =
        eingabe === korrekt ? "Richtig! ✓" : `Nicht ganz — richtig wäre: ${zielSatz.zh}`;
    });
  }

  zeigeAufgabe();
  container.addEventListener("click", (e) => {
    if (e.target.id === "ergebnis-weiter") {
      index += 1;
      zeigeAufgabe();
    }
  });
}
```

- [ ] **Step 2: In `js/lektion.js` Übungen-Unterauswahl ergänzen**

Den `uebungen`-Zweig in `rendereTabInhalt` so erweitern, dass er ein kleines Untermenü
(Karteikarten / Satzbau / Hörverständnis / Aussprache) zeigt:
```javascript
  } else if (tabKey === "uebungen") {
    container.innerHTML = `
      <div class="uebungen-menu">
        <button data-uebung="karteikarten">Karteikarten</button>
        <button data-uebung="satzbau">Satzbau</button>
        <button data-uebung="hoerverstehen">Hörverständnis</button>
        <button data-uebung="aussprache">Aussprache</button>
      </div>
      <div id="uebung-inhalt"></div>
    `;
    const inhalt = container.querySelector("#uebung-inhalt");
    container.querySelectorAll("[data-uebung]").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const modul = btn.dataset.uebung;
        if (modul === "karteikarten") {
          const { rendereKarteikarten } = await import("./karteikarten.js");
          rendereKarteikarten(lektion.woerter, inhalt);
        } else if (modul === "satzbau") {
          const { rendereSatzbau } = await import("./satzbau.js");
          rendereSatzbau(lektion.text, inhalt);
        } else if (modul === "hoerverstehen") {
          const { rendereHoerverstehen } = await import("./hoerverstehen.js");
          rendereHoerverstehen(lektion.text, inhalt);
        } else if (modul === "aussprache") {
          const { rendereAussprache } = await import("./aussprache.js");
          rendereAussprache(lektion.text, inhalt);
        }
      });
    });
  }
```

(Dies ersetzt den einfachen Direkt-Aufruf aus Task 13 — die Karteikarten-Bewertungslogik
selbst bleibt unverändert in `karteikarten.js`.)

- [ ] **Step 3: Im Browser prüfen**

Tab "Übungen" → "Satzbau": Zeichen-Buttons in zufälliger Reihenfolge, Klicks bauen den
Satz zusammen, "Prüfen" zeigt richtig/falsch.

- [ ] **Step 4: Commit**

```bash
git add js/satzbau.js js/lektion.js
git commit -m "feat: add drag-free tap-to-build sentence construction exercise"
```

---

### Task 15: Hörverständnis-Quiz

**Files:**
- Create: `js/hoerverstehen.js`

- [ ] **Step 1: Logik schreiben**

`js/hoerverstehen.js`:
```javascript
function mische(array) {
  return [...array].sort(() => Math.random() - 0.5);
}

export function erzeugeOptionen(zielZeile, alleZeilen, anzahl = 4) {
  const andere = alleZeilen.filter((z) => z !== zielZeile);
  const ablenkerAnzahl = Math.min(anzahl - 1, andere.length);
  const ablenker = mische(andere).slice(0, ablenkerAnzahl);
  return mische([zielZeile, ...ablenker]);
}

export function rendereHoerverstehen(dialogZeilen, container) {
  const zeilen = dialogZeilen.filter((z) => z.audio && z.de);
  let index = 0;

  function zeigeFrage() {
    if (index >= zeilen.length) {
      container.innerHTML = "<p>Quiz beendet!</p>";
      return;
    }
    const ziel = zeilen[index];
    const optionen = erzeugeOptionen(ziel, zeilen);
    container.innerHTML = `
      <audio controls autoplay src="${ziel.audio}"></audio>
      <p>Welche Übersetzung passt?</p>
      <ul class="quiz-optionen">
        ${optionen.map((o, i) => `<li><button data-i="${i}">${o.de}</button></li>`).join("")}
      </ul>
      <p id="ergebnis"></p>
    `;
    container.querySelectorAll("[data-i]").forEach((btn, i) => {
      btn.addEventListener("click", () => {
        const richtig = optionen[i] === ziel;
        container.querySelector("#ergebnis").textContent = richtig
          ? "Richtig! ✓"
          : `Falsch — richtig: ${ziel.de}`;
        setTimeout(() => {
          index += 1;
          zeigeFrage();
        }, 1200);
      });
    });
  }

  zeigeFrage();
}
```

- [ ] **Step 2: Im Browser prüfen**

Tab "Übungen" → "Hörverständnis": Audio spielt automatisch, 4 Antwortoptionen erscheinen,
Klick zeigt Feedback und lädt nach 1,2s die nächste Frage.

- [ ] **Step 3: Commit**

```bash
git add js/hoerverstehen.js
git commit -m "feat: add listening comprehension quiz using original audio"
```

---

### Task 16: Ausspracheübung (Web Speech API)

**Files:**
- Create: `js/aussprache.js`

- [ ] **Step 1: Logik schreiben**

`js/aussprache.js`:
```javascript
function aehnlichkeit(a, b) {
  const laenge = Math.max(a.length, b.length);
  if (laenge === 0) return 1;
  let treffer = 0;
  for (let i = 0; i < Math.min(a.length, b.length); i++) {
    if (a[i] === b[i]) treffer += 1;
  }
  return treffer / laenge;
}

export function bewerteAussprache(erkannterText, zielText) {
  const score = aehnlichkeit(erkannterText.trim(), zielText.trim());
  if (score > 0.8) return { label: "Sehr gut!", score };
  if (score > 0.5) return { label: "Geht in die richtige Richtung.", score };
  return { label: "Nochmal versuchen.", score };
}

export function rendereAussprache(dialogZeilen, container) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const zeilen = dialogZeilen.filter((z) => z.zh);
  let index = 0;

  function zeigeSatz() {
    if (index >= zeilen.length) {
      container.innerHTML = "<p>Ausspracheübung beendet!</p>";
      return;
    }
    const ziel = zeilen[index];
    container.innerHTML = `
      <p class="zh">${ziel.zh}</p>
      ${ziel.audio ? `<audio controls src="${ziel.audio}"></audio>` : ""}
      <button id="aufnehmen" ${SpeechRecognition ? "" : "disabled"}>🎤 Sprechen</button>
      ${SpeechRecognition ? "" : `<p class="hinweis">Aussprache-Erkennung wird von diesem
        Browser nicht unterstützt — funktioniert zuverlässig nur in Chrome oder Edge.</p>`}
      <p id="ergebnis"></p>
      <button id="weiter">Nächster Satz</button>
    `;
    if (SpeechRecognition) {
      container.querySelector("#aufnehmen").addEventListener("click", () => {
        const erkennung = new SpeechRecognition();
        erkennung.lang = "zh-TW";
        erkennung.onresult = (event) => {
          const erkannterText = event.results[0][0].transcript;
          const bewertung = bewerteAussprache(erkannterText, ziel.zh);
          container.querySelector("#ergebnis").textContent =
            `Erkannt: "${erkannterText}" — ${bewertung.label}`;
        };
        erkennung.onerror = () => {
          container.querySelector("#ergebnis").textContent =
            "Aufnahme fehlgeschlagen — Mikrofon-Zugriff erlaubt?";
        };
        erkennung.start();
      });
    }
    container.querySelector("#weiter").addEventListener("click", () => {
      index += 1;
      zeigeSatz();
    });
  }

  zeigeSatz();
}
```

- [ ] **Step 2: Im Browser prüfen (Chrome/Edge)**

Tab "Übungen" → "Aussprache": Mikrofon-Button fragt Berechtigung ab, gesprochener Satz
wird erkannt und grob bewertet. In Firefox: Button ist deaktiviert, Hinweistext sichtbar
statt stillem Fehler.

- [ ] **Step 3: Commit**

```bash
git add js/aussprache.js
git commit -m "feat: add pronunciation practice via Web Speech API with graceful fallback"
```

---

## Phase D: Fortschritt & Persistenz

### Task 17: Export/Import des Lernfortschritts

**Files:**
- Create: `js/fortschritt.js`
- Modify: `index.html` (Export/Import-Buttons ergänzen)
- Modify: `js/main.js`

- [ ] **Step 1: Logik schreiben**

`js/fortschritt.js`:
```javascript
const RELEVANTE_SCHLUESSEL = ["karteikarten-status", "fortschritt"];

export function exportiereFortschritt() {
  const daten = {};
  for (const schluessel of RELEVANTE_SCHLUESSEL) {
    const wert = localStorage.getItem(schluessel);
    if (wert) daten[schluessel] = JSON.parse(wert);
  }
  const blob = new Blob([JSON.stringify(daten, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  const heute = new Date().toISOString().slice(0, 10);
  a.href = url;
  a.download = `fortschritt-${heute}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function importiereFortschritt(datei) {
  const text = await datei.text();
  const daten = JSON.parse(text);
  for (const schluessel of RELEVANTE_SCHLUESSEL) {
    if (daten[schluessel]) {
      localStorage.setItem(schluessel, JSON.stringify(daten[schluessel]));
    }
  }
}
```

- [ ] **Step 2: Buttons in `index.html` ergänzen**

In `<header class="kopf">` nach der Überschrift einfügen:
```html
    <div class="fortschritt-aktionen">
      <button id="export-btn">Fortschritt exportieren</button>
      <label class="datei-label">
        Fortschritt importieren
        <input type="file" id="import-input" accept="application/json" hidden />
      </label>
    </div>
```

- [ ] **Step 3: In `js/main.js` verdrahten**

Anhängen:
```javascript
import { exportiereFortschritt, importiereFortschritt } from "./fortschritt.js";

document.getElementById("export-btn").addEventListener("click", exportiereFortschritt);
document.getElementById("import-input").addEventListener("change", async (e) => {
  const datei = e.target.files[0];
  if (!datei) return;
  if (!confirm("Aktuellen Fortschritt mit der importierten Datei überschreiben?")) return;
  await importiereFortschritt(datei);
  location.reload();
});
```

- [ ] **Step 4: Im Browser prüfen**

Export klicken → Datei `fortschritt-YYYY-MM-DD.json` wird heruntergeladen und enthält
den aktuellen `karteikarten-status`. Datei über Import-Feld erneut einlesen → Bestätigungsdialog
→ Seite lädt neu, Fortschritt bleibt identisch.

- [ ] **Step 5: Commit**

```bash
git add js/fortschritt.js index.html js/main.js
git commit -m "feat: add progress export/import as downloadable JSON file"
```

---

## Phase E: Deployment

### Task 18: GitHub-Repo erstellen und GitHub Pages aktivieren

**Files:** keine Code-Änderungen, nur Anleitung + finaler Push

- [ ] **Step 1: Alles committen, was noch offen ist**

Run: `git status`
Falls Änderungen vorhanden: committen (siehe vorherige Tasks für Commit-Stil).

- [ ] **Step 2: GitHub-Repo erstellen (Nutzer-Aktion, ich leite an)**

Anleitung für den Nutzer:
1. Auf github.com einloggen, oben rechts "+" → "New repository"
2. Name z.B. `chinesisch-lern-app`, Sichtbarkeit nach Wunsch (öffentlich nötig für
   GitHub Pages im kostenlosen Plan ohne Pro-Account), **kein** README/​.gitignore
   beim Erstellen anhaken (haben wir schon lokal)
3. "Create repository" klicken, die angezeigte Remote-URL kopieren
   (z.B. `https://github.com/<user>/chinesisch-lern-app.git`)

- [ ] **Step 3: Remote verbinden und pushen**

Run (Platzhalter `<url>` durch die kopierte Remote-URL ersetzen):
```bash
git remote add origin <url>
git branch -M main
git push -u origin main
```
Expected: Push erfolgreich, Repo auf GitHub zeigt alle Dateien inkl. `data/` und `audio/`.

- [ ] **Step 4: GitHub Pages aktivieren (Nutzer-Aktion, ich leite an)**

Anleitung für den Nutzer:
1. Im Repo auf GitHub: "Settings" → "Pages" (linke Seitenleiste)
2. Unter "Build and deployment" → "Source": "Deploy from a branch"
3. Branch: `main`, Ordner: `/ (root)` → "Save"
4. Nach 1-2 Minuten ist die Seite erreichbar unter
   `https://<user>.github.io/chinesisch-lern-app/`

- [ ] **Step 5: Live-Version verifizieren**

Die veröffentlichte URL öffnen, Startseite + eine Lektion inkl. Audio-Wiedergabe prüfen.

---

## Selbstprüfung (bereits durchgeführt)

- **Spec-Abdeckung:** Alle Abschnitte aus dem Design-Dokument sind abgedeckt: Datenextraktion
  (Tasks 1-8), Frontend-Kern (Tasks 9-11), alle 4 Übungstypen (Tasks 12-16), Fortschritt/Export
  (Task 17), Deployment (Task 18).
- **Abweichung vom Design-Dokument dokumentiert:** `zhuyin` existiert nur bei Vokabeleinträgen,
  nicht bei Dialogzeilen (siehe "Bereits verifizierte Fakten" oben) — echte Einschränkung der
  Quelldaten, keine Vereinfachung.
- **Kein Platzhalter:** Jeder Code-Schritt enthält vollständigen, lauffähigen Code; die einzigen
  manuellen Schritte (Task 8/Step 8, Task 18) sind explizit als Nutzer- bzw.
  Kontroll-Aktionen benannt, nicht als vage "TODO".
- **Typkonsistenz geprüft:** `lektion.woerter[].zhuyin/pinyin/de`, `lektion.text[].sprecher/zh/
  pinyin/de/audio` und `lektion.wiederholung[].sprecher/zh` werden in Tasks 8-16 konsistent
  verwendet.
