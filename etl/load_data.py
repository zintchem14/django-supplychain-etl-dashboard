# creation du script pour automatiser le pipeline ETL pour extraire nettoyer et charger nos données 

import os
import django
import pandas as pd
from datetime import datetime
from django.utils.timezone import make_aware

# 1. Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supplychain_core.settings')
django.setup()

from logistics.models import Entrepot, Transporteur, Commande, Expedition

# importons le fichier csv
def run_etl():
    # Chemin vers votre fichier CSV
    csv_path = 'etl/DataCoSupplyChainDataset.csv' # le chemin dacces de notre csv
   
    print(" 1. EXTRACTION : Lecture du fichier CSV ")
    # Utilisation d'un encodage robuste car les données contiennent des caractères spéciaux
    df = pd.read_csv(csv_path, encoding='latin1') # ici nous avons mis latin1 pour gerer les caaratres specifique
    print(f"Nombre de lignes chargées : {len(df)}")

    # a. VOIR LES VALEURS MANQUantes
    print("Rapport des valeurs manquantes par colonne")
    print(df.isnull().sum())
    print("-" * 30) # ajoutons une ligne de separation juste pour un bon visuel

    # b. VOIR LES DOUBLONS
    duplicates_count = df.duplicated(subset=['Order Id']).sum()
    print(f"Nombre de lignes dupliquées (basées sur l'Order Id) : {duplicates_count}")
    print("-" * 50)

    # C. Suppression automatique des doublons
    df = df.drop_duplicates(subset=['Order Id'])
    print(f"Doublons supprimés automatiquement. Lignes restantes : {len(df)}")
    print("-" * 50)

    # D. Gestion des valeurs manquantes : Suppression des colonnes avec > 5% de valeurs vides
    seuil = len(df) * 0.05
    colonnes_a_supprimer = [col for col in df.columns if df[col].isnull().sum() > seuil]
   
    print("COLONNES SUPPRIMÉES (> 5% de valeurs vides)")
    if colonnes_a_supprimer:
        for col in colonnes_a_supprimer:
            print(f"- {col} ({df[col].isnull().sum()} valeurs manquantes)")
        df = df.drop(columns=colonnes_a_supprimer)
    else:
        print("Aucune colonne ne dépasse le seuil de 5% de valeurs vides.")
    print("-" * 50)

    # 3. Préparation du cache et des listes de lots pour l'optimisation
    entrepot_objs = {}
    transporteur_objs = {}
   
    commandes_batch = []
    expeditions_batch = []
    print("Cache et listes initialisés avec succès ")
    print("-" * 50)

    # Parcours de chaque ligne du DataFrame Pandas
    for index, row in df.iterrows():
       
        # a. Gestion de l'Entrepôt (Département)
        dept_id = row['Department Id']
        dept_name = row['Department Name']
        if dept_id not in entrepot_objs:
            entrepot, _ = Entrepot.objects.get_or_create(
                departement_id=dept_id,
                defaults={'departement_name': str(dept_name)}
            )
            entrepot_objs[dept_id] = entrepot
        else:
            entrepot = entrepot_objs[dept_id]

        
        # B. Gestion du Transporteur (Shipping Mode)
        shipping_mode = str(row['Shipping Mode'])
        if shipping_mode not in transporteur_objs:
            transporteur, _ = Transporteur.objects.get_or_create(name=shipping_mode)
            transporteur_objs[shipping_mode] = transporteur
        else:
            transporteur = transporteur_objs[shipping_mode]

        
        # c. Parsing des dates
        try:
            dt_order = pd.to_datetime(row['order date (DateOrders)']).to_pydatetime()
            order_date = make_aware(dt_order)
        except:
            order_date = datetime.now()

        try:
            dt_shipping = pd.to_datetime(row['shipping date (DateOrders)']).to_pydatetime()
            shipping_date = make_aware(dt_shipping)    
        except:
            shipping_date = None

        
        # D. Création de l'objet Commande (Nettoyage des types numériques et texte)
        order_id = int(row['Order Id'])
       
        commande = Commande(
            order_id=order_id,
            order_date=order_date,
            order_status=str(row['Order Status']),
            customer_id=int(row['Customer Id']),
            customer_segment=str(row['Customer Segment']),
            market=str(row['Market']),
            order_region=str(row['Order Region']),
            order_country=str(row['Order Country']),
            product_name=str(row['Product Name']),
            product_price=float(row['Product Price']),
            sales=float(row['Sales']),
            benefit_per_order=float(row['Benefit per order']),
            departement=entrepot
        )
        commandes_batch.append(commande)

         # e. Création de l'objet Expedition lié
        risk = 1 if int(row['Late_delivery_risk']) == 1 else 0
        expedition = Expedition(
            commande=commande,
            shipping_date=shipping_date,
            days_for_shipping_real=int(row['Days for shipping (real)']),
            days_for_shipment_scheduled=int(row['Days for shipment (scheduled)']),
            delivery_status=str(row['Delivery Status']),
            late_delivery_risk=bool(risk),
            transporteur=transporteur
        )
        expeditions_batch.append(expedition)

    # 4. Insertion en masse (Bulk Create) en base de données
    print("3. CHARGEMENT FINAL : Enregistrement en base de données")
    Commande.objects.bulk_create(commandes_batch, ignore_conflicts=True)
    Expedition.objects.bulk_create(expeditions_batch, ignore_conflicts=True)
    print(f"Nombre total de lignes finales enregistrées en base : {Commande.objects.count()}")
    print("ETL exécuté avec succès !")

if __name__ == '__main__':
    run_etl()



        











