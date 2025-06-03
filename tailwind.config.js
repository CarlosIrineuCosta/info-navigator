// tailwind.config.js
/** @type {import('tailwindcss').Config} */
const defaultTheme = require('tailwindcss/defaultTheme'); // Import defaultTheme

module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      fontFamily: {
        // Set Montserrat as the default sans-serif font
        sans: ['Montserrat', ...defaultTheme.fontFamily.sans],
        // Add Lato as an alternative if needed, or for specific elements
        lato: ['Lato', ...defaultTheme.fontFamily.sans],
      },
      colors: {
        'brand-primary': '#00a8e1',
        'brand-secondary': '#005f73',
        'gray-900': '#1a202c',
        'gray-800': '#2d3748',
        'gray-700': '#4a5568',
        'gray-600': '#718096',
      },
      height: {
        'banner-mobile': '60vh',
        'banner-desktop': '70vh',
      }
    },
  },
  plugins: [
    // Line clamp is now built into Tailwind CSS v3.3+ as 'line-clamp-*' utilities
  ],
}