import React from 'react';
import { Database, Inbox, Search, FileQuestion, Plus } from 'lucide-react';

const EmptyState = ({ 
  type = 'default',
  title,
  message,
  actionText,
  onAction,
  icon: CustomIcon
}) => {
  const getDefaultContent = () => {
    switch (type) {
      case 'no-data':
        return {
          icon: Inbox,
          title: title || 'No data yet',
          message: message || 'Get started by adding your first item'
        };
      case 'search':
        return {
          icon: Search,
          title: title || 'No results found',
          message: message || 'Try adjusting your search terms'
        };
      case 'services':
        return {
          icon: Database,
          title: title || 'No services connected',
          message: message || 'Connect your infrastructure to start mapping dependencies'
        };
      case 'error':
        return {
          icon: FileQuestion,
          title: title || 'Something went wrong',
          message: message || 'We encountered an error loading this content'
        };
      default:
        return {
          icon: Inbox,
          title: title || 'Nothing here yet',
          message: message || 'Content will appear here once available'
        };
    }
  };

  const content = getDefaultContent();
  const Icon = CustomIcon || content.icon;

  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
      </div>
      
      <h3 className="text-xl font-semibold text-gray-900 mb-2">
        {content.title}
      </h3>
      
      <p className="text-gray-600 mb-6 max-w-sm">
        {content.message}
      </p>

      {actionText && onAction && (
        <button
          onClick={onAction}
          className="px-6 py-3 bg-black text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors inline-flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          {actionText}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
