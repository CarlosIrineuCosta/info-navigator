# InfoNavigator PWA - Viewer Skeleton

This project is a functional skeleton for the Box_i Quiz App, built as a Progressive Web App (PWA) using React and Tailwind CSS. It's designed to be easily deployable to static hosting services like GitHub Pages, Netlify, or Vercel.

## ⚠️ WARNING - TODO

**URGENT**: Database structure and Builder integration changes needed:

### 🔧 Implemented (Ready for testing):
1. **✅ Set Numbering**: Added `set_number` field (s001, s002, s003) to content_sets.json
2. **✅ Card Numbering**: Added `card_number` field (c001, c002, etc.) to cards.json  
3. **✅ Image Organization**: Created `/public/images/sets/{set_number}/` structure with subfolders
4. **✅ Path Updates**: Updated JSON to use `./images/sets/s001/banner.jpg` format
5. **✅ Fallback System**: Images gracefully fallback to placeholders if missing

### 🚨 Builder Integration Required:
1. **Database Structure**: See `DATABASE_STRUCTURE.md` for complete field specifications
2. **Auto-numbering**: Builder must generate `set_number` and `card_number` fields
3. **Creator ID Validation**: System must check `creator_id` availability before creation
4. **Image Path Generation**: Auto-generate paths using new numbering system
5. **Color Scheme UI**: Interface for selecting per-set color themes

### 📸 Quick Image Testing:
- Drop images into `/public/images/sets/s001/`, `/s002/`, `/s003/` folders
- Naming: `banner.jpg`, `thumbnail.jpg`, `cards/c001.jpg`, etc.
- See folder README.md files for specific guidance
- Missing images automatically show placeholders

## Features

- **Netflix/Amazon Prime-style Homepage:**
    - Hero banner for featured content.
    - Horizontally scrollable rows for "Popular" and "Featured" quiz sets.
- **Static Data:** Fetches quiz data (creators, content sets, cards) from local JSON files in the `public/data` directory.
- **Responsive Design:** Adapts to various screen sizes (desktop and mobile).
- **Basic PWA Capabilities:** Includes a `manifest.json` and setup for service workers (via Create React App). Service worker registration is commented out by default in `src/index.js` but can be enabled.
- **Portuguese UI:** All user-facing strings are in Portuguese and managed for potential future i18n.
- **Routing:** Uses `HashRouter` for better compatibility with static hosting (especially GitHub Pages).
    - Homepage (`/`)
    - Content Set Detail Page (`/#/set/:setId`)
    - 404 Not Found Page

## Project Structure

(Refer to the directory structure provided earlier in the main response)

## Getting Started

### Prerequisites

- Node.js (v16 or later recommended)
- npm or yarn

### Installation

1.  **Create your project folder.**
2.  **Set up the file structure** as outlined above and copy the content for each file provided.
3.  **Navigate to the project directory:**
    ```bash
    cd your-project-directory
    ```
4.  **Install dependencies:**
    ```bash
    npm install
    # OR
    yarn install
    ```
    *If `package.json` was created manually, ensure all dependencies listed are installed. If you started with `npx create-react-app my-app`, you'll need to add `react-router-dom`, `tailwindcss`, `@heroicons/react`, and `@tailwindcss/line-clamp` (optional).*
    ```bash
    npm install react-router-dom tailwindcss @heroicons/react @tailwindcss/line-clamp
    npm install -D tailwindcss 
    npx tailwindcss init # if you haven't already, to create tailwind.config.js. Then, configure it.
    ```


### Running the Development Server

```bash
npm start
# OR
yarn start