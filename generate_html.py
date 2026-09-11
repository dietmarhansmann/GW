import openpyxl
import json
import datetime
import random
random.seed(42)
from collections import defaultdict

wb = openpyxl.load_workbook('Tennis_Spielplan_Google_Drive_Native_Fix.xlsx', data_only=True)
sheet = wb['Gesamt-Spielplan']

global_pair_counts = defaultdict(int)
global_time_counts = defaultdict(lambda: {19: 0, 20: 0, 21: 0})

def get_matchday_score(test_slots, singles_keys, doppel_keys):
    score = 0
    for i in range(0, len(singles_keys), 2):
        p1 = test_slots[singles_keys[i]]
        p2 = test_slots[singles_keys[i+1]]
        if p1 and p2:
            score += global_pair_counts[tuple(sorted([p1, p2]))]

    t1 = [test_slots['d_t1_1'], test_slots['d_t1_2']]
    t2 = [test_slots['d_t2_1'], test_slots['d_t2_2']]
    t1 = [p for p in t1 if p]
    t2 = [p for p in t2 if p]
    for pa in t1:
        for pb in t2:
            score += global_pair_counts[tuple(sorted([pa, pb]))]
    for pair in [tuple(sorted(t1)), tuple(sorted(t2))]:
        if len(pair) == 2:
            score += global_pair_counts[pair]

    # Time slot fairness penalty (balance 19:00, 20:00, 21:00 across season)
    slot_hours = [
        ('p1_1', 19), ('p1_2', 19),
        ('p2_1', 20), ('p2_2', 20),
        ('p3_1', 21), ('p3_2', 21)
    ]
    for sk, hour in slot_hours:
        p = test_slots.get(sk)
        if p:
            score += global_time_counts[p][hour] * 3.0

    return score

def register_matchday_pairs(test_slots, singles_keys, doppel_keys):
    for i in range(0, len(singles_keys), 2):
        p1 = test_slots[singles_keys[i]]
        p2 = test_slots[singles_keys[i+1]]
        if p1 and p2:
            global_pair_counts[tuple(sorted([p1, p2]))] += 1
    t1 = [test_slots['d_t1_1'], test_slots['d_t1_2']]
    t2 = [test_slots['d_t2_1'], test_slots['d_t2_2']]
    t1 = [p for p in t1 if p]
    t2 = [p for p in t2 if p]
    for pa in t1:
        for pb in t2:
            global_pair_counts[tuple(sorted([pa, pb]))] += 1
    for pair in [tuple(sorted(t1)), tuple(sorted(t2))]:
        if len(pair) == 2:
            global_pair_counts[pair] += 1

    slot_hours = [
        ('p1_1', 19), ('p1_2', 19),
        ('p2_1', 20), ('p2_2', 20),
        ('p3_1', 21), ('p3_2', 21)
    ]
    for sk, hour in slot_hours:
        p = test_slots.get(sk)
        if p:
            global_time_counts[p][hour] += 1

# =========================================================================
# 📋 PRO-SPIELER REGELWERK (Verschachtelt unter "rules")
# Diese Regeln werden aktiv auf die dynamische Generierung der Tabelle angewandt.
# =========================================================================
PLAYER_RULES = {
    "Mönning": {
        "rules": [
            {
                "id": "slot_preference_monning",
                "target": "doppel_pref",
                "ratio": 0.0,
                "description": "Spielt ausschließlich Einzel (0% Doppel)."
            }
        ]
    },
    "Hansmann": {
        "rules": [
            {
                "id": "slot_preference_hansmann",
                "target": "doppel_pref",
                "ratio": 0.3,
                "description": "Möchte ca. 70% Einzel spielen (30% Doppel)."
            },
            {
                "id": "blackout_spieltage",
                "spieltage": [9],
                "description": "Kann an Spieltag 9 nicht teilnehmen."
            }
        ]
    },
    "Dedores": {
        "rules": [
            {
                "id": "slot_preference_dedores",
                "target": "doppel_pref",
                "ratio": 0.0,
                "description": "Spielt ausschließlich Einzel (0% Doppel)."
            },
            {
                "id": "blackout_spieltage",
                "spieltage": [3, 4, 8, 13],
                "description": "Kann an folgenden Tagen nicht teilnehmen: 20.10.26 (#3), 27.10.26 (#4), 24.11.26 (#8), 29.12.26 (#13)."
            }
        ]
    },
    "Hinz": {
        "rules": [
            {
                "id": "slot_preference_hinz",
                "target": "doppel_pref",
                "ratio": 0.5,
                "description": "Möchte ca. 50% Doppel und 50% Einzel spielen."
            },
            {
                "id": "blackout_spieltage",
                "spieltage": list(range(1, 14)) + [30],
                "description": "Kann vor dem 01.01.2027 (Spieltag 1–13) und am 27.04.2027 (Spieltag 30) nicht spielen."
            }
        ]
    },
    "Beumer": {
        "rules": [
            {
                "id": "slot_preference_beumer",
                "target": "doppel_pref",
                "ratio": 0.5,
                "description": "Möchte ca. 50% Doppel und 50% Einzel spielen."
            }
        ]
    },
    "Prodehl": {
        "rules": [
            {
                "id": "slot_preference_prodehl",
                "target": "doppel_pref",
                "ratio": 0.6,
                "description": "Möchte ca. 60% Doppel spielen."
            },
            {
                "id": "blackout_spieltage",
                "spieltage": [5, 6],
                "description": "Ist in den ersten beiden Wochen im November im Urlaub (Spieltag 5 & 6)."
            }
        ]
    },
    "Marschollek": {
        "rules": [
            {
                "id": "slot_preference_marschollek",
                "target": "doppel_pref",
                "ratio": 0.9,
                "description": "Möchte ca. 90% Doppel spielen."
            },
            {
                "id": "blackout_spieltage",
                "spieltage": [2, 3, 5, 10, 16, 24],
                "description": "Kann an folgenden Tagen nicht teilnehmen: 13.10.26 (#2), 20.10.26 (#3), 03.11.26 (#5), 08.12.26 (#10), 19.01.27 (#16), 16.03.27 (#24)."
            }
        ]
    },
    "Kissner": {
        "rules": [
            {
                "id": "slot_preference_kissner",
                "target": "doppel_pref",
                "ratio": 0.0,
                "description": "Spielt nur Einzel (0% Doppel)."
            }
        ]
    },
    "Knust": {
        "rules": [
            {
                "id": "info_knust",
                "description": "Nimmt erst 2027 teil."
            }
        ]
    },
    "Heyn": {
        "rules": [
            {
                "id": "slot_preference_heyn",
                "target": "doppel_pref",
                "ratio": 0.5,
                "description": "Möchte ca. 50% Doppel und 50% Einzel spielen."
            },
            {
                "id": "blackout_spieltage",
                "spieltage": [2, 4, 5, 6, 10, 13],
                "description": "Kann an folgenden Tagen nicht teilnehmen: 13.10.26 (#2), 27.10.26 (#4), 03.11.26 (#5), 10.11.26 (#6), 08.12.26 (#10), 29.12.26 (#13)."
            }
        ]
    },
    "Trojanski": {
        "rules": [
            {
                "id": "max_frequency_gap",
                "min_gap": 2,
                "description": "2-Wochen-Rhythmus (mindestens 1 Spieltag Pause dazwischen)."
            },
            {
                "id": "slot_preference_trojanski",
                "target": "doppel_pref",
                "ratio": 0.0,
                "description": "Spielt ausschließlich Einzel (0% Doppel)."
            },
            {
                "id": "blackout_spieltage",
                "spieltage": [2, 5, 10],
                "description": "Kann an folgenden Tagen nicht teilnehmen: 13.10.26 (#2), 03.11.26 (#5), 08.12.26 (#10)."
            }
        ]
    },
    "Kuhlhoff": {
        "rules": [
            {
                "id": "blackout_spieltage",
                "spieltage": [6, 7, 8, 10, 13],
                "description": "Kann an folgenden Tagen nicht teilnehmen: 10.11.26 (#6), 17.11.26 (#7), 24.11.26 (#8), 08.12.26 (#10), 29.12.26 (#13)."
            },
            {
                "id": "slot_preference_kuhlhoff",
                "target": "doppel_pref",
                "ratio": 0.0,
                "description": "Spielt ausschließlich Einzel (0% Doppel)."
            }
        ]
    },
    "van de Loo": {
        "rules": [
            {
                "id": "max_frequency_gap",
                "min_gap": 4,
                "description": "Einmal im Monat (mindestens 3 Spieltage Pause dazwischen)."
            },
            {
                "id": "slot_preference_vandeloo",
                "target": "doppel_pref",
                "ratio": 0.0,
                "description": "Spielt ausschließlich Einzel (0% Doppel)."
            }
        ]
    },
    "Wojtanowitsch": {
        "rules": [
            {
                "id": "slot_preference_wojtanowitsch",
                "target": "doppel_pref",
                "ratio": 0.0,
                "description": "Spielt ausschließlich Einzel (0% Doppel)."
            }
        ]
    }
}

def can_play_slot(player, stype):
    for rule in PLAYER_RULES.get(player, {}).get("rules", []):
        r_target = rule.get("target")
        r_id = rule.get("id", "")
        r_ratio = rule.get("ratio", 0.8)
        if (r_target == "doppel_pref" or r_id.startswith("slot_preference")):
            if stype == "singles" and r_ratio >= 1.0:
                return False
            if stype == "doppel" and r_ratio <= 0.0:
                return False
    return True


# Get all unique players from Excel as a substitution pool
all_excel_players = set()
raw_rows = [r for r in list(sheet.iter_rows(values_only=True))[6:] if r[0] is not None and int(r[0]) <= 13]
for r in raw_rows:
    if r[0] is not None:
        for col in [2, 4, 6, 8, 10, 12, 14, 15, 17, 18]:
            val = str(r[col] or '').strip()
            if val == 'Wojtanowtisch':
                val = 'Wojtanowitsch'
            if val and val != 'vs':
                all_excel_players.add(val)

all_excel_players.add("Kissner")
if "Höttinger" in all_excel_players:
    all_excel_players.remove("Höttinger")
player_pool = sorted(list(all_excel_players))

matches = []
players_set = set()

# State tracking for rules across matchdays
player_last_played = {p: -99 for p in player_pool}
player_total_games = {p: 0 for p in player_pool}
player_doppel_games = {p: 0 for p in player_pool}

for r in raw_rows:
    if r[0] is not None:
        try:
            spieltag = int(r[0])
        except:
            continue
        date_val = str(r[1])[:10] if r[1] else ''

        time_p1 = "19:00"
        time_p2 = "20:00"
        time_p3 = "21:00"
        time_doppel = "20:30"

        is_doppel_week = (spieltag % 2 == 1)
        if is_doppel_week:
            slots = {
                'p1_1': str(r[2] or '').strip(),
                'p1_2': str(r[4] or '').strip(),
                'p2_1': str(r[6] or '').strip(),
                'p2_2': str(r[8] or '').strip(),
                'p3_1': str(r[10] or '').strip(),
                'p3_2': str(r[12] or '').strip(),
                'd_t1_1': str(r[14] or '').strip(),
                'd_t1_2': str(r[15] or '').strip(),
                'd_t2_1': str(r[17] or '').strip(),
                'd_t2_2': str(r[18] or '').strip(),
            }
            slot_keys = ['p1_1', 'p1_2', 'p2_1', 'p2_2', 'p3_1', 'p3_2', 'd_t1_1', 'd_t1_2', 'd_t2_1', 'd_t2_2']
            singles_keys = ['p1_1', 'p1_2', 'p2_1', 'p2_2', 'p3_1', 'p3_2']
            doppel_keys = ['d_t1_1', 'd_t1_2', 'd_t2_1', 'd_t2_2']
        else:
            slots = {
                'p1_1': str(r[2] or '').strip(),
                'p1_2': str(r[4] or '').strip(),
                'p2_1': str(r[6] or '').strip(),
                'p2_2': str(r[8] or '').strip(),
                'p3_1': str(r[10] or '').strip(),
                'p3_2': str(r[12] or '').strip(),
                'd_t1_1': str(r[14] or '').strip(),
                'd_t1_2': '',
                'd_t2_1': str(r[17] or '').strip(),
                'd_t2_2': '',
            }
            slot_keys = ['p1_1', 'p1_2', 'p2_1', 'p2_2', 'p3_1', 'p3_2', 'd_t1_1', 'd_t2_1']
            singles_keys = ['p1_1', 'p1_2', 'p2_1', 'p2_2', 'p3_1', 'p3_2', 'd_t1_1', 'd_t2_1']
            doppel_keys = []

        # Clean 'vs' entries and normalize spelling
        for k in slots:
            if slots[k] == 'Wojtanowtisch':
                slots[k] = 'Wojtanowitsch'
            if slots[k] == 'vs' or slots[k] == 'Knust' or slots[k] == 'Höttinger':
                slots[k] = ''

        if spieltag == 13 or date_val == '2026-12-29':
            status = 'Reserviert für alle'
            is_dw = (spieltag % 2 == 1)
            matches.append({
                'spieltag': spieltag,
                'date': date_val,
                'court2_type': 'doppel' if is_dw else 'singles',
                'p1': {'p1': '', 'p2': '', 'time': time_p1},
                'p2': {'p1': '', 'p2': '', 'time': time_p2},
                'p3': {'p1': '', 'p2': '', 'time': time_p3},
                'doppel': {
                    'team1': ['', ''],
                    'team2': ['', ''],
                    'time': time_doppel
                } if is_dw else {
                    'p1': '', 'p2': '', 'time': time_doppel
                },
                'status': status
            })
            continue

        slot_keys = ['p1_1', 'p1_2', 'p2_1', 'p2_2', 'p3_1', 'p3_2', 'd_t1_1', 'd_t1_2', 'd_t2_1', 'd_t2_2']
        singles_keys = ['p1_1', 'p1_2', 'p2_1', 'p2_2', 'p3_1', 'p3_2']

        def get_substitute(occupied_today, exclude_set=None, slot_type='any'):
            if exclude_set is None:
                exclude_set = set()

            def check_can_play(p):

                # Check slot type restrictions
                if slot_type == 'singles':
                    for rule in PLAYER_RULES.get(p, {}).get("rules", []):
                        if (rule.get("target") == "doppel_pref" or rule.get("id", "").startswith("slot_preference")) and rule.get("ratio", 0.8) >= 1.0:
                            return False
                elif slot_type == 'doppel':
                    for rule in PLAYER_RULES.get(p, {}).get("rules", []):
                        if (rule.get("target") == "doppel_pref" or rule.get("id", "").startswith("slot_preference")) and rule.get("ratio", 0.8) <= 0.0:
                            return False

                for rule in PLAYER_RULES.get(p, {}).get("rules", []):
                    rule_id = rule.get("id")
                    if rule_id == "blackout_spieltage":
                        if spieltag in rule.get("spieltage", []):
                            return False
                    elif rule_id in ["tshirt_size_frequency", "max_frequency_gap"]:
                        size = rule.get("size", "L").upper()
                        size_gaps = {"S": 4, "M": 3, "L": 2, "XL": 0}
                        min_gap = rule.get("min_gap", size_gaps.get(size, 2))
                        last_st = player_last_played.get(p, -99)
                        if spieltag - last_st < min_gap:
                            return False
                return True

            for p in player_pool:
                if p == "Knust":
                    continue
                if p not in occupied_today and p not in exclude_set:
                    if check_can_play(p):
                        return p

            best_p = None
            max_gap_seen = -1
            for p in player_pool:
                if p == "Knust":
                    continue
                if p not in occupied_today and p not in exclude_set:
                    if check_can_play(p):
                        last_st = player_last_played.get(p, -99)
                        gap = spieltag - last_st
                        if gap > max_gap_seen:
                            max_gap_seen = gap
                            best_p = p
            if best_p:
                return best_p

            for p in player_pool:
                if p == "Knust":
                    continue
                if p not in occupied_today and p not in exclude_set:
                    return p
            return player_pool[0]

        occupied_today = set()
        resting_today = set()

        doppel_keys = ['d_t1_1', 'd_t1_2', 'd_t2_1', 'd_t2_2']
        # Robust Pre-enforce strict ratios (0% doppel / 100% doppel)
        def can_play_slot(player, stype):
            for rule in PLAYER_RULES.get(player, {}).get("rules", []):
                r_target = rule.get("target")
                r_id = rule.get("id", "")
                r_ratio = rule.get("ratio", 0.8)
                if (r_target == "doppel_pref" or r_id.startswith("slot_preference")):
                    if stype == "singles" and r_ratio >= 1.0:
                        return False
                    if stype == "doppel" and r_ratio <= 0.0:
                        return False
            return True

        for dk in doppel_keys:
            p = slots[dk]
            if p and not can_play_slot(p, "doppel"):
                slots[dk] = ''
                swapped = False
                for sk in singles_keys:
                    sp = slots[sk]
                    if sp and can_play_slot(sp, "doppel"):
                        slots[sk] = p
                        slots[dk] = sp
                        swapped = True
                        break
                if not swapped:
                    current_occ = set(slots.values())
                    sub = get_substitute(current_occ, slot_type="doppel")
                    slots[dk] = sub

        for sk in singles_keys:
            p = slots[sk]
            if p and not can_play_slot(p, "singles"):
                slots[sk] = ''
                swapped = False
                for dk in doppel_keys:
                    dp = slots[dk]
                    if dp and can_play_slot(dp, "singles"):
                        slots[dk] = p
                        slots[sk] = dp
                        swapped = True
                        break
                if not swapped:
                    current_occ = set(slots.values())
                    sub = get_substitute(current_occ, slot_type="singles")
                    slots[sk] = sub

        # 1. Apply Player Rules dynamically from nested structure
        for player, player_data in PLAYER_RULES.items():
            rules_list = player_data.get("rules", [])
            for rule in rules_list:
                rule_id = rule.get("id")

                # Rule: Blackout Spieltage (e.g. Hansmann November)
                if rule_id == "blackout_spieltage":
                    if spieltag in rule.get("spieltage", []):
                        for k in slot_keys:
                            if slots[k] == player:
                                stype = 'singles' if k in singles_keys else 'doppel'
                                sub = get_substitute(set(slots.values()).union(occupied_today), exclude_set={player}, slot_type=stype)
                                slots[k] = sub
                        resting_today.add(player)

                # Rule: Max Frequency Gap (e.g. Hinz every 2 weeks)
                elif rule_id == "max_frequency_gap":
                    min_gap = rule.get("min_gap", 2)
                    last_spieltag = player_last_played.get(player, -99)
                    if spieltag - last_spieltag < min_gap:
                        for k in slot_keys:
                            if slots[k] == player:
                                stype = 'singles' if k in singles_keys else 'doppel'
                                sub = get_substitute(set(slots.values()).union(occupied_today), exclude_set={player}, slot_type=stype)
                                slots[k] = sub
                        resting_today.add(player)
                    else:
                        player_present = any(slots[k] == player for k in slot_keys)
                        if player_present:
                            player_last_played[player] = spieltag

                # Rule: T-Shirt Size Frequency (S, M, L, XL)
                elif rule_id == "tshirt_size_frequency":
                    size = rule.get("size", "L").upper()
                    size_gaps = {"S": 4, "M": 3, "L": 2, "XL": 0}
                    min_gap = rule.get("min_gap", size_gaps.get(size, 2))
                    last_spieltag = player_last_played.get(player, -99)
                    if spieltag - last_spieltag < min_gap:
                        for k in slot_keys:
                            if slots[k] == player:
                                stype = 'singles' if k in singles_keys else 'doppel'
                                sub = get_substitute(set(slots.values()).union(occupied_today), exclude_set={player}, slot_type=stype)
                                slots[k] = sub
                        resting_today.add(player)
                    else:
                        player_present = any(slots[k] == player for k in slot_keys)
                        if player_present:
                            player_last_played[player] = spieltag
                # Rule: Slot Preference (Doppel vs Singles ratio based on actual games played)
                elif rule_id and (rule_id.startswith("slot_preference") or rule.get("target") == "doppel_pref"):
                    if player in resting_today:
                        continue
                    ratio = rule.get("ratio", 0.8) # e.g. 0.8 for Heyn, 0.6 for Hinz
                    in_singles = any(slots[k] == player for k in singles_keys)
                    in_doppel = any(slots[k] == player for k in ['d_t1_1', 'd_t1_2', 'd_t2_1', 'd_t2_2'])

                    if in_singles or in_doppel:
                        player_total_games[player] = player_total_games.get(player, 0) + 1
                        current_doppel = player_doppel_games.get(player, 0)
                        total_g = player_total_games[player]

                        if ratio >= 1.0:
                            should_be_doppel = True
                        elif ratio <= 0.0:
                            should_be_doppel = False
                        else:
                            should_be_doppel = (current_doppel / total_g) < ratio

                        doppel_keys = ['d_t1_1', 'd_t1_2', 'd_t2_1', 'd_t2_2']

                        if should_be_doppel and in_singles:
                            moved = False
                            for sk in singles_keys:
                                if slots[sk] == player:
                                    for dk in doppel_keys:
                                        dp = slots[dk]
                                        if dp and dp != player:
                                            slots[sk] = dp
                                            slots[dk] = player
                                            moved = True
                                            break
                                    if not moved:
                                        for dk in doppel_keys:
                                            if not slots[dk]:
                                                slots[sk] = ''
                                                slots[dk] = player
                                                moved = True
                                                break
                                    if not moved:
                                        # Force direct swap with first doppel player
                                        dk = doppel_keys[0]
                                        dp = slots[dk]
                                        slots[sk] = dp
                                        slots[dk] = player
                                        moved = True
                        elif not should_be_doppel and in_doppel:
                            moved = False
                            for dk in doppel_keys:
                                if slots[dk] == player:
                                    for sk in singles_keys:
                                        sp = slots[sk]
                                        if sp and sp != player:
                                            slots[dk] = sp
                                            slots[sk] = player
                                            moved = True
                                            break
                                    if not moved:
                                        for sk in singles_keys:
                                            if not slots[sk]:
                                                slots[dk] = ''
                                                slots[sk] = player
                                                moved = True
                                                break
                                    if not moved:
                                        # Force direct swap with first singles player
                                        sk = singles_keys[0]
                                        sp = slots[sk]
                                        slots[dk] = sp
                                        slots[sk] = player
                                        moved = True

                        final_in_doppel = any(slots[k] == player for k in doppel_keys)
                        if final_in_doppel:
                            player_doppel_games[player] = current_doppel + 1
                        else:
                            player_doppel_games[player] = current_doppel

        # Enforce strict 100% or 0% ratios if configured
        print(f"DEBUG Stg {spieltag} resting_today:", resting_today)
        for player, player_data in PLAYER_RULES.items():
            if player in resting_today:
                continue
            for rule in player_data.get("rules", []):
                if rule.get("target") == "doppel_pref" or rule.get("id", "").startswith("slot_preference"):
                    ratio = rule.get("ratio", 0.8)
                    if ratio >= 1.0:
                        for sk in singles_keys:
                            if slots[sk] == player:
                                slots[sk] = ''
                        if not any(slots[dk] == player for dk in doppel_keys):
                            placed = False
                            for dk in doppel_keys:
                                if not slots[dk]:
                                    slots[dk] = player
                                    placed = True
                                    break
                            if not placed and doppel_keys:
                                slots[doppel_keys[0]] = player
                    elif ratio <= 0.0:
                        for dk in doppel_keys:
                            if slots[dk] == player:
                                slots[dk] = ''
                        if not any(slots[sk] == player for sk in singles_keys):
                            placed = False
                            for sk in singles_keys:
                                if not slots[sk]:
                                    slots[sk] = player
                                    placed = True
                                    break
                            if not placed and singles_keys:
                                slots[singles_keys[0]] = player

        # Build occupied_today from current assignments
        occupied_today = set()
        for k in slot_keys:
            p = slots[k]
            if p and p in player_pool:
                if p in occupied_today:
                    # Double booking detected, resolve with substitute
                    stype = 'singles' if k in singles_keys else 'doppel'
                    sub = get_substitute(occupied_today, slot_type=stype)
                    slots[k] = sub
                    occupied_today.add(sub)
                else:
                    occupied_today.add(p)

        # Fill any remaining empty slots (ensure singles has 2 players, doppel has 4 players)
        for k in slot_keys:
            if not slots[k]:
                stype = 'singles' if k in singles_keys else 'doppel'
                sub = get_substitute(occupied_today, slot_type=stype)
                slots[k] = sub
                occupied_today.add(sub)

        # Optimize pairings to minimize duplicate matchups across the season
        current_players = [slots[k] for k in slot_keys if slots[k]]
        best_slots = dict(slots)
        best_score = float('inf')

        def respects_constraints(test_slots):
            for p in current_players:
                for rule in PLAYER_RULES.get(p, {}).get("rules", []):
                    r_target = rule.get("target")
                    r_id = rule.get("id", "")
                    r_ratio = rule.get("ratio", 0.8)
                    if (r_target == "doppel_pref" or r_id.startswith("slot_preference")) and r_ratio >= 1.0:
                        if any(test_slots[sk] == p for sk in singles_keys):
                            return False
                    elif (r_target == "doppel_pref" or r_id.startswith("slot_preference")) and r_ratio <= 0.0:
                        if any(test_slots[dk] == p for dk in doppel_keys):
                            return False
            return True

        for _ in range(300):
            shuffled = list(current_players)
            random.shuffle(shuffled)
            test_slots = {k: shuffled[idx] for idx, k in enumerate(slot_keys)}
            if respects_constraints(test_slots):
                score = get_matchday_score(test_slots, singles_keys, doppel_keys)
                if score < best_score:
                    best_score = score
                    best_slots = test_slots

        slots = best_slots
        register_matchday_pairs(slots, singles_keys, doppel_keys)

        # Track last played for all participating players today
        for k in slot_keys:
            p = slots[k]
            if p and p in player_pool:
                player_last_played[p] = spieltag

        # Collect active players for legend
        for k in slot_keys:
            if slots[k]:
                players_set.add(slots[k])

        status = str(r[19] or 'Geplant')
        if spieltag == 13 or date_val == '2026-12-29':
            status = 'Reserviert für alle'

        matches.append({
            'spieltag': spieltag,
            'date': date_val,
            'court2_type': 'doppel' if is_doppel_week else 'singles',
            'p1': {'p1': slots['p1_1'], 'p2': slots['p1_2'], 'time': time_p1},
            'p2': {'p1': slots['p2_1'], 'p2': slots['p2_2'], 'time': time_p2},
            'p3': {'p1': slots['p3_1'], 'p2': slots['p3_2'], 'time': time_p3},
            'doppel': {
                'team1': [slots['d_t1_1'], slots['d_t1_2']],
                'team2': [slots['d_t2_1'], slots['d_t2_2']],
                'time': time_doppel
            } if is_doppel_week else {
                'p1': slots['d_t1_1'],
                'p2': slots['d_t2_1'],
                'time': time_doppel
            },
            'status': status
        })

players = sorted(list(players_set.union(PLAYER_RULES.keys()).union(player_pool)))

# Post-pass ratio balancing for players with ratio rules
for player, player_data in PLAYER_RULES.items():
    for rule in player_data.get("rules", []):
        if rule.get("target") == "doppel_pref" or rule.get("id", "").startswith("slot_preference"):
            ratio = rule.get("ratio", 0.8)
            if ratio >= 1.0 or ratio <= 0.0:
                continue

            player_matches = []
            for m in matches:
                s_list = [m["p1"]["p1"], m["p1"]["p2"], m["p2"]["p1"], m["p2"]["p2"], m["p3"]["p1"], m["p3"]["p2"]]
                if m.get("court2_type") == 'singles':
                    s_list.extend([m["doppel"]["p1"], m["doppel"]["p2"]])
                    d_list = []
                else:
                    d_list = m["doppel"]["team1"] + m["doppel"]["team2"]
                if player in s_list:
                    player_matches.append((m, 'singles'))
                elif player in d_list:
                    player_matches.append((m, 'doppel'))

            total_p = len(player_matches)
            if total_p == 0:
                continue

            target_doppel = int(round(total_p * ratio))
            current_doppel_matches = [item for item in player_matches if item[1] == 'doppel']
            current_singles_matches = [item for item in player_matches if item[1] == 'singles']

            diff = len(current_doppel_matches) - target_doppel
            if diff > 0:
                to_convert = current_doppel_matches[:diff]
                for m, _ in to_convert:
                    d_slot = None
                    if m.get('court2_type') != 'singles':
                        for t, idx in [('team1', 0), ('team1', 1), ('team2', 0), ('team2', 1)]:
                            if m["doppel"][t][idx] == player:
                                d_slot = (t, idx)
                                break
                    s_slot = None
                    for group, s_key in [('p1', 'p1'), ('p1', 'p2'), ('p2', 'p1'), ('p2', 'p2'), ('p3', 'p1'), ('p3', 'p2')]:
                        other = m[group][s_key]
                        if other and other != player and can_play_slot(other, "doppel"):
                            s_slot = (group, s_key)
                            break
                    if d_slot and s_slot:
                        t, idx = d_slot
                        group, s_key = s_slot
                        other = m[group][s_key]
                        m[group][s_key] = player
                        m["doppel"][t][idx] = other
            elif diff < 0:
                to_convert = current_singles_matches[:abs(diff)]
                for m, _ in to_convert:
                    s_slot = None
                    for group, s_key in [('p1', 'p1'), ('p1', 'p2'), ('p2', 'p1'), ('p2', 'p2'), ('p3', 'p1'), ('p3', 'p2')]:
                        if m[group][s_key] == player:
                            s_slot = (group, s_key)
                            break
                    d_slot = None
                    if m.get('court2_type') != 'singles':
                        for t, idx in [('team1', 0), ('team1', 1), ('team2', 0), ('team2', 1)]:
                            other = m["doppel"][t][idx]
                            if other and other != player and can_play_slot(other, 'singles'):
                                d_slot = (t, idx)
                                break
                    if s_slot and d_slot:
                        group, s_key = s_slot
                        t, idx = d_slot
                        other = m["doppel"][t][idx]
                        m["doppel"][t][idx] = player
                        m[group][s_key] = other

# =========================================================================
# 🔍 AUTOMATED RULE VERIFICATION
# =========================================================================
print("\n" + "="*50)
print("🔍 AUTOMATE REGEL-VALIDIERUNG")
print("="*50)

errors_found = 0

for m in matches:
    stg = m["spieltag"]
    singles = [m["p1"]["p1"], m["p1"]["p2"], m["p2"]["p1"], m["p2"]["p2"], m["p3"]["p1"], m["p3"]["p2"]]
    if m.get("court2_type") == 'singles':
        singles.extend([m["doppel"]["p1"], m["doppel"]["p2"]])
        doppel = []
    else:
        doppel = m["doppel"]["team1"] + m["doppel"]["team2"]
    all_today = singles + doppel

    # 1. Hansmann blackout check (dynamic)
    for rule in PLAYER_RULES.get("Hansmann", {}).get("rules", []):
        if rule.get("id") == "blackout_spieltage":
            if stg in rule.get("spieltage", []) and "Hansmann" in all_today:
                print(f"❌ Regelverstoß [Hansmann Blackout]: Hansmann spielt an Spieltag {stg}!")
                errors_found += 1

    # Hinz blackout check (dynamic)
    for rule in PLAYER_RULES.get("Hinz", {}).get("rules", []):
        if rule.get("id") == "blackout_spieltage":
            if stg in rule.get("spieltage", []) and "Hinz" in all_today:
                print(f"❌ Regelverstoß [Hinz Blackout]: Hinz spielt an Spieltag {stg}!")
                errors_found += 1

    # Prodehl blackout check (dynamic)
    for rule in PLAYER_RULES.get("Prodehl", {}).get("rules", []):
        if rule.get("id") == "blackout_spieltage":
            if stg in rule.get("spieltage", []) and "Prodehl" in all_today:
                print(f"❌ Regelverstoß [Prodehl Blackout]: Prodehl spielt an Spieltag {stg}!")
                errors_found += 1

    # 3. Double booking check per matchday
    seen_today = set()
    for p in all_today:
        if p and p != 'vs':
            if p in seen_today:
                print(f"❌ Regelverstoß [Doppelbelegung]: Spieler '{p}' spielt mehrfach am Spieltag {stg}!")
                errors_found += 1
            seen_today.add(p)

    # 4. Ratio constraint check (0% doppel or 100% doppel)
    for p in all_today:
        if p and p in PLAYER_RULES:
            for rule in PLAYER_RULES[p].get("rules", []):
                if rule.get("target") == "doppel_pref" or rule.get("id", "").startswith("slot_preference"):
                    ratio = rule.get("ratio", 0.8)
                    if ratio <= 0.0 and p in doppel:
                        print(f"❌ Regelverstoß [Nur-Einzel]: Spieler '{p}' spielt Doppel an Spieltag {stg}!")
                        errors_found += 1
                    elif ratio >= 1.0 and p in singles:
                        print(f"❌ Regelverstoß [Nur-Doppel]: Spieler '{p}' spielt Einzel an Spieltag {stg}!")
                        errors_found += 1

if errors_found == 0:
    print("✅ Alle   wurden erfolgreich validiert! Keine Fehler gefunden.")
else:
    print(f"⚠️ {errors_found} Regelverstöße festgestellt!")
    import sys
    sys.exit(1)

# Prepare rules grouped by player for frontend display from nested structure
frontend_rules_by_player = {}
for p, player_data in PLAYER_RULES.items():
    rules_list = [r.get('description', '') for r in player_data.get("rules", [])]
    if rules_list:
        frontend_rules_by_player[p] = rules_list

# Calculate player statistics (singles vs doubles)
player_stats = {}
for p in players:
    s_count = 0
    d_count = 0
    for m in matches:
        s_list = [m["p1"]["p1"], m["p1"]["p2"], m["p2"]["p1"], m["p2"]["p2"], m["p3"]["p1"], m["p3"]["p2"]]
        if m.get("court2_type") == "singles":
            s_list.extend([m["doppel"]["p1"], m["doppel"]["p2"]])
            d_list = []
        else:
            d_list = m["doppel"]["team1"] + m["doppel"]["team2"]
        s_count += s_list.count(p)
        d_count += d_list.count(p)
    total = s_count + d_count
    ratio = int(round((d_count / total * 100))) if total > 0 else 0
    kosten = (s_count * 0.5) + (d_count * (1.5 / 4.0))
    player_stats[p] = {
        'singles': s_count,
        'doppel': d_count,
        'total': total,
        'ratio': ratio,
        'kosten': round(kosten, 2)
    }

print(f'Generated {len(matches)} matches with nested per-player rules engine.')

html_template = """<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tennis-Spielplan Wintersaison 2026/2027</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f3f4f6; }
    </style>
</head>
<body class="bg-gray-50 text-gray-800 antialiased min-h-screen p-2 md:p-3">
    <div id="app" class="max-w-[98%] mx-auto">
        <!-- Quick Stats & Global Export Bar -->
        <div class="bg-white border border-emerald-200 rounded-lg px-3 py-2 mb-2.5 shadow-sm text-xs flex flex-wrap justify-between items-center gap-2">
            <div class="flex items-center gap-3 text-gray-700 font-medium">
                <span>📊 <b>13</b> Spieltage (Saison 2026/2027)</span>
                <span class="text-gray-300">•</span>
                <span>👥 <b>[[ allPlayers.length ]]</b> aktive Spieler</span>
                <span class="text-gray-300">•</span>
                <span class="text-emerald-800 font-semibold">⭐ Nächster Spieltag: <b>06.10.2026</b> (#1)</span>
            </div>
            <div>
                <button @click="downloadAllIcs()" class="bg-emerald-800 hover:bg-emerald-900 text-white px-3 py-1.5 rounded-lg text-xs font-semibold transition border border-emerald-700 flex items-center gap-1.5 shadow-sm">
                    <span>📅 Gesamter Spielplan als ICS</span>
                </button>
            </div>
        </div>

        <!-- Player Legend & Controls Bar -->
        <div class="bg-white border border-gray-200 rounded-lg p-2.5 mb-2.5 shadow-sm flex flex-col md:flex-row justify-between items-start md:items-center gap-2">
            <div class="flex-1 w-full">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-1.5 gap-1">
                    <span class="font-bold text-xs uppercase tracking-wider text-gray-700">Klick [NAME] = Spiele filtern | 📅 = Kalender-Download für z.B. Google Kalender:</span>
                    <span v-if="currentFilter !== 'ALL'" class="text-[11px] text-emerald-700 font-semibold">
                        Filter aktiv: [[ currentFilter ]] ([[ filteredMatches.length ]] Spieltage)
                    </span>
                </div>

                <div class="flex flex-wrap gap-2 items-center pt-1 pb-0.5">
                    <!-- 'Alle' button -->
                    <button @click="setFilter('ALL')"
                        :class="currentFilter === 'ALL' ? 'bg-black text-white border-black ring-2 ring-gray-400 scale-105' : 'bg-gray-100 hover:bg-gray-200 text-gray-800 border-gray-300'"
                        class="px-2.5 py-0.5 rounded text-[10px] font-bold transition flex items-center gap-1 border shadow-sm">
                        <span>Alle</span>
                    </button>

                    <!-- Player pills -->
                    <div v-for="player in allPlayers" :key="player"
                        :style="{ backgroundColor: currentFilter === player ? '#111827' : (playerColors[player] ? playerColors[player].bg : '#eee'), borderColor: playerColors[player] ? playerColors[player].border : '#ccc' }"
                        :class="currentFilter === player ? 'scale-110 font-black shadow-xl ring-2 ring-emerald-600 ring-offset-1 z-10' : 'hover:opacity-95 shadow-sm border'""
                        class="inline-flex items-center rounded border transition relative">
                        <button @click="setFilter(player)"
                            :style="{ color: currentFilter === player ? '#ffffff' : '#111827' }"
                            class="px-2 py-1 text-xs font-bold flex items-center gap-1 focus:outline-none">
                            <span>[[ player ]]</span>
                            <span v-if="nextMatchPlayers.includes(player)" title="Am nächsten Spieltag im Einsatz">⭐</span>
                        </button>
                        <button @click.stop="downloadPlayerIcs(player)"
                            :style="{ borderColor: playerColors[player] ? playerColors[player].border : '#ccc', color: currentFilter === player ? '#ffffff' : '#111827' }"
                            class="px-2 py-1 text-xs border-l transition hover:bg-black/10 focus:outline-none"
                            :title="'ICS-Kalender für ' + player + ' herunterladen'">
                            📅
                        </button>
                    </div>
                </div>
            </div>
            <div>
                <button @click="togglePastMatches"
                    :class="showPastMatches ? 'bg-emerald-100 hover:bg-emerald-200 text-emerald-800 border-emerald-300' : 'bg-gray-100 hover:bg-gray-200 text-gray-700 border-gray-300'"
                    class="text-xs font-medium px-3 py-1.5 rounded-lg border transition whitespace-nowrap">
                    [[ showPastMatches ? '📁 Vergangene Spiele ausblenden' : '📁 Vergangene Spiele anzeigen' ]]
                </button>
            </div>
        </div>

        <!-- Ultra-Compact Table -->
        <div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-x-auto mb-2.5">
            <table class="w-full text-left border-collapse text-xs table-auto">
                <thead>
                    <tr class="bg-gray-100 text-gray-600 uppercase text-[10px] tracking-wider border-b border-gray-200">
                        <th class="py-2 px-1 whitespace-nowrap w-1">Datum</th>
                        <th class="py-2 px-1.5">19:00 Uhr</th>
                        <th class="py-2 px-1.5">20:00 Uhr</th>
                        <th class="py-2 px-1.5">21:00 Uhr</th>
                        <th class="py-2 px-1.5">Doppel / Einzel <span class="font-normal normal-case text-gray-500">(20:30)</span></th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200">
                    <tr v-if="displayedMatches.length === 0">
                        <td colspan="5" class="py-6 text-center text-gray-500 text-xs">Keine entsprechenden Spiele gefunden (Vergangene Spiele sind ausgeblendet).</td>
                    </tr>
                    <tr v-for="(m, idx) in displayedMatches" :key="m.spieltag"
                        :id="isNextUpcoming(m, idx) ? 'next-match-target' : null"
                        :class="getRowClass(m, idx)">
                        <template v-if="m.status === 'Reserviert für alle'">
                            <td colspan="5" class="py-3 px-3 text-center bg-amber-50 border-amber-200">
                                <div class="flex items-center justify-center gap-2 text-amber-900 font-bold text-xs md:text-sm whitespace-nowrap">
                                    <span>🎾 Spieltag #[[ m.spieltag ]] — [[ formatFullDate(m.date) ]]:</span>
                                    <span class="bg-amber-200 text-amber-900 px-2.5 py-1 rounded-md shadow-sm border border-amber-300 font-extrabold uppercase tracking-wide">
                                        Reserviert für alle
                                    </span>
                                </div>
                            </td>
                        </template>
                        <template v-else>
                        <td class="py-2 px-1" :class="m.status === 'Abgeschlossen' ? 'text-gray-400' : 'text-gray-600'">
                            <span class="md:hidden">[[ formatShortDate(m.date) ]]</span>
                            <div class="hidden md:block leading-tight">
                                <span class="font-bold text-[10px]">#[[ m.spieltag ]]</span>
                                <div class="text-[11px]">[[ formatFullDate(m.date) ]]</div>
                            </div>
                        </td>
                        <!-- Platz 1 (19:00) -->
                        <td class="py-2 px-1.5">
                            <div class="flex flex-wrap items-center gap-1">
                                <span v-html="formatPlayerBadge(m.p1.p1, m.status === 'Abgeschlossen')"></span>
                                <span v-if="m.p1.p1 && m.p1.p2" class="text-[9px] hidden md:inline" :class="m.status === 'Abgeschlossen' ? 'text-gray-300' : 'text-gray-400'">vs</span>
                                <span v-html="formatPlayerBadge(m.p1.p2, m.status === 'Abgeschlossen')"></span>
                            </div>
                        </td>
                        <!-- Platz 1 (20:00) -->
                        <td class="py-2 px-1.5">
                            <div class="flex flex-wrap items-center gap-1">
                                <span v-html="formatPlayerBadge(m.p2.p1, m.status === 'Abgeschlossen')"></span>
                                <span v-if="m.p2.p1 && m.p2.p2" class="text-[9px] hidden md:inline" :class="m.status === 'Abgeschlossen' ? 'text-gray-300' : 'text-gray-400'">vs</span>
                                <span v-html="formatPlayerBadge(m.p2.p2, m.status === 'Abgeschlossen')"></span>
                            </div>
                        </td>
                        <!-- Platz 1 (21:00) -->
                        <td class="py-2 px-1.5">
                            <div class="flex flex-wrap items-center gap-1">
                                <span v-html="formatPlayerBadge(m.p3.p1, m.status === 'Abgeschlossen')"></span>
                                <span v-if="m.p3.p1 && m.p3.p2" class="text-[9px] hidden md:inline" :class="m.status === 'Abgeschlossen' ? 'text-gray-300' : 'text-gray-400'">vs</span>
                                <span v-html="formatPlayerBadge(m.p3.p2, m.status === 'Abgeschlossen')"></span>
                            </div>
                        </td>
                        <!-- Platz 2 - Doppel / Einzel (20:30) -->
                        <td class="py-2 px-1.5">
                            <div v-if="m.court2_type !== 'singles'" class="flex flex-wrap items-center gap-1">
                                <span class="inline-flex flex-col gap-0.5">
                                    <span v-html="formatPlayerBadge(m.doppel.team1[0], m.status === 'Abgeschlossen')"></span>
                                    <span v-html="formatPlayerBadge(m.doppel.team1[1], m.status === 'Abgeschlossen')"></span>
                                </span>
                                <span v-if="(m.doppel.team1[0] || m.doppel.team1[1]) && (m.doppel.team2[0] || m.doppel.team2[1])" class="text-[9px] hidden md:inline" :class="m.status === 'Abgeschlossen' ? 'text-gray-300' : 'text-emerald-700 font-bold'">vs</span>
                                <span class="inline-flex flex-col gap-0.5">
                                    <span v-html="formatPlayerBadge(m.doppel.team2[0], m.status === 'Abgeschlossen')"></span>
                                    <span v-html="formatPlayerBadge(m.doppel.team2[1], m.status === 'Abgeschlossen')"></span>
                                </span>
                            </div>
                            <div v-else class="flex flex-wrap items-center gap-1">
                                <span v-html="formatPlayerBadge(m.doppel.p1, m.status === 'Abgeschlossen')"></span>
                                <span v-if="m.doppel.p1 && m.doppel.p2" class="text-[9px] hidden md:inline" :class="m.status === 'Abgeschlossen' ? 'text-gray-300' : 'text-gray-400'">vs</span>
                                <span v-html="formatPlayerBadge(m.doppel.p2, m.status === 'Abgeschlossen')"></span>
                            </div>
                        </td>
                        </template>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Player Statistics Matrix Section -->
        <div class="bg-white border border-emerald-200 rounded-lg p-3 mb-2.5 shadow-sm">
            <div class="flex justify-between items-center mb-2 border-b border-gray-100 pb-1.5">
                <h3 class="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
                    <span>📊 Spieler-Statistik-Matrix (Einzel vs. Doppel)</span>
                </h3>
                <span class="text-[10px] text-gray-500 font-medium">Klick auf Spaltenköpfe zum Sortieren</span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs">
                    <thead>
                        <tr class="bg-emerald-800 text-white select-none">
                            <th @click="sortBy('name')" class="p-2 font-semibold cursor-pointer hover:bg-emerald-700">Spieler [[ sortColumn === 'name' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' ]]</th>
                            <th @click="sortBy('singles')" class="p-2 text-center font-semibold cursor-pointer hover:bg-emerald-700">Einzel [[ sortColumn === 'singles' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' ]]</th>
                            <th @click="sortBy('doppel')" class="p-2 text-center font-semibold cursor-pointer hover:bg-emerald-700">Doppel [[ sortColumn === 'doppel' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' ]]</th>
                            <th @click="sortBy('total')" class="p-2 text-center font-semibold cursor-pointer hover:bg-emerald-700">Gesamt Spiele [[ sortColumn === 'total' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' ]]</th>
                            <th @click="sortBy('ratio')" class="p-2 text-center font-semibold cursor-pointer hover:bg-emerald-700">Doppel-Anteil [[ sortColumn === 'ratio' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' ]]</th>
                            <th @click="sortBy('kosten')" class="p-2 text-center font-semibold cursor-pointer hover:bg-emerald-700" title="Kosten = (Einzel × 0.5) + (Doppel × 0.375)">Kosten ℹ️ [[ sortColumn === 'kosten' ? (sortDirection === 'asc' ? '▲' : '▼') : '↕' ]]</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="stat in sortedPlayerStats" :key="stat.name" class="border-b border-gray-100 hover:bg-emerald-50/50">
                            <td class="p-2 font-medium">
                                <span v-html="formatPlayerBadge(stat.name, false)"></span>
                            </td>
                            <td class="p-2 text-center font-semibold text-gray-700">[[ stat.singles ]]</td>
                            <td class="p-2 text-center font-semibold text-emerald-700">[[ stat.doppel ]]</td>
                            <td class="p-2 text-center font-bold text-gray-900">[[ stat.total ]]</td>
                            <td class="p-2 text-center">
                                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-gray-100 text-gray-800">
                                    [[ stat.ratio ]]%
                                </span>
                            </td>
                            <td class="p-2 text-center font-bold text-emerald-800">[[ stat.kosten ]]</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Rules Section -->
        <div class="bg-white border border-emerald-200 rounded-lg p-3 shadow-sm">
            <div class="flex justify-between items-center mb-2 border-b border-gray-100 pb-1.5">
                <h3 class="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
                    <span>📋 Aktive Spielerregeln & Abwesenheiten</span>
                </h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2">
                <div v-for="(rulesList, player) in rulesByPlayer" :key="player" class="bg-gray-50 border border-gray-200 rounded p-2.5 text-xs flex flex-col justify-between shadow-2xs">
                    <div>
                        <div class="mb-2">
                            <span :style="{ backgroundColor: playerColors[player] ? playerColors[player].bg : '#eee', borderColor: playerColors[player] ? playerColors[player].border : '#ccc', color: '#111827' }"
                                class="inline-flex items-center px-2.5 py-0.5 rounded border text-xs font-bold shadow-2xs">
                                [[ player ]]
                            </span>
                        </div>
                        <ul class="list-disc list-inside text-gray-600 text-[11px] space-y-1 pl-1">
                            <li v-for="(desc, idx) in rulesList" :key="idx">[[ desc ]]</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Footer / Stand timestamp -->
        <div class="mt-3 mb-2 text-center text-xs text-gray-500 py-2 border-t border-gray-200">
            Stand: /*UPDATE_DATE_PLACEHOLDER*/
        </div>

    </div>

    <script>
        const matchesData = /*JSON_DATA_PLACEHOLDER*/;
        const playerRules = /*RULES_JSON_PLACEHOLDER*/;
        const playerStats = /*PLAYER_STATS_JSON_PLACEHOLDER*/;

        const { createApp, ref, computed, onMounted, nextTick } = Vue;

        createApp({
            setup() {
                const currentFilter = ref('ALL');
                const showPastMatches = ref(false);
                const rulesByPlayer = ref(playerRules);

                function getMatchPlayers(m) {
                    const players = [
                        m.p1.p1, m.p1.p2,
                        m.p2.p1, m.p2.p2,
                        m.p3.p1, m.p3.p2
                    ];
                    if (m.court2_type === 'singles') {
                        if (m.doppel.p1) players.push(m.doppel.p1);
                        if (m.doppel.p2) players.push(m.doppel.p2);
                    } else {
                        if (m.doppel.team1) players.push(...m.doppel.team1);
                        if (m.doppel.team2) players.push(...m.doppel.team2);
                    }
                    return players.filter(p => p && p !== 'vs');
                }

                const allPlayers = computed(() => {
                    return [...new Set(matchesData.flatMap(m => getMatchPlayers(m)))].sort();
                });

                const explicitPlayerColors = {
                    "Beumer": { bg: '#bfdbfe', text: '#111827', border: '#60a5fa' },   // Soft Blue
                    "Dedores": { bg: '#fecaca', text: '#111827', border: '#f87171' },  // Soft Red
                    "Hansmann": { bg: '#fef08a', text: '#111827', border: '#facc15' }, // Soft Yellow
                    "Heyn": { bg: '#bbf7d0', text: '#111827', border: '#4ade80' },     // Soft Green
                    "Hinz": { bg: '#fed7aa', text: '#111827', border: '#fb923c' },     // Soft Orange
                    "Kissner": { bg: '#e9d5ff', text: '#111827', border: '#c084fc' },  // Soft Purple
                    "Kuhlhoff": { bg: '#a5f3fc', text: '#111827', border: '#22d3ee' }, // Soft Cyan
                    "Marschollek": { bg: '#fbcfe8', text: '#111827', border: '#f472b6' }, // Soft Pink
                    "Mönning": { bg: '#c7d2fe', text: '#111827', border: '#818cf8' },  // Soft Indigo
                    "Nolte": { bg: '#d9f99d', text: '#111827', border: '#a3e635' },    // Soft Lime
                    "Prodehl": { bg: '#99f6e4', text: '#111827', border: '#2dd4bf' },  // Soft Teal
                    "Redieker": { bg: '#fecdd3', text: '#111827', border: '#fb7185' }, // Soft Rose
                    "Rumpf": { bg: '#fed7aa', text: '#111827', border: '#f97316' },    // Distinct Deep Orange/Amber for Rumpf
                    "Trojanski": { bg: '#cbd5e1', text: '#111827', border: '#94a3b8' }, // Soft Slate
                    "Weber": { bg: '#ddd6fe', text: '#111827', border: '#a78bfa' },    // Soft Violet
                    "Wojtanowitsch": { bg: '#a7f3d0', text: '#111827', border: '#34d399' }, // Soft Emerald
                    "van de Loo": { bg: '#bae6fd', text: '#111827', border: '#38bdf8' }  // Soft Sky
                };

                const playerColors = {};
                allPlayers.value.forEach((player) => {
                    if (explicitPlayerColors[player]) {
                        playerColors[player] = explicitPlayerColors[player];
                    } else {
                        // Fallback palette
                        playerColors[player] = { bg: '#e2e8f0', text: '#111827', border: '#64748b' };
                    }
                });

                const filteredMatches = computed(() => {
                    if (currentFilter.value === 'ALL') return matchesData;
                    return matchesData.filter(m => getMatchPlayers(m).includes(currentFilter.value));
                });

                const displayedMatches = computed(() => {
                    let matches = matchesData;
                    if (!showPastMatches.value) {
                        matches = matches.filter(m => m.status !== 'Abgeschlossen');
                    }
                    return matches;
                });

                function matchHasPlayer(m, player) {
                    if (player === 'ALL') return true;
                    return getMatchPlayers(m).includes(player);
                }

                const nextMatch = computed(() => {
                    const todayStr = new Date().toISOString().split('T')[0];
                    let m = matchesData.find(match => match.date >= todayStr && match.status !== 'Abgeschlossen');
                    return m || matchesData[0];
                });

                const nextMatchPlayers = computed(() => {
                    const m = nextMatch.value;
                    if (!m) return [];
                    return [...new Set(getMatchPlayers(m))].sort();
                });

                const nextUpcomingIndex = computed(() => {
                    const todayStr = new Date().toISOString().split('T')[0];
                    let idx = displayedMatches.value.findIndex(m => m.date >= todayStr);
                    if (idx === -1 && displayedMatches.value.length > 0) {
                        idx = 0;
                    }
                    return idx;
                });

                function isNextUpcoming(m, idx) {
                    if (currentFilter.value !== 'ALL' || showPastMatches.value) return false;
                    const firstFuture = nextUpcomingIndex.value;
                    return firstFuture !== -1 && idx === firstFuture && m.status !== 'Abgeschlossen';
                }

                function getRowClass(m, idx) {
                    const isCompleted = m.status === 'Abgeschlossen';
                    const isNext = isNextUpcoming(m, idx);
                    const hasPlayer = matchHasPlayer(m, currentFilter.value);

                    let base = '';
                    if (!hasPlayer && currentFilter.value !== 'ALL') {
                        base = 'opacity-30 grayscale-[30%] ';
                    }

                    if (isNext) {
                        return base + 'bg-emerald-50/90 border-l-4 border-emerald-600 font-medium hover:bg-emerald-100/60 transition';
                    } else if (isCompleted) {
                        return base + 'bg-gray-50/70 text-gray-400 hover:bg-gray-100/80 transition';
                    } else {
                        return base + (idx % 2 === 0 ? 'bg-white hover:bg-emerald-50/40 transition' : 'bg-gray-100/90 hover:bg-emerald-50/40 transition');
                    }
                }

                function setFilter(player) {
                    currentFilter.value = (currentFilter.value === player) ? 'ALL' : player;
                }

                function togglePastMatches() {
                    showPastMatches.value = !showPastMatches.value;
                }

                function formatShortDate(dateStr) {
                    if (!dateStr) return '';
                    const parts = dateStr.split('-');
                    if (parts.length === 3) {
                        return `${parts[2]}.${parts[1]}`;
                    }
                    return dateStr;
                }

                function formatFullDate(dateStr) {
                    if (!dateStr) return '';
                    const parts = dateStr.split('-');
                    if (parts.length === 3) {
                        return `${parts[2]}.${parts[1]}.${parts[0]}`;
                    }
                    return dateStr;
                }

                function formatPlayerBadge(player, isCompleted) {
                    if (!player || player === 'vs') return '';
                    const colors = playerColors[player] || { bg: '#eee', text: '#333', border: '#ccc' };
                    const isSelected = currentFilter.value === player;

                    const shortName = player.length > 4 ? player.substring(0, 4) + '...' : player;
                    const innerHtml = `<span class="md:hidden">${shortName}</span><span class="hidden md:inline">${player}</span>`;

                    if (isSelected) {
                        return `<span class="px-2.5 py-0.5 rounded text-xs font-black inline-block border shadow-md whitespace-nowrap ring-2 ring-emerald-600 ring-offset-1" style="background-color: #111827; color: #ffffff; border-color: ${colors.border};">${innerHtml}</span>`;
                    } else if (isCompleted) {
                        return `<span class="px-2 py-0.5 rounded text-xs font-medium inline-block border whitespace-nowrap opacity-40 grayscale-[20%]" style="background-color: ${colors.bg}; color: ${colors.text}; border-color: ${colors.border};">${innerHtml}</span>`;
                    } else {
                        return `<span class="px-2 py-0.5 rounded text-xs font-bold inline-block border shadow-sm whitespace-nowrap" style="background-color: ${colors.bg}; color: ${colors.text}; border-color: ${colors.border};">${innerHtml}</span>`;
                    }
                }

                function downloadPlayerIcs(playerName) {
                    let icsContent = "BEGIN:VCALENDAR\\nVERSION:2.0\\nPRODID:-//Tennis Spielplan 2026/2027//DE\\nCALSCALE:GREGORIAN\\nMETHOD:PUBLISH\\n";

                    matchesData.forEach(m => {
                        let matchTime = null;
                        let courtName = "";

                        const p1List = [m.p1.p1, m.p1.p2];
                        const p2List = [m.p2.p1, m.p2.p2];
                        const p3List = [m.p3.p1, m.p3.p2];
                        const c2List = (m.court2_type === 'singles') ? [m.doppel.p1, m.doppel.p2] : [...(m.doppel.team1 || []), ...(m.doppel.team2 || [])];

                        if (p1List.includes(playerName)) { matchTime = m.p1.time; courtName = "19:00 Uhr"; }
                        else if (p2List.includes(playerName)) { matchTime = m.p2.time; courtName = "20:00 Uhr"; }
                        else if (p3List.includes(playerName)) { matchTime = m.p3.time; courtName = "21:00 Uhr"; }
                        else if (c2List.includes(playerName)) {
                            matchTime = m.doppel.time;
                            courtName = (m.court2_type === 'singles') ? "Einzel (20:30 Uhr)" : "Doppel (20:30 Uhr)";
                        }

                        if (matchTime && m.date) {
                            const dateStr = m.date.replace(/-/g, '');
                            const timeClean = matchTime.replace(':', '') + '00';
                            let [hours, mins] = matchTime.split(':').map(Number);
                            hours += 1;
                            mins += 30;
                            if (mins >= 60) { hours += 1; mins -= 60; }
                            const endTimeStr = String(hours).padStart(2, '0') + String(mins).padStart(2, '0') + '00';

                            let matchDetails = `19:00: ${m.p1.p1} vs ${m.p1.p2} | 20:00: ${m.p2.p1} vs ${m.p2.p2} | 21:00: ${m.p3.p1} vs ${m.p3.p2}`;

                            icsContent += "BEGIN:VEVENT\\n";
                            icsContent += `UID:spieltag-${m.spieltag}-${playerName.replace(/\\s+/g, '')}@tennis.local\\n`;
                            icsContent += `DTSTAMP:${dateStr}T${timeClean}Z\\n`;
                            icsContent += `DTSTART:${dateStr}T${timeClean}Z\\n`;
                            icsContent += `DTEND:${dateStr}T${endTimeStr}Z\\n`;
                            icsContent += `SUMMARY:Tennis-Training (${courtName}, Spieltag ${m.spieltag})\\n`;
                            icsContent += `DESCRIPTION:Deine Begegnungen:\\n${matchDetails}\\n`;
                            icsContent += "END:VEVENT\\n";
                        }
                    });

                    icsContent += "END:VCALENDAR";

                    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
                    const link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = `Tennis_Spielplan_${playerName.replace(/__+/g, '_')}.ics`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }

                function downloadAllIcs() {
                    let icsContent = "BEGIN:VCALENDAR\\nVERSION:2.0\\nPRODID:-//Tennis Spielplan Gesamtsaison 2026/2027//DE\\nCALSCALE:GREGORIAN\\nMETHOD:PUBLISH\\n";
                    matchesData.forEach(m => {
                        if (m.status === 'Reserviert für alle' || !m.date) return;
                        const dateStr = m.date.replace(/-/g, '');
                        const timeClean = '190000';
                        const endTimeStr = '223000';
                        let matchDetails = `19:00: ${m.p1.p1} vs ${m.p1.p2} | 20:00: ${m.p2.p1} vs ${m.p2.p2} | 21:00: ${m.p3.p1} vs ${m.p3.p2}`;
                        icsContent += "BEGIN:VEVENT\\n";
                        icsContent += `UID:spieltag-${m.spieltag}-gesamt@tennis.local\\n`;
                        icsContent += `DTSTAMP:${dateStr}T${timeClean}Z\\n`;
                        icsContent += `DTSTART:${dateStr}T${timeClean}Z\\n`;
                        icsContent += `DTEND:${dateStr}T${endTimeStr}Z\\n`;
                        icsContent += `SUMMARY:Tennis-Abend Spieltag ${m.spieltag} (Wintersaison)\\n`;
                        icsContent += `DESCRIPTION:Spieltag ${m.spieltag} am ${m.date}\\n${matchDetails}\\n`;
                        icsContent += "END:VEVENT\\n";
                    });
                    icsContent += "END:VCALENDAR";

                    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
                    const link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = "Tennis_Gesamter_Spielplan_2026_2027.ics";
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }

                const sortColumn = ref('total');
                const sortDirection = ref('desc');

                function sortBy(col) {
                    if (sortColumn.value === col) {
                        sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
                    } else {
                        sortColumn.value = col;
                        sortDirection.value = ['name', 'ratio'].includes(col) ? 'asc' : 'desc';
                    }
                }

                const sortedPlayerStats = computed(() => {
                    const entries = Object.entries(playerStats).map(([name, stats]) => ({ name, ...stats }));
                    entries.sort((a, b) => {
                        let valA = (sortColumn.value === 'name') ? a.name : a[sortColumn.value];
                        let valB = (sortColumn.value === 'name') ? b.name : b[sortColumn.value];
                        if (valA < valB) return sortDirection.value === 'asc' ? -1 : 1;
                        if (valA > valB) return sortDirection.value === 'asc' ? 1 : -1;
                        return 0;
                    });
                    return entries;
                });

                onMounted(() => {
                    if (currentFilter.value === 'ALL' && !showPastMatches.value) {
                        setTimeout(() => {
                            const target = document.getElementById('next-match-target');
                            if (target) {
                                target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            }
                        }, 150);
                    }
                });

                return {
                    currentFilter,
                    showPastMatches,
                    rulesByPlayer,
                    playerStats,
                    allPlayers,
                    playerColors,
                    filteredMatches,
                    displayedMatches,
                    nextMatch,
                    nextMatchPlayers,
                    isNextUpcoming,
                    getRowClass,
                    setFilter,
                    togglePastMatches,
                    formatShortDate,
                    formatFullDate,
                    formatPlayerBadge,
                    downloadPlayerIcs,
                    downloadAllIcs,
                    sortColumn,
                    sortDirection,
                    sortedPlayerStats,
                    sortBy
                };
            },
            compilerOptions: {
                delimiters: ['[[', ']]']
            }
        }).mount('#app');
    </script>
</body>
</html>
"""

html_content = html_template.replace('/*JSON_DATA_PLACEHOLDER*/', json.dumps(matches, ensure_ascii=False))
html_content = html_content.replace('/*RULES_JSON_PLACEHOLDER*/', json.dumps(frontend_rules_by_player, ensure_ascii=False))
html_content = html_content.replace('/*PLAYER_STATS_JSON_PLACEHOLDER*/', json.dumps(player_stats, ensure_ascii=False))
html_content = html_content.replace('/*UPDATE_DATE_PLACEHOLDER*/', datetime.datetime.now().strftime('%d.%m.%Y %H:%M'))

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print('Successfully structured PLAYER_RULES with nested "rules" key and regenerated index.html!')
