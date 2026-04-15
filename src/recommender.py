from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import csv

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    popularity: int = 50
    release_decade: int = 2010
    mood_tags: str = ""
    instrumentalness: float = 0.5
    liveness: float = 0.5
    speechiness: float = 0.2
    musical_key: str = "C"
    time_signature: int = 4

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    preferred_decades: Optional[List[int]] = None
    preferred_mood_tags: Optional[List[str]] = None
    speechiness_tolerance: float = 0.35
    preferred_time_signature: Optional[int] = None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_song_dict(song: Song) -> Dict[str, Any]:
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
        "popularity": song.popularity,
        "release_decade": song.release_decade,
        "mood_tags": song.mood_tags,
        "instrumentalness": song.instrumentalness,
        "liveness": song.liveness,
        "speechiness": song.speechiness,
        "musical_key": song.musical_key,
        "time_signature": song.time_signature,
    }


def _extract_user_dict(user: UserProfile) -> Dict[str, Any]:
    return {
        "favorite_genre": user.favorite_genre,
        "favorite_mood": user.favorite_mood,
        "target_energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
        "preferred_decades": user.preferred_decades,
        "preferred_mood_tags": user.preferred_mood_tags,
        "speechiness_tolerance": user.speechiness_tolerance,
        "preferred_time_signature": user.preferred_time_signature,
    }


def _infer_preferred_decades(user_prefs: Dict[str, Any]) -> List[int]:
    explicit = user_prefs.get("preferred_decades")
    if explicit:
        return [_safe_int(decade) for decade in explicit]

    mood_decade_map = {
        "nostalgic": [1970, 1980, 1990],
        "reflective": [1990, 2000],
        "dark": [1990, 2000],
        "euphoric": [2000, 2010, 2020],
        "energetic": [2010, 2020],
        "focused": [2010, 2020],
        "chill": [2000, 2010],
        "happy": [2010, 2020],
    }
    return mood_decade_map.get(user_prefs.get("favorite_mood", ""), [2000, 2010])


def _infer_target_tags(user_prefs: Dict[str, Any]) -> List[str]:
    explicit_tags = user_prefs.get("preferred_mood_tags")
    if explicit_tags:
        return [str(tag).strip().lower() for tag in explicit_tags if str(tag).strip()]

    mood_to_tags = {
        "happy": ["bright", "feel-good", "uplifting", "danceable"],
        "chill": ["calm", "study", "laid-back", "soft"],
        "intense": ["driving", "power", "adrenaline", "high-energy"],
        "focused": ["study", "minimal", "concentration", "flow"],
        "moody": ["brooding", "urban", "late-night", "dreamy"],
        "serene": ["peaceful", "ambient", "still", "gentle"],
        "energetic": ["workout", "hype", "fast", "pumped"],
        "nostalgic": ["retro", "memory", "analog", "melancholy"],
        "euphoric": ["peak", "festival", "anthemic", "shimmer"],
        "reflective": ["introspective", "lyrical", "storytelling", "soulful"],
        "dark": ["heavy", "ominous", "shadow", "industrial"],
        "uplifting": ["optimistic", "inspiring", "rise", "hopeful"],
        "warm": ["cozy", "organic", "golden", "sunset"],
        "aggressive": ["mosh", "furious", "hard-hitting", "relentless"],
    }
    return mood_to_tags.get(user_prefs.get("favorite_mood", ""), [])


def _infer_target_liveness(user_prefs: Dict[str, Any]) -> float:
    mood_liveness_map = {
        "serene": 0.20,
        "chill": 0.28,
        "focused": 0.30,
        "nostalgic": 0.35,
        "happy": 0.45,
        "reflective": 0.40,
        "euphoric": 0.62,
        "energetic": 0.68,
        "intense": 0.72,
        "aggressive": 0.75,
    }
    return mood_liveness_map.get(user_prefs.get("favorite_mood", ""), 0.45)

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        """Initialize the recommender with a list of songs."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return up to k recommended songs for the given user profile."""
        user_prefs = _extract_user_dict(user)
        ranked = sorted(
            self.songs,
            key=lambda song: score_song(user_prefs, _extract_song_dict(song))[0],
            reverse=True,
        )
        return ranked[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a short explanation for why a song was recommended."""
        user_prefs = _extract_user_dict(user)
        _, reasons = score_song(user_prefs, _extract_song_dict(song))
        return " | ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load songs from CSV and convert numeric fields to Python numeric types."""
    songs = []
    numeric_fields = {
        'id': int,
        'energy': float,
        'tempo_bpm': int,
        'valence': float,
        'danceability': float,
        'acousticness': float,
        'popularity': int,
        'release_decade': int,
        'instrumentalness': float,
        'liveness': float,
        'speechiness': float,
        'time_signature': int,
    }
    
    try:
        with open(csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert numeric strings to their proper types
                for field, field_type in numeric_fields.items():
                    if field in row:
                        row[field] = field_type(row[field])
                songs.append(row)
        print(f"Loaded {len(songs)} songs from {csv_path}")
        return songs
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found.")
        return []
    except Exception as e:
        print(f"Error loading songs: {e}")
        return []

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return score plus reason strings."""
    score = 0.0
    reasons = []
    
    # Genre match: +1.0 point (half importance)
    if song.get('genre') == user_prefs.get('favorite_genre'):
        score += 1.0
        reasons.append(f"Genre match: {song['genre']} (+1.0)")
    
    # Mood match: +1.0 point
    if song.get('mood') == user_prefs.get('favorite_mood'):
        score += 1.0
        reasons.append(f"Mood match: {song['mood']} (+1.0)")
    
    # Energy closeness (1.0 = exact match, 0.0 = maximum difference)
    target_energy = user_prefs.get('target_energy', 0.5)
    song_energy = float(song.get('energy', 0.5))
    energy_closeness = 1.0 - abs(song_energy - target_energy)
    energy_score = energy_closeness * 3.0
    score += energy_score
    reasons.append(f"Energy closeness ({song_energy:.2f} vs {target_energy:.2f}): {energy_closeness:.2f} (+{energy_score:.2f})")
    
    # Acousticness match to preference
    likes_acoustic = user_prefs.get('likes_acoustic', False)
    song_acousticness = float(song.get('acousticness', 0.5))
    if likes_acoustic:
        acoustic_score = song_acousticness * 1.0
        reasons.append(f"Acoustic preference: {song_acousticness:.2f} (+{acoustic_score:.2f})")
    else:
        acoustic_score = (1.0 - song_acousticness) * 1.0
        reasons.append(f"Electronic preference: {acoustic_score:.2f} (+{acoustic_score:.2f})")
    score += acoustic_score

    # Popularity contributes in normalized form to prevent domination over style features.
    popularity = _safe_int(song.get('popularity', 50), 50)
    popularity_norm = max(0.0, min(1.0, popularity / 100.0))
    popularity_score = popularity_norm * 1.5
    score += popularity_score
    reasons.append(f"Popularity ({popularity}/100): (+{popularity_score:.2f})")

    # Era proximity score based on nearest preferred decade.
    preferred_decades = _infer_preferred_decades(user_prefs)
    song_decade = _safe_int(song.get('release_decade', 2010), 2010)
    nearest_decade_gap = min(abs(song_decade - decade) for decade in preferred_decades)
    decade_closeness = max(0.0, 1.0 - (nearest_decade_gap / 60.0))
    decade_score = decade_closeness * 1.4
    score += decade_score
    reasons.append(
        f"Era fit ({song_decade}s vs prefs {preferred_decades}): {decade_closeness:.2f} (+{decade_score:.2f})"
    )

    # Tag overlap ratio (Jaccard-like) rewards semantic mood alignment.
    target_tags = set(_infer_target_tags(user_prefs))
    song_tags = {
        tag.strip().lower() for tag in str(song.get('mood_tags', '')).split('|') if tag.strip()
    }
    if target_tags:
        overlap = len(target_tags & song_tags)
        union = len(target_tags | song_tags)
        tag_similarity = overlap / union if union else 0.0
    else:
        tag_similarity = 0.0
    tag_score = tag_similarity * 1.6
    score += tag_score
    reasons.append(f"Mood-tag overlap ({tag_similarity:.2f}): (+{tag_score:.2f})")

    # Instrumentalness reward shifts with acoustic preference.
    instrumentalness = _safe_float(song.get('instrumentalness', 0.5), 0.5)
    if likes_acoustic:
        instrumental_score = instrumentalness * 0.9
        reasons.append(f"Instrumental match ({instrumentalness:.2f}): (+{instrumental_score:.2f})")
    else:
        instrumental_score = (1.0 - instrumentalness) * 0.9
        reasons.append(f"Vocal-forward match ({1.0 - instrumentalness:.2f}): (+{instrumental_score:.2f})")
    score += instrumental_score

    # Live-performance feel is matched to mood-specific target liveness.
    target_liveness = _infer_target_liveness(user_prefs)
    song_liveness = _safe_float(song.get('liveness', 0.5), 0.5)
    liveness_closeness = max(0.0, 1.0 - abs(song_liveness - target_liveness))
    liveness_score = liveness_closeness * 0.8
    score += liveness_score
    reasons.append(
        f"Liveness fit ({song_liveness:.2f} vs {target_liveness:.2f}): {liveness_closeness:.2f} (+{liveness_score:.2f})"
    )

    # Penalize excess spoken-word content above user tolerance.
    speechiness = _safe_float(song.get('speechiness', 0.2), 0.2)
    tolerance = max(0.0, min(1.0, _safe_float(user_prefs.get('speechiness_tolerance', 0.35), 0.35)))
    over_tolerance = max(0.0, speechiness - tolerance)
    speechiness_score = max(0.0, 1.0 - (over_tolerance * 2.0)) * 0.9
    score += speechiness_score
    reasons.append(f"Speechiness control ({speechiness:.2f} <= {tolerance:.2f}): (+{speechiness_score:.2f})")

    preferred_time_signature = user_prefs.get('preferred_time_signature')
    if preferred_time_signature is not None:
        song_time_signature = _safe_int(song.get('time_signature', 4), 4)
        if song_time_signature == _safe_int(preferred_time_signature, 4):
            score += 0.4
            reasons.append(f"Time signature match ({song_time_signature}/4): (+0.40)")
        else:
            reasons.append(f"Time signature mismatch ({song_time_signature}/4): (+0.00)")
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return top-k songs sorted by score with a human-readable explanation string."""
    # Score all songs and collect results
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored_songs.append((song, score, explanation))
    
    # Sort by score descending
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k recommendations
    return scored_songs[:k]
