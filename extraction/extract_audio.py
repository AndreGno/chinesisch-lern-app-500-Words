"""Extrahiert alle im PDF eingebetteten MP3-Dateien (echte Sound-Streams, referenziert
über Filespec-Objekte mit /F <name>.mp3 und /EF <</F <stream_xref> 0 R>>)."""
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
