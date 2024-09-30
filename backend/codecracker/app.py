from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import gensim.downloader as api
from typing import List, Tuple, Dict
from itertools import combinations
import nltk
from nltk.corpus import stopwords, wordnet
from nltk import pos_tag

nltk.download('averaged_perceptron_tagger_eng')

app = Flask(__name__)

CORS(app, resources={r"/generate-hints": {
    "origins": ["http://localhost:3000", "https://codecracker-seven.vercel.app"]
}})

print("Loading word vectors...")
word_vectors = api.load('glove-twitter-25')
print("Word vectors loaded.")

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
stop_words = set(stopwords.words('english'))

similarity_cache = {}

def get_similarity(word1: str, word2: str) -> float:
    pair = tuple(sorted([word1, word2]))
    if pair in similarity_cache:
        return similarity_cache[pair]

    if word1 in word_vectors and word2 in word_vectors:
        similarity = word_vectors.similarity(word1, word2)
    else:
        similarity = 0.0

    similarity_cache[pair] = similarity
    return similarity

def get_synonyms(word: str) -> List[str]:
    synonyms = set()
    for synset in wordnet.synsets(word):
        for lemma in synset.lemmas():
            if lemma.name().isalpha():  # Only include valid words
                synonyms.add(lemma.name())
    return list(synonyms)

def is_valid_hint(hint: str, board_words: set) -> bool:
    hint_lower = hint.lower()
    
    if hint_lower in stop_words:
        return False
    
    for word in board_words:
        word_lower = word.lower()
        if word_lower in hint_lower or hint_lower in word_lower:
            return False
    
    return True

def is_ambiguous_hint(hint: str) -> bool:
    pos = pos_tag([hint])[0][1]
    return pos in ['NNP', 'NNPS']  # Filtering out proper nouns

def calculate_weighted_coherence(hint: str, words: List[str], weight_factor: float = 0.7) -> float:
    similarities = [get_similarity(hint, word) for word in words]
    return sum(similarities) / (len(similarities) ** weight_factor) if similarities else 0

def adaptive_threshold(num_words: int) -> float:
    base_threshold = 0.4
    return base_threshold - (num_words * 0.05)

def get_valid_hints(words: List[str], all_board_words: set, top_n: int = 100) -> List[str]:
    hints = set()
    for word in words:
        if word in word_vectors:
            similar_words = word_vectors.most_similar(word, topn=top_n)
            for hint, _ in similar_words:
                synonyms = get_synonyms(hint)  # Add synonyms for hint diversity
                for synonym in synonyms:
                    if synonym.isalpha() and is_valid_hint(synonym, all_board_words) and not is_ambiguous_hint(synonym):
                        hints.add(synonym)
    return list(hints)

def find_strategic_hints(my_words: List[str], opponent_words: List[str], neutral_words: List[str], assassin_word: str) -> Dict[int, List[Tuple[str, float, List[str]]]]:
    all_board_words = set(my_words + opponent_words + neutral_words + [assassin_word])

    valid_hints = get_valid_hints(my_words, all_board_words)
    strategic_hints = {2: [], 3: [], 4: []}

    for num_words in range(4, 1, -1):
        for words_combo in combinations(my_words, num_words):
            for hint in valid_hints:
                coherence_score = calculate_weighted_coherence(hint, words_combo)
                opponent_score = max((get_similarity(hint, w) for w in opponent_words), default=0)
                assassin_score = get_similarity(hint, assassin_word)
                
                dynamic_threshold = adaptive_threshold(num_words)

                if coherence_score > dynamic_threshold and coherence_score > opponent_score and coherence_score > assassin_score:
                    strategic_hints[num_words].append((hint, coherence_score, list(words_combo)))

    for num_words in strategic_hints:
        strategic_hints[num_words].sort(key=lambda x: x[1], reverse=True)
        strategic_hints[num_words] = strategic_hints[num_words][:5]  # Keep top 5 hints

    return strategic_hints

@app.route('/generate-hints', methods=['POST', 'OPTIONS'])
def generate_hints():
    if request.method == 'OPTIONS':
        response = make_response()
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:3000", "https://codecracker-seven.vercel.app"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    try:
        data = request.json
        my_words = data.get('my_words', [])
        opponent_words = data.get('opponent_words', [])
        neutral_words = data.get('neutral_words', [])
        assassin_word = data.get('assassin_word', '')

        if not my_words:
            return jsonify({"error": "No words provided"}), 400

        hints = find_strategic_hints(my_words, opponent_words, neutral_words, assassin_word)
        
        response = jsonify(hints)
        origin = request.headers.get('Origin')
        if origin in ["http://localhost:3000", "https://codecracker-seven.vercel.app"]:
            response.headers.add('Access-Control-Allow-Origin', origin)
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def test_find_strategic_hints():
    # Define test case words
    my_words = ['dog', 'phone', 'rabbit', 'gun', 'tree', 'table', 'laptop']
    opponent_words = ['fish', 'book', 'war', 'pipe', 'kiwi', 'hair']
    neutral_words = ['car', 'tree', 'house']
    assassin_word = 'shark'

    # Call the function directly
    hints = find_strategic_hints(my_words, opponent_words, neutral_words, assassin_word)
    
    # Print the output in a readable format
    for num_words, hint_list in hints.items():
        print(f"\nHints for {num_words} words:")
        for hint, score, words in hint_list:
            print(f"Hint: {hint}, Score: {score}, Words: {', '.join(words)}")

if __name__ == '__main__':
    test_find_strategic_hints()
    # app.run(debug=True)
