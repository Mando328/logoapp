import sys
from pathlib import Path
import locale

# Ensure project root and this UI folder are on sys.path when running directly
ROOT_DIR = Path(__file__).resolve().parent.parent
UI_DIR = Path(__file__).resolve().parent
for p in (ROOT_DIR, UI_DIR):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)

from database import Child, session
from PySide6.QtCore import Qt, QSize, QDate   
from PySide6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QTextEdit,
    QFormLayout,
    QInputDialog,
    QMessageBox,
)
try:
    from style import apply_app_style
except ImportError:
    from UI.style import apply_app_style


TRANSLATIONS = {
    "pl": {
        "title": "LogoApp",
        "list_children": "Lista dzieci",
        "start_work": "Rozpocznij diagnozę",
        "user_settings": "Ustawienia użytkownika",
        "back": "Powrót do menu",
        "lang_toggle": "English",
        "lang_label": "Język",
        "add_child": "Dodaj dziecko",
        "first_name": "Imię",
        "last_name": "Nazwisko",
        "birth_date": "Data urodzenia",
        "gender": "Płeć (M/K)",
        "notes": "Notatki",
        "save": "Zapisz",
        "cancel": "Anuluj",
        "child_info": "Szczegóły dziecka",
        "delete_child": "Usuń dziecko",
        "edit_notes": "Edytuj notatki",
        "confirm_delete": "Czy na pewno chcesz usunąć to dziecko?",
        "delete_success": "Dziecko zostało usunięte.",
           "birth_date_label": "Data ur.:",
           "gender_label": "Płeć:",
           "notes_label": "Notatki:",
           "no_notes": "(brak notatek)",
    },
    "en": {
        "title": "LogoApp",
        "list_children": "Children list",
        "start_work": "Start diagnosis",
        "user_settings": "User settings",
        "back": "Back to menu",
        "lang_toggle": "Polski",
        "lang_label": "Language",
        "add_child": "Add child",
        "first_name": "First name",
        "last_name": "Last name",
        "birth_date": "Birth date",
        "gender": "Gender (M/F)",
        "notes": "Notes",
        "save": "Save",
        "cancel": "Cancel",
        "child_info": "Child details",
        "delete_child": "Delete child",
        "edit_notes": "Edit notes",
        "confirm_delete": "Are you sure you want to delete this child?",
        "delete_success": "Child has been deleted.",
           "birth_date_label": "Birth date:",
           "gender_label": "Gender:",
           "notes_label": "Notes:",
           "no_notes": "(no notes)",
    },
}


def detect_default_language():
    """Detect system language (two-letter) and fall back to en if unsupported."""
    try:
        lang = locale.getlocale()[0] or "en_US"
    except Exception:
        lang = "en_US"
    lang_code = (lang or "en")[:2].lower()
    return lang_code if lang_code in TRANSLATIONS else "en"


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        #window attributes
        self.setWindowTitle("LogoApp")
        self.setMinimumSize(QSize(600, 400))
        self.language = detect_default_language()

        # Stacked views: menu and children list
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        # Main menu view
        self.menu_widget = QWidget()
        menu_layout = QVBoxLayout(self.menu_widget)
        buttons_row = QHBoxLayout()
        self.btn_open_children = QPushButton("Lista dzieci")
        self.btn_start_working = QPushButton("Rozpocznij pracę z dziećmi")
        self.btn_user_settings = QPushButton("Ustawienia użytkownika")
        buttons_row.addWidget(self.btn_open_children)
        buttons_row.addWidget(self.btn_start_working)
        buttons_row.addWidget(self.btn_user_settings)
        menu_layout.addLayout(buttons_row)
        self.stacked.addWidget(self.menu_widget)

        # Children list view
        self.children_widget = QWidget()
        children_layout = QVBoxLayout(self.children_widget)
        self.list = QListWidget()
        self.btn_add_child = QPushButton("Dodaj dziecko")
        self.btn_back = QPushButton("Powrót do menu")
        children_buttons = QHBoxLayout()
        children_buttons.addWidget(self.btn_back)
        children_buttons.addStretch(1)
        children_buttons.addWidget(self.btn_add_child)
        children_layout.addWidget(self.list)
        children_layout.addLayout(children_buttons)
        self.stacked.addWidget(self.children_widget)

        # Add-child view
        self.add_child_widget = QWidget()
        add_layout = QVBoxLayout(self.add_child_widget)
        add_layout.setContentsMargins(24, 24, 24, 24)
        add_layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(8)
        self.lbl_first_name = QLabel("Imię")
        self.input_first_name = QLineEdit()
        self.lbl_last_name = QLabel("Nazwisko")
        self.input_last_name = QLineEdit()
        self.lbl_birth_date = QLabel("Data urodzenia")
        self.input_birth_date = QDateEdit()
        self.input_birth_date.setCalendarPopup(True)
        self.input_birth_date.setDisplayFormat("dd.MM.yyyy")
        self.input_birth_date.setDate(QDate.currentDate())
        self.lbl_gender = QLabel("Płeć (M/K)")
        self.input_gender = QComboBox()
        self.input_gender.addItems(["", "M", "K", "F"])
        self.lbl_notes = QLabel("Notatki")
        self.input_notes = QTextEdit()
        form.addRow(self.lbl_first_name, self.input_first_name)
        form.addRow(self.lbl_last_name, self.input_last_name)
        form.addRow(self.lbl_birth_date, self.input_birth_date)
        form.addRow(self.lbl_gender, self.input_gender)
        form.addRow(self.lbl_notes, self.input_notes)
        add_layout.addLayout(form)
        add_buttons = QHBoxLayout()
        self.btn_add_save = QPushButton("Zapisz")
        self.btn_add_cancel = QPushButton("Anuluj")
        add_buttons.addWidget(self.btn_add_save)
        add_buttons.addStretch(1)
        add_buttons.addWidget(self.btn_add_cancel)
        add_layout.addLayout(add_buttons)
        self.stacked.addWidget(self.add_child_widget)

        # Settings view
        self.settings_widget = QWidget()
        settings_layout = QVBoxLayout(self.settings_widget)
        settings_layout.setContentsMargins(24, 24, 24, 24)
        settings_layout.setSpacing(12)
        self.lang_label = QLabel("Język")
        self.btn_toggle_language = QPushButton("English")
        self.btn_settings_back = QPushButton("Powrót do menu")
        settings_layout.addWidget(self.lang_label)
        settings_layout.addWidget(self.btn_toggle_language)
        settings_layout.addStretch(1)
        settings_layout.addWidget(self.btn_settings_back)
        self.stacked.addWidget(self.settings_widget)

        # Child info view (dynamically populated per child)
        self.child_info_widget = QWidget()
        self.child_info_layout = QVBoxLayout(self.child_info_widget)
        self.child_info_layout.setContentsMargins(24, 24, 24, 24)
        self.child_info_layout.setSpacing(12)
        self.lbl_child_full_name = QLabel()
        self.lbl_child_birth = QLabel()
        self.lbl_child_gender = QLabel()
        self.lbl_child_notes = QLabel()
        self.child_info_layout.addWidget(self.lbl_child_full_name)
        self.child_info_layout.addWidget(self.lbl_child_birth)
        self.child_info_layout.addWidget(self.lbl_child_gender)
        self.lbl_notes_title = QLabel("Notatki")
        self.child_info_layout.addWidget(self.lbl_notes_title)
        self.lbl_child_notes.setWordWrap(True)
        self.child_info_layout.addWidget(self.lbl_child_notes)
        self.child_info_layout.addStretch(1)
        # Buttons for delete and edit notes
        child_action_buttons = QHBoxLayout()
        self.btn_edit_notes = QPushButton("Edytuj notatki")
        self.btn_delete_child = QPushButton("Usuń dziecko")
        child_action_buttons.addWidget(self.btn_delete_child)
        child_action_buttons.addWidget(self.btn_edit_notes)
        child_action_buttons.addStretch(1)
        self.child_info_layout.addLayout(child_action_buttons)
        self.btn_child_info_back = QPushButton("Powrót do listy")
        self.child_info_layout.addWidget(self.btn_child_info_back)
        self.stacked.addWidget(self.child_info_widget)


        # Wiring actions
        self.btn_open_children.clicked.connect(self.show_children_view)
        self.btn_back.clicked.connect(self.show_menu_view)
        self.btn_add_child.clicked.connect(self.show_add_child_view)
        self.btn_user_settings.clicked.connect(self.show_settings_view)
        self.btn_toggle_language.clicked.connect(self.toggle_language)
        self.btn_settings_back.clicked.connect(self.show_menu_view)
        self.list.itemClicked.connect(self.on_child_clicked)
        self.btn_add_cancel.clicked.connect(self.show_children_view)
        self.btn_add_save.clicked.connect(self.add_child)
        self.btn_child_info_back.clicked.connect(self.show_children_view)
        self.btn_edit_notes.clicked.connect(self.edit_child_notes)
        self.btn_delete_child.clicked.connect(self.delete_child_with_confirmation)
        
        # Track current child ID for edit/delete operations
        self.current_child_id = None
        
        # Apply initial translations
        self.apply_translations()

    def populate_children_list(self):
        self.list.clear()
        for i in session.query(Child).all():
            item = QListWidgetItem(f"{i.first_name} {i.last_name}")
            item.setData(Qt.UserRole, i.id)
            self.list.addItem(item)

    def show_children_view(self):
        self.populate_children_list()
        self.stacked.setCurrentWidget(self.children_widget)

    def show_menu_view(self):
        self.stacked.setCurrentWidget(self.menu_widget)

    def show_settings_view(self):
        self.stacked.setCurrentWidget(self.settings_widget)

    def populate_children_list(self):
        self.list.clear()
        for i in session.query(Child).all():
            item = QListWidgetItem(f"{i.first_name} {i.last_name}")
            item.setData(Qt.UserRole, i.id)
            self.list.addItem(item)

    def show_children_view(self):
        self.populate_children_list()
        self.stacked.setCurrentWidget(self.children_widget)

    def show_menu_view(self):
        self.stacked.setCurrentWidget(self.menu_widget)

    def show_settings_view(self):
        self.stacked.setCurrentWidget(self.settings_widget)

    def apply_translations(self):
        t = TRANSLATIONS[self.language]
        self.setWindowTitle(t["title"])
        self.btn_open_children.setText(t["list_children"])
        self.btn_start_working.setText(t["start_work"])
        self.btn_user_settings.setText(t["user_settings"])
        self.btn_add_child.setText(t["add_child"])
        self.btn_back.setText(t["back"])
        self.btn_settings_back.setText(t["back"])
        self.btn_toggle_language.setText(t["lang_toggle"])
        self.lbl_first_name.setText(t["first_name"])
        self.lbl_last_name.setText(t["last_name"])
        self.lbl_birth_date.setText(t["birth_date"])
        self.lbl_gender.setText(t["gender"])
        self.lbl_notes.setText(t["notes"])
        self.btn_add_save.setText(t["save"])
        self.btn_add_cancel.setText(t["cancel"])
        self.btn_child_info_back.setText(t["back"])
        self.btn_edit_notes.setText(t["edit_notes"])
        self.btn_delete_child.setText(t["delete_child"])
        self.lang_label.setText(t["lang_label"])
        self.lbl_notes_title.setText(t["notes_label"])

    def toggle_language(self):
        self.language = "en" if self.language == "pl" else "pl"
        self.apply_translations()

    def show_add_child_view(self):
        self.stacked.setCurrentWidget(self.add_child_widget)
        self.stacked.setCurrentWidget(self.add_child_widget)

    def clear_add_child_form(self):
        self.input_first_name.clear()
        self.input_last_name.clear()
        self.input_birth_date.setDate(QDate.currentDate())
        self.input_gender.setCurrentIndex(0)
        self.input_notes.clear()

    def add_child(self):
        first = self.input_first_name.text().strip()
        last = self.input_last_name.text().strip()
        if not first or not last:
            print("Brak imienia lub nazwiska.")
            return
        birth = self.input_birth_date.date().toPython()
        gender = self.input_gender.currentText().strip()
        notes = self.input_notes.toPlainText().strip()

        new_child = Child(
            first_name=first,
            last_name=last,
            birth_date=birth,
            gender=gender if gender else None,
            notes=notes if notes else None,
        )
        session.add(new_child)
        session.commit()
        print(f"Dodano dziecko ID: {new_child.id}")
        self.clear_add_child_form()
        self.populate_children_list()
        self.show_children_view()

    def on_child_clicked(self, item):
        child_id = item.data(Qt.UserRole)
        self.current_child_id = child_id
        child = session.query(Child).filter_by(id=child_id).first()
        if child:
            t = TRANSLATIONS[self.language]
            self.lbl_child_full_name.setText(f"<b>{child.first_name} {child.last_name}</b>")
            self.lbl_child_birth.setText(f"<b>{t['birth_date_label']}</b> {child.birth_date}")
            self.lbl_child_gender.setText(f"<b>{t['gender_label']}</b> {child.gender if child.gender else 'N/A'}")
            self.lbl_child_notes.setText(f"{child.notes if child.notes else t['no_notes']}")
            self.stacked.setCurrentWidget(self.child_info_widget)
            print(f"Wybrano dziecko ID: {child_id}")

    def edit_child_notes(self):
        if not self.current_child_id:
            return
        child = session.query(Child).filter_by(id=self.current_child_id).first()
        if not child:
            return
        # Simple dialog-like approach: use input from a simple window
        new_notes, ok = QInputDialog.getMultiLineText(
            self, "Edytuj notatki", "Notatki:", child.notes or ""
        )
        if ok:
            child.notes = new_notes.strip() if new_notes.strip() else None
            session.commit()
            print(f"Notatki dziecka ID {self.current_child_id} zostały zaktualizowane.")
            # Re-fetch to update display
            child = session.query(Child).filter_by(id=self.current_child_id).first()
            t = TRANSLATIONS[self.language]
            self.lbl_child_notes.setText(f"{child.notes if child.notes else t['no_notes']}")

    def delete_child_with_confirmation(self):
        if not self.current_child_id:
            return
        t = TRANSLATIONS[self.language]
        result = QMessageBox.question(
            self, 
            "Potwierdzenie", 
            t["confirm_delete"],
            QMessageBox.Yes | QMessageBox.No
        )
        if result == QMessageBox.Yes:
            self.delete_child()

    def delete_child(self):
        if not self.current_child_id:
            return
        child = session.query(Child).filter_by(id=self.current_child_id).first()
        if not child:
            return
        
        # Delete all examinations and answers first (cascade)
        for exam in child.examinations:
            for answer in exam.answers:
                session.delete(answer)
            session.delete(exam)
        
        session.delete(child)
        session.commit()
        t = TRANSLATIONS[self.language]
        print(f"{t['delete_success']}")
        self.current_child_id = None
        self.show_children_view()
    
if __name__ == "__main__":
    # This module defines the UI; use main.py or run.py to start the app.
    print("LogoApp: uruchom aplikację poprzez main.py lub run.py.")
    import sys
    sys.exit(0)