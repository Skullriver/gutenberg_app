import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faBook } from '@fortawesome/free-solid-svg-icons';
import './bookDetails.css';
import Header from '../Header/Header';


function BookDetails() {
  const { id } = useParams();
  const [book, setBook] = useState(null);
  const [isLoading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/api/search/books/${id}`)
      .then(res => res.json())
      .then(data => {
        setBook(data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching book details:", error);
        setLoading(false);
      });
  }, [id]);

  if (isLoading) return <div>Loading...</div>;
  if (!book) return <div>Book not found</div>;

  return (
    <div>
        <Header />
        <div className="book-details-container">
            <img src={book.cover} alt={book.title} className="book-cover"/>
            <div className="book-info">
                <h2 className="book-details-title">{book.title}</h2>
                <a href={book.text_link} className="book-link"> <FontAwesomeIcon className='book-icon' icon={faBook} /> Read or Download</a>
                <p className="book-details-info">Type: {book.type}</p>
                <p className="book-details-info">Authors: {book.authors}</p>
                <p className="book-details-info">Language: {book.language}</p>
                <p className="book-details-info">Subjects: {book.subjects}</p>
                <p className="book-details-info">Bookshelves: {book.bookshelves}</p>
            </div>
        </div>
    </div>
  );
}

export default BookDetails;