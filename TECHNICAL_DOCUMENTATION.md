# LogoApp — Technical Documentation (English)

This document provides comprehensive technical documentation for the LogoApp project, including architecture, library descriptions, function documentation, database schema, and development guidelines.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Dependencies & Libraries](#dependencies--libraries)
4. [Directory Structure](#directory-structure)
5. [Database Models](#database-models)
6. [Module Documentation](#module-documentation)
7. [UI Components & Navigation](#ui-components--navigation)
8. [Internationalization (i18n)](#internationalization-i18n)
9. [Styling](#styling)
10. [Running the Application](#running-the-application)
11. [Development Guidelines](#development-guidelines)

---

## Project Overview

**LogoApp** is a desktop application designed to assist speech therapists (logopedists) in managing patient records, conducting assessments, and storing clinical data locally. The application emphasizes data privacy by storing all information in a local SQLite database rather than cloud-based storage.

### Core Objectives

- Provide a user-friendly interface for patient management
- Support multilingual interfaces (Polish and English)
- Maintain data integrity through proper ORM usage
- Ensure no patient data is exposed to external services

### Technology Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.11+ |
| GUI Framework | PySide6 (Qt6) | Latest |
| ORM | SQLAlchemy | 2.x |
| Database | SQLite | 3.x |
| Styling | QSS (Qt Style Sheets) | Custom |

---

## Architecture

### High-Level Design

LogoApp follows a **Model-View-Controller (MVC)** pattern:

```
┌─────────────────────────────────────────────────────────┐
│                    PySide6 GUI Layer                     │
│  (UI/UI.py: MainWindow, Widgets, Event Handlers)        │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              Application Logic Layer                     │
│  (Signal handling, form validation, navigation)         │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│          SQLAlchemy ORM Layer                           │
│  (database.py: Models, Session Management)              │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────┐
│              SQLite Database                            │
│  (logopedia.db: Tables, Indexes, Constraints)          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Action** → Click button in UI
2. **Signal Emission** → Qt signal emitted (e.g., `clicked.connect()`)
3. **Handler Execution** → Slot method called (e.g., `on_child_clicked()`)
4. **Validation** → Input checked for validity
5. **ORM Operation** → SQLAlchemy query or insert/update/delete
6. **Database Commit** → `session.commit()` persists to SQLite
7. **UI Update** → `populate_children_list()` refreshes display

---

## Dependencies & Libraries

### 3.1 Python Standard Library

#### `datetime`
- **Usage**: Represent and manipulate dates
- **Key Classes**:
  - `date(year, month, day)` — Immutable date object
- **Application**: Child birth dates, examination dates

```python
from datetime import date
birth_date = date(2015, 5, 10)  # May 10, 2015
```

#### `locale`
- **Usage**: Access system locale information for language detection
- **Key Functions**:
  - `locale.getlocale()` — Returns tuple `(language_code, encoding)`, e.g., `('pl_PL', 'UTF-8')`
- **Application**: Auto-detect system language (Polish or English)

```python
lang = locale.getlocale()[0]  # e.g., "pl_PL"
lang_code = lang[:2].lower()  # Extract "pl"
```

#### `pathlib`
- **Usage**: Object-oriented file path handling
- **Key Classes**:
  - `Path(string)` — Create platform-independent path objects
- **Application**: Construct sys.path entries for module imports

```python
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
```

#### `sys`
- **Usage**: System-specific parameters and functions
- **Key Attributes**:
  - `sys.path` — List of module search paths
  - `sys.argv` — Command-line arguments
  - `sys.exit(code)` — Exit with status code
- **Application**: Manage module paths, retrieve CLI args, graceful shutdown

```python
sys.path.insert(0, str(ROOT_DIR))
app = QApplication(sys.argv)
```

---

### 3.2 SQLAlchemy 2.x (ORM)

**Purpose**: Object-Relational Mapping library to interact with SQLite database using Python objects instead of raw SQL.

#### Core Components

**`create_engine(url, **options)`**
- Creates database connection engine
- `url = "sqlite:///logopedia.db"` — Relative path to local SQLite file
- `echo=False` — Suppress SQL logging (set `True` for debugging)

```python
from sqlalchemy import create_engine
engine = create_engine("sqlite:///logopedia.db", echo=False)
```

**`declarative_base()`**
- Factory function returning a base class for ORM models
- All model classes inherit from this base
- Tracks model definitions for schema creation

```python
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Child(Base):
    __tablename__ = "children"
    # ... columns
```

**`Column(type, **kwargs)`**
- Defines table columns with types and constraints
- Common types:
  - `Integer` — 32-bit/64-bit integer
  - `String` — Variable-length text (max length optional)
  - `Date` — Date object (stored as ISO string in SQLite)
  - `Text` — Unlimited text
  - `ForeignKey(table.column)` — Reference to another table
- Common kwargs:
  - `primary_key=True` — Mark as primary key
  - `nullable=False` — Disallow NULL values
  - `default=value` — Default value on insert

```python
class Child(Base):
    __tablename__ = "children"
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
```

**`ForeignKey(table.column)`**
- Establishes referential integrity between tables
- Prevents orphaned records
- Enables relationship navigation

```python
class Examination(Base):
    __tablename__ = "examinations"
    child_id = Column(Integer, ForeignKey("children.id"))
```

**`relationship(Model, back_populates=...)`**
- Python-side relationship between models (not stored in DB)
- Enables attribute access to related objects

```python
# In Child model:
examinations = relationship("Examination", back_populates="child")

# Usage:
child = session.query(Child).first()
for exam in child.examinations:  # Automatic lazy-load
    print(exam.date)
```

**`sessionmaker(bind=engine)`**
- Factory for creating database sessions
- Each session = database transaction context

```python
Session = sessionmaker(bind=engine)
session = Session()  # Open transaction
```

**`session.query(Model).all()`**
- Retrieve all rows of a model as objects
- Returns list of model instances

```python
all_children = session.query(Child).all()
for child in all_children:
    print(child.first_name)
```

**`session.query(Model).filter_by(column=value).first()`**
- Retrieve first row matching condition
- Returns single model instance or None

```python
child = session.query(Child).filter_by(id=1).first()
```

**`session.add(obj)` / `session.delete(obj)` / `session.commit()`**
- `add()` — Stage object for insert
- `delete()` — Stage object for delete
- `commit()` — Flush staged changes to database (transaction commit)

```python
new_child = Child(first_name="Jan", last_name="Kowalski", ...)
session.add(new_child)
session.commit()  # INSERT INTO children ...
```

---

### 3.3 PySide6 (Qt6 Python Bindings)

**Purpose**: Cross-platform GUI framework for building desktop applications.

#### Core Classes

**`QApplication(sys.argv)`**
- Main application object (singleton-like)
- Manages GUI application control and settings
- **Must** be instantiated before creating any widgets

```python
from PySide6.QtWidgets import QApplication
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
```

**`QMainWindow`**
- Top-level window widget
- Provides application-level frame (title bar, menu bar, status bar)
- Takes a central widget via `setCentralWidget(widget)`

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogoApp")
        self.setCentralWidget(central_widget)
```

**`QStackedWidget`**
- Container that displays one widget at a time
- Enables view switching without destroying/recreating widgets
- Provides `setCurrentWidget(widget)` to switch views

```python
self.stacked = QStackedWidget()
self.stacked.addWidget(self.menu_widget)
self.stacked.addWidget(self.children_widget)
self.stacked.setCurrentWidget(self.children_widget)  # Switch view
```

**Layout Classes**
- **`QVBoxLayout`** — Arranges widgets vertically (top to bottom)
- **`QHBoxLayout`** — Arranges widgets horizontally (left to right)
- **`QFormLayout`** — Pairs labels with input widgets (label | input)

```python
layout = QVBoxLayout()
layout.addWidget(label)
layout.addWidget(button)
widget.setLayout(layout)
```

**Input Widgets**
- **`QLineEdit`** — Single-line text input
- **`QTextEdit`** — Multi-line text input
- **`QDateEdit`** — Date picker widget
- **`QComboBox`** — Dropdown selector
- **`QPushButton`** — Clickable button

```python
self.input_name = QLineEdit()
self.input_date = QDateEdit()
self.input_date.setDisplayFormat("dd.MM.yyyy")
self.input_gender = QComboBox()
self.input_gender.addItems(["", "M", "K", "F"])
```

**Display Widgets**
- **`QLabel`** — Static or dynamic text display
- **`QListWidget`** — Scrollable list of items
- **`QListWidgetItem`** — Individual list entry

```python
label = QLabel("Hello, World!")
list_widget = QListWidget()
item = QListWidgetItem("Child Name")
item.setData(Qt.UserRole, child_id)  # Store metadata
list_widget.addItem(item)
```

**Dialog Classes**
- **`QMessageBox`** — Modal dialog for messages/confirmations
  - `question(parent, title, text, buttons)` — Yes/No dialog
  - Returns `QMessageBox.Yes` or `QMessageBox.No`
- **`QInputDialog`** — Modal dialog for user input
  - `getMultiLineText(parent, title, label, default_text)` — Multi-line input

```python
reply = QMessageBox.question(
    self, "Confirm", "Delete this child?",
    QMessageBox.Yes | QMessageBox.No
)
if reply == QMessageBox.Yes:
    delete_child()

new_notes, ok = QInputDialog.getMultiLineText(
    self, "Edit Notes", "Notes:", current_notes
)
if ok:
    child.notes = new_notes
```

**Signals & Slots**
- **Signal**: Event emitted by widget (e.g., button click)
- **Slot**: Method called when signal emitted
- **Connection**: `widget.signal.connect(method)`

```python
self.btn_add.clicked.connect(self.add_child)
# When btn_add is clicked, self.add_child() is called
```

**Qt Enums & Core Classes**
- **`Qt.UserRole`** — Custom data role for storing metadata in items
- **`QSize(width, height)`** — Represent widget size
- **`QDate.currentDate()`** — Get today's date as QDate object
- **`QDate.toPython()`** — Convert QDate to Python `datetime.date`

```python
self.setMinimumSize(QSize(600, 400))
current = QDate.currentDate()
python_date = current.toPython()  # datetime.date object
```

---

## Directory Structure

```
logoapp/
├── run.py                          # Official launcher (recommended entry point)
├── main.py                         # Alternate launcher + CLI helpers
├── database.py                     # SQLAlchemy models & session setup
│
├── UI/
│   ├── __init__.py                # Package marker
│   ├── UI.py                      # MainWindow & all views
│   └── style.py                   # QSS stylesheet & apply_app_style()
│
├── logopedia.db                    # SQLite database (local, not in Git)
├── .gitignore                      # Ignore .db, venv, DOCS_PL.md
├── README.md                       # Casual project overview
├── DOCS_PL.md                      # Polish technical docs (local only)
├── TECHNICAL_DOCUMENTATION.md      # This file
│
└── .venv/                          # Virtual environment (not in Git)
    ├── bin/ or Scripts/
    └── lib/
```

---

## Database Models

### Entity-Relationship Diagram

```
┌──────────────┐
│    Child     │
├──────────────┤
│ id (PK)      │◄───┐
│ first_name   │    │
│ last_name    │    │
│ birth_date   │    │
│ gender       │    │ 1:N
│ notes        │    │
└──────────────┘    │
                    │
            ┌───────┴──────────┐
            │                  │
    ┌───────────────┐   ┌─────────────┐
    │ Examination   │   │   Answer    │
    ├───────────────┤   ├─────────────┤
    │ id (PK)       │   │ id (PK)     │
    │ child_id (FK) │───│ exam_id(FK) │
    │ date          │   │ question_id │
    │ exam_type     │   │ answer_val  │
    │ conclusions   │   └─────────────┘
    └───────────────┘
```

### `Child` Model

Represents a patient/child in therapy.

```python
class Child(Base):
    __tablename__ = "children"
    
    # Columns
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=True)  # e.g., "M", "K", "F"
    notes = Column(Text, nullable=True)     # Clinical notes
    
    # Relationships
    examinations = relationship("Examination", back_populates="child")
```

**Attributes**:
- `id` — Auto-incrementing primary key
- `first_name`, `last_name` — Required identity fields
- `birth_date` — Required date of birth
- `gender` — Optional gender indicator
- `notes` — Optional clinical observations

**Relationships**:
- One-to-Many with `Examination` — A child can have multiple exams

---

### `Examination` Model

Represents a diagnostic session with a child.

```python
class Examination(Base):
    __tablename__ = "examinations"
    
    # Columns
    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey("children.id"))
    date = Column(Date, default=datetime.date.today)
    exam_type = Column(String, nullable=True)        # e.g., "articulation", "fluency"
    conclusions = Column(Text, nullable=True)        # Diagnostic conclusion
    
    # Relationships
    child = relationship("Child", back_populates="examinations")
    answers = relationship("Answer", back_populates="examination")
```

**Attributes**:
- `id` — Auto-incrementing primary key
- `child_id` — Foreign key to `Child`
- `date` — Examination date (defaults to today)
- `exam_type` — Type/category of exam
- `conclusions` — Clinical conclusions from exam

**Relationships**:
- Many-to-One with `Child` — Each exam belongs to one child
- One-to-Many with `Answer` — An exam can have multiple answers

---

### `Answer` Model

Represents a single response within an examination (not yet heavily used).

```python
class Answer(Base):
    __tablename__ = "answers"
    
    # Columns
    id = Column(Integer, primary_key=True)
    examination_id = Column(Integer, ForeignKey("examinations.id"))
    question_id = Column(String, nullable=False)     # e.g., "r_articulation"
    answer_value = Column(String, nullable=False)    # Response value
    
    # Relationships
    examination = relationship("Examination", back_populates="answers")
```

**Attributes**:
- `id` — Auto-incrementing primary key
- `examination_id` — Foreign key to `Examination`
- `question_id` — Identifier for question being answered
- `answer_value` — The response

---

## Module Documentation

### `database.py`

Handles database initialization, ORM model definitions, and session management.

#### Initialization

```python
engine = create_engine("sqlite:///logopedia.db", echo=False)
Base = declarative_base()
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
```

**What happens**:
1. Engine connects to `logopedia.db`
2. Base class created for ORM models
3. All tables created (if not exist)
4. Session factory created and global session instantiated

#### Helper Functions

**`connect_to_db()`**
- Returns native SQLite connection (not ORM)
- Useful for raw SQL queries if needed
- Not heavily used in current version

```python
def connect_to_db():
    import sqlite3
    return sqlite3.connect("logopedia.db")
```

**`init_db()`**
- Explicitly initialize database schema
- Calls `Base.metadata.create_all(engine)`
- Idempotent (safe to call multiple times)

```python
def init_db():
    Base.metadata.create_all(engine)
```

**`get_all_children(session)`**
- Retrieve all children from database
- Returns list of `Child` objects
- Simple wrapper around `session.query(Child).all()`

```python
def get_all_children(session):
    return session.query(Child).all()

children = get_all_children(session)
for child in children:
    print(f"{child.first_name} {child.last_name}")
```

---

### `main.py`

Entry point with styling and optional CLI helpers.

#### Imports

```python
from datetime import date
import sys
from PySide6.QtWidgets import QApplication
from UI.UI import MainWindow
from database import Child, session
from UI.style import apply_app_style
```

#### GUI Launch (Main Block)

```python
if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_app_style(app)  # Apply global QSS
    window = MainWindow()
    window.show()
    app.exec()
```

**Flow**:
1. Create `QApplication`
2. Apply stylesheet globally
3. Create main window
4. Show window
5. Enter Qt event loop (blocks until window closed)

#### CLI Helper Functions (Legacy)

**`add_new_child(session)`**
- Prompts user for child data via console
- Creates `Child` object and commits

```python
def add_new_child(session):
    first_name = input("Podaj imię dziecka: ")
    last_name = input("Podaj nazwisko dziecka: ")
    # ... more prompts
    new_child = Child(
        first_name=first_name,
        last_name=last_name,
        birth_date=date(...),
        ...
    )
    session.add(new_child)
    session.commit()
    print("Dziecko zostało dodane do bazy.")
```

**`print_all_children(session)`**
- Lists all children in console

```python
def print_all_children(session):
    children = session.query(Child).all()
    if not children:
        print("Brak dzieci w bazie.")
        return
    for child in children:
        print(f"{child.id} - {child.first_name} {child.last_name} ...")
```

**`delete_child_by_id(session, child_id)`**
- Delete child and cascade-delete related exams/answers

```python
def delete_child_by_id(session, child_id):
    child = session.query(Child).filter_by(id=child_id).first()
    if not child:
        print(f"Child ID {child_id} not found")
        return
    
    # Cascade delete
    for exam in child.examinations:
        for answer in exam.answers:
            session.delete(answer)
        session.delete(exam)
    session.delete(child)
    session.commit()
    print(f"Child ID {child_id} deleted.")
```

---

### `run.py`

Official launcher—clean entry point without CLI clutter.

```python
import sys
from PySide6.QtWidgets import QApplication
from UI.UI import MainWindow
from UI.style import apply_app_style

def main():
    app = QApplication(sys.argv)
    apply_app_style(app)
    window = MainWindow()
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
```

**Recommended launch method**:
```bash
python run.py
```

---

### `UI/UI.py`

Core GUI module containing `MainWindow` class and all views.

#### Module Setup

```python
import sys, locale
from pathlib import Path
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QPushButton, QListWidget, ...
)
from database import Child, session
from UI.style import apply_app_style  # With fallback import

# Ensure imports work regardless of execution context
ROOT_DIR = Path(__file__).resolve().parent.parent
UI_DIR = Path(__file__).resolve().parent
for p in (ROOT_DIR, UI_DIR):
    sp = str(p)
    if sp not in sys.path:
        sys.path.insert(0, sp)
```

#### Translations Dictionary

```python
TRANSLATIONS = {
    "pl": {
        "title": "LogoApp",
        "list_children": "Lista dzieci",
        "first_name": "Imię",
        "notes": "Notatki",
        "confirm_delete": "Czy na pewno chcesz usunąć to dziecko?",
        ...
    },
    "en": {
        "title": "LogoApp",
        "list_children": "Children list",
        "first_name": "First name",
        "notes": "Notes",
        "confirm_delete": "Are you sure you want to delete this child?",
        ...
    }
}
```

**Purpose**: Centralized locale-specific strings.

#### Language Detection

```python
def detect_default_language():
    """Auto-detect system language (two-letter code)."""
    try:
        lang = locale.getlocale()[0] or "en_US"
    except Exception:
        lang = "en_US"
    lang_code = (lang or "en")[:2].lower()
    return lang_code if lang_code in TRANSLATIONS else "en"
```

**Returns**: `"pl"` for Polish systems, `"en"` for others.

---

#### MainWindow Class

**Constructor (`__init__`)**

Builds 5 main views in a `QStackedWidget`:

1. **Menu View** — 3 buttons: List Children, Start Work, Settings
2. **Children List View** — `QListWidget` + Add/Back buttons
3. **Add Child Form** — `QFormLayout` with fields + Save/Cancel
4. **Settings View** — Language toggle + Back button
5. **Child Details View** — Info display + Edit Notes/Delete buttons

At end of `__init__`:
- Connect all signals to slots
- Set `self.current_child_id = None`
- Call `self.apply_translations()`

```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogoApp")
        self.setMinimumSize(QSize(600, 400))
        self.language = detect_default_language()
        
        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)
        
        # Build 5 views...
        self.stacked.addWidget(self.menu_widget)
        self.stacked.addWidget(self.children_widget)
        # ... etc
        
        # Wire signals
        self.btn_add_child.clicked.connect(self.show_add_child_view)
        # ... etc
        
        self.current_child_id = None
        self.apply_translations()
```

---

#### Navigation Methods

**`populate_children_list()`**
- Query all children from DB
- Clear and repopulate `QListWidget`
- Each item stores `id` in `Qt.UserRole`

```python
def populate_children_list(self):
    self.list.clear()
    for child in session.query(Child).all():
        item = QListWidgetItem(f"{child.first_name} {child.last_name}")
        item.setData(Qt.UserRole, child.id)
        self.list.addItem(item)
```

**`show_children_view()` / `show_menu_view()` / `show_settings_view()` / `show_add_child_view()`**
- Switch view via `self.stacked.setCurrentWidget(widget)`
- `show_children_view()` also calls `populate_children_list()` to refresh

---

#### Internationalization Methods

**`apply_translations()`**
- Fetch language dict from `TRANSLATIONS[self.language]`
- Update all widget text (buttons, labels, etc.)

```python
def apply_translations(self):
    t = TRANSLATIONS[self.language]
    self.setWindowTitle(t["title"])
    self.btn_open_children.setText(t["list_children"])
    # ... update all widgets
```

**`toggle_language()`**
- Switch `self.language` between "pl" and "en"
- Immediately call `apply_translations()` to update UI

```python
def toggle_language(self):
    self.language = "en" if self.language == "pl" else "pl"
    self.apply_translations()
```

---

#### Form Management

**`clear_add_child_form()`**
- Reset all input fields to defaults
- Used after successful add or when switching views

```python
def clear_add_child_form(self):
    self.input_first_name.clear()
    self.input_last_name.clear()
    self.input_birth_date.setDate(QDate.currentDate())
    self.input_gender.setCurrentIndex(0)
    self.input_notes.clear()
```

**`add_child()`**
- Validate required fields (first/last name)
- Build `Child` object from form inputs
- Add to session, commit
- Clear form, refresh list, return to children view

```python
def add_child(self):
    first = self.input_first_name.text().strip()
    last = self.input_last_name.text().strip()
    if not first or not last:
        print("Name fields required")
        return
    
    birth = self.input_birth_date.date().toPython()
    gender = self.input_gender.currentText().strip()
    notes = self.input_notes.toPlainText().strip()
    
    new_child = Child(
        first_name=first,
        last_name=last,
        birth_date=birth,
        gender=gender or None,
        notes=notes or None,
    )
    session.add(new_child)
    session.commit()
    
    self.clear_add_child_form()
    self.populate_children_list()
    self.show_children_view()
```

---

#### Child Details & Operations

**`on_child_clicked(item)`**
- Called when user clicks item in children list
- Extract `child_id` from item's `Qt.UserRole`
- Query child from DB
- Populate detail labels (using translated labels like `birth_date_label`)
- Switch to child details view
- Store `child_id` in `self.current_child_id` for edit/delete ops

```python
def on_child_clicked(self, item):
    child_id = item.data(Qt.UserRole)
    self.current_child_id = child_id
    child = session.query(Child).filter_by(id=child_id).first()
    if child:
        t = TRANSLATIONS[self.language]
        self.lbl_child_full_name.setText(f"<b>{child.first_name} {child.last_name}</b>")
        self.lbl_child_birth.setText(f"<b>{t['birth_date_label']}</b> {child.birth_date}")
        self.lbl_child_gender.setText(f"<b>{t['gender_label']}</b> {child.gender or 'N/A'}")
        notes_text = child.notes if child.notes else t['no_notes']
        self.lbl_child_notes.setText(notes_text)
        self.stacked.setCurrentWidget(self.child_info_widget)
```

**`edit_child_notes()`**
- Get current child
- Open `QInputDialog.getMultiLineText()` with current notes
- If OK clicked, save updated notes and commit
- Refresh display

```python
def edit_child_notes(self):
    if not self.current_child_id:
        return
    child = session.query(Child).filter_by(id=self.current_child_id).first()
    if not child:
        return
    
    new_notes, ok = QInputDialog.getMultiLineText(
        self, "Edit Notes", "Notes:", child.notes or ""
    )
    if ok:
        child.notes = new_notes.strip() or None
        session.commit()
        
        t = TRANSLATIONS[self.language]
        updated_child = session.query(Child).filter_by(id=self.current_child_id).first()
        notes_text = updated_child.notes if updated_child.notes else t['no_notes']
        self.lbl_child_notes.setText(notes_text)
```

**`delete_child_with_confirmation()`**
- Show `QMessageBox.question()` with translated confirm message
- If "Yes", call `delete_child()`

```python
def delete_child_with_confirmation(self):
    if not self.current_child_id:
        return
    t = TRANSLATIONS[self.language]
    reply = QMessageBox.question(
        self, "Confirm", t["confirm_delete"],
        QMessageBox.Yes | QMessageBox.No
    )
    if reply == QMessageBox.Yes:
        self.delete_child()
```

**`delete_child()`**
- Get child from DB
- Cascade-delete examinations & answers
- Delete child
- Commit
- Clear `self.current_child_id`
- Return to children list

```python
def delete_child(self):
    if not self.current_child_id:
        return
    child = session.query(Child).filter_by(id=self.current_child_id).first()
    if not child:
        return
    
    for exam in child.examinations:
        for answer in exam.answers:
            session.delete(answer)
        session.delete(exam)
    session.delete(child)
    session.commit()
    
    t = TRANSLATIONS[self.language]
    print(t['delete_success'])
    self.current_child_id = None
    self.show_children_view()
```

---

### `UI/style.py`

Global stylesheet and application of styling.

#### QSS Stylesheet

```python
APP_STYLE = r'''
* {
    font-family: "Segoe UI", "Inter", system-ui, sans-serif;
    color: #1f2d46;
}

QMainWindow {
    background-color: #f6f8fb;  /* Light blue background */
}

QPushButton {
    background-color: #2fb9c9;  /* Teal buttons */
    border-radius: 10px;
    padding: 10px 14px;
}

QPushButton:hover {
    background-color: #28a5b5;
}

QPushButton:pressed {
    background-color: #1f8b98;
}

QListWidget {
    background: #ffffff;
    border: 1px solid #d7deea;
    border-radius: 12px;
}

QListWidget::item:selected {
    background: #e3f7fa;
}

/* ... more QSS rules ... */
'''
```

**Medical Theme Colors**:
- Background: `#f6f8fb` (very light blue)
- Primary: `#2fb9c9` (teal)
- Text: `#1f2d46` (dark blue-gray)
- List hover: `#e3f7fa` (light cyan)

#### `apply_app_style(app)`

```python
def apply_app_style(app):
    """Apply global stylesheet to QApplication."""
    app.setStyleSheet(APP_STYLE)
```

Called in `main.py` and `run.py` before showing window:

```python
app = QApplication(sys.argv)
apply_app_style(app)
window = MainWindow()
window.show()
```

---

## UI Components & Navigation

### View Hierarchy

```
MainWindow (QMainWindow)
└── QStackedWidget (self.stacked)
    ├── menu_widget (QWidget) — Main menu (3 buttons)
    ├── children_widget (QWidget) — Children list + Add/Back
    ├── add_child_widget (QWidget) — Form to add new child
    ├── settings_widget (QWidget) — Language settings
    └── child_info_widget (QWidget) — Child details + Edit/Delete
```

### Navigation Flow Diagram

```
┌─────────────────────────┐
│     MENU SCREEN         │
│ ┌─────────────────────┐ │
│ │ List Children   [→] │ │
│ ├─────────────────────┤ │
│ │ Start Work      [→] │ │
│ ├─────────────────────┤ │
│ │ Settings        [→] │ │
│ └─────────────────────┘ │
└────────────┬────────────┘
             │
    ┌────────┼────────┐
    ↓        ↓        ↓
┌────────┐ (Future) ┌──────────┐
│Children│           │Settings  │
│ LIST   │           │  SCREEN  │
│  [+]   │           │[Toggle]  │
│  [←]   │           │  [←]     │
└───┬────┘           └──────────┘
    │
    ↓
  [Click]
    ↓
┌─────────────────────┐
│  ADD CHILD FORM     │
│ [Form Fields]       │
│ [Save]  [Cancel]    │
│         (→Children) │
└─────────────────────┘
    OR
    ↓
┌──────────────────────┐
│ CHILD DETAILS SCREEN │
│ Name, Birth, Gender  │
│ Notes                │
│ [Edit Notes]         │
│ [Delete]             │
│ [← Back to List]     │
└──────────────────────┘
```

---

## Internationalization (i18n)

### System Language Detection

On startup, `detect_default_language()` checks system locale:

```
locale.getlocale()[0]
↓
"pl_PL" → Extract "pl" → Check if in TRANSLATIONS → Use Polish
"en_US" → Extract "en" → Check if in TRANSLATIONS → Use English
"de_DE" → Extract "de" → Not in TRANSLATIONS → Fallback to English
```

### Language Toggle

User clicks "Language" button → `toggle_language()` called:

```
self.language = "pl" ↔ "en"
apply_translations()  # Re-update all labels
```

### Adding New Strings

1. Add key-value to both `TRANSLATIONS["pl"]` and `TRANSLATIONS["en"]`
2. In UI code, use: `t = TRANSLATIONS[self.language]; self.label.setText(t["key"])`
3. Call `apply_translations()` if changing language to refresh

**Example**:
```python
TRANSLATIONS = {
    "pl": {"new_key": "Polski tekst"},
    "en": {"new_key": "English text"}
}

# Later:
t = TRANSLATIONS[self.language]
self.label.setText(t["new_key"])
```

---

## Styling

### QSS (Qt Style Sheets)

QSS is similar to CSS but for Qt widgets. Applied globally via `app.setStyleSheet()`.

#### Basic Structure

```qss
Selector {
    property: value;
}

/* Pseudo-states */
Selector:hover {
    property: value;
}

Selector:pressed {
    property: value;
}
```

#### Common Properties

- `background-color: #RRGGBB;` — Background color
- `color: #RRGGBB;` — Text color
- `border: width style color;` — Border style
- `border-radius: px;` — Rounded corners
- `padding: top right bottom left;` — Internal spacing
- `margin: top right bottom left;` — External spacing
- `font-family: name;` — Font typeface
- `font-size: px;` — Font size
- `font-weight: bold;` — Font weight

#### Custom Classes

Apply custom stylesheets to specific widget classes:

```qss
QPushButton {
    background-color: #2fb9c9;
    padding: 10px;
}

QListWidget::item:selected {
    background-color: #e3f7fa;
}
```

---

## Running the Application

### Prerequisites

- Python 3.11+ installed
- `pip` available
- Virtual environment recommended

### Installation Steps

```bash
# 1. Clone repository
git clone <repo-url>
cd logoapp

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install PySide6 SQLAlchemy

# 5. Run application
python run.py
```

### Launching Methods

**Recommended**:
```bash
python run.py
```

**Alternative**:
```bash
python main.py
```

**DO NOT** run `UI/UI.py` directly (disabled by design to prevent multiple windows).

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `No module named 'PySide6'` | Dependency not installed | `pip install PySide6` |
| `No module named 'database'` | Import path issue | Run from project root: `cd logoapp && python run.py` |
| Multiple windows open | Running multiple processes | Close all instances, run one `python run.py` |
| No styling applied | Launcher doesn't call `apply_app_style()` | Use `run.py` or `main.py`, not `UI/UI.py` |
| `OperationalError: no such table` | Database corrupted/missing | Delete `logopedia.db`, restart app (recreates schema) |

---

## Development Guidelines

### Code Style

- Follow **PEP 8** (Python Enhancement Proposal 8)
- Use **snake_case** for variables and functions
- Use **PascalCase** for classes
- Max line length: 100 characters (Qt/PySide idioms may exceed)

### Adding New Features

#### Example: Add "Notes" Button to Menu

1. **UI**: In `MainWindow.__init__()`, create button and wire signal
2. **Slot**: Define `show_notes_view()` method
3. **Data**: Ensure data model supports feature
4. **Translations**: Add strings to `TRANSLATIONS` dict
5. **Test**: Run, verify button works and language toggle works

**Code Example**:
```python
# In __init__:
self.btn_notes = QPushButton("View Notes")
self.btn_notes.clicked.connect(self.show_notes_view)
buttons_row.addWidget(self.btn_notes)

# Define slot:
def show_notes_view(self):
    self.populate_notes_view()
    self.stacked.setCurrentWidget(self.notes_widget)

# In apply_translations():
self.btn_notes.setText(t["view_notes"])

# In TRANSLATIONS:
"pl": {"view_notes": "Wyświetl notatki"},
"en": {"view_notes": "View Notes"}
```

### Database Modifications

If modifying schema:

1. **Update Model**: Edit `Child`, `Examination`, or `Answer` class in `database.py`
2. **Migration**: SQLite doesn't support ALTER TABLE well; either:
   - Delete `logopedia.db` (loses data—OK for dev)
   - Use `alembic` for schema versioning (future enhancement)
3. **Test**: Verify new column/table appears in DB

### Testing

(Currently no automated test suite—recommended future addition)

Manual testing checklist:
- [ ] Add child with all fields
- [ ] Add child with minimal fields
- [ ] Edit notes on existing child
- [ ] Delete child with confirmation
- [ ] Toggle language—all text updates
- [ ] List refreshes after add/delete
- [ ] Close/reopen app—data persists

### Git Workflow

- **Branches**: `main` (stable), `develop` (WIP)
- **Commits**: Small, logical, clear messages
- **.gitignore**: Respects `.db`, `.venv/`, `DOCS_PL.md`
- **Push**: Never push `logopedia.db` or local docs

---

## Future Enhancements

### Short-term

- [ ] Examination form & data entry
- [ ] Answer storage & retrieval UI
- [ ] Report generation (PDF)
- [ ] Patient search/filter

### Medium-term

- [ ] User authentication
- [ ] Backup/restore functionality
- [ ] Data export (CSV, JSON)
- [ ] Statistics/analytics dashboard

### Long-term

- [ ] Mobile app / responsive web version
- [ ] Cloud sync (with privacy safeguards)
- [ ] Integration with speech therapy standards
- [ ] Multi-user collaboration (with roles)

---

## License & Attribution

[Add your license text here]

---

## Questions?

For detailed Polish documentation, see [DOCS_PL.md](./DOCS_PL.md).

For quick overview, see [README.md](./README.md).

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Author**: Łukasz
