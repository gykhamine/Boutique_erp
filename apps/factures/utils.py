"""
Génération de factures PDF avec ReportLab.
PyPDF2 est utilisé pour fusion/lecture de PDFs existants.
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from django.core.files.base import ContentFile
from django.conf import settings


def generer_pdf_facture(facture):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            topMargin=1.5*cm, bottomMargin=1.5*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    styles = getSampleStyleSheet()
    bleu = colors.HexColor('#1a3c5e')
    gris = colors.HexColor('#f0f4f8')
    elements = []

    # En-tête
    nom_boutique = getattr(settings, 'NOM_BOUTIQUE', 'Ma Boutique')
    devise = getattr(settings, 'DEVISE', 'FCFA')

    titre_style = ParagraphStyle('Titre', parent=styles['Normal'],
                                  fontSize=22, textColor=bleu, spaceAfter=4, fontName='Helvetica-Bold')
    sub_style = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=9, textColor=colors.grey)
    right_style = ParagraphStyle('Right', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=10)

    header_data = [
        [Paragraph(f"<b>{nom_boutique}</b>", titre_style),
         Paragraph(f"<b>FACTURE</b><br/>N° {facture.numero}<br/>Date: {facture.date_emission.strftime('%d/%m/%Y')}", right_style)]
    ]
    header_table = Table(header_data, colWidths=[10*cm, 7*cm])
    header_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    elements.append(header_table)
    elements.append(HRFlowable(width="100%", thickness=2, color=bleu, spaceAfter=10))

    # Infos client
    vente = facture.vente
    client_info = f"<b>Client:</b> {vente.client.nom if vente.client else 'Client comptant'}"
    if vente.client:
        if vente.client.telephone:
            client_info += f"<br/>Tél: {vente.client.telephone}"
        if vente.client.adresse:
            client_info += f"<br/>Adresse: {vente.client.adresse}"
    elements.append(Paragraph(client_info, styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Tableau des lignes
    col_headers = ['Référence', 'Désignation', 'Qté', 'P.U. (FCFA)', 'Remise', 'Total (FCFA)']
    data = [col_headers]
    for ligne in vente.lignes.all():
        data.append([
            ligne.produit.reference,
            ligne.produit.nom,
            str(ligne.quantite),
            f"{int(ligne.prix_unitaire):,}".replace(',', ' '),
            f"{ligne.remise_ligne}%",
            f"{int(ligne.total_ligne):,}".replace(',', ' '),
        ])

    col_widths = [3*cm, 6*cm, 1.5*cm, 2.5*cm, 1.5*cm, 2.5*cm]
    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), bleu),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (2,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, gris]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3*cm))

    # Totaux
    totaux = [
        ['Sous-total HT:', f"{int(vente.sous_total):,} {devise}".replace(',', ' ')],
        [f'Remise ({vente.remise}%):', f"-{int(vente.sous_total * vente.remise / 100):,} {devise}".replace(',', ' ')],
        [f'TVA:', f"{int(vente.tva_montant):,} {devise}".replace(',', ' ')],
        ['TOTAL TTC:', f"{int(vente.total):,} {devise}".replace(',', ' ')],
    ]
    tot_table = Table(totaux, colWidths=[5*cm, 4*cm])
    tot_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
        ('FONTNAME', (0,3), (-1,3), 'Helvetica-Bold'),
        ('FONTSIZE', (0,3), (-1,3), 11),
        ('TEXTCOLOR', (0,3), (-1,3), bleu),
        ('LINEABOVE', (0,3), (-1,3), 1, bleu),
        ('FONTSIZE', (0,0), (-1,2), 9),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))

    tot_wrapper = Table([[Paragraph('', styles['Normal']), tot_table]], colWidths=[9*cm, 8*cm])
    elements.append(tot_wrapper)
    elements.append(Spacer(1, 0.5*cm))

    # Mode de paiement
    elements.append(Paragraph(f"<b>Mode de paiement:</b> {vente.get_mode_paiement_display()}", styles['Normal']))
    if facture.notes:
        elements.append(Spacer(1, 0.3*cm))
        elements.append(Paragraph(f"<i>{facture.notes}</i>", sub_style))

    elements.append(Spacer(1, 1*cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Paragraph("Merci de votre confiance — " + nom_boutique, sub_style))

    doc.build(elements)
    buffer.seek(0)
    filename = f"facture_{facture.numero}.pdf"
    facture.fichier_pdf.save(filename, ContentFile(buffer.read()), save=True)
    return facture


def lire_infos_pdf(filepath):
    """Utilise PyPDF2 pour lire les métadonnées d'un PDF existant."""
    try:
        import PyPDF2
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            info = reader.metadata
            pages = len(reader.pages)
            return {'pages': pages, 'info': dict(info) if info else {}}
    except Exception as e:
        return {'erreur': str(e)}
