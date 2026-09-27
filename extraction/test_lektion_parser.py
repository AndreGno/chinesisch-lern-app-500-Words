from fixtures.lektion_01_raw import PAGES
from fixtures.lektion_16_multipage_raw import PAGES as MULTIPAGE_PAGES
from lektion_parser import (
    parse_dialogue,
    parse_vokabular,
    parse_wiederholung,
    split_into_buckets,
)


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


def test_multipage_section_keeps_unmarked_continuation_pages():
    buckets = split_into_buckets(MULTIPAGE_PAGES)
    joined = "\n".join(buckets[16]["字與詞"])
    # Seiten 113-115 tragen keinen Marker, gehoeren aber noch zu 字與詞
    # (der Marker fuer diesen Abschnitt stand bereits auf Seite 112).
    assert "文具" in joined
    assert "公司" in joined
    assert "紙（ㄓˇ；zhǐ）das Papier" in joined


def test_multipage_section_does_not_leak_into_wrong_bucket():
    buckets = split_into_buckets(MULTIPAGE_PAGES)
    joined = "\n".join(buckets[16]["溫習"])
    # "工具"/"硯台" kommen nur in den unmarkierten 字與詞-Folgeseiten vor, nicht
    # im eigentlichen 溫習-Wiederholungsdialog von Seite 116.
    assert "工具" not in joined
    assert "硯台" not in joined


def test_table_of_contents_headers_without_marker_do_not_advance_lesson():
    # Das Inhaltsverzeichnis listet "第一課".."第三十課" ohne Abschnittsmarker
    # auf. Ein Header allein (ohne Marker auf derselben Seite) darf die
    # Lektionsnummer nicht vorspulen, sonst landet der gesamte Lektion-1-Inhalt
    # faelschlich in einem viel spaeteren Lektions-Bucket.
    pages = [
        "目錄 INHALT\n第一課 您早… 1\n第二課 您好嗎？… 7\n",
        "第十六課 到那裡去買？… 105\n第三十課 …… 212\n",
        "㆙：您早。\nnín zǎo\nGuten Morgen!\n第㆒課\n Lektion 1\n 一    課文  TEXT\n",
    ]
    buckets = split_into_buckets(pages)
    assert set(buckets.keys()) == {1}
    assert "Guten Morgen!" not in "\n".join(buckets.get(16, {}).get("課文", []))


def test_lesson_number_regression_stops_forward_fill():
    # Simuliert den Anhang (Seiten 227-236): kein Marker mehr vorhanden, aber
    # die Kopfzeile zaehlt die Lektionsnummer wieder von vorne hoch. Sobald die
    # erkannte Lektionsnummer sinkt, darf nicht mehr in den zuletzt offenen
    # Abschnitt (hier: Lektion 2, 應用) weitergeschrieben werden.
    pages = [
        "第㆓課\n㆙：你好。\nHallo!\n 四    應用  ANWENDUNG\n",
        "第㆒課\n生難字表\n王\n李\n先\n生\n",
    ]
    buckets = split_into_buckets(pages)
    joined = "\n".join(buckets[2]["應用"])
    assert "生難字表" not in joined
    assert "王" not in joined


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


def test_parse_dialogue_handles_bare_translation_with_no_speaker_prefix():
    lines = [
        "㆙：這是什麼？",
        "zhè shì shé me",
        "Was ist das?",
    ]
    result = parse_dialogue(lines)
    assert result == [
        {
            "sprecher": "㆙",
            "zh": "這是什麼？",
            "pinyin": "zhè shì shé me",
            "de": "Was ist das?",
        }
    ]


def test_parse_dialogue_does_not_treat_adjacent_speaker_line_as_translation():
    lines = [
        "乙：這種筆一枝五百塊。",
        "甲：五百塊？太貴了。",
        "㆙：不好看沒關係。",
        "pinyin fuer nicht gut aussehend",
        "Macht nichts, wenn es nicht schön aussieht.",
    ]
    result = parse_dialogue(lines)
    assert result == [
        {
            "sprecher": "㆙",
            "zh": "不好看沒關係。",
            "pinyin": "pinyin fuer nicht gut aussehend",
            "de": "Macht nichts, wenn es nicht schön aussieht.",
        }
    ]


def test_parse_dialogue_handles_translation_without_space_before_colon():
    lines = [
        "王先生：我很好，謝謝您。",
        "Wáng xiān shēng wǒ hěn hǎo xiè xie nín",
        "Herr Wang: Es geht mir gut, danke schön!",
    ]
    result = parse_dialogue(lines)
    assert result == [
        {
            "sprecher": "王先生",
            "zh": "我很好，謝謝您。",
            "pinyin": "Wáng xiān shēng wǒ hěn hǎo xiè xie nín",
            "de": "Es geht mir gut, danke schön!",
        }
    ]


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


def test_parse_vokabular_skips_additional_pronunciation_blocks():
    lines = ["什麼（ㄕㄜˊ ・ㄇㄜ；shé me）（ㄕㄣˊ ・ㄇㄜ；shén me）was"]
    result = parse_vokabular(lines)
    assert result == [
        {
            "zh": "什麼",
            "zhuyin": "ㄕㄜˊ ・ㄇㄜ",
            "pinyin": "shé me",
            "de": "was",
        }
    ]


def test_parse_vokabular_skips_additional_pronunciation_block_with_space():
    lines = ["個（ㄍㄜˋ；gè） （・ㄍㄜ；ge）das Stück (Zählwort)"]
    result = parse_vokabular(lines)
    assert result == [
        {
            "zh": "個",
            "zhuyin": "ㄍㄜˋ",
            "pinyin": "gè",
            "de": "das Stück (Zählwort)",
        }
    ]


def test_parse_wiederholung_extracts_speaker_and_zh_only():
    lines = ["王先生：李太太，您早。", "李太太：早，王先生，您早。"]
    result = parse_wiederholung(lines)
    assert result == [
        {"sprecher": "王先生", "zh": "李太太，您早。"},
        {"sprecher": "李太太", "zh": "早，王先生，您早。"},
    ]
