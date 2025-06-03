// src/pages/ContentSetPageDebug.js - Simplified debug version
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

const ContentSetPageDebug = () => {
  const { setId } = useParams();
  const [contentSet, setContentSet] = useState(null);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [debugLog, setDebugLog] = useState([]);

  const addLog = (message) => {
    console.log(message);
    setDebugLog(prev => [...prev, `${new Date().toISOString()}: ${message}`]);
  };

  useEffect(() => {
    const loadData = async () => {
      addLog(`Starting loadData for setId: ${setId}`);
      
      if (!setId) {
        addLog('❌ No setId provided');
        setError('No setId');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);
        
        addLog('📄 Loading content sets...');
        const response1 = await fetch('./data/content_sets.json');
        addLog(`Content sets response: ${response1.status} ${response1.ok}`);
        const contentSets = await response1.json();
        addLog(`Content sets loaded: ${contentSets.length} items`);
        
        addLog('👤 Loading creators...');
        const response2 = await fetch('./data/creators.json');
        addLog(`Creators response: ${response2.status} ${response2.ok}`);
        const creators = await response2.json();
        addLog(`Creators loaded: ${creators.length} items`);
        
        addLog(`🔍 Looking for setId: ${setId}`);
        const foundSet = contentSets.find(set => set.set_id === setId);
        addLog(`Content set found: ${!!foundSet}`);
        
        if (!foundSet) {
          addLog('❌ Content set not found');
          addLog(`Available IDs: ${contentSets.map(s => s.set_id).join(', ')}`);
          setError('Content set not found');
          return;
        }
        
        addLog(`✅ Found set: ${foundSet.title}`);
        
        // Add creator info
        const creatorsMap = new Map(creators.map(creator => [creator.creator_id, creator]));
        const creator = creatorsMap.get(foundSet.creator_id);
        addLog(`Creator found: ${!!creator} - ${creator?.display_name || 'None'}`);
        
        const setWithCreator = {
          ...foundSet,
          creator: creator || { display_name: 'Autor Desconhecido' }
        };
        
        setContentSet(setWithCreator);
        addLog(`✅ Content set state updated`);
        
        // Load cards
        addLog('🃏 Loading cards...');
        const response3 = await fetch('./data/cards.json');
        addLog(`Cards response: ${response3.status} ${response3.ok}`);
        const allCards = await response3.json();
        addLog(`All cards loaded: ${allCards.length} items`);
        
        const setCards = allCards.filter(card => card.set_id === setId);
        addLog(`Cards for this set: ${setCards.length}`);
        
        setCards(setCards);
        addLog(`✅ Cards state updated`);
        
        addLog('🎯 SUCCESS: All data loaded successfully');
        
      } catch (err) {
        addLog(`💥 ERROR: ${err.message}`);
        console.error(`Error loading content set details for ${setId}:`, err);
        setError('Error loading data: ' + err.message);
      } finally {
        setLoading(false);
        addLog('🏁 Loading finished');
      }
    };
    
    loadData();
  }, [setId]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Debug Loading...</h1>
        <div className="bg-gray-800 p-4 rounded">
          {debugLog.map((log, i) => (
            <div key={i} className="text-sm text-gray-300 font-mono">{log}</div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !contentSet) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4 text-red-400">
          Error: {error || 'Content set not found'}
        </h1>
        <div className="bg-gray-800 p-4 rounded mb-4">
          <h2 className="text-lg font-bold mb-2">Debug Log:</h2>
          {debugLog.map((log, i) => (
            <div key={i} className="text-sm text-gray-300 font-mono">{log}</div>
          ))}
        </div>
        <Link to="/" className="text-brand-primary hover:underline">Go Home</Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4 text-green-400">SUCCESS!</h1>
      <div className="bg-gray-800 p-4 rounded mb-4">
        <h2 className="text-lg font-bold mb-2">Content Set:</h2>
        <p><strong>Title:</strong> {contentSet.title}</p>
        <p><strong>Creator:</strong> {contentSet.creator?.display_name}</p>
        <p><strong>Cards:</strong> {cards.length}</p>
      </div>
      
      <div className="bg-gray-800 p-4 rounded mb-4">
        <h2 className="text-lg font-bold mb-2">Cards:</h2>
        {cards.map((card, i) => (
          <div key={card.card_id || i} className="mb-2 p-2 bg-gray-700 rounded">
            <strong>{card.title}</strong>
            <p className="text-sm text-gray-400">{card.summary}</p>
          </div>
        ))}
      </div>
      
      <div className="bg-gray-800 p-4 rounded">
        <h2 className="text-lg font-bold mb-2">Debug Log:</h2>
        {debugLog.map((log, i) => (
          <div key={i} className="text-xs text-gray-400 font-mono">{log}</div>
        ))}
      </div>
      
      <Link to="/" className="text-brand-primary hover:underline mt-4 block">Go Home</Link>
    </div>
  );
};

export default ContentSetPageDebug;
