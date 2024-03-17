import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import SearchBar from '../SearchBar/SearchBar';
import PaginationElem from '../SearchResultPage/Pagination';
import CustomSwiper from '../SearchResultPage/CustomSwiper';
import '../SearchResultPage/searchResultPage.css';
import Header from '../Header/Header';

const SearchRegexPage = () => {

    const location = useLocation();
    const [results, setResults] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState(location.state?.query || '');
    const [currentPage, setCurrentPage] = useState(1);
    const [booksPerPage] = useState(10);
    
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
          params: { regex: searchTerm }
        });
        const books = Object.values(response.data.results);
        const suggestions =  Object.values(response.data.suggestions);
        setResults(books || []);
        setSuggestions(suggestions || []);
      } catch (error) {
        console.error('Error fetching search results:', error);
        setResults([]);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    };

    const indexOfLastBook = currentPage * booksPerPage;
    const indexOfFirstBook = indexOfLastBook - booksPerPage;
    const currentBooks = results.slice(indexOfFirstBook, indexOfLastBook);

  return (
    <div>
        <Header />
        <div className="search-results-page">
        <SearchBar onSearch={performSearch} initialSearchTerm={searchTerm}/>
      <h2>Search Results</h2>
      {isLoading ? (
        <div className="loader"></div> // Display loader while loading
      ) : results.length > 0 ? (
        <div className="results">
          <div className="results-list">
            {currentBooks.map((book, index) => (
              <div key={index} className="book-result">
                <img src={book.cover} alt={book.title} />
                <span>{book.title}</span>
              </div>
            ))}
          </div>
          <PaginationElem booksPerPage={booksPerPage} 
          totalBooks={results.length} 
          paginate={setCurrentPage} 
          currentPage={currentPage}  />
          {suggestions.length > 0 && (
            <div className="suggestions-section">
              <h2>You Might Also Like</h2>
              <CustomSwiper suggestions={suggestions} />
              
            </div>
          )}
        </div>
      ) : (
        <p>No results found.</p>
      )}
    </div>
    </div>
    
  );
};

export default SearchRegexPage;
