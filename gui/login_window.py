from pathlib import Path

from gui.qt_compat import QtWidgets, QtCore, QtGui, QtMultimedia
from core import user_auth
import qtawesome as qta


class LoginWindow(QtWidgets.QDialog):
    login_success = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._welcome_sound = self._load_sound("welcome.mp3")
        self._goodbye_sound = self._load_sound("goodbye.mp3")

        # Object name so the stylesheet can target this dialog
        self.setObjectName("loginDialog")

        # Remove the Windows "?" help button
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.setWindowTitle("PlanIt — Login")
        self.resize(420, 320)

        # ----------- MAIN LAYOUT -----------
        main = QtWidgets.QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 20)
        main.setSpacing(14)

        # ----------- LOGO ROW -----------
        logo_row = QtWidgets.QHBoxLayout()
        logo_row.addStretch()

        self.logo_label = QtWidgets.QLabel()
        self.logo_label.setObjectName("loginLogo")

        # Load logo (make sure this path is correct relative to where you run main.py)
        pix = QtGui.QPixmap("icons/planit_logo.png")
        if not pix.isNull():
            pix = pix.scaled(
                130, 130,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self.logo_label.setPixmap(pix)

        logo_row.addWidget(self.logo_label)
        logo_row.addStretch()
        main.addLayout(logo_row)

        # ----------- TITLE + SUBTITLE -----------
        # Single main title: "Log in to PlanIt"
        title = QtWidgets.QLabel("Log in to PlanIt")
        title.setObjectName("loginTitle")
        title.setAlignment(QtCore.Qt.AlignCenter)

        main.addWidget(title)

        # ----------- INPUTS -----------
        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setObjectName("usernameInput")

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setObjectName("passwordInput")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)

        main.addSpacing(8)
        main.addWidget(self.username_input)
        main.addWidget(self.password_input)

        # ----------- BUTTONS -----------
        btn_row = QtWidgets.QHBoxLayout()

        login_btn = QtWidgets.QPushButton(" Login")
        login_btn.setObjectName("loginPrimaryBtn")

        register_btn = QtWidgets.QPushButton(" Register")
        register_btn.setObjectName("loginSecondaryBtn")

        # Cute icons
        try:
            purple = "#7D55D9"
            login_btn.setIcon(qta.icon("fa5s.check", color=purple))
            register_btn.setIcon(qta.icon("fa5s.user-plus", color=purple))
        except Exception:
            pass

        btn_row.addWidget(login_btn)
        btn_row.addWidget(register_btn)
        main.addSpacing(6)
        main.addLayout(btn_row)

        # ----------- SIGNALS -----------
        login_btn.clicked.connect(self._on_login)
        register_btn.clicked.connect(self._on_register)
    # ================================
    # LOGIC
    # ================================
    #this is the welcome sound effect
    def _load_sound(self, filename):
        """Prepare a reusable sound effect using Qt's multimedia stack."""
        sound_path = Path(__file__).resolve().parent.parent / "sounds" / filename
        if not sound_path.exists():
            return None
        url = QtCore.QUrl.fromLocalFile(str(sound_path))
        player = QtMultimedia.QMediaPlayer(self)
        if hasattr(QtMultimedia, "QAudioOutput"):
            audio = QtMultimedia.QAudioOutput(self)
            audio.setVolume(1.0)
            player.setAudioOutput(audio)
            player._audio_output = audio 
            player.setSource(url)
        else:
            player.setMedia(QtMultimedia.QMediaContent(url))
            player.setVolume(100)
        return player

    def _play_welcome_sound(self):
        if self._welcome_sound is not None:
            self._welcome_sound.stop()
            self._welcome_sound.play()
            return True
        return False

    def _play_goodbye_sound(self):
        if self._goodbye_sound is not None:
            self._goodbye_sound.stop()
            self._goodbye_sound.play()
            return True
        return False

    def _complete_login(self, user_data):
        """Finalize a successful login and close after optional SFX."""
        self.login_success.emit(user_data)
        if self._play_welcome_sound():
            QtCore.QTimer.singleShot(800, self.accept)
        else:
            self.accept()

    def accept(self):
        if self._play_goodbye_sound():
            QtCore.QTimer.singleShot(600, super().accept)
        else:
            super().accept()

    def _on_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        ok, msg, user_id = user_auth.register_user(username, password)
        QtWidgets.QMessageBox.information(self, "Register", msg)
        if ok:
            # Optionally auto-login after register
            success, _, user_data = user_auth.login_user(username, password)
            if success:
                self._complete_login(user_data)

    def _on_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        ok, msg, user_data = user_auth.login_user(username, password)
        if not ok:
            QtWidgets.QMessageBox.warning(self, "Login failed", msg)
            return
        self._complete_login(user_data)

