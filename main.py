import customtkinter as ctk
import json
import os
import shutil

CARDS_FILE = "cards.json"
PROGRESS_FILE = "progress.json"
DEFAULT_FILE = "default_cards.json"

# --- Модуль Repository (Загрузка данных) ---
def load_cards():
    # Защита от сбоя: если файла нет, копируем дефолтный
    if not os.path.exists(CARDS_FILE):
        shutil.copy(DEFAULT_FILE, CARDS_FILE)
    
    try:
        with open(CARDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Если файл битый, загружаем дефолт
        with open(DEFAULT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"known": [], "unknown": []}

def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f)

# --- Интерфейс ---
class FlashCardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Флеш-карточки")
        self.geometry("400x500")
        
        self.cards = load_cards()
        self.progress = load_progress()
        self.current_index = 0
        self.showing_answer = False
        
        # Экран 1: Список тем (упрощенно - просто список всех карточек)
        self.frame_list = ctk.CTkFrame(self)
        self.frame_list.pack(fill="both", expand=True)
        
        ctk.CTkLabel(self.frame_list, text="Выберите карточку:", font=("Arial", 20)).pack(pady=20)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self.frame_list, width=300, height=350)
        self.scroll_frame.pack(pady=10)
        
        self.render_card_list()

        # Экран 2: Сама карточка (по умолчанию скрыт)
        self.frame_card = ctk.CTkFrame(self)
        
        self.lbl_counter = ctk.CTkLabel(self.frame_card, text="", font=("Arial", 12))
        self.lbl_counter.pack(pady=10)
        
        self.btn_card = ctk.CTkButton(self.frame_card, text="Вопрос", width=300, height=200, 
                                      font=("Arial", 20), fg_color="#2b2b2b", hover_color="#3b3b3b",
                                      command=self.flip_card)
        self.btn_card.pack(pady=20)
        
        frame_btns = ctk.CTkFrame(self.frame_card)
        frame_btns.pack(pady=10)
        
        self.btn_known = ctk.CTkButton(frame_btns, text="Знаю", fg_color="green", width=120, command=lambda: self.answer_card(True))
        self.btn_known.pack(side="left", padx=10)
        
        self.btn_unknown = ctk.CTkButton(frame_btns, text="Не знаю", fg_color="red", width=120, command=lambda: self.answer_card(False))
        self.btn_unknown.pack(side="left", padx=10)
        
        ctk.CTkButton(self.frame_card, text="Назад", fg_color="gray", command=self.back_to_list).pack(pady=20)

    def render_card_list(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        for i, card in enumerate(self.cards):
            status = "✅" if card["id"] in self.progress["known"] else ("❌" if card["id"] in self.progress["unknown"] else "⚪")
            btn = ctk.CTkButton(self.scroll_frame, text=f"{status} {card['question']}", 
                                command=lambda idx=i: self.open_card(idx))
            btn.pack(pady=5, fill="x")

    def open_card(self, index):
        self.current_index = index
        self.showing_answer = False
        self.frame_list.pack_forget()
        self.frame_card.pack(fill="both", expand=True)
        self.update_card_view()

    def update_card_view(self):
        card = self.cards[self.current_index]
        self.lbl_counter.configure(text=f"Карточка {self.current_index + 1} из {len(self.cards)}")
        if self.showing_answer:
            self.btn_card.configure(text=card["answer"], fg_color="#005a9e")
        else:
            self.btn_card.configure(text=card["question"], fg_color="#2b2b2b")

    def flip_card(self):
        self.showing_answer = not self.showing_answer
        self.update_card_view()

    def answer_card(self, known):
        card_id = self.cards[self.current_index]["id"]
        
        # Обновляем прогресс
        if known:
            if card_id in self.progress["unknown"]:
                self.progress["unknown"].remove(card_id)
            if card_id not in self.progress["known"]:
                self.progress["known"].append(card_id)
        else:
            if card_id in self.progress["known"]:
                self.progress["known"].remove(card_id)
            if card_id not in self.progress["unknown"]:
                self.progress["unknown"].append(card_id)
                
        save_progress(self.progress)
        self.back_to_list()

    def back_to_list(self):
        self.frame_card.pack_forget()
        self.frame_list.pack(fill="both", expand=True)
        self.render_card_list()

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = FlashCardApp()
    app.mainloop()