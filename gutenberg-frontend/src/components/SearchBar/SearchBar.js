// SearchBar.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faTimes } from '@fortawesome/free-solid-svg-icons';
import './searchBar.css';

const SearchBar = ({ onSearch, initialSearchTerm = '' }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    setSearchTerm(initialSearchTerm);
  }, [initialSearchTerm]);

  const handleSearch = () => {
    if (onSearch) {
      // Perform search without redirecting (for SearchResultPage)
      onSearch(searchTerm);
    } else {
      sessionStorage.removeItem('searchTerm');
      sessionStorage.removeItem('searchResults');
      sessionStorage.removeItem('searchSuggestions');

      // Navigate to SearchResultPage with searchTerm (for MainPage)
      navigate('/search', { state: { query: searchTerm } });
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && searchTerm.trim()) {
      handleSearch();
    }
  };

  const clearSearch = () => {
    setSearchTerm(''); // Clear the search input
  };

  return (
    <div className="search-bar">
      <input
        type="text"
        placeholder="Search for books..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        onKeyPress={handleKeyPress}
      />
      {searchTerm && (
        <button onClick={clearSearch} className="clear-search">
          <FontAwesomeIcon icon={faTimes} />
        </button>
      )}
      <button className='search-button' onClick={handleSearch}>Search</button>
    </div>
  );
};

export default SearchBar;
