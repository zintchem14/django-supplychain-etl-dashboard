import json
import re

# Un nombre : des chiffres, éventuellement suivis d'une virgule ou d'un point et d'autres chiffres
NOMBRE = re.compile(r"\d+(?:[.,]\d+)?")
CONFIANCES = ("faible", "moyenne", "élevée")
PETITS_ENTIERS = {str(i) for i in range(11)}  # "1)", "2 vérifications"... toujours permis


def normaliser(nombre):
    """'57,10' et '57.1' doivent être reconnus comme le même nombre."""
    texte = nombre.replace(",", ".")
    if "." in texte:
        texte = texte.rstrip("0").rstrip(".")
    return texte


def nombres_dans(objet):
    """Tous les nombres présents dans un dictionnaire, une fois converti en texte."""
    texte = json.dumps(objet, ensure_ascii=False)
    return {normaliser(n) for n in NOMBRE.findall(texte)}


def valider(explication, faits):
    """Renvoie (True, []) si l'explication est acceptable, sinon (False, [problèmes])."""
    problemes = []

    inconnus = nombres_dans(explication) - nombres_dans(faits) - PETITS_ENTIERS
    if inconnus:
        problemes.append(f"nombres absents des faits : {sorted(inconnus)[:5]}")

    if not isinstance(explication.get("preuves"), list) or not explication["preuves"]:
        problemes.append("aucune preuve citée")

    if explication.get("confiance") not in CONFIANCES:
        problemes.append("niveau de confiance invalide")

    return len(problemes) == 0, problemes


def explication_gabarit(faits):
    """Explication de secours, construite uniquement avec les chiffres des faits."""
    taux = faits["taux_retard_pct"]
    volume = faits["volume"]["fenetre"]
    principal = faits["facteurs"][0] if faits["facteurs"] else None

    preuves = [
        f"Taux de retard de {taux['fenetre']} % contre {taux['reference']} % "
        f"sur la période de référence (volume {volume})."
    ]

    if principal:
        if abs(principal["effet_taux_points"]) >= abs(principal["effet_mix_points"]):
            cause = "de la dégradation de son taux de retard"
        else:
            cause = "d'un changement de répartition des volumes"
        preuves.append(
            f"{principal['dimension']} = {principal['modalite']} : taux de retard "
            f"{principal['taux_retard_fenetre_pct']} % (référence "
            f"{principal['taux_retard_reference_pct']} %), contribution "
            f"{principal['contribution_points']} points."
        )
        hypothese = (f"Le pic serait principalement associé à {principal['dimension']} "
                     f"« {principal['modalite']} », du fait {cause}.")
        confiance = "moyenne" if principal["volume_fenetre"] >= 100 else "faible"
    else:
        hypothese = "Aucune modalité ne ressort nettement : le pic semble diffus."
        confiance = "faible"

    return {
        "titre": f"Pic de retards du {faits['periode']['debut']}",
        "resume": preuves[0],
        "hypothese": hypothese,
        "confiance": confiance,
        "preuves": preuves,
        "hypothese_alternative": ("Variation aléatoire ou effet d'une dimension non analysée "
                                  "(catégorie de produit, météo, jour férié)."),
        "limites": ["Corrélation n'est pas causalité.",
                    "Le coût est estimé et il n'existe pas de date de livraison réelle."],
        "verifications": ["Comparer avec la même période de l'année précédente.",
                          "Croiser avec les dimensions non analysées."],
    }