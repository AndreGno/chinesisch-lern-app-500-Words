"""Ersetzt kaputte Font-Codepoints (Ideographic Annotation / Parenthesized/Circled
Ideograph) durch die eigentlich gemeinten CJK-Unified-Ideographs. Siehe Design-Dokument
und Plan-Kopf fuer die verifizierte Herleitung jedes Eintrags."""

BROKEN_CHAR_MAP = {
    "㆗": "中", "㆒": "一", "㆙": "甲", "㆚": "乙",
    "㈲": "有", "㈻": "學", "㈤": "五", "㆖": "上",
    "㆝": "天", "㈩": "十", "㆟": "人", "㆓": "二",
    "㆘": "下", "㆔": "三", "㈥": "六", "㊢": "寫",
    "㊛": "女", "㈪": "月", "㊚": "男", "㆕": "四",
    "㈧": "八", "㈴": "名", "㆞": "地", "㈰": "日",
    "㈦": "七", "㈨": "九", "㈬": "水", "㊧": "左",
    "㊨": "右", "㆛": "丙", "㉂": "自", "㊩": "醫",
}


def fix_text(text: str) -> str:
    for broken, correct in BROKEN_CHAR_MAP.items():
        text = text.replace(broken, correct)
    return text
