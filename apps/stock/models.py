from django.db import models
from apps.produits.models import Produit


class MouvementStock(models.Model):
    TYPES = [('entree','Entrée'),('sortie','Sortie'),('ajustement','Ajustement'),('retour','Retour')]

    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=20, choices=TYPES)
    quantite = models.IntegerField()
    stock_avant = models.IntegerField()
    stock_apres = models.IntegerField()
    motif = models.CharField(max_length=200, blank=True)
    reference_doc = models.CharField(max_length=50, blank=True)
    cree_par = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Mouvement de stock"
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_type_mouvement_display()} {self.produit.nom} x{self.quantite}"


class Inventaire(models.Model):
    STATUTS = [('en_cours','En cours'),('valide','Validé'),('annule','Annulé')]

    reference = models.CharField(max_length=30, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Inventaire"
        ordering = ['-date']

    def __str__(self):
        return self.reference

    def save(self, *args, **kwargs):
        if not self.reference:
            from django.utils import timezone
            self.reference = f"INV{timezone.now().strftime('%Y%m%d%H%M')}"
        super().save(*args, **kwargs)


class LigneInventaire(models.Model):
    inventaire = models.ForeignKey(Inventaire, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    stock_theorique = models.IntegerField()
    stock_reel = models.IntegerField(default=0)

    @property
    def ecart(self):
        return self.stock_reel - self.stock_theorique
