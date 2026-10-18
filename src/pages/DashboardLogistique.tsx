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
    return <div style={{ padding: '2rem', textAlign: 'center' }}>Chargement des données de la Supply Chain...</div>;
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>Tableau de Bord - Supply Chain</h1>
     
      {/* Cards KPI */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <div style={{ background: '#f4f4f4', padding: '1.5rem', borderRadius: '8px', flex: 1 }}>
          <h3>Taux de Livraison</h3>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            {tauxLivraison ? `${tauxLivraison.taux_livraison_a_temps}%` : 'N/A'}
          </p>
        </div>

        <div style={{ background: '#f4f4f4', padding: '1.5rem', borderRadius: '8px', flex: 1 }}>
          <h3>Coût Moyen d'Expédition</h3>
          <p style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>
            {coutMoyen ? `${coutMoyen.cout_moyen_expedition} €` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Section Points de blocage */}
      <div>
        <h2>Points de Blocage par Région</h2>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
          <thead>
            <tr style={{ background: '#eee', textAlign: 'left' }}>
              <th style={{ padding: '0.5rem', border: '1px solid #ddd' }}>Région</th>
              <th style={{ padding: '0.5rem', border: '1px solid #ddd' }}>Expéditions Totales</th>
              <th style={{ padding: '0.5rem', border: '1px solid #ddd' }}>Total Retards</th>
            </tr>
          </thead>
          <tbody>
            {pointsBlocage.map((item, index) => (
              <tr key={index}>
                <td style={{ padding: '0.5rem', border: '1px solid #ddd' }}>{item.commande__order_region}</td>
                <td style={{ padding: '0.5rem', border: '1px solid #ddd' }}>{item.total_expeditions}</td>
                <td style={{ padding: '0.5rem', border: '1px solid #ddd' }}>{item.total_retards}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};