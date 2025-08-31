import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { cn } from '../../lib/utils';
import { useAuth } from '../../contexts/AuthContext';
import {
  LayoutDashboard,
  Users,
  Settings,
  MessageSquare,
  TrendingUp,
  CreditCard,
  Radio,
  FileText,
  BarChart3,
  Shield,
  LogOut,
  ChevronLeft
} from 'lucide-react';

const navigation = [
  {
    name: 'لوحة المعلومات',
    href: '/',
    icon: LayoutDashboard,
    permissions: ['read']
  },
  {
    name: 'إدارة المستخدمين',
    href: '/users',
    icon: Users,
    permissions: ['manage_users', 'manage_users_basic']
  },
  {
    name: 'التكاملات',
    href: '/integrations',
    icon: Settings,
    permissions: ['manage_integrations']
  },
  {
    name: 'الإشارات',
    href: '/signals',
    icon: TrendingUp,
    permissions: ['read']
  },
  {
    name: 'المدفوعات',
    href: '/payments',
    icon: CreditCard,
    permissions: ['read']
  },
  {
    name: 'قوالب الرسائل',
    href: '/templates',
    icon: FileText,
    permissions: ['write']
  },
  {
    name: 'الرسائل العامة',
    href: '/broadcasts',
    icon: Radio,
    permissions: ['manage_broadcasts']
  },
  {
    name: 'Futures',
    href: '/futures',
    icon: BarChart3,
    permissions: ['manage_futures']
  }
];

export const Sidebar = ({ collapsed, onToggle }) => {
  const location = useLocation();
  const { user, hasPermission, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className={cn(
      'bg-white border-l border-gray-200 transition-all duration-300 flex flex-col',
      collapsed ? 'w-16' : 'w-64'
    )}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center space-x-3 space-x-reverse">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-gray-900">لوحة التحكم</h1>
                <p className="text-xs text-gray-500">إدارة الإشارات</p>
              </div>
            </div>
          )}
          <button
            onClick={onToggle}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ChevronLeft className={cn(
              'w-4 h-4 text-gray-500 transition-transform',
              collapsed && 'rotate-180'
            )} />
          </button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          // Check if user has permission for this item
          const hasAccess = item.permissions.some(permission => hasPermission(permission));
          if (!hasAccess) return null;

          const isActive = location.pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                isActive
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-100',
                collapsed && 'justify-center'
              )}
            >
              <Icon className={cn('w-5 h-5', !collapsed && 'ml-3')} />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="p-4 border-t border-gray-200">
        {!collapsed && user && (
          <div className="mb-3">
            <p className="text-sm font-medium text-gray-900">{user.username}</p>
            <p className="text-xs text-gray-500">{user.email}</p>
          </div>
        )}
        
        <button
          onClick={handleLogout}
          className={cn(
            'flex items-center w-full px-3 py-2 text-sm font-medium text-red-700 rounded-lg hover:bg-red-50 transition-colors',
            collapsed && 'justify-center'
          )}
        >
          <LogOut className={cn('w-5 h-5', !collapsed && 'ml-3')} />
          {!collapsed && <span>تسجيل الخروج</span>}
        </button>
      </div>
    </div>
  );
};

