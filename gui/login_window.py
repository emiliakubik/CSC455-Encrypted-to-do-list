from gui.qt_compat import QtWidgets, QtCore
from core import user_auth
import qtawesome as qta


class LoginWindow(QtWidgets.QDialog):
    login_success = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        # give unique name so stylesheet can target it
        self.setObjectName("loginDialog")

        # remove Windows "?" button
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("PlanIt — Login")
        self.resize(380, 260)

        # ----------- MAIN LAYOUT -----------
        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 20)
        main.setSpacing(16)

        # 🌸 cute title
        title = QtWidgets.QLabel("Welcome Back 💜")
        title.setObjectName("loginTitle")
        title.setAlignment(QtCore.Qt.AlignCenter)

        subtitle = QtWidgets.QLabel("Log in to PlanIt")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(QtCore.Qt.AlignCenter)

        # ----------- INPUTS -----------
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setObjectName("usernameInput")

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setObjectName("passwordInput")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        # ----------- BUTTONS -----------
        btn_row = QtWidgets.QHBoxLayout()

        login_btn = QtWidgets.QPushButton(" Login")
        login_btn.setObjectName("loginPrimaryBtn")

        register_btn = QtWidgets.QPushButton(" Register")
        register_btn.setObjectName("loginSecondaryBtn")

        # cute icons
        try:
            purple = "#7D55D9"
            login_btn.setIcon(qta.icon("fa5s.check", color=purple))
            register_btn.setIcon(qta.icon("fa5s.user-plus", color=purple))
        except Exception:
            pass

        btn_row.addWidget(login_btn)
        btn_row.addWidget(register_btn)

        # ----------- ADD TO LAYOUT -----------
        main.addWidget(title)
        main.addWidget(subtitle)
        main.addSpacing(6)
        main.addWidget(self.username_input)
        main.addWidget(self.password_input)
        main.addSpacing(6)
        main.addLayout(btn_row)

        # ----------- SIGNALS -----------
        login_btn.clicked.connect(self._on_login)
        register_btn.clicked.connect(self._on_register)

    # ================================
    # LOGIC (unchanged)
    # ================================
    def _on_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        ok, msg, user_id = user_auth.register_user(username, password)
        QtWidgets.QMessageBox.information(self, "Register", msg)
        if ok:
            success, _, user_data = user_auth.login_user(username, password)
            if success:
                self.login_success.emit(user_data)
                self.accept()

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        ok, msg, user_data = user_auth.login_user(username, password)
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Login failed", msg)
            return
        self.login_success.emit(user_data)
        self.accept()
