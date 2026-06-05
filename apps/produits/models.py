from django.db import models
import qrcode
import io
from django.core.files.base import ContentFile


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creee_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Produit(models.Model):
    UNITES = [('pce', 'Pièce'), ('kg', 'Kilogramme'), ('l', 'Litre'), ('m', 'Mètre'), ('boite', 'Boîte')]

    reference = models.CharField(max_length=50, unique=True)
    nom = models.CharField(max_length=200)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='produits')
    description = models.TextField(blank=True)
    prix_achat = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    prix_vente = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    unite = models.CharField(max_length=10, choices=UNITES, default='pce')
    stock_actuel = models.IntegerField(default=0)
    stock_minimum = models.IntegerField(default=5)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        ordering = ['nom']

    def __str__(self):
        return f"{self.reference} - {self.nom}"

    @property
    def marge(self):
        if self.prix_achat > 0:
            return round(((self.prix_vente - self.prix_achat) / self.prix_achat) * 100, 1)
        return 0

    @property
    def valeur_stock(self):
        return self.stock_actuel * self.prix_vente

    @property
    def en_rupture(self):
        return self.stock_actuel <= self.stock_minimum

    def generer_qr_code(self):
        data = f"REF:{self.reference}|NOM:{self.nom}|PRIX:{self.prix_vente}FCFA"
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        filename = f"qr_{self.reference}.png"
        self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generer_qr_code()
        super().save(*args, **kwargs)
