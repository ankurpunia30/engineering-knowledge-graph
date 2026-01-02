import React from 'react';

const EKGLogo = ({ size = 32 }) => {
  return (
    <svg 
      width={size} 
      height={size} 
      viewBox="0 0 64 64" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style={{ stopColor: '#2563eb', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#7c3aed', stopOpacity: 1 }} />
        </linearGradient>
      </defs>
      
      {/* Background circle */}
      <circle cx="32" cy="32" r="30" fill="url(#logoGrad)"/>
      
      {/* Graph nodes */}
      <circle cx="32" cy="20" r="4" fill="white"/>
      <circle cx="20" cy="36" r="4" fill="white"/>
      <circle cx="44" cy="36" r="4" fill="white"/>
      <circle cx="32" cy="48" r="4" fill="white"/>
      
      {/* Graph edges */}
      <line x1="32" y1="20" x2="20" y2="36" stroke="white" strokeWidth="2" opacity="0.7"/>
      <line x1="32" y1="20" x2="44" y2="36" stroke="white" strokeWidth="2" opacity="0.7"/>
      <line x1="20" y1="36" x2="32" y2="48" stroke="white" strokeWidth="2" opacity="0.7"/>
      <line x1="44" y1="36" x2="32" y2="48" stroke="white" strokeWidth="2" opacity="0.7"/>
      <line x1="20" y1="36" x2="44" y2="36" stroke="white" strokeWidth="2" opacity="0.7"/>
    </svg>
  );
};

export default EKGLogo;
