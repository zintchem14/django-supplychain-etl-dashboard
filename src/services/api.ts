import axios from 'axios';

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