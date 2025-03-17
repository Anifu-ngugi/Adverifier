import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

function History() {
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDate, setSelectedDate] = useState(null);

  useEffect(() => {
    const fetchChatHistory = async () => {
      try {
        const response = await api.get('/api/chat-messages/');
        const messages = response.data;
        setChatHistory(messages);
        
        // Set the most recent date as selected by default
        if (messages.length > 0) {
          const dates = [...new Set(messages.map(msg => 
            new Date(msg.created_at).toLocaleDateString()
          ))];
          dates.sort((a, b) => new Date(b) - new Date(a));
          setSelectedDate(dates[0]);
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching chat history:', error);
        setLoading(false);
      }
    };

    fetchChatHistory();
  }, []);

  // Get unique dates from chat history
  const getUniqueDates = () => {
    const dates = [...new Set(chatHistory.map(msg => 
      new Date(msg.created_at).toLocaleDateString()
    ))];
    return dates.sort((a, b) => new Date(b) - new Date(a)); // Sort by newest first
  };

  // Get messages for the selected date
  const getMessagesForDate = (date) => {
    return chatHistory.filter(msg => 
      new Date(msg.created_at).toLocaleDateString() === date
    ).sort((a, b) => new Date(a.created_at) - new Date(b.created_at)); // Sort by oldest first
  };

  const uniqueDates = getUniqueDates();
  const selectedDateMessages = selectedDate ? getMessagesForDate(selectedDate) : [];

  return (
    <div className="history-container">
      <div className="chat-header">
        <h2>Chat History</h2>
        <p>Review your past conversations with AdVerifier</p>
      </div>
      
      {loading ? (
        <div className="loading-container">
          <p>Loading your chat history...</p>
        </div>
      ) : chatHistory.length > 0 ? (
        <div className="history-content">
          <div className="date-selector">
            <h3>Conversations</h3>
            <ul className="date-list">
              {uniqueDates.map(date => (
                <li 
                  key={date} 
                  className={`date-item ${selectedDate === date ? 'selected' : ''}`}
                  onClick={() => setSelectedDate(date)}
                >
                  {date}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="chat-messages-container">
            {selectedDate ? (
              <>
                <div className="selected-date-header">
                  <h3>{selectedDate}</h3>
                </div>
                <div className="chat-messages">
                  {selectedDateMessages.length > 0 ? selectedDateMessages.map((msg) => (
                    <div key={msg.id} className={`message ${msg.is_user ? 'user-message' : 'bot-message'}`}>
                      <div className="message-bubble">{msg.message}</div>
                      <div className="message-info">
                        {msg.is_user ? 'You' : 'AdVerifier Bot'} • {new Date(msg.created_at).toLocaleTimeString()}
                      </div>
                    </div>
                  )) : (
                    <p className="no-messages">No messages found for this date.</p>
                  )}
                </div>
              </>
            ) : (
              <div className="select-prompt">
                <p>Select a date to view conversation history</p>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="empty-history">
          <h3>No Chat History</h3>
          <p>You haven't had any conversations with AdVerifier yet. Start a chat to see your history!</p>
        </div>
      )}
    </div>
  );
}

export default History;