from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox
from PyQt6.QtCore import QTimer, QDateTime
from plyer import notification
import json
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class NotesBackend:
    def __init__(self, filename="notes.json", tags_file="tags.json"):
        self.filename = resource_path(filename)
        self.tags_file = resource_path(tags_file)
        self.notes = self.load_notes()
        self.tags = self.load_tags()

    def load_notes(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                data = json.load(file)
                if all(isinstance(note, str) for note in data):
                    return [{"title": "", "content": note, "tags": ""} for note in data]
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_notes(self):
        with open(self.filename, "w", encoding="utf-8") as file:
            json.dump(self.notes, file, indent=4, ensure_ascii=False)

    def get_notes(self):
        return [note["content"] for note in self.notes] if self.notes else []

    def get_note_title(self, index):
        return self.notes[index]["title"] if 0 <= index < len(self.notes) else ""

    def get_note_tags(self, index):
        return self.notes[index]["tags"] if 0 <= index < len(self.notes) else ""

    def add_note(self):
        self.notes.append({
            "title": "",
            "content": "Нова нотатка",
            "tags": ""
        })
        self.save_notes()

    def update_note(self, index, content, title=None, tags=None):
        if 0 <= index < len(self.notes):
            self.notes[index]["content"] = content
            if title is not None:
                self.notes[index]["title"] = title
            if tags is not None:
                self.notes[index]["tags"] = tags
            self.save_notes()

    def load_tags(self):
        try:
            with open(self.tags_file, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list) and all("name" in tag and "color" in tag for tag in data):
                    return {tag["name"]: tag["color"] for tag in data}
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return {
            "запис": "#cccccc",
            "важливо": "#ff9999",
            "ідея": "#99ff99",
            "робота": "#9999ff",
            "особисте": "#ffcc99"
        }

    def save_tags(self):
        with open(self.tags_file, "w", encoding="utf-8") as file:
            json.dump(
                [{"name": name, "color": color} for name, color in self.tags.items()],
                file, ensure_ascii=False, indent=4
            )

    def get_tags(self):
        return self.tags 
    
    def get_tag_colors(self):
        return self.tags

    def add_tag(self, name, color="#cccccc"):
        if name not in self.tags:
            self.tags[name] = color
            self.save_tags()

    def save_to_clipboard(self, text: str):
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            print("Текст успішно скопійовано до буфера обміну")
        except Exception as e:
            print(f"Помилка при копіюванні до буфера обміну: {e}")

    def save_to_file(self, text: str, parent=None):
        try:
            file_path, _ = QFileDialog.getSaveFileName(parent, "Зберегти нотатку", "", "Текстові файли (*.txt);;Усі файли (*)")
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Файл успішно збережено: {file_path}")
        except Exception as e:
            print(f"Помилка збереження файлу: {e}")


REMINDERS_FILE = resource_path("reminders.json")

class ReminderManager:
    def __init__(self, parent):
        self.parent = parent
        self.timers = []
        self.load_saved_reminders()

    def set_reminder(self, note_text: str, target_datetime: QDateTime):
        if QDateTime.currentDateTime() >= target_datetime:
            self._notify(note_text)
        else:
            self._save_reminder(note_text, target_datetime)
            self._schedule_timer(note_text, target_datetime)

    def _schedule_timer(self, note_text: str, target_datetime: QDateTime):
        current = QDateTime.currentDateTime()
        msecs_to_target = current.msecsTo(target_datetime)
        
        if msecs_to_target > 0:
            timer = QTimer()
            timer.setSingleShot(True)
            timer.setInterval(msecs_to_target)
            timer.timeout.connect(lambda: self._notify(note_text))
            timer.start()
            self.timers.append(timer)

    def _notify(self, note_text: str):
        try:
            notification.notify(
                title="Нагадування",
                message=note_text[:100] + "..." if len(note_text) > 100 else note_text,
                app_name="Нотатки",
                timeout=10
            )
            self._remove_reminder(note_text)
            if self.parent.reminders_widget and self.parent.reminders_widget.isVisible():
                self.parent.reminders_widget.update_reminders()
        except Exception as e:
            print(f"Помилка при відправці повідомлення: {e}")

    def _remove_reminder(self, note_text: str):
        try:
            data = self._load_all_reminders()
            data = [r for r in data if r["text"] != note_text]
            with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Помилка при видаленні нагадування: {e}")

    def _save_reminder(self, note_text: str, dt: QDateTime):
        data = self._load_all_reminders()
        data.append({
            "text": note_text,
            "datetime": dt.toString("yyyy-MM-ddTHH:mm:ss")
        })
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_saved_reminders(self):
        data = self._load_all_reminders()
        current = QDateTime.currentDateTime()
        
        for reminder in data:
            try:
                dt = QDateTime.fromString(reminder["datetime"], "yyyy-MM-ddTHH:mm:ss")
                if current < dt:
                    self._schedule_timer(reminder["text"], dt)
            except Exception as e:
                print(f"Помилка при завантаженні нагадування: {e}")

    def _load_all_reminders(self):
        if os.path.exists(REMINDERS_FILE):
            try:
                with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []
