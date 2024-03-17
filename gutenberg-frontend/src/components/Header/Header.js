// Header.js
import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faHome } from '@fortawesome/free-solid-svg-icons';
import { Link } from 'react-router-dom';
import './header.css'; // Create and customize your header styles

const Header = () => {
  return (
    <header className="app-header">
      <nav>
        <ul>
          <li><Link to="/"><FontAwesomeIcon icon={faHome} /></Link></li>
          <li><Link to="/search">Search</Link></li>
          <li><Link to="/regex_search">RegEx Search</Link></li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
