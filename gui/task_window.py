from pathlib import Path

from gui.qt_compat import QtWidgets, QtCore, QtGui
from core import task_manager
from database.models import User
from gui.share_window import ShareDialog
import qtawesome as qta
from datetime import datetime
from gui.sound_player import sound_player

QPropertyAnimation = QtCore.QPropertyAnimation
QParallelAnimationGroup = QtCore.QParallelAnimationGroup


class TaskWindow(QtWidgets.QMainWindow):
    logout_requested = QtCore.pyqtSignal()

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user = user_data
        self.setWindowTitle(f"PlanIt — {self.user['username']}")
        self.resize(800, 480)
        self._closing_with_sound = False

        self._tasks = []
        # keep animations alive so they don’t get GC’d
        self._active_anims: list[QtCore.QAbstractAnimation] = []

        self.current_filter = "all"  # "all", "done", "pending", "shared"
        self._all_done_announced = False

        # ---------- MAIN LAYOUT ----------
        central = QtWidgets.QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        main_layout = QtWidgets.QHBoxLayout()
        # 🌸 extra breathing room around everything
        main_layout.setContentsMargins(40, 30, 40, 30)
        main_layout.setSpacing(32)
        central.setLayout(main_layout)

        # ========== LEFT COLUMN: FILTERS + TASK LIST ==========
        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 20, 0)
        left_layout.setSpacing(10)

        # tiny filter bar above the list
        filter_row = QtWidgets.QHBoxLayout()
        self.filter_all_btn = QtWidgets.QPushButton("🌟 All")
        self.filter_done_btn = QtWidgets.QPushButton("✔ Done")
        self.filter_pending_btn = QtWidgets.QPushButton("✏ Pending")
        self.filter_shared_btn = QtWidgets.QPushButton("🤝 Shared")

        for b in (
            self.filter_all_btn,
            self.filter_done_btn,
            self.filter_pending_btn,
            self.filter_shared_btn,
        ):
            b.setCheckable(True)
            filter_row.addWidget(b)
        filter_row.addStretch()

        # default filter
        self.filter_all_btn.setChecked(True)

        left_layout.addLayout(filter_row)

        # task list widget
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setObjectName("todoList")
        left_layout.addWidget(self.list_widget, 1)

        # add left column to main layout (narrower)
        main_layout.addLayout(left_layout, 1)

        # ========== RIGHT COLUMN: HEADER + DETAILS + BUTTONS ==========
        right_container = QtWidgets.QWidget()
        right_container.setObjectName("rightColumn")
        right_layout = QtWidgets.QVBoxLayout(right_container)
        # 🌸 padding inside the right column (welcome, chips, details, buttons)
        right_layout.setContentsMargins(18, 12, 18, 18)
        right_layout.setSpacing(24)   # more space between header / chips / progress

        main_layout.addWidget(right_container, 3)

        # ----------- LONG TOP HEADER BAR (logo + welcome + date) -----------
        header_container = QtWidgets.QWidget()
        header_container.setObjectName("topHeaderBar")

        header_row = QtWidgets.QHBoxLayout(header_container)
        header_row.setContentsMargins(18, 10, 18, 10)
        header_row.setSpacing(12)

        # cute mascot icon
        self.mascot_label = QtWidgets.QLabel()
        self.mascot_label.setObjectName("mascotLabel")

        pix = QtGui.QPixmap("icons/planit_logo.png")  # adjust path if needed
        if not pix.isNull():
            pix = pix.scaled(
                150, 150,                    # big logo like you had
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )
            self.mascot_label.setPixmap(pix)

        # welcome text
        self.welcome_label = QtWidgets.QLabel(
            f"Welcome back, {self.user['username'].capitalize()} 💜"
        )
        self.welcome_label.setObjectName("welcomeHeader")

        # today's date badge on the right side of the same bar
        self.date_label = QtWidgets.QLabel()
        self.date_label.setObjectName("dateBadge")
        self._update_date_label()      # fill in text like "📅 Today • Friday, Nov 22"

        header_row.addWidget(self.mascot_label)
        header_row.addWidget(self.welcome_label)
        header_row.addStretch()
        header_row.addWidget(self.date_label)

        # add full-width header bar to right column
        right_layout.addWidget(header_container)

        # ---------- TASK SUMMARY CHIPS (Total / Done / Pending) ----------
        chips_row = QtWidgets.QHBoxLayout()

        self.total_chip = QtWidgets.QLabel()
        self.completed_chip = QtWidgets.QLabel()
        self.pending_chip = QtWidgets.QLabel()

        # mark them as "chip" so stylesheet can style them nicely
        for chip in (self.total_chip, self.completed_chip, self.pending_chip):
            chip.setProperty("chip", True)
            chips_row.addWidget(chip)

        chips_row.addStretch()
        right_layout.addLayout(chips_row)

        # a little gap before the progress bar
        right_layout.addSpacing(10)

        # ---------- TODAY'S PROGRESS BAR + VIBE TEXT ----------
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setRange(0, 100)
        right_layout.addWidget(self.progress_bar)

        self.vibe_label = QtWidgets.QLabel()
        self.vibe_label.setObjectName("vibeLabel")
        right_layout.addWidget(self.vibe_label)

        # details area – full height, just text
        self.details = QtWidgets.QTextEdit()
        self.details.setReadOnly(True)
        self.details.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        right_layout.addWidget(self.details, 1)

        # footer buttons inside a glowing footer bar
        footer_bar = QtWidgets.QWidget()
        footer_bar.setObjectName("footerBar")

        btn_row = QtWidgets.QHBoxLayout(footer_bar)
        btn_row.setContentsMargins(12, 8, 12, 8)
        btn_row.setSpacing(12)

        new_btn = QtWidgets.QPushButton("New")
        edit_btn = QtWidgets.QPushButton("Edit")
        delete_btn = QtWidgets.QPushButton("Delete")
        share_btn = QtWidgets.QPushButton("Share")
        refresh_btn = QtWidgets.QPushButton("Refresh")
        logout_btn = QtWidgets.QPushButton("Logout")

        # icons (safe if qtawesome installed)
        try:
            purple = "#7D55D9"
            new_btn.setIcon(qta.icon("fa5s.plus", color=purple))
            edit_btn.setIcon(qta.icon("fa5s.edit", color=purple))
            delete_btn.setIcon(qta.icon("fa5s.trash", color=purple))
            share_btn.setIcon(qta.icon("fa5s.share-alt", color=purple))
            refresh_btn.setIcon(qta.icon("fa5s.sync", color=purple))
            logout_btn.setIcon(qta.icon("fa5s.sign-out-alt", color=purple))
        except Exception:
            pass

        btn_row.addWidget(new_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addWidget(share_btn)
        btn_row.addWidget(refresh_btn)
        btn_row.addWidget(logout_btn)

        right_layout.addWidget(footer_bar)

        # button squish animation (visible bounce + opacity blink)
        for b in (new_btn, edit_btn, delete_btn, share_btn, refresh_btn, logout_btn):
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
        delete_btn.clicked.connect(self._on_delete)
        refresh_btn.clicked.connect(self.refresh)
        share_btn.clicked.connect(self._on_share)
        logout_btn.clicked.connect(self._on_logout)

        # filter buttons
        self.filter_all_btn.clicked.connect(lambda: self._set_filter("all"))
        self.filter_done_btn.clicked.connect(lambda: self._set_filter("done"))
        self.filter_pending_btn.clicked.connect(lambda: self._set_filter("pending"))
        self.filter_shared_btn.clicked.connect(lambda: self._set_filter("shared"))

        self.refresh()
        # start the soft idle animation on the mascot
        self._start_mascot_idle_animation()

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

    def _set_filter(self, mode: str):
        """Change current filter and update buttons + list."""
        self.current_filter = mode

        # keep toggle state in sync
        if hasattr(self, "filter_all_btn"):
            self.filter_all_btn.setChecked(mode == "all")
            self.filter_done_btn.setChecked(mode == "done")
            self.filter_pending_btn.setChecked(mode == "pending")
            self.filter_shared_btn.setChecked(mode == "shared")

        # rebuild list with new filter
        self.refresh()

    def _update_date_label(self):
        """Set the cute 'Today • Friday, Nov 22' text."""
        today = QtCore.QDate.currentDate()
        pretty = today.toString("dddd, MMM d")   # e.g. Friday, Nov 22
        self.date_label.setText(f"📅 Today • {pretty}")

    def _start_mascot_idle_animation(self):
        if not hasattr(self, "mascot_label") or self.mascot_label is None:
            return

        effect = QtWidgets.QGraphicsOpacityEffect(self.mascot_label)
        self.mascot_label.setGraphicsEffect(effect)
        effect.setOpacity(0.8)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(1800)
        anim.setStartValue(0.75)
        anim.setKeyValueAt(0.5, 1.0)
        anim.setEndValue(0.75)
        anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        anim.setLoopCount(-1)  # infinite loop

        self._register_anim(anim)
        anim.start()

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

    def _maybe_play_all_done(self, total: int, completed: int):
        """Play the celebratory audio only when everything is done once per run."""
        if total <= 0:
            self._all_done_announced = False
            return

        if completed == total:
            if not self._all_done_announced:
                if not sound_player.play("completedall.mp3"):
                    if not sound_player.play("Completed.mp3"):
                        sound_player.play("done.mp3")
                self._all_done_announced = True
        else:
            self._all_done_announced = False

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

        # helper to decide if a task should be visible under current filter
        def _visible(t):
            if self.current_filter == "done":
                return t["is_complete"]
            if self.current_filter == "pending":
                return not t["is_complete"]
            if self.current_filter == "shared":
                # treat tasks CREATED BY someone else as "shared with me"
                return t["created_by"] != self.user["user_id"]
            return True  # "all"

        for t in tasks:
            if not _visible(t):
                continue

            # build title (add shared badge if not created by me)
            title = t["title"]
            if t["created_by"] != self.user["user_id"]:
                title += "   🤝"

            item = QtWidgets.QListWidgetItem(title)
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

        # --- UPDATE SUMMARY CHIPS (always based on ALL tasks) ---
        total = len(tasks)
        completed = sum(1 for t in tasks if t["is_complete"])
        pending = total - completed

        if hasattr(self, "total_chip"):
            self.total_chip.setText(f"🌟 Total: {total}")
        if hasattr(self, "completed_chip"):
            self.completed_chip.setText(f"✔ Done: {completed}")
        if hasattr(self, "pending_chip"):
            self.pending_chip.setText(f"✏ Pending: {pending}")

        # update progress bar + vibe
        pct = int((completed / total) * 100) if total > 0 else 0
        if hasattr(self, "progress_bar"):
            self.progress_bar.setValue(pct)

        if hasattr(self, "vibe_label"):
            if total == 0:
                vibe = "No tasks yet — start a mission ✨"
            elif pct == 0:
                vibe = "Let’s start with one task 🌱"
            elif pct < 50:
                vibe = "Nice, you’re getting into orbit 🚀"
            elif pct < 100:
                vibe = "So close, keep going ⭐"
            else:
                vibe = "All done — mission complete 🌙"
            self.vibe_label.setText(vibe)

        self._maybe_play_all_done(total, completed)

        # keep date fresh (in case app stays open over midnight)
        self._update_date_label()

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            self._on_select()
        else:
            self.details.setPlainText(
                "No tasks yet!\n\nStart your first mission by clicking “New” 🌙"
            )

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

        # Base meta text
        meta = (
            f"Created by: {creator_label} | "
            f"Updated by: {updater_label} | "
            f"Complete: {t['is_complete']}"
        )

        # --- Shared info ---
        shared_extra = ""
        try:
            # uses same helper as ShareDialog
            shares = task_manager.get_task_shares(t["task_id"])  # list of {user_id, username}
        except Exception:
            shares = []

        # If *you* are not the creator, show who shared it with you
        if t.get("created_by") is not None and t["created_by"] != self.user["user_id"]:
            shared_extra = f" | Shared by: {creator_label}"
        else:
            # You are the creator – show who you shared it with (if anyone)
            if shares:
                # exclude yourself from the list if present
                other_names = [
                    s.get("username", str(s.get("user_id")))
                    for s in shares
                    if s.get("user_id") != self.user["user_id"]
                ]
                if other_names:
                    shared_extra = " | Shared with: " + ", ".join(other_names)

        meta += shared_extra

        # Write meta + full details into the right panel
        self.details.setPlainText(meta + "\n\n" + t.get("details", ""))

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
            sound_player.play("onetask.mp3")
            self._play_complete_effect(item)

        # --- UPDATE PROGRESS BAR + VIBE IMMEDIATELY ---
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks if t["is_complete"])

        if hasattr(self, "progress_bar"):
            pct = int((completed / total) * 100) if total > 0 else 0
            self.progress_bar.setValue(pct)

        if hasattr(self, "vibe_label"):
            if total == 0:
                vibe = "No tasks yet — start a mission ✨"
            elif pct == 0:
                vibe = "Let’s start with one task 🌱"
            elif pct < 50:
                vibe = "Nice, you’re getting into orbit 🚀"
            elif pct < 100:
                vibe = "So close, keep going ⭐"
            else:
                vibe = "All done — mission complete 🌙"

            self.vibe_label.setText(vibe)

        self._maybe_play_all_done(total, completed)

    def _on_new(self):
        dialog = NewTaskDialog(self.user["user_id"], self)
        if dialog.exec_():
            self.refresh()
            sound_player.play("createtask.mp3")

    def _on_share(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Share", "Select a task first")
            return

        item = self.list_widget.currentItem()
        task_id = item.data(QtCore.Qt.UserRole)

        dlg = ShareDialog(task_id, self.user["user_id"], self)
        dlg.exec_()

    def _on_edit(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Edit Task", "Select a task first")
            return

        item = self.list_widget.currentItem()
        task_id = item.data(QtCore.Qt.UserRole)

        task = None
        for t in self._tasks:
            if t["task_id"] == task_id:
                task = t
                break

        if task is None:
            QtWidgets.QMessageBox.warning(self, "Edit Task", "Task not found.")
            return

        dlg = EditTaskDialog(task, self.user["user_id"], self)
        if dlg.exec_():
            # reload tasks so list + details show updated text
            self.refresh()

    def _on_delete(self):
        row = self.list_widget.currentRow()
        if row < 0:
            QtWidgets.QMessageBox.warning(self, "Delete Task", "Select a task first")
            return

        item = self.list_widget.currentItem()
        task_id = item.data(QtCore.Qt.UserRole)

        confirm = QtWidgets.QMessageBox.question(
            self,
            "Delete Task",
            f"Delete '{item.text()}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if confirm != QtWidgets.QMessageBox.Yes:
            return

        ok, msg = task_manager.delete_task(task_id, self.user["user_id"])
        QtWidgets.QMessageBox.information(self, "Delete Task", msg)
        if ok:
            sound_player.play("deletetask.mp3")
            self.refresh()

    def _on_logout(self):
        self.logout_requested.emit()
        self.close()

    def closeEvent(self, event):
        if self._closing_with_sound:
            return super().closeEvent(event)

        played = sound_player.play("goodbye.mp3")
        if played:
            event.ignore()
            self._closing_with_sound = True
            QtCore.QTimer.singleShot(600, self.close)
            return

        super().closeEvent(event)


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
