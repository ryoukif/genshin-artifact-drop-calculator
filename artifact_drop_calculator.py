import sys
import math
from PyQt5 import QtWidgets, QtCore, QtGui

class ArtifactDropCalculator(QtWidgets.QWidget):
    """
    Genshin Impact Artifact Drop Calculator (PyQt5)
    Calculates probability and expected runs for a specific artifact configuration,
    including Main Stat, flexible Substat selection, and detailed breakdown.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Genshin Artifact Drop Calculator")
        self.resize(600, 700)  # Adjust window size
        self._init_data()
        self._init_ui()

    def _init_data(self):
        # Main Stat mapping for each piece
        self.main_stats_map = {
            "Flower of Life": ["HP"],
            "Plume of Death": ["ATK"],
            "Sands of Eon": ["HP%", "ATK%", "DEF%", "Energy Recharge%", "Elemental Mastery"],
            "Goblet of Eonothem": [
                "ATK%", "HP%", "DEF%", "Elemental Mastery",
                "Physical DMG Bonus%",
                "Pyro DMG Bonus%", "Cryo DMG Bonus%", "Hydro DMG Bonus%", "Anemo DMG Bonus%",
                "Electro DMG Bonus%", "Geo DMG Bonus%", "Dendro DMG Bonus%"
            ],
            "Circlet of Logos": ["ATK%", "HP%", "DEF%", "CRIT Rate%", "CRIT DMG%", "Healing Bonus%", "Elemental Mastery"]
        }
        # All possible substats
        self.substat_list = [
            "ATK", "ATK%", "DEF", "DEF%", "HP", "HP%",
            "CRIT Rate%", "CRIT DMG%", "Elemental Mastery", "Energy Recharge%"
        ]

    def _init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        font = QtGui.QFont()
        font.setPointSize(11)
        self.setFont(font)

        # Artifact Set Selection
        self.set_combo = QtWidgets.QComboBox()
        self.set_combo.addItems(["Set 1", "Set 2", "Either Set"])
        layout.addWidget(QtWidgets.QLabel("Select Artifact Set:"))
        layout.addWidget(self.set_combo)

        # Artifact Piece Selection
        self.piece_combo = QtWidgets.QComboBox()
        self.piece_combo.addItems(self.main_stats_map.keys())
        self.piece_combo.currentTextChanged.connect(self._update_main_stats)
        layout.addWidget(QtWidgets.QLabel("Select Artifact Piece:"))
        layout.addWidget(self.piece_combo)

        # Main Stat Selection
        self.main_stat_combo = QtWidgets.QComboBox()
        layout.addWidget(QtWidgets.QLabel("Select Main Stat:"))
        layout.addWidget(self.main_stat_combo)
        self._update_main_stats(self.piece_combo.currentText())

        # Substat count selection
        self.subcount_combo = QtWidgets.QComboBox()
        self.subcount_combo.addItems(["Any", "3 Substats (80%)", "4 Substats (20%)"])
        self.subcount_combo.currentTextChanged.connect(self._update_sublist_state)
        layout.addWidget(QtWidgets.QLabel("Number of starting Substats:"))
        layout.addWidget(self.subcount_combo)

        # Substat selection
        layout.addWidget(QtWidgets.QLabel("Desired Substats (optional, select 1 to N):"))
        self.sub_list = QtWidgets.QListWidget()
        self.sub_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.sub_list.setMinimumHeight(200)
        self.sub_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        for stat in self.substat_list:
            self.sub_list.addItem(stat)
        layout.addWidget(self.sub_list)
        self._update_sublist_state(self.subcount_combo.currentText())

        # Calculate Button
        self.calc_button = QtWidgets.QPushButton("Calculate Probability")
        self.calc_button.setMinimumHeight(40)
        self.calc_button.clicked.connect(self.calculate)
        layout.addWidget(self.calc_button)

        # Dark Mode Toggle
        self.darkmode_checkbox = QtWidgets.QCheckBox("Enable Dark Mode")
        self.darkmode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.darkmode_checkbox)

        # Result Display
        self.result_label = QtWidgets.QLabel("")
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet("QLabel { font-size: 12pt; }")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def _update_main_stats(self, piece_name: str):
        self.main_stat_combo.clear()
        for ms in self.main_stats_map.get(piece_name, []):
            self.main_stat_combo.addItem(ms)

    def _update_sublist_state(self, mode: str):
        if mode.startswith("Any"):
            self.sub_list.setEnabled(False)
            for i in range(self.sub_list.count()):
                item = self.sub_list.item(i)
                item.setSelected(False)
        else:
            self.sub_list.setEnabled(True)

    def calculate(self):
        choice = self.set_combo.currentText()
        p_set = 1.0 if choice == "Either Set" else 0.5

        p_piece = p_set * (1/5)
        piece = self.piece_combo.currentText()
        main_options = self.main_stats_map[piece]
        p_main = 1 / len(main_options)

        mode = self.subcount_combo.currentText()
        p_subroll = 1.0
        p_subs = 1.0
        N = 0

        if mode.startswith("3"):
            N = 3
            p_subroll = 0.8
        elif mode.startswith("4"):
            N = 4
            p_subroll = 0.2

        details = []
        details.append(f"Set chance: {p_set*100:.2f}%")
        details.append(f"Piece chance: {p_piece*100:.2f}%")
        details.append(f"Main Stat chance: {p_main*100:.2f}%")

        if N == 0:
            details.append("Starting Substats: Any (p_subroll=1.0)")
        else:
            details.append(f"Starting Substats: {N} (p_subroll={p_subroll})")

        if mode.startswith("Any"):
            p_subs = 1.0
            details.append("Substats: Any (p_subs=1.0)")
        elif N in (3, 4):
            selected = self.sub_list.selectedItems()
            r = len(selected)
            if r > N:
                QtWidgets.QMessageBox.warning(self, "Selection Error", f"Max {N} substats allowed.")
                return
            total_sub = len(self.substat_list)
            if r == 0:
                p_subs = 1.0
                details.append("Substats: none selected (p_subs=1.0)")
            else:
                favorable = math.comb(total_sub - r, N - r)
                total = math.comb(total_sub, N)
                p_subs = favorable / total
                details.append(f"Substats: {r} selected (p_subs={p_subs:.6f})")

        p_total = p_piece * p_main * p_subroll * p_subs
        expected = (1 / p_total) if p_total > 0 else float('inf')

        breakdown = (
            "Calculation Details:\n"
            + "\n".join(details)
            + f"\n\nTotal Probability: {p_total*100:.6f}%"
            + f"\nExpected Runs: {expected:.1f}"
        )

        self.result_label.setText(breakdown)

    def _apply_dark_mode(self):
        dark_palette = QtGui.QPalette()
        dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
        dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        dark_palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        dark_palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
        dark_palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.setPalette(dark_palette)

        self.setStyleSheet("""
            QWidget {
                background-color: #353535;
                color: white;
                font-size: 11pt;
            }
            QComboBox, QAbstractItemView, QListWidget {
                background-color: #252525;
                color: white;
                selection-background-color: #8e2dc5;
            }
            QPushButton {
                background-color: #444;
                color: white;
                border: 1px solid #666;
                padding: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QScrollBar:vertical {
                background: #252525;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #666;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #888;
            }
        """)

    def _apply_light_mode(self):
        self.setPalette(QtGui.QPalette())
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
                font-size: 11pt;
            }
            QComboBox, QAbstractItemView, QListWidget {
                background-color: white;
                color: black;
                selection-background-color: #d0d0d0;
            }
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                border: 1px solid #aaa;
                padding: 6px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background: #ccc;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #aaa;
            }
        """)

    def toggle_dark_mode(self, state):
        if state == QtCore.Qt.Checked:
            self._apply_dark_mode()
        else:
            self._apply_light_mode()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = ArtifactDropCalculator()
    win.show()
    sys.exit(app.exec_())
