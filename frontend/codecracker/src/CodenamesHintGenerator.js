import React, { useState } from 'react';
import axios from 'axios';

const CodenamesHintGenerator = () => {
  const [gameState, setGameState] = useState({
    my_words: '',
    opponent_words: '',
    neutral_words: '',
    assassin_word: ''
  });
  const [hints, setHints] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setGameState(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const generateHints = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate-hints', {
        my_words: gameState.my_words.split(',').map(word => word.trim()),
        opponent_words: gameState.opponent_words.split(',').map(word => word.trim()),
        neutral_words: gameState.neutral_words.split(',').map(word => word.trim()),
        assassin_word: gameState.assassin_word.trim()
      });
      setHints(response.data);
    } catch (err) {
      setError('Failed to generate hints. Please try again.');
      console.error('Error generating hints:', err);
    }
    setIsLoading(false);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Codenames Hint Generator</h1>
      <div className="mb-4">
        <label className="block mb-2">Your Team's Words (comma-separated):</label>
        <input
          className="w-full p-2 border rounded"
          name="my_words"
          value={gameState.my_words}
          onChange={handleInputChange}
          placeholder="e.g. apple, tree, green"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-2">Opponent's Words (comma-separated):</label>
        <input
          className="w-full p-2 border rounded"
          name="opponent_words"
          value={gameState.opponent_words}
          onChange={handleInputChange}
          placeholder="e.g. car, road, wheel"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-2">Neutral Words (comma-separated):</label>
        <input
          className="w-full p-2 border rounded"
          name="neutral_words"
          value={gameState.neutral_words}
          onChange={handleInputChange}
          placeholder="e.g. house, window, door"
        />
      </div>
      <div className="mb-4">
        <label className="block mb-2">Assassin Word:</label>
        <input
          className="w-full p-2 border rounded"
          name="assassin_word"
          value={gameState.assassin_word}
          onChange={handleInputChange}
          placeholder="e.g. poison"
        />
      </div>
      <button
        className="bg-blue-500 text-white p-2 rounded hover:bg-blue-600"
        onClick={generateHints}
        disabled={isLoading}
      >
        {isLoading ? 'Generating...' : 'Generate Hints'}
      </button>
      {error && <p className="text-red-500 mt-4">{error}</p>}
      {hints && (
        <div className="mt-8">
          <h2 className="text-2xl font-bold mb-4">Generated Hints:</h2>
          {[4, 3, 2].map(numWords => (
            <div key={numWords} className="mb-6">
              <h3 className="text-xl font-semibold mb-2">{numWords}-Word Hints:</h3>
              {hints[numWords].length > 0 ? (
                <ul className="list-disc pl-5">
                  {hints[numWords].map((hint, index) => (
                    <li key={index} className="mb-2">
                      <span className="font-bold">{hint.hint}</span> (Score: {hint.score.toFixed(2)})
                      <br />
                      <span className="text-sm text-gray-600">Words: {hint.words.join(', ')}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>No hints generated for {numWords} words.</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CodenamesHintGenerator;