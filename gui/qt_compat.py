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

# Align signal/slot naming so the rest of the codebase can always use the PyQt API.
if not hasattr(QtCore, "pyqtSignal") and hasattr(QtCore, "Signal"):
    QtCore.pyqtSignal = QtCore.Signal
if not hasattr(QtCore, "pyqtSlot") and hasattr(QtCore, "Slot"):
    QtCore.pyqtSlot = QtCore.Slot

__all__ = ["QtWidgets", "QtCore", "QtGui", "backend"]
