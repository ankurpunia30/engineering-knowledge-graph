import React from 'react';
import { X, AlertTriangle } from 'lucide-react';

const ConfirmModal = ({ 
  isOpen, 
  onClose, 
  onConfirm, 
  title, 
  message, 
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'danger' // 'danger' | 'warning' | 'info'
}) => {
  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div 
        className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start gap-4 mb-6">
          <div className={`
            w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0
            ${variant === 'danger' ? 'bg-red-100' : ''}
            ${variant === 'warning' ? 'bg-yellow-100' : ''}
            ${variant === 'info' ? 'bg-blue-100' : ''}
          `}>
            <AlertTriangle className={`
              w-6 h-6
              ${variant === 'danger' ? 'text-red-600' : ''}
              ${variant === 'warning' ? 'text-yellow-600' : ''}
              ${variant === 'info' ? 'text-blue-600' : ''}
            `} />
          </div>
          
          <div className="flex-1">
            <h3 id="modal-title" className="text-xl font-bold text-gray-900 mb-2">
              {title}
            </h3>
            <p className="text-gray-600 text-sm">
              {message}
            </p>
          </div>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2.5 border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={handleConfirm}
            className={`
              flex-1 px-4 py-2.5 font-semibold rounded-lg transition-colors
              ${variant === 'danger' ? 'bg-red-600 hover:bg-red-700 text-white' : ''}
              ${variant === 'warning' ? 'bg-yellow-600 hover:bg-yellow-700 text-white' : ''}
              ${variant === 'info' ? 'bg-blue-600 hover:bg-blue-700 text-white' : ''}
            `}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmModal;
