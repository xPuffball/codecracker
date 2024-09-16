import gensim.downloader as api
from typing import List, Tuple, Dict
from itertools import combinations
import random

print("Loading word vectors...")
word_vectors = api.load('word2vec-google-news-300')
print("Word vectors loaded.")

def simple_stem(word: str) -> str:
    word = word.lower()
    for ending in ['s', 'es', 'ed', 'ing', 'ly']:
        if word.endswith(ending):
            word = word[:-len(ending)]
            break
    return word

def preprocess_word(word: str) -> str:
    return simple_stem(word.lower().strip())

def is_valid_hint(hint: str, board_words: set) -> bool:
    hint_lower = hint.lower()
    for word in board_words:
        word_lower = word.lower()
        if word_lower in hint_lower or hint_lower in word_lower:
            return False
    return True

def calculate_coherence_score(hint: str, words: List[str]) -> float:
    similarities = [word_vectors.similarity(hint, word) for word in words if word in word_vectors]
    if not similarities:
        return 0
    return (sum(similarities) / len(similarities)) * (len(similarities) ** 0.5)

def find_strategic_hints(my_words: List[str], opponent_words: List[str], neutral_words: List[str], assassin_word: str) -> Dict[int, List[Tuple[str, float, List[str]]]]:
    all_board_words = set(my_words + opponent_words + neutral_words + [assassin_word])
    print(f"All board words: {all_board_words}")
    
    def get_valid_hints(words: List[str], top_n: int = 100) -> List[str]:
        hints = set()
        for word in words:
            if word in word_vectors:
                similar = word_vectors.most_similar(word, topn=top_n)
                hints.update([w for w, _ in similar if w.isalpha() and ' ' not in w and is_valid_hint(w, all_board_words)])
            else:
                print(f"Warning: '{word}' not in vocabulary")
        return list(hints)

    valid_hints = get_valid_hints(my_words)
    print(f"Number of valid hints generated: {len(valid_hints)}")
    print(f"Sample of valid hints: {valid_hints[:10]}")

    strategic_hints = {2: [], 3: [], 4: []}

    for num_words in range(4, 1, -1):
        print(f"\nLooking for {num_words}-word hints:")
        for words_combo in combinations(my_words, num_words):
            for hint in valid_hints:
                coherence_score = calculate_coherence_score(hint, words_combo)
                opponent_score = max((word_vectors.similarity(hint, w) for w in opponent_words if w in word_vectors), default=0)
                assassin_score = word_vectors.similarity(hint, assassin_word) if assassin_word in word_vectors else 0
                
                # Adjust thresholds based on the number of words
                threshold = 0.35 if num_words > 2 else 0.45
                
                if coherence_score > threshold and coherence_score > opponent_score and coherence_score > assassin_score:
                    strategic_hints[num_words].append((hint, coherence_score, list(words_combo)))
                    print(f"Found hint: {hint}, Score: {coherence_score:.2f}, Words: {words_combo}")

    # Sort hints for each word count and remove duplicates
    for num_words in strategic_hints:
        strategic_hints[num_words].sort(key=lambda x: x[1], reverse=True)
        seen_hints = set()
        unique_hints = []
        for hint, score, words in strategic_hints[num_words]:
            if hint not in seen_hints:
                seen_hints.add(hint)
                unique_hints.append((hint, score, words))
        strategic_hints[num_words] = unique_hints[:5]  # Keep top 5 unique hints for each word count

    return strategic_hints

# Authentic Codenames wordset
all_words = [
    "apple", "book", "chair", "dog", "elephant", "fire", "guitar", "hospital",
    "ice", "jungle", "key", "lamp", "moon", "newspaper", "ocean", "piano",
    "queen", "robot", "sun", "telephone", "umbrella", "volcano", "window",
    "xylophone", "zebra"
]

# Shuffle and distribute words
random.shuffle(all_words)
my_words = all_words[:8]
opponent_words = all_words[8:15]
neutral_words = all_words[15:24]
assassin_word = all_words[24]

print("Game Setup:")
print(f"My team's words: {my_words}")
print(f"Opponent's words: {opponent_words}")
print(f"Neutral words: {neutral_words}")
print(f"Assassin word: {assassin_word}")

print("\nGenerating hints...")
hints = find_strategic_hints(my_words, opponent_words, neutral_words, assassin_word)

print("\nTop Strategic Hints:")
for num_words in [4, 3, 2]:
    print(f"\nBest {num_words}-word hints:")
    for hint, score, words in hints[num_words]:
        print(f"Hint: {hint}, Score: {score:.2f}, Words: {', '.join(words)}")

if all(len(hints[num_words]) == 0 for num_words in [2, 3, 4]):
    print("\nNo hints were generated. This could be due to strict criteria or words not in the vocabulary.")

# Best 4-word hints:
# Hint: streetlamp, Score: 0.72, Words: lamp, sun, umbrella, chair
# Hint: sunlight, Score: 0.69, Words: lamp, sun, ice, jungle
# Hint: canopy, Score: 0.68, Words: lamp, sun, umbrella, jungle
# Hint: parasol, Score: 0.68, Words: lamp, sun, umbrella, jungle
# Hint: shade, Score: 0.67, Words: lamp, sun, umbrella, jungle

# Best 3-word hints:
# Hint: sunlight, Score: 0.72, Words: lamp, sun, ice
# Hint: streetlamp, Score: 0.69, Words: lamp, sun, umbrella
# Hint: shade, Score: 0.67, Words: lamp, sun, umbrella
# Hint: sunrays, Score: 0.67, Words: lamp, sun, ice
# Hint: tundra, Score: 0.66, Words: sun, ice, jungle

# Best 2-word hints:
# Hint: sunlight, Score: 0.70, Words: lamp, sun
# Hint: sunrays, Score: 0.65, Words: lamp, sun
# Hint: streetlamp, Score: 0.64, Words: lamp, sun
# Hint: lights, Score: 0.63, Words: lamp, sun
# Hint: sunshine, Score: 0.63, Words: sun, ice