import React, { useState } from 'react';
import {
  BarChart3,
  Truck,
  MapPin,
  AlertTriangle,
  DollarSign,
  Package,
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

  const menuItems = [
    { id: 'overview', label: 'Vue Globale', icon: BarChart3 },
    { id: 'shipping', label: 'Expéditions & Délais', icon: Truck },
    { id: 'map', label: 'Carte Géographique', icon: MapPin },
    { id: 'risk', label: 'Analyse des Risques', icon: AlertTriangle },
    { id: 'financials', label: 'Ventes & Profits', icon: DollarSign },
    { id: 'products', label: 'Produits & Catégories', icon: Package },
  ];

  return (
    <aside
      className={`bg-slate-900 text-slate-100 h-screen transition-all duration-300 ease-in-out flex flex-col border-r border-slate-800 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Header / Logo */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="p-2 bg-indigo-600 rounded-lg shrink-0">
            <Boxes className="w-6 h-6 text-white" />
          </div>
          {!collapsed && (
            <span className="font-bold text-lg tracking-wide whitespace-nowrap text-indigo-400">
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

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1.5 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group ${
                isActive
                  ? 'bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 font-medium'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
              title={collapsed ? item.label : undefined}
            >
              <Icon className={`w-5 h-5 shrink-0 ${isActive ? 'text-indigo-400' : 'group-hover:text-indigo-300'}`} />
              {!collapsed && (
                <span className="text-sm truncate">{item.label}</span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer / Info utilisateur ou projet */}
      {!collapsed && (
        <div className="p-4 border-t border-slate-800 text-xs text-slate-500 text-center">
          ETL Supply Chain v1.0
        </div>
      )}
    </aside>
  );
};