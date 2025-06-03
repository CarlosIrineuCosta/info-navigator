// src/pages/ContentSetPage.js
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getContentSetById, getCardsForSet, t } from '../services/dataService';

const ContentSetPage = () => {
  const { setId } = useParams();
  const [contentSet, setContentSet] = useState(null);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      if (!setId) {
        setError(t('pageNotFound'));
        setLoading(false);
        return;
      }
      try {
        setLoading(true);
        setError(null);
        const setDetails = await getContentSetById(setId);
        if (setDetails) {
          setContentSet(setDetails);
          const cardsForSet = await getCardsForSet(setId);
          setCards(cardsForSet);
        } else {
          setError(t('pageNotFound'));
        }
      } catch (err) {
        console.error(`Error loading content set details for ${setId}:`, err);
        setError(t('errorLoadingSetDetails'));
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [setId]);

  if (loading) {
    return <div className="container mx-auto px-4 py-8 text-center">{t('loading')}</div>;
  }

  if (error || !contentSet) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold mb-4 text-red-400">{error || t('pageNotFound')}</h1>
        <Link to="/" className="text-brand-primary hover:underline">{t('goHome')}</Link>
      </div>
    );
  }
  
  const defaultPageBanner = 'https://placehold.co/1280x400/1a202c/4a5568?text=' + encodeURIComponent(contentSet.title);
  const creatorName = contentSet.creator ? contentSet.creator.display_name : 'Autor Desconhecido';

  return (
    <div className="bg-gray-900 min-h-screen">
      <div 
        className="h-64 md:h-80 bg-cover bg-center relative"
        style={{ backgroundImage: `linear-gradient(to top, rgba(26, 32, 44, 1) 0%, rgba(26, 32, 44, 0.7) 40%, transparent 100%), url(${contentSet.banner_url || defaultPageBanner})` }}
      >
        <div className="absolute bottom-0 left-0 p-4 md:p-8 max-w-3xl">
          <h1 className="text-2xl md:text-4xl font-bold mb-1 md:mb-2">{contentSet.title}</h1>
          {contentSet.creator && (
            <p className="text-sm md:text-base text-gray-300">
              {t('createdBy')} <span className="font-semibold">{creatorName}</span>
            </p>
          )}
          <p className="text-xs md:text-sm text-gray-400 line-clamp-2 mt-1">{contentSet.description}</p>
        </div>
      </div>

      <div className="container mx-auto px-4 md:px-8 py-6 md:py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
          <div className="md:col-span-2 bg-gray-800 p-4 md:p-6 rounded-lg shadow-xl">
            <h2 className="text-xl md:text-2xl font-semibold mb-4">{t('totalCardsLabel')} ({cards.length})</h2>
            {cards.length > 0 ? (
              <ul className="space-y-3">
                {cards.map((card, index) => (
                  <li key={card.card_id || index} className="bg-gray-700 p-3 rounded-md hover:bg-gray-600 transition-colors">
                    {/* Link to individual card page (QuizPage - not yet implemented) */}
                    {/* <Link to={`/set/${setId}/card/${card.card_id}`} className="block"> */}
                      <h3 className="text-md md:text-lg font-medium text-brand-primary">{`${index + 1}. ${card.title}`}</h3>
                      <p className="text-xs md:text-sm text-gray-400 truncate mt-1">{card.summary}</p>
                    {/* </Link> */}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-400">{t('noCardsInSet')}</p>
            )}
             <div className="mt-6 text-center">
                <button 
                    // onClick={() => navigateToQuizStart()} // Implement navigation to first card/quiz start
                    disabled // Enable when quiz functionality is ready
                    className="bg-brand-primary hover:bg-brand-secondary text-white font-bold py-2 px-6 md:py-3 md:px-8 rounded-lg transition duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {t('startQuizSoon')}
                </button>
            </div>
          </div>

          <div className="md:col-span-1 bg-gray-800 p-4 md:p-6 rounded-lg shadow-xl self-start sticky top-24"> {/* Sticky for details */}
            <h3 className="text-lg md:text-xl font-semibold mb-4 border-b border-gray-700 pb-2">{t('collectionDetailsTitle')}</h3>
            <div className="space-y-2 text-xs md:text-sm">
              {contentSet.category && <p><strong className="text-gray-400">{t('categoryLabel')}</strong> {contentSet.category}</p>}
              {contentSet.difficulty_level && <p><strong className="text-gray-400">{t('levelLabel')}</strong> {t(`difficulty_${contentSet.difficulty_level}`)}</p>}
              {contentSet.estimated_time_minutes !== undefined && <p><strong className="text-gray-400">{t('estimatedTimeLabel')}</strong> {t('estimatedTime', { time: contentSet.estimated_time_minutes })}</p>}
              {contentSet.card_count !== undefined && <p><strong className="text-gray-400">{t('totalCardsLabel')}</strong> {t('cardsCount', { count: contentSet.card_count })}</p>}
              {contentSet.target_audience && <p><strong className="text-gray-400">{t('targetAudienceLabel')}</strong> {contentSet.target_audience}</p>}
              {contentSet.prerequisites && contentSet.prerequisites.length > 0 && (
                <p><strong className="text-gray-400">{t('prerequisitesLabel')}</strong> {contentSet.prerequisites.join(', ')}</p>
              )}
              {contentSet.tags && contentSet.tags.length > 0 && (
                <div>
                  <strong className="text-gray-400">{t('tagsLabel')}</strong>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {contentSet.tags.map(tag => (
                      <span key={tag} className="bg-gray-700 px-2 py-0.5 rounded text-xs">{tag}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContentSetPage;