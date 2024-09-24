from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import gensim.downloader as api
from typing import List, Tuple, Dict
from itertools import combinations
import nltk
from nltk.corpus import stopwords

# Initialize the app
app = Flask(__name__)

# Enable CORS for specific origins
CORS(app, resources={r"/generate-hints": {
    "origins": ["http://localhost:3000", "https://codecracker-seven.vercel.app"]
}})

# Load word vectors (consider using a smaller model for performance)
print("Loading word vectors...")
word_vectors = api.load('glove-twitter-25')  # Using a smaller/faster model
print("Word vectors loaded.")

# Download NLTK stopwords and load them
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Cache for word similarities to avoid recalculating
similarity_cache = {}

def get_similarity(word1: str, word2: str) -> float:
    # Return cached similarity if available
    pair = tuple(sorted([word1, word2]))
    if pair in similarity_cache:
        return similarity_cache[pair]

    # Compute similarity only if both words are in the model
    if word1 in word_vectors and word2 in word_vectors:
        similarity = word_vectors.similarity(word1, word2)
    else:
        similarity = 0.0

    similarity_cache[pair] = similarity
    return similarity

def is_valid_hint(hint: str, board_words: set) -> bool:
    hint_lower = hint.lower()
    
    # Check if the hint is a stopword
    if hint_lower in stop_words:
        return False
    
    # Check if the hint is part of the board words (to avoid conflicts)
    for word in board_words:
        word_lower = word.lower()
        if word_lower in hint_lower or hint_lower in word_lower:
            return False
    
    return True

def calculate_coherence_score(hint: str, words: List[str]) -> float:
    # Bulk similarity calculation
    similarities = [get_similarity(hint, word) for word in words]
    if not similarities:
        return 0
    return (sum(similarities) / len(similarities)) * (len(similarities) ** 0.5)

def find_strategic_hints(my_words: List[str], opponent_words: List[str], neutral_words: List[str], assassin_word: str) -> Dict[int, List[Tuple[str, float, List[str]]]]:
    all_board_words = set(my_words + opponent_words + neutral_words + [assassin_word])

    # Filter valid hints using only my_words to reduce the search space
    def get_valid_hints(words: List[str], top_n: int = 100) -> List[str]:
        hints = set()
        for word in words:
            if word in word_vectors:
                similar = word_vectors.most_similar(word, topn=top_n)
                hints.update([w for w, _ in similar if w.isalpha() and ' ' not in w and is_valid_hint(w, all_board_words)])
        return list(hints)

    # Cache valid hints for my_words
    valid_hints = get_valid_hints(my_words)
    strategic_hints = {2: [], 3: [], 4: []}

    # Reduce combination space to handle large requests efficiently
    for num_words in range(4, 1, -1):
        for words_combo in combinations(my_words, num_words):
            for hint in valid_hints:
                coherence_score = calculate_coherence_score(hint, words_combo)
                opponent_score = max((get_similarity(hint, w) for w in opponent_words), default=0)
                assassin_score = get_similarity(hint, assassin_word)

                # Use a higher threshold for fewer words
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

@app.route('/generate-hints', methods=['POST', 'OPTIONS'])
def generate_hints():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = make_response()
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:3000", "https://codecracker-seven.vercel.app"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    # Handle POST request
    try:
        data = request.json
        my_words = data.get('my_words', [])
        opponent_words = data.get('opponent_words', [])
        neutral_words = data.get('neutral_words', [])
        assassin_word = data.get('assassin_word', '')

        if not my_words:
            return jsonify({"error": "No words provided"}), 400

        hints = find_strategic_hints(my_words, opponent_words, neutral_words, assassin_word)
        
        # Create the response
        response = jsonify(hints)
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:3000", "https://codecracker-seven.vercel.app"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
