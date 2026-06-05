from django.db import models
from django.utils import timezone
from apps.fournisseurs.models import Fournisseur
from apps.produits.models import Produit


class CommandeAchat(models.Model):
    STATUTS = [('brouillon','Brouillon'),('envoyee','Envoyée'),('recue','Reçue'),('annulee','Annulée')]

    numero = models.CharField(max_length=20, unique=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.PROTECT, related_name='commandes')
    date = models.DateTimeField(default=timezone.now)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commande Achat"
        ordering = ['-date']

    def __str__(self):
        return self.numero

    def save(self, *args, **kwargs):
        if not self.numero:
            count = CommandeAchat.objects.count() + 1
            self.numero = f"ACH{timezone.now().strftime('%Y%m%d')}{count:03d}"
        super().save(*args, **kwargs)

    def calculer_total(self):
        self.total = sum(l.total_ligne for l in self.lignes.all())
        self.save()


class LigneAchat(models.Model):
    commande = models.ForeignKey(CommandeAchat, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=0)

    @property
    def total_ligne(self):
        return self.quantite * self.prix_unitaire
