"""
ontologie.py — Module d'ontologie et d'analyse de réseau pour Boutique ERP
Utilise NetworkX pour modéliser les relations entre entités métier.

Entités modélisées :
  - Client  → Produit   (via LigneVente)
  - Produit → Catégorie
  - Fournisseur → Produit (via LigneAchat)
  - Produit → Produit   (co-achat dans la même vente)

Analyses disponibles :
  - Centralité (clients/produits les plus influents)
  - Communautés de produits
  - Flux financiers (graphe pondéré par FCFA)
  - Graphique de visualisation matplotlib (PNG)
"""

import io
import json
import math
from collections import defaultdict

import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from django.utils import timezone
from datetime import timedelta


# ─────────────────────────────────────────────────────────────────────────────
# Couleurs palette ERP (cohérent avec le thème #1a3c5e)
# ─────────────────────────────────────────────────────────────────────────────
COULEURS = {
    'client':      '#2980b9',
    'produit':     '#27ae60',
    'categorie':   '#e67e22',
    'fournisseur': '#8e44ad',
    'vente':       '#1a3c5e',
    'edge_achat':  '#8e44ad',
    'edge_vente':  '#2980b9',
    'edge_coachat':'#27ae60',
    'edge_cat':    '#e67e22',
}


# ─────────────────────────────────────────────────────────────────────────────
# Construction des graphes
# ─────────────────────────────────────────────────────────────────────────────

def construire_graphe_ventes(jours=90):
    """
    Graphe orienté pondéré : Client → Produit
    Poids = montant total FCFA dépensé par ce client sur ce produit.
    """
    from apps.ventes.models import LigneVente

    G = nx.DiGraph()
    debut = timezone.now() - timedelta(days=jours)

    lignes = (LigneVente.objects
              .filter(vente__date__gte=debut,
                      vente__statut__in=['confirmee', 'livree'])
              .select_related('vente__client', 'produit', 'produit__categorie'))

    for ligne in lignes:
        client = ligne.vente.client
        produit = ligne.produit

        # Nœud client
        client_id = f"CLI_{client.id}" if client else "CLI_COMPTANT"
        client_label = client.nom[:20] if client else "Comptant"
        if not G.has_node(client_id):
            G.add_node(client_id,
                       label=client_label,
                       type='client',
                       color=COULEURS['client'],
                       taille=15)

        # Nœud produit
        prod_id = f"PRD_{produit.id}"
        if not G.has_node(prod_id):
            G.add_node(prod_id,
                       label=produit.nom[:20],
                       type='produit',
                       color=COULEURS['produit'],
                       categorie=str(produit.categorie) if produit.categorie else 'Sans catégorie',
                       taille=12)

        # Nœud catégorie
        if produit.categorie:
            cat_id = f"CAT_{produit.categorie.id}"
            if not G.has_node(cat_id):
                G.add_node(cat_id,
                           label=str(produit.categorie)[:15],
                           type='categorie',
                           color=COULEURS['categorie'],
                           taille=10)
            if not G.has_edge(prod_id, cat_id):
                G.add_edge(prod_id, cat_id, type='appartient', weight=1)

        # Arc client → produit
        montant = float(ligne.total_ligne)
        if G.has_edge(client_id, prod_id):
            G[client_id][prod_id]['weight'] += montant
            G[client_id][prod_id]['quantite'] += ligne.quantite
        else:
            G.add_edge(client_id, prod_id,
                       weight=montant,
                       quantite=ligne.quantite,
                       type='achat')

    return G


def construire_graphe_achats(jours=90):
    """
    Graphe orienté pondéré : Fournisseur → Produit
    Poids = montant total commandé.
    """
    from apps.achats.models import LigneAchat

    G = nx.DiGraph()
    debut = timezone.now() - timedelta(days=jours)

    lignes = (LigneAchat.objects
              .filter(commande__date__gte=debut,
                      commande__statut__in=['recue', 'envoyee'])
              .select_related('commande__fournisseur', 'produit'))

    for ligne in lignes:
        fournisseur = ligne.commande.fournisseur
        produit = ligne.produit

        frn_id = f"FRN_{fournisseur.id}"
        prod_id = f"PRD_{produit.id}"

        if not G.has_node(frn_id):
            G.add_node(frn_id,
                       label=fournisseur.nom[:20],
                       type='fournisseur',
                       color=COULEURS['fournisseur'],
                       pays=fournisseur.pays,
                       taille=14)

        if not G.has_node(prod_id):
            G.add_node(prod_id,
                       label=produit.nom[:20],
                       type='produit',
                       color=COULEURS['produit'],
                       taille=12)

        montant = float(ligne.total_ligne)
        if G.has_edge(frn_id, prod_id):
            G[frn_id][prod_id]['weight'] += montant
        else:
            G.add_edge(frn_id, prod_id, weight=montant, type='approvisionnement')

    return G


def construire_graphe_coachat(jours=90):
    """
    Graphe non orienté : Produit — Produit
    Arc = ces deux produits ont été achetés ensemble dans au moins une vente.
    Poids = nombre de ventes communes.
    """
    from apps.ventes.models import Vente, LigneVente
    from itertools import combinations

    G = nx.Graph()
    debut = timezone.now() - timedelta(days=jours)

    ventes = (Vente.objects
              .filter(date__gte=debut, statut__in=['confirmee', 'livree'])
              .prefetch_related('lignes__produit'))

    for vente in ventes:
        produits = [l.produit for l in vente.lignes.all()]
        for p in produits:
            pid = f"PRD_{p.id}"
            if not G.has_node(pid):
                G.add_node(pid,
                           label=p.nom[:20],
                           type='produit',
                           color=COULEURS['produit'],
                           categorie=str(p.categorie) if p.categorie else '')
        for p1, p2 in combinations(produits, 2):
            id1, id2 = f"PRD_{p1.id}", f"PRD_{p2.id}"
            if id1 == id2:
                continue
            if G.has_edge(id1, id2):
                G[id1][id2]['weight'] += 1
            else:
                G.add_edge(id1, id2, weight=1, type='co_achat')

    return G


# ─────────────────────────────────────────────────────────────────────────────
# Analyses de réseau
# ─────────────────────────────────────────────────────────────────────────────

def analyser_centralite(G, top=10):
    """
    Retourne les nœuds les plus centraux (degree, betweenness, pagerank).
    Adapté aux graphes orientés et non orientés.
    """
    if G.number_of_nodes() == 0:
        return {}

    # Degree centrality (pondéré si possible)
    if G.is_directed():
        deg = dict(G.in_degree(weight='weight'))
    else:
        deg = dict(G.degree(weight='weight'))

    # PageRank (sur graphe orienté uniquement)
    pagerank = {}
    if G.is_directed() and G.number_of_edges() > 0:
        try:
            pagerank = nx.pagerank(G, weight='weight', max_iter=200)
        except nx.PowerIterationFailedConvergence:
            pagerank = {}

    # Betweenness (sur graphe non orienté, coûteux sur les grands graphes)
    betweenness = {}
    if not G.is_directed() and G.number_of_nodes() <= 500:
        betweenness = nx.betweenness_centrality(G, weight='weight', normalized=True)

    # Tri et top N
    top_degree = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:top]
    top_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:top]
    top_bw = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:top]

    def enrich(items):
        return [
            {
                'id': nid,
                'label': G.nodes[nid].get('label', nid),
                'type': G.nodes[nid].get('type', ''),
                'valeur': round(v, 4),
            }
            for nid, v in items
        ]

    return {
        'top_degree': enrich(top_degree),
        'top_pagerank': enrich(top_pr),
        'top_betweenness': enrich(top_bw),
    }


def detecter_communautes(G):
    """
    Détecte les communautés de produits (Louvain si disponible, sinon greedy modularity).
    Retourne une liste de communautés triées par taille.
    """
    if G.number_of_nodes() == 0:
        return []

    # Toujours travailler sur le graphe non orienté pour la détection
    H = G.to_undirected() if G.is_directed() else G

    if H.number_of_edges() == 0:
        return [[{'id': n, 'label': H.nodes[n].get('label', n)} for n in H.nodes()]]

    try:
        from networkx.algorithms.community import greedy_modularity_communities
        comms = list(greedy_modularity_communities(H, weight='weight'))
    except Exception:
        # fallback : chaque composante connexe est une communauté
        comms = [list(c) for c in nx.connected_components(H)]

    result = []
    for i, comm in enumerate(sorted(comms, key=len, reverse=True)):
        membres = [
            {
                'id': n,
                'label': G.nodes[n].get('label', n),
                'type': G.nodes[n].get('type', ''),
            }
            for n in comm if n in G.nodes
        ]
        result.append({'id': i + 1, 'taille': len(membres), 'membres': membres[:10]})

    return result


def statistiques_reseau(G):
    """Métriques globales du graphe."""
    if G.number_of_nodes() == 0:
        return {}

    H = G.to_undirected() if G.is_directed() else G
    composantes = list(nx.connected_components(H))

    stats = {
        'nb_noeuds': G.number_of_nodes(),
        'nb_arcs': G.number_of_edges(),
        'nb_composantes': len(composantes),
        'taille_plus_grande_composante': max((len(c) for c in composantes), default=0),
        'densite': round(nx.density(G), 4),
    }

    if G.number_of_nodes() >= 2:
        try:
            stats['clustering_moyen'] = round(nx.average_clustering(H), 4)
        except Exception:
            stats['clustering_moyen'] = None

    return stats


# ─────────────────────────────────────────────────────────────────────────────
# Sérialisation JSON (pour D3.js / vis.js côté front)
# ─────────────────────────────────────────────────────────────────────────────

def graphe_vers_json(G, max_noeuds=80):
    """
    Convertit le graphe en format nodes/links compatible D3.js.
    Limite aux max_noeuds les plus connectés pour l'affichage.
    """
    if G.number_of_nodes() == 0:
        return {'nodes': [], 'links': []}

    # Sélectionner les nœuds les plus connectés
    if G.number_of_nodes() > max_noeuds:
        if G.is_directed():
            scores = dict(G.in_degree(weight='weight'))
        else:
            scores = dict(G.degree(weight='weight'))
        noeuds_gardes = set(
            n for n, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:max_noeuds]
        )
    else:
        noeuds_gardes = set(G.nodes())

    # Index de position (pour D3 force)
    id_to_index = {n: i for i, n in enumerate(noeuds_gardes)}

    nodes = []
    for nid in noeuds_gardes:
        attrs = G.nodes[nid]
        nodes.append({
            'id': nid,
            'index': id_to_index[nid],
            'label': attrs.get('label', nid),
            'type': attrs.get('type', 'inconnu'),
            'color': attrs.get('color', '#999999'),
            'group': attrs.get('type', 'inconnu'),
        })

    links = []
    for u, v, data in G.edges(data=True):
        if u in noeuds_gardes and v in noeuds_gardes:
            links.append({
                'source': id_to_index[u],
                'target': id_to_index[v],
                'weight': round(float(data.get('weight', 1)), 2),
                'type': data.get('type', ''),
            })

    return {'nodes': nodes, 'links': links}


# ─────────────────────────────────────────────────────────────────────────────
# Visualisation Matplotlib (PNG serveur)
# ─────────────────────────────────────────────────────────────────────────────

def graphique_reseau_png(G, titre="Réseau ERP", figsize=(14, 10), max_noeuds=60):
    """
    Génère un graphique matplotlib du réseau et retourne les bytes PNG.
    """
    if G.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor('#f8fafc')
        ax.text(0.5, 0.5, 'Aucune donnée disponible\n(pas de ventes sur la période)',
                ha='center', va='center', fontsize=14, color='#999',
                transform=ax.transAxes)
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.read()

    # Réduire si trop grand
    if G.number_of_nodes() > max_noeuds:
        if G.is_directed():
            scores = dict(G.in_degree(weight='weight'))
        else:
            scores = dict(G.degree(weight='weight'))
        gardes = set(
            n for n, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:max_noeuds]
        )
        G = G.subgraph(gardes).copy()

    # Layout
    if G.number_of_nodes() <= 20:
        pos = nx.spring_layout(G, seed=42, k=2.5)
    else:
        pos = nx.kamada_kawai_layout(G)

    # Attributs visuels
    node_colors = [G.nodes[n].get('color', '#aaaaaa') for n in G.nodes()]
    node_sizes = []
    for n in G.nodes():
        if G.is_directed():
            deg = G.in_degree(n, weight='weight') or 1
        else:
            deg = G.degree(n, weight='weight') or 1
        node_sizes.append(min(600 + math.log1p(float(deg)) * 200, 3000))

    # Poids des arcs (épaisseur)
    weights = [math.log1p(float(G[u][v].get('weight', 1))) * 0.8
               for u, v in G.edges()]
    edge_colors = [COULEURS.get(f"edge_{G[u][v].get('type','')}", '#cccccc')
                   for u, v in G.edges()]

    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')

    # Dessiner
    nx.draw_networkx_edges(G, pos, ax=ax,
                           width=weights, edge_color=edge_colors,
                           alpha=0.5, arrows=G.is_directed(),
                           arrowsize=12, connectionstyle='arc3,rad=0.1')

    nx.draw_networkx_nodes(G, pos, ax=ax,
                           node_color=node_colors,
                           node_size=node_sizes, alpha=0.9)

    # Labels (seulement si peu de nœuds)
    if G.number_of_nodes() <= 40:
        labels = {n: G.nodes[n].get('label', n) for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, ax=ax,
                                font_size=7, font_color='#1a1a1a',
                                font_weight='bold')

    # Légende
    types_presents = set(G.nodes[n].get('type') for n in G.nodes())
    noms = {'client': 'Client', 'produit': 'Produit',
            'categorie': 'Catégorie', 'fournisseur': 'Fournisseur'}
    patches = [mpatches.Patch(color=COULEURS[t], label=noms.get(t, t))
               for t in types_presents if t in COULEURS]
    if patches:
        ax.legend(handles=patches, loc='upper left', fontsize=9,
                  framealpha=0.8, fancybox=True)

    ax.set_title(titre, fontweight='bold', color='#1a3c5e', fontsize=14, pad=15)
    ax.axis('off')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=110, bbox_inches='tight',
                facecolor='#f8fafc')
    plt.close()
    buf.seek(0)
    return buf.read()


def graphique_centralite_png(G, titre="Centralité des nœuds", top=15):
    """
    Graphique en barres horizontales des nœuds les plus centraux (PageRank ou degree).
    """
    if G.number_of_nodes() == 0:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, 'Aucune donnée', ha='center', va='center', transform=ax.transAxes)
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.read()

    # Score : PageRank ou degree pondéré
    try:
        if G.is_directed() and G.number_of_edges() > 0:
            scores = nx.pagerank(G, weight='weight', max_iter=200)
        else:
            scores = dict(G.degree(weight='weight'))
    except Exception:
        scores = dict(G.degree(weight='weight'))

    top_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top]
    labels = [G.nodes[n].get('label', n) for n, _ in top_items]
    valeurs = [v for _, v in top_items]
    couleurs = [G.nodes[n].get('color', '#1a3c5e') for n, _ in top_items]

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.5)))
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#f8fafc')

    bars = ax.barh(range(len(labels)), valeurs, color=couleurs, alpha=0.85, edgecolor='white')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_title(titre, fontweight='bold', color='#1a3c5e', fontsize=13, pad=12)
    ax.set_xlabel('Score de centralité', fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Valeurs sur les barres
    for bar, val in zip(bars, valeurs):
        ax.text(bar.get_width() * 1.01, bar.get_y() + bar.get_height() / 2,
                f'{val:.4f}', va='center', fontsize=7, color='#444')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='#f8fafc')
    plt.close()
    buf.seek(0)
    return buf.read()


def graphique_flux_financiers_png(jours=30):
    """
    Graphique de flux : montants entrants (ventes) vs sortants (achats) par mois.
    Enrichi d'une analyse de corrélation via le graphe.
    """
    from apps.ventes.models import Vente
    from apps.achats.models import CommandeAchat
    from django.db.models.functions import TruncMonth
    from django.db.models import Sum
    import pandas as pd

    debut = timezone.now() - timedelta(days=max(jours, 90))

    ventes_m = (Vente.objects
                .filter(date__gte=debut, statut__in=['confirmee', 'livree'])
                .annotate(mois=TruncMonth('date'))
                .values('mois').annotate(total=Sum('total'))
                .order_by('mois'))

    achats_m = (CommandeAchat.objects
                .filter(date__gte=debut, statut__in=['recue', 'envoyee'])
                .annotate(mois=TruncMonth('date'))
                .values('mois').annotate(total=Sum('total'))
                .order_by('mois'))

    df_v = pd.DataFrame(list(ventes_m)).rename(columns={'total': 'ventes'})
    df_a = pd.DataFrame(list(achats_m)).rename(columns={'total': 'achats'})

    if df_v.empty and df_a.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, 'Aucune donnée disponible', ha='center', va='center',
                transform=ax.transAxes, fontsize=13, color='#999')
        ax.axis('off')
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        plt.close()
        buf.seek(0)
        return buf.read()

    if not df_v.empty:
        df_v['mois'] = pd.to_datetime(df_v['mois'])
    if not df_a.empty:
        df_a['mois'] = pd.to_datetime(df_a['mois'])

    df = pd.merge(df_v, df_a, on='mois', how='outer').fillna(0).sort_values('mois')
    df['marge'] = df['ventes'] - df['achats']
    x = range(len(df))
    labels = [m.strftime('%b %Y') for m in df['mois']]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    fig.patch.set_facecolor('#f8fafc')

    width = 0.35
    ax1.bar([i - width/2 for i in x], df['ventes'], width, label='Ventes (entrées)',
            color='#27ae60', alpha=0.85, edgecolor='white')
    ax1.bar([i + width/2 for i in x], df['achats'], width, label='Achats (sorties)',
            color='#e74c3c', alpha=0.85, edgecolor='white')
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels, rotation=30, fontsize=8)
    ax1.set_title('Flux financiers mensuels (FCFA)', fontweight='bold', color='#1a3c5e', fontsize=13)
    ax1.set_facecolor('#f8fafc')
    ax1.legend(fontsize=9)
    ax1.grid(axis='y', alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    colors_marge = ['#27ae60' if v >= 0 else '#e74c3c' for v in df['marge']]
    ax2.bar(list(x), df['marge'], color=colors_marge, alpha=0.85, edgecolor='white')
    ax2.axhline(0, color='#1a3c5e', linewidth=1, linestyle='--', alpha=0.5)
    ax2.set_xticks(list(x))
    ax2.set_xticklabels(labels, rotation=30, fontsize=8)
    ax2.set_title('Marge brute mensuelle (FCFA)', fontweight='bold', color='#1a3c5e', fontsize=13)
    ax2.set_facecolor('#f8fafc')
    ax2.grid(axis='y', alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=110, bbox_inches='tight', facecolor='#f8fafc')
    plt.close()
    buf.seek(0)
    return buf.read()
