// src/components/Footer.js
import React from 'react';
import { t } from '../services/dataService';

const Footer = () => {
  const currentYear = new Date().getFullYear();
  return (
    <footer className="bg-gray-800 text-gray-400 py-6 text-center">
      <div className="container mx-auto px-4">
        <p className="text-sm">{t('footerText', { year: currentYear })}</p>
      </div>
    </footer>
  );
};

export default Footer;