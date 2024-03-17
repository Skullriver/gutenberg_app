// src/components/Bookshelf/Bookshelf.js
import React, { useState, useEffect } from 'react';
import './bookshelf.css';
import BookCover from '../BookCover/BookCover';

const Bookshelf = ({ books }) => {
    const [gridItems, setGridItems] = useState([]);
    const letters = 'ABCDEFGHIJKLMNPQRSTUVWXYZ'; // Omitting 'O' to avoid confusion with zero

    

    useEffect(() => {
        if (books.length !== 0) {
        const viewportWidth = document.documentElement.clientWidth;
        const numColumns = Math.floor(viewportWidth*0.5 / 175);

        const numItems = numColumns * 3; // 3 rows

        let lastBook = null;
        let lastLetter = null;
        let letterCount = 0; // Track the number of letters added
        const items = []; // Assuming this is initialized somewhere


        for (let i = 0; i < numItems; i++) {
            let item;
            do {
                if (Math.random() < 0.5 || numItems - i <= 5 - letterCount) { 
                    // Randomly pick a letter, but not the same as the last one
                    // Also, ensure there are at least 5 letters by forcing letter selection
                    // if the remaining items to add are equal to the number needed to reach 5 letters
                    let letter;
                    do {
                        letter = letters[Math.floor(Math.random() * letters.length)];
                    } while (lastLetter === letter);
                    lastLetter = letter;
                    item = { type: 'letter', content: letter };
                    letterCount++; // Increment letter count
                } else {
                    // Randomly pick a book, but not the same as the last one
                    let book;
                    do {
                        book = books[Math.floor(Math.random() * books.length)];
                    } while (lastBook === book);
                    lastBook = book;
                    item = { type: 'book', content: book };
                }
            } while (items.length && items[items.length - 1].content === item.content); // Ensure no immediate repetitions
        
            items.push(item);
        }

        setGridItems(items);
        }
    }, [books, letters]);

    

    return (
        <div className="bookshelf">
            {gridItems.map((item, index) => (
                item.type === 'book' ? (
                    <BookCover key={index} title={item.content.title} cover={item.content.cover} />
                ) : (
                    <div key={index} className="book-letter">{item.content}</div>
                )
            ))}
        </div>
    );
};

export default Bookshelf;
