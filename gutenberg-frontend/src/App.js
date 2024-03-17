import logo from './logo.svg';
import './App.css';
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import SearchResultPage from './components/SearchResultPage/SearchResultPage'; // Assume you have this component
import SearchRegexPage from './components/SearchRegexPage/SearchRegexPage';

import MainPage from './components/MainPage/MainPage';

function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/" exact element={<MainPage/>} />
          <Route path="/search" element={<SearchResultPage/>} />
          <Route path="/regex_search" element={<SearchRegexPage/>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
