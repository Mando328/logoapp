# LogoApp

A speech therapy app for managing patient records. Early WIP (v0.0.2).

## What is it?

Desktop app to:
- Add/edit/delete kids in a database
- Store notes and examination data
- Polish & English support (auto-detected)
- Everything stored locally in SQLite

## What's done

- Patient CRUD (add, view, edit notes, delete)
- Basic UI with navigation
- Language toggle
- Medical-ish theme

## What's next

- Examination forms
- Reports/export (PDF?)
- Better UI polish
- Idk, we'll see

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install PySide6 SQLAlchemy
python run.py
```

## Project layout

```
├── run.py                 # start here
├── main.py                # alt launcher
├── database.py            # db models
└── UI/
    ├── UI.py             # main window
    └── style.py          # styling
```

## Notes

- Database is local, not in Git
- Uses PySide6 + SQLite + SQLAlchemy

---

Early version. Made for learning. Might break things 🤷

