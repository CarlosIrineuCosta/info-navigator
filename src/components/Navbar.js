// src/components/Navbar.js
import React from 'react';
import { Link } from 'react-router-dom';
import { t } from '../services/dataService';

const Navbar = () => {
  return (
    <nav className="bg-gray-800 shadow-lg sticky top-0 z-50">
      <div className="container mx-auto px-4 sm:px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="text-xl sm:text-2xl font-bold text-white">
            <Link to="/">{t('appTitle')}</Link>
          </div>
          <div className="flex items-center">
            <Link to="/" className="px-2 sm:px-3 py-2 text-sm sm:text-base text-gray-300 hover:text-white rounded-md">{t('navHome')}</Link>
            {/* Add more links here if needed */}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;