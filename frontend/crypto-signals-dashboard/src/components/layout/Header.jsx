import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { RoleBadge } from '../ui/role-badge';
import { Bell, Search, Settings } from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';

export const Header = ({ title, subtitle }) => {
  const { user } = useAuth();

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Page Title */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {subtitle && (
            <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
          )}
        </div>

        {/* Right Side */}
        <div className="flex items-center space-x-4 space-x-reverse">
          {/* Search */}
          <div className="relative">
            <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <Input
              type="text"
              placeholder="بحث..."
              className="pr-10 w-64"
            />
          </div>

          {/* Notifications */}
          <Button variant="ghost" size="sm" className="relative">
            <Bell className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full"></span>
          </Button>

          {/* Settings */}
          <Button variant="ghost" size="sm">
            <Settings className="w-5 h-5" />
          </Button>

          {/* User Info */}
          {user && (
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">{user.username}</p>
                <RoleBadge role={user.role} />
              </div>
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {user.username.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

