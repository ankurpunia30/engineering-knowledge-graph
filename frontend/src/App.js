import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import EnterpriseDashboard from './components/EnterpriseDashboard';
import { ThemeProvider } from './components/ThemeProvider';
import { ToastProvider } from './components/Toast';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('access_token');
  return token ? children : <Navigate to="/login" replace />;
};

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
    <ThemeProvider>
      <ToastProvider>
        <ErrorBoundary>
          <Router>
            <div className="App">
              <Routes>
          {/* Public Routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          {/* Protected Routes */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <EnterpriseDashboard />
              </ProtectedRoute>
            }
          />
          
          {/* Redirect old route to dashboard */}
          <Route path="/app" element={<Navigate to="/dashboard" replace />} />
          
          {/* 404 - Redirect to home */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
        </ErrorBoundary>
      </ToastProvider>
    </ThemeProvider>
  );
}

export default App;
