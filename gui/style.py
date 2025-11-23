def get_stylesheet():
    """Return a pastel, soft lavender stylesheet for the app.

    The stylesheet aims for a kawaii / pastel aesthetic: light lavender
    background, rounded boxes, thin purple outlines, and soft gradients.
    """
    return r'''
/* GLOBAL LOGIN-STYLE FONT APPLIED TO ENTIRE APP */
QWidget, QMainWindow, QDialog, QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget, QListWidget::item {
  font-family: "Segoe UI Semilight", "Segoe UI", "Helvetica Neue", Arial;
  font-size: 14px;                  /* softer, rounder, login vibe */
  color: #4b3670;                   /* same purple-gray as login */
  letter-spacing: 0.3px;            /* subtle cute spacing */
}

/* Subtle textured look using radial gradient overlay on main widgets */
QWidget::before {
  /* Not a real pseudo-element; kept for reference if using custom painting */
}

/* Rounded panels (list and detail area) */
QListWidget, QTextEdit, QLineEdit {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #fbf7ff);
  border: 1px solid rgba(150, 115, 255, 0.35);
  border-radius: 10px;
  padding: 8px;
}

/* List items styled as soft cards */
QListWidget::item {
  background: transparent;
  margin: 6px;
  padding: 10px;
  border-radius: 10px;
}
QListWidget::item:selected {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #f6ecff, stop:1 #efe0ff);
  border: 1px solid rgba(170,120,255,0.5);
  color: #3a2b4a; /* dark lavender text for readability on selection */
}

/* Make the list area look like stacked cards */
QListWidget {
  outline: none;
}

/* LOGIN STYLE BUTTONS — APPLIED GLOBALLY */
QPushButton {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
      stop:0 #ffffff,
      stop:1 #f4ebff);
  border: 1px solid rgba(150,115,255,0.4);
  padding: 8px 16px;
  border-radius: 14px;
  font-weight: 500;                 /* Same as login */
  color: #5a3e85;                   /* Login’s soft purple */
}

QPushButton:hover {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
      stop:0 #ffffff,
      stop:1 #ecddff);
}

QPushButton:pressed {
  background: #e4d4ff;
}

QLineEdit, QTextEdit {
  background: #ffffff;
  border: 1px solid rgba(150,115,255,0.35);
  border-radius: 10px;
  padding: 6px 10px;
}

QLineEdit:focus, QTextEdit:focus {
  border: 1px solid rgba(150,115,255,0.7);
}

/* ❌ GLOBAL INDICATOR RULE DISABLED — breaks QListWidget checkboxes */
/*
QCheckBox::indicator, QListView::indicator, QListWidget::indicator, QTreeView::indicator, QTableView::indicator {
  width: 18px; height: 18px; border-radius: 6px;
}
*/

/* Title area style */
QLabel.title {
  font-size: 16px;
  font-weight: 600;
  color: #45335a;
}

/* Small subtle footer text */
QLabel.subtle {
  color: rgba(58,43,74,0.6);
  font-size: 11px;
}

/* --- FIX: VISIBLE PURPLE CHECKBOXES IN TASK LIST --- */
QListWidget#todoList QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 6px;
    border: 2px solid #d9b3ff;
    background: #f8f0ff;
}

QListWidget#todoList QCheckBox::indicator:checked {
    background: #d6b0ff;
    border-color: #b07bff;
}

/* ================================
   Login Dialog – Cute Pastel Style
   ================================*/

QDialog#loginDialog {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
    stop:0 #fbf6ff, stop:1 #f3eaff);
  border-radius: 18px;
}

/* Pretty title */
QLabel#loginTitle {
  font-size: 20px;
  font-weight: 600;
  color: #5a4385;
}

QLabel#loginSubtitle {
  font-size: 11px;
  color: rgba(90, 67, 133, 0.7);
}

/* Rounded pastel inputs */
QDialog#loginDialog QLineEdit {
  background: #ffffff;
  border-radius: 14px;
  padding: 8px 12px;
  border: 1px solid rgba(150, 115, 255, 0.45);
}

QDialog#loginDialog QLineEdit:focus {
  border: 1px solid rgba(150, 115, 255, 0.9);
}

/* Buttons */
QPushButton#loginPrimaryBtn {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
    stop:0 #ffffff, stop:1 #f5ecff);
  border-radius: 14px;
  border: 1px solid rgba(140, 105, 240, 0.7);
  padding: 8px 16px;
  font-weight: 500;
}

QPushButton#loginPrimaryBtn:hover {
  background: #f0e6ff;
}

QPushButton#loginSecondaryBtn {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
    stop:0 #fff, stop:1 #f8f1ff);
  border-radius: 14px;
  border: 1px solid rgba(180, 150, 255, 0.5);
  padding: 8px 16px;
}

QPushButton#loginSecondaryBtn:hover {
  background: #f3e7ff;
}

'''
