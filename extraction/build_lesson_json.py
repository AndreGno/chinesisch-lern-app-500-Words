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
