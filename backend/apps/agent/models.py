from django.db import models


class AnomalyReport(models.Model):
    granularite = models.CharField(max_length=6)
    periode_debut = models.DateField()
    periode_fin = models.DateField()
    taux_retard_pct = models.FloatField()
    reference_pct = models.FloatField()
    z_score = models.FloatField()
    volume = models.PositiveIntegerField()
    explanation = models.JSONField(null=True, blank=True)
    explanation_source = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-periode_debut"]
        constraints = [
            models.UniqueConstraint(fields=["granularite", "periode_debut"],
                                    name="uniq_anomalie_periode"),
        ]

    def __str__(self):
        return f"Anomalie {self.granularite} du {self.periode_debut}"