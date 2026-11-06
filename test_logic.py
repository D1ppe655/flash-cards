import pytest
import os
from main import load_cards, load_progress, save_progress

def test_load_cards_default():
    # Если файл cards.json отсутствует, должна загрузиться база
    if os.path.exists("cards.json"):
        os.remove("cards.json")
    cards = load_cards()
    assert len(cards) == 5
    assert "question" in cards[0]

def test_progress_save(tmp_path):
    # Проверка сохранения прогресса
    progress = {"known": [1, 2], "unknown": [3]}
    save_progress(progress)
    loaded = load_progress()
    assert loaded["known"] == [1, 2]
    assert loaded["unknown"] == [3]