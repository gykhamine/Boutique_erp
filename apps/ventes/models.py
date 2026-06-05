from django.db import models
from django.utils import timezone
from apps.clients.models import Client
from apps.produits.models import Produit


class Vente(models.Model):
    STATUTS = [('brouillon', 'Brouillon'), ('confirmee', 'Confirmée'), ('livree', 'Livrée'), ('annulee', 'Annulée')]
    MODES_PAIEMENT = [('especes', 'Espèces'), ('mobile', 'Mobile Money'), ('virement', 'Virement'), ('credit', 'Crédit')]

    numero = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='ventes', null=True, blank=True)
    date = models.DateTimeField(default=timezone.now)
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    mode_paiement = models.CharField(max_length=20, choices=MODES_PAIEMENT, default='especes')
    sous_total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tva_montant = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vente"
        ordering = ['-date']

    def __str__(self):
        return self.numero

    def save(self, *args, **kwargs):
        if not self.numero:
            today = timezone.now()
            count = Vente.objects.filter(date__date=today.date()).count() + 1
            self.numero = f"VTE{today.strftime('%Y%m%d')}{count:03d}"
        super().save(*args, **kwargs)

    def calculer_totaux(self):
        lignes = self.lignes.all()
        self.sous_total = sum(l.total_ligne for l in lignes)
        remise_montant = self.sous_total * (self.remise / 100)
        base = self.sous_total - remise_montant
        self.tva_montant = sum(
            (l.total_ligne * (1 - self.remise / 100)) * (l.produit.tva / 100) for l in lignes
        )
        self.total = base + self.tva_montant
        self.save()


class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=0)
    remise_ligne = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    @property
    def total_ligne(self):
        base = self.quantite * self.prix_unitaire
        return base * (1 - self.remise_ligne / 100)

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"
