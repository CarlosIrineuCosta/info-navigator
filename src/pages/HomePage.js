// src/pages/HomePage.js
import React, { useEffect, useState } from 'react';
import HeroBanner from '../components/HeroBanner';
import ContentRow from '../components/ContentRow';
import { getHomepageData, t } from '../services/dataService';

const HomePage = () => {
  const [homepageData, setHomepageData] = useState({
    heroSet: null,
    popularSets: [],
    featuredSets: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getHomepageData();
        setHomepageData(data);
      } catch (err) {
        console.error("Error loading homepage data:", err);
        setError(t('errorLoadingContent'));
        setHomepageData({ heroSet: null, popularSets: [], featuredSets: [] });
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-200px)]"> {/* Adjust height based on Nav/Footer */}
        <div className="text-xl">{t('loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[calc(100vh-200px)] p-4 text-center">
        <div className="text-xl text-red-400 bg-red-900 bg-opacity-50 p-6 rounded-lg">{error}</div>
      </div>
    );
  }
  
  const { heroSet, popularSets, featuredSets } = homepageData;

  const noContent = !heroSet && (!popularSets || popularSets.length === 0) && (!featuredSets || featuredSets.length === 0);

  return (
    <div className="bg-gray-900">
      {heroSet ? <HeroBanner contentSet={heroSet} /> : 
        !loading && !error && <div className="bg-gray-700 h-banner-mobile md:h-banner-desktop flex items-center justify-center text-center p-4">
                                <h1 className="text-3xl md:text-5xl font-bold">{t('appTitle')}</h1>
                              </div>
      }
      
      {popularSets && popularSets.length > 0 && (
        <ContentRow 
          title={t('popularSectionTitle')} 
          contentSets={popularSets} 
        />
      )}
      
      {featuredSets && featuredSets.length > 0 && (
        <ContentRow 
          title={t('featuredSectionTitle')} 
          contentSets={featuredSets} 
        />
      )}

      {noContent && !loading && (
         <div className="text-center py-10 text-gray-500 min-h-[calc(100vh-200px-var(--banner-height,300px))] flex flex-col justify-center items-center"> {/* Adjust banner height variable */}
           <p className="text-xl">{t('noContentAvailable')}</p>
           <p className="text-sm mt-2">Verifique os arquivos de dados em `public/data/` ou adicione novo conteúdo.</p>
         </div>
       )}
    </div>
  );
};

export default HomePage;