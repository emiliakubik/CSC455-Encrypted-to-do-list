import sys
import os
import platform
from PyQt5 import QtCore
from gui.qt_compat import QtWidgets, backend
from database.db_setup import initialize_database
from gui.login_window import LoginWindow
from gui.task_window import TaskWindow
from gui.style import get_stylesheet


def main():
    # --- High DPI scaling (helps on macOS + HiDPI displays) ---
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

    initialize_database()
    app = QtWidgets.QApplication(sys.argv)

    # Informational: which Qt backend is in use
    print(f"Using Qt backend: {backend}")

    # Apply the pastel kawaii stylesheet
    app.setStyleSheet(get_stylesheet())

    windows = {}

    def show_login():
        login = LoginWindow()
        login.login_success.connect(on_login)
        login.show()
        windows["login"] = login

    def on_login(user):
        # Close any login dialog
        dlg = windows.pop("login", None)
        if dlg:
            try:
                dlg.close()
            except Exception:
                pass

        win = TaskWindow(user)
        win.logout_requested.connect(on_logout)

        # --- Window mode depending on OS ---
        if platform.system() == "Darwin":
            # macOS: real fullscreen space
            win.showFullScreen()
        else:
            # Windows / Linux: maximized window
            win.showMaximized()

        windows["task"] = win

    def on_logout():
        # Close current task window and show login again
        win = windows.pop("task", None)
        if win:
            try:
                win.close()
            except Exception:
                pass
        show_login()

    show_login()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
