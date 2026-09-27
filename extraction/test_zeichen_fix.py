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
