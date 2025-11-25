def get_stylesheet():
    """Return a pastel, soft lavender stylesheet for the app.

    The stylesheet aims for a kawaii / pastel aesthetic: light lavender
    background, rounded boxes, thin purple outlines, and soft gradients.
    """
    return r'''
/* GLOBAL LOGIN-STYLE FONT APPLIED TO ENTIRE APP */
QWidget, QMainWindow, QDialog, QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget, QListWidget::item {
  font-family: "Segoe UI Semilight", "Segoe UI", "Helvetica Neue", Arial;
  font-size: 12pt;                  /* scalable base size */
  color: #4b3670;                   /* same purple-gray as login */
  letter-spacing: 0.3px;            /* subtle cute spacing */
}

/* 🌌 Aurora Lights only on the main window background */
QMainWindow {
    background:
        qlineargradient(
            x1:0, y1:0,
            x2:1, y2:1,
            stop:0   rgba(190, 255, 110, 0.25),
            stop:0.35 rgba(155, 120, 255, 0.32),
            stop:0.6 rgba(255, 235, 255, 0.30),
            stop:1   rgba(205, 175, 255, 0.28)
        );
}

/* Subtle textured look using radial gradient overlay on main widgets */
QWidget::before {
  /* Not a real pseudo-element; kept for reference if using custom painting */
}

QListWidget#todoList {
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff,
        stop:1 #faf6ff);     /* soft lavender tint */
    border: 1px solid rgba(170, 120, 255, 0.25);
    border-radius: 18px;
}

/* Frosted-glass panel for the details area */
QTextEdit {
  background: qlineargradient(
      spread:pad, x1:0, y1:0, x2:0, y2:1,
      stop:0 #ffffffdd,
      stop:1 #fbf7ffdd
  );
  border: 1px solid rgba(150, 115, 255, 0.35);
  border-radius: 20px;
  padding: 18px;
  box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.06);
}

/* Keep line edits simple and rounded */
QLineEdit {
  background: #ffffff;
  border: 1px solid rgba(150,115,255,0.35);
  border-radius: 10px;
  padding: 6px 10px;
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
  font-size: 13pt;
  font-weight: 600;
  color: #45335a;
}

/* Small subtle footer text */
QLabel.subtle {
  color: rgba(58,43,74,0.6);
  font-size: 10pt;
}

QLabel#panelTitle {
  font-size: 13pt;
  font-weight: 600;
  color: #f5f0ff;
  margin-bottom: 6px;
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
   Login Dialog
   ================================*/

QDialog#loginDialog {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
    stop:0 #f0e4ff,      /* slightly darker top */
    stop:0.5 #e0d2ff,
    stop:1 #c5b2ff);     /* deeper lavender bottom so logo pops */
  border-radius: 18px;
  border: 1px solid rgba(185, 255, 90, 0.45);  /* PlanIt green outline */
}

/* Logo spacing */
QLabel#loginLogo {
  margin-bottom: 4px;
}

/* Main title: "Log in to PlanIt" */
QLabel#loginTitle {
  font-size: 18pt;
  font-weight: 600;
  color: #ffffff;                 /* bright against darker bg */
}

/* Small helper text */
QLabel#loginSubtitle {
  font-size: 11pt;
  color: rgba(230, 225, 255, 0.85);
}

/* Inputs with subtle green focus accent */
QDialog#loginDialog QLineEdit {
  background: #ffffff;
  border-radius: 14px;
  padding: 8px 12px;
  border: 1px solid rgba(150, 115, 255, 0.6);
}

QDialog#loginDialog QLineEdit:focus {
  border: 1px solid #b9ff5a;   /* PlanIt green */
}

/* Primary button – purple with green border accent */
QPushButton#loginPrimaryBtn {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
    stop:0 #ffffff,
    stop:1 #f3e7ff);
  border-radius: 14px;
  border: 1px solid #b9ff5a;   /* PlanIt green */
  padding: 8px 16px;
  font-weight: 500;
  color: #4b2f78;
}

QPushButton#loginPrimaryBtn:hover {
  background: #f4ffe6;          /* soft pastel green glow */
  border-color: #b9ff5a;        /* same PlanIt green accent */
  color: #4b2f78;               /* keep purple text readable */
}

/* Secondary button – softer purple, still inside theme */
QPushButton#loginSecondaryBtn {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
    stop:0 #fdfbff,
    stop:1 #f6edff);
  border-radius: 14px;
  border: 1px solid #b9ff5a;
  padding: 8px 16px;
  color: #4b2f78;
}

QPushButton#loginSecondaryBtn:hover {
  background: #f4ffe6;          /* soft pastel green glow */
  border-color: #b9ff5a;        /* same PlanIt green accent */
  color: #4b2f78;               /* keep the same purple text */
}

/* ================================
   ✨ PlanIt Dialog Theme
   (Used for New Task, Edit Task, Share)
   ================================*/

QDialog {
    background: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:1,
        stop:0 #f4e9ff,
        stop:0.5 #ebddff,
        stop:1 #d4c2ff
    );
    border-radius: 18px;
    border: 1px solid rgba(185, 255, 90, 0.45);   /* PlanIt green outline */
    padding: 12px;
}

/* Inputs */
QDialog QLineEdit,
QDialog QTextEdit {
    background: #ffffff;
    border-radius: 14px;
    padding: 10px 12px;
    border: 1px solid rgba(150,115,255,0.55);
    font-size: 12pt;
}

QDialog QLineEdit:focus,
QDialog QTextEdit:focus {
    border: 1px solid #b9ff5a;                   /* PlanIt green glow */
    background: #ffffff;
}

/* Buttons */
QDialog QPushButton {
    background: qlineargradient(
        spread:pad, x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff,
        stop:1 #f3e7ff
    );
    border-radius: 14px;
    border: 1px solid #b9ff5a;                   /* green accent */
    padding: 8px 16px;
    font-weight: 500;
    color: #4b2f78;
}

QDialog QPushButton:hover {
    background: #f4ffe6;                         /* soft green glow */
}

/* Make dialog look less cramped */
QDialog QWidget {
    margin-top: 6px;
}

/* ================================
   Dashboard Header + Chips + Date
   ================================*/

/* Dashboard header: mascot + welcome text */
QLabel#mascotLabel {
  margin-right: 8px;
}

/* Long header bar that wraps mascot + welcome + date */
QWidget#topHeaderBar {
    background: rgba(255, 255, 255, 0.35);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.55);
    margin-bottom: 6px;           /* tiny gap under the bar */
}

/* BIG welcome text (flattened, no inner box) */
QLabel#welcomeHeader {
    font-size: 22pt;
    font-weight: 600;
    color: #5a3e85;           /* soft purple */
    padding: 0px 4px;
    background: transparent;
    border: none;
}

/* Cute task summary chips under welcome header – medium */
QLabel[chip="true"] {
  background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
    stop:0 #ffffff,
    stop:1 #f5ecff);
  border-radius: 999px;             /* pill shape */
  border: 1px solid rgba(185, 255, 90, 0.6);  /* PlanIt green accent */
  padding: 6px 14px;
  margin-right: 8px;
  font-size: 12pt;
  color: #4b2f78;
}

/* Soft pastel date text on header */
QLabel#dateBadge {
    background: transparent;
    border: none;
    padding: 0px;
    font-size: 14pt;
    font-weight: 500;
    color: #ffffff;      /* white so it pops on header */
}

/* === DASHBOARD LAYOUT SPACING === */

/* The whole window gets inner margins */
QWidget#centralWidget {
    padding: 20px;
}

/* List + details white blocks get extra spacing away from edges */
QListWidget#todoList {
    margin: 12px;
}

QTextEdit {
    margin: 12px;
}

/* The whole right details column gets breathing space (used if you set objectName) */
QWidget#rightColumn {
    padding: 10px;
}

QWidget#footerBar {
  background: rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.26);
  padding: 4px;
}

/* Bigger progress bar */
QProgressBar {
    background: rgba(255, 255, 255, 0.25);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.35);
    height: 28px;
    min-height: 28px;
    margin-top: 10px;
    margin-bottom: 14px;
}

QProgressBar::chunk {
    border-radius: 14px;
    background: qlineargradient(
        spread:pad, x1:0, y1:0, x2:1, y2:0,
        stop:0 #c7ff89,
        stop:1 #e8d1ff
    );
}

/* Larger vibe text */
QLabel#vibeLabel {
    font-size: 11pt;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.95);
    margin-top: 8px;
    margin-bottom: 12px;
}

/* ================================
   To-Do List Item & Details Text
   ================================*/

/* Bigger task list text */
QListWidget#todoList {
    font-size: 14pt;
    font-family: "Segoe UI Semilight";
}

/* Text specifically inside list items */
QListWidget#todoList::item {
    font-size: 14pt;
    padding: 10px;
}

/* When selected */
QListWidget#todoList::item:selected {
    font-size: 14pt;
}

/* Checkbox label text size inside list */
QListWidget#todoList QCheckBox {
    font-size: 14pt;
}

/* Bigger details panel text (meta + description) */
QTextEdit {
    font-size: 13pt;
    line-height: 1.35;
}
'''
