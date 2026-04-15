# Profile Pair Reflections

Profiles tested:
- High-Energy Pop
- Chill Lofi
- Deep Intense Rock
- Adversarial - High Energy Sad Acoustic
- Adversarial - Chill Max Energy
- Adversarial - Missing Genre

## Pairwise comparisons

1. High-Energy Pop vs Chill Lofi: High-Energy Pop pushes songs like "Gym Hero" and "Storm Runner," while Chill Lofi shifts to "Library Rain" and "Midnight Coding" because lower target energy plus acoustic preference rewards softer, more acoustic tracks.
2. High-Energy Pop vs Deep Intense Rock: Both profiles keep high-energy songs near the top, but Deep Intense Rock puts "Storm Runner" first because it matches both rock and intense mood, while High-Energy Pop puts "Sunrise City" first due to happy pop alignment.
3. High-Energy Pop vs Adversarial - High Energy Sad Acoustic: The sad-acoustic profile still gets "Gym Hero" and "Sunrise City," which shows energy closeness can overpower mood mismatch when there are few songs with both very high energy and high acousticness.
4. High-Energy Pop vs Adversarial - Chill Max Energy: The max-energy chill profile unexpectedly keeps lofi songs like "Midnight Coding" near the top because exact lofi + chill matches add enough points to beat many high-energy songs.
5. High-Energy Pop vs Adversarial - Missing Genre: With missing genre, top songs become a broader mix like "Rooftop Lights" and "Golden Hour Glow," which makes sense because the model falls back to mood, energy closeness, and electronic preference.
6. Chill Lofi vs Deep Intense Rock: Chill Lofi favors low-energy acoustic songs, while Deep Intense Rock favors high-energy low-acoustic songs, so their top lists almost fully split by both energy direction and acoustic direction.
7. Chill Lofi vs Adversarial - High Energy Sad Acoustic: Chill Lofi keeps calm tracks at the top, but high-energy sad acoustic pulls in "Gym Hero" and "Neon Horizon" because the high energy target dominates even though acoustic preference is set to true.
8. Chill Lofi vs Adversarial - Chill Max Energy: Both want lofi and chill, but Chill Max Energy introduces very energetic songs like "Iron Sky" in the top five because the target energy is pushed to the maximum.
9. Chill Lofi vs Adversarial - Missing Genre: Chill Lofi gets mostly acoustic chill songs, while Missing Genre shifts to brighter, lower-acoustic tracks since genre points disappear and electronic preference becomes more important.
10. Deep Intense Rock vs Adversarial - High Energy Sad Acoustic: Both profiles rank high-energy songs high, but Deep Intense Rock gives a clear advantage to "Storm Runner" because both genre and mood match, while the sad-acoustic profile has no strong mood matches in the dataset.
11. Deep Intense Rock vs Adversarial - Chill Max Energy: Deep Intense Rock prioritizes intense rock-like tracks, while Chill Max Energy still keeps lofi songs near the top because exact genre and mood matches can still beat pure energy matches.
12. Deep Intense Rock vs Adversarial - Missing Genre: Missing Genre removes rock points and spreads recommendations across multiple genres, which shows how much personalization drops when a key preference field is unavailable.
13. Adversarial - High Energy Sad Acoustic vs Adversarial - Chill Max Energy: Both are adversarial, but the first behaves like a high-energy profile and the second behaves like a lofi/chill profile, showing that mood and genre exact matches can redirect results even under unusual settings.
14. Adversarial - High Energy Sad Acoustic vs Adversarial - Missing Genre: Missing Genre gives a more diverse top five, while High Energy Sad Acoustic repeats high-energy songs, because one profile has no genre anchor and the other has a strong energy anchor.
15. Adversarial - Chill Max Energy vs Adversarial - Missing Genre: Chill Max Energy still keeps lofi/chill songs at the top thanks to exact matches, while Missing Genre leans toward medium-high energy and low acousticness due to fallback scoring behavior.

## Plain-language takeaway

"Gym Hero" keeps showing up for users who want "Happy Pop" because it has very high energy and very low acousticness, and those two factors are heavily rewarded in the current formula. Even when mood is imperfect, the energy bonus is large enough to keep it near the top.
