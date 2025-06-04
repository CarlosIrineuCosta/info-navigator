// src/services/dataService.js
import translations from '../translations/pt.json'; // Import directly

export const t = (key, replacements = {}) => {
  let translation = translations[key] || key;
  Object.keys(replacements).forEach(rKey => {
    translation = translation.replace(new RegExp(`{{${rKey}}}`, 'g'), replacements[rKey]);
  });
  return translation;
};

const fetchData = async (url) => {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status} for URL: ${url}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Could not fetch data from ${url}:`, error);
    return []; // Return empty array on error to prevent app crashes
  }
};

export const getCreators = async () => {
  return fetchData('./data/creators.json');
};

export const getContentSets = async () => {
  return fetchData('./data/content_sets.json');
};

export const getCardsForSet = async (setId) => {
  const allCards = await fetchData('./data/cards.json');
  return allCards.filter(card => card.set_id === setId);
};

export const getContentSetById = async (setId) => {
  const contentSets = await getContentSets();
  const creators = await getCreators();
  
  const contentSet = contentSets.find(set => set.set_id === setId);
  if (!contentSet) {
    return null;
  }
  
  // Add creator information (same logic as getHomepageData)
  const creatorsMap = new Map(creators.map(creator => [creator.creator_id, creator]));
  return {
    ...contentSet,
    creator: creatorsMap.get(contentSet.creator_id) || { display_name: 'Autor Desconhecido' }
  };
};

export const getHomepageData = async () => {
  const rawContentSets = await getContentSets();
  const rawCreators = await getCreators();

  if (!rawContentSets || rawContentSets.length === 0) {
    return {
      heroSet: null,
      popularSets: [],
      featuredSets: [],
      allSetsWithCreator: []
    };
  }

  const creatorsMap = new Map(rawCreators.map(creator => [creator.creator_id, creator]));

  const contentSets = rawContentSets.map(set => ({
    ...set,
    creator: creatorsMap.get(set.creator_id) || { display_name: 'Autor Desconhecido' } // Fallback for creator
  }));

  let heroSet = contentSets.find(set => set.is_hero) || contentSets[0] || null;
  
  let popularSets = [];
  let featuredSets = [];

  // Prioritize 'tags_pt' if available
  const setsTaggedPopular = contentSets.filter(set => set.tags_pt && set.tags_pt.includes("Populares"));
  const setsTaggedFeatured = contentSets.filter(set => set.tags_pt && set.tags_pt.includes("Destaques") && set.set_id !== (heroSet ? heroSet.set_id : null));

  if (setsTaggedPopular.length > 0) {
    popularSets = setsTaggedPopular;
  }
  if (setsTaggedFeatured.length > 0) {
    featuredSets = setsTaggedFeatured;
  }

  // Fallback to slicing if tags are not sufficient or not present
  if (popularSets.length === 0) {
    let startIndex = heroSet ? 1 : 0; // Skip hero set if it's the first one
    if (heroSet && contentSets.length > 0 && heroSet.set_id !== contentSets[0].set_id) {
        // If heroSet is defined but not the first item, we need to be careful with slicing
        // This case might be complex if heroSet is in the middle. For simplicity,
        // we assume heroSet is usually the first or explicitly tagged.
        // If not, the filtering by set_id should handle it.
    }
    popularSets = contentSets.filter(s => s.set_id !== (heroSet ? heroSet.set_id : null)).slice(0, 5);
  }
  
  if (featuredSets.length === 0) {
     // Try to get different sets than popular ones
    const remainingSets = contentSets.filter(s => 
        s.set_id !== (heroSet ? heroSet.set_id : null) && 
        !popularSets.find(ps => ps.set_id === s.set_id)
    );
    featuredSets = remainingSets.slice(0, 5);
  }
  
  // Ensure heroSet is not duplicated in popular/featured if it was selected by slicing as contentSets[0]
  if (heroSet) {
      popularSets = popularSets.filter(s => s.set_id !== heroSet.set_id);
      featuredSets = featuredSets.filter(s => s.set_id !== heroSet.set_id);
  }


  return {
    heroSet,
    popularSets: popularSets.slice(0, 5), 
    featuredSets: featuredSets.slice(0, 5),
    allSetsWithCreator: contentSets 
  };
};