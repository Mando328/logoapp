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
