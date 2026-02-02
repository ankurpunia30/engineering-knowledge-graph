import React from 'react';

const EKGLogo = ({ className = '', width = 32, height = 32 }) => {
  return (
    <svg 
      width={width} 
      height={height} 
      viewBox="0 0 32 32" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer circle */}
      <circle cx="16" cy="16" r="15" stroke="currentColor" strokeWidth="2" fill="none" />
      
      {/* Network nodes */}
      <circle cx="16" cy="8" r="2" fill="currentColor" />
      <circle cx="24" cy="16" r="2" fill="currentColor" />
      <circle cx="16" cy="24" r="2" fill="currentColor" />
      <circle cx="8" cy="16" r="2" fill="currentColor" />
      
      {/* Connecting lines */}
      <line x1="16" y1="8" x2="24" y2="16" stroke="currentColor" strokeWidth="1.5" />
      <line x1="24" y1="16" x2="16" y2="24" stroke="currentColor" strokeWidth="1.5" />
      <line x1="16" y1="24" x2="8" y2="16" stroke="currentColor" strokeWidth="1.5" />
      <line x1="8" y1="16" x2="16" y2="8" stroke="currentColor" strokeWidth="1.5" />
      
      {/* Center node */}
      <circle cx="16" cy="16" r="3" fill="currentColor" />
    </svg>
  );
};

export default EKGLogo;
