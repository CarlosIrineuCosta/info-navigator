// src/components/ContentCard.js
import React from 'react';
import { Link } from 'react-router-dom';
import { t } from '../services/dataService';

const ContentCard = ({ contentSet }) => {
  if (!contentSet) return null;

  const { set_id, title, thumbnail_url, creator, card_count, estimated_time_minutes } = contentSet;
  const defaultThumbnail = 'https://placehold.co/400x400/2d3748/718096?text=Quiz';
  const creatorName = creator ? creator.display_name : 'Autor Desconhecido';

  return (
    <Link to={`/set/${set_id}`} className="block group h-full">
      <div className="bg-gray-800 rounded-lg overflow-hidden shadow-xl transform transition-all duration-300 ease-in-out hover:scale-105 hover:shadow-2xl w-full h-full flex flex-col">
        <div className="aspect-square w-full"> {/* Square aspect ratio */}
          <img
            src={thumbnail_url || defaultThumbnail}
            alt={title || 'Título do Quiz'}
            className="object-cover w-full h-full group-hover:opacity-80 transition-opacity duration-300"
            onError={(e) => { e.target.onerror = null; e.target.src=defaultThumbnail; }}
          />
        </div>
        <div className="p-3 md:p-4 flex flex-col flex-grow">
          <h3 className="text-base md:text-lg font-semibold text-white truncate group-hover:text-brand-primary transition-colors duration-300" title={title || 'Título do Quiz'}>
            {title || 'Título do Quiz'}
          </h3>
          {creator && (
            <p className="text-xs md:text-sm text-gray-400 truncate mt-1" title={creatorName}>
              {creatorName}
            </p>
          )}
          <div className="mt-auto pt-2 flex items-center justify-between text-xs text-gray-500">
            {card_count !== undefined && <span>{t('cardsCount', { count: card_count })}</span>}
            {estimated_time_minutes !== undefined && <span>{t('estimatedTime', { time: estimated_time_minutes })}</span>}
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ContentCard;