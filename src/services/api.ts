import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export interface FilterParams {
  market?: string;
  segment?: string;
  transporteur?: string;
  delivery_status?: string;
}

// Anciens appels de votre DashboardLogistique
export const getTauxLivraison = async () => {
  return await axios.get(`${API_BASE_URL}/taux-livraison/`);
};

export const getCoutMoyen = async () => {
  return await axios.get(`${API_BASE_URL}/cout-moyen/`);
};

export const getPointsDeBlocage = async () => {
  return await axios.get(`${API_BASE_URL}/points-de-blocage/`);
};

export const getKPIsGlobaux = async () => {
  const response = await axios.get(`${API_BASE_URL}/kpis-globaux/`);
  return response.data;
};

// Nouvel appel pour l'analyse globale enrichie avec filtres multiples
export const getVousesGlobalesEnrichies = async (filters: FilterParams = {}) => {
  try {
    const params = new URLSearchParams();
    if (filters.market && filters.market !== 'ALL') params.append('market', filters.market);
    if (filters.segment && filters.segment !== 'ALL') params.append('segment', filters.segment);
    if (filters.transporteur && filters.transporteur !== 'ALL') params.append('transporteur', filters.transporteur);
    if (filters.delivery_status && filters.delivery_status !== 'ALL') params.append('delivery_status', filters.delivery_status);

    const response = await axios.get(`${API_BASE_URL}/vouses-globales-enrichies/?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error("Erreur lors de l'appel getVousesGlobalesEnrichies :", error);
    throw error;
  }
};