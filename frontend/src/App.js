import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import InputScreen from './components/InputScreen';
import OutputScreen from './components/OutputScreen';

function App() {
  const [result, setResult] = useState(null);

  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>AI SMM Assistant</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<InputScreen setResult={setResult} />} />
            <Route path="/results/:token" element={<OutputScreen savedResult={result} />} />
          </Routes>
        </main>
        <footer>
          <p>AI-powered content ideas for your social media</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
