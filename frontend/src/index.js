// Import core React functionality
import React from 'react';

// ReactDOM is used to render React elements into the DOM
import ReactDOM from 'react-dom/client';

// Global CSS file (you can style the entire app here)
import './index.css';

// Import the main App component (contains your chatbot and layout)
import App from './App';

// Performance monitoring tool (optional)
import reportWebVitals from './reportWebVitals';

// Bootstrap styles and interactivity (like modals, dropdowns)
import 'bootstrap/dist/css/bootstrap.min.css'; // Bootstrap CSS styles
import 'bootstrap/dist/js/bootstrap.bundle.min.js'; // Bootstrap JS (for interactive components)

// React 18+ way to create root and render the app
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render your App inside <React.StrictMode> (helps with development warnings)
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Optional: Collect app performance metrics (e.g., TTFB, CLS, etc.)
reportWebVitals();
// You can replace reportWebVitals() with:
// reportWebVitals(console.log)
// to see results in the browser console

