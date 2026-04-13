# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works
Major streaming platforms like YouTube and Spotify utilize a multi-stage hybrid pipeline that integrates collaborative filtering, recommending items based on similar user behavior, with content-based filtering, which matches item metadata to a user's established preferences. The process begins with a retrieval stage (candidate generation) to narrow billions of items down to a few hundred using user-item embeddings, followed by a sophisticated ranking stage that scores these candidates based on deep behavioral signals like watch time and engagement. To ensure long-term satisfaction rather than just immediate clicks, the system applies a final layer of re-ranking to enforce business rules, diversity, and content safety, constantly refining itself through continuous learning and A/B testing.

Explain your design in plain language.
What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo 

Algorithm Recipe:

1-We represent each song with:
- Categorical features: genre, mood
- Numeric features: energy, tempo_bpm, valence, danceability, acousticness
2-We build a user preference profile with:
- Preferred genre (e.g., lofi)
- Preferred mood (e.g., chill)
- Numeric targets (p_f) for each numeric feature, each scaled to ([0,1])
3-Compute a per-feature score for each song.

4-Combine feature scores into one total song score using weights.

5-Rank songs by total score and return top (K).

- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
Scoring Rule (one song)
For a numeric feature (f), we score by closeness to the user target, not by “higher is better”:

sf(i)=1−∣xi,f −pf∣

- (x_{i,f}): song (i)'s normalized value for feature (f)
- (p_f): user preference for feature (f)
- Since both are in ([0,1]), (s_f(i)\in[0,1])
- Closer means larger score, exact match gives (1)


- How do you choose which songs to recommend

Ranking Rule (list of songs)

After scoring all songs:

Sort by (S(i)) descending.
Remove songs the user already consumed (if you track history).
Return top (K) songs.
Optional tie-breakers:
Higher genre match first
Then closer energy/tempo
Then diversity rule (avoid too many songs from same artist)


You can include a simple diagram or bullet list if helpful.
![](flowchart_v2.svg)

example of output:
![](recom_Screenshot.png)

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

