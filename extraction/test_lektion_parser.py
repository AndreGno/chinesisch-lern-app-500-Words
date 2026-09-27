from fixtures.lektion_01_raw import PAGES
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


def test_parse_wiederholung_extracts_speaker_and_zh_only():
    lines = ["王先生：李太太，您早。", "李太太：早，王先生，您早。"]
    result = parse_wiederholung(lines)
    assert result == [
        {"sprecher": "王先生", "zh": "李太太，您早。"},
        {"sprecher": "李太太", "zh": "早，王先生，您早。"},
    ]
