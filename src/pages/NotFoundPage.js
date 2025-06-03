// src/pages/NotFoundPage.js
import React from 'react';
import { Link } from 'react-router-dom';
import { t } from '../services/dataService';

const NotFoundPage = () => {
  return (
    <div className="container mx-auto px-4 py-16 text-center flex flex-col items-center justify-center min-h-[calc(100vh-200px)]">
      <h1 className="text-5xl sm:text-6xl font-bold text-brand-primary mb-4">404</h1>
      <h2 className="text-2xl sm:text-3xl font-semibold mb-6">{t('pageNotFound')}</h2>
      <p className="text-gray-400 mb-8 max-w-md">
        A página que você está procurando não existe ou foi movida. Verifique o endereço ou volte para o início.
      </p>
      <Link
        to="/"
        className="bg-brand-primary hover:bg-brand-secondary text-white font-semibold py-3 px-6 rounded-lg transition duration-300 text-sm sm:text-base"
      >
        {t('goHome')}
      </Link>
    </div>
  );
};

export default NotFoundPage;