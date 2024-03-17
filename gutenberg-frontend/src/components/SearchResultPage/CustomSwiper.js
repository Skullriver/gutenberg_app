import React, { useState } from 'react';
import './CustomSwiper.css'; // Make sure to create a corresponding CSS file

const CustomSwiper = ({ suggestions }) => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const goToNext = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === suggestions.length - 1 ? 0 : prevIndex + 1
    );
  };

  const goToPrev = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? suggestions.length - 1 : prevIndex - 1
    );
  };

  const displayedBooks = suggestions.slice(currentIndex, currentIndex + 3);

  return (
    <div className="custom-swiper">
      <button className="swiper-button prev" onClick={goToPrev}>&laquo;</button>
      <div className="swiper-slide">
        {suggestions.length > 0 && (
          <div className="book">
            <img src={suggestions[currentIndex].cover} alt={suggestions[currentIndex].title} />
            <span>{suggestions[currentIndex].title}</span>
          </div>
        )}
      </div>
      <button className="swiper-button next" onClick={goToNext}>&raquo;</button>
    </div>
  );
};

export default CustomSwiper;
