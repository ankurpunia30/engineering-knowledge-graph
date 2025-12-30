import React from 'react';
import { User, Bot, AlertCircle, CheckCircle, Users, Database, Zap, TrendingUp } from 'lucide-react';

const ChatMessage = ({ message, onSuggestionClick }) => {
  const isUser = message.type === 'user';
  const content = message.content;

  const renderContent = () => {
    if (typeof content === 'string') {
      return (
        <div className="prose prose-slate max-w-none">
          <p className="text-slate-700 leading-relaxed mb-0">{content}</p>
        </div>
      );
    }

    // Handle success responses
    if (content.type === 'success') {
      return (
        <div className="glass-strong border-l-4 border-emerald-400 rounded-xl p-6 shadow-xl card-hover">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gradient-to-r from-emerald-500 to-green-500 rounded-full flex items-center justify-center shadow-lg">
                <CheckCircle className="text-white" size={20} />
              </div>
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-emerald-800 mb-2 text-lg">Success</h4>
              <p className="text-emerald-700 leading-relaxed mb-0">{content.message}</p>
              {content.details && (
                <div className="mt-3 p-3 bg-emerald-50/50 rounded-lg backdrop-blur-sm">
                  <p className="text-emerald-600 text-sm mb-0">{content.details}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    // Handle error responses
    if (content.error) {
      return (
        <div className="glass-strong border-l-4 border-red-400 rounded-xl p-6 shadow-xl card-hover">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg">
                <AlertCircle className="text-white" size={20} />
              </div>
            </div>
            <div className="flex-1">
              <h4 className="font-semibold text-red-800 mb-2 text-lg">Error</h4>
              <p className="text-red-700 leading-relaxed mb-0">{content.error}</p>
              {content.suggestion && (
                <div className="mt-3 p-3 bg-red-50/50 rounded-lg backdrop-blur-sm">
                  <p className="text-red-600 text-sm italic mb-0">{content.suggestion}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    // Handle different query types
    if (content.type === 'blast_radius') {
      return (
        <div className="space-y-6">
          <div className="glass-morphism border-l-4 border-amber-400 rounded-xl p-6 shadow-glow hover-lift">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-gradient-to-r from-amber-500 to-orange-500 rounded-xl flex items-center justify-center shadow-lg">
                  <Zap className="text-white" size={22} />
                </div>
              </div>
              <div className="flex-1">
                <h4 className="font-bold text-amber-800 mb-3 text-xl">⚡ Blast Radius Analysis</h4>
                <p className="text-amber-700 text-base leading-relaxed">
                  Impact analysis for service: <span className="font-mono bg-amber-100/70 px-3 py-1 rounded-lg font-semibold text-amber-900 shadow-sm">{content.service_analyzed}</span>
                </p>
              </div>
            </div>
          </div>
          
          {content.affected_services_count > 0 ? (
            <div className="space-y-4">
              <div className="glass-morphism-strong border-l-4 border-red-400 rounded-xl p-6 shadow-glow-purple">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 bg-gradient-to-r from-red-500 to-pink-500 rounded-lg flex items-center justify-center mr-3 shadow-md">
                    <TrendingUp className="text-white" size={18} />
                  </div>
                  <h5 className="font-bold text-red-800 text-lg">
                    🚨 {content.affected_services_count} service{content.affected_services_count !== 1 ? 's' : ''} would be impacted
                  </h5>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                  {content.affected_services.map(serviceId => {
                    const serviceName = serviceId.split(':')[1];
                    return (
                      <div key={serviceId} className="group hover-lift">
                        <div className="bg-gradient-to-r from-red-100 to-pink-100 text-red-800 border border-red-200 rounded-xl px-4 py-3 shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer">
                          <div className="flex items-center space-x-2">
                            <div className="w-2 h-2 bg-red-500 rounded-full status-error"></div>
                            <span className="font-semibold text-sm">{serviceName}</span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {content.team_details && (
                <div className="glass-morphism border-l-4 border-blue-400 rounded-xl p-6 shadow-glow">
                  <div className="flex items-center mb-4">
                    <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center mr-3 shadow-md">
                      <Users className="text-white" size={18} />
                    </div>
                    <h5 className="font-bold text-blue-800 text-lg">
                      👥 {content.teams_count} team{content.teams_count !== 1 ? 's' : ''} affected
                    </h5>
                  </div>
                  <div className="grid gap-4">
                    {Object.entries(content.team_details).map(([teamName, teamInfo]) => (
                      <div key={teamName} className="card-professional hover-lift p-4 border border-blue-200/50">
                        <div className="flex items-center justify-between mb-3">
                          <span className="font-bold text-blue-900 text-lg">{teamName}</span>
                          <div className="bg-gradient-to-r from-blue-100 to-indigo-100 text-blue-700 px-3 py-1 rounded-full text-xs font-semibold shadow-sm">
                            {teamInfo.services.length} services
                          </div>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center">
                            <span className="font-semibold text-blue-700 mr-3 w-12">Lead:</span>
                            <span className="text-slate-700">{teamInfo.lead}</span>
                          </div>
                          <div className="flex items-center">
                            <span className="font-semibold text-blue-700 mr-3 w-12">Slack:</span>
                            <span className="font-mono text-xs bg-blue-50 px-3 py-1 rounded-lg border border-blue-200 text-blue-800 shadow-sm">
                              {teamInfo.slack}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className={`card-professional p-4 text-center font-bold text-lg shadow-lg ${
                content.severity === 'HIGH' ? 'bg-gradient-to-r from-red-100 to-pink-100 text-red-800 border border-red-200' :
                content.severity === 'MEDIUM' ? 'bg-gradient-to-r from-amber-100 to-orange-100 text-amber-800 border border-amber-200' :
                'bg-gradient-to-r from-green-100 to-emerald-100 text-green-800 border border-green-200'
              }`}>
                Severity: {content.severity}
              </div>
            </div>
          ) : (
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-l-4 border-green-400 rounded-lg p-4 shadow-professional">
              <div className="flex items-start">
                <CheckCircle className="text-green-600 mt-1 mr-3 flex-shrink-0" size={20} />
                <div>
                  <h4 className="font-semibold text-green-800 mb-1">No direct impact detected</h4>
                  <p className="text-green-700 text-sm">
                    This service appears to be a leaf node with no direct dependents.
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      );
    }

    if (content.type === 'ownership') {
      return (
        <div className="space-y-3">
          <div className="bg-gradient-to-r from-purple-50 to-violet-50 border-l-4 border-purple-400 rounded-lg p-4 shadow-professional">
            <div className="flex items-start">
              <Users className="text-purple-600 mt-1 mr-3 flex-shrink-0" size={20} />
              <div className="flex-1">
                <h4 className="font-semibold text-purple-800 mb-3">Ownership Information</h4>
                {content.entity && (
                  <div className="bg-white rounded-lg p-4 border border-purple-200 mb-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-purple-700">Service:</span>
                        <span className="font-mono text-sm bg-purple-100 px-3 py-1 rounded-full text-purple-800">
                          {content.entity}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-purple-700">Type:</span>
                        <span className="text-sm bg-gray-100 px-3 py-1 rounded-full text-gray-700">
                          {content.entity_type}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-purple-700">Team:</span>
                        <span className="font-medium text-purple-900">{content.team}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-purple-700">Lead:</span>
                        <span className="text-purple-800">{content.team_lead}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-purple-700">On-call:</span>
                        <span className="text-purple-800">{content.oncall}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-purple-700">Slack:</span>
                        <span className="font-mono text-sm bg-purple-100 px-2 py-1 rounded text-purple-800">{content.slack_channel}</span>
                      </div>
                    </div>
                  </div>
                )}
                
                {content.additional_properties && Object.keys(content.additional_properties).length > 0 && (
                  <div className="bg-white rounded-lg p-4 border border-purple-200">
                    <h5 className="font-medium text-purple-800 mb-3">Additional Properties</h5>
                    <div className="grid grid-cols-1 gap-2">
                      {Object.entries(content.additional_properties).map(([key, value]) => (
                        <div key={key} className="flex items-start space-x-2">
                          <span className="text-sm font-medium text-purple-700 capitalize min-w-0">
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span className="text-sm text-purple-800 font-mono bg-purple-50 px-2 py-1 rounded flex-1">
                            {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (content.type === 'team_info') {
      return (
        <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border-l-4 border-indigo-400 rounded-lg p-4 shadow-professional">
          <div className="flex items-start">
            <Users className="text-indigo-600 mt-1 mr-3 flex-shrink-0" size={20} />
            <div className="flex-1">
              <h4 className="font-semibold text-indigo-800 mb-4">Team Information</h4>
              {content.teams && (
                <div className="grid gap-4">
                  {content.teams.map((team, idx) => (
                    <div key={idx} className="bg-white rounded-lg p-4 border border-indigo-200 shadow-professional">
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="font-semibold text-indigo-900">{team.name}</h5>
                        <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full">
                          {team.services_count} services
                        </span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-indigo-700">Lead:</span>
                          <span className="text-indigo-800">{team.lead}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="font-medium text-indigo-700">Slack:</span>
                          <span className="font-mono text-xs bg-indigo-50 px-2 py-1 rounded text-indigo-800">{team.slack}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {content.total_teams && (
                <div className="mt-4 text-center">
                  <span className="inline-flex items-center bg-indigo-100 text-indigo-800 text-sm font-medium px-3 py-1 rounded-full">
                    Total: {content.total_teams} teams
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    if (content.type === 'dependencies') {
      return (
        <div className="bg-gradient-to-r from-teal-50 to-cyan-50 border-l-4 border-teal-400 rounded-lg p-4 shadow-professional">
          <div className="flex items-start">
            <Database className="text-teal-600 mt-1 mr-3 flex-shrink-0" size={20} />
            <div className="flex-1">
              <h4 className="font-semibold text-teal-800 mb-4">
                Dependencies for {content.service}
              </h4>
              
              {content.outgoing_connections && content.outgoing_connections.length > 0 && (
                <div className="bg-white rounded-lg p-4 border border-teal-200 mb-4">
                  <h5 className="font-medium text-teal-700 mb-3 flex items-center">
                    <span className="mr-2">→</span>
                    Outgoing Connections ({content.outgoing_connections.length})
                  </h5>
                  <div className="space-y-2">
                    {content.outgoing_connections.map((conn, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 bg-teal-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <span className="font-mono text-sm bg-teal-100 px-3 py-1 rounded-full text-teal-800">
                            {conn.name}
                          </span>
                          <span className="text-xs text-teal-600 bg-white px-2 py-1 rounded">
                            {conn.type}
                          </span>
                        </div>
                        <span className="text-sm italic text-teal-600">{conn.relationship}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {content.incoming_connections && content.incoming_connections.length > 0 && (
                <div className="bg-white rounded-lg p-4 border border-teal-200">
                  <h5 className="font-medium text-teal-700 mb-3 flex items-center">
                    <span className="mr-2">←</span>
                    Incoming Connections ({content.incoming_connections.length})
                  </h5>
                  <div className="space-y-2">
                    {content.incoming_connections.map((conn, idx) => (
                      <div key={idx} className="flex items-center justify-between p-2 bg-teal-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <span className="font-mono text-sm bg-teal-100 px-3 py-1 rounded-full text-teal-800">
                            {conn.name}
                          </span>
                          <span className="text-xs text-teal-600 bg-white px-2 py-1 rounded">
                            {conn.type}
                          </span>
                        </div>
                        <span className="text-sm italic text-teal-600">{conn.relationship}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    if (content.type === 'connection') {
      return (
        <div className="space-y-3">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-800 mb-2">
              Connection Analysis for {content.service}
            </h4>
            
            {content.outgoing_connections.length > 0 && (
              <div className="mb-4">
                <h5 className="font-medium text-blue-700 mb-2">
                  Outgoing Connections ({content.total_outgoing})
                </h5>
                <div className="space-y-1">
                  {content.outgoing_connections.map((conn, idx) => (
                    <div key={idx} className="flex items-center space-x-3 text-sm">
                      <span className="text-blue-600">→</span>
                      <span className="font-mono bg-blue-100 px-2 py-1 rounded text-blue-800">
                        {conn.name}
                      </span>
                      <span className="text-blue-600">({conn.type})</span>
                      <span className="text-blue-500 italic">{conn.relationship}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {content.incoming_connections.length > 0 && (
              <div>
                <h5 className="font-medium text-blue-700 mb-2">
                  Incoming Connections ({content.total_incoming})
                </h5>
                <div className="space-y-1">
                  {content.incoming_connections.map((conn, idx) => (
                    <div key={idx} className="flex items-center space-x-3 text-sm">
                      <span className="text-blue-600">←</span>
                      <span className="font-mono bg-blue-100 px-2 py-1 rounded text-blue-800">
                        {conn.name}
                      </span>
                      <span className="text-blue-600">({conn.type})</span>
                      <span className="text-blue-500 italic">{conn.relationship}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }

    if (content.type === 'database') {
      return (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="font-medium text-green-800 mb-3">Database Overview</h4>
          <div className="space-y-3">
            {content.databases.map((db, idx) => (
              <div key={idx} className="bg-white rounded-lg p-3 border border-green-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono font-medium text-green-800">{db.name}</span>
                  <div className="flex items-center space-x-2">
                    {db.encrypted && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        Encrypted
                      </span>
                    )}
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                      {db.connections_count} connections
                    </span>
                  </div>
                </div>
                <p className="text-sm text-green-700">Team: {db.team}</p>
                <p className="text-sm text-green-600">Image: {db.image}</p>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // Default case - show general information
    if (content.message) {
      return (
        <div>
          <p className="text-slate-800 leading-relaxed mb-4">{content.message}</p>
          {content.suggestions && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-slate-600 mb-3">Try asking:</p>
              <div className="grid gap-2">
                {content.suggestions.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => onSuggestionClick(suggestion)}
                    className="text-left text-sm bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 text-blue-700 hover:text-blue-800 px-4 py-3 rounded-lg border border-blue-200 hover:border-blue-300 transition-professional shadow-professional hover:shadow-professional-lg"
                  >
                    <span className="block font-medium">{suggestion}</span>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    }

    return <p className="text-slate-800 font-mono text-sm bg-slate-100 p-3 rounded-lg">{JSON.stringify(content, null, 2)}</p>;
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} slide-up`}>
      <div className={`flex max-w-5xl ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-4`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-4' : 'mr-4'}`}>
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-lg card-hover ${
            isUser 
              ? 'bg-gradient-to-r from-blue-600 to-indigo-600' 
              : 'bg-gradient-to-r from-purple-600 to-indigo-600'
          }`}>
            {isUser ? (
              <User className="text-white" size={20} />
            ) : (
              <Bot className="text-white" size={20} />
            )}
          </div>
          <div className={`w-2 h-2 rounded-full mt-2 mx-auto shadow-sm ${
            isUser ? 'status-online bg-emerald-500' : 'bg-purple-400'
          } animate-pulse-slow`}></div>
        </div>

        {/* Message Content */}
        <div className={`flex-1 group ${
          isUser 
            ? 'message-bubble-user' 
            : 'message-bubble-assistant'
        } transition-all duration-300`}>
          <div className="message-content">
            {renderContent()}
          </div>
          
          {/* Timestamp */}
          <div className={`text-xs mt-4 flex items-center space-x-2 ${
            isUser ? 'text-white/80' : 'text-slate-500'
          }`}>
            <div className={`w-1.5 h-1.5 rounded-full ${
              isUser ? 'bg-white/60' : 'bg-purple-400'
            }`}></div>
            <span className="font-medium">
              {new Date(message.timestamp).toLocaleTimeString([], { 
                hour: '2-digit', 
                minute: '2-digit'
              })}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
