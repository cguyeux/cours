# IA prédictive : analyse et modélisation de données

Travaux pratiques de troisième année du BUT informatique, sur l'analyse de données et
l'apprentissage automatique.

## Une différence avec le module IA générative

Contrairement au module [IA générative](../ia-generative/index.md), aucun TP de ce module
ne dépend d'une clé API : tout s'exécute en local avec des bibliothèques Python courantes
(pandas, scikit-learn, xgboost, statsmodels...), et **le code de chaque TP est vérifié par
le harnais du site**, au même titre que les TP d'[outils fondamentaux](../outils-fondamentaux/index.md) :
chaque valeur annoncée dans un « résultat attendu » a été réellement calculée, pas devinée.

## Les séances

| Séance | Sujet | Ce que vous saurez faire |
|---|---|---|
| [TP1](tp1-pandas.md) | Pandas | charger, sélectionner, filtrer, transformer, agréger, visualiser un jeu de données |
| [TP1bis](tp1bis-geopandas.md) | GeoPandas | géométries, systèmes de coordonnées, jointure spatiale, cartographie thématique |
| [TP2](tp2-clustering.md) | Clustering | K-Means, DBSCAN, HDBSCAN, choisir un nombre de clusters, réduire la dimension pour visualiser |
| [TP2bis](tp2bis-reduction-dimension.md) | Réduction de dimension | le fléau de la dimension, PCA depuis sa définition, t-SNE, LDA |
| [TP3](tp3-classification.md) | Classification | apprentissage supervisé, arbres, forêts, métriques de classification |
| [TP5](tp5-regression.md) | Régression et validation | un troisième ensemble (validation), au delà du couple entraînement/test |
| [TP4](tp4-xgboost.md) | XGBoost | arrêt anticipé, courbe d'apprentissage, sous et surapprentissage |
| [TP6](tp6-series-temporelles.md) | Séries temporelles | tendance, saisonnalité, stationnarité, ARIMA, approche supervisée |
| [TP7](tp7-xgboost-objectifs-metriques.md) | XGBoost, objectifs et métriques | fonctions objectif personnalisées, métriques d'évaluation |
| [TP8](tp8-pretraitement.md) | Prétraitement des variables | sélection, normalisation, encodage, valeurs aberrantes, classes déséquilibrées |
| [TP9](tp9-xgboost-explicabilite-causalite.md) | XGBoost, explicabilité et causalité | valeurs de Shapley (SHAP), corrélation contre causalité |
| [TP10](tp10-theorie-information.md) | Théorie de l'information | entropie, information mutuelle, lien avec les arbres de décision |

Le TP4 (XGBoost) est volontairement placé après le TP5 (régression et validation) dans ce
parcours, pas avant : il s'appuie sur la notion d'ensemble de validation que le TP5
introduit. Les numéros de TP reprennent ceux du corpus source ; l'ordre de lecture
recommandé est celui du tableau ci-dessus et de la navigation du site.

Aucun TP de ce module n'a de QCM d'auto-évaluation pour l'instant ; c'est signalé sur
chaque page.

## Ce que le harnais a trouvé en chemin

Convertir ces TP en pages testées a mis au jour plusieurs décalages entre le corpus
source (rédigé avant janvier 2026) et les bibliothèques réellement installées : des
paramètres scikit-learn et XGBoost supprimés ou déplacés, une bibliothèque de causalité
(`dowhy`) incompatible avec l'environnement du site et remplacée par `econml`, et deux
corrigés bien réels mais mal classés dans le corpus source (voir le journal du projet
pour le détail). Chaque décalage est documenté directement sur la page concernée plutôt
que caché.
