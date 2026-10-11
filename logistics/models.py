from django.db import models

# Create your models here.

#creations des classes selon notre dataset DataCoSupplyChain

class Entrepot(models.Model):
    departement_id = models.IntegerField(primary_key=True)
    departement_name = models.CharField(max_length=100)

    def __str__(self):
        return self.departement_name

#creation de la classe transporteur
class Transporteur(models.Model):
    name = models.CharField(max_length=100, unique=True) # Ex: Standard Class, Same Day, etc.

    def __str__(self):
        return self.name


#creation de la classe commande 
class Commande(models.Model):
    order_id = models.IntegerField(primary_key=True)
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)
   
    # Infos client & géographie
    customer_id = models.IntegerField()
    customer_segment = models.CharField(max_length=50, blank=True, null=True)
    market = models.CharField(max_length=100, blank=True, null=True)
    order_region = models.CharField(max_length=100, blank=True, null=True)
    order_country = models.CharField(max_length=100, blank=True, null=True)
   
    # Infos produit / vente
    product_name = models.CharField(max_length=255)
    product_price = models.FloatField()
    sales = models.FloatField()
    benefit_per_order = models.FloatField()
   
    # Lien vers l'entrepôt (Département)
    departement = models.ForeignKey(Entrepot, on_delete=models.SET_NULL, null=True, blank=True, related_name='commandes')

    def __str__(self):
        return f"Commande #{self.order_id} - {self.order_status}"

# creation de la classe expedition
class Expedition(models.Model):
    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, primary_key=True, related_name='expedition')
    shipping_date = models.DateTimeField(null=True, blank=True)
    days_for_shipping_real = models.IntegerField()
    days_for_shipment_scheduled = models.IntegerField()
    delivery_status = models.CharField(max_length=50)
    late_delivery_risk = models.BooleanField(default=False)
   
    # Lien vers le transporteur
    transporteur = models.ForeignKey(Transporteur, on_delete=models.SET_NULL, null=True, blank=True, related_name='expeditions')

    def __str__(self):
        return f"Expédition pour Commande #{self.commande_id} ({self.delivery_status})"
    