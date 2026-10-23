from django.db import models

# 1. Modèle Entrepot (Basé sur le département / centre logistique source)
class Entrepot(models.Model):
    departement_id = models.IntegerField(primary_key=True)
    departement_name = models.CharField(max_length=150)

    def __str__(self):
        return f"Entrepôt {self.departement_id} - {self.departement_name}"


# 2. Modèle Transporteur (Mode d'expédition / Mode de livraison)
class Transporteur(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ex: Standard Class, First Class, Same Day, Second Class

    def __str__(self):
        return self.name


# 3. Modèle Commande (Contient les détails financiers, client, produit et géographie)
class Commande(models.Model):
    # Identifiants & Dates
    order_item_id = models.IntegerField(primary_key=True)
    order_id = models.IntegerField()
    
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)  # Ex: COMPLETE, PENDING, CLOSED, CANCELED
    payment_type = models.CharField(max_length=50, null=True, blank=True)  # DEBIT, TRANSFER, CASH, PAYMENT

    # Informations Client
    customer_id = models.IntegerField()
    customer_name = models.CharField(max_length=200, null=True, blank=True)
    customer_segment = models.CharField(max_length=50, null=True, blank=True)  # Consumer, Corporate, Home Office
    customer_country = models.CharField(max_length=100, null=True, blank=True)
    customer_city = models.CharField(max_length=100, null=True, blank=True)

    # Géographie de Livraison (Destination)
    market = models.CharField(max_length=100, null=True, blank=True)        # Ex: Europe, USCA, LATAM, Pacific Asia, Africa
    order_region = models.CharField(max_length=100, null=True, blank=True)  # Ex: Western Europe, Southeast Asia
    order_country = models.CharField(max_length=100, null=True, blank=True) # Ex: France, Germany, Indonesia
    order_city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Informations Produit & Catégorie
    product_card_id = models.IntegerField(null=True, blank=True)
    product_name = models.CharField(max_length=255)
    category_id = models.IntegerField(null=True, blank=True)
    category_name = models.CharField(max_length=150, null=True, blank=True) # Ex: Sporting Goods, Cleats

    # Données Financières & Ventes
    product_price = models.FloatField(default=0.0)
    order_item_quantity = models.IntegerField(default=1)
    sales_before_discount = models.FloatField(default=0.0)  # Sales
    discount_amount = models.FloatField(default=0.0)        # Order Item Discount
    discount_rate = models.FloatField(default=0.0)          # Order Item Discount Rate
    sales = models.FloatField(default=0.0)                  # Order Item Total
    benefit_per_order = models.FloatField(default=0.0)      # Benefit per order / Profit

    # Relation vers l'Entrepôt / Département source
    entrepot = models.ForeignKey(
        Entrepot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commandes"
    )

    def __str__(self):
        return f"Commande #{self.order_id} - {self.product_name} ({self.sales} €)"


# 4. Modèle Expedition (Détails d'expédition, retards et transporteur)
class Expedition(models.Model):
    commande = models.OneToOneField(
        Commande,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="expedition"
    )
    shipping_date = models.DateTimeField(null=True, blank=True)
    days_for_shipping_real = models.IntegerField()       # Délais réels d'expédition
    days_for_shipment_scheduled = models.IntegerField()  # Délais prévus
    delivery_status = models.CharField(max_length=50)    # Advance shipping, Late delivery, Shipping on time
    late_delivery_risk = models.BooleanField(default=False) # 1 ou 0

    # Relation vers le Transporteur (Mode de livraison)
    transporteur = models.ForeignKey(
        Transporteur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expeditions"
    )

    @property
    def est_en_retard(self):
        return self.days_for_shipping_real > self.days_for_shipment_scheduled

    def __str__(self):
        return f"Expédition Commande #{self.commande_id} - {self.delivery_status}"