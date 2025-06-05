class Styles:
    LIGHT_BG = "#ffffff"
    DARK_BG = "#333333"
    LIGHT_TEXT = "#000000"
    DARK_TEXT = "#ffffff"
    
    @classmethod
    def get_theme_styles(cls, is_dark_mode):
        if (is_dark_mode):
            return {
                'background': cls.DARK_BG,
                'text': cls.DARK_TEXT,
                'border': "#66686b",
                'note_bg': "#444444",
                'button_bg': "#444444",
                'hover_bg': "#555555",
                'topbar_bg': "#222222"
            }
        else:
            return {
                'background': cls.LIGHT_BG,
                'text': cls.LIGHT_TEXT,
                'border': "#f2f2f2",
                'note_bg': "#ffffff",
                'button_bg': "#ffffff",
                'hover_bg': "#f0f0f0",
                'topbar_bg': "#ff9633"
            }

    @classmethod
    def get_main_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QMainWindow, QWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #f2f2f2;
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #e6e6e6;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

    @classmethod
    def get_note_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QWidget {{
                border: 1px solid {theme['border']};
                border-radius: 15px;
                background-color: {theme['note_bg']};
                color: {theme['text']};
                text-align: left;
            }}
            QLabel {{
                background-color: transparent;
                border: none;
                padding: 0px;
                font-size: 12px;
                color: {theme['text']};
            }}
            QWidget > QWidget {{
                background-color: transparent;
                border: none;
            }}
        """

    @classmethod
    def get_expanded_note_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QWidget#expandedNote {{
                border: 1px solid {theme['border']};
                border-radius: 15px;
                background-color: {theme['note_bg']};
                color: {theme['text']};
                min-width: 300px;
                min-height: 400px;
            }}
            QLineEdit, QTextEdit {{
                background-color: transparent;
                border: none;
                padding: 5px;
                min-width: 200px;
                color: {theme['text']};
            }}
            QLabel {{
                background-color: transparent;
                border: none;
                min-width: 100px;
                color: {theme['text']};
            }}
            QWidget > QWidget {{
                background-color: transparent;
                border: none;
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                border: 1px solid {theme['border']};
                border-radius: 10px;
                padding: 6px 12px;
                min-width: 80px;
                color: {theme['text']};
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
            QScrollBar:vertical {{
                border: none;
                background: transparent;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #f2f2f2;
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #e6e6e6;
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {{
                background: none;
            }}
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """

    SCREEN_STYLES = {
        'small': {
            'note_size': (120, 120),
            'note_font': '10px',
            'button_padding': '6px',
            'spacing': '30px'
        },
        'medium': {
            'note_size': (150, 150),
            'note_font': '12px',
            'button_padding': '8px',
            'spacing': '40px'
        },
        'large': {
            'note_size': (180, 180),
            'note_font': '14px',
            'button_padding': '10px',
            'spacing': '50px'
        }
    }

    DARK_MODE_BUTTON_STYLE = """
        QPushButton {
            border-radius: 15px;
            background-color: #ffffff;
            padding: 10px;
            text-align: right;
        }
    """

    NO_TAG_BUTTON_STYLE = """
        QPushButton {
            border-radius: 15px;
            background-color: #ffffff;
            padding: 10px;
            text-align: left;
        }
    """

    TEXT_EDIT_STYLE = """
        QTextEdit {
            border-radius: 15px;
            background-color: transparent;
            padding: 10px;
        }
    """

    NOTE_STYLE = """
        QWidget {
            border: 2px solid #dcdcdc;
            border-radius: 15px;
            background-color: #ffffff;
            text-align: left;
        }
        QLabel {
            background-color: transparent;
            border: none;
            padding: 0px;
            font-size: 12px;
        }
        QWidget > QWidget {
            background-color: transparent;
            border: none;
        }
    """

    EXPANDED_NOTE_STYLE = """
        QWidget#expandedNote {
            border: 1px solid #f2f2f2;
            border-radius: 15px;
            background-color: white;
            min-width: 300px;
            min-height: 400px;
        }
        QLineEdit, QTextEdit {
            background-color: transparent;
            border: none;
            padding: 5px;
            min-width: 200px;
        }
        QLabel {
            background-color: transparent;
            border: none;
            min-width: 100px;
        }
        QWidget > QWidget {
            background-color: transparent;
            border: none;
        }
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #f2f2f2;
            border-radius: 10px;
            padding: 6px 12px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #f0f0f0;
        }
    """

    MAIN_WIDGET_STYLE = """
        QMainWindow, QWidget {
            background-color: white;
        }
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background: #f2f2f2;
            min-height: 20px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: #e6e6e6;
        }

        QScrollBar::add-line:vertical {
            height: 0px;
        }

        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """

    ADD_BUTTON_STYLE = """
        background-color: #ffffff;
        border-radius: 15px;
        border: 1px solid #dcdcdc;
    """

    TAG_DIALOG_STYLE = """
        QDialog {
            background: transparent;
            border: none;
        }
        QWidget#tagSelectorContainer {
            background-color: white;
            border: 1px solid #f2f2f2;
            border-radius: 15px;
            padding: 10px;
            margin: 5px;
        }
        QPushButton {
            border-radius: 10px;
            padding: 5px 10px;
            margin: 2px;
            min-width: 60px;
        }
        QPushButton[text="OK"] {
            background-color: #f2f2f2;
            color: black;
            border: none;
            padding: 8px 16px;
        }
        QPushButton[text="OK"]:hover {
            background-color: #e6e6e6;
        }
    """

    TAG_SELECTOR_STYLE = """
        QDialog {
            background: transparent;
            border: none;
        }
        #tagSelectorContainer {
            background-color: white;
            border: 1px solid #f2f2f2;
            border-radius: 15px;
            padding: 10px;
        }
        QPushButton {
            border-radius: 10px;
            padding: 5px 10px;
            margin: 2px;
            min-width: 60px;
        }
        QPushButton[text="Вибрати тег"] {
            background-color: white;
            border: 1px solid #f2f2f2;
            border-radius: 15px;
            padding: 6px 12px;
            font-size: 12px;
        }
    """

    TAG_BUTTON_STYLE = """
        QPushButton {{
            background-color: {color};
            color: black;
            border-radius: 10px;
            padding: 6px 12px;
            margin: 4px;
        }}
        QPushButton:checked {{
            border: 2px solid black;
        }}
    """

    TAG_LABEL_STYLE = """
        background-color: {color};
        color: black;
        border-radius: 10px;
        padding: 6px 12px;
        border: none;
    """

    TOP_BAR_STYLE = """
        #searchContainer {
            background-color: #ff9633;
            min-height: 35px;
        }
        #searchField {
            border: 1px solid #f2f2f2;
            border-radius: 18px;
            background-color: white;
            padding: 6px 12px;
            min-width: 120px;
            font-size: 12px;
            margin: 0px;
        }
        QVBoxLayout {
            margin: 0;
            padding: 5px;
        }
        QHBoxLayout {
            margin: 0;
            padding: 0;
        }
        QPushButton {
            padding: 6px 12px;
            font-size: 12px;
            min-width: 10px;
        }
    """

    SEARCH_FIELD_STYLE = """
        QLineEdit {
            border: 1px solid #f2f2f2;
            border-radius: 18px;
            background-color: #ffffff;
            padding: 6px 12px;
            min-width: 120px;
            font-size: 12px;
        }
    """

    TAG_SELECT_BUTTON_STYLE = """
        QPushButton {
            background-color: #ffffff;
            border-radius: 15px;
            padding: 6px 12px;
            border: 1px solid #cccccc;
            font-size: 12px;
        }
    """

    CONTEXT_MENU_STYLE = """
        #menuContainer {
            background-color: #ffffff;
            border: 1px solid #f2f2f2;
            border-radius: 8px;
            padding: 4px;
        }

        QPushButton {
            background-color: white;
            border: none;
            padding: 5px 7px;
            text-align: center;
            border-radius: 5px;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #f0f0f0;
        }
    """

    REMINDERS_BUTTON_STYLE = """
        QPushButton {
            border-radius: 15px;
            background-color: #ffffff;
            padding: 10px;
            text-align: center;
        }
    """

    REMINDERS_WIDGET_STYLE = """
        QWidget#remindersContainer {
            background-color: #ffffff;
            border: 1px solid #f2f2f2;
            border-radius: 15px;
            padding: 10px;
            min-width: 250px;
            max-width: 400px;
            min-height: 300px;
            max-height: 600px;
        }
        QLabel {
            color: #333333;
            padding: 5px;
            background: transparent;
        }
        QLabel#reminderItem {
            background-color: #f0f0f0;
            border-radius: 8px;
            padding: 8px;
            margin: 2px;
        }
        QScrollArea {
            min-height: 200px;
            background: transparent;
            border: none;
        }
        QWidget#reminderContent {
            background: transparent;
        }
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background: #808080;
            min-height: 20px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: #666666;
        }

        QScrollBar::add-line:vertical {
            height: 0px;
        }

        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """

    NOTE_WRAPPER_STYLE = """
        QPushButton {
            border: 1px solid #f2f2f2;
            border-radius: 15px;
            background-color: #ffffff;
        }
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background: #f2f2f2;
            min-height: 20px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: #e6e6e6;
        }

        QScrollBar::add-line:vertical {
            height: 0px;
        }

        QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
    """

    EXPAND_BUTTON_STYLE = """
        QPushButton {
            background-color: #ff9633;
            color: white;
            border: none;
            border-radius: 20px;
            font-size: 24px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #e68a2e;
        }
    """

    REMINDER_ITEM_STYLE = """
        QWidget#remindersContainer {
            background-color: white;
            border: 1px solid #dcdcdc;
            border-radius: 15px;
            margin: 5px;
        }
        QLabel {
            color: #333333;
            padding: 5px;
            background: transparent;
        }
        QLabel#reminderItem {
            background-color: #f0f0f0;
            border-radius: 8px;
            padding: 8px;
            margin: 2px;
        }
        QScrollArea {
            min-height: 200px;
            background: transparent;
            border: none;
        }
    """

    REMINDER_SCROLLBAR_STYLE = """
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 12px;
            margin: 0px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background: #808080;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover {
            background: #666666;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            border: none;
            background: none;
            height: 0px;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none
        }
    """

    FLOATING_ADD_BUTTON_STYLE = """
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #f2f2f2;
            border-radius: 30px;
            position: fixed;
            bottom: 20px;
            right: 20px;
        }
        QPushButton:hover {
            background-color: #f0f0f0;
            border-color: #e6e6e6;
        }
    """

    DARK_MODE_SWITCH_STYLE = """
        QPushButton#dark_mode_switch {
            background-color: #ffffff;
            border: 1px solid #f2f2f2;
            border-radius: 15px;
            padding: 5px 10px;
            min-width: 50px;
            text-align: center;
        }
        QPushButton#dark_mode_switch:checked {
            background-color: #f2f2f2;
            color: black;
        }
    """

    @classmethod
    def get_dark_mode_switch_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QPushButton#dark_mode_switch {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 14px;
                padding: 5px 10px;
                min-width: 50px;
                text-align: center;
            }}
            QPushButton#dark_mode_switch:checked {{
                background-color: {theme['hover_bg']};
                color: {theme['text']};
            }}
        """

    @classmethod
    def get_search_field_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QLineEdit {{
                border-radius: 18px;
                background-color: {theme['note_bg']};
                color: {theme['text']};
                padding: 6px 10px;
                border: 1px solid {theme['border']};
                min-width: 120px;
                font-size: 12px;
            }}
        """

    @classmethod
    def get_top_bar_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QWidget {{
                background-color: {theme['topbar_bg']};
            }}
            QVBoxLayout {{
                margin: 0;
                padding: 5px;
            }}
            QHBoxLayout {{
                margin: 0;
                padding: 0;
            }}
            QLineEdit {{
                min-width: 120px;
                font-size: 12px;
            }}
            QPushButton {{
                padding: 6px 12px;
                font-size: 12px;
                min-width: 10px;
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """

    @classmethod
    def get_reminders_widget_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QWidget#remindersContainer {{
                background-color: {theme['note_bg']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                padding: 10px;
                min-width: 250px;
                max-width: 400px;
                min-height: 300px;
                max-height: 600px;
            }}
            QLabel {{
                color: {theme['text']};
                padding: 5px;
                background: transparent;
            }}
            QLabel#reminderItem {{
                background-color: {theme['button_bg']};
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
            }}
            QScrollArea {{
                min-height: 200px;
                background: transparent;
                border: none;
            }}
            QWidget#reminderContent {{
                background: transparent;
            }}
        """

    @classmethod
    def get_note_wrapper_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QPushButton {{
                border: 1px solid {theme['border']};
                border-radius: 15px;
                background-color: {theme['note_bg']};
                color: {theme['text']};
            }}
        """

    @classmethod
    def get_tag_selector_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QDialog {{
                background: transparent;
                border: none;
            }}
            #tagSelectorContainer {{
                background-color: {theme['note_bg']};
                border: 1px solid #f2f2f2;
                border-radius: 15px;
                padding: 10px;
            }}
            QPushButton {{
                border-radius: 10px;
                padding: 5px 10px;
                margin: 2px;
                min-width: 60px;
                background-color: {theme['button_bg']};
                color: {theme['text']};
            }}
            QPushButton#tag_confirm_btn {{
                border: 2px solid #f2f2f2;
                background-color: {theme['button_bg']};
                color: {theme['text']};
            }}
        """

    @classmethod
    def get_tag_button_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                padding: 10px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """

    TAG_LABEL_STYLE = """
        background-color: {color};
        color: black;
        border-radius: 10px;
        padding: 6px 12px;
        border: none;
    """

    @classmethod
    def get_context_menu_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            #menuContainer {{
                background-color: {theme['note_bg']};
                border: 1px solid {theme['border']};
                border-radius: 8px;
                padding: 4px;
            }}

            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border: none;
                padding: 5px 7px;
                text-align: center;
                border-radius: 5px;
                font-size: 14px;
            }}

            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """

    @classmethod
    def get_tag_dropdown_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QMenu {{
                background-color: {theme['note_bg']};
                border: 1.5px solid {theme['border']};
                border-radius: 10px;
                padding: 0px;
                outline: none;
            }}
            QWidgetAction > QWidget {{
                background: transparent;
                border: none;
                border-radius: 0px;
                margin: 0px;
                padding: 0px;
            }}
            QLabel {{
                background: transparent;
                border: none;
                border-radius: 0px;
                padding: 0px;
                margin: 0px;
            }}
        """

    @classmethod
    def get_tag_dropdown_button_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                padding: 8px 16px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """

    @classmethod
    def get_tag_select_button_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border-radius: 15px;
                padding: 6px 12px;
                border: 1px solid {theme['border']};
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """

    @classmethod
    def get_no_tag_button_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """

    @classmethod
    def get_scroll_area_style(cls, is_dark_mode):
        return """
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """

    @classmethod
    def get_scroll_area_viewport_style(cls, is_dark_mode):
        return "background-color: transparent;"

    @classmethod
    def get_scrollbar_style(cls, is_dark_mode):
        return """
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #f2f2f2;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #e6e6e6;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """

    @classmethod
    def get_notes_container_style(cls, is_dark_mode):
        return """
            QWidget {
                background-color: transparent;
            }
            QScrollArea {
                background: transparent;
                border: none;
            }
        """

    @classmethod
    def get_note_title_label_style(cls, is_dark_mode, font_size):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            font-size: {font_size};
            color: {theme['text']};
        """

    @classmethod
    def get_note_content_label_style(cls, is_dark_mode, font_size):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            color: {theme['text']};
            font-size: {font_size};
        """

    @classmethod
    def get_expanded_note_input_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            background-color: transparent;
            color: {theme['text']};
            border: none;
            padding: 5px;
        """

    @classmethod
    def get_floating_add_button_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        if is_dark_mode:
            button_bg = "#313131"
            border_color = "#444444"
        else:
            button_bg = "#ffffff"
            border_color = "#f2f2f2"
        return f"""
            QPushButton {{
                background-color: {button_bg};
                border: 1px solid {border_color};
                border-radius: 30px;
                position: fixed;
                bottom: 20px;
                right: 20px;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
                border-color: {theme['border']};
            }}
        """

    @classmethod
    def get_reminder_dialog_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QDialog {{
                background: transparent;
                border: none;
            }}
            QWidget#reminderDialogContainer {{
                background-color: {theme['note_bg']};
                border-radius: 18px;
                border: 2px solid {theme['border']};
            }}
            QLabel {{
                color: {theme['text']};
                background: transparent;
            }}
            QDateEdit, QTimeEdit {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border: 1.5px solid {theme['border']};
                border-radius: 10px;
                padding: 4px 6px;
                font-size: 14px;
                selection-background-color: #888888;
                selection-color: {theme['text']};
            }}
            QDateEdit::drop-down, QTimeEdit::down-arrow {{
                background: transparent;
            }}
            QDateEdit QAbstractItemView, QTimeEdit QAbstractItemView {{
                background: {theme['note_bg']};
                color: {theme['text']};
                selection-background-color: #888888;
                selection-color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border-radius: 12px;
                border: 1.5px solid {theme['border']};
                padding: 4px 12px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """

    @classmethod
    def get_expand_button_style_dark(cls):
        return """
            QPushButton {
                background-color: #222222;
                color: #ffffff;
                border: none;
                border-radius: 20px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #333333;
            }
        """

    @classmethod
    def get_tag_creation_widget_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QWidget#menuContainer {{
                background-color: {theme['note_bg']};
                border: 2px solid {theme['border']};
                border-radius: 18px;
                padding: 10px;
            }}
            QLineEdit {{
                border: 1.5px solid {theme['border']};
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 14px;
                background: {theme['background']};
                color: {theme['text']};
            }}
            QPushButton {{
                border: 1.5px solid {theme['border']};
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 14px;
                background: {theme['button_bg']};
                color: {theme['text']};
            }}
            QPushButton:hover {{
                background: {theme['hover_bg']};
            }}
        """

    @classmethod
    def get_reminder_item_frame_style(cls, is_dark_mode):
        border_color = "#646464" if is_dark_mode else "#ff9633"
        return f"""
            QFrame#reminderItemFrame {{
                border: 2px solid {border_color};
                border-radius: 10px;
                background-color: transparent;
                margin-bottom: 8px;
            }}
        """

    @classmethod
    def get_tag_delete_dialog_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QDialog {{
                background: transparent;
                border: none;
            }}
            #tagSelectorContainer {{
                background-color: {theme['note_bg']};
                border: 1px solid {theme['border']};
                border-radius: 15px;
                padding: 10px;
            }}
        """

    @classmethod
    def get_tag_delete_button_style(cls, color, is_selected, is_dark_mode):
        border = "2px solid #6E6E6E;" if is_selected else "none"
        text_color = "#fff" if is_dark_mode else "#000"
        return f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border-radius: 10px;
                padding: 6px 12px;
                border: {border};
                font-size: 13px;
            }}
        """

    @classmethod
    def get_tag_delete_confirm_button_style(cls, is_dark_mode):
        theme = cls.get_theme_styles(is_dark_mode)
        return f"""
            QPushButton {{
                background-color: {theme['button_bg']};
                color: {theme['text']};
                border-radius: 12px;
                border: 1.5px solid {theme['border']};
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme['hover_bg']};
            }}
        """




