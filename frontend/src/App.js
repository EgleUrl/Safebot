// React core import
import React from "react";

// Import your custom chatbot widget component
import ChatWidget from "./ChatWiget";

// Import main CSS for page layout/styling
import "./App.css"; // Ensure this file defines .app-background and .centered-box

// Import image asset used as page background (UCP building)
import UCPbuilding from "./UCPbuilding.jpeg";

// Root App component that displays the welcome screen and chat widget
function App() {
  return (
    <div
      className="app-background" // Custom background container (CSS class)
      style={{ backgroundImage: `url(${UCPbuilding})` }} // Sets the background image
    >
      {/* Welcome message container */}
      <div className="centered-box">
        <h1>Welcome to the University Centre Peterborough</h1>
        <h3>Please press the tab at the bottom right of the screen to use Safebot</h3>
      </div>

      {/* Embed the chatbot widget on the page */}
      <ChatWidget />
    </div>
  );
}

// Export this App component so it can be rendered by index.js
export default App;

