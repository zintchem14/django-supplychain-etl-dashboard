from datetime import datetime, timezone

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.logistics.models import Commande, Entrepot, Expedition, Transporteur


@pytest.fixture
def client(db):
    c = APIClient()
    c.force_authenticate(get_user_model().objects.create_user("t", password="x"))
    return c


@pytest.fixture
def data(db):
    t = Transporteur.objects.create(code="std", nom="Standard Class")
    e = Entrepot.objects.create(code="europe", nom="Hub Europe")

    def make(i, statut, ecart):
        cmd = Commande.objects.create(
            order_id=i, date_commande=datetime(2017, 5, i, tzinfo=timezone.utc),
            statut="COMPLETE", client_id=i, segment_client="Consumer", marche="Europe",
            region="Western Europe", pays="France", nb_articles=1,
            montant_total=10, profit_total=2,
        )
        Expedition.objects.create(
            commande=cmd, transporteur=t, entrepot=e, delai_prevu_jours=2,
            delai_reel_jours=2 + ecart, ecart_jours=ecart, statut_livraison=statut,
            en_retard=(statut == "en_retard"), cout_estime=10,
        )

    make(1, "a_temps", 0)
    make(2, "a_temps", -1)
    make(3, "en_retard", 2)
    make(4, "annulee", 0)


def test_non_authentifie_refuse():
    assert APIClient().get("/api/v1/kpis/summary/").status_code == 401


def test_summary_exclut_les_annulations(client, data):
    r = client.get("/api/v1/kpis/summary/").json()
    assert r["volume"] == 3 and r["retards"] == 1
    assert r["taux_livraison_a_temps"] == pytest.approx(2 / 3, abs=1e-3)


def test_filtre_sans_resultat_ne_plante_pas(client, data):
    r = client.get("/api/v1/kpis/summary/?region=Nulle%20part").json()
    assert r["volume"] == 0 and r["taux_retard"] is None


def test_date_invalide_renvoie_400(client, data):
    assert client.get("/api/v1/kpis/summary/?date_min=pas-une-date").status_code == 400


def test_pagination_plafonnee(client, data):
    r = client.get("/api/v1/expeditions/?page_size=100000").json()
    assert len(r["results"]) <= 200