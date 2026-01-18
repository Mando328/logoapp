
APP_STYLE = r'''
* {
    font-family: "Segoe UI", "Inter", system-ui, sans-serif;
    font-size: 14px;
    color: #1f2d46;
}

QMainWindow {
    background-color: #f6f8fb;
}

QWidget {
    background-color: #f6f8fb;
}

QPushButton {
    background-color: #2fb9c9;
    color: #1f2d46;
    border: 1px solid #27a5b5;
    border-radius: 10px;
    padding: 10px 14px;
    font-weight: 600;
    letter-spacing: 0.2px;
}

QPushButton:hover {
    background-color: #28a5b5;
}

QPushButton:pressed {
    background-color: #1f8b98;
}

QPushButton:disabled {
    background-color: #dbe5ec;
    border-color: #dbe5ec;
    color: #7a8699;
}

QListWidget {
    background: #ffffff;
    border: 1px solid #d7deea;
    border-radius: 12px;
    padding: 8px;
}

QListWidget::item {
    padding: 10px 12px;
    margin: 2px 0px;
    border-radius: 8px;
}

QListWidget::item:selected {
    background: #e3f7fa;
    color: #0f172a;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 4px 0 4px 0;
}

QScrollBar::handle:vertical {
    background: #c5d6e4;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #9db8cd;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
'''

def apply_app_style(app):
    """Apply the global stylesheet to the given QApplication."""
    app.setStyleSheet(APP_STYLE)
