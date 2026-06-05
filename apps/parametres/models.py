from django.db import models

class Parametre(models.Model):
    cle = models.CharField(max_length=100, unique=True)
    valeur = models.TextField()
    description = models.CharField(max_length=200, blank=True)
    modifie_le = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cle

    @classmethod
    def get(cls, cle, defaut=''):
        try:
            return cls.objects.get(cle=cle).valeur
        except cls.DoesNotExist:
            return defaut
