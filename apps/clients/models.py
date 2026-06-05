from django.db import models


class Client(models.Model):
    TYPE_CLIENT = [('particulier', 'Particulier'), ('entreprise', 'Entreprise')]

    code = models.CharField(max_length=20, unique=True, blank=True)
    type_client = models.CharField(max_length=20, choices=TYPE_CLIENT, default='particulier')
    nom = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    solde_credit = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    limite_credit = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client"
        ordering = ['nom']

    def __str__(self):
        return f"{self.code} - {self.nom}"

    def save(self, *args, **kwargs):
        if not self.code:
            last = Client.objects.order_by('-id').first()
            n = (last.id + 1) if last else 1
            self.code = f"CLI{n:04d}"
        super().save(*args, **kwargs)

    @property
    def total_achats(self):
        return self.ventes.aggregate(t=models.Sum('total'))['t'] or 0
