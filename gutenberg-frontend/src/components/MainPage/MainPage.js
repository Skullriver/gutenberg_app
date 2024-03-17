import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './mainPage.css';
import Banner from '../Banner/Banner';
import Header from '../Header/Header'; 
import SearchBar from '../SearchBar/SearchBar';
import Bookshelf from '../Bookshelf/Bookshelf';


const MainPage = () => {
    // Mock data - you will replace this with real data fetched from an API
    const [books, setBooks] = useState([]); // Initialize state to hold books

    const fetchRandomBooks = async () => {
        try {
            const response = await axios.get('http://127.0.0.1:8000/api/random-books/'); // Replace YOUR_BACKEND_URL with your actual backend URL
            setBooks(response.data.books); // Assuming the backend response format is { books: [...] }
        } catch (error) {
            console.error("Failed to fetch books:", error);
            // Handle error (e.g., set an error state, show a notification)
        }
    };

    useEffect(() => {
        fetchRandomBooks();
    }, []);

    return (
        <div className="main-page">
            <div className="left-panel">
                <Header />
                <div className='search-bar-main'>
                    <Banner />
                    <SearchBar />
                </div>
                
            </div>
            <div className="right-panel">
                <Bookshelf books={books} />
            </div>
        </div>
    );
};

export default MainPage;
