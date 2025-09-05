import React from 'react';
import ReactDOM from 'react-dom/client';
import { useState } from 'react';
import { VscSend } from 'react-icons/vsc';
import { FiUpload } from 'react-icons/fi';
import './index.css';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [uploadedFile, setUploadedFile] = useState(null);

  const handleSendMessage = () => {
    if (input.trim() !== '') {
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
    }
  };

  const handleUploadFile = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left Panel */}
      <div className="w-1/4 p-4 bg-gray-100 border-r border-gray-200">
        <h2 className="text-xl font-semibold mb-4">Files</h2>
        {uploadedFile ? (
          <div className="p-2 bg-white rounded-md shadow-sm">
            <p className="truncate">{uploadedFile.name}</p>
          </div>
        ) : (
          <p className="text-gray-500">No file uploaded.</p>
        )}
      </div>

      {/* Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Conversation Box */}
        <div className="flex-1 p-4 overflow-y-auto bg-white">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400">
              Start a conversation
            </div>
          ) : (
            messages.map((message, index) => (
              <div
                key={index}
                className={`mb-2 p-2 rounded-lg max-w-lg ${
                  message.sender === 'user' ? 'bg-blue-500 text-white self-end ml-auto' : 'bg-gray-200 self-start'
                }`}
              >
                {message.text}
              </div>
            ))
          )}
        </div>

        {/* Input and Buttons */}
        <div className="p-4 bg-gray-100 flex items-center border-t border-gray-200">
          <label htmlFor="file-upload" className="cursor-pointer p-2 rounded-full hover:bg-gray-200">
            <FiUpload size={24} className="text-gray-600" />
            <input
              id="file-upload"
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleUploadFile}
            />
          </label>
          <input
            type="text"
            className="flex-1 mx-4 p-2 rounded-full border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                
                ();
              }
            }}
          />
          <button
            onClick={handleSendMessage}
            className="p-3 bg-blue-500 text-white rounded-full hover:bg-blue-600 transition-colors duration-200"
          >
            <VscSend size={24} />
          </button>
        </div>
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <ChatInterface />
  </React.StrictMode>
);