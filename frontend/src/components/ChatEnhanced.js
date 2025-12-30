import React, { useState, useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import apiService from '../services/apiEnhanced';

const Chat = ({ onNodesHighlight }) => {
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: '👋 Hello! I\'m your Engineering Knowledge Graph assistant with advanced natural language capabilities. I can help you understand your infrastructure by answering questions about services, dependencies, teams, and more. What would you like to know?',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationContext, setConversationContext] = useState({});
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await apiService.sendMessage(inputMessage);
      
      // Handle both new NLI format and legacy format
      let assistantMessage;
      
      if (typeof response.response === 'string') {
        // New NLI format - response is a formatted string
        assistantMessage = {
          type: 'assistant',
          content: response.response,
          timestamp: new Date(),
          metadata: {
            intent: response.intent,
            confidence: response.confidence,
            success: response.success,
            execution_time: response.execution_time_ms,
            entities: response.entities || []
          }
        };
      } else {
        // Legacy format - response is an object
        assistantMessage = {
          type: 'assistant',
          content: formatLegacyResponse(response.response),
          timestamp: new Date(),
          metadata: {
            intent: response.response?.type || 'unknown',
            success: !response.response?.error,
            legacy: true
          }
        };
      }

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update conversation context
      setConversationContext({
        lastQuery: inputMessage,
        lastResponse: response,
        entities: response.entities || []
      });
      
      // Highlight related nodes in the graph
      if (response.related_nodes && response.related_nodes.length > 0) {
        onNodesHighlight(response.related_nodes);
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        type: 'assistant',
        content: `❌ Sorry, I encountered an error: ${error.message || 'Unknown error'}. Please try again.`,
        timestamp: new Date(),
        metadata: { success: false, error: true }
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setInputMessage('');
    setIsLoading(false);
  };

  const formatLegacyResponse = (response) => {
    if (!response) return 'No response received.';
    
    if (response.error) {
      return `❌ ${response.error}`;
    }

    // Format different response types
    switch (response.type) {
      case 'blast_radius':
        return formatBlastRadiusResponse(response);
      case 'ownership':
        return formatOwnershipResponse(response);
      case 'dependencies':
        return formatDependencyResponse(response);
      case 'path':
        return formatPathResponse(response);
      case 'team_info':
        return formatTeamInfoResponse(response);
      default:
        return JSON.stringify(response, null, 2);
    }
  };

  const formatBlastRadiusResponse = (response) => {
    const { service_analyzed, total_affected, teams_count, severity } = response;
    const severityEmoji = { low: '🟢', medium: '🟡', high: '🟠', critical: '🔴' }[severity] || '⚪';
    
    return `💥 **Blast Radius Analysis for ${service_analyzed}**

${severityEmoji} **Severity:** ${severity?.charAt(0).toUpperCase() + severity?.slice(1)}
📊 **Total Affected:** ${total_affected} services
👥 **Teams Affected:** ${teams_count} teams`;
  };

  const formatOwnershipResponse = (response) => {
    const { service, team, team_lead, slack_channel } = response;
    return `🏢 **${service}** is owned by the **${team} team**

👤 **Team Lead:** ${team_lead}
💬 **Slack:** ${slack_channel}`;
  };

  const formatDependencyResponse = (response) => {
    const { service, dependency_count } = response;
    return `🔗 **${service}** depends on ${dependency_count} service(s)`;
  };

  const formatPathResponse = (response) => {
    const { from_service, to_service, path_length } = response;
    return `🛤️ **Path from ${from_service} to ${to_service}** (length: ${path_length})`;
  };

  const formatTeamInfoResponse = (response) => {
    const { total_teams } = response;
    return `👥 **Found ${total_teams} teams in the system**`;
  };

  const resetConversation = async () => {
    try {
      await apiService.resetConversation();
      setMessages([
        {
          type: 'assistant',
          content: '🔄 Conversation context reset. How can I help you?',
          timestamp: new Date()
        }
      ]);
      setConversationContext({});
    } catch (error) {
      console.error('Reset error:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const showExamples = () => {
    setMessages(prev => [...prev, {
      type: 'assistant',
      content: `📚 **Here are some example queries you can try:**

**🏢 Ownership Questions:**
• "Who owns the payment service?"
• "What does the orders team own?"

**🔗 Dependency Questions:**  
• "What does order-service depend on?"
• "What services use redis?"

**💥 Blast Radius Questions:**
• "What breaks if redis-main goes down?"
• "What's the blast radius of users-db?"

**📋 Exploration Questions:**
• "List all services"
• "Show me all databases"

**🛤️ Path Questions:**
• "How does api-gateway connect to orders-db?"

Just type any of these or ask your own question!`,
      timestamp: new Date(),
      metadata: { examples: true }
    }]);
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-title">
          <h2>🤖 Knowledge Graph Assistant</h2>
          <div className="chat-status">
            {conversationContext.lastQuery && (
              <span className="context-indicator">
                Context: {conversationContext.entities?.join(', ') || 'Active'}
              </span>
            )}
          </div>
        </div>
        <div className="chat-actions">
          <button 
            onClick={showExamples}
            className="action-btn examples-btn"
            title="Show example queries"
          >
            💡 Examples
          </button>
          <button 
            onClick={resetConversation}
            className="action-btn reset-btn"
            title="Reset conversation"
          >
            🔄 Reset
          </button>
        </div>
      </div>
      
      <div className="messages-container">
        {messages.map((message, index) => (
          <ChatMessage 
            key={index} 
            message={message} 
          />
        ))}
        {isLoading && (
          <div className="loading-message">
            <div className="loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span>Processing your query...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="input-container">
        <div className="input-wrapper">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your infrastructure... (e.g., 'Who owns the payment service?')"
            disabled={isLoading}
            rows="1"
            className="message-input"
          />
          <button 
            onClick={sendMessage} 
            disabled={!inputMessage.trim() || isLoading}
            className="send-button"
            title="Send message (Enter)"
          >
            {isLoading ? '⏳' : '📤'}
          </button>
        </div>
        
        <div className="quick-actions">
          <button 
            onClick={() => setInputMessage("Who owns the payment service?")}
            className="quick-action-btn"
          >
            👤 Ownership
          </button>
          <button 
            onClick={() => setInputMessage("What breaks if order-service goes down?")}
            className="quick-action-btn"
          >
            💥 Blast Radius  
          </button>
          <button 
            onClick={() => setInputMessage("List all services")}
            className="quick-action-btn"
          >
            📋 Explore
          </button>
          <button 
            onClick={() => setInputMessage("What does order-service depend on?")}
            className="quick-action-btn"
          >
            🔗 Dependencies
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
