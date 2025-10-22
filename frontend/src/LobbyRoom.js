import React, { useState, useEffect } from 'react';
import { IoArrowBack } from 'react-icons/io5';
import { API_URL } from './config';

function LobbyRoom({ lobbyId, userId, username, onLeaveLobby }) {
  const [lobby, setLobby] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [selectedChoice, setSelectedChoice] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState('');
  const [currentAudio, setCurrentAudio] = useState(null);
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  // Poll lobby state
  useEffect(() => {
    const pollLobby = async () => {
      try {
        const response = await fetch(`${API_URL}/lobby/${lobbyId}`);
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

  // Handle mobile viewport
  useEffect(() => {
    const viewport = document.querySelector('meta[name="viewport"]');
    if (viewport) {
      viewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no');
    }
  }, []);

  const toggleReady = async () => {
    try {
      const response = await fetch(`${API_URL}/lobby/ready`, {
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
      const response = await fetch(`${API_URL}/lobby/choice`, {
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
      await fetch(`${API_URL}/lobby/leave`, {
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

  const playStoryAudio = async (storyText) => {
    if (!storyText) {
      setError('No story to read');
      return;
    }

    // Stop current audio if playing
    if (currentAudio) {
      currentAudio.pause();
      setCurrentAudio(null);
      setIsPlayingAudio(false);
      return;
    }

    setIsPlayingAudio(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/text-to-speech`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: storyText }),
      });

      if (response.ok) {
        const audioBlob = await response.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        
        audio.onended = () => {
          setIsPlayingAudio(false);
          setCurrentAudio(null);
        };
        
        audio.onerror = () => {
          setError('Failed to play audio');
          setIsPlayingAudio(false);
          setCurrentAudio(null);
        };

        setCurrentAudio(audio);
        await audio.play();
      } else {
        const data = await response.json();
        setError(data.error || 'Failed to generate audio');
        setIsPlayingAudio(false);
      }
    } catch (err) {
      setError('Failed to connect to audio service');
      setIsPlayingAudio(false);
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
    <div className="book-container">
      <div className="game-header">
        <button className="back-to-menu" onClick={leaveLobby}>
          <IoArrowBack />
        </button>
        <h3>Lobby: {lobbyId}</h3>
        <div className="lobby-stats-header">
          <span>Players: {playerCount}/3</span>
          <span>Events: {lobby.events_remaining}/10</span>
          <span>Round: {lobby.current_round}</span>
        </div>
      </div>

      <div className="open-book lobby-room-book">
        <div className="book-spine"></div>
        
        <div className="book-pages">
          <div className="left-page lobby-page">

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
                    {isHost ? 'Host' : 'Player'}
                    {currentUser.ready ? ' ✓ Ready' : ' ○ Not Ready'}
                  </span>
                </div>
                {otherUsers.map(([uid, user]) => (
                  <div key={uid} className="player">
                    <span className="player-name">{user.username}</span>
                    <span className="player-status">
                      {user.ready ? ' ✓ Ready' : ' ○ Not Ready'}
                      {user.choice ? ' ✓ Chosen' : ''}
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
                  {isReady ? '✓ Ready!' : '○ Not Ready'}
                </button>
                
                {canStart && (
                  <div className="start-section">
                    <p>All players ready! The adventure can begin!</p>
                    <button 
                      className="start-button"
                      disabled={isStarting}
                      onClick={async () => {
                        if (isStarting) return;
                        setIsStarting(true);
                        setError('');
                        try {
                          const response = await fetch(`${API_URL}/lobby/start`, {
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
                      {isStarting ? 'Starting...' : '⚔️ Start Adventure'}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Page - Story Section */}
          <div className="right-page lobby-page">
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
                          <div className="message-header">Collaborative Story</div>
                          <div className="message-content">{msg.content}</div>
                          <div className="audio-controls">
                            <button 
                              className="audio-button-small"
                              onClick={() => playStoryAudio(msg.content)}
                              disabled={isPlayingAudio && !currentAudio}
                            >
                              {isPlayingAudio ? 'Stop' : 'Listen'}
                            </button>
                          </div>
                          {msg.scene_image && (
                            <div className="scene-image-container">
                              <div className="scene-image-label">Scene Visualization</div>
                              <img 
                                src={msg.scene_image} 
                                alt="Scene visualization" 
                                className="scene-image"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                }}
                              />
                            </div>
                          )}
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
                          <div className="message-header">{msg.username}</div>
                          <div className="message-content">{msg.content}</div>
                          {msg.scene_image && (
                            <div className="scene-image-container">
                              <div className="scene-image-label">Scene Visualization</div>
                              <img 
                                src={msg.scene_image} 
                                alt="Scene visualization" 
                                className="scene-image"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                }}
                              />
                            </div>
                          )}
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
                        {isLoading ? 'Submitting...' : 'Submit Choice'}
                      </button>
                    )}
                  </div>
                )}

                {/* Waiting for Others */}
                {!lobby.story_complete && allChosen && (
                  <div className="waiting-section">
                    <h4>Waiting for other players to choose...</h4>
                    <div className="waiting-status">
                      {Object.entries(lobby.users).map(([uid, user]) => (
                        <div key={uid} className="waiting-player">
                          <span>{user.username}:</span>
                          <span>{user.choice ? '✓ Chosen' : '⏳ Choosing...'}</span>
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
                      Start New Adventure
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default LobbyRoom;
