# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

One weakness I found is that the scoring can over-prioritize energy similarity compared to other preferences. In practice, users who clearly prefer a specific genre can still receive songs outside that genre if the energy value is closer to their target. The model also uses exact genre matching, so related labels such as "pop" and "indie pop" are treated as completely different categories. This can unintentionally narrow recommendations and create a small filter bubble around numeric features instead of the full musical taste of the user.

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

I tested six user profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, Adversarial - High Energy Sad Acoustic, Adversarial - Chill Max Energy, and Adversarial - Missing Genre. I looked at the top five songs for each profile and checked whether they matched the profile's genre, mood, energy target, and acoustic preference in plain language. The biggest surprise was how often songs like "Gym Hero" stayed near the top for high-energy users, even when mood or acoustic preference did not really fit, because the strong energy score keeps pushing it up. Another surprise was that when genre was missing, the system quickly fell back to energy and low acousticness, which still produced plausible songs but less clearly personalized taste. This made it clear that our current weighting system is consistent, but it can over-reward energy and create repeated recommendations across different profiles.

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
