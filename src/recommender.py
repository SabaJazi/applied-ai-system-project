from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
import csv

STATE_DEEP_FOCUS = "Deep Focus"
STATE_AEROBIC_STEADY = "Aerobic Steady-State"
STATE_HIIT_PEAK = "HIIT Peak"
STATE_ACTIVE_RECOVERY = "Active Recovery"

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


@dataclass
class ActivityInput:
    """Biometric input used by the primary activity-state classifier."""
    heart_rate_bpm: float
    velocity_mps: float


@dataclass
class ActivityStateResult:
    """Classifier output containing inferred state and confidence."""
    state: str
    confidence: float
    rationale: str


@dataclass
class SongConstraints:
    """State-dependent target values used to adapt song ranking."""
    min_valence: float
    max_tempo_bpm: float
    min_acousticness: float
    target_energy: float


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


def classify_activity_state(activity_input: ActivityInput) -> ActivityStateResult:
    """
    Rule-based baseline classifier for activity state.

    This baseline can later be swapped for a trained RF/GBM model while keeping
    the same output contract.
    """
    hr = _safe_float(activity_input.heart_rate_bpm, 0.0)
    velocity = _safe_float(activity_input.velocity_mps, 0.0)

    # Priority edge case requested by design:
    # high heart rate + low velocity likely indicates stress/focus state.
    if hr >= 145.0 and velocity < 1.2:
        return ActivityStateResult(
            state=STATE_DEEP_FOCUS,
            confidence=0.85,
            rationale=f"High HR ({hr:.1f}) with low velocity ({velocity:.2f})",
        )

    # High exertion movement.
    if hr >= 160.0 and velocity >= 2.8:
        return ActivityStateResult(
            state=STATE_HIIT_PEAK,
            confidence=0.93,
            rationale=f"Very high HR ({hr:.1f}) and high velocity ({velocity:.2f})",
        )

    # Recovery: lower movement and lower cardiac load.
    if hr < 110.0 and velocity < 1.3:
        return ActivityStateResult(
            state=STATE_ACTIVE_RECOVERY,
            confidence=0.88,
            rationale=f"Low HR ({hr:.1f}) and gentle velocity ({velocity:.2f})",
        )

    # Moderate sustained physical effort.
    if 110.0 <= hr < 160.0 and 1.2 <= velocity < 2.8:
        return ActivityStateResult(
            state=STATE_AEROBIC_STEADY,
            confidence=0.81,
            rationale=f"Moderate HR ({hr:.1f}) and steady velocity ({velocity:.2f})",
        )

    # Fallback logic for mixed signals.
    if hr >= 150.0:
        return ActivityStateResult(
            state=STATE_HIIT_PEAK,
            confidence=0.65,
            rationale=f"Elevated HR ({hr:.1f}) dominates ambiguous movement ({velocity:.2f})",
        )

    return ActivityStateResult(
        state=STATE_AEROBIC_STEADY,
        confidence=0.60,
        rationale=f"Defaulting to steady-state for HR {hr:.1f}, velocity {velocity:.2f}",
    )


def map_state_to_constraints(state: str) -> SongConstraints:
    """Map inferred activity state to target song constraints."""
    if state == STATE_ACTIVE_RECOVERY:
        return SongConstraints(
            min_valence=0.70,
            max_tempo_bpm=100.0,
            min_acousticness=0.50,
            target_energy=0.35,
        )
    if state == STATE_DEEP_FOCUS:
        return SongConstraints(
            min_valence=0.45,
            max_tempo_bpm=115.0,
            min_acousticness=0.35,
            target_energy=0.45,
        )
    if state == STATE_HIIT_PEAK:
        return SongConstraints(
            min_valence=0.55,
            max_tempo_bpm=190.0,
            min_acousticness=0.00,
            target_energy=0.92,
        )

    # STATE_AEROBIC_STEADY default mapping.
    return SongConstraints(
        min_valence=0.50,
        max_tempo_bpm=140.0,
        min_acousticness=0.20,
        target_energy=0.65,
    )


def _score_constraints(song: Dict[str, Any], constraints: SongConstraints) -> Tuple[float, List[str]]:
    """Compute additional score terms from state-derived song constraints."""
    score = 0.0
    reasons: List[str] = []

    valence = _safe_float(song.get("valence", 0.5), 0.5)
    if valence >= constraints.min_valence:
        score += 0.7
        reasons.append(f"Constraint valence >= {constraints.min_valence:.2f}: pass (+0.70)")
    else:
        reasons.append(f"Constraint valence >= {constraints.min_valence:.2f}: miss (+0.00)")

    tempo = _safe_float(song.get("tempo_bpm", 120.0), 120.0)
    if tempo <= constraints.max_tempo_bpm:
        score += 0.7
        reasons.append(f"Constraint tempo <= {constraints.max_tempo_bpm:.0f}: pass (+0.70)")
    else:
        reasons.append(f"Constraint tempo <= {constraints.max_tempo_bpm:.0f}: miss (+0.00)")

    acousticness = _safe_float(song.get("acousticness", 0.5), 0.5)
    if acousticness >= constraints.min_acousticness:
        score += 0.7
        reasons.append(f"Constraint acousticness >= {constraints.min_acousticness:.2f}: pass (+0.70)")
    else:
        reasons.append(f"Constraint acousticness >= {constraints.min_acousticness:.2f}: miss (+0.00)")

    energy = _safe_float(song.get("energy", 0.5), 0.5)
    energy_fit = max(0.0, 1.0 - abs(energy - constraints.target_energy))
    energy_bonus = energy_fit * 1.2
    score += energy_bonus
    reasons.append(
        f"State target energy ({energy:.2f} vs {constraints.target_energy:.2f}): (+{energy_bonus:.2f})"
    )

    return score, reasons


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


def recommend_songs_from_activity(
    user_prefs: Dict,
    songs: List[Dict],
    activity_input: ActivityInput,
    k: int = 5,
) -> Tuple[ActivityStateResult, SongConstraints, List[Tuple[Dict, float, str]]]:
    """
    Classifier-first recommendation pipeline.

    1) Classify activity state from BPM and velocity.
    2) Map state to dynamic song targets.
    3) Produce top-k songs with state-aware scoring.
    """
    state_result = classify_activity_state(activity_input)
    constraints = map_state_to_constraints(state_result.state)

    scored_songs: List[Tuple[Dict, float, str]] = []
    for song in songs:
        base_score, base_reasons = score_song(user_prefs, song)
        state_score, state_reasons = _score_constraints(song, constraints)
        total_score = base_score + state_score
        explanation = " | ".join(
            [
                f"Activity state: {state_result.state} ({state_result.confidence:.2f})",
                f"State rationale: {state_result.rationale}",
            ]
            + base_reasons
            + state_reasons
        )
        scored_songs.append((song, total_score, explanation))

    scored_songs.sort(key=lambda x: x[1], reverse=True)
    return state_result, constraints, scored_songs[:k]
