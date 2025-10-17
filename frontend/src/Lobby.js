import React, { useState, useEffect } from 'react';

function Lobby({ onJoinLobby, onCreateLobby }) {
  const [mode, setMode] = useState('menu'); // 'menu', 'create', 'join'
  const [username, setUsername] = useState('');
  const [lobbyCode, setLobbyCode] = useState('');
  const [error, setError] = useState('');

  const handleCreateLobby = async () => {
    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    try {
      const response = await fetch('http://localhost:8001/lobby/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username.trim() }),
      });

      const data = await response.json();

      if (response.ok) {
        onJoinLobby(data.lobby_id, data.user_id, username.trim());
      } else {
        setError(data.error || 'Failed to create lobby');
      }
    } catch (err) {
      setError('Failed to connect to server');
    }
  };

  const handleJoinLobby = async () => {
    if (!username.trim() || !lobbyCode.trim()) {
      setError('Please enter both username and lobby code');
      return;
    }

    try {
      const response = await fetch('http://localhost:8001/lobby/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          username: username.trim(),
          lobby_id: lobbyCode.trim().toUpperCase()
        }),
      });

      const data = await response.json();

      if (response.ok) {
        onJoinLobby(data.lobby_id, data.user_id, username.trim());
      } else {
        setError(data.error || 'Failed to join lobby');
      }
    } catch (err) {
      setError('Failed to connect to server');
    }
  };

  return (
    <div className="lobby-container">
      <div className="lobby-card">
        <h2>🎭 Collaborative Story Lobby</h2>
        <p>Join up to 3 players in an epic collaborative storytelling adventure!</p>
        
        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {mode === 'menu' && (
          <div className="lobby-menu">
            <div className="username-input">
              <input
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                maxLength={20}
              />
            </div>
            
            <div className="menu-buttons">
              <button 
                className="create-button"
                onClick={() => setMode('create')}
                disabled={!username.trim()}
              >
                🏰 Create New Lobby
              </button>
              <button 
                className="join-button"
                onClick={() => setMode('join')}
                disabled={!username.trim()}
              >
                🚪 Join Existing Lobby
              </button>
            </div>
          </div>
        )}

        {mode === 'create' && (
          <div className="create-lobby">
            <h3>Create New Lobby</h3>
            <p>You'll be the host and can invite others with your lobby code.</p>
            <button 
              className="confirm-button"
              onClick={handleCreateLobby}
            >
              🎮 Start Adventure
            </button>
            <button 
              className="back-button"
              onClick={() => setMode('menu')}
            >
              ← Back
            </button>
          </div>
        )}

        {mode === 'join' && (
          <div className="join-lobby">
            <h3>Join Existing Lobby</h3>
            <div className="lobby-code-input">
              <input
                type="text"
                placeholder="Enter lobby code (e.g., ABC12345)"
                value={lobbyCode}
                onChange={(e) => setLobbyCode(e.target.value.toUpperCase())}
                maxLength={8}
              />
            </div>
            <button 
              className="confirm-button"
              onClick={handleJoinLobby}
            >
              🚪 Join Lobby
            </button>
            <button 
              className="back-button"
              onClick={() => setMode('menu')}
            >
              ← Back
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default Lobby;
