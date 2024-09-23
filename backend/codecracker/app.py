from flask import Flask, request, jsonify
from flask_cors import CORS
import gensim.downloader as api
from typing import List, Tuple, Dict
from itertools import combinations
import json

# Load word vectors (this might take a while, consider loading on-demand or using a smaller model)
print("Loading word vectors...")
word_vectors = api.load('glove-wiki-gigaword-100')
print("Word vectors loaded.")

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
    
    def get_valid_hints(words: List[str], top_n: int = 100) -> List[str]:
        hints = set()
        for word in words:
            if word in word_vectors:
                similar = word_vectors.most_similar(word, topn=top_n)
                hints.update([w for w, _ in similar if w.isalpha() and ' ' not in w and is_valid_hint(w, all_board_words)])
        return list(hints)

    valid_hints = get_valid_hints(my_words)
    strategic_hints = {2: [], 3: [], 4: []}

    for num_words in range(4, 1, -1):
        for words_combo in combinations(my_words, num_words):
            for hint in valid_hints:
                coherence_score = calculate_coherence_score(hint, words_combo)
                opponent_score = max((word_vectors.similarity(hint, w) for w in opponent_words if w in word_vectors), default=0)
                assassin_score = word_vectors.similarity(hint, assassin_word) if assassin_word in word_vectors else 0
                
                threshold = 0.35 if num_words > 2 else 0.45
                
                if coherence_score > threshold and coherence_score > opponent_score and coherence_score > assassin_score:
                    strategic_hints[num_words].append((hint, coherence_score, list(words_combo)))

    # Sort and remove duplicates
    for num_words in strategic_hints:
        strategic_hints[num_words].sort(key=lambda x: x[1], reverse=True)
        seen_hints = set()
        unique_hints = []
        for hint, score, words in strategic_hints[num_words]:
            if hint not in seen_hints:
                seen_hints.add(hint)
                unique_hints.append({"hint": hint, "score": score, "words": words})
        strategic_hints[num_words] = unique_hints[:5]  # Keep top 5 unique hints for each word count

    return strategic_hints

@app.route('/generate-hints', methods=['GET', 'POST'])
def generate_hints():
    if request.method == 'POST':
        data = request.json
    else:  # GET
        data = request.args

    my_words = data.get('my_words', '').split(',') if isinstance(data.get('my_words'), str) else data.get('my_words', [])
    opponent_words = data.get('opponent_words', '').split(',') if isinstance(data.get('opponent_words'), str) else data.get('opponent_words', [])
    neutral_words = data.get('neutral_words', '').split(',') if isinstance(data.get('neutral_words'), str) else data.get('neutral_words', [])
    assassin_word = data.get('assassin_word', '')

    if not my_words:
        return jsonify({"error": "No words provided"}), 400

    hints = find_strategic_hints(my_words, opponent_words, neutral_words, assassin_word)
    return jsonify(hints)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

if __name__ == '__main__':
    app.run(debug=True)




