import sys
from gui.qt_compat import QtWidgets, backend
from database.db_setup import initialize_database
from gui.login_window import LoginWindow
from gui.task_window import TaskWindow
from gui.style import get_stylesheet


def main():
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
        windows['login'] = login

    def on_login(user):
        # Close any login dialog
        dlg = windows.pop('login', None)
        if dlg:
            try:
                dlg.close()
            except Exception:
                pass

        win = TaskWindow(user)
        win.logout_requested.connect(on_logout)
        win.show()
        windows['task'] = win

    def on_logout():
        # Close current task window and show login again
        win = windows.pop('task', None)
        if win:
            try:
                win.close()
            except Exception:
                pass
        show_login()

    show_login()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
