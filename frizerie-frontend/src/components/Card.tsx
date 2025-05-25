import React from 'react';

interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  footer?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ 
  title, 
  children, 
  className = '',
  footer
}) => {
  return (
    <div className={`card bg-white rounded-lg shadow-md overflow-hidden ${className}`}>
      {title && (
        <div className="card-header p-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
        </div>
      )}
      <div className="card-body p-4">
        {children}
      </div>
      {footer && (
        <div className="card-footer p-4 bg-gray-50 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card; 