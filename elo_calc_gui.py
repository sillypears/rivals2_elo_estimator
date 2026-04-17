#!/usr/bin/env python3
import math
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QRadioButton,
    QPushButton,
    QGroupBox,
    QButtonGroup,
)
from PySide6.QtCore import Qt, QSize


class Prediction:
    def __init__(self, elo_old, elo_opp, win, wins, total, streak):
        self.elo_old = elo_old
        self.elo_opponent = elo_opp
        self.match_win = win
        self.total_wins = wins
        self.total_matches = total
        self.win_streak = streak
        self.predicted_change = 0


def predict_elo_change(
    my_elo,
    opp_elo,
    is_win,
    streak_if_win,
    total_wins_before,
    matches_played_before,
):
    if opp_elo == -2:
        opp_elo = 950
    if matches_played_before < 5:
        k = 120
        apply_bonus = False
    elif matches_played_before < 24:
        k = 40
        apply_bonus = True
    else:
        k = 24
        apply_bonus = True

    exp = 1 / (1 + 10 ** ((opp_elo - my_elo) / 400.0))
    base = k * ((1 if is_win else 0) - exp)

    change = base
    pct = 0.0
    if is_win and apply_bonus:
        thresholds = [250, 500, 700, 900, 1100, 1300, 1500, 1700, 1800]
        rank = sum(1 for t in thresholds if my_elo >= t)
        rank = min(rank, 9)

        bps = [
            [],
            [
                {"s": 1, "e": 3, "p": 0.35},
                {"s": 3, "e": 5, "p": 0.45},
                {"s": 5, "e": 8, "p": 0.5},
                {"s": 8, "e": 10, "p": 0.75},
                {"s": 10, "e": -1, "p": 1},
            ],
            [
                {"s": 1, "e": 3, "p": 0.25},
                {"s": 3, "e": 5, "p": 0.4},
                {"s": 5, "e": 8, "p": 0.45},
                {"s": 8, "e": 10, "p": 0.6},
                {"s": 10, "e": -1, "p": 0.8},
            ],
            [
                {"s": 1, "e": 3, "p": 0.15},
                {"s": 3, "e": 5, "p": 0.25},
                {"s": 5, "e": 8, "p": 0.35},
                {"s": 8, "e": 10, "p": 0.55},
                {"s": 10, "e": -1, "p": 0.75},
            ],
            [
                {"s": 1, "e": 3, "p": 0.05},
                {"s": 3, "e": 5, "p": 0.1},
                {"s": 5, "e": 8, "p": 0.25},
                {"s": 8, "e": 10, "p": 0.4},
                {"s": 10, "e": -1, "p": 0.55},
            ],
            [
                {"s": 1, "e": 3, "p": 0.05},
                {"s": 3, "e": 5, "p": 0.1},
                {"s": 5, "e": 8, "p": 0.2},
                {"s": 8, "e": 10, "p": 0.3},
                {"s": 10, "e": -1, "p": 0.4},
            ],
            [
                {"s": 1, "e": 3, "p": 0.05},
                {"s": 3, "e": 5, "p": 0.1},
                {"s": 5, "e": 8, "p": 0.15},
                {"s": 8, "e": 10, "p": 0.2},
                {"s": 10, "e": -1, "p": 0.25},
            ],
            [{"s": 5, "e": -1, "p": 0.1}],
            [{"s": 8, "e": -1, "p": 0.05}],
            [],
        ]

        for bp in bps[rank]:
            if bp["s"] <= streak_if_win and (bp["e"] == -1 or streak_if_win <= bp["e"]):
                pct = bp["p"]
                break

        factor = 1 + pct * 2
        change = base * factor

    final = math.floor(change) if change >= 0 else round(change)
    return final


class ELOApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ELO Calculator")
        self.setMinimumSize(400, 600)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("ELO Calculator")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.elo_old_spin = self._add_spinbox(
            main_layout, "Your Current ELO:", 0, 99999
        )
        self.elo_opp_spin = self._add_spinbox(main_layout, "Opponent ELO:", 0, 99999)
        self.total_wins_spin = self._add_spinbox(main_layout, "Total Wins:", 0, 99999)
        self.total_matches_spin = self._add_spinbox(
            main_layout, "Total Matches:", 0, 99999
        )
        self.win_streak_spin = self._add_spinbox(main_layout, "Win Streak:", 0, 99999)

        result_container = QWidget()
        result_layout = QVBoxLayout(result_container)
        result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #2E7D32; 
            padding: 20px;
            background-color: #E8F5E9;
            border-radius: 10px;
        """)
        self.result_label.setAlignment(Qt.AlignCenter)
        result_layout.addWidget(self.result_label)
        main_layout.addWidget(result_container)

        radio_label = QLabel("Match Result")
        radio_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(radio_label)

        self.win_radio = QRadioButton("Win")
        self.loss_radio = QRadioButton("Loss")
        self.win_radio.setChecked(True)

        radio_btn_layout = QHBoxLayout()
        radio_btn_layout.addWidget(self.win_radio)
        radio_btn_layout.addWidget(self.loss_radio)
        radio_btn_layout.addStretch()
        main_layout.addLayout(radio_btn_layout)

        calc_btn = QPushButton("Calculate")
        calc_btn.setStyleSheet("""
            QPushButton {
                background-color: #2E7D32;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1B5E20;
            }
        """)
        calc_btn.setMinimumSize(QSize(0, 50))
        calc_btn.clicked.connect(self.calculate)
        main_layout.addWidget(calc_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        clear_btn.clicked.connect(self.clear)
        main_layout.addWidget(clear_btn)

        main_layout.addStretch()
        self.setLayout(main_layout)

        self.clear()

    def _add_spinbox(self, layout, label_text, min_val, max_val):
        label = QLabel(label_text)
        label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(label)
        spinner = QSpinBox()
        spinner.setRange(min_val, max_val)
        spinner.setStyleSheet("font-size: 16px; padding: 8px;")
        layout.addWidget(spinner)
        layout.addSpacing(10)
        return spinner

    def calculate(self):
        try:
            elo_old = self.elo_old_spin.value()
            elo_opp = self.elo_opp_spin.value()
            total_wins = self.total_wins_spin.value()
            total_matches = self.total_matches_spin.value()
            win_streak = self.win_streak_spin.value()
            is_win = self.win_radio.isChecked()

            change = predict_elo_change(
                my_elo=elo_old,
                opp_elo=elo_opp,
                is_win=is_win,
                streak_if_win=win_streak,
                total_wins_before=total_wins,
                matches_played_before=total_matches,
            )

            new_elo = elo_old + change
            sign = "+" if change >= 0 else ""
            self.result_label.setText(f"Change: {sign}{change}\nNew ELO: {new_elo}")
        except Exception as e:
            self.result_label.setText("Error")

    def clear(self):
        self.elo_old_spin.setValue(1100)
        self.elo_opp_spin.setValue(1100)
        self.total_wins_spin.setValue(25)
        self.total_matches_spin.setValue(30)
        self.win_streak_spin.setValue(0)
        self.win_radio.setChecked(True)
        self.result_label.setText("")


def main():
    app = QApplication()
    window = ELOApp()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
