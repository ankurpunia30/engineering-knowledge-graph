import React, { useState, useRef, useEffect } from 'react';
import apiService from '../services/apiEnhanced';

const ChatModern = () => {
  const [messages, setMessages] = useState([
    {
      type: 'assistant',
      content: '👋 Hello! I\'m your AI-powered infrastructure assistant. Ask me anything about your services, dependencies, teams, and more.',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationContext, setConversationContext] = useState({});
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await apiService.sendMessage(inputMessage);
      
      const assistantMessage = {
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

      setMessages(prev => [...prev, assistantMessage]);
      
      setConversationContext({
        lastQuery: inputMessage,
        lastResponse: response,
        entities: response.entities || []
      });
      
    } catch (error) {
      setMessages(prev => [...prev, {
        type: 'assistant',
        content: `❌ Error: ${error.message}`,
        timestamp: new Date(),
        metadata: { error: true }
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetConversation = async () => {
    try {
      await apiService.resetConversation();
      setMessages([
        {
          type: 'assistant',
          content: '🔄 Conversation reset. How can I help you explore your infrastructure?',
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

  const quickActions = [
    { icon: '📋', label: 'List Services', query: 'show all services' },
    { icon: '👥', label: 'Show Teams', query: 'list all teams' },
    { icon: '🗄️', label: 'Databases', query: 'show all databases' },
    { icon: '💥', label: 'Blast Radius', query: 'what is the blast radius of payment-service' },
  ];

  const sendQuickAction = (query) => {
    setInputMessage(query);
    setTimeout(() => sendMessage(), 100);
  };

  const getIntentColor = (intent) => {
    const colors = {
      exploration: 'bg-blue-100 text-blue-700 border-blue-300',
      dependency: 'bg-purple-100 text-purple-700 border-purple-300',
      ownership: 'bg-green-100 text-green-700 border-green-300',
      impact: 'bg-red-100 text-red-700 border-red-300',
      path: 'bg-yellow-100 text-yellow-700 border-yellow-300',
      team: 'bg-indigo-100 text-indigo-700 border-indigo-300',
      unknown: 'bg-gray-100 text-gray-700 border-gray-300'
    };
    return colors[intent] || colors.unknown;
  };

  const getIntentIcon = (intent) => {
    const icons = {
      exploration: '🔍',
      dependency: '🔗',
      ownership: '👤',
      impact: '💥',
      path: '🛤️',
      team: '👥',
      unknown: '❓'
    };
    return icons[intent] || icons.unknown;
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-indigo-50">
      {/* Glassmorphism Header */}
      <div className="bg-white/70 backdrop-blur-xl shadow-2xl border-b border-white/20">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 via-indigo-600 to-purple-600 rounded-2xl flex items-center justify-center shadow-xl transform hover:scale-105 transition-transform">
                <span className="text-2xl">🧠</span>
              </div>
              <div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent">
                  Infrastructure Intelligence
                </h1>
                <p className="text-sm text-gray-600 mt-1 font-medium">
                  Natural Language Knowledge Graph Assistant
                </p>
              </div>
            </div>
            
            <button
              onClick={resetConversation}
              className="px-5 py-2.5 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all shadow-lg hover:shadow-xl flex items-center gap-2 font-medium transform hover:scale-105"
            >
              <span className="text-lg">🔄</span>
              <span>Reset</span>
            </button>
          </div>
          
          {/* Context Pills */}
          {conversationContext.entities && conversationContext.entities.length > 0 && (
            <div className="mt-5 flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold text-gray-500 uppercase tracking-wider">Active Context:</span>
              {conversationContext.entities.map((entity, idx) => (
                <span 
                  key={idx} 
                  className="px-3 py-1.5 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-full text-xs font-semibold shadow-md transform hover:scale-105 transition-transform"
                >
                  {entity}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions Bar */}
      <div className="bg-white/60 backdrop-blur-md border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-6 py-3">
          <div className="flex items-center gap-3 overflow-x-auto">
            <span className="text-xs font-bold text-gray-500 uppercase tracking-wider whitespace-nowrap">Quick Actions:</span>
            {quickActions.map((action, idx) => (
              <button
                key={idx}
                onClick={() => sendQuickAction(action.query)}
                className="px-4 py-2 bg-white hover:bg-gray-50 border-2 border-gray-200 hover:border-indigo-400 rounded-lg transition-all shadow-sm hover:shadow-md flex items-center gap-2 whitespace-nowrap transform hover:scale-105"
              >
                <span className="text-lg">{action.icon}</span>
                <span className="text-sm font-medium text-gray-700">{action.label}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-5xl mx-auto space-y-6">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}
            >
              <div className={`flex gap-3 max-w-3xl ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                {/* Avatar */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-md ${
                  message.type === 'user' 
                    ? 'bg-gradient-to-br from-indigo-500 to-purple-600' 
                    : 'bg-gradient-to-br from-blue-500 to-indigo-600'
                }`}>
                  <span className="text-xl">{message.type === 'user' ? '👤' : '🤖'}</span>
                </div>

                {/* Message Content */}
                <div className={`flex-1 ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                  <div className={`px-5 py-4 rounded-2xl shadow-lg ${
                    message.type === 'user'
                      ? 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white'
                      : 'bg-white border border-gray-200'
                  }`}>
                    <div className={`whitespace-pre-wrap font-medium ${
                      message.type === 'user' ? 'text-white' : 'text-gray-800'
                    }`}>
                      {message.content}
                    </div>
                    
                    {/* Metadata */}
                    {message.metadata && !message.metadata.error && (
                      <div className="mt-4 pt-3 border-t border-gray-200 flex flex-wrap gap-2">
                        {message.metadata.intent && (
                          <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getIntentColor(message.metadata.intent)}`}>
                            {getIntentIcon(message.metadata.intent)} {message.metadata.intent}
                          </span>
                        )}
                        {message.metadata.confidence !== undefined && (
                          <span className="px-3 py-1 bg-gray-100 border border-gray-300 text-gray-700 rounded-full text-xs font-semibold">
                            {Math.round(message.metadata.confidence * 100)}% confident
                          </span>
                        )}
                        {message.metadata.execution_time !== undefined && (
                          <span className="px-3 py-1 bg-green-100 border border-green-300 text-green-700 rounded-full text-xs font-semibold">
                            ⚡ {message.metadata.execution_time.toFixed(2)}ms
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Timestamp */}
                  <div className={`mt-1.5 text-xs text-gray-500 px-2 ${message.type === 'user' ? 'text-right' : 'text-left'}`}>
                    {message.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start animate-fadeIn">
              <div className="flex gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-md">
                  <span className="text-xl">🤖</span>
                </div>
                <div className="bg-white border border-gray-200 px-5 py-4 rounded-2xl shadow-lg">
                  <div className="flex gap-2">
                    <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2.5 h-2.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="bg-white/70 backdrop-blur-xl border-t border-gray-200/50 shadow-2xl">
        <div className="max-w-5xl mx-auto px-6 py-5">
          <div className="flex gap-3">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask anything about your infrastructure... (Shift+Enter for new line)"
              className="flex-1 px-5 py-4 border-2 border-gray-300 rounded-2xl focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 resize-none font-medium text-gray-800 shadow-sm transition-all"
              rows="2"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-2xl hover:from-indigo-700 hover:to-purple-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl flex items-center gap-3 font-bold text-lg transform hover:scale-105 disabled:transform-none"
            >
              <span>{isLoading ? '⏳' : '🚀'}</span>
              <span>{isLoading ? 'Thinking...' : 'Send'}</span>
            </button>
          </div>
          
          <p className="mt-3 text-xs text-gray-500 text-center">
            💡 Try: "Who owns payment-service?", "What depends on redis?", "Show blast radius of api-gateway"
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatModern;
