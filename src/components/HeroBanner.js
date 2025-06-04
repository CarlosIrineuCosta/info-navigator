// src/components/HeroBanner.js
import React from 'react';
import { Link } from 'react-router-dom';
import { t } from '../services/dataService';

const HeroBanner = ({ contentSet }) => {
  if (!contentSet) {
    return (
      <div className="bg-gray-700 h-banner-mobile md:h-banner-desktop flex items-center justify-center text-center p-4">
        <div className="max-w-2xl">
          <h1 className="text-3xl md:text-5xl font-bold mb-4">{t('appTitle')}</h1>
          <p className="text-lg md:text-xl text-gray-300">{t('loading')}</p>
        </div>
      </div>
    );
  }

  const { set_id, title, description, banner_url, creator } = contentSet;
  const defaultBanner = 'https://placehold.co/1280x720/1a202c/4a5568?text=Box_i';
  const creatorName = creator ? creator.display_name : t('createdBy', { name: 'Desconhecido' });


  return (
    <div
      className="h-banner-mobile md:h-banner-desktop bg-cover bg-no-repeat flex items-end p-4 md:p-8 relative overflow-hidden"
      style={{ 
        backgroundImage: `linear-gradient(to top, rgba(26, 32, 44, 0.95) 0%, rgba(26, 32, 44, 0.8) 20%, rgba(26, 32, 44, 0.3) 60%, transparent 100%), url(${banner_url || defaultBanner})`,
        backgroundPosition: 'center 30%', /* Show more of the upper part */
        backgroundSize: 'cover'
      }}
    >
      <div className="max-w-xl z-10">
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold mb-2 md:mb-4 leading-tight shadow-text">{title || 'Título Indisponível'}</h1>
        {creator && (
          <p className="text-sm md:text-base text-gray-300 mb-1 md:mb-2">
            {t('createdBy')} <span className="font-semibold">{creator.display_name || 'Autor Desconhecido'}</span>
          </p>
        )}
        <p className="text-gray-200 text-sm md:text-lg mb-4 md:mb-6 line-clamp-3">{description || 'Descrição não disponível.'}</p>
        <Link
          to={`/set/${set_id}`}
          className="text-white font-semibold py-2 px-4 md:py-3 md:px-6 rounded-lg text-sm md:text-base transition duration-300 ease-in-out transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-opacity-50"
          style={{ 
            backgroundColor: '#A09CA6',
            border: '2px solid #A09CA6'
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = '#8B8793';
            e.target.style.borderColor = '#8B8793';
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = '#A09CA6';
            e.target.style.borderColor = '#A09CA6';
          }}
        >
          {t('heroActionText')}
        </Link>
      </div>
    </div>
  );
};

export default HeroBanner;