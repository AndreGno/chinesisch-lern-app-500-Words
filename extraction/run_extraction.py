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
    print(f"vokabular.json geschrieben ({len(all_vokabeln)} Einträge gesamt).")


if __name__ == "__main__":
    main()
