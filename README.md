# 🌙 PlanIt — A Pastel Productivity Task Manager

PlanIt is a **space-themed productivity application** built with **PyQt5**, focused on simplicity and encrypted task sharing.
The app allows users to create tasks, collaborate securely, and track progress using a clean, aesthetic dashboard.

---

### 📝 Task Management
- Create / edit / delete tasks  
- View task details in a panel  
- Progress bar with motivational messages  

### 🔐 Encrypted Tasks
- All task contents are encrypted using PyCryptodome (AES-GCM)  
- Secure storage for shared or personal tasks  

### 🤝 Task Sharing
- Share tasks with other registered users  
- “Shared by: …” display on each task  
- Great for group projects or planning  

### 🔍 Task Filters
- **All**, **Done**, **Pending**  
- Instant filtering with no reload  

### 👥 Multi-User Login
- Secure login system  
- Each user has their own dashboard  

---

## 👥 Test Accounts Included

These users are **already created in the database** for easy testing:

| Username | Password |
|----------|----------|
| **ella** | **test123** |
| **jane** | **test123** |

Just log in using these credentials after launching the program.

---

## 🧩 Tech Stack

| Component | Technology |
|----------|------------|
| GUI | PyQt5 |
| Encryption | PyCryptodome |
| Icons | QtAwesome |
| Database | SQLite |
| Backend | Python |
| Testing | pytest |

---

## 🔧 Installation Guide

Use this command to install requirements:
pip install -r requirements.txt
