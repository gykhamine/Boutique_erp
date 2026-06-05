from django.db import models
from django.contrib.auth.models import User


class Tache(models.Model):
    PRIORITES = [('basse','Basse'),('normale','Normale'),('haute','Haute'),('urgente','Urgente')]
    STATUTS = [('todo','À faire'),('en_cours','En cours'),('fait','Terminée'),('annulee','Annulée')]

    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigne_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='taches')
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='taches_creees')
    priorite = models.CharField(max_length=10, choices=PRIORITES, default='normale')
    statut = models.CharField(max_length=20, choices=STATUTS, default='todo')
    echeance = models.DateField(null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Tâche"
        ordering = ['-priorite', 'echeance']

    def __str__(self):
        return self.titre

    @property
    def est_en_retard(self):
        from django.utils import timezone
        return self.echeance and self.echeance < timezone.now().date() and self.statut != 'fait'
