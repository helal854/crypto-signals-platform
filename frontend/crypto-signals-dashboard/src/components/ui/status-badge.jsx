import React from 'react';
import { cn, getStatusColor, getStatusText } from '../../lib/utils';

export const StatusBadge = ({ status, className, ...props }) => {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        getStatusColor(status),
        className
      )}
      {...props}
    >
      {getStatusText(status)}
    </span>
  );
};

