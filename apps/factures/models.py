from django.db import models
from apps.ventes.models import Vente


class Facture(models.Model):
    STATUTS = [('brouillon','Brouillon'),('emise','Émise'),('payee','Payée'),('annulee','Annulée')]

    numero = models.CharField(max_length=30, unique=True)
    vente = models.OneToOneField(Vente, on_delete=models.PROTECT, related_name='facture')
    date_emission = models.DateField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    fichier_pdf = models.FileField(upload_to='factures/', blank=True, null=True)
    notes = models.TextField(blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Facture"
        ordering = ['-date_emission']

    def __str__(self):
        return self.numero

    def save(self, *args, **kwargs):
        if not self.numero:
            from django.utils import timezone
            count = Facture.objects.count() + 1
            self.numero = f"FAC{timezone.now().strftime('%Y')}{count:05d}"
        super().save(*args, **kwargs)
