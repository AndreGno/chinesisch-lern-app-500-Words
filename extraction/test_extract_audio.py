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
