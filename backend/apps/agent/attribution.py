from django.db.models import Count, Q

# Les 4 axes d'analyse : nom affiché -> chemin vers le champ (le "__" traverse les relations)
DIMENSIONS = {
    "transporteur": "transporteur__nom",
    "region": "commande__region",
    "marche": "commande__marche",
    "segment_client": "commande__segment_client",
}


def totaux(queryset):
    """Volume et nombre de retards d'un ensemble d'expéditions."""
    resultat = queryset.aggregate(
        volume=Count("id"),
        retards=Count("id", filter=Q(en_retard=True)),
    )
    return resultat["volume"], resultat["retards"]


def par_modalite(queryset, champ):
    """Volume et retards pour chaque valeur d'un champ (GROUP BY)."""
    lignes = queryset.values(champ).annotate(
        volume=Count("id"),
        retards=Count("id", filter=Q(en_retard=True)),
    )
    return {ligne[champ]: (ligne["volume"], ligne["retards"]) for ligne in lignes}


def pourcentage(x):
    return round(100 * x, 1)


def attribuer(fenetre, reference, top=5, volume_min=15):
    """Décompose l'écart de taux de retard entre la fenêtre et la référence."""
    vol_f, ret_f = totaux(fenetre)
    vol_r, ret_r = totaux(reference)
    if vol_f == 0 or vol_r == 0:
        return []
    taux_global_r = ret_r / vol_r

    resultats = []
    for dimension, champ in DIMENSIONS.items():
        groupes_f = par_modalite(fenetre, champ)
        groupes_r = par_modalite(reference, champ)
        
        if len(groupes_f) < 2:
            continue  # une seule modalité dans la fenêtre : rien à comparer, aucune valeur explicative

        for modalite, (n_f, l_f) in groupes_f.items():
            if n_f < volume_min:
                continue  # trop peu d'expéditions : ce serait du bruit

            part_f, taux_f = n_f / vol_f, l_f / n_f
            n_r, l_r = groupes_r.get(modalite, (0, 0))
            if n_r:
                part_r, taux_r = n_r / vol_r, l_r / n_r
            else:
                part_r, taux_r = 0.0, taux_global_r  # modalité absente de la référence : neutre

            effet_taux = part_f * (taux_f - taux_r)
            effet_mix = (part_f - part_r) * (taux_r - taux_global_r)

            resultats.append({
                "dimension": dimension,
                "modalite": modalite,
                "volume_fenetre": n_f,
                "part_volume_fenetre_pct": pourcentage(part_f),
                "part_volume_reference_pct": pourcentage(part_r),
                "taux_retard_fenetre_pct": pourcentage(taux_f),
                "taux_retard_reference_pct": pourcentage(taux_r),
                "effet_taux_points": pourcentage(effet_taux),
                "effet_mix_points": pourcentage(effet_mix),
                "contribution_points": pourcentage(effet_taux + effet_mix),
            })

    resultats.sort(key=lambda r: r["contribution_points"], reverse=True)
    return resultats[:top]