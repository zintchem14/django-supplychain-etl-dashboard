import calendar
from datetime import datetime, timedelta

from django.conf import settings

from apps.api import kpis

from .attribution import attribuer
from .detection import detect
from .guardrails import explication_gabarit, valider
from .llm import appeler_llm
from .models import AnomalyReport

GRANULARITES = ("day", "week", "month")
REFERENCE_JOURS = {"day": 28, "week": 56, "month": 240}  # historique comparé au pic


def en_date(valeur):
    """Les regroupements par période peuvent renvoyer une date-heure : on garde la date."""
    return valeur.date() if isinstance(valeur, datetime) else valeur


def fin_de_periode(debut, granularite):
    if granularite == "month":
        dernier_jour = calendar.monthrange(debut.year, debut.month)[1]
        return debut.replace(day=dernier_jour)
    if granularite == "week":
        return debut + timedelta(days=6)
    return debut


def pourcentage(x):
    return None if x is None else round(100 * x, 1)


def actualiser_anomalies(granularite="week"):
    """Lance la détection et enregistre chaque pic (sans doublon). Renvoie le nombre de pics."""
    lignes = kpis.timeseries(kpis.base_queryset({}), granularite)
    pics = detect(lignes, z_threshold=settings.ANOMALY_Z_THRESHOLD,
                  min_volume=settings.ANOMALY_MIN_VOLUME)
    for pic in pics:
        debut = en_date(pic["periode"])
        AnomalyReport.objects.update_or_create(
            granularite=granularite,
            periode_debut=debut,
            defaults={
                "periode_fin": fin_de_periode(debut, granularite),
                "taux_retard_pct": pourcentage(pic["taux"]),
                "reference_pct": pourcentage(pic["base"]),
                "z_score": round(pic["z"], 2),
                "volume": pic["volume"],
            },
        )
    return len(pics)


def construire_faits(rapport):
    """Rassemble les chiffres de la période anormale et de sa période de référence."""
    expeditions = kpis.base_queryset({})
    debut_f, fin_f = rapport.periode_debut, rapport.periode_fin
    fin_r = debut_f - timedelta(days=1)
    debut_r = debut_f - timedelta(days=REFERENCE_JOURS[rapport.granularite])

    fenetre = expeditions.filter(commande__date_commande__date__range=(debut_f, fin_f))
    reference = expeditions.filter(commande__date_commande__date__range=(debut_r, fin_r))
    kf, kr = kpis.summary(fenetre), kpis.summary(reference)

    return {
        "periode": {"debut": str(debut_f), "fin": str(fin_f), "granularite": rapport.granularite},
        "reference": {"debut": str(debut_r), "fin": str(fin_r)},
        "taux_retard_pct": {"fenetre": pourcentage(kf["taux_retard"]),
                            "reference": pourcentage(kr["taux_retard"])},
        "volume": {"fenetre": kf["volume"], "reference": kr["volume"]},
        "retard_moyen_jours": {"fenetre": kf["retard_moyen_jours"],
                               "reference": kr["retard_moyen_jours"]},
        "cout_estime_moyen": {"fenetre": kf["cout_moyen"], "reference": kr["cout_moyen"]},
        "z_score": rapport.z_score,
        "facteurs": attribuer(fenetre, reference),
    }


def expliquer_rapport(rapport, forcer=False):
    """Renvoie l'explication d'une anomalie : en cache, sinon modèle de langage ou gabarit."""
    if rapport.explanation and not forcer:
        return {"source": rapport.explanation_source, "explanation": rapport.explanation}

    faits = construire_faits(rapport)
    explication = appeler_llm(faits)
    source = "llm"
    if explication is None:
        problemes = ["modèle de langage indisponible"]
    else:
        _, problemes = valider(explication, faits)

    if problemes:
        explication = explication_gabarit(faits)
        explication["_garde_fous"] = problemes  # trace : pourquoi le secours a été utilisé
        source = "template"

    rapport.explanation = explication
    rapport.explanation_source = source
    rapport.save(update_fields=["explanation", "explanation_source"])
    return {"source": source, "explanation": explication, "evidence": faits}