import React, { useState, useEffect } from 'react';
import './App.css';

// Backend API URL - Change this to your cloud backend IP/URL
const API_URL = 'http://localhost:8000';  // TODO: Replace with your backend URL

// Available models (will be fetched from backend)
const DEFAULT_MODELS = [
  { id: 'gpt-2', name: 'GPT-2' },
  { id: 'tiny-llama', name: 'TinyLlama 1.1B' },
  { id: 'mistral-7b', name: 'Mistral 7B Instruct' },
  { id: 'llama-2-7b', name: 'Llama 2 7B Chat' },
  { id: 'falcon-7b', name: 'Falcon 7B Instruct' },
  { id: 'phi-2', name: 'Microsoft Phi-2' },
];

function App() {
  const [models, setModels] = useState(DEFAULT_MODELS);
  const [model1, setModel1] = useState(DEFAULT_MODELS[0].id);
  const [model2, setModel2] = useState(DEFAULT_MODELS[1].id);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [error, setError] = useState(null);

  // Fetch available models from backend
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await fetch(`${API_URL}/models`);
        if (response.ok) {
          const data = await response.json();
          // API now returns array directly
          const modelsList = Array.isArray(data) ? data : data.models || [];
          
          if (modelsList.length > 0) {
            const formattedModels = modelsList.map(m => ({
              id: m.id,
              name: m.name,
              available: m.available,  // New field: TGI endpoint health status
              endpoint: m.endpoint
            }));
            setModels(formattedModels);
            setBackendStatus('connected');
          }
        } else {
          setBackendStatus('disconnected');
        }
      } catch (error) {
        console.error('Failed to fetch models:', error);
        setBackendStatus('disconnected');
      }
    };

    fetchModels();
    
    // Refresh model status every 30 seconds
    const interval = setInterval(fetchModels, 30000);
    return () => clearInterval(interval);
  }, []);

  // Generate response using backend API
  const generateResponse = async (modelId, userMessage) => {
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model_id: modelId,
          prompt: userMessage,
          max_new_tokens: 200,
          temperature: 0.7,
          top_p: 0.95,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Generation failed');
      }

      const data = await response.json();
      return data.generated_text;
    } catch (error) {
      console.error(`Error generating response from ${modelId}:`, error);
      return `Error: ${error.message}. Make sure the backend server is running and Docker is available.`;
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setError(null);

    // Add user message
    const newMessage = {
      id: Date.now(),
      user: userMessage,
      model1: null,
      model2: null,
    };
    setMessages(prev => [...prev, newMessage]);

    // Generate responses from both models
    try {
      const [response1, response2] = await Promise.all([
        generateResponse(model1, userMessage),
        generateResponse(model2, userMessage),
      ]);

      setMessages(prev =>
        prev.map(msg =>
          msg.id === newMessage.id
            ? { ...msg, model1: response1, model2: response2 }
            : msg
        )
      );
    } catch (error) {
      console.error('Error generating responses:', error);
      setError('Failed to generate responses. Check console for details.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="App">
      <header className="header">
        <h1>LLM Model Comparison</h1>
        <p>Compare responses from different language models side by side</p>
        <div className={`status-indicator ${backendStatus}`}>
          {backendStatus === 'connected' && '✓ Backend Connected'}
          {backendStatus === 'disconnected' && '✗ Backend Disconnected'}
          {backendStatus === 'checking' && '⟳ Checking...'}
        </div>
      </header>

      <div className="model-selectors">
        <div className="selector-group">
          <label htmlFor="model1">Model 1:</label>
          <select
            id="model1"
            value={model1}
            onChange={(e) => setModel1(e.target.value)}
            disabled={isLoading}
          >
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name} {model.available ? '✓' : '✗'}
              </option>
            ))}
          </select>
        </div>

        <div className="selector-group">
          <label htmlFor="model2">Model 2:</label>
          <select
            id="model2"
            value={model2}
            onChange={(e) => setModel2(e.target.value)}
            disabled={isLoading}
          >
            {models.map(model => (
              <option key={model.id} value={model.id}>
                {model.name} {model.available ? '✓' : '✗'}
              </option>
            ))}
          </select>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <div className="chat-container">
        <div className="messages-wrapper">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>Start a conversation to compare model responses</p>
            </div>
          ) : (
            messages.map((message) => (
              <div key={message.id} className="message-group">
                <div className="user-message">
                  <div className="message-label">You</div>
                  <div className="message-content user">{message.user}</div>
                </div>

                <div className="responses-container">
                  <div className="response-box">
                    <div className="message-label">
                      {models.find(m => m.id === model1)?.name || model1}
                    </div>
                    <div className="message-content assistant">
                      {message.model1 || (
                        <span className="loading">Generating response...</span>
                      )}
                    </div>
                  </div>

                  <div className="response-box">
                    <div className="message-label">
                      {models.find(m => m.id === model2)?.name || model2}
                    </div>
                    <div className="message-content assistant">
                      {message.model2 || (
                        <span className="loading">Generating response...</span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="input-container">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here... (Press Enter to send)"
          disabled={isLoading}
          rows="3"
        />
        <button onClick={handleSend} disabled={isLoading || !input.trim()}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </div>
  );
}

export default App;
