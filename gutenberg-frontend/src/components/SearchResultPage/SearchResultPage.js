import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import axios from 'axios';
import SearchBar from '../SearchBar/SearchBar';
import PaginationElem from '../SearchResultPage/Pagination';
import CustomSwiper from '../SearchResultPage/CustomSwiper';
import './searchResultPage.css';
import Header from '../Header/Header';
import ImageLoader from '../ImageLoader/ImageLoader';
import { Link } from 'react-router-dom';


const SearchResultPage = () => {

    const location = useLocation();
    const [results, setResults] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [searchTerm, setSearchTerm] = useState(location.state?.query || '');
    const [currentPage, setCurrentPage] = useState(1);
    const [booksPerPage] = useState(10);
    
    useEffect(() => {
      
      // Retrieve stored search term, results, and suggestions
      const storedSearchTerm = sessionStorage.getItem('searchTerm');
      const storedResults = sessionStorage.getItem('searchResults');
      const storedSuggestions = sessionStorage.getItem('searchSuggestions');
    
      if (storedSearchTerm) setSearchTerm(storedSearchTerm)
      else setSearchTerm(searchTerm);
      if (storedResults) setResults(JSON.parse(storedResults));
      if (storedSuggestions) setSuggestions(JSON.parse(storedSuggestions));
    
      // Perform a new search if searchTerm is provided and storage is empty
      if (!storedResults && searchTerm) {
        performSearch(searchTerm);
      }
    }, []);
  
    const performSearch = async (searchTerm) => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/search`, {
          params: { query: searchTerm }
        });
        const books = Object.values(response.data.results);
        const suggestions =  Object.values(response.data.suggestions);

        sessionStorage.setItem('searchTerm', searchTerm);
        sessionStorage.setItem('searchResults', JSON.stringify(books));
        sessionStorage.setItem('searchSuggestions', JSON.stringify(suggestions));

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

    const handlePageChange = newPage => {
      setIsLoading(true);  // Trigger loading state
      setCurrentPage(newPage);  // Change to the new page
      setTimeout(() => setIsLoading(false), 150);
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
              <Link key={index} to={`/books/${book.id}`}>
                <div className="book-result">
                {/* <ImageLoader src={book.cover} alt={book.title} /> */}
                  <img src={book.cover} alt={book.title} />
                  <span>{book.title}</span>
                </div>
              </Link>
            ))}
          </div>
          <PaginationElem booksPerPage={booksPerPage} 
          totalBooks={results.length} 
          paginate={handlePageChange} 
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

export default SearchResultPage;
