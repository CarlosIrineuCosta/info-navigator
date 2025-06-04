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
        className="h-64 md:h-80 bg-cover relative overflow-hidden"
        style={{ 
          backgroundImage: `linear-gradient(to top, rgba(26, 32, 44, 1) 0%, rgba(26, 32, 44, 0.7) 40%, transparent 100%), url(${contentSet.banner_url || defaultPageBanner})`,
          backgroundPosition: 'center 30%', /* Show more of the upper part */
          backgroundSize: 'cover'
        }}
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
            <h2 className="text-xl md:text-2xl font-semibold mb-4">{t('aboutThisCollection')}</h2>
            <p className="text-gray-300 leading-relaxed mb-6">
              {contentSet.description}
            </p>
            
            <div className="text-center">
              <Link 
                to={`/set/${setId}/quiz/0`}
                className="inline-block bg-gray-500 hover:bg-gray-600 text-white font-bold py-3 px-8 rounded-lg transition duration-300 transform hover:scale-105"
                style={{ backgroundColor: '#A09CA6' }}
              >
                🚀 {t('startQuiz')} ({cards.length} {t('cards')})
              </Link>
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