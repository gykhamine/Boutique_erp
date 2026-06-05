from django.db import models


class Fournisseur(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True)
    nom = models.CharField(max_length=200)
    contact = models.CharField(max_length=100, blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    pays = models.CharField(max_length=100, default='Congo')
    delai_livraison = models.IntegerField(default=7, help_text='Jours')
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fournisseur"
        ordering = ['nom']

    def __str__(self):
        return f"{self.code} - {self.nom}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Fournisseur.objects.order_by('-id').first()
            n = (last.id + 1) if last else 1
            self.code = f"FRN{n:04d}"
        super().save(*args, **kwargs)
