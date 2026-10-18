import { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { DashboardLogistique }from './pages/DashboardLogistique'; // Ajustez selon votre chemin d'import

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100">
      {/* Barre latérale à gauche */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Zone principale à droite */}
      <main className="flex-1 overflow-y-auto p-6">
        <DashboardLogistique />
      </main>
    </div>
  );
}