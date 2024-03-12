import React from 'react';
import './mainPage.css';
import Banner from '../Banner/Banner';
import SearchBar from '../SearchBar/SearchBar';
import Bookshelf from '../Bookshelf/Bookshelf';
import defaultCover from '../../assets/cover.jpg';

const MainPage = () => {
    // Mock data - you will replace this with real data fetched from an API
    const books = [
        { title: 'Book Title 1', cover: defaultCover },
        { title: 'Book Title 2', cover: defaultCover },
        // More books...
    ];

    return (
        <div className="main-page">
            <div className="left-panel">
                <Banner />
                <SearchBar />
            </div>
            <div className="right-panel">
                <Bookshelf books={books} />
            </div>
        </div>
    );
};

export default MainPage;
