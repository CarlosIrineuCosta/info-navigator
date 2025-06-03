# InfoNavigator PWA - Viewer Skeleton

This project is a functional skeleton for the Box_i Quiz App, built as a Progressive Web App (PWA) using React and Tailwind CSS. It's designed to be easily deployable to static hosting services like GitHub Pages, Netlify, or Vercel.

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