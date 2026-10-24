def quality_report(orders, rejects, stats) -> str:
    if orders.empty:
        return f"Lignes lues : {stats['rows_in']}\nAucune commande valide produite."
    actives = orders[orders["statut_livraison"] != "annulee"]
    lines = [
        f"Lignes lues            : {stats['rows_in']}",
        f"Lignes rejetées        : {stats['rows_rejected']}",
        f"Doublons supprimés     : {stats['duplicates_dropped']}",
        f"Commandes produites    : {stats['orders_out']}",
        f"Commandes incohérentes : {stats['commandes_incoherentes']}",
        f"Incohérences retard    : {stats['incoherences_retard']}",
        f"Taux d'annulation      : {1 - len(actives) / len(orders):.1%}",
        f"Taux de retard global  : {actives['en_retard'].mean():.1%}",
        f"Période                : {orders['date_commande'].min():%Y-%m-%d} -> "
        f"{orders['date_commande'].max():%Y-%m-%d}",
    ]
    if len(rejects):
        lines.append("Motifs de rejet        : " + ", ".join(
            f"{k}={v}" for k, v in rejects["motif"].value_counts().items()))
    return "\n".join(lines)