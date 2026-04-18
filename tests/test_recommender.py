from src.recommender import (
    ActivityInput,
    Recommender,
    Song,
    UserProfile,
    STATE_ACTIVE_RECOVERY,
    STATE_DEEP_FOCUS,
    STATE_HIIT_PEAK,
    classify_activity_state,
    map_state_to_constraints,
    recommend_songs_from_activity,
)

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


def test_classify_activity_state_high_hr_low_velocity_is_deep_focus():
    result = classify_activity_state(ActivityInput(heart_rate_bpm=152, velocity_mps=0.8))
    assert result.state == STATE_DEEP_FOCUS


def test_classify_activity_state_high_hr_high_velocity_is_hiit():
    result = classify_activity_state(ActivityInput(heart_rate_bpm=172, velocity_mps=3.2))
    assert result.state == STATE_HIIT_PEAK


def test_active_recovery_constraints_match_required_targets():
    constraints = map_state_to_constraints(STATE_ACTIVE_RECOVERY)
    assert constraints.min_valence == 0.70
    assert constraints.max_tempo_bpm == 100.0
    assert constraints.min_acousticness == 0.50


def test_recommend_songs_from_activity_returns_activity_aware_recommendations():
    songs = [
        {
            "id": 1,
            "title": "Calm Horizon",
            "artist": "A",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.34,
            "tempo_bpm": 88,
            "valence": 0.78,
            "danceability": 0.52,
            "acousticness": 0.71,
            "popularity": 50,
            "release_decade": 2010,
            "mood_tags": "calm|study",
            "instrumentalness": 0.60,
            "liveness": 0.30,
            "speechiness": 0.10,
            "musical_key": "C",
            "time_signature": 4,
        },
        {
            "id": 2,
            "title": "Sprint Flame",
            "artist": "B",
            "genre": "edm",
            "mood": "intense",
            "energy": 0.95,
            "tempo_bpm": 170,
            "valence": 0.48,
            "danceability": 0.87,
            "acousticness": 0.05,
            "popularity": 60,
            "release_decade": 2020,
            "mood_tags": "hype|peak",
            "instrumentalness": 0.20,
            "liveness": 0.55,
            "speechiness": 0.30,
            "musical_key": "A",
            "time_signature": 4,
        },
    ]
    user_prefs = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.40,
        "likes_acoustic": True,
    }

    state_result, _, recommendations = recommend_songs_from_activity(
        user_prefs,
        songs,
        ActivityInput(heart_rate_bpm=98, velocity_mps=0.7),
        k=2,
    )

    assert state_result.state == STATE_ACTIVE_RECOVERY
    assert len(recommendations) == 2
    assert recommendations[0][0]["title"] == "Calm Horizon"
    assert "Activity state:" in recommendations[0][2]
