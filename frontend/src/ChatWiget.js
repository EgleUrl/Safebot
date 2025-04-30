// React and component state
import React, { useState } from "react";

// HTTP client for backend API requests
import axios from "axios";

// UI styles
import "bootstrap/dist/css/bootstrap.min.css";
import "./ChatWiget.css";

// FontAwesome icon
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMessage } from '@fortawesome/free-regular-svg-icons';

// ChatWidget component — shows/hides the chat UI
const ChatWidget = () => {
  // --- State variables ---
  const [open, setOpen] = useState(false);          // Chat open/closed
  const [query, setQuery] = useState("");            // User's current message input
  const [messages, setMessages] = useState([         // Chat message history
    { sender: "bot", text: "Hi! Ask me anything about the university." },
  ]);
  const [loading, setLoading] = useState(false);     // Loading state for backend response

  // Toggles chat open/closed and resets memory
  const toggleChat = async () => {
    if (!open) {
      // Reset chat messages when opening
      setMessages([
        { sender: "bot", text: "Hi! Ask me anything about the university." },
      ]);
      try {
        // Tell the backend to clear conversation memory
        await fetch("http://localhost:8002/clear_memory", { method: "POST" });
      } catch (err) {
        console.error("Failed to clear backend memory:", err);
      }
    }
    setOpen(!open);  // Toggle state
  };

  // Sends message to backend and handles response
  const sendMessage = async (e) => {
    e.preventDefault();  // Prevent form reload
    if (!query.trim()) return;  // Skip if empty

    // Add user's message to chat history
    const newMessages = [...messages, { sender: "user", text: query }];
    setMessages(newMessages);
    setQuery("");       // Clear input
    setLoading(true);   // Show loading

    try {
      // Send query to backend
      const res = await axios.post("http://localhost:8002/ask", { query });
      // Add bot's response
      setMessages((prev) => [...prev, { sender: "bot", text: res.data.response }]);
    } catch {
      // Fallback if API call fails
      setMessages((prev) => [...prev, { sender: "bot", text: "Something went wrong." }]);
    } finally {
      setLoading(false);  // Reset loading spinner
    }
  };

  // --- JSX Render ---
  return (
    <>
      {/* Chat button when closed */}
      {!open && (
        <button className="chat-tab" onClick={toggleChat}>
          Chat with Safebot <FontAwesomeIcon icon={faMessage} beatFade size="lg" />
        </button>
      )}

      {/* Chat UI when open */}
      {open && (
        <div
          className="card shadow-md position-fixed bottom-0 end-0 m-2"
          style={{ width: "330px", maxHeight: "500px", zIndex: 9999 }}
        >
          {/* Header */}
          <div className="card-header bg-white text-black position-relative shadow-sm">
            <h6 className="text-center m-2">Welcome to Chat!</h6>
            {/* Minimize button */}
            <button
              className="btn btn-lg btn-light position-absolute end-0 top-50 translate-middle-y me-2"
              onClick={toggleChat}
            >
              __
            </button>
          </div>

          {/* Chat message body */}
          <div className="card-body bg-light overflow-auto" style={{ maxHeight: "300px" }}>
            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`mb-2 text-${msg.sender === "user" ? "end" : "start"}`}
              >
                <strong style={{ color: msg.sender === "bot" ? "teal" : "black" }}>
                  {msg.sender === "user" ? "You" : "Safebot"}:
                </strong>{" "}
                {msg.text}
              </div>
            ))}
          </div>

          {/* Input + send */}
          <div className="card-footer">
            <form onSubmit={sendMessage}>
              <textarea
                className="form-control"
                rows="2"
                placeholder="Type your question..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button
                type="submit"
                className="btn btn-light w-100 mt-2"
                id="button"
                disabled={loading}
              >
                {loading ? "Thinking..." : "Send"}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default ChatWidget;


