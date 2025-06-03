// src/components/ContentRow.js
import React, { useRef } from 'react';
import ContentCard from './ContentCard';
// Make sure you have @heroicons/react installed: npm install @heroicons/react
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/react/24/solid';

const ContentRow = ({ title, contentSets }) => {
  const scrollRef = useRef(null);

  if (!contentSets || contentSets.length === 0) {
    return null;
  }

  const scroll = (direction) => {
    if (scrollRef.current) {
      const { scrollLeft, clientWidth } = scrollRef.current;
      const scrollAmount = clientWidth * 0.8; // Scroll by 80% of visible width
      const scrollTo = direction === 'left' 
        ? scrollLeft - scrollAmount
        : scrollLeft + scrollAmount;
      scrollRef.current.scrollTo({ left: scrollTo, behavior: 'smooth' });
    }
  };

  return (
    <div className="py-6 md:py-8 relative group">
      <h2 className="text-xl md:text-2xl font-semibold mb-3 md:mb-4 px-4 sm:px-6 lg:px-8">{title}</h2>
      <div className="relative">
        {contentSets.length > 2 && ( // Show scroll buttons if there's enough content to scroll
          <>
            <button 
              onClick={() => scroll('left')}
              className="absolute left-0 top-1/2 -translate-y-1/2 z-20 p-2 bg-black bg-opacity-50 hover:bg-opacity-75 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 ml-1 sm:ml-2 focus:outline-none"
              aria-label="Scroll Left"
            >
              <ChevronLeftIcon className="h-6 w-6 md:h-8 md:w-8" />
            </button>
            <button 
              onClick={() => scroll('right')}
              className="absolute right-0 top-1/2 -translate-y-1/2 z-20 p-2 bg-black bg-opacity-50 hover:bg-opacity-75 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity duration-300 mr-1 sm:mr-2 focus:outline-none"
              aria-label="Scroll Right"
            >
              <ChevronRightIcon className="h-6 w-6 md:h-8 md:w-8" />
            </button>
          </>
        )}
        <div 
          ref={scrollRef} 
          className="flex overflow-x-auto pb-4 space-x-3 md:space-x-4 px-4 sm:px-6 lg:px-8 horizontal-scrollbar"
        >
          {contentSets.map((set) => (
            <div key={set.set_id} className="flex-shrink-0 w-48 sm:w-56 md:w-64 lg:w-72 h-full">
              <ContentCard contentSet={set} />
            </div>
          ))}
          <div className="flex-shrink-0 w-1"></div> {/* Spacer */}
        </div>
      </div>
    </div>
  );
};

export default ContentRow;