import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { cn } from '../../lib/utils';

export const Layout = ({ children, title, subtitle }) => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex" dir="rtl">
      {/* Sidebar */}
      <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header title={title} subtitle={subtitle} />
        
        {/* Page Content */}
        <main className={cn(
          'flex-1 overflow-auto p-6',
          sidebarCollapsed ? 'mr-16' : 'mr-64'
        )}>
          {children}
        </main>
      </div>
    </div>
  );
};

