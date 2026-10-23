import React, { useEffect, useState } from 'react';
import { getVousesGlobalesEnrichies } from '../services/api';
import {
  DollarSign,
  Award,
  Truck,
  Globe,
  Package,
  AlertTriangle
} from 'lucide-react';

export const AnalyseGlobale: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // États pour les filtres multiples
  const [selectedMarket, setSelectedMarket] = useState<string>('ALL');
  const [selectedSegment, setSelectedSegment] = useState<string>('ALL');
  const [selectedTransporteur, setSelectedTransporteur] = useState<string>('ALL');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await getVousesGlobalesEnrichies({
          market: selectedMarket,
          segment: selectedSegment,
          transporteur: selectedTransporteur
        });
        setData(res);
      } catch (error) {
        console.error("Erreur lors du chargement des données analytiques :", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedMarket, selectedSegment, selectedTransporteur]);

  if (loading && !data) {
    return (
      <div className="p-4 text-slate-400 text-xs">
        Chargement de l'analyse globale et logistique...
      </div>
    );
  }

  const kpis = data?.kpis || {};
  const filters = data?.filters || {};
  const ventesProduits = data?.categories_stats || [];
  const transporteurs = data?.fiabilite_transporteurs || [];
  const blocagesRegionaux = data?.blocages_regionaux || [];
 
  const maxProdCA = ventesProduits.length > 0
    ? Math.max(...ventesProduits.map((p: any) => p.ca || 0))
    : 1;

  const SEGMENT_COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ec4899'];

  return (
    <div className="p-6 font-sans space-y-5 text-slate-100 w-full">
      
      {/* 1. BARRE DE FILTRES MULTIPLES */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center space-x-2 text-xs font-bold text-slate-200 uppercase tracking-wider">
          <Globe className="w-4 h-4 text-sky-400" />
          <span>Analyse Globale Supply Chain & Filtres Dynamiques</span>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs">
          <select
            value={selectedMarket}
            onChange={(e) => setSelectedMarket(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-sky-400 font-bold px-3 py-1.5 rounded cursor-pointer focus:outline-none"
          >
            <option value="ALL">Tous les Marchés</option>
            {filters.markets?.map((mkt: string) => (
              <option key={mkt} value={mkt}>{mkt}</option>
            ))}
          </select>

          <select
            value={selectedSegment}
            onChange={(e) => setSelectedSegment(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-emerald-400 font-bold px-3 py-1.5 rounded cursor-pointer focus:outline-none"
          >
            <option value="ALL">Tous les Segments</option>
            {filters.segments?.map((seg: string) => (
              <option key={seg} value={seg}>{seg}</option>
            ))}
          </select>

          <select
            value={selectedTransporteur}
            onChange={(e) => setSelectedTransporteur(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-amber-400 font-bold px-3 py-1.5 rounded cursor-pointer focus:outline-none"
          >
            <option value="ALL">Tous les Transporteurs</option>
            {filters.transporteurs?.map((t: string) => (
              <option key={t} value={t}>{t}</option>
            ))}
          </select>
        </div>
      </div>

      {/* 2. KPIS FINANCIERS ET LOGISTIQUES */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-3 grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="flex flex-col justify-center px-2">
          <div className="text-slate-400 text-[11px] mb-0.5 flex items-center gap-1"><DollarSign className="w-3.5 h-3.5 text-sky-400"/> Chiffre d'Affaires</div>
          <span className="text-lg font-bold text-sky-400">{kpis.total_ca ? `${Math.round(kpis.total_ca).toLocaleString()} €` : '0 €'}</span>
        </div>

        <div className="flex flex-col justify-center px-2 border-l border-slate-800/80">
          <div className="text-slate-400 text-[11px] mb-0.5 flex items-center gap-1"><Award className="w-3.5 h-3.5 text-emerald-400"/> Bénéfice Net</div>
          <span className="text-lg font-bold text-emerald-400">{kpis.total_profit ? `${Math.round(kpis.total_profit).toLocaleString()} €` : '0 €'}</span>
        </div>

        <div className="flex flex-col justify-center px-2 border-l border-slate-800/80">
          <div className="text-slate-400 text-[11px] mb-0.5 flex items-center gap-1"><Truck className="w-3.5 h-3.5 text-indigo-400"/> Livraisons à Temps</div>
          <span className="text-lg font-bold text-indigo-400">{kpis.taux_a_temps_pct ?? 0}%</span>
        </div>

        <div className="flex flex-col justify-center px-2 border-l border-slate-800/80">
          <div className="text-slate-400 text-[11px] mb-0.5 flex items-center gap-1"><AlertTriangle className="w-3.5 h-3.5 text-rose-400"/> Risque de Retard</div>
          <span className="text-lg font-bold text-rose-400">{kpis.taux_retard_pct ?? 0}%</span>
        </div>
      </div>

      {/* 3. GRAPHIQUES : PRODUITS & TRANSPORTEURS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start">
       
        {/* Histogramme Catégories */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 space-y-4 h-[340px] flex flex-col justify-between overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <div className="flex items-center space-x-2 text-xs font-bold text-sky-400 uppercase">
              <Package className="w-4 h-4" />
              <span>Performance par Catégorie (CA en €)</span>
            </div>
            <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">Histogramme</span>
          </div>

          <div className="flex-1 flex items-end justify-between gap-2 border-l-2 border-b-2 border-slate-700 pt-4 pb-1 px-2 relative">
            {ventesProduits.map((item: any, idx: number) => {
              const caVal = item.ca || 0;
              const heightPct = maxProdCA > 0 ? Math.round((caVal / maxProdCA) * 100) : 0;

              return (
                <div key={item.category_name || idx} className="flex flex-col items-center flex-1 h-full justify-end max-w-[65px]">
                  <span className="text-[9px] font-bold text-sky-400 mb-1 text-center truncate w-full">{Math.round(caVal / 1000)}k €</span>
                  <div className="w-full bg-slate-800/80 rounded-t h-full flex items-end overflow-hidden">
                    <div className="w-full bg-sky-500 rounded-t transition-all duration-300" style={{ height: `${Math.max(8, heightPct)}%` }}></div>
                  </div>
                  <span className="text-[9px] text-slate-400 mt-1 truncate w-full text-center" title={item.category_name}>{item.category_name || `Cat ${idx+1}`}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Fiabilité Transporteurs */}
        <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 space-y-4 h-[340px] flex flex-col justify-between overflow-hidden">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2.5">
            <div className="flex items-center space-x-2 text-xs font-bold text-indigo-400 uppercase">
              <Truck className="w-4 h-4" />
              <span>Fiabilité & Retards par Transporteur</span>
            </div>
            <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded">Logistique</span>
          </div>

          <div className="flex-1 flex flex-col justify-center space-y-2.5 px-1 overflow-y-auto">
            {transporteurs.map((t: any, index: number) => {
              const totalExp = t.total_expeditions || 1;
              const retards = t.retards || 0;
              const tauxRetardT = Math.round((retards / totalExp) * 100);
              const color = SEGMENT_COLORS[index % SEGMENT_COLORS.length];

              return (
                <div key={t.nom_transporteur} className="bg-slate-950 p-2.5 rounded border border-slate-800/80 space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <div className="flex items-center space-x-2">
                      <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }}></span>
                      <span className="font-bold text-slate-200">{t.nom_transporteur}</span>
                    </div>
                    <span className="font-extrabold text-rose-400">{retards} retards ({tauxRetardT}%)</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div className="h-full rounded-full" style={{ width: `${tauxRetardT}%`, backgroundColor: '#f43f5e' }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>

      {/* 4. TABLEAU DES POINTS DE BLOCAGE RÉGIONAUX (Intégration propre) */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-lg p-4 space-y-3">
        <div className="flex items-center space-x-2 border-b border-slate-800 pb-2 text-xs font-bold text-rose-400 uppercase">
          <AlertTriangle className="w-4 h-4" />
          <span>Top Régions à Risque de Retard Logistique</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs text-slate-300">
            <thead>
              <tr className="bg-slate-950/80 text-slate-400 border-b border-slate-800 text-[11px]">
                <th className="py-2 px-3">Région</th>
                <th className="py-2 px-3">Pays</th>
                <th className="py-2 px-3">Commandes</th>
                <th className="py-2 px-3">Retards</th>
                <th className="py-2 px-3">CA Affecté</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/40">
              {blocagesRegionaux.map((b: any, idx: number) => (
                <tr key={idx} className="hover:bg-slate-800/30">
                  <td className="py-2 px-3 font-bold text-slate-200">{b.region}</td>
                  <td className="py-2 px-3 text-slate-400">{b.pays}</td>
                  <td className="py-2 px-3 text-slate-300">{b.total_commandes}</td>
                  <td className="py-2 px-3 text-rose-400 font-bold">{b.nb_retards}</td>
                  <td className="py-2 px-3 text-sky-400 font-semibold">{Math.round(b.ca_affecte || 0).toLocaleString()} €</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};