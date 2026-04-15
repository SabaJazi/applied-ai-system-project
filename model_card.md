# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

BeatMatch Buddy 1.0

---

## 2. Intended Use  

This recommender suggests songs from a small catalog based on a simple user profile.
It uses favorite genre, favorite mood, target energy, and acoustic preference.
It is designed for classroom learning and experimentation.
It is not designed for real-world music apps or high-stakes personalization.

---

## 3. How the Model Works  

Each song gets points from four checks.
Genre match gives +1 point.
Mood match gives +1 point.
Energy closeness gives up to +3 points, so energy matters the most.
Acoustic preference gives up to +1 point based on whether the user likes acoustic songs.
I changed the starter logic by lowering genre weight and increasing energy weight.

---

## 4. Data  

The dataset has 18 songs.
Each song has title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.
Genres include pop, lofi, rock, ambient, jazz, indie pop, classical, hip hop, edm, metal, and more.
The dataset is small, so many moods and niche styles are missing.
I did not add or remove rows during this version.

---

## 5. Strengths  

It works well for clear profiles like high-energy pop and chill lofi.
It usually finds songs with the right energy range.
It also reacts in a predictable way when acoustic preference flips.
The top songs often matched my intuition for simple user tastes.

---

## 6. Limitations and Bias 

One bias is that energy can dominate the ranking.
Because energy has the biggest weight, songs like Gym Hero keep appearing for many high-energy users.
The model also uses exact genre matching, so pop and indie pop are treated as different even when they are related.
This can create repeated recommendations and small filter bubbles.

---

## 7. Evaluation  

I tested six profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, High Energy Sad Acoustic, Chill Max Energy, and Missing Genre.
For each one, I reviewed the top five songs and checked genre, mood, energy, and acoustic fit.
I compared profile pairs to see what changed and why.
A surprising pattern was that Gym Hero stayed high for many high-energy settings.
That makes sense because high energy and low acousticness are strongly rewarded.

---

## 8. Future Work  

1. Add a diversity rule so top results are not all the same vibe.
2. Use soft genre similarity so related genres can partially match.
3. Add a user control slider for how much energy should matter.

---

## 9. Personal Reflection  

My biggest learning moment was seeing how one weight change could reshape almost every top result.
When I increased energy weight, I finally understood why some songs kept showing up across different users.
AI tools helped me move faster by generating test ideas, explanations, and clean wording for documentation.
I still had to double-check AI suggestions against real outputs, because some suggestions sounded right but did not match what the recommender actually returned.
I was surprised that a simple scoring formula could still feel personal, even without machine learning, just by combining a few preferences.
If I extend this project, I want to add diversity rules, softer genre matching, and better controls so users can tune what matters most.
