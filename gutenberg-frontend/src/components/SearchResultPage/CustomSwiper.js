import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './CustomSwiper.css'; // Make sure to create a corresponding CSS file

const CustomSwiper = ({ suggestions }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const booksToShow = 5; // Number of books to show at a time

  const goToNext = () => {
    setCurrentIndex(prevIndex => (prevIndex + 1) % suggestions.length);
  };

  const goToPrev = () => {
    setCurrentIndex(prevIndex => (prevIndex - 1 + suggestions.length) % suggestions.length);
  };

  const getDisplayedBooks = () => {
    let displayed = [];
    for (let i = 0; i < booksToShow; i++) {
      displayed.push(suggestions[(currentIndex + i) % suggestions.length]);
    }
    return displayed;
  };

  const displayedBooks = getDisplayedBooks();

  return (
    <div className="custom-swiper">
      <button className="swiper-button prev" onClick={goToPrev}>&laquo;</button>
      <div className="swiper-slides">
        {displayedBooks.map((book, index) => (
          <Link key={index} to={`/books/${book.id}`}>
          <div className="swiper-slide">
            <img src={book.cover} alt={book.title} />
            <span>{book.title}</span>
          </div>
          </Link>
        ))}
      </div>
      <button className="swiper-button next" onClick={goToNext}>&raquo;</button>
    </div>
  );
};

export default CustomSwiper;
