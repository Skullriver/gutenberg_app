import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import SearchBar from '../SearchBar/SearchBar';
import './searchResultPage.css';

const SearchResultPage = () => {

    const location = useLocation();
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState(location.state?.query || '');

    
    useEffect(() => {
      // Perform initial search if query is provided in state
      if (searchTerm) {
        performSearch(searchTerm);
      }
    }, [searchTerm]);
  
    const performSearch = async (searchTerm) => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/search`, {
          params: { query: searchTerm }
        });
        const books = Object.values(response.data.results);
        setResults(books || []);
      } catch (error) {
        console.error('Error fetching search results:', error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

  return (
    <div className="search-results-page">
        <SearchBar onSearch={performSearch} initialSearchTerm={searchTerm}/>
        {console.log(results)}
      <h2>Search Results</h2>
      {isLoading ? (
        <div className="loader"></div> // Display loader while loading
      ) : results.length > 0 ? (
        <div className="results-list">
          {results.map((book, index) => (
            <div key={index} className="book-result">
              <img src={book.cover} alt={book.title} />
              <span>{book.title}</span>
            </div>
          ))}
        </div>
      ) : (
        <p>No results found.</p>
      )}
    </div>
  );
};

export default SearchResultPage;
