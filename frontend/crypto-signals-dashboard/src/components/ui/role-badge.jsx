import React from 'react';
import { cn, getRoleColor, getRoleText } from '../../lib/utils';

export const RoleBadge = ({ role, className, ...props }) => {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        getRoleColor(role),
        className
      )}
      {...props}
    >
      {getRoleText(role)}
    </span>
  );
};

