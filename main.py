import sys
import os
import json
from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QLineEdit, QPushButton, QVBoxLayout, QMenu, QFileDialog, QWidgetAction, QLabel, QScrollArea, QSystemTrayIcon, QStyle, QSizePolicy, QGraphicsDropShadowEffect, QDialog, QColorDialog, QFrame
from PyQt6.QtGui import QAction, QIcon, QDrag, QColor
from PyQt6.QtCore import pyqtSignal, QSize, QPoint, Qt, QMimeData, QTimer
from back import NotesBackend
from Mainpage import MainPage
from styles import Styles


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class NotesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Нотатки")
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.resize(1200, 800)

        screen = QApplication.primaryScreen().geometry()
        self.setMinimumSize(int(screen.width() * 0.3), int(screen.height() * 0.3))

        self.backend = NotesBackend()
        self.main_page = MainPage(self.backend)
        self.setCentralWidget(self.main_page)

        self.reminders_widget = None
        self.is_dark_mode = False

        self.setup_top_bar()
        self.setup_system_tray()
        self.setup_expand_button()
        self.update_theme()

        self.current_tag = None
        self.search_text = ""
        self.is_topbar_expanded = True

    def setup_top_bar(self):
        top_bar = QWidget()
        top_bar.setStyleSheet(Styles.get_top_bar_style(self.is_dark_mode))
        
        self.main_layout = QVBoxLayout(top_bar)
        self.main_layout.setContentsMargins(10, 5, 10, 5)
        self.main_layout.setSpacing(5)

        self.single_row_container = QWidget()
        single_row_layout = QHBoxLayout(self.single_row_container)
        single_row_layout.setContentsMargins(0, 0, 0, 0)
        single_row_layout.setSpacing(10)

        left_container = QWidget()
        left_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        left_layout = QHBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Пошук нотаток...")
        self.search_field.textChanged.connect(self.update_search_text)
        self.search_field.setFixedHeight(36)
        self.search_field.setStyleSheet(Styles.get_search_field_style(self.is_dark_mode))
        self.search_field.setMinimumWidth(250)
        self.search_field.setMaximumWidth(400)
        self.search_field.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        left_layout.addWidget(self.search_field)

        self.tag_menu_button = QPushButton("Теги")
        self.tag_menu_button.setStyleSheet(Styles.get_tag_dropdown_button_style(self.is_dark_mode))
        self.tag_menu_button.clicked.connect(self.show_tag_menu)
        left_layout.addWidget(self.tag_menu_button)

        tags_container = QWidget()
        tags_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        tags_layout = QHBoxLayout(tags_container)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        tags_layout.setSpacing(5)

        self.tag_selector = TagSelector()
        self.tag_selector.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.tag_selector.tag_selected.connect(self.search_by_tag)
        tags_layout.addWidget(self.tag_selector)

        self.reset_tag_button = QPushButton("Скинути тег")
        self.reset_tag_button.clicked.connect(self.reset_tag_search)
        self.reset_tag_button.setEnabled(False)
        self.reset_tag_button.setStyleSheet(Styles.get_no_tag_button_style(self.is_dark_mode))
        self.reset_tag_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        tags_layout.addWidget(self.reset_tag_button)

        left_layout.addWidget(tags_container)

        right_container = QWidget()
        right_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)

        self.reminders_button = QPushButton("Мої нагадування")
        self.reminders_button.setStyleSheet(Styles.get_tag_button_style(self.is_dark_mode))
        self.reminders_button.clicked.connect(self.toggle_reminders_widget)
        self.reminders_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        right_layout.addWidget(self.reminders_button)

        self.dark_mode_switch = QPushButton()
        self.dark_mode_switch.setObjectName("dark_mode_switch")
        self.dark_mode_switch.setCheckable(True)
        self.dark_mode_switch.setChecked(False)
        self.dark_mode_switch.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.dark_mode_switch.setIcon(QIcon(resource_path("contrast.png")))
        self.dark_mode_switch.setIconSize(QSize(25, 25))
        self.dark_mode_switch.clicked.connect(self.toggle_theme)
        self.dark_mode_switch.setStyleSheet(Styles.get_dark_mode_switch_style(self.is_dark_mode))
        right_layout.addWidget(self.dark_mode_switch)

        single_row_layout.addWidget(left_container)
        single_row_layout.addStretch(1)
        single_row_layout.addWidget(right_container)

        self.main_layout.addWidget(self.single_row_container)
        self.setMenuWidget(top_bar)
        
        self.initial_search_width = 250
        self.initial_button_width = 150
        self.initial_icon_size = 32

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("Add.png")))
        
        tray_menu = QMenu()
        
        show_action = tray_menu.addAction("Показати")
        show_action.triggered.connect(self.show_from_tray)
        
        quit_action = tray_menu.addAction("Вийти")
        quit_action.triggered.connect(self.quit_application)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        self.tray_icon.show()

    def setup_expand_button(self):
        self.expand_button = QPushButton("≡", self)
        self.expand_button.setFixedSize(40, 40)
        self.expand_button.clicked.connect(self.toggle_topbar)
        self.expand_button.setStyleSheet(Styles.EXPAND_BUTTON_STYLE)
        self.expand_button.hide()

    def toggle_topbar(self):
        self.is_topbar_expanded = not self.is_topbar_expanded
        if self.is_topbar_expanded:
            self.menuWidget().show()
            self.expand_button.setText("≡")
        else:
            self.menuWidget().hide()
            self.expand_button.setText("≡")
        self.update_expand_button_position()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        

    def show_from_tray(self):
        self.showNormal()
        self.activateWindow()

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_from_tray()

    def quit_application(self):
        self.backend.save_notes()
        QApplication.quit()

    def update_search_text(self, text):
        self.search_text = text
        self.apply_filters()

    def search_notes(self):
        self.apply_filters()

    def apply_filters(self):
        self.main_page.filter_notes(self.search_text, self.current_tag)


    def search_by_tag(self, tag_name):
        self.current_tag = tag_name
        self.apply_filters()
        self.reset_tag_button.setEnabled(True)


    def reset_tag_search(self):
        self.current_tag = None
        self.apply_filters()
        self.reset_tag_button.setEnabled(False)
        self.tag_selector.reset_tag_button_text()

    def toggle_reminders_widget(self):
        if self.reminders_widget is None or not self.reminders_widget.isVisible():
            if self.reminders_widget is None:
                self.reminders_widget = RemindersWidget(self)
                self.reminders_widget.setStyleSheet(Styles.get_reminders_widget_style(self.is_dark_mode))
            
            button_pos = self.reminders_button.mapToGlobal(
                self.reminders_button.rect().bottomLeft())
            screen = QApplication.primaryScreen().geometry()
            
            widget_pos = QPoint(
                min(button_pos.x(), screen.width() - self.reminders_widget.width()),
                min(button_pos.y(), screen.height() - self.reminders_widget.height())
            )
            
            self.reminders_widget.move(widget_pos)
            self.reminders_widget.update_reminders()
            self.reminders_widget.show()
        else:
            self.reminders_widget.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = event.size().width()
        if width < 800:
            small_screen_container = self.findChild(QWidget, "small_screen_container")
            if not small_screen_container:
                small_screen_container = QWidget(self)
                small_screen_container.setObjectName("small_screen_container")
                small_layout = QVBoxLayout(small_screen_container)
                small_layout.setContentsMargins(0, 0, 0, 0)
                small_layout.setSpacing(5)
                top_row = QWidget()
                top_row.setStyleSheet(Styles.TOP_BAR_STYLE)
                top_layout = QHBoxLayout(top_row)
                top_layout.setContentsMargins(0, 0, 0, 0)
                top_layout.setSpacing(5)
                for w in [self.search_field, self.tag_selector, self.reset_tag_button, self.reminders_button, self.dark_mode_switch, self.tag_menu_button]:
                    if w.parent():
                        w.setParent(None)
                top_layout.addWidget(self.search_field)
                top_layout.addStretch(1)
                top_layout.addWidget(self.tag_selector)
                top_layout.addWidget(self.reset_tag_button)
                bottom_row = QWidget()
                bottom_row.setStyleSheet(Styles.TOP_BAR_STYLE)
                bottom_layout = QHBoxLayout(bottom_row)
                bottom_layout.setContentsMargins(0, 0, 0, 0)
                bottom_layout.setSpacing(5)
                bottom_layout.addWidget(self.reminders_button)
                bottom_layout.addWidget(self.dark_mode_switch)
                bottom_layout.addStretch(1)
                bottom_layout.addWidget(self.tag_menu_button)
                self.tag_menu_button.setFixedSize(self.initial_button_width, 36)
                small_layout.addWidget(top_row), 
                small_layout.addWidget(bottom_row)
                self.update_small_screen_styles()
                self.single_row_container.hide()
                self.main_layout.addWidget(small_screen_container)
            else:
                for i in range(small_screen_container.layout().count()):
                    row = small_screen_container.layout().itemAt(i).widget()
                    if isinstance(row, QWidget):
                        layout = row.layout()
                        if layout:
                            if i == 0:
                                while layout.count():
                                    item = layout.takeAt(0)
                                    if item.widget():
                                        item.widget().setParent(None)
                                layout.addWidget(self.search_field)
                                layout.addStretch(1)
                                layout.addWidget(self.tag_selector)
                                layout.addWidget(self.reset_tag_button)
                            elif i == 1:
                                while layout.count():
                                    item = layout.takeAt(0)
                                    if item.widget():
                                        item.widget().setParent(None)
                                layout.addWidget(self.reminders_button)
                                layout.addWidget(self.dark_mode_switch)
                                layout.addStretch(1)
                                layout.addWidget(self.tag_menu_button)
                                self.tag_menu_button.setFixedSize(self.initial_button_width, 36)
            self.search_field.setFixedHeight(36)
            self.search_field.setStyleSheet(Styles.get_search_field_style(self.is_dark_mode))
            self.search_field.setMinimumWidth(200)
            self.search_field.setMaximumWidth(300)
        else:
            small_screen_container = self.findChild(QWidget, "small_screen_container")
            if small_screen_container:
                for w in [self.search_field, self.tag_menu_button, self.tag_selector, self.reset_tag_button, self.reminders_button, self.dark_mode_switch]:
                    if w.parent():
                        w.setParent(None)
                small_screen_container.deleteLater()
                left_container = QWidget()
                left_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                left_layout = QHBoxLayout(left_container)
                left_layout.setContentsMargins(0, 0, 0, 0)
                left_layout.setSpacing(10)
                tags_container = QWidget()
                tags_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                tags_layout = QHBoxLayout(tags_container)
                tags_layout.setContentsMargins(0, 0, 0, 0)
                tags_layout.setSpacing(5)
                left_layout.addWidget(self.search_field)
                left_layout.addWidget(self.tag_menu_button)
                tags_layout.addWidget(self.tag_selector)
                tags_layout.addWidget(self.reset_tag_button)
                left_layout.addWidget(tags_container)
                right_container = QWidget()
                right_container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                right_layout = QHBoxLayout(right_container)
                right_layout.setContentsMargins(0, 0, 0, 0)
                right_layout.setSpacing(10)
                right_layout.addWidget(self.reminders_button)
                right_layout.addWidget(self.dark_mode_switch)
                while self.single_row_container.layout().count():
                    item = self.single_row_container.layout().takeAt(0)
                    if item.widget():
                        item.widget().setParent(None)
                single_row_layout = self.single_row_container.layout()
                single_row_layout.addWidget(left_container)
                single_row_layout.addStretch(1)
                single_row_layout.addWidget(right_container)
                self.search_field.setMinimumWidth(250)
                self.search_field.setMaximumWidth(400)
                self.dark_mode_switch.setIconSize(QSize(32, 32))
                self.tag_menu_button.setFixedSize(self.initial_button_width, 36)
                self.single_row_container.show()
        if width < 800:
            self.expand_button.show()
            QTimer.singleShot(0, self.update_expand_button_position)
            if not self.is_topbar_expanded:
                self.menuWidget().hide()
        else:
            self.expand_button.hide()
            self.menuWidget().show()
        
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(200, self.main_page._update_button_position)
        
    def toggle_theme(self):
        self.is_dark_mode = self.dark_mode_switch.isChecked()
        self.update_theme()

    def update_theme(self):
        self.setStyleSheet(Styles.get_main_style(self.is_dark_mode))
        
        if hasattr(self, 'search_field'):
            self.search_field.setFixedHeight(36)
            self.search_field.setStyleSheet(Styles.get_search_field_style(self.is_dark_mode))

        if hasattr(self, 'tag_menu_button'):
            self.tag_menu_button.setStyleSheet(Styles.get_tag_dropdown_button_style(self.is_dark_mode))

        if hasattr(self, 'tag_selector'):
            self.tag_selector.tag_button.setStyleSheet(Styles.get_tag_select_button_style(self.is_dark_mode))
            self.tag_selector.tag_menu.setStyleSheet(Styles.get_tag_selector_style(self.is_dark_mode))
        
        if hasattr(self, 'reset_tag_button'):
            self.reset_tag_button.setStyleSheet(Styles.get_no_tag_button_style(self.is_dark_mode))
        
        if hasattr(self, 'reminders_button'):
            self.reminders_button.setStyleSheet(Styles.get_tag_button_style(self.is_dark_mode))
        
        if hasattr(self, 'menuWidget'):
            self.menuWidget().setStyleSheet(Styles.get_top_bar_style(self.is_dark_mode))
        
        if hasattr(self, 'reminders_widget') and self.reminders_widget:
            self.reminders_widget.setStyleSheet(Styles.get_reminders_widget_style(self.is_dark_mode))
        
        if hasattr(self, 'main_page'):
            self.main_page.update_theme(self.is_dark_mode)
        
        if hasattr(self, 'expand_button'):
            if self.is_dark_mode:
                self.expand_button.setStyleSheet(Styles.get_expand_button_style_dark())
            else:
                self.expand_button.setStyleSheet(Styles.EXPAND_BUTTON_STYLE)

        if hasattr(self, 'dark_mode_switch'):
            self.dark_mode_switch.setStyleSheet(Styles.get_dark_mode_switch_style(self.is_dark_mode))
        
        if hasattr(self, 'tag_creation_widget'):
            self.tag_creation_widget.update_theme(self.is_dark_mode)

    def update_small_screen_styles(self):
        self.search_field.setFixedHeight(36)
        self.search_field.setStyleSheet(Styles.get_search_field_style(self.is_dark_mode))
        self.search_field.setMinimumWidth(200)
        self.search_field.setMaximumWidth(300)
        
    def update_layout_for_screen_size(self, width):

        self.search_field.setFixedHeight(36)
        self.search_field.setStyleSheet(Styles.get_search_field_style(self.is_dark_mode))
        
        if width < 800: 
            self.search_field.setMinimumWidth(200)
            self.search_field.setMaximumWidth(300)
        else:
            self.search_field.setMinimumWidth(250)
            self.search_field.setMaximumWidth(400)
        
    def show_tag_menu(self):
        menu = CustomTagMenu(self, self.is_dark_mode)
        
        tags = self.backend.get_tags()
        for tag_name, color in tags.items():
            menu.add_tag_item(tag_name, color)
        
        menu.add_separator()
        
        # Однаковий стиль для обох кнопок
        tag_btn_style = Styles.get_tag_dropdown_button_style(self.is_dark_mode)
        menu.add_action("Створити новий тег", self.create_new_tag, style=tag_btn_style)
        menu.add_action("Видалити теги", self.show_delete_tags_menu, style=tag_btn_style)
        
        pos = self.tag_menu_button.mapToGlobal(self.tag_menu_button.rect().bottomLeft())
        menu.move(pos)
        menu.show()

    def create_new_tag(self):
        if not hasattr(self, 'tag_creation_widget'):
            self.tag_creation_widget = TagCreationWidget(self, self.is_dark_mode)
            self.tag_creation_widget.ok_button.clicked.connect(self.handle_tag_creation)
        
        button_pos = self.tag_menu_button.mapToGlobal(self.tag_menu_button.rect().bottomLeft())
        self.tag_creation_widget.move(button_pos)
        self.tag_creation_widget.show()

    def handle_tag_creation(self):
        tag_data = self.tag_creation_widget.get_tag_data()
        self.backend.add_tag(tag_data["name"], tag_data["color"])
        self.tag_selector.available_tags = self.tag_selector.load_tags()
        self.tag_selector.populate_menu()
        self.tag_creation_widget.hide()

    def show_delete_tags_menu(self):
        tags_dict = self.backend.get_tags()
        tag_names = list(tags_dict.keys())
        tag_colors = self.backend.get_tag_colors()
        dialog = TagDeleteDialog(tag_names, tag_colors, self)
        dialog.update_theme(self.is_dark_mode)
        if dialog.exec():
            tags_to_delete = dialog.get_selected_tags()
            for tag in tags_to_delete:
                if tag in self.backend.tags:
                    del self.backend.tags[tag]
            self.backend.save_tags()
            self.tag_selector.available_tags = self.tag_selector.load_tags()
            self.tag_selector.populate_menu()

    def update_expand_button_position(self):
        width = self.width()
        btn_width = self.expand_button.width()
        margin = 10
        if self.menuWidget() and self.menuWidget().isVisible():
            navbar_height = self.menuWidget().height()
            if navbar_height < 10:
                navbar_height = self.menuWidget().sizeHint().height()
        else:
            navbar_height = 0
        if width < 800:
            if self.is_topbar_expanded:
                x = margin
                y = navbar_height + margin
                self.expand_button.move(x, y)
            else:
                x = margin
                y = margin
                self.expand_button.move(x, y)

class TagSelector(QWidget):
    tag_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.tag_button = QPushButton("Вибрати тег")
        self.tag_button.setStyleSheet(Styles.get_tag_select_button_style(False))
        self.layout.addWidget(self.tag_button)

        self.tag_menu = QWidget(None)
        self.tag_menu.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.tag_menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tag_menu.setObjectName("tagSelectorContainer")
        self.tag_menu.setStyleSheet(Styles.get_tag_selector_style(False))
        
        self.inner_container = QWidget(self.tag_menu)
        self.inner_container.setObjectName("tagSelectorContainer")
        
        self.menu_layout = QVBoxLayout(self.inner_container)
        self.menu_layout.setContentsMargins(10, 10, 10, 10)
        self.menu_layout.setSpacing(5)

        main_menu_layout = QVBoxLayout(self.tag_menu)
        main_menu_layout.setContentsMargins(0, 0, 0, 0)
        main_menu_layout.addWidget(self.inner_container)

        self.tag_button.clicked.connect(self.show_tag_menu)
        self.available_tags = self.load_tags()
        self.populate_menu()

    def update_theme(self, is_dark_mode):
        self.tag_button.setStyleSheet(Styles.get_tag_select_button_style(is_dark_mode))
        self.tag_menu.setStyleSheet(Styles.get_tag_selector_style(is_dark_mode))
        self.inner_container.setStyleSheet(Styles.get_tag_selector_style(is_dark_mode))

    def show_tag_menu(self):
        if not self.tag_menu.isVisible():
            pos = self.tag_button.mapToGlobal(self.tag_button.rect().bottomLeft())
            
            self.tag_menu.setFixedWidth(200)
            self.tag_menu.adjustSize()
            
            screen = QApplication.primaryScreen().geometry()
            menu_height = self.tag_menu.sizeHint().height()
            
            if pos.y() + menu_height > screen.height():
                pos.setY(pos.y() - menu_height - self.tag_button.height())
            
            self.tag_menu.move(pos)
            self.tag_menu.show()
        else:
            self.tag_menu.hide()

    def load_tags(self):
        tags_path = resource_path("tags.json")
        if os.path.exists(tags_path):
            with open(tags_path, "r", encoding="utf-8") as f:
                try:
                    tags_data = json.load(f)
                    if isinstance(tags_data, list):
                        return tags_data
                except json.JSONDecodeError:
                    print("Помилка при зчитуванні tags.json.")
        return []

    def populate_menu(self):
        for i in reversed(range(self.menu_layout.count())):
            widget = self.menu_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for tag in self.available_tags:
            tag_name = tag.get("name", "невідомо")
            tag_color = tag.get("color", "#dddddd")
            tag_btn = QPushButton(f"#{tag_name}")
            tag_btn.setStyleSheet(Styles.TAG_BUTTON_STYLE.format(color=tag_color))
            tag_btn.clicked.connect(lambda checked, t=tag_name: self.select_tag(t))
            self.menu_layout.addWidget(tag_btn)

        self.tag_menu.setFixedWidth(200)
        self.tag_menu.adjustSize()

    def select_tag(self, tag_name):
        self.tag_button.setText(tag_name)
        self.tag_selected.emit(tag_name)

    def reset_tag_button_text(self):
        self.tag_button.setText("Вибрати тег")


class RemindersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("remindersContainer")
        main_container = QWidget(self)
        main_container.setObjectName("remindersContainer")
        self.setStyleSheet(Styles.get_reminders_widget_style(parent.is_dark_mode if parent and hasattr(parent, "is_dark_mode") else False))
        self.setFixedSize(300, 400)
        
        main_layout = QVBoxLayout(main_container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.title = QLabel("Мої нагадування")
        self.set_title_style(parent.is_dark_mode if parent and hasattr(parent, "is_dark_mode") else False)
        main_layout.addWidget(self.title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent;")
        
        content = QWidget()
        content.setObjectName("reminderContent")
        self.content_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(main_container)
        
        self.update_reminders()
        
    def set_title_style(self, is_dark_mode):
        color = "#ffffff" if is_dark_mode else "#333333"
        self.title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")

    def update_theme(self, is_dark_mode):
        self.set_title_style(is_dark_mode)
        self.setStyleSheet(Styles.get_reminders_widget_style(is_dark_mode))

    def update_reminders(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
        try:
            with open(resource_path("reminders.json"), "r", encoding="utf-8") as f:
                reminders = json.load(f)
                
            if not reminders:
                no_reminders = QLabel("Немає активних нагадувань")
                no_reminders.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.content_layout.addWidget(no_reminders)
            else:
                for reminder in reminders:
                    reminder_text = reminder["text"]
                    reminder_datetime = reminder["datetime"].replace("T", " ")

                    reminder_frame = QFrame()
                    reminder_frame.setObjectName("reminderItemFrame")
                    reminder_frame.setFrameShape(QFrame.Shape.StyledPanel)
                    reminder_frame.setFrameShadow(QFrame.Shadow.Raised)
                    reminder_frame.setStyleSheet(
                        Styles.get_reminder_item_frame_style(
                            self.parent().is_dark_mode if self.parent() and hasattr(self.parent(), "is_dark_mode") else False
                        )
                    )
                    frame_layout = QVBoxLayout(reminder_frame)
                    frame_layout.setContentsMargins(8, 8, 8, 8)
                    frame_layout.setSpacing(2)

                    item = QLabel(f"Текст: {reminder_text[:50]}...\nДата та час: {reminder_datetime}")
                    item.setObjectName("reminderItem")
                    item.setWordWrap(True)
                    frame_layout.addWidget(item)

                    self.content_layout.addWidget(reminder_frame)
                
        except (FileNotFoundError, json.JSONDecodeError):
            no_reminders = QLabel("Немає активних нагадувань")
            no_reminders.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.content_layout.addWidget(no_reminders)
            
        self.content_layout.addStretch()


class TagCreationDialog(QDialog):
    def __init__(self, parent=None, is_dark_mode=False):
        super().__init__(parent)
        self.is_dark_mode = is_dark_mode if hasattr(parent, "is_dark_mode") else False
        self.setWindowTitle("Створити новий тег")
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Назва тегу")
        layout.addWidget(self.name_input)
        
        color_layout = QHBoxLayout()
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#RRGGBB")
        color_layout.addWidget(self.color_input)
        
        color_button = QPushButton("Обрати колір")
        color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(color_button)
        layout.addLayout(color_layout)
        
        buttons = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Скасувати")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(Styles.get_tag_selector_style(self.is_dark_mode))

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_input.setText(color.name())
            
    def get_tag_data(self):
        return {
            "name": self.name_input.text(),
            "color": self.color_input.text() or "#cccccc"
        }


class CustomTagMenu(QWidget):
    def __init__(self, parent=None, is_dark_mode=False):
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.is_dark_mode = is_dark_mode
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        self.container = QWidget(self)
        self.container.setObjectName("menuContainer")
        
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(8, 8, 8, 8)
        self.container_layout.setSpacing(4)
        
        self.main_layout.addWidget(self.container)
        
        self.apply_theme()
    
    def add_tag_item(self, tag_name, color):
        tag_widget = QWidget()
        tag_widget.setStyleSheet("background: transparent;")
        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(4, 4, 4, 4)
        tag_layout.setSpacing(0)
        
        label = QLabel(f"#{tag_name}")
        label.setStyleSheet(Styles.TAG_LABEL_STYLE.format(color=color))
        tag_layout.addWidget(label)
        
        self.container_layout.addWidget(tag_widget)
    
    def add_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {Styles.get_theme_styles(self.is_dark_mode)['border']}; margin: 4px 0px;")
        self.container_layout.addWidget(line)
    
    def add_action(self, text, callback, style=None):
        button = QPushButton(text)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)
        if style:
            button.setStyleSheet(style)
        self.container_layout.addWidget(button)
    
    def apply_theme(self):
        self.container.setStyleSheet(Styles.get_context_menu_style(self.is_dark_mode))

    def update_theme(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        self.apply_theme()


class TagCreationWidget(QWidget):
    def __init__(self, parent=None, is_dark_mode=False):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.is_dark_mode = is_dark_mode if hasattr(parent, "is_dark_mode") else False
        self.setFixedSize(400, 200)
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.container = QWidget(self)
        self.container.setObjectName("menuContainer")
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)
        title = QLabel("Створити новий тег")
        title.setStyleSheet("font-size: 16px; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Назва тегу")
        self.name_input.setMinimumHeight(40)
        layout.addWidget(self.name_input)
        color_layout = QHBoxLayout()
        color_layout.setSpacing(10)
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("#RRGGBB")
        self.color_input.setMinimumHeight(40)
        color_layout.addWidget(self.color_input)
        color_button = QPushButton("Обрати колір")
        color_button.setMinimumHeight(40)
        color_button.clicked.connect(self.choose_color)
        color_layout.addWidget(color_button)
        layout.addLayout(color_layout)
        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        self.ok_button = QPushButton("OK")
        self.ok_button.setMinimumHeight(40)
        self.ok_button.clicked.connect(self.hide)
        cancel_button = QPushButton("Скасувати")
        cancel_button.setMinimumHeight(40)
        cancel_button.clicked.connect(self.hide)
        buttons.addWidget(self.ok_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)
        self.main_layout.addWidget(self.container)
        self.apply_theme()

    def apply_theme(self):
        self.setStyleSheet(Styles.get_tag_creation_widget_style(self.is_dark_mode))

    def choose_color(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            self.color_input.setText(color.name())

    def update_theme(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        self.apply_theme()

    def get_tag_data(self):
        return {
            "name": self.name_input.text(),
            "color": self.color_input.text() or "#cccccc"
        }


class TagDeleteDialog(QDialog):
    def __init__(self, available_tags, tag_colors, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Видалити теги")
        self.setMinimumSize(300, 200)
        self.selected_tags = set()
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
            tag_btn.setChecked(False)
            color = self.tag_colors.get(tag, "#dddddd")
            tag_btn.setStyleSheet(self.get_tag_button_style(color, False))
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
        tag = sender.text().lstrip('#')
        if sender.isChecked():
            self.selected_tags.add(tag)
        else:
            self.selected_tags.discard(tag)
        color = self.tag_colors.get(tag, "#dddddd")
        sender.setStyleSheet(self.get_tag_button_style(color, sender.isChecked()))

    def get_selected_tags(self):
        return list(self.selected_tags)

    def update_theme(self, is_dark_mode):
        self.is_dark_mode = is_dark_mode
        self.apply_theme()
        for button in self.buttons:
            tag = button.text().lstrip('#')
            color = self.tag_colors.get(tag, "#dddddd")
            button.setStyleSheet(self.get_tag_button_style(color, button.isChecked()))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NotesApp()
    window.showMaximized()
    sys.exit(app.exec())
