import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';

export const Layout: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  return (
    <div className="flex h-screen bg-gray-100">
      <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-200 lg:translate-x-0 lg:static`}>
        {/* Sidebar content */}
        <div className="p-4">Sidebar</div>
      </aside>
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex justify-between items-center p-4 bg-white shadow-sm">
          <button onClick={() => setIsOpen(!isOpen)} className="lg:hidden">Menu</button>
          <div className="font-bold">Topnav</div>
        </header>
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-4"><Outlet /></main>
      </div>
    </div>
  );
};
