import React from 'react';
import './bookCover.css';

const BookCover = ({ title, cover }) => {
    return (
        <div className="book-cover">
            <img src={cover} alt={`Cover of ${title}`} />
        </div>
    );
};

export default BookCover;
