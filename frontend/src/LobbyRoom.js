import React, { useState, useEffect } from 'react';

function LobbyRoom({ lobbyId, userId, username, onLeaveLobby }) {
  const [lobby, setLobby] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [selectedChoice, setSelectedChoice] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState('');

  // Poll lobby state
  useEffect(() => {
    const pollLobby = async () => {
      try {
        const response = await fetch(`http://localhost:8001/lobby/${lobbyId}`);
        const data = await response.json();
        
        if (response.ok) {
          setLobby(data.lobby);
        } else {
          setError(data.error || 'Failed to fetch lobby state');
        }
      } catch (err) {
        setError('Failed to connect to server');
      }
    };

    pollLobby();
    const interval = setInterval(pollLobby, 2000); // Poll every 2 seconds
    
    return () => clearInterval(interval);
  }, [lobbyId]);

  const toggleReady = async () => {
    try {
      const response = await fetch('http://localhost:8001/lobby/ready', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          lobby_id: lobbyId,
          ready: !isReady
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setIsReady(!isReady);
        setLobby(data.lobby);
      } else {
        setError(data.error || 'Failed to update ready status');
      }
    } catch (err) {
      setError('Failed to connect to server');
    }
  };

  const submitChoice = async () => {
    if (!selectedChoice) {
      setError('Please select a choice');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8001/lobby/choice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          lobby_id: lobbyId,
          choice: selectedChoice
        }),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.waiting_for_others) {
          // Still waiting for other players
          setLobby(data.lobby);
        } else {
          // Story progressed
          setLobby(data.lobby);
          setSelectedChoice('');
        }
      } else {
        setError(data.error || 'Failed to submit choice');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  const leaveLobby = async () => {
    try {
      await fetch('http://localhost:8001/lobby/leave', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          lobby_id: lobbyId
        }),
      });
      
      onLeaveLobby();
    } catch (err) {
      console.error('Failed to leave lobby:', err);
      onLeaveLobby(); // Leave anyway
    }
  };

  if (!lobby) {
    return (
      <div className="lobby-room">
        <div className="loading">Loading lobby...</div>
      </div>
    );
  }

  const isHost = userId === lobby.host_user_id;
  const currentUser = lobby.users[userId];
  const otherUsers = Object.entries(lobby.users).filter(([uid]) => uid !== userId);
  const allReady = Object.values(lobby.users).every(user => user.ready);
  const playerCount = Object.keys(lobby.users).length;
  const canStart = playerCount >= 2 && allReady;
  const allChosen = Object.values(lobby.users).every(user => user.choice !== null);

  return (
    <div className="lobby-room">
      <div className="lobby-header">
        <div className="lobby-info">
          <h2>🎭 Lobby: {lobbyId}</h2>
          <div className="lobby-stats">
            <span>Players: {playerCount}/3</span>
            <span>Events: {lobby.events_remaining}/10</span>
            <span>Round: {lobby.current_round}</span>
          </div>
        </div>
        <button className="leave-button" onClick={leaveLobby}>
          🚪 Leave Lobby
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* Player List */}
      <div className="players-section">
        <h3>Players</h3>
        <div className="players-list">
          <div className={`player ${isHost ? 'host' : ''}`}>
            <span className="player-name">{currentUser.username} (You)</span>
            <span className="player-status">
              {isHost ? '👑 Host' : '👤 Player'}
              {currentUser.ready ? ' ✅ Ready' : ' ⏳ Not Ready'}
            </span>
          </div>
          {otherUsers.map(([uid, user]) => (
            <div key={uid} className="player">
              <span className="player-name">{user.username}</span>
              <span className="player-status">
                {user.ready ? ' ✅ Ready' : ' ⏳ Not Ready'}
                {user.choice ? ' 🎯 Chosen' : ''}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Ready Section */}
      {lobby.status === 'waiting' && (
        <div className="ready-section">
          <h3>Ready Up!</h3>
          <p>All players must be ready to start the adventure.</p>
          <button 
            className={`ready-button ${isReady ? 'ready' : 'not-ready'}`}
            onClick={toggleReady}
          >
            {isReady ? '✅ Ready!' : '⏳ Not Ready'}
          </button>
          
          {canStart && (
            <div className="start-section">
              <p>🎮 All players ready! The adventure can begin!</p>
              <button 
                className="start-button"
                disabled={isStarting}
                onClick={async () => {
                  if (isStarting) return;
                  setIsStarting(true);
                  setError('');
                  try {
                    const response = await fetch('http://localhost:8001/lobby/start', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ lobby_id: lobbyId, user_id: userId })
                    });
                    const data = await response.json();
                    if (response.ok) {
                      setLobby(data.lobby);
                    } else {
                      setError(data.error || 'Failed to start lobby');
                    }
                  } catch (err) {
                    setError('Failed to connect to server');
                  } finally {
                    setIsStarting(false);
                  }
                }}
              >
                {isStarting ? '⏳ Starting...' : '🚀 Start Adventure'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Story Section */}
      {lobby.status === 'playing' && (
        <div className="story-section">
          <h3>Collaborative Story</h3>
          
          {/* Story Messages */}
          <div className="story-messages">
            {lobby.story_messages.map((msg, index) => (
              <div key={index} className={`story-message ${msg.type || 'user'}`}>
                {msg.type === 'collaborative' ? (
                  <div>
                    <div className="message-header">🎭 Collaborative Story</div>
                    <div className="message-content">{msg.content}</div>
                    {msg.user_choices && (
                      <div className="user-choices">
                        <h4>Player Choices:</h4>
                        {Object.entries(msg.user_choices).map(([uid, choice]) => (
                          <div key={uid} className="choice-item">
                            <strong>{lobby.users[uid]?.username}:</strong> {choice}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    <div className="message-header">👤 {msg.username}</div>
                    <div className="message-content">{msg.content}</div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Choice Selection */}
          {!lobby.story_complete && !allChosen && (
            <div className="choice-section">
              <h4>Choose Your Action:</h4>
              <div className="choice-options">
                {lobby.story_messages.length > 0 && 
                 lobby.story_messages[lobby.story_messages.length - 1].player_options?.[userId]?.options?.map((option, index) => (
                  <button
                    key={index}
                    className={`choice-button ${selectedChoice === option ? 'selected' : ''}`}
                    onClick={() => setSelectedChoice(option)}
                    disabled={isLoading}
                  >
                    {option}
                  </button>
                ))}
              </div>
              
              {selectedChoice && (
                <button 
                  className="submit-choice-button"
                  onClick={submitChoice}
                  disabled={isLoading}
                >
                  {isLoading ? '⏳ Submitting...' : '🎯 Submit Choice'}
                </button>
              )}
            </div>
          )}

          {/* Waiting for Others */}
          {!lobby.story_complete && allChosen && (
            <div className="waiting-section">
              <h4>⏳ Waiting for other players to choose...</h4>
              <div className="waiting-status">
                {Object.entries(lobby.users).map(([uid, user]) => (
                  <div key={uid} className="waiting-player">
                    <span>{user.username}:</span>
                    <span>{user.choice ? '✅ Chosen' : '⏳ Choosing...'}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Story Complete */}
          {lobby.story_complete && (
            <div className="story-complete">
              <h3>🎉 Story Complete!</h3>
              <p>Your collaborative adventure has reached its conclusion!</p>
              <button className="new-adventure-button" onClick={leaveLobby}>
                🆕 Start New Adventure
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default LobbyRoom;
