// App.js
import React, { useState } from 'react';
import './App.css'; // Ensure this file exists
import { VscFilePdf } from "react-icons/vsc";
import { IoSend } from "react-icons/io5";
import { BsChatLeft } from "react-icons/bs";

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [files, setFiles] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleSend = () => {
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
    }
  };

  const handleFileUpload = (event) => {
    const uploadedFile = event.target.files[0];
    if (uploadedFile) {
      setFiles([...files, { name: uploadedFile.name }]);
    }
  };

  return (
    <div className="gemini-app-container">
      {/* Sidebar - Gemini style */}
      <div className={`gemini-sidebar ${isSidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn">
            <BsChatLeft size={20} />
            <span style={{ marginLeft: '10px' }}>New Chat</span>
          </button>
        </div>
        <div className="file-list">
          {files.length > 0 ? (
            files.map((file, index) => <div key={index} className="file-item">{file.name}</div>)
          ) : (
            <div className="no-files-text">No files uploaded</div>
          )}
        </div>
      </div>

      {/* Main chat interface */}
      <div className="gemini-main-container">
        {/* Top bar with menu button */}
        <div className="top-bar">
          <button className="menu-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
              <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"></path>
            </svg>
          </button>
        </div>

        {/* Conversation box */}
        <div className="gemini-conversation-box">
          {messages.length === 0 ? (
            <div className="welcome-message-container">
              <h1>Hello, how can I help you today?</h1>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`gemini-message ${message.sender}`}>
                {message.text}
              </div>
            ))
          )}
        </div>

        {/* Floating input box */}
        <div className="gemini-input-area">
          <div className="input-field-wrapper">
            <input
              type="text"
              className="gemini-chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Message Gemini"
            />
            <div className="input-buttons">
              <label className="gemini-upload-btn">
                <VscFilePdf size={24} style={{ cursor: 'pointer', color: '#5f6368' }} />
                <input type="file" onChange={handleFileUpload} accept=".pdf" style={{ display: 'none' }} />
              </label>
              <button className="gemini-send-btn" onClick={handleSend} disabled={!input.trim()}>
                <IoSend size={24} style={{ color: 'white' }} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;