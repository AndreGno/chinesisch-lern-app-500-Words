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
