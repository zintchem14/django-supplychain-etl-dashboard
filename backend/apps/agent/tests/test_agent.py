from datetime import date, timedelta

import pytest
from django.contrib.auth.models import Group, User
from rest_framework.test import APIClient

from apps.agent.detection import detect
from apps.agent.guardrails import explication_gabarit, valider
from apps.agent.models import AnomalyReport

TAUX_REGULIERS = [0.55, 0.57, 0.56, 0.54, 0.58, 0.55, 0.56, 0.57, 0.56]

FAITS = {
    "periode": {"debut": "2017-03-06", "fin": "2017-03-12", "granularite": "week"},
    "taux_retard_pct": {"fenetre": 78.4, "reference": 57.1},
    "volume": {"fenetre": 412, "reference": 3300},
    "z_score": 3.1,
    "facteurs": [{
        "dimension": "transporteur", "modalite": "First Class", "volume_fenetre": 128,
        "part_volume_fenetre_pct": 31.0, "part_volume_reference_pct": 12.0,
        "taux_retard_fenetre_pct": 100.0, "taux_retard_reference_pct": 100.0,
        "effet_taux_points": 0.0, "effet_mix_points": 8.1, "contribution_points": 8.1,
    }],
}


def serie(taux, volume=400):
    """Série hebdomadaire fictive : une semaine par taux, 400 expéditions chacune."""
    debut = date(2017, 1, 2)
    return [{"periode": debut + timedelta(weeks=i), "volume": volume,
             "retards": int(t * volume)} for i, t in enumerate(taux)]


# ---------- Détection ----------

def test_detection_signale_le_pic():
    pics = detect(serie(TAUX_REGULIERS + [0.85]))
    assert len(pics) == 1
    assert pics[0]["periode"] == date(2017, 3, 6)
    assert pics[0]["z"] >= 2.5


def test_detection_ignore_une_serie_reguliere():
    assert detect(serie(TAUX_REGULIERS + [0.57])) == []


def test_detection_sans_historique_suffisant():
    assert detect(serie([0.50, 0.90])) == []


# ---------- Garde-fous ----------

def test_gabarit_passe_les_garde_fous():
    ok, problemes = valider(explication_gabarit(FAITS), FAITS)
    assert ok, problemes


def test_nombre_invente_rejete():
    explication = explication_gabarit(FAITS)
    explication["resume"] = "Le taux de retard atteint 92.5 % cette semaine."
    ok, problemes = valider(explication, FAITS)
    assert not ok
    assert "92.5" in problemes[0]


def test_confiance_invalide_rejetee():
    explication = explication_gabarit(FAITS)
    explication["confiance"] = "certaine"
    ok, problemes = valider(explication, FAITS)
    assert not ok
    assert "niveau de confiance invalide" in problemes


# ---------- API et permissions ----------

@pytest.fixture
def anomalie(db):
    return AnomalyReport.objects.create(
        granularite="week", periode_debut=date(2017, 10, 9), periode_fin=date(2017, 10, 15),
        taux_retard_pct=64.1, reference_pct=57.3, z_score=2.93, volume=462,
    )


def client_connecte(nom, analyste=False):
    utilisateur = User.objects.create_user(username=nom, password="mot-de-passe-de-test")
    if analyste:
        groupe, _ = Group.objects.get_or_create(name="analyste")
        utilisateur.groups.add(groupe)
    client = APIClient()
    client.force_authenticate(user=utilisateur)
    return client


def test_lecteur_ne_peut_pas_demander_une_explication(anomalie):
    reponse = client_connecte("lecteur").post(f"/api/v1/anomalies/{anomalie.pk}/explain/")
    assert reponse.status_code == 403


def test_analyste_obtient_une_explication_de_secours(anomalie, settings):
    settings.ANTHROPIC_API_KEY = ""  # garantit le mode secours, même si une clé existe
    client = client_connecte("analyste", analyste=True)
    reponse = client.post(f"/api/v1/anomalies/{anomalie.pk}/explain/")
    assert reponse.status_code == 200
    assert reponse.data["source"] == "template"
    anomalie.refresh_from_db()
    assert anomalie.explanation_source == "template"  # l'explication est bien mise en cache