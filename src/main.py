"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from textwrap import wrap
from importlib.util import find_spec

from recommender import load_songs, recommend_songs


TABULATE_AVAILABLE = find_spec("tabulate") is not None


USER_PROFILES = {
    "High-Energy Pop": {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
        "likes_acoustic": False,
    },
    "Chill Lofi": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.35,
        "likes_acoustic": True,
    },
    "Deep Intense Rock": {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.95,
        "likes_acoustic": False,
    },
    "Adversarial - High Energy Sad Acoustic": {
        "favorite_genre": "pop",
        "favorite_mood": "sad",
        "target_energy": 0.95,
        "likes_acoustic": True,
    },
    "Adversarial - Chill Max Energy": {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 1.0,
        "likes_acoustic": True,
    },
    "Adversarial - Missing Genre": {
        "favorite_genre": "nonexistent_genre",
        "favorite_mood": "happy",
        "target_energy": 0.70,
        "likes_acoustic": False,
    },
    "Era-Tuned Nostalgic Mix": {
        "favorite_genre": "soul",
        "favorite_mood": "nostalgic",
        "target_energy": 0.55,
        "likes_acoustic": True,
        "preferred_decades": [1970, 1980, 1990],
        "preferred_mood_tags": ["retro", "memory", "analog", "warm"],
        "speechiness_tolerance": 0.28,
        "preferred_time_signature": 4,
    },
    "Modern Festival Driver": {
        "favorite_genre": "edm",
        "favorite_mood": "euphoric",
        "target_energy": 0.92,
        "likes_acoustic": False,
        "preferred_decades": [2010, 2020],
        "preferred_mood_tags": ["festival", "anthemic", "peak", "hype"],
        "speechiness_tolerance": 0.45,
        "preferred_time_signature": 4,
    },
    # "Adversarial - Missing Mood": {
    #     "favorite_genre": "rock",
    #     "favorite_mood": "nonexistent_mood",
    #     "target_energy": 0.80,
    #     "likes_acoustic": False,
    # },
    # "Adversarial - Neutral Energy Midpoint": {
    #     "favorite_genre": "pop",
    #     "favorite_mood": "happy",
    #     "target_energy": 0.50,
    #     "likes_acoustic": False,
    # },
    # "Adversarial - EDM But Acoustic": {
    #     "favorite_genre": "edm",
    #     "favorite_mood": "intense",
    #     "target_energy": 0.90,
    #     "likes_acoustic": True,
    # },
    # "Adversarial - Folk But Electronic": {
    #     "favorite_genre": "folk",
    #     "favorite_mood": "calm",
    #     "target_energy": 0.20,
    #     "likes_acoustic": False,
    # },
    # "Adversarial - Energy Too High": {
    #     "favorite_genre": "pop",
    #     "favorite_mood": "happy",
    #     "target_energy": 1.50,
    #     "likes_acoustic": False,
    # },
    # "Adversarial - Energy Too Low": {
    #     "favorite_genre": "rock",
    #     "favorite_mood": "sad",
    #     "target_energy": -0.30,
    #     "likes_acoustic": True,
    # },
    # "Adversarial - Minimal Signal": {
    #     "favorite_genre": "",
    #     "favorite_mood": "",
    #     "target_energy": 0.90,
    #     "likes_acoustic": False,
    # },
    # "Adversarial - Pop Chill Conflict": {
    #     "favorite_genre": "pop",
    #     "favorite_mood": "chill",
    #     "target_energy": 0.90,
    #     "likes_acoustic": False,
    # },
    # "Adversarial - Tie Heavy Rock": {
    #     "favorite_genre": "rock",
    #     "favorite_mood": "intense",
    #     "target_energy": 0.90,
    #     "likes_acoustic": False,
    # },
}


def _render_ascii_table(headers, rows):
    """Render a plain ASCII table for terminals without external dependencies."""
    string_rows = [[str(cell) for cell in row] for row in rows]
    widths = [len(h) for h in headers]

    for row in string_rows:
        for i, cell in enumerate(row):
            max_line_width = max(len(line) for line in cell.splitlines()) if cell else 0
            widths[i] = max(widths[i], max_line_width)

    divider = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_line = "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |"

    table_lines = [divider, header_line, divider]
    for row in string_rows:
        cell_lines = [cell.splitlines() or [""] for cell in row]
        row_height = max(len(lines) for lines in cell_lines)

        for line_idx in range(row_height):
            line_parts = []
            for col_idx, lines in enumerate(cell_lines):
                line_text = lines[line_idx] if line_idx < len(lines) else ""
                line_parts.append(line_text.ljust(widths[col_idx]))
            table_lines.append("| " + " | ".join(line_parts) + " |")
    table_lines.append(divider)
    return "\n".join(table_lines)


def format_recommendations_table(recommendations):
    """Format recommendations as a readable table including explanation reasons."""
    headers = [
        "Rank",
        "Title",
        "Artist",
        "Genre",
        "Mood",
        "Score",
        "Popularity",
        "Decade",
        "Mood Tags",
        "Instr",
        "Live",
        "Speech",
        "TS",
        "Reasons",
    ]
    rows = []

    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        wrapped_reasons = wrap(explanation, width=58) or [""]
        reasons_cell = "\n".join(wrapped_reasons)
        rows.append(
            [
                rank,
                song["title"],
                song["artist"],
                song["genre"],
                song["mood"],
                f"{score:.2f}",
                song.get("popularity", "-"),
                song.get("release_decade", "-"),
                song.get("mood_tags", "-"),
                f"{song.get('instrumentalness', '-')}",
                f"{song.get('liveness', '-')}",
                f"{song.get('speechiness', '-')}",
                song.get("time_signature", "-"),
                reasons_cell,
            ]
        )

    if TABULATE_AVAILABLE:
        from tabulate import tabulate

        return tabulate(rows, headers=headers, tablefmt="fancy_grid", stralign="left")

    return _render_ascii_table(headers, rows)


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Pick one profile to run in the CLI.
    # active_profile_name = "High-Energy Pop"
    active_profile_name = "Era-Tuned Nostalgic Mix"

    user_prefs = USER_PROFILES[active_profile_name]

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # Format and display results
    print("\n" + "="*80)
    print("🎵 MUSIC RECOMMENDER RESULTS")
    print("="*80)
    print(f"Profile: {active_profile_name}")
    print(f"\nUser Preferences:")
    print(f"  • Genre: {user_prefs['favorite_genre']}")
    print(f"  • Mood: {user_prefs['favorite_mood']}")
    print(f"  • Target Energy: {user_prefs['target_energy']}")
    print(f"  • Likes Acoustic: {user_prefs['likes_acoustic']}")
    print(f"  • Preferred Decades: {user_prefs.get('preferred_decades', 'auto')}")
    print(f"  • Preferred Mood Tags: {user_prefs.get('preferred_mood_tags', 'auto')}")
    print(f"  • Speechiness Tolerance: {user_prefs.get('speechiness_tolerance', 0.35)}")
    print(f"  • Preferred Time Signature: {user_prefs.get('preferred_time_signature', 'any')}")
    print("\n" + "-"*80)
    print(f"Top {len(recommendations)} Recommendations:\n")

    print(format_recommendations_table(recommendations))
    if not TABULATE_AVAILABLE:
        print("\nTip: Install 'tabulate' for prettier tables: pip install tabulate")

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
