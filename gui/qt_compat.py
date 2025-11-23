"""Compatibility shim: prefer PyQt5, fall back to PySide6 if needed."""
try:
    from PyQt5 import QtWidgets, QtCore, QtGui
    backend = "PyQt5"
except Exception:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
        backend = "PySide6"
    except Exception:
        raise ImportError("Requires PyQt5 or PySide6. Install with 'pip install PyQt5' or 'pip install PySide6'.")

__all__ = ["QtWidgets", "QtCore", "QtGui", "backend"]
