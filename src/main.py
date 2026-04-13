"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {
        "favorite_genre": "pop", 
        "favorite_mood": "happy", 
        "target_energy": 0.8,
        "likes_acoustic": False
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    # Format and display results
    print("\n" + "="*80)
    print("🎵 MUSIC RECOMMENDER RESULTS")
    print("="*80)
    print(f"\nUser Preferences:")
    print(f"  • Genre: {user_prefs['favorite_genre']}")
    print(f"  • Mood: {user_prefs['favorite_mood']}")
    print(f"  • Target Energy: {user_prefs['target_energy']}")
    print(f"  • Likes Acoustic: {user_prefs['likes_acoustic']}")
    print("\n" + "-"*80)
    print(f"Top {len(recommendations)} Recommendations:\n")

    for rank, rec in enumerate(recommendations, 1):
        song, score, explanation = rec
        
        print(f"{rank}. {song['title']}")
        print(f"   Artist: {song['artist']} | Genre: {song['genre']} | Mood: {song['mood']}")
        print(f"   Score: {score:.2f}/5.5")
        
        # Parse and format reasons
        reasons = explanation.split(" | ")
        print(f"   Why:")
        for reason in reasons:
            print(f"      ✓ {reason}")
        print()

    print("="*80 + "\n")


if __name__ == "__main__":
    main()
