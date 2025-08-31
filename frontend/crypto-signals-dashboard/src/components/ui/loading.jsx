import React from 'react';
import { cn } from '../../lib/utils';

export const LoadingSpinner = ({ size = 'md', className }) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div
      className={cn(
        'animate-spin rounded-full border-2 border-gray-300 border-t-blue-600',
        sizeClasses[size],
        className
      )}
    />
  );
};

export const LoadingPage = ({ message = 'جاري التحميل...' }) => {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <LoadingSpinner size="xl" className="mx-auto mb-4" />
        <p className="text-gray-600 text-lg">{message}</p>
      </div>
    </div>
  );
};

export const LoadingCard = ({ message = 'جاري التحميل...' }) => {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="text-center">
        <LoadingSpinner size="lg" className="mx-auto mb-4" />
        <p className="text-gray-600">{message}</p>
      </div>
    </div>
  );
};

export const LoadingButton = ({ loading, children, ...props }) => {
  return (
    <button {...props} disabled={loading || props.disabled}>
      {loading ? (
        <div className="flex items-center justify-center">
          <LoadingSpinner size="sm" className="mr-2" />
          جاري التحميل...
        </div>
      ) : (
        children
      )}
    </button>
  );
};

