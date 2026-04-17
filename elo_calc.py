import math
import argparse
import sys
from pprint import pprint


class Prediction:
    def __init__(self, elo_old, elo_opp, win, wins, total, streak):
        self.elo_old = elo_old
        self.elo_opponent = elo_opp
        self.match_win = win
        self.total_wins = wins
        self.total_matches = total
        self.win_streak = streak
        self.predicted_change = 0

    def __str__(self):
        return f"Elo: {self.elo_old} Opp: {self.elo_opponent} Win: {self.match_win} WinStreak: {self.win_streak}"

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(elo_old={self.elo_old!r},(elo_opponent={self.elo_opponent!r},(match_win={self.match_win!r},(total_wins={self.total_wins!r},(total_matches={self.total_matches!r},(win_streak={self.win_streak!r})"

    def to_json(self):
        return {
            "eloOld": self.elo_old,
            "eloOpponent": self.elo_opponent,
            "matchWin": self.match_win,
            "totalWins": self.total_wins,
            "totalMatches": self.total_matches,
            "winStreak": self.win_streak,
            "predictedChange": self.predicted_change,
        }


winstreak_types = [  # Same as JSON
    {"bps": []},  # 0
    {
        "bps": [
            {"s": 1, "e": 3, "p": 0.35},
            {"s": 3, "e": 5, "p": 0.45},
            {"s": 5, "e": 8, "p": 0.5},
            {"s": 8, "e": 10, "p": 0.75},
            {"s": 10, "e": -1, "p": 1},
        ]
    },  # 1
    {
        "bps": [
            {"s": 1, "e": 3, "p": 0.25},
            {"s": 3, "e": 5, "p": 0.4},
            {"s": 5, "e": 8, "p": 0.45},
            {"s": 8, "e": 10, "p": 0.6},
            {"s": 10, "e": -1, "p": 0.8},
        ]
    },  # 2
    {
        "bps": [
            {"s": 1, "e": 3, "p": 0.15},
            {"s": 3, "e": 5, "p": 0.25},
            {"s": 5, "e": 8, "p": 0.35},
            {"s": 8, "e": 10, "p": 0.55},
            {"s": 10, "e": -1, "p": 0.75},
        ]
    },  # 3
    {
        "bps": [
            {"s": 1, "e": 3, "p": 0.05},
            {"s": 3, "e": 5, "p": 0.1},
            {"s": 5, "e": 8, "p": 0.25},
            {"s": 8, "e": 10, "p": 0.4},
            {"s": 10, "e": -1, "p": 0.55},
        ]
    },  # 4 Gold
    {
        "bps": [
            {"s": 1, "e": 3, "p": 0.05},
            {"s": 3, "e": 5, "p": 0.1},
            {"s": 5, "e": 8, "p": 0.2},
            {"s": 8, "e": 10, "p": 0.3},
            {"s": 10, "e": -1, "p": 0.4},
        ]
    },  # 5 Plat
    {
        "bps": [
            {"s": 1, "e": 3, "p": 0.05},
            {"s": 3, "e": 5, "p": 0.1},
            {"s": 5, "e": 8, "p": 0.15},
            {"s": 8, "e": 10, "p": 0.2},
            {"s": 10, "e": -1, "p": 0.25},
        ]
    },  # 6
    {"bps": [{"s": 5, "e": -1, "p": 0.1}]},  # 7
    {"bps": [{"s": 8, "e": -1, "p": 0.05}]},  # 8
    {"bps": []},  # 9
]


def get_rank(elo):
    thresholds = [250, 500, 700, 900, 1100, 1300, 1500, 1700, 1800]
    rank = sum(1 for t in thresholds if elo >= t)
    return min(rank, 9)


def get_bonus_pct(rank, streak):
    bps = winstreak_types[rank]["bps"]
    for bp in bps:
        if bp["s"] <= streak <= (bp["e"] if bp["e"] != -1 else float("inf")):
            return bp["p"]
    return 0.0


def predict_elo_change(
    args,
    my_elo,
    opp_elo,
    is_win,
    streak_if_win,
    total_wins_before,
    matches_played_before,
):
    if opp_elo == -2:
        opp_elo = 950
        print("Unranked so probably wrong")
    # Phase detection (use PRE-match values!)
    if matches_played_before < 5:
        k = 120
        apply_bonus = False
        phase = "placement"
    elif matches_played_before < 24:
        k = 40
        apply_bonus = True
        phase = "post-placement"
    else:
        k = 24
        apply_bonus = True
        phase = "established"

    exp = 1 / (1 + 10 ** ((opp_elo - my_elo) / 400.0))
    base = k * ((1 if is_win else 0) - exp)

    change = base
    bonus_amount = 0
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

        pct = 0.0
        for bp in bps[rank]:
            if bp["s"] <= streak_if_win and (bp["e"] == -1 or streak_if_win <= bp["e"]):
                pct = bp["p"]
                break

        factor = 1 + pct * 2
        change = base * factor
        total_change = math.floor(base * factor)
        bonus_amount = total_change - math.floor(base)  # difference due to bonus
    final = math.floor(change) if change >= 0 else round(change)

    # Debug print (remove later)
    if args.debug:
        print(
            f"Phase: {phase}, K={k}, exp={exp:.4f}, base={base:.3f}, bonus_applied={apply_bonus}, pct={pct if 'pct' in locals() else 0}, factor={factor if 'factor' in locals() else 1}, base_change={base:.2f}, bonus_change={bonus_amount}, final={final}"
        )

    return final


def test_predict(args):
    print(Prediction(1096, 1200, True, 17, 23, 1))
    print(
        f"Change = {predict_elo_change(args, 1096, 1200, True, 17, 23, 1)}"
    )  # Win, streak=1: 28
    print(Prediction(1096, 1200, True, 17, 23, 4))  # Win, streak=4: 31
    print(
        f"Change = {predict_elo_change(args, 1096, 1200, True, 17, 23, 4)}"
    )  # Win, streak=4: 31
    print(Prediction(1096, 1200, False, 17, 23, 0))  # Loss: -14
    print(
        f"Change = {predict_elo_change(args, 1096, 1200, False, 17, 23, 0)}"
    )  # Loss: -14


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o", "--oldelo", dest="elo_old", type=int, default=-99, help="Your old elo"
    )
    parser.add_argument(
        "-r",
        "--opponentelo",
        dest="elo_opponent",
        type=int,
        default=-99,
        help="Your opponent elo",
    )
    parser.add_argument(
        "-w",
        "--win",
        dest="match_win",
        type=int,
        choices=[0, 1],
        default=-99,
        help="Your old elo",
    )
    parser.add_argument(
        "-tw",
        "--totalwins",
        dest="total_wins",
        type=int,
        default=-99,
        help="Your total wins",
    )
    parser.add_argument(
        "-tm",
        "--totalmatches",
        dest="total_matches",
        type=int,
        default=-99,
        help="Your total matches",
    )
    parser.add_argument(
        "-ws",
        "--winstreak",
        dest="win_streak",
        type=int,
        default=-99,
        help="Your current winstreak",
    )
    parser.add_argument(
        "--dryrun",
        dest="dry_run",
        default=False,
        action="store_true",
        help="Run test prediction data (skips actual calcs)",
    )
    parser.add_argument(
        "--debug", dest="debug", default=False, action="store_true", help="Enable debug"
    )
    args = parser.parse_args()

    if args.dry_run:
        test_predict(args)
        return 0

    if (
        args.elo_old == -99
        or args.elo_opponent == -99
        or args.match_win == -99
        or args.total_wins == -99
        or args.total_matches == -99
        or args.win_streak == -99
    ):
        sys.exit("Fill out the args bro")

    x = Prediction(
        elo_old=args.elo_old,
        elo_opp=args.elo_opponent,
        win=True if args.match_win else False,
        streak=args.win_streak,
        wins=args.total_wins,
        total=args.total_matches,
    )

    change = predict_elo_change(
        args=args,
        my_elo=x.elo_old,
        opp_elo=x.elo_opponent,
        is_win=True if x.match_win else False,
        streak_if_win=x.win_streak,
        total_wins_before=x.total_wins,
        matches_played_before=x.total_matches,
    )
    x.predicted_change = change

    if args.debug:
        # print("# ranked_game_number, elo_rank_old, opponent_elo, match_win, win_streak_value, total_wins, predicted_change")
        # print(f"'{args.total_matches}','{args.elo_old}', '{args.elo_opponent}', '{1 if args.match_win else 0}', '{args.win_streak}', '{args.total_wins}', '{predict_elo_change(args, x.elo_old, x.elo_opponent, True if x.match_win else False, x.total_wins, x.total_matches, x.win_streak)}'")
        pprint(x.to_json())
        print(
            f"""predict_elo_change({args.elo_old}, {args.elo_opponent}, {True if args.match_win else False}, {args.win_streak}, {args.total_wins}, {args.total_matches})"""
        )
    print(x)
    print(f"Change = {change}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
