import axios from 'axios';
import type { KPIsGlobaux } from '../types';


// Configuration de base d'Axios pointant vers votre backend Django
const API = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Fonctions pour appeler vos endpoints Django
export const getTauxLivraison = () => API.get('taux-livraison/');
export const getCoutMoyen = () => API.get('cout-moyen/');
export const getPointsDeBlocage = () => API.get('points-de-blocage/');


export const getKPIsGlobaux = async (): Promise<KPIsGlobaux> => {
  const response = await fetch('http://localhost:8000/api/kpis-globaux/'); // Adaptez l'URL si besoin
  if (!response.ok) {
    throw new Error('Erreur lors de la récupération des KPIs globaux');
  }
  return response.json();
};