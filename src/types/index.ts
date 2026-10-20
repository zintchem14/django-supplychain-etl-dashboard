export interface TauxLivraisonData {
  total_expeditions: number;
  expeditions_a_temps: number;
  taux_livraison_a_temps: number; // Corrigé ici
}

export interface CoutMoyenData {
  cout_moyen_expedition: number;
}

export interface PointDeBlocage {
  commande__order_region: string;
  total_expeditions: number;
  total_retards: number;
}

export interface TopMarket {
  market: string;
  total: number;
}

export interface KPIsGlobaux {
  volume_total_expeditions: number;
  benefice_total: number;
  marge_beneficiaire_pct: number;
  retard_moyen_jours: number;
  top_marches: TopMarket[];
}