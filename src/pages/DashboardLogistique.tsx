import React, { useEffect, useState } from 'react';
import { getTauxLivraison, getCoutMoyen, getPointsDeBlocage } from '../services/api';
import type { TauxLivraisonData, CoutMoyenData, PointDeBlocage } from '../types';

export const DashboardLogistique: React.FC = () => {
  const [tauxLivraison, setTauxLivraison] = useState<TauxLivraisonData | null>(null);
  const [coutMoyen, setCoutMoyen] = useState<CoutMoyenData | null>(null);
  const [pointsBlocage, setPointsBlocage] = useState<PointDeBlocage[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resTaux = await getTauxLivraison();
        const resCout = await getCoutMoyen();
        const resBlocage = await getPointsDeBlocage();

        setTauxLivraison(resTaux.data);
        setCoutMoyen(resCout.data);

        // Django renvoie { points_de_blocage_region: [...] }
        if (resBlocage.data && resBlocage.data.points_de_blocage_region) {
          setPointsBlocage(resBlocage.data.points_de_blocage_region);
        } else if (Array.isArray(resBlocage.data)) {
          setPointsBlocage(resBlocage.data);
        }
      } catch (error) {
        console.error("Erreur lors de la récupération des données Django :", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400">
        Chargement des données de la Supply Chain...
      </div>
    );
  }

  return (
    <div className="p-8 font-sans space-y-8 text-slate-100">
      <h1 className="text-2xl font-bold tracking-tight text-slate-100 text-white">
        Tableau de Bord - Supply Chain
      </h1>
    
      {/* Cards KPI */}
      <div className="flex gap-4 mb-8">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex-1 shadow-lg">
          <h3 className="text-sm font-medium text-slate-400 mb-2">Taux de Livraison</h3>
          <p className="text-3xl font-bold text-emerald-400">
            {tauxLivraison ? `${tauxLivraison.taux_livraison_a_temps}%` : 'N/A'}
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl flex-1 shadow-lg">
          <h3 className="text-sm font-medium text-slate-400 mb-2">Coût Moyen d'Expédition</h3>
          <p className="text-3xl font-bold text-indigo-400">
            {coutMoyen ? `${coutMoyen.cout_moyen_expedition} €` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Section Points de blocage */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          Points de Blocage par Région
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse mt-4 text-sm text-slate-300">
            <thead>
              <tr className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <th className="p-3 font-semibold border-b border-slate-800">Région</th>
                <th className="p-3 font-semibold border-b border-slate-800">Expéditions Totales</th>
                <th className="p-3 font-semibold border-b border-slate-800">Total Retards</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {pointsBlocage.map((item, index) => (
                <tr key={index} className="hover:bg-slate-800/50 transition-colors">
                  <td className="p-3 border-b border-slate-800/50">{item.commande__order_region}</td>
                  <td className="p-3 border-b border-slate-800/50">{item.total_expeditions}</td>
                  <td className="p-3 border-b border-slate-800/50 text-rose-400 font-semibold">{item.total_retards}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};