import React, { useEffect } from 'react';
import EnterpriseDashboard from './components/EnterpriseDashboard';
import './App.css';

function App() {
  
  useEffect(() => {
    // Suppress ResizeObserver errors globally
    const originalError = console.error;
    console.error = (...args) => {
      if (args[0] && typeof args[0] === 'string' && 
          (args[0].includes('ResizeObserver loop completed') ||
           args[0].includes('ResizeObserver loop limit exceeded'))) {
        return;
      }
      originalError.apply(console, args);
    };

    // Handle unhandled errors
    const handleError = (event) => {
      if (event.message && 
          (event.message.includes('ResizeObserver loop completed') ||
           event.message.includes('ResizeObserver loop limit exceeded'))) {
        event.preventDefault();
        return false;
      }
    };

    window.addEventListener('error', handleError);
    
    return () => {
      console.error = originalError;
      window.removeEventListener('error', handleError);
    };
  }, []);

  return (
    <div className="App">
      <EnterpriseDashboard />
    </div>
  );
}

export default App;
