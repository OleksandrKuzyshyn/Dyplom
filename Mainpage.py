from PyQt6.QtWidgets import (
    QWidget, QPushButton, QTextEdit, QVBoxLayout, QGridLayout, QGraphicsDropShadowEffect, QDateEdit, QDateEdit, QTimeEdit,
    QLabel, QSpacerItem, QSizePolicy, QMenu, QLineEdit, QDialog, QHBoxLayout, QFrame, 
    QGraphicsOpacityEffect, QApplication, QFileDialog, QScrollArea, QWidgetAction
)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QPoint, QRect, QMimeData, QAbstractItemModel, QItemSelectionModel, QSortFilterProxyModel, QDate, QTime, QDateTime, pyqtSignal, QTimer
from PyQt6.QtGui import QDrag, QMouseEvent, QIcon, QColor, QAction
from back import NotesBackend, ReminderManager
from styles import Styles
import sys
import os

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainPage(QWidget):
    def __init__(self, backend):
        super().__init__()
        self.backend = backend
        self.is_dark_mode = False 

        self.reminder_manager = ReminderManager(self)
        self.reminder_manager.load_saved_reminders()

        self.setAcceptDrops(True)

        self.note_buttons = []
        self.expanded_notes = {}
        self.highlighted_index = None
        self.ignore_resize = False
        
        
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.handle_resize_timeout)
        self.resize_delay = 150
        
        self.button_position_timer = QTimer()
        self.button_position_timer.setSingleShot(True)
        self.button_position_timer.timeout.connect(self.delayed_button_position_update)
        self.button_position_delay = 50
        
        self.pending_size = None
        self.last_window_size = None

        self.setStyleSheet(Styles.get_main_style(self.is_dark_mode))

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet(Styles.get_scroll_area_style(self.is_dark_mode))
        self.scroll_area.viewport().setStyleSheet(Styles.get_scroll_area_viewport_style(self.is_dark_mode))
        self.scroll_area.verticalScrollBar().setStyleSheet(Styles.get_scrollbar_style(self.is_dark_mode))

        self.notes_container = QWidget()
        self.notes_container.setStyleSheet(Styles.get_notes_container_style(self.is_dark_mode))
        self.notes_layout = QGridLayout(self.notes_container)
        self.notes_layout.setSpacing(50)
        self.notes_layout.setContentsMargins(20, 20, 20, 20)
        self.notes_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        self.scroll_area.setWidget(self.notes_container)
        self.main_layout.addWidget(self.scroll_area)

        self.add_button = QPushButton(self)
        self.add_button.setIcon(QIcon(resource_path("add.png")))
        self.add_button.setIconSize(QSize(32, 32))
        self.add_button.clicked.connect(self.add_new_note)
        self.add_button.setStyleSheet(Styles.get_floating_add_button_style(self.is_dark_mode))
        self.add_button.setFixedSize(60, 60)
        self.add_button.hide()

        QTimer.singleShot(100, self.initial_setup)
        
        self.update_screen_style()
        self.load_notes()

    def initial_setup(self):
        self.add_button.show()
        self._update_button_position()
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.update_add_button_position)

    def update_screen_style(self):
        width = self.width()
        if width < 800:
            self.current_style = Styles.SCREEN_STYLES['small']
        elif width < 1200:
            self.current_style = Styles.SCREEN_STYLES['medium']
        else:
            self.current_style = Styles.SCREEN_STYLES['large']
        self.notes_layout.setSpacing(int(self.current_style['spacing'].replace('px', '')))
        note_width, note_height = self.current_style['note_size']
        self.add_button.setFixedSize(note_width * 2, note_height // 2)
        self.add_button.setStyleSheet(Styles.get_floating_add_button_style(self.is_dark_mode))

    def load_notes(self):
        self.arrange_notes(self.backend.get_notes())
        self.scroll_area.setStyleSheet(Styles.get_scroll_area_style(self.is_dark_mode))

    def arrange_notes(self, notes_or_indices):
        if self.ignore_resize:
            return
        expanded_indices = list(self.expanded_notes.keys())
        for i in reversed(range(self.notes_layout.count())):
            widget = self.notes_layout.itemAt(i).widget()
            if widget and not any(widget == note for note in self.expanded_notes.values()):
                widget.setParent(None)
        self.note_buttons = []
        notes = self.backend.get_notes()
        if not notes_or_indices:
            notes_or_indices = range(len(notes))
        viewport_width = self.scroll_area.viewport().width()
        total_width = viewport_width - 40
        note_width, _ = self.current_style['note_size']
        min_spacing = 20
        max_columns = max(1, int((total_width + min_spacing) / (note_width + min_spacing)))
        if max_columns > 1:
            available_space = total_width - (max_columns * note_width)
            spacing = available_space // (max_columns - 1)
            spacing = max(min_spacing, min(spacing, 60))
        else:
            spacing = min_spacing
        self.notes_layout.setSpacing(spacing)
        self.notes_layout.setContentsMargins(20, 20, 20, 20)
        for display_idx, value in enumerate(notes_or_indices):
            real_note_index = value if isinstance(value, int) else display_idx
            if real_note_index in expanded_indices:
                continue
            note_btn = DraggableNoteButton(real_note_index, on_click_callback=self.handle_note_click)
            note_width, note_height = self.current_style['note_size']
            note_btn.setFixedSize(note_width, note_height)
            note_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            note_btn.customContextMenuRequested.connect(
                self.make_context_menu_handler(note_btn, real_note_index))
            note_btn.setStyleSheet(Styles.get_note_wrapper_style(self.is_dark_mode))
            content_container = QWidget()
            content_layout = QVBoxLayout(content_container)
            content_layout.setSpacing(5)
            padding = int(self.current_style['button_padding'].replace('px', ''))
            content_layout.setContentsMargins(padding, padding, padding, padding)
            title = self.backend.get_note_title(real_note_index)
            content = notes[real_note_index]
            tags = self.backend.get_note_tags(real_note_index)
            title_label = QLabel(f"<b>{title or 'Без назви'}</b>")
            title_label.setWordWrap(True)
            title_label.setStyleSheet(Styles.get_note_title_label_style(self.is_dark_mode, self.current_style['note_font']))
            content_layout.addWidget(title_label)
            content_label = QLabel(content[:60] + "..." if len(content) > 60 else content)
            content_label.setWordWrap(True)
            content_label.setStyleSheet(Styles.get_note_content_label_style(self.is_dark_mode, self.current_style['note_font']))
            content_layout.addWidget(content_label)
            if tags:
                tags_layout = QHBoxLayout()
                tags_layout.setSpacing(5)
                tags_layout.setContentsMargins(0, 0, 0, 0)
                for tag in tags.split():
                    tag_label = QLabel(tag)
                    tag_without_hash = tag.lstrip('#')
                    tag_colors = self.backend.get_tag_colors()
                    tag_label.setStyleSheet(Styles.TAG_LABEL_STYLE.format(
                        color=tag_colors.get(tag_without_hash, '#dddddd')))
                    tags_layout.addWidget(tag_label)
                tag_container = QWidget()
                tag_container.setLayout(tags_layout)
                content_layout.addWidget(tag_container)
            note_btn.setLayout(QVBoxLayout())
            note_btn.layout().addWidget(content_container)
            row, col = divmod(display_idx, max_columns)
            self.notes_layout.addWidget(note_btn, row, col)
            self.note_buttons.append(note_btn)

    def add_new_note(self):
        self.backend.add_note()
        self.arrange_notes(self.backend.get_notes())
        self.expand_note_view(len(self.backend.get_notes()) - 1, editable=True)

    def handle_note_click(self, event, index):
        note_index = getattr(index, 'real_note_index', index)
        if event.button() == Qt.MouseButton.LeftButton:
            self.expand_note_view(note_index, editable=False)
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint(), note_index)

    def expand_note_view(self, index, editable=False):
        if index in self.expanded_notes:
            return
        self.ignore_resize = True
        try:
            display_index = None
            for idx, btn in enumerate(self.note_buttons):
                if btn.real_note_index == index:
                    display_index = idx
                    break
            if display_index is None:
                return
            note_btn = self.note_buttons[display_index]
            note_btn.setVisible(False)
            parent_rect = self.rect()
            parent_center = parent_rect.center()
            note_width = int(parent_rect.width() * 0.6)
            note_height = int(parent_rect.height() * 0.7)
            expanded_note = QWidget(self)
            expanded_note.setObjectName("expandedNote")
            expanded_note.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
            expanded_note.setStyleSheet(Styles.get_expanded_note_style(self.is_dark_mode))
            start_pos = note_btn.mapTo(self, QPoint(0, 0))
            expanded_note.setGeometry(QRect(start_pos, note_btn.size()))
            layout = QVBoxLayout(expanded_note)
            layout.setContentsMargins(20, 20, 20, 20)
            title_edit = QLineEdit()
            title_edit.setPlaceholderText("Назва нотатки")
            title_edit.setText(self.backend.get_note_title(index))
            title_edit.setReadOnly(not editable)
            title_edit.setStyleSheet(Styles.get_expanded_note_input_style(self.is_dark_mode))
            layout.addWidget(title_edit)
            text_edit = QTextEdit()
            text_edit.setText(self.backend.get_notes()[index])
            text_edit.setReadOnly(not editable)
            text_edit.setStyleSheet(Styles.get_expanded_note_input_style(self.is_dark_mode))
            layout.addWidget(text_edit)
            tags_layout = QHBoxLayout()
            tags_edit = QLineEdit()
            tags_edit.setPlaceholderText("Теги")
            tags_edit.setText(self.backend.get_note_tags(index))
            tags_edit.setReadOnly(not editable)
            tags_edit.setStyleSheet(Styles.get_expanded_note_input_style(self.is_dark_mode))
            tags_layout.addWidget(tags_edit)
            if editable:
                select_tags_btn = QPushButton("Обрати")
                select_tags_btn.setFixedWidth(80)
                select_tags_btn.clicked.connect(lambda: self.open_tag_selector(tags_edit))
                select_tags_btn.setStyleSheet(Styles.get_tag_button_style(self.is_dark_mode))
                tags_layout.addWidget(select_tags_btn)
            layout.addLayout(tags_layout)
            tags_display_layout = QHBoxLayout()
            tags_display_layout.setSpacing(5)
            tags_display_layout.setContentsMargins(0, 0, 0, 0)
            tag_colors = self.backend.get_tag_colors()
            for tag in tags_edit.text().split():
                tag_without_hash = tag.lstrip('#')
                color = tag_colors.get(tag_without_hash, '#dddddd')
                tag_label = QLabel(tag)
                tag_label.setStyleSheet(Styles.TAG_LABEL_STYLE.format(color=color))
                tags_display_layout.addWidget(tag_label)
            layout.addLayout(tags_display_layout)
            buttons_layout = QHBoxLayout()
            if editable:
                save_btn = QPushButton("Зберегти")
                save_btn.clicked.connect(
                    lambda: self.save_note(index, expanded_note, title_edit, text_edit, tags_edit))
                save_btn.setStyleSheet(Styles.get_tag_button_style(self.is_dark_mode))
                buttons_layout.addWidget(save_btn)
            close_btn = QPushButton("Закрити")
            close_btn.clicked.connect(lambda: self.collapse_note(index))
            close_btn.setStyleSheet(Styles.get_tag_button_style(self.is_dark_mode))
            buttons_layout.addWidget(close_btn)
            layout.addLayout(buttons_layout)
            expanded_note.show()
            self.expanded_notes[index] = expanded_note
            final_x = parent_center.x() - note_width // 2
            final_y = parent_center.y() - note_height // 2
            final_rect = QRect(final_x, final_y, note_width, note_height)
            animation = QPropertyAnimation(expanded_note, b"geometry")
            animation.setDuration(200)
            animation.setStartValue(QRect(start_pos, note_btn.size()))
            animation.setEndValue(final_rect)
            animation.start()
            self.animation = animation
        finally:
            self.ignore_resize = False

    def save_note(self, index, expanded_note, title_edit, text_edit, tags_edit):
        self.backend.update_note(index, text_edit.toPlainText(), title_edit.text(), tags_edit.text())
        self.collapse_note(index)
        self.arrange_notes(self.backend.get_notes())

    def collapse_note(self, index):
        if index in self.expanded_notes:
            expanded_note = self.expanded_notes.pop(index)
            expanded_note.close()
            for btn in self.note_buttons:
                if btn.real_note_index == index:
                    btn.setVisible(True)
                    break

    def make_context_menu_handler(self, note_btn, index):
        def handler(pos):
            global_pos = note_btn.mapToGlobal(pos)
            self.show_context_menu(global_pos, index)
        return handler

    def show_context_menu(self, global_pos: QPoint, index: int):
        menu = CustomContextMenu(self, note_index=index)
        menu.edit_btn.clicked.connect(lambda: (menu.close(), self.expand_note_view(index, editable=True)))
        menu.delete_btn.clicked.connect(lambda: (menu.close(), self.delete_note(index)))
        main_geom = self.window().geometry()
        menu_size = menu.sizeHint()
        x, y = global_pos.x(), global_pos.y()
        if x + menu_size.width() > main_geom.x() + main_geom.width():
            x = max(main_geom.x(), main_geom.x() + main_geom.width() - menu_size.width())
        if y + menu_size.height() > main_geom.y() + main_geom.height():
            y = max(main_geom.y(), main_geom.y() + main_geom.height() - menu_size.height())
        if x < main_geom.x():
            x = main_geom.x()
        if y < main_geom.y():
            y = main_geom.y()
        menu.move(x, y)
        menu.show()

    def delete_note(self, index):
        del self.backend.notes[index]
        self.backend.save_notes()
        self.arrange_notes(self.backend.get_notes())

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.update_add_button_position)

    def update_add_button_position(self):
        self.button_position_timer.start(self.button_position_delay)

    def delayed_button_position_update(self):
        window_rect = self.rect()
        current_size = window_rect.size()
        if self.last_window_size is not None:
            width_diff = abs(current_size.width() - self.last_window_size.width())
            height_diff = abs(current_size.height() - self.last_window_size.height())
            if width_diff > 300 or height_diff > 300:
                QTimer.singleShot(100, self._update_button_position)
                self.last_window_size = current_size
                return
        self._update_button_position()
        self.last_window_size = current_size

    def _update_button_position(self):
        margin = 20
        window_rect = self.rect()
        viewport = self.scroll_area.viewport()
        viewport_rect = viewport.rect()
        x = window_rect.width() - self.add_button.width() - margin
        y = min(
            window_rect.height() - self.add_button.height() - margin,
            viewport_rect.height() - self.add_button.height() - margin
        )
        x = max(margin, min(x, window_rect.width() - self.add_button.width() - margin))
        y = max(margin, min(y, window_rect.height() - self.add_button.height() - margin))
        self.add_button.move(x, y)

    def resizeEvent(self, event):
        if not self.ignore_resize:
            super().resizeEvent(event)
            self.pending_size = event.size()
            self.update_add_button_position()
            self.resize_timer.start(self.resize_delay)

    def handle_resize_timeout(self):
        if self.pending_size is None:
            return
        width = self.pending_size.width()
        if width < 800:
            new_style = Styles.SCREEN_STYLES['small']
        elif width < 1200:
            new_style = Styles.SCREEN_STYLES['medium']
        else:
            new_style = Styles.SCREEN_STYLES['large']
        self.current_style = new_style
        note_width, note_height = new_style['note_size']
        spacing = int(new_style['spacing'].replace('px', ''))
        self.notes_layout.setSpacing(spacing)
        available_width = width - 100
        new_columns = max(1, available_width // (note_width + spacing))
        self.arrange_notes(self.backend.get_notes())
        self.add_button.setFixedSize(note_width * 2, note_height // 2)
        self.pending_size = None

    def open_tag_selector(self, tags_edit: QLineEdit):
        available_tags = self.backend.get_tags()
        tag_colors = self.backend.get_tag_colors()
        dialog = TagSelectorDialog(available_tags, tags_edit.text(), tag_colors, self)
        dialog.update_theme(self.is_dark_mode)
        if dialog.exec():
            selected = dialog.get_selected_tags()
            tags_edit.setText(selected)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        drop_pos = event.position().toPoint()
        new_index = self.find_drop_target_index(drop_pos)
        if new_index != self.highlighted_index:
            self.clear_highlight()
            self.highlighted_index = new_index
            if new_index is not None and new_index < len(self.note_buttons):
                target_btn = self.note_buttons[new_index]
                opacity_effect = QGraphicsOpacityEffect(target_btn)
                opacity_effect.setOpacity(0.6)
                target_btn.setGraphicsEffect(opacity_effect)

    def dragLeaveEvent(self, event):
        self.clear_all_highlights()
        self.highlighted_index = None
        event.accept()

    def dropEvent(self, event):
        source_index = int(event.mimeData().text())
        self.clear_all_highlights()
        self.highlighted_index = None
        drop_pos = event.position().toPoint()
        target_index = self.find_drop_target_index(drop_pos)
        if (
            target_index is not None
            and target_index != source_index
            and 0 <= source_index < len(self.backend.notes)
            and 0 <= target_index <= len(self.backend.notes)
        ):
            note = self.backend.notes.pop(source_index)
            self.backend.notes.insert(target_index, note)
            self.backend.save_notes()
            self.arrange_notes(self.backend.get_notes())
        event.acceptProposedAction()

    def clear_highlight(self):
        if self.highlighted_index is not None and self.highlighted_index < len(self.note_buttons):
            btn = self.note_buttons[self.highlighted_index]
            btn.setGraphicsEffect(None)

    def clear_all_highlights(self):
        for btn in self.note_buttons:
            btn.setGraphicsEffect(None)

    def filter_notes(self, search_text, search_tag=None):
        search_text = search_text.lower()
        matches = []
        notes = self.backend.get_notes()
        for i, note in enumerate(notes):
            title = self.backend.get_note_title(i).lower()
            content = note.lower()
            tags = self.backend.get_note_tags(i).lower()
            text_match = not search_text or search_text in title or search_text in content
            tag_match = not search_tag or search_tag.lower() in tags
            matches.append(text_match and tag_match)
        self.update_notes_opacity(matches)

    def filter_notes_by_tag(self, search_tag):
        search_tag = search_tag.strip().lower()
        matches = []
        notes = self.backend.get_notes()
        if not search_tag:
            matches = [True] * len(notes)
        else:
            for i, _ in enumerate(notes):
                tags = self.backend.get_note_tags(i).lower()
                matches.append(search_tag in tags)
        self.update_notes_opacity(matches)

    def update_notes_opacity(self, matches):
        for btn, is_match in zip(self.note_buttons, matches):
            opacity_effect = QGraphicsOpacityEffect(btn)
            opacity_effect.setOpacity(1.0 if is_match else 0.3)
            btn.setGraphicsEffect(opacity_effect)

    def get_note_content(self, save_function):
        for index, expanded_note in self.expanded_notes.items():
            text_edits = expanded_note.findChildren(QTextEdit)
            if text_edits:
                content = text_edits[0].toPlainText()
                save_function(content)
                return
        for btn in self.note_buttons:
            if not btn.isVisible():
                content = self.backend.get_notes()[btn.real_note_index]
                save_function(content)
                return
        if self.note_buttons:
            content = self.backend.get_notes()[self.note_buttons[0].real_note_index]
            save_function(content)

    def update_theme(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        self.setStyleSheet(Styles.get_main_style(is_dark_mode))
        self.scroll_area.setStyleSheet(Styles.get_scroll_area_style(is_dark_mode))
        theme = Styles.get_theme_styles(is_dark_mode)
        tag_colors = self.backend.get_tag_colors()
        for btn in self.note_buttons:
            btn.setStyleSheet(Styles.get_note_wrapper_style(is_dark_mode))
            for label in btn.findChildren(QLabel):
                tag_text = label.text().lstrip('#')
                if tag_text in tag_colors:
                    label.setStyleSheet(Styles.TAG_LABEL_STYLE.format(color=tag_colors[tag_text]))
                else:
                    label.setStyleSheet(Styles.get_note_content_label_style(is_dark_mode, self.current_style['note_font']))
        for expanded_note in self.expanded_notes.values():
            expanded_note.setStyleSheet(Styles.get_expanded_note_style(is_dark_mode))
            for widget in expanded_note.findChildren((QLineEdit, QTextEdit)):
                widget.setStyleSheet(Styles.get_expanded_note_input_style(is_dark_mode))
            for label in expanded_note.findChildren(QLabel):
                tag_text = label.text().lstrip('#')
                if tag_text in tag_colors:
                    label.setStyleSheet(Styles.TAG_LABEL_STYLE.format(color=tag_colors[tag_text]))
                else:
                    label.setStyleSheet(Styles.get_note_content_label_style(is_dark_mode, self.current_style['note_font']))
        self.add_button.setStyleSheet(Styles.get_floating_add_button_style(is_dark_mode))
        parent = self.parent()
        if parent and hasattr(parent, "reminders_widget") and parent.reminders_widget:
            parent.reminders_widget.update_theme(is_dark_mode)

    def show_tag_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(Styles.get_tag_dropdown_style(self.is_dark_mode))
        tags = self.backend.get_tags()
        for tag_name, color in tags.items():
            tag_label = QWidgetAction(menu)
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(8, 4, 8, 4)
            label = QLabel(f"#{tag_name}")
            label.setStyleSheet(Styles.TAG_LABEL_STYLE.format(color=color))
            layout.addWidget(label)
            tag_label.setDefaultWidget(widget)
            menu.addAction(tag_label)
        menu.addSeparator()
        create_tag_action = QAction("Створити новий тег", menu)
        create_tag_action.triggered.connect(self.create_new_tag)
        menu.addAction(create_tag_action)
        menu.exec(self.tag_menu_button.mapToGlobal(self.tag_menu_button.rect().bottomLeft()))

    def find_drop_target_index(self, drop_pos):
        for i, btn in enumerate(self.note_buttons):
            btn_pos = btn.mapFrom(self, drop_pos)
            if btn.rect().contains(btn_pos):
                return i
        return None

class DraggableNoteButton(QPushButton):
    def __init__(self, index, on_click_callback=None, parent=None):
        super().__init__(parent)
        self.index = index
        self.real_note_index = index
        self.on_click_callback = on_click_callback
        self.setAcceptDrops(True)
        self.start_pos = None
        self.drag_preview = None

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.position().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.start_pos is not None:
            distance = (event.position().toPoint() - self.start_pos).manhattanLength()
            if distance >= QApplication.startDragDistance():
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(str(self.real_note_index))
                drag.setMimeData(mime_data)
                drag.setPixmap(self.grab())
                drag.exec()
                self.start_pos = None
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.start_pos is not None:
            distance = (event.position().toPoint() - self.start_pos).manhattanLength()
            if distance < QApplication.startDragDistance():
                if self.on_click_callback:
                    self.on_click_callback(event, self.real_note_index)
        self.start_pos = None
        super().mouseReleaseEvent(event)

    def create_drag_preview(self):
        preview = QLabel(self.window())
        preview.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        preview.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.ToolTip)
        preview.setStyleSheet("border: 2px solid #aaa; border-radius: 15px;")
        preview.setPixmap(self.grab())
        preview.setFixedSize(self.size())
        return preview
    

class TagSelectorDialog(QDialog):
    def __init__(self, available_tags, current_tags="", tag_colors=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обрати теги")
        self.setMinimumSize(300, 200)
        self.selected_tags = set(current_tags.split())
        self.is_dark_mode = parent.is_dark_mode if parent else False
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_container = QWidget(self)
        main_container.setObjectName("tagSelectorContainer")
        self.apply_theme()
        self.tag_colors = tag_colors or {}
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(10)
        self.buttons = []
        for tag in available_tags:
            tag_with_hash = f"#{tag}"
            tag_btn = QPushButton(tag_with_hash)
            tag_btn.setCheckable(True)
            tag_btn.setChecked(tag_with_hash in self.selected_tags)
            color = self.tag_colors.get(tag, "#dddddd")
            tag_btn.setStyleSheet(self.get_tag_button_style(color, tag_with_hash in self.selected_tags))
            tag_btn.clicked.connect(self.toggle_tag)
            self.buttons.append(tag_btn)
            container_layout.addWidget(tag_btn)
        self.confirm_btn = QPushButton("OK")
        self.confirm_btn.setObjectName("tag_confirm_btn")
        self.confirm_btn.clicked.connect(self.accept)
        container_layout.addWidget(self.confirm_btn)
        main_layout.addWidget(main_container)

    def apply_theme(self):
        self.setStyleSheet(Styles.get_tag_selector_style(self.is_dark_mode))

    def get_tag_button_style(self, color, is_selected=False):
        border = "2px solid #6E6E6E;" if is_selected else "none"
        return f"""
            background-color: {color};
            color: black;
            border-radius: 10px;
            padding: 6px 12px;
            border: {border};
        """

    def toggle_tag(self):
        sender = self.sender()
        tag = sender.text()
        if sender.isChecked():
            self.selected_tags.add(tag)
        else:
            self.selected_tags.discard(tag)
        tag_without_hash = tag.lstrip('#')
        color = self.tag_colors.get(tag_without_hash, "#dddddd")
        sender.setStyleSheet(self.get_tag_button_style(color, sender.isChecked()))

    def get_selected_tags(self):
        return " ".join(self.selected_tags)

    def update_theme(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        self.apply_theme()
        for button in self.buttons:
            tag = button.text().lstrip('#')
            color = self.tag_colors.get(tag, "#dddddd")
            button.setStyleSheet(self.get_tag_button_style(color, button.isChecked()))


class CustomContextMenu(QWidget):
    def __init__(self, parent=None, note_index=None):
        super().__init__(parent)
        self.note_index = note_index
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setStyleSheet(Styles.get_context_menu_style(parent.is_dark_mode))
        self.setFixedSize(240, 170)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        container = QWidget(self)
        container.setObjectName("menuContainer")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(5)
        container_layout.setContentsMargins(5, 5, 5, 5)
        self.edit_btn = QPushButton("Редагувати")
        self.save_b_btn = QPushButton("Зберегти вміст до буфера обміну")
        self.save_f_btn = QPushButton("Зберегти вміст до файлу")
        self.remind_btn = QPushButton("Встановити нагадування")
        self.delete_btn = QPushButton("Видалити")
        container_layout.addWidget(self.edit_btn)
        container_layout.addWidget(self.save_b_btn)
        container_layout.addWidget(self.save_f_btn)
        container_layout.addWidget(self.remind_btn)
        container_layout.addWidget(self.delete_btn)
        outer_layout.addWidget(container)
        self.save_b_btn.clicked.connect(self.save_to_clipboard)
        self.save_f_btn.clicked.connect(self.save_to_file)
        self.remind_btn.clicked.connect(self.set_reminder)

    def save_to_clipboard(self):
        parent = self.parent()
        if parent and self.note_index is not None:
            content = parent.backend.get_notes()[self.note_index]
            parent.backend.save_to_clipboard(content)
        self.close()

    def save_to_file(self):
        parent = self.parent()
        if parent and self.note_index is not None:
            content = parent.backend.get_notes()[self.note_index]
            parent.backend.save_to_file(content, parent)
        self.close()

    def set_reminder(self):
        dialog = ReminderDialog(self, is_dark_mode=self.parent().is_dark_mode)
        if dialog.exec():
            date, time = dialog.get_datetime()
            dt = QDateTime(date, time)
            note_text = self.parent().backend.get_notes()[self.note_index]
            self.parent().reminder_manager.set_reminder(note_text, dt)
        self.close()

class ReminderDialog(QDialog):
    def __init__(self, parent=None, is_dark_mode=False):
        super().__init__(parent)
        self.is_dark_mode = is_dark_mode
        self.setWindowTitle("Встановити нагадування")
        self.setFixedSize(300, 200)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        main_container = QWidget(self)
        main_container.setObjectName("reminderDialogContainer")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)
        title_label = QLabel("Встановити нагадування")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; background: transparent;")
        container_layout.addWidget(title_label)
        self.date_edit = QDateEdit(self)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        container_layout.addWidget(self.date_edit)
        self.time_edit = QTimeEdit(self)
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setButtonSymbols(QTimeEdit.ButtonSymbols.NoButtons)
        container_layout.addWidget(self.time_edit)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        self.ok_button = QPushButton("OK", self)
        self.ok_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.ok_button)
        cancel_button = QPushButton("Скасувати", self)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)
        container_layout.addLayout(buttons_layout)
        main_layout.addWidget(main_container)
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(Styles.get_reminder_dialog_style(self.is_dark_mode))

    def get_datetime(self):
        return self.date_edit.date(), self.time_edit.time()
