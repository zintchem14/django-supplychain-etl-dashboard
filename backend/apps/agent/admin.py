from django.contrib import admin

from .models import AnomalyReport


@admin.register(AnomalyReport)
class AnomalyReportAdmin(admin.ModelAdmin):
    list_display = ("periode_debut", "granularite", "taux_retard_pct", "reference_pct",
                    "z_score", "volume", "explanation_source")
    list_filter = ("granularite", "explanation_source")