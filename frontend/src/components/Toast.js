import React, { createContext, useContext, useState, useCallback } from 'react';
import { CheckCircle, AlertCircle, Info, X } from 'lucide-react';

const ToastContext = createContext();

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within ToastProvider');
  }
  return context;
};

export const ToastProvider = ({ children }) => {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);

    if (duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, duration);
    }
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  }, []);

  const toast = {
    success: (message, duration) => addToast(message, 'success', duration),
    error: (message, duration) => addToast(message, 'error', duration),
    info: (message, duration) => addToast(message, 'info', duration),
  };

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed top-4 right-4 z-[9999] space-y-2 pointer-events-none">
        {toasts.map(({ id, message, type }) => (
          <div
            key={id}
            className="pointer-events-auto animate-slide-in-right"
            role="alert"
            aria-live="polite"
          >
            <div className={`
              flex items-start gap-3 p-4 rounded-lg shadow-2xl border min-w-[300px] max-w-md
              ${type === 'success' ? 'bg-green-50 border-green-200' : ''}
              ${type === 'error' ? 'bg-red-50 border-red-200' : ''}
              ${type === 'info' ? 'bg-blue-50 border-blue-200' : ''}
            `}>
              {type === 'success' && <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />}
              {type === 'error' && <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />}
              {type === 'info' && <Info className="w-5 h-5 text-blue-600 flex-shrink-0" />}
              
              <div className="flex-1">
                <p className={`text-sm font-medium
                  ${type === 'success' ? 'text-green-900' : ''}
                  ${type === 'error' ? 'text-red-900' : ''}
                  ${type === 'info' ? 'text-blue-900' : ''}
                `}>
                  {message}
                </p>
              </div>

              <button
                onClick={() => removeToast(id)}
                className={`
                  flex-shrink-0 hover:bg-black/5 rounded p-0.5 transition-colors
                  ${type === 'success' ? 'text-green-600' : ''}
                  ${type === 'error' ? 'text-red-600' : ''}
                  ${type === 'info' ? 'text-blue-600' : ''}
                `}
                aria-label="Close notification"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
