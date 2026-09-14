# TP2bis. Réduction de dimension

**Durée : 2 h.**

## Objectifs

- Comprendre pourquoi un grand nombre de variables pose problème (le fléau de la
  dimension).
- Retrouver la PCA depuis sa définition mathématique (vecteurs et valeurs propres), puis
  la comparer à l'implémentation scikit-learn.
- Utiliser t-SNE pour une visualisation non linéaire, et connaître ses pièges
  d'interprétation.
- Comparer une réduction non supervisée (PCA) à une réduction supervisée (LDA).

## Prérequis

Le [TP2](tp2-clustering.md) : PCA et UMAP y ont déjà été utilisés pour visualiser des
clusters. Ce TP revient sur le **pourquoi** et le **comment** de la PCA, et introduit
t-SNE et LDA.

```bash
pip install scikit-learn matplotlib numpy pandas
```

## Ressources

- [Distill.pub, comment lire correctement du t-SNE](https://distill.pub/2016/misread-tsne/).
- [Décomposition, documentation scikit-learn](https://scikit-learn.org/stable/modules/decomposition.html).

---

## Étape 1. Le fléau de la dimension (15 min)

Pourquoi réduire le nombre de variables plutôt que de toutes les garder ? Une expérience
simple le montre : tirez des points au hasard dans un espace de plus en plus grand, et
mesurez la distance moyenne entre un point et son plus proche voisin.

```python
import numpy as np
from sklearn.neighbors import NearestNeighbors

rng = np.random.default_rng(0)
for dimension in [2, 3, 10, 50]:
    X = rng.uniform(0, 1, size=(200, dimension))
    voisins = NearestNeighbors(n_neighbors=2).fit(X)
    distances, _ = voisins.kneighbors(X)
    print(f"dimension {dimension} : distance moyenne au plus proche voisin = {distances[:, 1].mean():.3f}")
```

!!! question "Exercice 1.1 : quantifier l'effet"
    Combien de fois la distance moyenne au plus proche voisin est-elle plus grande en
    dimension 50 qu'en dimension 2, pour ces mêmes 200 points ?

    **Résultat attendu :** un facteur d'environ `60` à `65` (la distance passe d'environ
    `0.035` à `2.24`), alors que les points sont toujours tirés dans le même intervalle
    `[0, 1]` sur chaque axe : ce n'est pas la taille de l'espace qui a changé, c'est le
    nombre d'axes.

    ??? success "Corrigé"
        ```python
        X2 = rng.uniform(0, 1, size=(200, 2))
        X50 = rng.uniform(0, 1, size=(200, 50))
        d2 = NearestNeighbors(n_neighbors=2).fit(X2).kneighbors(X2)[0][:, 1].mean()
        d50 = NearestNeighbors(n_neighbors=2).fit(X50).kneighbors(X50)[0][:, 1].mean()
        print(f"facteur : {d50 / d2:.1f}")
        ```

        En haute dimension, presque tous les points finissent à une distance comparable
        les uns des autres : la notion même de « proche voisin » perd de son sens
        discriminant. C'est le fléau de la dimension, et c'est la raison structurelle pour
        laquelle un modèle entraîné sur des centaines de variables a besoin de
        démesurément plus de données qu'un modèle à quelques variables, à qualité de
        prédiction égale.

## Étape 2. La PCA, depuis sa définition (25 min)

La PCA cherche les directions de l'espace qui portent le plus de variance. Ces directions
sont les vecteurs propres de la matrice de covariance des données centrées, et la variance
qu'elles portent est la valeur propre associée. Reconstruisons-la à la main, sur Iris :

```python
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler

iris = load_iris()
X = iris.data
y = iris.target
Xs = StandardScaler().fit_transform(X)

X_centre = Xs - Xs.mean(axis=0)
covariance = np.cov(X_centre.T)
valeurs_propres, vecteurs_propres = np.linalg.eig(covariance)

ordre = valeurs_propres.argsort()[::-1]
valeurs_propres = valeurs_propres[ordre].real
vecteurs_propres = vecteurs_propres[:, ordre].real

X_pca_manuel = X_centre @ vecteurs_propres[:, :2]
print("valeurs propres :", valeurs_propres[:2].round(3))
```

Et voici la même chose avec scikit-learn :

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2, random_state=42)
X_pca_sklearn = pca.fit_transform(Xs)
print("variance expliquée :", pca.explained_variance_.round(3))
```

!!! question "Exercice 2.1 : les deux PCA sont-elles vraiment identiques ?"
    Comparez `X_pca_manuel` et `X_pca_sklearn` sur les trois premiers points, colonne par
    colonne. La première colonne coïncide-t-elle ? La deuxième ?

    **Résultat attendu :** la première colonne coïncide exactement (aux arrondis près).
    La deuxième colonne a le **signe opposé** entre les deux versions, alors que les
    valeurs absolues sont identiques.

    ??? success "Corrigé"
        ```python
        print("manuel   :", X_pca_manuel[:3].round(3))
        print("sklearn  :", X_pca_sklearn[:3].round(3))
        ```

        Ce n'est pas une erreur : un vecteur propre reste un vecteur propre si on
        l'inverse (si \( v \) vérifie \( \Sigma v = \lambda v \), alors \( -v \) aussi).
        Deux implémentations de la PCA peuvent légitimement choisir des signes différents
        pour leurs axes. C'est pour cette raison qu'une projection PCA ne se lit jamais en
        « haut/bas » ou « gauche/droite » absolus : seule la position **relative** des
        points les uns par rapport aux autres a un sens, jamais le signe d'un axe pris
        isolément.

## Étape 3. t-SNE : préserver les voisinages, pas les distances globales (30 min)

t-SNE cherche une projection en 2D où les points proches en haute dimension restent
proches, sans chercher à préserver les distances entre points éloignés. Son paramètre
principal, `perplexity`, contrôle grossièrement le nombre de voisins considérés :

```python
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score

for perplexity in [5, 30, 50]:
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    X_tsne = tsne.fit_transform(Xs)
    score = silhouette_score(X_tsne, y)
    print(f"perplexity={perplexity} : silhouette (vs vraies espèces) = {score:.3f}")
```

!!! warning "L'IA vous le donne en trois secondes"
    Demandez à un assistant d'interpréter deux clusters t-SNE éloignés l'un de l'autre sur
    un graphique. Beaucoup répondent que « les deux groupes sont très différents »,
    en déduisant cette différence de la **distance** entre les clusters sur le graphique.
    C'est un abus d'interprétation classique et documenté (voir la ressource Distill.pub
    ci-dessus) : t-SNE optimise pour que les voisins **locaux** restent proches, il ne
    garantit rien sur la distance entre deux clusters distants, ni sur leur taille
    relative. Deux clusters très éloignés sur un graphique t-SNE ne sont pas
    nécessairement plus différents que deux clusters proches : la seule lecture fiable est
    « ces points sont voisins », jamais « cette distance vaut X fois cette autre ».

!!! question "Exercice 3.1 : l'effet de `perplexity`"
    Comparez le score de silhouette obtenu à `perplexity=5` et à `perplexity=30` (mesuré
    contre les vraies espèces d'Iris, pas contre un clustering). Lequel structure le mieux
    les trois espèces ?

    **Résultat attendu :** `perplexity=30` obtient un score plus élevé (environ `0.53`)
    que `perplexity=5` (environ `0.44`) sur ce jeu de 150 points : une perplexité trop
    basse ne capture qu'un voisinage très local, trop étroit pour un jeu de cette taille.

    ??? success "Corrigé"
        ```python
        resultats_tsne = {}
        for perplexity in [5, 30]:
            X_t = TSNE(n_components=2, perplexity=perplexity, random_state=42).fit_transform(Xs)
            resultats_tsne[perplexity] = silhouette_score(X_t, y)
        print(resultats_tsne)
        ```

        `perplexity` se choisit en fonction de la taille du jeu de données, pas d'une
        valeur universelle : la documentation scikit-learn recommande de rester entre `5`
        et `50`, et de le traiter comme un hyperparamètre à essayer sur plusieurs valeurs
        plutôt que de figer un choix par défaut.

## Étape 4. LDA : une réduction qui utilise les étiquettes (20 min)

La PCA ne regarde jamais les étiquettes : elle cherche la variance, où qu'elle soit.
L'analyse discriminante linéaire (LDA) fait l'inverse : elle cherche les axes qui séparent
le mieux des classes **connues**.

```python
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

lda = LinearDiscriminantAnalysis(n_components=2)
X_lda = lda.fit_transform(Xs, y)

print("silhouette PCA (vs vraies espèces)  :", round(silhouette_score(X_pca_sklearn, y), 3))
print("silhouette LDA (vs vraies espèces)  :", round(silhouette_score(X_lda, y), 3))
```

!!! question "Exercice 4.1 : pourquoi LDA sépare mieux"
    Le score de silhouette de LDA est-il supérieur à celui de la PCA ? Expliquez ce
    résultat à partir de ce que chaque méthode optimise.

    **Résultat attendu :** oui, LDA obtient un score nettement supérieur (environ `0.65`
    contre `0.40` pour la PCA) : LDA optimise directement la séparation entre les classes
    `y`, la PCA optimise la variance totale sans savoir que ces classes existent. Rien ne
    garantit que la direction de plus grande variance soit aussi la direction qui sépare
    le mieux les classes, et c'est précisément ce qui se produit ici.

    ??? success "Corrigé"
        Il n'y a pas de code supplémentaire, la comparaison est déjà dans le bloc
        ci-dessus. Retenez la contrepartie : LDA a besoin d'étiquettes pour fonctionner,
        ce qui la rend inutilisable pour explorer un jeu de données non étiqueté, là où
        la PCA reste toujours disponible. Le choix entre les deux dépend donc d'abord
        d'une question très concrète : avez-vous des étiquettes, et voulez-vous vous en
        servir ?

## Pour aller plus loin

- **Isomap et LLE** (`sklearn.manifold`) préservent respectivement les distances
  géodésiques et les relations linéaires locales : utiles sur des données organisées en
  variété courbe (l'exemple classique est le « Swiss Roll », `make_swiss_roll`), là où une
  PCA linéaire écraserait la structure en la projetant à plat.
- **Kernel PCA** (`sklearn.decomposition.KernelPCA`) applique la PCA après une
  transformation non linéaire de l'espace, ce qui lui permet de séparer des structures
  qu'une PCA classique ne sépare pas (l'exemple classique est `make_circles`, deux cercles
  concentriques).
- **UMAP**, déjà vu au TP2, se situe entre PCA et t-SNE : plus rapide que t-SNE, meilleure
  préservation de la structure globale, et capable de projeter de nouveaux points après
  entraînement (`reducer.transform(X_nouveau)`), ce que t-SNE ne sait pas faire.

## Ce qu'il faut retenir

Le fléau de la dimension rend la notion de « proche voisin » de moins en moins
discriminante à mesure que le nombre de variables augmente, ce qui motive toute réduction
de dimension. La PCA cherche les axes de plus grande variance ; ses composantes sont
définies à un signe près, ce qui est normal et sans conséquence sur l'interprétation
relative des points. t-SNE préserve les voisinages locaux, pas les distances globales : la
distance entre deux clusters éloignés sur un graphique t-SNE ne se lit jamais comme une
mesure quantitative. LDA, contrairement à la PCA, utilise les étiquettes pour maximiser la
séparation entre classes connues, au prix de ne plus être utilisable sans étiquette.

## Auto-évaluation

Avant de continuer, vous devez pouvoir, sans regarder le corrigé :

- [ ] expliquer en une phrase le fléau de la dimension ;
- [ ] dire ce qu'une valeur propre de la matrice de covariance représente pour la PCA ;
- [ ] expliquer pourquoi deux implémentations de la PCA peuvent différer d'un signe sur un
      axe, sans que ce soit une erreur ;
- [ ] citer une mauvaise interprétation courante d'un graphique t-SNE ;
- [ ] dire ce qui distingue PCA et LDA, et quand utiliser l'une plutôt que l'autre.

!!! info "Pas encore de QCM pour ce TP"
    Contrairement au module IA générative, ce TP n'a pas de QCM d'auto-évaluation prêt à
    l'emploi : les TP d'IA prédictive n'en ont jamais eu. En créer un est possible avec le
    skill `qcm-generator`, mais reste à faire.

[Passer au TP3](tp3-classification.md){ .md-button .md-button--primary }
