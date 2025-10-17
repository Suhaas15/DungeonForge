import React, { useState, useRef, useEffect } from 'react';
import Lobby from './Lobby';
import LobbyRoom from './LobbyRoom';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [options, setOptions] = useState([]);
  const [eventsRemaining, setEventsRemaining] = useState(10);
  const [storyComplete, setStoryComplete] = useState(false);
  
  // Lobby state
  const [gameMode, setGameMode] = useState('menu'); // 'menu', 'solo', 'lobby'
  const [lobbyId, setLobbyId] = useState(null);
  const [userId, setUserId] = useState(null);
  const [username, setUsername] = useState('');
  
  const leftPageRef = useRef(null);
  const rightPageRef = useRef(null);

  const scrollToBottom = (ref) => {
    ref.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom(leftPageRef);
    scrollToBottom(rightPageRef);
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputValue.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8001/story', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: userMessage.content,
          eventsRemaining: eventsRemaining
        }),
      });

      const data = await response.json();

      if (response.ok) {
        const aiMessage = {
          type: 'ai',
          content: data.story,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiMessage]);
        setOptions(Array.isArray(data.options) ? data.options : []);
        setEventsRemaining(data.eventsRemaining || 0);
        setStoryComplete(data.storyComplete || false);
      } else {
        setError(data.error || 'Something went wrong');
      }
    } catch (err) {
      setError('Failed to connect to server. Make sure backend is running on port 8001.');
    } finally {
      setIsLoading(false);
    }
  };

  const chooseOption = (opt) => {
    if (storyComplete) return; // Don't allow choices when story is complete
    setInputValue(opt);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (!storyComplete) {
        sendMessage();
      }
    }
  };

  // Lobby management functions
  const handleJoinLobby = (newLobbyId, newUserId, newUsername) => {
    setLobbyId(newLobbyId);
    setUserId(newUserId);
    setUsername(newUsername);
    setGameMode('lobby');
  };

  const handleLeaveLobby = () => {
    setLobbyId(null);
    setUserId(null);
    setUsername('');
    setGameMode('menu');
  };

  const startSoloGame = () => {
    setGameMode('solo');
    // Reset story state
    setMessages([]);
    setEventsRemaining(10);
    setStoryComplete(false);
    setOptions([]);
    setError('');
  };

  // Separate messages for left and right pages
  const aiMessages = messages.filter(msg => msg.type === 'ai');
  const userMessages = messages.filter(msg => msg.type === 'user');

  // Render different modes
  if (gameMode === 'menu') {
    return (
      <div className="game-menu">
        <div className="menu-container">
          <h1>🎭 Dungeon & Dragons AI</h1>
          <p>Choose your adventure style:</p>
          
          <div className="menu-options">
            <button className="menu-button solo-button" onClick={startSoloGame}>
              🎮 Solo Adventure
              <span>Play alone with AI Dungeon Master</span>
            </button>
            
            <button className="menu-button lobby-button" onClick={() => setGameMode('lobby-menu')}>
              👥 Collaborative Story
              <span>Join up to 3 players in shared adventure</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (gameMode === 'lobby-menu') {
    return (
      <Lobby 
        onJoinLobby={handleJoinLobby}
        onCreateLobby={handleJoinLobby}
      />
    );
  }

  if (gameMode === 'lobby') {
    return (
      <LobbyRoom
        lobbyId={lobbyId}
        userId={userId}
        username={username}
        onLeaveLobby={handleLeaveLobby}
      />
    );
  }

  // Solo game mode (existing functionality)
  return (
    <div className="book-container">
      <div className="game-header">
        <button className="back-to-menu" onClick={() => setGameMode('menu')}>
          ← Back to Menu
        </button>
        <h3>Solo Adventure Mode</h3>
      </div>
      
      <div className="open-book">
        <div className="book-spine"></div>
        
        <div className="book-pages">
          {/* Left Page - AI Dungeon Master */}
          <div className="left-page">
            <div className="page-header">
              <div className="page-title">🎭 The Dungeon Master's Tale</div>
              {eventsRemaining > 0 && (
                <div className="events-counter">
                  Events Remaining: {eventsRemaining}
                </div>
              )}
              {storyComplete && (
                <div className="story-complete">
                  🎉 Story Complete! 🎉
                </div>
              )}
            </div>
            
            {aiMessages.length === 0 && !isLoading && (
              <div className="welcome-message">
                <h3>Welcome, Brave Adventurer!</h3>
                <p>I am your AI Dungeon Master, ready to weave epic tales of adventure, mystery, and magic. What story shall we tell together?</p>
              </div>
            )}

            {aiMessages.map((msg, index) => (
              <div key={index} className="message ai-message">
                <div className="message-label">🎭 Dungeon Master</div>
                <div className="message-content story-content">{msg.content}</div>
              </div>
            ))}


            {isLoading && (
              <div className="loading">
                🎭 The Dungeon Master is crafting your story...
              </div>
            )}

            <div ref={leftPageRef} />
          </div>

          {/* Right Page - User Input */}
          <div className="right-page">
            <div className="page-header">
              <div className="page-title">📝 Your Adventure</div>
            </div>

            {userMessages.length === 0 && (
              <div className="welcome-message">
                <h3>Your Turn, Hero!</h3>
                <p>Tell me what happens next in your adventure. Describe your actions, ask questions, or set the scene for our story to unfold.</p>
                <p style={{ marginTop: '20px', fontStyle: 'italic', color: '#8B4513' }}>
                  "You wake up in a mysterious forest..." or "I draw my sword and charge at the dragon!"
                </p>
              </div>
            )}

            {userMessages.map((msg, index) => (
              <div key={index} className="message user-message">
                <div className="message-label">🗡️ You</div>
                <div className="message-content story-content">{msg.content}</div>
              </div>
            ))}

            {options.length > 0 && !storyComplete && (
              <div className="options-panel">
                <div className="options-title">Choose your next action:</div>
                <div className="options-list">
                  {options.map((opt, idx) => (
                    <button key={idx} className="option-button" onClick={() => chooseOption(opt)}>
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <div ref={rightPageRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="input-area">
          {error && (
            <div className="error">
              {error}
            </div>
          )}

          <div className="input-container">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={storyComplete ? "Story complete! Start a new adventure by refreshing the page." : "What happens next in your adventure? Describe your actions, set the scene, or continue the story..."}
              disabled={isLoading || storyComplete}
            />
            <div className="button-group">
              <button 
                className="send-button"
                onClick={() => sendMessage()} 
                disabled={!inputValue.trim() || isLoading || storyComplete}
              >
                📝 Continue Story
              </button>
            </div>
          </div>
          
          <p style={{ 
            textAlign: 'center', 
            marginTop: '10px', 
            fontSize: '0.9em', 
            color: '#8B4513',
            fontStyle: 'italic'
          }}>
            Press Enter to continue • Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;