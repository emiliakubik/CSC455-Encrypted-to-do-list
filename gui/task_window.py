from gui.qt_compat import QtWidgets, QtCore, QtGui
from core import task_manager
from database.models import User
from gui.share_window import ShareDialog
import qtawesome as qta

QPropertyAnimation = QtCore.QPropertyAnimation
QParallelAnimationGroup = QtCore.QParallelAnimationGroup


class TaskWindow(QtWidgets.QMainWindow):
    logout_requested = QtCore.pyqtSignal()

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user = user_data
        self.setWindowTitle(f"Encrypted To-Do — {self.user['username']}")
        self.resize(800, 480)

        self._tasks = []
        # keep animations alive so they don’t get GC’d
        self._active_anims: list[QtCore.QAbstractAnimation] = []

        # ---------- MAIN LAYOUT ----------
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main_layout = QtWidgets.QHBoxLayout()
        central.setLayout(main_layout)

        # LEFT: task list
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setObjectName("todoList")
        main_layout.addWidget(self.list_widget, 1)

        # RIGHT: details + footer buttons (vertical)
        right_layout = QtWidgets.QVBoxLayout()

        # details area – full height, just text
        self.details = QtWidgets.QTextEdit()
        self.details.setReadOnly(True)
        self.details.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        right_layout.addWidget(self.details, 1)

        # footer buttons
        btn_row = QtWidgets.QHBoxLayout()
        new_btn = QtWidgets.QPushButton("New")
        edit_btn = QtWidgets.QPushButton("Edit")
        share_btn = QtWidgets.QPushButton("Share")
        refresh_btn = QtWidgets.QPushButton("Refresh")
        logout_btn = QtWidgets.QPushButton("Logout")

        # icons (safe if qtawesome installed)
        try:
            purple = "#7D55D9"
            new_btn.setIcon(qta.icon("fa5s.plus", color=purple))
            edit_btn.setIcon(qta.icon("fa5s.edit", color=purple))
            share_btn.setIcon(qta.icon("fa5s.share-alt", color=purple))
            refresh_btn.setIcon(qta.icon("fa5s.sync", color=purple))
            logout_btn.setIcon(qta.icon("fa5s.sign-out-alt", color=purple))
        except Exception:
            pass

        btn_row.addWidget(new_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(share_btn)
        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(logout_btn)
        right_layout.addLayout(btn_row)

        # add right column to main layout
        main_layout.addLayout(right_layout, 2)

        # button squish animation (visible bounce + opacity blink)
        for b in (new_btn, edit_btn, share_btn, refresh_btn, logout_btn):
            eff = QtWidgets.QGraphicsOpacityEffect(b)
            b.setGraphicsEffect(eff)
            # capture both button and effect in the lambda
            b.pressed.connect(
                lambda _b=b, _e=eff: self._animate_button_press(_b, _e)
            )

        # ---------- SIGNALS ----------
        self.list_widget.itemSelectionChanged.connect(self._on_select)
        self.list_widget.itemChanged.connect(self._on_item_changed)
        new_btn.clicked.connect(self._on_new)
        edit_btn.clicked.connect(self._on_edit)
        refresh_btn.clicked.connect(self.refresh)
        share_btn.clicked.connect(self._on_share)
        logout_btn.clicked.connect(self._on_logout)

        self.refresh()

    # ================= ANIMATION HELPERS =================

    def _register_anim(self, anim: QtCore.QAbstractAnimation):
        """Keep animation alive until finished (avoid GC killing it early)."""
        self._active_anims.append(anim)

        def _cleanup():
            try:
                self._active_anims.remove(anim)
            except ValueError:
                pass

        anim.finished.connect(_cleanup)

    def _animate_button_press(
        self,
        btn: QtWidgets.QPushButton,
        effect: QtWidgets.QGraphicsOpacityEffect,
    ):
        """Squish + opacity blink animation on button press."""
        try:
            # Opacity animation
            fade = QPropertyAnimation(effect, b"opacity")
            fade.setDuration(180)
            fade.setKeyValueAt(0.0, 1.0)
            fade.setKeyValueAt(0.45, 0.6)
            fade.setKeyValueAt(1.0, 1.0)

            # Geometry squish
            geo = btn.geometry()
            shrink = geo.adjusted(4, 4, -4, -4)

            squish = QPropertyAnimation(btn, b"geometry")
            squish.setDuration(180)
            squish.setStartValue(geo)
            squish.setKeyValueAt(0.5, shrink)
            squish.setEndValue(geo)
            squish.setEasingCurve(QtCore.QEasingCurve.OutCubic)

            group = QParallelAnimationGroup()
            group.addAnimation(fade)
            group.addAnimation(squish)

            self._register_anim(group)
            group.start()
        except Exception:
            pass

    def _play_complete_effect(self, item: QtWidgets.QListWidgetItem):
        """Sparkle + soft bounce next to the checkbox when a task is completed."""
        try:
            rect = self.list_widget.visualItemRect(item)
            if not rect.isValid():
                return

            # Sparkle emoji
            sparkle = QtWidgets.QLabel("✨", self.list_widget)
            sparkle.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            sparkle.setAlignment(QtCore.Qt.AlignCenter)

            font = sparkle.font()
            font.setPointSize(18)  # nice and big
            sparkle.setFont(font)

            size = 30
            x = rect.left() + 6
            y = rect.center().y() - size // 2
            base_rect = QtCore.QRect(x, y, size, size)
            sparkle.setGeometry(base_rect)

            eff = QtWidgets.QGraphicsOpacityEffect(sparkle)
            sparkle.setGraphicsEffect(eff)
            eff.setOpacity(1.0)
            sparkle.show()

            # Bounce (grow then shrink)
            grow_rect = base_rect.adjusted(-6, -6, 6, 6)
            bounce_anim = QPropertyAnimation(sparkle, b"geometry")
            bounce_anim.setDuration(260)
            bounce_anim.setStartValue(base_rect)
            bounce_anim.setKeyValueAt(0.4, grow_rect)
            bounce_anim.setEndValue(base_rect)
            bounce_anim.setEasingCurve(QtCore.QEasingCurve.OutBack)

            # Float up + fade out
            float_anim = QPropertyAnimation(sparkle, b"pos")
            float_anim.setDuration(750)
            float_anim.setStartValue(base_rect.topLeft())
            float_anim.setEndValue(base_rect.topLeft() + QtCore.QPoint(0, -28))

            fade_anim = QPropertyAnimation(eff, b"opacity")
            fade_anim.setDuration(750)
            fade_anim.setStartValue(1.0)
            fade_anim.setEndValue(0.0)

            group = QParallelAnimationGroup(self)
            group.addAnimation(bounce_anim)
            group.addAnimation(float_anim)
            group.addAnimation(fade_anim)

            def _delete_sparkle():
                sparkle.deleteLater()

            group.finished.connect(_delete_sparkle)
            self._register_anim(group)
            group.start()
        except Exception:
            # If anything fails, just skip the effect (no crash)
            pass

    # ================= CORE BEHAVIOR =================

    def refresh(self):
        """Reload tasks and rebuild the list with native checkable items."""
        self.list_widget.blockSignals(True)
        self.list_widget.clear()

        tasks = task_manager.get_tasks_for_user(self.user["user_id"])
        self._tasks = tasks

        for t in tasks:
            item = QtWidgets.QListWidgetItem(t["title"])
            item.setData(QtCore.Qt.UserRole, t["task_id"])

            flags = (
                item.flags()
                | QtCore.Qt.ItemIsUserCheckable
                | QtCore.Qt.ItemIsSelectable
                | QtCore.Qt.ItemIsEnabled
            )
            item.setFlags(flags)
            item.setCheckState(
                QtCore.Qt.Checked if t["is_complete"] else QtCore.Qt.Unchecked
            )
            self.list_widget.addItem(item)

        self.list_widget.blockSignals(False)

        if tasks:
            self.list_widget.setCurrentRow(0)
            self._on_select()
        else:
            self.details.clear()

    def _on_select(self):
        sel = self.list_widget.currentRow()
        if sel < 0 or sel >= len(self._tasks):
            self.details.clear()
            return

        t = self._tasks[sel]

        # Resolve numeric user ids to usernames for nicer display
        try:
            creator = User.get_by_id(t["created_by"])
            creator_label = creator["username"] if creator else str(t["created_by"])
        except Exception:
            creator_label = str(t["created_by"])

        try:
            updater = User.get_by_id(t["updated_by"])
            updater_label = updater["username"] if updater else str(t["updated_by"])
        except Exception:
            updater_label = str(t["updated_by"])

        meta = (
            f"Created by: {creator_label} | "
            f"Updated by: {updater_label} | "
            f"Complete: {t['is_complete']}"
        )

        self.details.setPlainText(meta + "\n\n" + t["details"])

    def _on_item_changed(self, item: QtWidgets.QListWidgetItem):
        """Called when the user ticks/unticks the checkbox in the list."""
        try:
            task_id = int(item.data(QtCore.Qt.UserRole))
        except Exception:
            return

        checked = item.checkState() == QtCore.Qt.Checked
        # use encrypted-safe update helper
        task_manager.update_task(
            task_id,
            self.user["user_id"],
            is_complete=checked,
        )

        for t in self._tasks:
            if t["task_id"] == task_id:
                t["is_complete"] = checked
                break

        if self.list_widget.currentItem() is item:
            self._on_select()

        if checked:
            self._play_complete_effect(item)

    def _on_new(self):
        dialog = NewTaskDialog(self.user["user_id"], self)
        if dialog.exec_():
            self.refresh()

    def _on_share(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Share", "Select a task first")
            return

        t = self._tasks[row]
        task_id = t["task_id"]
        dlg = ShareDialog(task_id, self.user["user_id"], self)
        dlg.exec_()

    def _on_edit(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self._tasks):
            QtWidgets.QMessageBox.warning(self, "Edit Task", "Select a task first")
            return

        task = self._tasks[row]
        dlg = EditTaskDialog(task, self.user["user_id"], self)
        if dlg.exec_():
            # reload tasks so list + details show updated text
            self.refresh()
            # restore selection to the same row if still valid
            if row < self.list_widget.count():
                self.list_widget.setCurrentRow(row)
                self._on_select()

    def _on_logout(self):
        self.logout_requested.emit()
        self.close()


class NewTaskDialog(QtWidgets.QDialog):
    """Dialog to create a brand-new task."""

    def __init__(self, owner_id, parent=None):
        super().__init__(parent)
        self.owner_id = owner_id

        self.setWindowTitle("New Task")
        self.resize(480, 360)

        # --- inputs ---
        self.title_input = QtWidgets.QLineEdit()
        self.title_input.setPlaceholderText("Title")

        self.details_input = QtWidgets.QTextEdit()

        self.collab_input = QtWidgets.QLineEdit()
        self.collab_input.setPlaceholderText(
            "Collaborators (comma-separated usernames)"
        )

        create_btn = QtWidgets.QPushButton("Create")

        # --- layout ---
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.title_input)
        layout.addWidget(self.details_input)
        layout.addWidget(self.collab_input)
        layout.addWidget(create_btn)
        self.setLayout(layout)

        create_btn.clicked.connect(self._on_create)

    def _on_create(self):
        title = self.title_input.text().strip()
        details = self.details_input.toPlainText()

        if not title:
            QtWidgets.QMessageBox.warning(self, "Create Task", "Title cannot be empty.")
            return

        # parse collaborators list
        collab_usernames = [
            u.strip().lower()
            for u in self.collab_input.text().split(",")
            if u.strip()
        ]

        shared_ids = []
        for uname in collab_usernames:
            user = User.get_by_username(uname)
            if user:
                if user["user_id"] != self.owner_id:
                    shared_ids.append(user["user_id"])
            else:
                QtWidgets.QMessageBox.warning(
                    self, "Create Task", f"User '{uname}' not found; skipping"
                )

        ok, msg, task_id = task_manager.create_encrypted_task(
            title, details, self.owner_id, shared_with=shared_ids
        )

        QtWidgets.QMessageBox.information(self, "Create Task", msg)
        if ok:
            self.accept()


class EditTaskDialog(QtWidgets.QDialog):
    """Dialog to edit an existing task's title & details."""

    def __init__(self, task_data, editor_id, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.editor_id = editor_id

        self.setWindowTitle("Edit Task")
        self.resize(480, 360)

        self.title_input = QtWidgets.QLineEdit()
        self.title_input.setPlaceholderText("Title")
        self.title_input.setText(task_data.get("title", ""))

        self.details_input = QtWidgets.QTextEdit()
        self.details_input.setPlainText(task_data.get("details", ""))

        save_btn = QtWidgets.QPushButton("Save changes")

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.title_input)
        layout.addWidget(self.details_input)
        layout.addWidget(save_btn)
        self.setLayout(layout)

        save_btn.clicked.connect(self._on_save)

    def _on_save(self):
        new_title = self.title_input.text().strip()
        new_details = self.details_input.toPlainText()

        if not new_title:
            QtWidgets.QMessageBox.warning(self, "Edit Task", "Title cannot be empty.")
            return

        task_id = self.task_data["task_id"]

        ok, msg = task_manager.update_task(
            task_id,
            self.editor_id,
            new_title=new_title,
            new_details=new_details,
        )

        if msg:
            QtWidgets.QMessageBox.information(self, "Edit Task", msg)

        if ok:
            self.accept()
