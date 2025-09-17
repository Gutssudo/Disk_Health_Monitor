"""Point d'entrée principal pour l'application Qt."""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from disk_health.ui import SmartMonitor
from disk_health.utils import SmartctlNotFoundError


def main() -> None:
    """Lance l'application principale."""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    try:
        monitor = SmartMonitor()
        monitor.show()
        sys.exit(app.exec())
    except SmartctlNotFoundError as e:
        # Afficher le message d'erreur dans une boîte de dialogue
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Smartctl introuvable")
        msg.setText(str(e))
        msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()
