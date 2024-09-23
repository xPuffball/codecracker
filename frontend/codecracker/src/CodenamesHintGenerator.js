import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  Grid, 
  Container, 
  Alert,
  Box,
  TextField,
  AppBar,
  Toolbar,
  IconButton,
  Menu,
  MenuItem,
  ToggleButtonGroup,
  ToggleButton,
  Select,
  FormControl,
  InputLabel
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import WORD_POOL from './wordPool.js';  // Import the word pool

// Import your agent images here
import blueAgentImage from './agentImages/blue.png';
import redAgentImage from './agentImages/red.png';
import neutralAgentImage from './agentImages/net.png';
import assassinAgentImage from './agentImages/bad.png';

const WORD_TYPES = {
  BLUE: 'blue',
  RED: 'red',
  NEUTRAL: 'neutral',
  ASSASSIN: 'assassin',
  UNASSIGNED: 'unassigned'
};

const INITIAL_WORDS = Array(25).fill('').map((_, index) => ({ id: `word-${index}`, word: '', type: WORD_TYPES.UNASSIGNED }));

const CodenamesHintGenerator = () => {
  const [words, setWords] = useState(INITIAL_WORDS);
  const [hints, setHints] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [focusedIndex, setFocusedIndex] = useState(0);
  const [anchorEl, setAnchorEl] = useState(null);
  const [currentRole, setCurrentRole] = useState(WORD_TYPES.UNASSIGNED);
  const [hintTeam, setHintTeam] = useState(WORD_TYPES.BLUE);
  
  const inputRefs = useRef([]);

  useEffect(() => {
    inputRefs.current = inputRefs.current.slice(0, words.length);
  }, [words]);

  const handleCardClick = (index) => {
    setWords(prevWords => {
      const newWords = [...prevWords];
      newWords[index] = { ...newWords[index], type: currentRole };
      return newWords;
    });
  };

  const generateHints = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const gameState = {
        my_words: words.filter(w => w.type === hintTeam).map(w => w.word),
        opponent_words: words.filter(w => w.type !== hintTeam && w.type !== WORD_TYPES.UNASSIGNED).map(w => w.word),
        neutral_words: words.filter(w => w.type === WORD_TYPES.NEUTRAL).map(w => w.word),
        assassin_word: words.find(w => w.type === WORD_TYPES.ASSASSIN)?.word || ''
      };
      console.log(gameState)

      const response = await axios.post('https://codecracker-2.onrender.com/generate-hints', gameState);
      setHints(response.data);
    } catch (err) {
      setError('Failed to generate hints. Please try again.');
      console.error('Error generating hints:', err);
    }
    setIsLoading(false);
  };

  const getCardColor = (type) => {
    switch (type) {
      case WORD_TYPES.BLUE: return '#BBDEFB';  // Light Blue
      case WORD_TYPES.RED: return '#FFCDD2';  // Light Red
      case WORD_TYPES.NEUTRAL: return '#FFF9C4';  // Light Yellow
      case WORD_TYPES.ASSASSIN: return '#212121';  // Dark Grey
      default: return '#FFFFFF';  // White
    }
  };

  const getAgentImage = (type) => {
    switch (type) {
      case WORD_TYPES.BLUE: return blueAgentImage;
      case WORD_TYPES.RED: return redAgentImage;
      case WORD_TYPES.NEUTRAL: return neutralAgentImage;
      case WORD_TYPES.ASSASSIN: return assassinAgentImage;
      default: return null;
    }
  };

  const handleWordChange = (index, newWord) => {
    setWords(prevWords => {
      const newWords = [...prevWords];
      newWords[index] = { ...newWords[index], word: newWord };
      return newWords;
    });
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const nextIndex = (index + 1) % words.length;
      setFocusedIndex(nextIndex);
      inputRefs.current[nextIndex].focus();
    }
  };

  const clearBoard = () => {
    setWords(INITIAL_WORDS);
    setHints(null);
  };

  const randomizeWords = () => {
    const shuffled = [...WORD_POOL].sort(() => 0.5 - Math.random());
    const selectedWords = shuffled.slice(0, 25);
    setWords(selectedWords.map((word, index) => ({ id: `word-${index}`, word, type: WORD_TYPES.UNASSIGNED })));
  };

  const randomizeGameSetup = () => {
    const newWords = [...words];
    const indices = Array.from({ length: 25 }, (_, i) => i);
    indices.sort(() => Math.random() - 0.5);

    const blueFirst = Math.random() < 0.5;
    const blueCount = blueFirst ? 9 : 8;
    const redCount = blueFirst ? 8 : 9;

    for (let i = 0; i < 25; i++) {
      if (i < blueCount) {
        newWords[indices[i]].type = WORD_TYPES.BLUE;
      } else if (i < blueCount + redCount) {
        newWords[indices[i]].type = WORD_TYPES.RED;
      } else if (i < blueCount + redCount + 7) {
        newWords[indices[i]].type = WORD_TYPES.NEUTRAL;
      } else if (i === 24) {
        newWords[indices[i]].type = WORD_TYPES.ASSASSIN;
      }
    }

    setWords(newWords);
    setHintTeam(blueFirst ? WORD_TYPES.BLUE : WORD_TYPES.RED);
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleRoleChange = (event, newRole) => {
    if (newRole !== null) {
      setCurrentRole(newRole);
    }
  };

  const handleHintTeamChange = (event) => {
    setHintTeam(event.target.value);
  };

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h3" component="div" sx={{ flexGrow: 1 }}>
            CODECRACKER
          </Typography>
          <IconButton
            size="large"
            edge="start"
            color="inherit"
            aria-label="menu"
            sx={{ mr: 2 }}
            onClick={handleMenuOpen}
          >
            <MenuIcon />
          </IconButton>
          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={() => { clearBoard(); handleMenuClose(); }}>Clear Board</MenuItem>
            <MenuItem onClick={() => { randomizeWords(); handleMenuClose(); }}>Randomize Words</MenuItem>
            <MenuItem onClick={() => { randomizeGameSetup(); handleMenuClose(); }}>Random Game Setup</MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Box sx={{ mb: 2 }}>
          <Typography variant="body2" sx={{ mb: 1 }}>
            Select a role to assign:
          </Typography>
          <ToggleButtonGroup
            value={currentRole}
            exclusive
            onChange={handleRoleChange}
            aria-label="text alignment"
          >
            <ToggleButton value={WORD_TYPES.BLUE} aria-label="blue team">
              Blue Team
            </ToggleButton>
            <ToggleButton value={WORD_TYPES.RED} aria-label="red team">
              Red Team
            </ToggleButton>
            <ToggleButton value={WORD_TYPES.NEUTRAL} aria-label="neutral">
              Neutral
            </ToggleButton>
            <ToggleButton value={WORD_TYPES.ASSASSIN} aria-label="assassin">
              Assassin
            </ToggleButton>
            <ToggleButton value={WORD_TYPES.UNASSIGNED} aria-label="unassigned">
              Unassigned
            </ToggleButton>
          </ToggleButtonGroup>
        </Box>
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {words.map((wordObj, index) => (
            <Grid item xs={2.4} key={wordObj.id}>
              <Card 
                onClick={() => handleCardClick(index)}
                sx={{ 
                  bgcolor: getCardColor(wordObj.type),
                  cursor: 'pointer',
                  '&:hover': { opacity: 0.8 },
                  height: '100%',
                  transition: 'background-color 0.5s ease',
                  position: 'relative',
                }}
              >
                <CardContent>
                  <TextField
                    value={wordObj.word}
                    onChange={(e) => handleWordChange(index, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                    inputRef={el => inputRefs.current[index] = el}
                    variant="standard"
                    fullWidth
                    autoFocus={index === focusedIndex}
                    InputProps={{
                      disableUnderline: true,
                      style: { textAlign: 'center' }
                    }}
                  />
                  {wordObj.type !== WORD_TYPES.UNASSIGNED && (
                    <Box
                      component="img"
                      src={getAgentImage(wordObj.type)}
                      alt={`${wordObj.type} agent`}
                      sx={{
                        position: 'absolute',
                        right: 5,
                        bottom: 5,
                        width: 30,
                        height: 30,
                      }}
                    />
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2 }}>
          <FormControl sx={{ minWidth: 120 }}>
            <InputLabel id="hint-team-select-label">Generate Hints For</InputLabel>
            <Select
              labelId="hint-team-select-label"
              id="hint-team-select"
              value={hintTeam}
              label="Generate Hints For"
              onChange={handleHintTeamChange}
            >
              <MenuItem value={WORD_TYPES.BLUE}>Blue Team</MenuItem>
              <MenuItem value={WORD_TYPES.RED}>Red Team</MenuItem>
            </Select>
          </FormControl>
          <Button 
            variant="contained" 
            color="primary"
            onClick={generateHints}
            disabled={isLoading}
          >
            {isLoading ? 'Generating...' : 'Generate Hints'}
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {hints && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom>
              Codes Cracked for {hintTeam === WORD_TYPES.BLUE ? 'Blue' : 'Red'} Team:
            </Typography>
            {[4, 3, 2].map(numWords => (
              <Box key={numWords} sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {numWords}-Word Hints:
                </Typography>
                {hints[numWords].length > 0 ? (
                  <Grid container spacing={2}>
                    {hints[numWords].map((hint, index) => (
                      <Grid item xs={12} sm={6} md={4} key={index}>
                        <Card>
                          <CardContent>
                            <Typography variant="h6" gutterBottom>
                              {hint.hint}
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              Score: {hint.score.toFixed(2)}
                            </Typography>
                            <Box sx={{ mt: 1 }}>
                              {hint.words.map((word, i) => (
                                <Typography key={i} variant="body2" component="span" sx={{ mr: 1 }}>
                                  {word}
                                </Typography>
                              ))}
                            </Box>
                          </CardContent>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                ) : (
                  <Typography>No hints generated for {numWords} words.</Typography>
                )}
              </Box>
            ))}
          </Box>
        )}
      </Container>
    </>
  );
};

export default CodenamesHintGenerator;