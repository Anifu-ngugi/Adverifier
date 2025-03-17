import React, { useState, useEffect, useRef } from "react";
import { api } from '../services/api'; // Use your API service

function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);
    
    useEffect(() => {
        const fetchMessages = async () => {
            try {
                const response = await api.get('/api/chat-messages/');
                setMessages(response.data);
            } catch (error) {
                console.error("Error fetching messages:", error);
            }
        };

        fetchMessages();
    }, []);

    useEffect(() => {
        // Scroll to bottom whenever messages change
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;
    
        setIsLoading(true);
    
        try {
            // Send message to the ChatBotView endpoint
            const response = await api.post('/api/chat/', {
                message: input
            });
            
            // Add both user message and bot response to the conversation
            setMessages(prevMessages => [
                ...prevMessages,
                // The user message is already saved by the backend
                // Add the bot response from the API
                { 
                    id: Date.now() + 1, 
                    message: response.data.bot_response, 
                    is_user: false, 
                    created_at: response.data.timestamp 
                }
            ]);
            
            setInput('');
        } catch (error) {
            console.error("Error sending message:", error);
            // If there's an error, still show the user's message but with an error for the bot
            setMessages(prevMessages => [
                ...prevMessages,
                { id: Date.now(), message: input, is_user: true, created_at: new Date().toISOString() },
                { id: Date.now() + 1, message: "Sorry, I couldn't process your request. Please try again.", is_user: false, created_at: new Date().toISOString() }
            ]);
        } finally {
            setIsLoading(false);
        }
    };
    

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2>Ad Verification Assistant</h2>
                <p>Ask me to verify the credibility of any advertisement</p>
            </div>
            <div className="chat-messages">
                {messages.length > 0 ? messages.map((msg) => (
                    <div key={msg.id} className={`message ${msg.is_user ? 'user-message' : 'bot-message'}`}>
                        <div className="message-bubble">{msg.message}</div>
                        <div className="message-info">{msg.is_user ? 'You' : 'AdVerifier Bot'} • {new Date(msg.created_at).toLocaleTimeString()}</div>
                    </div>
                )) : (
                    <div className="welcome-message">
                        <h3>Welcome to AdVerifier!</h3>
                        <p>I can help you verify the credibility of advertisements. Try sending me an ad to analyze.</p>
                        <p>For example: "Verify this ad: New miracle pill guarantees weight loss of 20 pounds in just one week with no diet or exercise!"</p>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>
            <form onSubmit={handleSendMessage} className="chat-input-container">
                <input 
                    type="text" 
                    value={input} 
                    onChange={(e) => setInput(e.target.value)} 
                    placeholder="Type your message here..." 
                    disabled={isLoading} 
                    className="chat-input" 
                />
                <button 
                    type="submit" 
                    className={`send-button ${isLoading ? 'disabled' : ''}`} 
                    disabled={isLoading || !input.trim()}
                >
                    {isLoading ? 'Sending...' : 'Send'}
                </button>
            </form>
        </div>
    );
}

export default ChatInterface;