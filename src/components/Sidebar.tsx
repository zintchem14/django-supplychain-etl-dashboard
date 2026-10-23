import React, { useState } from 'react';
import {
  BarChart3,
  Truck,
  MapPin,
  DollarSign,
  ChevronLeft,
  ChevronRight,
  Boxes
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const [collapsed, setCollapsed] = useState(false);

  // Exactement 4 rubriques stratégiques clés
  const menuItems = [
    { id: 'overview', label: 'Vue Globale', icon: BarChart3 },
    { id: 'map', label: 'vue detaillée', icon: MapPin },
  ];

  return (
    <aside
      className={`bg-slate-900 text-slate-100 h-screen transition-all duration-300 ease-in-out flex flex-col border-r border-slate-800 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Header / Logo DataSupply */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 bg-sky-600/20 border border-sky-500/30 rounded-lg shrink-0">
            <Boxes className="w-5 h-5 text-sky-400" />
          </div>
          {!collapsed && (
            <span className="font-bold text-base tracking-wide whitespace-nowrap text-white">
              DataSupply
            </span>
          )}
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Navigation (4 Entrées) */}
      <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200 group ${
                isActive
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20 font-medium'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-sky-400' : 'group-hover:text-slate-200'}`} />
              {!collapsed && (
                <span className="text-xs truncate">{item.label}</span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer / Version */}
      {!collapsed && (
        <div className="p-3 border-t border-slate-800/80 text-[10px] text-slate-500 text-center">
          ETL Supply Chain v1.0
        </div>
      )}
    </aside>
  );
};