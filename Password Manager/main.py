from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QToolButton,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QSpinBox,
    QTextEdit,
    QMessageBox,
    QDialog,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QSizePolicy,
)
import uuid
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
import secrets
import string
import json
import os
import sys
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')

def load_entries():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def save_entries(entries):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

def add_entry(entry: dict):
    entries = load_entries()
    if 'id' not in entry:
        entry = dict(entry)
        entry['id'] = str(uuid.uuid4())
    entries.append(entry)
    save_entries(entries)

def update_entry(entry_id: str, new_entry: dict):
    entries = load_entries()
    changed = False
    for i, e in enumerate(entries):
        if e.get('id') == entry_id:
            new = dict(new_entry)
            new['id'] = entry_id
            entries[i] = new
            changed = True
            break
    if changed:
        save_entries(entries)
    return changed

def delete_entry(entry_id: str):
    entries = load_entries()
    new_entries = [e for e in entries if e.get('id') != entry_id]
    if len(new_entries) == len(entries):
        return False
    save_entries(new_entries)
    return True
class PasswordGeneratorWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Generator")
        self.setGeometry(600, 250, 420, 220)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        row = QHBoxLayout()
        row.addWidget(QLabel("Length:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(4, 128)
        self.length_spin.setValue(16)
        row.addWidget(self.length_spin)
        layout.addLayout(row)

        self.chk_upper = QCheckBox("Uppercase")
        self.chk_upper.setChecked(True)
        self.chk_lower = QCheckBox("Lowercase")
        self.chk_lower.setChecked(True)
        self.chk_digits = QCheckBox("Digits")
        self.chk_digits.setChecked(True)
        self.chk_symbols = QCheckBox("Symbols")
        self.chk_symbols.setChecked(True)

        layout.addWidget(self.chk_upper)
        layout.addWidget(self.chk_lower)
        layout.addWidget(self.chk_digits)
        layout.addWidget(self.chk_symbols)

        gen_btn = QPushButton("Generate")
        gen_btn.clicked.connect(self.generate_password)
        layout.addWidget(gen_btn)

        out_row = QHBoxLayout()
        self.out_edit = QLineEdit()
        out_row.addWidget(self.out_edit)
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        out_row.addWidget(copy_btn)
        use_btn = QPushButton("Use")
        use_btn.clicked.connect(self.use_password)
        out_row.addWidget(use_btn)
        layout.addLayout(out_row)

        self.setLayout(layout)

    def generate_password(self):
        length = self.length_spin.value()
        pool = ""
        if self.chk_upper.isChecked():
            pool += string.ascii_uppercase
        if self.chk_lower.isChecked():
            pool += string.ascii_lowercase
        if self.chk_digits.isChecked():
            pool += string.digits
        if self.chk_symbols.isChecked():
            pool += string.punctuation
        if not pool:
            QMessageBox.warning(self, "No charset", "Select at least one character set")
            return
        pwd = ''.join(secrets.choice(pool) for _ in range(length))
        self.out_edit.setText(pwd)

    def copy_to_clipboard(self):
        pwd = self.out_edit.text()
        if not pwd:
            return
        QApplication.clipboard().setText(pwd)
        QMessageBox.information(self, "Copied", "Password copied to clipboard")

    def use_password(self):
        pwd = self.out_edit.text()
        if not pwd:
            return
        parent = self.parent()
        if parent is not None:
            if hasattr(parent, 'pw_edit'):
                try:
                    parent.pw_edit.setText(pwd)
                except Exception:
                    pass
            elif hasattr(parent, 'editor') and parent.editor is not None:
                try:
                    parent.editor.pw_edit.setText(pwd)
                except Exception:
                    pass
        QApplication.clipboard().setText(pwd)
        self.accept()


class StrengthCheckerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Strength Checker")
        self.setGeometry(650, 300, 480, 240)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter password to evaluate:"))
        self.input_edit = QLineEdit()
        self.input_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_edit)
        eval_btn = QPushButton("Evaluate")
        eval_btn.clicked.connect(self.evaluate)
        layout.addWidget(eval_btn)
        self.result_label = QLabel("")
        layout.addWidget(self.result_label)
        self.setLayout(layout)

    def evaluate(self):
        pwd = self.input_edit.text()
        score, desc = self.score_password(pwd)
        self.result_label.setText(f"Strength: {desc} ({score}/10)")

    def score_password(self, pwd: str):
        if not pwd:
            return 0, "Empty"
        score = 0
        length = len(pwd)
        if length >= 8:
            score += 2
        if length >= 12:
            score += 2
        types = 0
        if any(c.islower() for c in pwd):
            types += 1
        if any(c.isupper() for c in pwd):
            types += 1
        if any(c.isdigit() for c in pwd):
            types += 1
        if any(c in string.punctuation for c in pwd):
            types += 1
        score += types * 1
        unique_chars = len(set(pwd))
        if unique_chars > 6:
            score += 1
        if unique_chars > 12:
            score += 1
        if score > 10:
            score = 10
        if score >= 8:
            desc = "Very Strong"
        elif score >= 6:
            desc = "Strong"
        elif score >= 4:
            desc = "Medium"
        else:
            desc = "Weak"
        return score, desc


class AccountEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entry_id = None
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Label / Account:"))
        self.label_edit = QLineEdit()
        layout.addWidget(self.label_edit)
        layout.addWidget(QLabel("Password:"))
        pw_row = QHBoxLayout()
        self.pw_edit = QLineEdit()
        self.pw_edit.setEchoMode(QLineEdit.Password)
        pw_row.addWidget(self.pw_edit)
        paste_btn = QPushButton("Paste")
        paste_btn.clicked.connect(self.paste_from_clipboard)
        pw_row.addWidget(paste_btn)
        gen_btn = QPushButton("Open Generator")
        gen_btn.clicked.connect(self.open_generator)
        pw_row.addWidget(gen_btn)
        layout.addLayout(pw_row)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.cancel)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

        self.setLayout(layout)

    def load_entry(self, entry: dict):
        self.entry_id = entry.get('id')
        self.label_edit.setText(entry.get('label', ''))
        self.pw_edit.setText(entry.get('password', ''))

    def new_entry(self):
        self.entry_id = None
        self.label_edit.clear()
        self.pw_edit.clear()

    def paste_from_clipboard(self):
        txt = QApplication.clipboard().text()
        if txt:
            self.pw_edit.setText(txt)

    def open_generator(self):
        win = PasswordGeneratorWindow(parent=self)
        win.exec_()

    def save(self):
        label = self.label_edit.text().strip()
        pw = self.pw_edit.text()
        if not label or not pw:
            QMessageBox.warning(self, "Missing", "Please provide label and password")
            return
        try:
            if self.entry_id:
                ok = update_entry(self.entry_id, {'label': label, 'password': pw})
                if ok:
                    QMessageBox.information(self, "Saved", f"Updated entry '{label}'")
                else:
                    QMessageBox.warning(self, "Not found", "Original entry not found; creating new")
                    add_entry({'label': label, 'password': pw})
            else:
                add_entry({'label': label, 'password': pw})
                QMessageBox.information(self, "Saved", f"Saved entry '{label}' to data.json")

            main = self.parent()
            if main is not None and hasattr(main, 'refresh_accounts'):
                try:
                    main.refresh_accounts()
                except Exception:
                    pass
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save: {e}")

    def cancel(self):
        main = self.parent()
        if main is not None and hasattr(main, 'show_welcome'):
            main.show_welcome()


class MainWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RandPass")
        self.setWindowIcon(QIcon("static/icon.png"))
        self.setGeometry(500, 200, 1000, 700)

        self._build_toolBar()
        content = QWidget()
        cl = QVBoxLayout()
        content.setLayout(cl)
        self.setCentralWidget(content)

    def _build_toolBar(self):
        toolbar = self.addToolBar("Main toolbar")
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        toolbar.setMovable(False)
        toolbar.setOrientation(Qt.Vertical)
        toolbar.setFixedWidth(160)
        self.toolbar = toolbar

        new_button = QToolButton()
        edit_button = QToolButton()
        delete_button = QToolButton()
        gen_button = QToolButton()
        strength_button = QToolButton()
        new_button.setText("New")
        edit_button.setText("Edit")
        delete_button.setText("Delete")
        gen_button.setText("Generator")
        strength_button.setText("Strength")

        style = """
            QPushButton, QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #6fb3ff, stop:1 #1c86ff);
                color: white;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton:hover, QToolButton:hover {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 #84c6ff, stop:1 #2b95ff);
            }
            QPushButton:pressed, QToolButton:pressed {
                background: #0f66d0;
            }
        """
        for btn in (new_button, edit_button, gen_button, strength_button, delete_button):
            btn.setStyleSheet(style)

        new_button.clicked.connect(lambda: self.show_editor(None))
        edit_button.clicked.connect(lambda: self.edit())
        delete_button.clicked.connect(lambda: self.delete_selected())
        gen_button.clicked.connect(lambda: self.open_generator())
        strength_button.clicked.connect(lambda: self.open_strength_checker())

        
        btn_container = QWidget()
        vbox = QVBoxLayout()
        vbox.setContentsMargins(8, 8, 8, 8)
        vbox.setSpacing(10)
        for b in (new_button, edit_button, delete_button, gen_button, strength_button):
            row_w = QWidget()
            row_h = QHBoxLayout()
            row_h.setContentsMargins(0, 0, 0, 0)
            row_h.addStretch()
            row_h.addWidget(b)
            row_h.addStretch()
            row_w.setLayout(row_h)
            vbox.addWidget(row_w)

        btn_container.setLayout(vbox)
        toolbar.addWidget(btn_container)
        toolbar.addSeparator()
        self.accounts_list = QListWidget()
        self.accounts_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.accounts_list.itemClicked.connect(self._on_item_click)
        toolbar.addWidget(self.accounts_list)
        self.editor = None
        self.show_welcome()
        self.refresh_accounts()

    def _build_account_list(self):
        self.refresh_accounts()

    def refresh_accounts(self):
        self.accounts_list.clear()
        for entry in load_entries():
            label = entry.get('label') or '(no label)'
            it = QListWidgetItem(label)
            it.setData(Qt.UserRole, entry)
            pw = entry.get('password', '')
            it.setToolTip('Password: ' + ('*' * len(pw)))
            self.accounts_list.addItem(it)

    def show_welcome(self):
        w = QWidget()
        l = QVBoxLayout()
        lbl = QLabel("Welcome to RandPass")
        lbl.setFont(QFont("SansSerif", 14, QFont.Bold))
        l.addWidget(lbl)
        l.addStretch()
        w.setLayout(l)
        self.setCentralWidget(w)

    def show_editor(self, entry: dict = None):
        # Always create a new editor instance because previous central widgets
        # are deleted by Qt when replaced; reusing a deleted widget caused
        # "wrapped C/C++ object ... has been deleted" runtime errors.
        self.editor = AccountEditor(parent=self)
        if entry:
            self.editor.load_entry(entry)
        else:
            self.editor.new_entry()
        self.setCentralWidget(self.editor)

    def _on_item_double(self, item: QListWidgetItem):
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        pw = entry.get('password', '')
        lbl = entry.get('label', '(no label)')
        QMessageBox.information(self, lbl, f"Password: {pw}")

    def _on_item_click(self, item: QListWidgetItem):
        entry = item.data(Qt.UserRole)
        if not entry:
            return
        self.show_editor(entry)

    def new(self):
        self.show_editor(None)

    def edit(self):
        cur = self.accounts_list.currentItem()
        if not cur:
            QMessageBox.information(self, "Select", "Please select an account to edit")
            return
        entry = cur.data(Qt.UserRole)
        if not entry:
            QMessageBox.information(self, "Select", "Invalid selection")
            return
        self.show_editor(entry)

    def delete_selected(self):
        cur = self.accounts_list.currentItem()
        if not cur:
            QMessageBox.information(self, "Select", "Please select an account to delete")
            return
        entry = cur.data(Qt.UserRole)
        if not entry:
            QMessageBox.information(self, "Select", "Invalid selection")
            return
        lbl = entry.get('label', '(no label)')
        resp = QMessageBox.question(self, "Delete", f"Delete account '{lbl}'?", QMessageBox.Yes | QMessageBox.No)
        if resp != QMessageBox.Yes:
            return
        ok = delete_entry(entry.get('id'))
        if ok:
            QMessageBox.information(self, "Deleted", f"Deleted '{lbl}'")
            try:
                self.refresh_accounts()
            except Exception:
                pass
            self.show_welcome()
        else:
            QMessageBox.warning(self, "Not found", "Entry not found; nothing deleted")

    def open_generator(self):
        win = PasswordGeneratorWindow(parent=self)
        win.exec_()

    def open_strength_checker(self):
        win = StrengthCheckerWindow(parent=self)
        win.exec_()


def main():
    app = QApplication(sys.argv)
    window = MainWin()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
