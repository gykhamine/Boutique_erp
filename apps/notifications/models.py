from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    TYPES = [('info','Info'),('alerte','Alerte'),('succes','Succès'),('erreur','Erreur')]

    titre = models.CharField(max_length=200)
    message = models.TextField()
    type_notif = models.CharField(max_length=20, choices=TYPES, default='info')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    lue = models.BooleanField(default=False)
    lien = models.CharField(max_length=200, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        ordering = ['-cree_le']

    def __str__(self):
        return self.titre
