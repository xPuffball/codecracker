import React from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import CodenamesHintGenerator from './CodenamesHintGenerator';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <div className="App">
        <CodenamesHintGenerator />
      </div>
    </ThemeProvider>
  );
}

export default App;