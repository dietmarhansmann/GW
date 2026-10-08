from collections import Counter, defaultdict
from datetime import date
from itertools import combinations, permutations
from pathlib import Path
import json
import re
import html
import random

# Independent 2027-only generator. It deliberately does not read or write index.html.
random.seed(20270105)

PLAYERS = [
    "Beumer", "Dedores", "Hansmann", "Heyn", "Hinz", "Kissner", "Knust",
    "Kuhlhoff", "Marschollek", "Mönning", "Nolte", "Prodehl", "Quante", "Redieker",
    "Rumpf", "Trojanski", "Van de Looh", "Weber", "Wojtanowitsch",
]

# Doubles share (ratio); 0.0 means singles only. None means no fixed preference.
RATIOS = {
    "Beumer": 0.50, "Dedores": 0.0, "Hansmann": 0.30, "Heyn": 0.30,
    "Hinz": 0.50, "Kissner": 0.0, "Kuhlhoff": 0.0, "Marschollek": 0.90,
    "Mönning": 0.0, "Nolte": 0.0, "Prodehl": 0.60, "Quante": 0.75, "Redieker": 0.20, "Rumpf": 0.0, "Trojanski": 0.0,
    "Van de Looh": 0.0, "Wojtanowitsch": 0.0,
}

ABSENCES = {
    "Beumer": {22},
    "Dedores": {16, 17, 20, 21, 25, 26, 28},
    "Heyn": {15, 19, 23, 26, 28, 30},
    "Hinz": {30},
    "Kuhlhoff": {14, 18},
    "Marschollek": {16, 24},
    "Mönning": {14, 15},
    "Nolte": {22, 25, 29, 30},
    "Trojanski": {20},
}

# A player is not scheduled after reaching their requested number of appearances.
MAX_APPEARANCES = {"Dedores": 7, "Quante": 4}

# Manual pairings live in manual_matches_2027.json next to this script.
# Edit that JSON file, then rerun this generator; overrides are validated and
# all statistics and exports are generated from the final schedule.
MANUAL_MATCHES_FILE = Path(__file__).with_name("manual_matches_2027.json")

START_DAY, END_DAY = 14, 30
DATES = {
    n: date.fromisoformat(f"2027-{month:02d}-{day:02d}")
    for n, month, day in [
        (14, 1, 5), (15, 1, 12), (16, 1, 19), (17, 1, 26),
        (18, 2, 2), (19, 2, 9), (20, 2, 16), (21, 2, 23),
        (22, 3, 2), (23, 3, 9), (24, 3, 16), (25, 3, 23),
        (26, 3, 30), (27, 4, 6), (28, 4, 13), (29, 4, 20), (30, 4, 27),
    ]
}

# Allocate Quante's three doubles and one singles appearance across 2027.
_quante_rng = random.Random(20270105)
QUANTE_DOUBLE_DAYS = set(_quante_rng.sample([day for day in DATES if day % 2], 3))
QUANTE_SINGLE_DAY = _quante_rng.choice([day for day in DATES if day % 2 == 0])
QUANTE_DAYS = QUANTE_DOUBLE_DAYS | {QUANTE_SINGLE_DAY}


def slots_for(day):
    # Keep the existing alternating pattern: odd matchdays have a doubles match.
    if day % 2:
        return ["19:00", "19:00", "20:00", "20:00", "21:00", "21:00", "D", "D", "D", "D"]
    return ["19:00", "19:00", "20:00", "20:00", "21:00", "21:00", "20:30", "20:30"]


def choose_attendees():
    counts = Counter()
    last_played = {p: -99 for p in PLAYERS}
    attendance = {}
    for day in range(START_DAY, END_DAY + 1):
        needed = 10 if day % 2 else 8
        candidates = []
        for p in PLAYERS:
            if day in ABSENCES.get(p, set()):
                continue
            if p == "Quante" and day not in QUANTE_DAYS:
                continue
            if counts[p] >= MAX_APPEARANCES.get(p, float("inf")):
                continue
            if p == "Trojanski" and day - last_played[p] < 2:
                continue
            if p == "Van de Looh" and day - last_played[p] < 4:
                continue
            # Prefer fewer appearances; tie-break toward those resting longest.
            score = counts[p] + (0.55 if last_played[p] == day - 1 else 0)
            candidates.append((score, last_played[p], random.random(), p))
        candidates.sort()
        selected = [entry[3] for entry in candidates[:needed]]
        if day in QUANTE_DAYS and "Quante" not in selected:
            selected[-1] = next(entry[3] for entry in candidates if entry[3] == "Quante")
        if len(selected) != needed:
            raise RuntimeError(f"Not enough eligible players for matchday {day}")
        attendance[day] = selected
        for p in selected:
            counts[p] += 1
            last_played[p] = day
    return attendance


def doubles_choices(day, attendees, doubles_so_far, games_so_far, time_counts):
    if day % 2 == 0:
        return set()
    eligible = [p for p in attendees if RATIOS.get(p, None) != 0.0]
    if len(eligible) < 4:
        raise RuntimeError(f"Not enough doubles-eligible players on matchday {day}")
    best, best_score = None, float("inf")
    for choice in combinations(eligible, 4):
        if day in QUANTE_DOUBLE_DAYS and "Quante" not in choice:
            continue
        score = 0.0
        for p in attendees:
            future = list(time_counts[p])
            if p in choice:
                future[TIME_SLOTS.index("20:30")] += 1
                score += 100 * (max(future) - min(future)) ** 2
        for p in attendees:
            ratio = RATIOS.get(p)
            if ratio is None:
                continue
            total = games_so_far[p] + 1
            future_doubles = doubles_so_far[p] + (1 if p in choice else 0)
            # Normalize deviations so high-frequency players do not dominate.
            score += ((future_doubles - ratio * total) ** 2) / max(total, 1)
        if score < best_score:
            best, best_score = set(choice), score
    if best is None:
        raise RuntimeError(f"Not enough doubles-eligible players on matchday {day}")
    return best


TIME_SLOTS = ("19:00", "20:00", "21:00", "20:30")
# Internal scheduling constraints: these are enforced but intentionally not all shown publicly.
TIME_RULES = {"Dedores": {"19:00", "20:00"}}


def assign_time_slots(singles, time_counts, slots, fixed_matches=(), fixed_time="20:30"):
    """Assign singles matches while balancing appearances across all four court times."""
    fixed = [(fixed_time, group) for group in fixed_matches]
    best_order, best_score = None, float("inf")
    for order in permutations(range(len(singles))):
        assigned = [(slot, singles[index]) for slot, index in zip(slots, order)] + fixed
        if any(
            slot not in TIME_RULES[player]
            for slot, group in assigned
            for player in group
            if player in TIME_RULES
        ):
            continue
        score = 0
        for player in {player for _, group in assigned for player in group}:
            future = list(time_counts[player])
            for slot, group in assigned:
                if player in group:
                    future[TIME_SLOTS.index(slot)] += 1
            # Minimize each player's difference between their most and least used time.
            imbalance = max(future) - min(future)
            score += imbalance * imbalance
        score += random.random() * 0.001
        if score < best_score:
            best_order, best_score = order, score
    if best_order is None:
        raise RuntimeError("Could not assign legal court times")
    ordered = [singles[index] for index in best_order]
    for slot, group in [(slot, group) for slot, group in zip(slots, ordered)] + fixed:
        slot_index = TIME_SLOTS.index(slot)
        for player in group:
            time_counts[player][slot_index] += 1
    return ordered


def pair_up(day, attendees, double_players, pair_counts, partner_counts, time_counts=None):
    if day % 2:
        singles = [p for p in attendees if p not in double_players]
        groups = [singles[i:i + 2] for i in range(0, 6, 2)]
        doubles = list(double_players)
        best = None
        best_score = float("inf")
        for _ in range(1000):
            random.shuffle(singles)
            random.shuffle(doubles)
            s_pairs = [tuple(singles[i:i + 2]) for i in range(0, 6, 2)]
            teams = [tuple(doubles[:2]), tuple(doubles[2:])]
            score = sum(pair_counts[tuple(sorted(x))] * 10 for x in s_pairs)
            if time_counts:
                for slot, pair in zip(TIME_SLOTS[:3], s_pairs):
                    for player in pair:
                        future = list(time_counts[player])
                        future[TIME_SLOTS.index(slot)] += 1
                        score += 500 * (max(future) - min(future)) ** 2
            if "Dedores" in singles[4:]:
                continue
            if any("Dedores" in pair and set(pair) & {"Prodehl", "Beumer", "Heyn"} for pair in s_pairs):
                continue
            score += partner_counts[tuple(sorted(teams[0]))] * 12
            score += partner_counts[tuple(sorted(teams[1]))] * 12
            for a in teams[0]:
                for b in teams[1]:
                    score += pair_counts[tuple(sorted((a, b)))] * 5
            if score < best_score:
                best, best_score = (s_pairs, teams), score
        singles, teams = best
        if time_counts:
            singles = assign_time_slots(singles, time_counts, TIME_SLOTS[:3], [list(double_players)])
        for pair in singles:
            pair_counts[tuple(sorted(pair))] += 1
        partner_counts[tuple(sorted(teams[0]))] += 1
        partner_counts[tuple(sorted(teams[1]))] += 1
        for a in teams[0]:
            for b in teams[1]:
                pair_counts[tuple(sorted((a, b)))] += 1
        return singles, teams

    singles = list(attendees)
    best_pairs, best_score = None, float("inf")
    for _ in range(1200):
        random.shuffle(singles)
        pairs = [tuple(singles[i:i + 2]) for i in range(0, 8, 2)]
        if any("Dedores" in pair and set(pair) & {"Prodehl", "Beumer", "Heyn"} for pair in pairs):
            continue
        if any("Dedores" in pair for pair in pairs[2:]):
            continue
        score = sum(pair_counts[tuple(sorted(pair))] * 10 for pair in pairs)
        for slot, pair in zip(TIME_SLOTS[:3], pairs[:3]):
            for player in pair:
                future = list(time_counts[player])
                future[TIME_SLOTS.index(slot)] += 1
                score += 500 * (max(future) - min(future)) ** 2
        for player in pairs[3]:
            future = list(time_counts[player])
            future[TIME_SLOTS.index("20:30")] += 1
            score += 500 * (max(future) - min(future)) ** 2
        if score < best_score:
            best_pairs, best_score = pairs, score
    for pair in best_pairs:
        pair_counts[tuple(sorted(pair))] += 1
    return best_pairs, None


def generate_once():
    time_counts = defaultdict(lambda: [0, 0, 0, 0])
    attendance = choose_attendees()
    games, doubles_counts = Counter(), Counter()
    pair_counts, partner_counts = Counter(), Counter()
    matches = []

    for day in range(START_DAY, END_DAY + 1):
        attendees = attendance[day]
        double_players = doubles_choices(day, attendees, doubles_counts, games, time_counts)
        if day % 2:
            singles, teams = pair_up(day, attendees, double_players, pair_counts, partner_counts, time_counts)
            matches.append({"day": day, "date": DATES[day], "singles": singles, "teams": teams})
            for p in attendees:
                games[p] += 1
            for p in double_players:
                doubles_counts[p] += 1
            # A doubles participant is fixed at 20:30, so rotate the other three slots
            # among as many attendees as possible to compensate for that fixed assignment.
        else:
            singles = pair_up(day, attendees, set(), pair_counts, partner_counts, time_counts)[0]
            singles = assign_time_slots(
                singles[:3], time_counts, TIME_SLOTS[:3], [singles[3]], fixed_time="20:30"
            ) + [singles[3]]
            matches.append({"day": day, "date": DATES[day], "singles": singles, "teams": None})
            for p in attendees:
                games[p] += 1

    return matches


def optimize_time_slots(matches):
    """Globally rebalance match-time assignments without changing players or matchups."""
    def counts_for(schedule):
        counts = defaultdict(lambda: [0, 0, 0, 0])
        for match in schedule:
            for slot, pair in zip(TIME_SLOTS[:3], match["singles"][:3]):
                for player in pair:
                    counts[player][TIME_SLOTS.index(slot)] += 1
            final_players = ([player for team in match["teams"] for player in team]
                             if match["teams"] else match["singles"][3])
            for player in final_players:
                counts[player][TIME_SLOTS.index("20:30")] += 1
        return counts

    def score(schedule):
        counts = counts_for(schedule)
        total_score = 0.0
        for player, values in counts.items():
            allowed = sorted(TIME_SLOTS.index(slot) for slot in TIME_RULES.get(player, TIME_SLOTS))
            active = [values[index] for index in allowed]
            target = sum(active) / len(allowed)
            total_score += sum((value - target) ** 2 for value in active)
        return total_score

    current_score = score(matches)
    for _ in range(12):
        improved = False
        for match in matches:
            movable = 3 if match["teams"] else 4
            original = list(match["singles"][:movable])
            best_order, best_score = original, current_score
            for order in permutations(original):
                match["singles"][:movable] = order
                legal = all(
                    slot in TIME_RULES.get(player, TIME_SLOTS)
                    for slot, pair in zip(TIME_SLOTS[:3], match["singles"][:3])
                    for player in pair
                )
                if not match["teams"]:
                    legal = legal and all(
                        "20:30" in TIME_RULES.get(player, TIME_SLOTS)
                        for player in match["singles"][3]
                    )
                if legal:
                    candidate_score = score(matches)
                    if candidate_score < best_score - 1e-9:
                        best_order, best_score = list(order), candidate_score
            match["singles"][:movable] = best_order
            if best_score < current_score - 1e-9:
                current_score = best_score
                improved = True
        if not improved:
            break
    return matches


def apply_manual_overrides(matches):
    """Apply optional, explicit 2027 pairings from the adjacent JSON file."""
    if not MANUAL_MATCHES_FILE.exists():
        return matches

    overrides = json.loads(MANUAL_MATCHES_FILE.read_text(encoding="utf-8"))
    if not isinstance(overrides, dict):
        raise ValueError(f"{MANUAL_MATCHES_FILE.name} must contain a JSON object")

    by_day = {match["day"]: match for match in matches}
    for day_text, override in overrides.items():
        if str(day_text).startswith("_"):
            continue  # Reserved for explanatory comments and copyable examples.
        try:
            day = int(day_text)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid matchday key in {MANUAL_MATCHES_FILE.name}: {day_text!r}") from error
        if day not in by_day:
            raise ValueError(f"Manual override references unknown matchday {day}")
        if not isinstance(override, dict) or "singles" not in override or "teams" not in override:
            raise ValueError(f"Matchday {day} override must define both 'singles' and 'teams'")
        by_day[day]["singles"] = [tuple(pair) for pair in override["singles"]]
        by_day[day]["teams"] = (
            [tuple(team) for team in override["teams"]]
            if override["teams"] is not None else None
        )

    return matches


def generate():
    best_schedule, best_score = None, float("inf")
    for _ in range(300):
        try:
            candidate = generate_once()
        except RuntimeError:
            continue
        candidate = optimize_time_slots(candidate)
        counts = defaultdict(lambda: [0, 0, 0, 0])
        for match in candidate:
            for slot, pair in zip(TIME_SLOTS[:3], match["singles"][:3]):
                for player in pair:
                    counts[player][TIME_SLOTS.index(slot)] += 1
            final_players = ([player for team in match["teams"] for player in team]
                             if match["teams"] else match["singles"][3])
            for player in final_players:
                counts[player][TIME_SLOTS.index("20:30")] += 1
        if any(
            max(values) - min(values) > 3
            for player, values in counts.items()
            if player not in TIME_RULES
        ):
            continue
        score = 0
        for player, values in counts.items():
            if player in TIME_RULES:
                continue
            # Compare this player's slots to the ideal integer split for their games.
            total = sum(values)
            quotient, remainder = divmod(total, len(TIME_SLOTS))
            ideal = [quotient + (1 if index < remainder else 0) for index in range(len(TIME_SLOTS))]
            score += sum((actual - target) ** 2 for actual, target in zip(values, ideal))
        if score < best_score:
            best_schedule, best_score = candidate, score
        if score <= 2:
            break
    if best_schedule is None:
        raise RuntimeError("Could not generate a valid 2027 schedule")
    return best_schedule


def validate(matches):
    games, doubles = Counter(), Counter()
    last = {}
    for m in matches:
        day = m["day"]
        if day % 2:
            attendees = [p for pair in m["singles"] for p in pair] + [p for team in m["teams"] for p in team]
        else:
            attendees = [p for pair in m["singles"] for p in pair]
        assert len(attendees) == (10 if day % 2 else 8)
        assert len(attendees) == len(set(attendees)), f"Double booking on #{day}"
        assert not (set(attendees) & {p for p, days in ABSENCES.items() if day in days}), f"Absence violation #{day}"
        if day in QUANTE_DAYS:
            assert "Quante" in attendees, f"Quante missing from reserved matchday #{day}"
            if day in QUANTE_DOUBLE_DAYS:
                assert "Quante" in [p for team in m["teams"] for p in team], f"Quante not in doubles on #{day}"
            else:
                assert not any("Quante" in team for team in (m["teams"] or [])), f"Quante scheduled in doubles on #{day}"
        else:
            assert "Quante" not in attendees, f"Quante scheduled outside reserved matchdays #{day}"
        for player, maximum in MAX_APPEARANCES.items():
            assert games[player] + attendees.count(player) <= maximum, f"{player} exceeds {maximum} appearances"
        if "Dedores" in attendees:
            if day % 2:
                assert all("Dedores" not in team for team in m["teams"])
                assert any("Dedores" in pair for pair in m["singles"])
            else:
                assert "Dedores" in [p for pair in m["singles"][:2] for p in pair], f"Dedores outside allowed time #{day}"
        for time, pair in zip(TIME_SLOTS[:3], m["singles"][:3]):
            for player in pair:
                if player in TIME_RULES:
                    assert time in TIME_RULES[player], f"Time rule violation for {player} on #{day}"
        fourth = ([player for team in m["teams"] for player in team] if m["teams"]
                  else m["singles"][3])
        for player in fourth:
            if player in TIME_RULES:
                assert "20:30" in TIME_RULES[player], f"Time rule violation for {player} on #{day}"
        for pair in m["singles"]:
            games.update(pair)
            if "Dedores" in pair:
                assert not (set(pair) & {"Prodehl", "Beumer", "Heyn"}), f"Topf A pairing #{day}"
        if m["teams"]:
            for team in m["teams"]:
                doubles.update(team)
                games.update(team)
            for team in m["teams"]:
                assert not (set(team) & {p for p, ratio in RATIOS.items() if ratio == 0.0}), f"Singles-only in doubles #{day}"
            assert "Dedores" not in [p for team in m["teams"] for p in team]
        if "Trojanski" in attendees:
            assert day - last.get("Trojanski", -99) >= 2
            last["Trojanski"] = day
        if "Van de Looh" in attendees:
            assert day - last.get("Van de Looh", -99) >= 4
            last["Van de Looh"] = day
    time_counts = defaultdict(lambda: [0, 0, 0, 0])
    for match in matches:
        for slot, pair in zip(TIME_SLOTS[:3], match["singles"][:3]):
            for player in pair:
                time_counts[player][TIME_SLOTS.index(slot)] += 1
        fourth = ([player for team in match["teams"] for player in team] if match["teams"]
                  else match["singles"][3])
        for player in fourth:
            time_counts[player][TIME_SLOTS.index("20:30")] += 1
    for player, counts in time_counts.items():
        if player not in TIME_RULES:
            assert max(counts) - min(counts) <= 3, f"Unbalanced court times for {player}: {counts}"
    assert len(matches) == 17
    return games, doubles


def render(matches, games, doubles):
    rows = []
    for m in matches:
        singles = m["singles"]
        s = [f"{html.escape(a)} vs {html.escape(b)}" for a, b in singles]
        if m["teams"]:
            t1, t2 = m["teams"]
            court2 = f"<span class='team'>{html.escape(t1[0])} &amp; {html.escape(t1[1])}</span><br>vs<br><span class='team'>{html.escape(t2[0])} &amp; {html.escape(t2[1])}</span>"
            slots = s + [court2]
        else:
            slots = s[:3] + [s[3]]
        rows.append(
            f"<tr><th>#{m['day']}</th><td>{m['date'].strftime('%d.%m.%Y')}</td>"
            + "".join(f"<td>{v}</td>" for v in slots) + "</tr>"
        )

    stat_rows = []
    for p in PLAYERS:
        total = games[p]
        dcount = doubles[p]
        ratio = round(100 * dcount / total) if total else 0
        wanted = RATIOS.get(p)
        preference = f"{round(wanted * 100)}%" if wanted is not None else "–"
        stat_rows.append(
            f"<tr><td>{html.escape(p)}</td><td>{total}</td><td>{total-dcount}</td>"
            f"<td>{dcount}</td><td>{ratio}%</td><td>{preference}</td></tr>"
        )

    return f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tennis-Spielplan 2027</title>
<style>
:root{{--ink:#172b27;--muted:#586a64;--line:#d8e2dd;--paper:#fff;--bg:#f2f6f3;--green:#146b4b;--soft:#e8f2ec;--accent:#cb8b35}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;padding:28px}}
main{{max-width:1200px;margin:0 auto}}header,.card{{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:22px;margin-bottom:18px;box-shadow:0 5px 20px #1735280b}}
h1{{font-size:clamp(1.5rem,4vw,2.2rem);margin:0 0 4px}}h2{{font-size:1.1rem;margin:0 0 14px;color:var(--green)}}p{{margin:7px 0;color:var(--muted)}}.notice{{border-left:4px solid var(--accent);background:#fff7e8;padding:12px 14px;border-radius:7px;color:#634619;margin-top:16px}}
.table-wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;min-width:760px}}th,td{{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}}thead th{{background:var(--soft);color:var(--green);font-size:.84rem;white-space:nowrap}}tbody tr:nth-child(even){{background:#f8faf8}}tbody th{{white-space:nowrap;color:var(--green)}}.team{{font-weight:600}}.stats td:first-child{{font-weight:600}}.legend{{font-size:.9rem}}footer{{text-align:center;color:var(--muted);font-size:.83rem;padding:10px}}button{{border:0;background:var(--green);color:white;border-radius:8px;padding:9px 14px;font:inherit;cursor:pointer}}
@media(max-width:640px){{body{{padding:12px}}header,.card{{padding:16px;border-radius:10px}}th,td{{padding:8px}}}}
@media print{{body{{padding:0;background:white}}header,.card{{box-shadow:none;break-inside:avoid}}button{{display:none}}thead{{display:table-header-group}}tr{{break-inside:avoid}}}}
</style></head><body><main>
<header><button onclick="window.print()">Drucken / als PDF speichern</button><h1>🎾 Tennis-Spielplan – 2. Saisonhälfte 2027</h1>
<p>Spieltage 14–30 · 05.01.2027 bis 27.04.2027 · 19:00, 20:00, 21:00 und 20:30 Uhr</p>
<div class="notice"><strong>Abgrenzung:</strong> Diese eigenständige Planung enthält ausschließlich Spieltage 14–30. Der bestehende Plan und die festgelegten Regeln für 2026 wurden nicht verändert. Quante ist 2027 mit drei Doppel- und einem Einzel-Einsatz eingeplant.</div></header>
<section class="card"><h2>Spieltermine und Paarungen</h2><div class="table-wrap"><table><thead><tr><th>Spieltag</th><th>Datum</th><th>19:00</th><th>20:00</th><th>21:00</th><th>Platz 2 · 20:30</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="legend">Ungerade Spieltage: Doppel auf Platz 2. Gerade Spieltage: Einzel auf Platz 2. Die Wünsche zu Einzel/Doppel werden soweit mit den verfügbaren Spieltypen vereinbar berücksichtigt.</p></section>
<section class="card"><h2>Einsatzübersicht 2027</h2><div class="table-wrap"><table class="stats"><thead><tr><th>Spieler</th><th>Einsätze</th><th>Einzel</th><th>Doppel</th><th>Doppelanteil</th><th>Wunsch Doppel</th></tr></thead><tbody>{''.join(stat_rows)}</tbody></table></div>
<p>Quoten sind Präferenzen, keine Garantie; der feste Spielrhythmus, Abwesenheiten und das wechselnde Einzel-/Doppelformat begrenzen die erreichbaren Anteile.</p></section>
<footer>Eigenständiger 2027-Spielplan · Quelldaten: Saisontermine 14–30 aus der Arbeitsmappe</footer>
</main></body></html>'''


def render_matching_2026(schedule, games, doubles):
    colors = {
        "Beumer": "#bfdbfe", "Dedores": "#fecaca", "Hansmann": "#fef08a", "Heyn": "#bbf7d0",
        "Hinz": "#fed7aa", "Kissner": "#e9d5ff", "Knust": "#e2e8f0", "Kuhlhoff": "#a5f3fc",
        "Marschollek": "#fbcfe8", "Mönning": "#c7d2fe", "Nolte": "#d9f99d", "Prodehl": "#99f6e4", "Quante": "#fde68a",
        "Redieker": "#fecdd3", "Rumpf": "#fed7aa", "Trojanski": "#cbd5e1", "Van de Looh": "#bae6fd",
        "Weber": "#ddd6fe", "Wojtanowitsch": "#a7f3d0",
    }

    def badge(player):
        color = colors.get(player, "#e2e8f0")
        return f'<button class="player-badge" data-player="{html.escape(player)}" style="background:{color};border-color:{color}">{html.escape(player)}</button>'

    rows = []
    for match in schedule:
        day, when = match["day"], match["date"]
        singles = match["singles"]
        cells = []
        for pair in (singles[:1], singles[1:2], singles[2:3]):
            cells.append("<br>".join(f"{badge(a)} <span class='vs'>vs</span> {badge(b)}" for a, b in pair))
        if match["teams"]:
            a, b = match["teams"]
            court = f"{badge(a[0])} {badge(a[1])}<br><span class='vs'>vs</span><br>{badge(b[0])} {badge(b[1])}"
        else:
            a, b = singles[3]
            court = f"{badge(a)} <span class='vs'>vs</span> {badge(b)}"
        players = sorted({p for pair in singles for p in pair} | ({p for team in match["teams"] for p in team} if match["teams"] else set()))
        rows.append(
            f'<tr data-players="|{"|".join(html.escape(p) for p in players)}|">'
            f'<td class="date"><b>#{day}</b><span>{when.strftime("%a, %d.%m.%Y")}</span></td>'
            + "".join(f"<td>{cell}</td>" for cell in cells)
            + f"<td>{court}</td></tr>"
        )

    stats = []
    for player in PLAYERS:
        total, dcount = games[player], doubles[player]
        share = round(100 * dcount / total) if total else 0
        ratio = RATIOS.get(player)
        target = f"{round(ratio * 100)}% Doppel" if ratio is not None else "Keine Quote festgelegt"
        stats.append(f"<tr><td>{badge(player)}</td><td>{total}</td><td>{total-dcount}</td><td>{dcount}</td><td>{share}%</td><td>{target}</td></tr>")

    rules = [
        "Beumer: 50% Einzel / 50% Doppel; abwesend am 02.03.2027 (#22).",
        "Dedores: ausschließlich Einzel.",
        "Allgemein: Für Spieler ohne Zeit-Sonderregel werden die Einsätze möglichst gleichmäßig auf 19:00, 20:00, 21:00 und 20:30 Uhr verteilt.",
        "Hansmann: ca. 70% Einzel / 30% Doppel.",
        "Heyn: 75% Einzel / 25% Doppel.",
        "Hinz: 50% Einzel / 50% Doppel; abwesend am 27.04.2027 (#30).",
        "Kissner: ausschließlich Einzel. Kuhlhoff: ausschließlich Einzel; abwesend am 05.01.2027 (#14) und 02.02.2027 (#18). Mönning: ausschließlich Einzel; abwesend am 05.01.2027 (#14) und 12.01.2027 (#15). Nolte und Wojtanowitsch: ausschließlich Einzel.",
        "Marschollek: ca. 90% Doppel; abwesend am 19.01.2027 (#16) und 16.03.2027 (#24).",
        "Prodehl: ca. 60% Doppel. Trojanski: Einzel, mindestens ein Spieltag Pause; abwesend am 16.02.2027 (#20).",
        "Van de Looh: Einzel, mindestens drei Spieltage Pause. Knust nimmt ab 2027 teil.",
        "Quante: drei Doppel-Einsätze und ein Einzel-Einsatz in der zweiten Saisonhälfte 2027.",
    ]
    player_chips = "".join(
        f'<button class="player-badge" data-filter="{html.escape(p)}" data-player="{html.escape(p)}" style="background:{colors[p]};border-color:{colors[p]}">{html.escape(p)}</button>'
        for p in PLAYERS
    )
    rules_html = "".join(f"<li>{html.escape(rule)}</li>" for rule in rules)

    return f'''<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tennis-Spielplan zweite Saisonhälfte 2027</title>
<script src="https://cdn.tailwindcss.com"></script>
<style>
body{{font-family:Inter,Arial,sans-serif;background:#f3f4f6;color:#1f2937}}.player-badge{{display:inline-block;border:1px solid;border-radius:5px;padding:2px 6px;font-size:11px;font-weight:700;color:#111827;white-space:nowrap;cursor:pointer}}.vs{{font-size:10px;color:#9ca3af}}.schedule td{{vertical-align:middle}}.date span{{display:block;font-size:11px;white-space:nowrap}}.filter-chip{{border:0;background:none;padding:0}}tr.dimmed{{opacity:.23}}tr[hidden]{{display:none}}
@media(max-width:767px){{.player-badge{{font-size:10px;padding:2px 4px}}.date span{{font-size:9px}}.schedule td{{padding:4px 3px!important}}}}
@media print{{.no-print{{display:none!important}}body{{background:white!important}}}}
</style></head><body class="min-h-screen p-2 md:p-3">
<div class="max-w-[98%] mx-auto">
<div class="bg-white border border-emerald-200 rounded-lg px-3 py-2 mb-2.5 shadow-sm text-xs flex flex-wrap justify-between items-center gap-2 no-print">
<div class="flex items-center gap-3 text-gray-700 font-medium"><span>📊 <b>17</b> Spieltage · Saison 2026/2027</span><span>•</span><span>👥 <b>19</b> Spieler im Kader 2027</span><span>•</span><span class="text-emerald-800 font-semibold">⭐ 2. Saisonhälfte · Spieltage 14–30</span></div>
<div class="flex items-center gap-2"><a href="index.html" class="bg-blue-100 hover:bg-blue-200 text-blue-800 px-2.5 py-1.5 rounded-lg text-xs font-semibold border border-blue-300">↩ Spielplan 2026</a><button onclick="window.print()" class="bg-gray-100 hover:bg-gray-200 px-2.5 py-1.5 rounded-lg border">🖨️ Drucken</button></div></div>
<div class="bg-white border border-gray-200 rounded-lg p-2.5 mb-2.5 shadow-sm no-print"><div class="font-bold text-xs uppercase tracking-wider text-gray-700 mb-2">Spieler anklicken zum Filtern</div><button class="filter-chip" data-filter="ALL"><span class="player-badge" style="background:#111827;color:white;border-color:#111827">Alle</span></button> {player_chips}</div>
<div class="bg-white border border-gray-200 rounded-lg shadow-sm overflow-x-auto mb-2.5"><table id="schedule-table" class="schedule w-full text-left border-collapse text-xs table-auto"><thead><tr class="bg-gray-100 text-gray-600 uppercase text-[10px] tracking-wider"><th class="py-2 px-1">Spieltag / Datum</th><th class="py-2 px-1.5">19:00 Uhr</th><th class="py-2 px-1.5">20:00 Uhr</th><th class="py-2 px-1.5">21:00 Uhr</th><th class="py-2 px-1.5">Doppel / Einzel (20:30)</th></tr></thead><tbody class="divide-y divide-gray-200">{''.join(rows)}</tbody></table></div>
<div class="no-print bg-white border border-emerald-200 rounded-lg p-3 mb-2.5 shadow-sm"><h2 class="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-2">📊 Spieler-Statistik-Matrix (2027)</h2><div class="overflow-x-auto"><table class="w-full text-left border-collapse text-xs"><thead><tr class="bg-emerald-800 text-white"><th class="p-2">Spieler</th><th class="p-2">Gesamt</th><th class="p-2">Einzel</th><th class="p-2">Doppel</th><th class="p-2">Doppel-Anteil</th><th class="p-2">Wunsch</th></tr></thead><tbody class="divide-y divide-gray-100">{''.join(stats)}</tbody></table></div></div>
<div class="no-print bg-white border border-emerald-200 rounded-lg p-3 shadow-sm"><h2 class="text-xs font-bold uppercase tracking-wider text-emerald-800 mb-2">📋 Aktive Spielerregeln & Abwesenheiten · 2027</h2><ul class="list-disc list-inside text-gray-600 text-[11px] space-y-1">{rules_html}</ul><p class="mt-3 text-[11px] text-gray-500">Die 2026er Regeln und Spieltermine bleiben unverändert. Ungerade Spieltage: Doppel auf Platz 2; gerade Spieltage: Einzel.</p></div>
</div><script>
document.querySelectorAll('[data-filter]').forEach(button=>button.addEventListener('click',()=>{{const player=button.dataset.filter;document.querySelectorAll('#schedule-table tbody tr').forEach(row=>{{const match=player==='ALL'||row.dataset.players.includes('|'+player+'|');row.hidden=!match;row.classList.toggle('dimmed',!match)}})}}));
</script></body></html>'''


def render_from_2026_template(schedule, games, doubles):
    template_path = Path(__file__).with_name("index.html")
    page = template_path.read_text(encoding="utf-8")

    matches_data = []
    for match in schedule:
        singles = match["singles"]
        day = match["day"]
        court2_type = "doppel" if day % 2 else "einzel"
        item = {
            "spieltag": day,
            "date": match["date"].isoformat(),
            "court2_type": court2_type,
            "p1": {"p1": singles[0][0], "p2": singles[0][1], "time": "19:00"},
            "p2": {"p1": singles[1][0], "p2": singles[1][1], "time": "20:00"},
            "p3": {"p1": singles[2][0], "p2": singles[2][1], "time": "21:00"},
            "status": "Geplant",
        }
        if court2_type == "doppel":
            item["doppel"] = {"team1": list(match["teams"][0]), "team2": list(match["teams"][1]), "time": "20:30"}
        else:
            item["doppel"] = {"p1": singles[3][0], "p2": singles[3][1], "time": "20:30"}
        matches_data.append(item)

    rules = {
        "Beumer": ["Wunsch nach 50% Einzel und 50% Doppel.", "Abwesend am 02.03.2027 (Spieltag 22)."],
        "Dedores": ["Spielt ausschließlich Einzel.", "Abwesend am 19.01.2027 (#16), 26.01.2027 (#17), 16.02.2027 (#20), 23.02.2027 (#21), 23.03.2027 (#25), 30.03.2027 (#26) und 13.04.2027 (#28).", "Bis zu 7 Einsätze reichen."],
        "Hansmann": ["Wunsch nach ca. 70% Einzel und 30% Doppel."],
        "Heyn": ["Wunsch nach 70% Einzel und 30% Doppel.", "Abwesend am 12.01.2027 (Spieltag 15), 09.02.2027 (Spieltag 19), 09.03.2027 (Spieltag 23), 30.03.2027 (Spieltag 26), 13.04.2027 (Spieltag 28) und 27.04.2027 (Spieltag 30)."],
        "Hinz": ["Wunsch nach 50% Einzel und 50% Doppel.", "Abwesend am 27.04.2027 (Spieltag 30)."],
        "Kissner": ["Spielt ausschließlich Einzel."],
        "Knust": ["Nimmt ab 2027 teil."],
        "Kuhlhoff": ["Spielt ausschließlich Einzel.", "Abwesend am 05.01.2027 (Spieltag 14) und 02.02.2027 (Spieltag 18)."],
        "Marschollek": ["Wunsch nach ca. 90% Doppel.", "Abwesend am 19.01.2027 (Spieltag 16) und 16.03.2027 (Spieltag 24)."],
        "Mönning": ["Spielt ausschließlich Einzel.", "Abwesend am 05.01.2027 (Spieltag 14) und 12.01.2027 (Spieltag 15)."],
        "Nolte": ["Spielt ausschließlich Einzel.", "Abwesend am 02.03.2027 (#22), 23.03.2027 (#25), 20.04.2027 (#29) und 27.04.2027 (#30)."],
        "Prodehl": ["Wunsch nach ca. 60% Doppel."],
        "Quante": ["Genau drei Doppel-Einsätze und ein Einzel-Einsatz in der zweiten Saisonhälfte 2027."],
        "Redieker": ["Wunsch nach 80% Einzel und 20% Doppel."],
        "Rumpf": ["Spielt ausschließlich Einzel."],
        "Trojanski": ["Spielt ausschließlich Einzel.", "Mindestens ein Spieltag Pause zwischen Einsätzen.", "Abwesend am 16.02.2027 (Spieltag 20)."],
        "Van de Looh": ["Spielt ausschließlich Einzel.", "Mindestens drei Spieltage Pause zwischen Einsätzen."],
        "Weber": ["Keine besondere Einzel-/Doppelquote festgelegt."],
        "Wojtanowitsch": ["Spielt ausschließlich Einzel."],
        "Allgemeine Regeln": ["Faire Verteilung der Einsätze innerhalb der zweiten Saisonhälfte.", "Spielzeiten 19:00, 20:00, 21:00 und 20:30 werden ohne Sondervorgabe je Spieler möglichst gleichmäßig verteilt.", "Doppelte Begegnungen und Partnerschaften werden möglichst vermieden."],
    }
    stats = {}
    for player in PLAYERS:
        total = games[player]
        dcount = doubles[player]
        ecount = total - dcount
        stats[player] = {
            "einzel": ecount,
            "doppel": dcount,
            "total": total,
            "ratio": round(100 * dcount / total) if total else 0,
            "kosten": round(ecount * 0.5 + dcount * (1.5 / 4.0), 2),
        }

    def replace_assignment(source, name, next_name, value):
        pattern = rf"const {name} = .*?;\s*const {next_name} ="
        replacement = f"const {name} = {json.dumps(value, ensure_ascii=False, indent=4)};\n        const {next_name} ="
        updated, count = re.subn(pattern, replacement, source, count=1, flags=re.S)
        if count != 1:
            raise RuntimeError(f"Could not replace {name} data in index.html")
        return updated

    page = page.replace('"van de Loo": { bg: \'#bae6fd\', text: \'#111827\', border: \'#38bdf8\' }', '"Van de Looh": { bg: \'#bae6fd\', text: \'#111827\', border: \'#38bdf8\' }')
    page = re.sub(
        r"formatPlayerBadge\(([^,\n]+), (m\.status === 'Abgeschlossen')\)",
        lambda match: f"formatPlayerBadge({match.group(1)}, {match.group(2)}, getSlotPlayers(m.{match.group(1).split('.')[1]}))",
        page,
    )
    page = page.replace(
        "function formatPlayerBadge(player, isFinished) {",
        "function formatPlayerBadge(player, isFinished, matchPlayers = []) {",
    )
    page = page.replace(
        """let opacityClass = '';\n                    if (currentFilter.value !== 'ALL' && !isFiltered) {\n                        opacityClass = 'opacity-30';\n                    }""",
        """const opacity = currentFilter.value === 'ALL' || isFiltered\n                        ? 1\n                        : (matchPlayers.includes(currentFilter.value) ? 0.7 : 0.4);""",
    )
    page = page.replace("color: ${colors.text};\"", "color: ${colors.text}; opacity: ${opacity} !important;\"")
    page = page.replace("shadow-2xs transition ${opacityClass}", "shadow-2xs transition")
    page = page.replace(" opacity-25", "")
    page = page.replace("                    formatPlayerBadge,\n                    getRowClass,", "                    formatPlayerBadge,\n                    getSlotPlayers,\n                    getRowClass,")
    page = replace_assignment(page, "matchesData", "playerRules", matches_data)
    page = replace_assignment(page, "playerRules", "playerStats", rules)
    page = replace_assignment(page, "playerStats", "topfA", stats)
    pattern = r"const topfA = .*?;\s*const \{ createApp"
    replacement = f"const topfA = {json.dumps(['Prodehl', 'Beumer', 'Heyn'], ensure_ascii=False)};\n\n        const {{ createApp"
    page, count = re.subn(pattern, replacement, page, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError("Could not replace topfA data in index.html")

    page = re.sub(r"<title>.*?</title>", "<title>Tennis-Spielplan zweite Saisonhälfte 2027</title>", page, count=1)
    page = page.replace("<b>13</b> Spieltage (Saison 2026/2027)", "<b>17</b> Spieltage (2. Saisonhälfte 2027)")
    page = page.replace("Nächster Spieltag: <b>06.10.2026</b> (#1)", "Nächster Spieltag: <b>05.01.2027</b> (#14)")
    heading = (
        '<h1>GW Halle 2026<a href="spielplan_2027.html" class="year-switch no-print" '
        'title="Zum Spielplan 2027 wechseln" aria-label="Zum Spielplan 2027 wechseln">↗ 2027</a></h1>'
    )
    replacement = (
        '<h1>GW Halle 2027<a href="index.html" class="year-switch no-print" '
        'title="Zum Spielplan 2026 wechseln" aria-label="Zum Spielplan 2026 wechseln">↗ 2026</a></h1>'
    )
    count = page.count(heading)
    if count != 1:
        raise RuntimeError("Could not replace year-switch heading in index.html")
    page = page.replace(heading, replacement)
    page = page.replace("tennis_spielplan_statistik_2026_2027.csv", "tennis_spielplan_statistik_2027_zweite_haelfte.csv")
    page = page.replace("tennis_spielplan_gesamtsaison_2026_2027.ics", "tennis_spielplan_2027_zweite_haelfte.ics")
    page = page.replace("Stand: 21.09.2026", "Stand: 01.10.2026")
    return page


if __name__ == "__main__":
    schedule = apply_manual_overrides(generate())
    games, doubles = validate(schedule)
    output = Path(__file__).with_name("spielplan_2027.html")
    generated_html = render_from_2026_template(schedule, games, doubles)
    output.write_text(generated_html, encoding="utf-8")

    # Keep the established 2026 page intact except for the reciprocal navigation link.
    main_page = Path(__file__).with_name("index.html")
    main_html = main_page.read_text(encoding="utf-8")
    link = '''                <a href="spielplan_2027.html" class="no-print bg-blue-100 hover:bg-blue-200 text-blue-800 px-2.5 py-1.5 rounded-lg text-xs font-semibold transition border border-blue-300 flex items-center gap-1 shadow-sm" title="Spielplan zweite Saisonhälfte 2027 öffnen">
                    <span>📅 Spielplan 2027</span>
                </a>
'''
    if 'href="spielplan_2027.html"' not in main_html:
        anchor = '            <div class="flex items-center gap-2">\n                <button @click="printPage()"'
        if anchor not in main_html:
            raise RuntimeError("Could not locate navigation area in index.html")
        main_html = main_html.replace(anchor, '            <div class="flex items-center gap-2">\n' + link + '                <button @click="printPage()"', 1)
        main_page.write_text(main_html, encoding="utf-8")
    print(f"Erstellt: {output.name} ({len(schedule)} Spieltage)")
    for p in PLAYERS:
        print(f"{p}: {games[p]} Spiele, davon {doubles[p]} Doppel")
