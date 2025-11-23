from gui.qt_compat import QtWidgets
from database.models import User
from core import task_manager


class ShareDialog(QtWidgets.QDialog):
    def __init__(self, task_id, owner_id, parent=None):
        super().__init__(parent)
        self.task_id = task_id
        self.owner_id = owner_id
        self.setWindowTitle("Share Task")
        self.resize(320, 110)

        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setObjectName("shareUsername")
        self.username_input.setPlaceholderText("Username to share with")

        import qtawesome as qta
        share_btn = QtWidgets.QPushButton("Share")
        share_btn.setObjectName("shareBtn")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.username_input)
        layout.addWidget(share_btn)
        self.setLayout(layout)

        try:
            purple = '#7D55D9'
            share_btn.setIcon(qta.icon('fa5s.share-alt', color=purple))
        except Exception:
            pass
        share_btn.clicked.connect(self._on_share)

    def _on_share(self):
        username = self.username_input.text().strip().lower()
        user = User.get_by_username(username)
        if not user:
            QtWidgets.QMessageBox.warning(self, "Error", "User not found")
            return
        ok, msg = task_manager.share_task_with_user(self.task_id, self.owner_id, user['user_id'])
        QtWidgets.QMessageBox.information(self, "Share", msg)
        if ok:
            self.accept()
