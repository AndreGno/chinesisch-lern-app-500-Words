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
