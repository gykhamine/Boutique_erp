from django.db import models
from django.contrib.auth.models import User


class Employe(models.Model):
    POSTES = [('vendeur','Vendeur'),('caissier','Caissier'),('magasinier','Magasinier'),
              ('comptable','Comptable'),('manager','Manager'),('directeur','Directeur')]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employe')
    matricule = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    poste = models.CharField(max_length=30, choices=POSTES)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    salaire = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    date_embauche = models.DateField()
    actif = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='employes/', blank=True, null=True)

    class Meta:
        verbose_name = "Employé"
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.matricule} — {self.prenom} {self.nom}"

    def save(self, *args, **kwargs):
        if not self.matricule:
            last = Employe.objects.order_by("-id").first()
            n = (last.id + 1) if last else 1
            self.matricule = f"EMP{n:04d}"
        super().save(*args, **kwargs)


class Conge(models.Model):
    TYPES = [('annuel','Congé annuel'),('maladie','Maladie'),('maternite','Maternité'),('autre','Autre')]
    STATUTS = [('demande','Demandé'),('approuve','Approuvé'),('refuse','Refusé')]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, related_name='conges')
    type_conge = models.CharField(max_length=20, choices=TYPES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(max_length=20, choices=STATUTS, default='demande')
    motif = models.TextField(blank=True)
    approuve_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def duree(self):
        return (self.date_fin - self.date_debut).days + 1
