// src/pages/QuizPage.js
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getContentSetById, getCardsForSet, t } from '../services/dataService';
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

const QuizPage = () => {
  const { setId, cardIndex } = useParams();
  const navigate = useNavigate();
  const [contentSet, setContentSet] = useState(null);
  const [cards, setCards] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
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
          
          // Set current card index from URL parameter or default to 0
          const index = cardIndex ? parseInt(cardIndex) : 0;
          setCurrentCardIndex(Math.max(0, Math.min(index, cardsForSet.length - 1)));
        } else {
          setError(t('pageNotFound'));
        }
      } catch (err) {
        console.error(`Error loading quiz data for ${setId}:`, err);
        setError(t('errorLoadingSetDetails'));
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [setId, cardIndex]);

  // Update URL when card index changes
  useEffect(() => {
    if (cards.length > 0 && !loading) {
      navigate(`/set/${setId}/quiz/${currentCardIndex}`, { replace: true });
    }
  }, [currentCardIndex, setId, navigate, cards.length, loading]);
  const goToNextCard = () => {
    if (currentCardIndex < cards.length - 1) {
      setCurrentCardIndex(currentCardIndex + 1);
      setShowAnswer(false);
    }
  };

  const goToPreviousCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(currentCardIndex - 1);
      setShowAnswer(false);
    }
  };

  const toggleAnswer = () => {
    setShowAnswer(!showAnswer);
  };

  if (loading) {
    return <div className="container mx-auto px-4 py-8 text-center">{t('loading')}</div>;
  }

  if (error || !contentSet || cards.length === 0) {
    return (
      <div className="container mx-auto px-4 py-8 text-center">
        <h1 className="text-2xl font-bold mb-4 text-red-400">{error || t('pageNotFound')}</h1>
        <Link to={`/set/${setId}`} className="text-brand-primary hover:underline mr-4">{t('backToSet')}</Link>
        <Link to="/" className="text-brand-primary hover:underline">{t('goHome')}</Link>
      </div>
    );
  }

  const currentCard = cards[currentCardIndex];
  const progress = ((currentCardIndex + 1) / cards.length) * 100;

  // Get color scheme from content set (with fallback)
  const colorScheme = contentSet.color_scheme || {
    primary: '#3B82F6',
    secondary: '#1E40AF',
    accent: '#60A5FA'
  };
  return (
    <div className="bg-gray-900 min-h-screen">
      {/* Header with progress */}
      <div className="bg-gray-800 border-b border-gray-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-2">
            <Link 
              to={`/set/${setId}`} 
              className="text-sm hover:underline"
              style={{ color: colorScheme.primary }}
            >
              ← {t('backToSet')}
            </Link>
            <span className="text-sm text-gray-400">
              {currentCardIndex + 1} de {cards.length}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div 
              className="h-2 rounded-full transition-all duration-300"
              style={{ 
                width: `${progress}%`, 
                backgroundColor: colorScheme.primary 
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Main Quiz Content */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="bg-gray-800 rounded-lg shadow-xl overflow-hidden">
          {/* Card Content */}
          <div className="p-6 md:p-8">
            {/* Question */}
            <div className="mb-8">
              <h1 className="text-2xl md:text-3xl font-bold mb-4 text-white">
                {currentCard.title}
              </h1>
              
              {/* Tip/Summary */}
              <div 
                className="p-4 rounded-lg mb-6"
                style={{ backgroundColor: `${colorScheme.primary}20` }}
              >
                <p 
                  className="text-sm font-medium mb-1"
                  style={{ color: colorScheme.primary }}
                >
                  💡 Dica:
                </p>
                <p className="text-gray-300">{currentCard.summary}</p>
              </div>
            </div>
            {/* Answer Section */}
            {showAnswer && (
              <div className="mb-8 animate-fadeIn">
                <div className="bg-gray-700 p-6 rounded-lg">
                  <h3 
                    className="text-lg font-semibold mb-3"
                    style={{ color: colorScheme.accent }}
                  >
                    📖 Resposta:
                  </h3>
                  <div className="prose prose-invert max-w-none">
                    <p className="text-gray-200 leading-relaxed whitespace-pre-wrap">
                      {currentCard.detailed_content}
                    </p>
                  </div>
                  
                  {/* Media if available */}
                  {currentCard.media && currentCard.media.length > 0 && (
                    <div className="mt-4 flex justify-center">
                      {currentCard.media.map((media, index) => (
                        media.media_type === 'image' && (
                          <img 
                            key={index}
                            src={media.url} 
                            alt={media.alt_text}
                            className="w-full max-w-md rounded-lg shadow-lg"
                            style={{ 
                              aspectRatio: '2/3',
                              objectFit: 'cover',
                              objectPosition: 'center top',
                              maxWidth: '500px'
                            }}
                            onError={(e) => {
                              // Fallback to placeholder if image fails to load
                              e.target.src = `https://placehold.co/400x600/374151/9CA3AF?text=${encodeURIComponent(media.alt_text || 'Imagem não disponível')}`;
                            }}
                          />
                        )
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              {!showAnswer ? (
                <button
                  onClick={toggleAnswer}
                  className="flex-1 py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200 transform hover:scale-105"
                  style={{ backgroundColor: colorScheme.primary }}
                >
                  🔍 Mostrar a Resposta
                </button>
              ) : (
                <div className="flex gap-4 w-full">
                  <button
                    onClick={toggleAnswer}
                    className="flex-1 py-3 px-6 rounded-lg font-semibold border-2 transition-all duration-200"
                    style={{ 
                      borderColor: colorScheme.primary,
                      color: colorScheme.primary
                    }}
                  >
                    🔒 Ocultar Resposta
                  </button>
                  
                  {currentCardIndex < cards.length - 1 ? (
                    <button
                      onClick={goToNextCard}
                      className="flex-1 py-3 px-6 rounded-lg font-semibold text-white transition-all duration-200 transform hover:scale-105"
                      style={{ backgroundColor: colorScheme.secondary }}
                    >
                      Próxima Pergunta →
                    </button>
                  ) : (
                    <Link
                      to={`/set/${setId}`}
                      className="flex-1 py-3 px-6 rounded-lg font-semibold text-center text-white transition-all duration-200 transform hover:scale-105"
                      style={{ backgroundColor: colorScheme.accent }}
                    >
                      🎉 Finalizar Quiz
                    </Link>
                  )}
                </div>
              )}
            </div>
          </div>
          {/* Navigation Footer */}
          <div className="bg-gray-750 px-6 py-4 border-t border-gray-700">
            <div className="flex justify-between items-center">
              <button
                onClick={goToPreviousCard}
                disabled={currentCardIndex === 0}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ 
                  color: currentCardIndex === 0 ? '#6B7280' : colorScheme.primary 
                }}
              >
                <ChevronLeftIcon className="h-5 w-5" />
                Anterior
              </button>
              
              <div className="text-sm text-gray-400">
                Cartão {currentCardIndex + 1} de {cards.length}
              </div>
              
              <button
                onClick={goToNextCard}
                disabled={currentCardIndex === cards.length - 1}
                className="flex items-center gap-2 px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ 
                  color: currentCardIndex === cards.length - 1 ? '#6B7280' : colorScheme.primary 
                }}
              >
                Próxima
                <ChevronRightIcon className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizPage;