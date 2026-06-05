from django.db import models
from django.utils import timezone


class SessionCaisse(models.Model):
    ouverture = models.DateTimeField(default=timezone.now)
    fermeture = models.DateTimeField(null=True, blank=True)
    fond_ouverture = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    fond_fermeture = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    caissier = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Session de caisse"
        ordering = ['-ouverture']

    def __str__(self):
        return f"Caisse {self.ouverture.strftime('%d/%m/%Y %H:%M')}"

    @property
    def est_ouverte(self):
        return self.fermeture is None

    @property
    def total_entrees(self):
        return self.transactions.filter(type_transaction='entree').aggregate(
            t=models.Sum('montant'))['t'] or 0

    @property
    def total_sorties(self):
        return self.transactions.filter(type_transaction='sortie').aggregate(
            t=models.Sum('montant'))['t'] or 0

    @property
    def solde_theorique(self):
        return self.fond_ouverture + self.total_entrees - self.total_sorties


class TransactionCaisse(models.Model):
    TYPES = [('entree','Entrée'),('sortie','Sortie')]

    session = models.ForeignKey(SessionCaisse, on_delete=models.CASCADE, related_name='transactions')
    type_transaction = models.CharField(max_length=10, choices=TYPES)
    montant = models.DecimalField(max_digits=12, decimal_places=0)
    motif = models.CharField(max_length=200)
    reference = models.CharField(max_length=50, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_type_transaction_display()} {self.montant} FCFA"
