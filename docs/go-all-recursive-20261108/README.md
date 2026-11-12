# GO ALL Tristan : synthèses récursives et travail humain économisé

Date : 8 novembre 2026  
Statut : **SPECIFICATION_CANDIDATE**  
Portée : proposition documentaire originale ; aucune activation de service, aucun déploiement et aucune économie réelle d’heures revendiqués.

## 1. Finalité et continuité

Cette proposition organise une ambition précise : réutiliser les créations et les connaissances accumulées pour produire des capacités utiles, transmissibles et progressivement moins dépendantes du travail de leur créateur. Chaque itération doit également faciliter les suivantes. La mesure recherchée porte sur le travail humain effectivement évité, à qualité comparable, après déduction des efforts de préparation, de contrôle, de réparation et d’entretien.

Le dépôt public contient déjà des propriétaires adaptés. [Jarvis R9](../../docs/JARVIS_R9_ULTRA_CLOSURE.md) définit des missions, des capacités régénérables et une progression incluant le travail futur éliminé. [Jarvis R12](../../docs/JARVIS_R12_INTENT_REALITY_DELTA.md) distingue récupération historique, accomplissement et vérification. Cette proposition étend leur vocabulaire documentaire. Elle ne crée ni ordonnanceur, ni autorité, ni mémoire concurrente.

Les notations ci-dessous sont des **définitions candidates explicites**. Elles ne prétendent pas reconstituer une définition historique absente. La conservation des sources et des variantes permet de les corriger lorsqu’un texte antérieur est retrouvé.

## 2. Distinguer les indices

| Symbole | Sens proposé |
| --- | --- |
| `n` | Étiquette d’ordre ou de génération d’un collectif. |
| `k` | Décalage vers une génération antérieure : les parents ont un ordre `n-k`. |
| `N_n` | Nombre de membres sélectionnés pour contribuer au nouveau collectif. |
| `n_i` | Nombre de répétitions locales de l’opérateur associé à l’élément `i`. |
| `m_{i,n_i,j}` | Nombre d’applications croisées de cet opérateur au contexte ou à l’élément `j`. |
| `depth` | Profondeur effective du graphe des dépendances. |
| `n_T` | Nom conservé ; un typage multidimensionnel est proposé, sans définition historique revendiquée. |
| `MetaN` | Nom conservé ; politique candidate de choix des indices et budgets. |

L’ordre et la profondeur restent distincts. Pour un collectif ayant des parents, sa profondeur vaut `1 + max(depth(parent))`. Son ordre demeure l’étiquette `n` déclarée. Une génération peut dépendre uniquement de `n-3` et `n-5` ; il serait alors incorrect d’imposer que son ordre soit un plus le maximum des ordres parentaux.

Chaque enregistrement conserve séparément la date de création, l’ordre, la profondeur et les versions des parents. Une génération élevée ne démontre aucune qualité supérieure.

## 3. Deux lignées de synthèse

On conserve deux lignées distinctes :

- **G** : synergies et synthèses générales ;
- **T** : synergies et synthèses TOP, construites à partir de parents appartenant explicitement à la lignée TOP.

Pour une lignée `L`, le réservoir de parents admissibles est :

```text
Pool(L,n) = union des Archive(L,n-k), pour k dans Delays(L,n)
Selected(L,n) = Select(Pool(L,n), cardinalité=N(L,n), contexte)
Collective(L,n) = Compose(Selected(L,n), rôles, interfaces)
```

Chaque décalage est strictement positif, chaque parent a un ordre inférieur à `n`, et chaque référence est liée à une version. Les paramètres peuvent différer entre les deux lignées. La sélection de `N(L,n)` meilleurs candidats exige un critère explicite : objectif, métriques, validité et incertitude.

Les archives gardent aussi les candidats non sélectionnés, leurs limites et les raisons du rejet. Une transformation entre G et T peut être proposée, mais elle doit posséder une identité et une justification. Le système ne transforme pas silencieusement toute synthèse générale en synthèse TOP.

## 4. Tous les membres sélectionnés restent actifs

Dans le nouveau collectif, **les N membres sélectionnés doivent tous contribuer**. Un indicateur `active=true`, une citation ou une présence dans une liste ne suffit pas.

Le contrat de participation décrit, pour chaque membre :

1. son entrée typée et sa version ;
2. son rôle dans la composition ;
3. la transformation, le calcul, la proposition ou le test auquel il contribue ;
4. sa sortie attendue et la manière de vérifier cette contribution ;
5. ses dépendances et ses limites.

Une contribution peut être différente selon le rôle : produire une variante, fournir une représentation, construire un contre-exemple ou effectuer une vérification distincte. Les responsabilités de production et de jugement restent explicites.

Si un membre manque, échoue ou demeure indisponible, le collectif prévu est incomplet. Une réduction de cardinalité constitue un **nouveau collectif versionné**. Un budget insuffisant entraîne un redimensionnement explicite ou un report ; il n’autorise pas à annoncer N membres actifs après en avoir utilisé moins.

## 5. Préserver les axes TOP

Les noms et la sémantique complète des axes TOP historiques ne sont pas établis ici. Ils sont donc conservés dans un champ opaque `top_axes`, accompagné de `schema_ref`, `source_ref` et `source_version`. Une valeur inconnue demeure inconnue.

Cette enveloppe exige de déclarer les axes conservés au lieu de les remplacer arbitrairement par un score unique. Une transformation doit déclarer les axes transmis, leur représentation et toute perte éventuelle. Une implémentation devra vérifier ces déclarations. La réduction d’une vue destinée à la lecture ne réduit pas automatiquement le contrat du collectif.

Le [Top de l’Atlas R8](../../docs/JARVIS_R8_FINAL_FUSION.md) organise l’attention selon l’intention. Il ne fournit pas une preuve de vérité ni une définition historique des axes TOP de cette proposition. Une correspondance entre les deux exige un adaptateur documenté.

## 6. Le TOP conserve diversité et racines

Une sélection concentrée uniquement sur les derniers gagnants peut perdre des méthodes anciennes, rares ou complémentaires. La politique candidate conserve donc plusieurs dimensions : qualité observée, couverture, coût, incertitude, diversité et valeur de récupération des racines.

La diversité ne dispense jamais des exigences minimales de validité. Elle intervient entre candidats admissibles, ou dans un budget d’exploration distinct. La part réservée aux racines doit être déclarée avant l’évaluation ; aucune fraction universelle n’est imposée.

Une comparaison utile confronte trois politiques à ressources comparables : TOP seul, TOP avec diversité, TOP avec diversité et récupération historique. Le résultat peut favoriser une politique différente selon le domaine. Les exemples historiques retrouvés servent à produire des expériences nouvelles ; leur ancienneté ne les rend ni vrais ni obsolètes.

## 7. Auto-application typée et ordre des opérations

Un élément devient applicable lorsqu’un opérateur associé précise ses types d’entrée et de sortie. Appliquer une théorie, une méthode ou une synthèse à elle-même exige donc une représentation compatible.

```text
self(i)  = iterate(Phi_i, n_i, representation(i))
transformed_operator(i) = operator_from(self(i))
cross(i,j) = iterate(transformed_operator(i), m(i,n_i,j), representation(j))
```

Ces expressions désignent des programmes candidats. `operator_from` doit être défini et vérifié pour le type de la représentation obtenue : un objet quelconque ne devient pas un opérateur par son seul nom. L’application croisée dépend ainsi effectivement du résultat des `n_i` auto-applications. Si le résultat d’une étape n’appartient plus au domaine de l’étape suivante, une conversion explicite est nécessaire. Une application non définie reste non définie.

La composition ne suppose pas la commutativité : `Phi_i après Phi_j` peut être différente de `Phi_j après Phi_i`, voire être seule à avoir un sens. Le graphe conserve l’ordre, les conversions et les invariants attendus. Les essais doivent distinguer différence réelle, erreur de typage et perte de représentation.

L’auto-application concerne aussi cette spécification : elle peut être critiquée, simplifiée et remplacée. Sa révision conserve les sources, les résultats négatifs et les limites de la version précédente.

## 8. Objet-T, MétaObjet-T et paramètres n_T

Un collectif peut être décrit comme un objet : identité, version, représentations, parents, transformations, preuves, limites, droits et procédure de reconstruction. Un MétaObjet-T décrit les règles de construction, de sélection et de révision de tels objets.

Cette distinction est fonctionnelle. Un MétaObjet-T ne reçoit aucun privilège d’auto-approbation. Une modification du sélectionneur doit être évaluée sur des cas distincts de ceux qui ont servi à la proposer.

Pour `n_T`, une proposition de typage est un enregistrement nommé contenant, par exemple, ordre, profondeur, échelle, budget, représentation et horizon de prévision. Ces dimensions sont **des choix de conception nouveaux**, remplaçables et versionnés. Elles ne définissent pas rétroactivement le terme historique.

`MetaN` peut alors désigner une politique qui choisit les paramètres selon les résultats et les ressources. Son évaluation comprend le coût de cette adaptation. Une politique constante et simple reste une référence légitime.

## 9. Prévoir n+k sans confondre prévision et résultat

L’intuition du `n+k` se traduit par une prévision testable formulée avant la matérialisation des étapes intermédiaires. Elle indique une cible, un horizon, des conditions, un résultat attendu, une incertitude et un critère d’échec.

Le [registre public de prédictions](../../src/tristan/prediction_ledger.py) peut lier une déclaration à une portée et à une chaîne d’empreintes. Son code vérifie une intégrité locale ; il ne garantit pas un horodatage externe ni la véracité de la prédiction. Un ancrage indépendant est nécessaire lorsqu’une preuve d’antériorité est importante.

[R12](../../docs/JARVIS_R12_INTENT_REALITY_DELTA.md) fournit la séparation entre le moment auquel un événement se rapporte et celui où il est enregistré. La prévision, le résultat observé et l’évaluation sont trois événements distincts.

Prévoir juste après avoir vu le résultat n’est pas une anticipation validée. Une prédiction convaincante ne dispense pas non plus de construire et vérifier les dépendances nécessaires à son utilisation.

## 10. Mesurer les heures humaines nettes

L’unité de mesure primaire est la seconde de travail humain actif. Pour un épisode comparable :

```text
gain_opérationnel =
    effort_humain_référence
  - effort_humain_avec_système

gain_net_cumulé =
    somme(gains_opérationnels_des_épisodes_uniques)
  - investissement_initial_unique
  - efforts_non_déjà_imputés
```

L’effort de chaque route comprend la préparation, l’exécution humaine, la revue, la correction, la récupération et la maintenance attribuable. Le temps d’attente, le temps machine et les coûts financiers sont enregistrés séparément. Un processeur occupé pendant une heure ne prouve pas une heure humaine économisée.

Les efforts non déjà imputés comprennent les tentatives échouées ou abandonnées et les frais humains transversaux qui ne sont rattachés à aucun épisode. Chaque événement de coût appartient à une seule catégorie : épisode, investissement ou coût résiduel. Un échec ne disparaît pas des comptes parce qu’il n’a produit aucun résultat utile. Les différences et le bilan net peuvent être négatifs et ne sont jamais ramenés artificiellement à zéro.

La référence doit correspondre à une tâche utile et à une qualité comparable : méthode courante, outil existant, route simple ou combinaison déjà disponible. Les deux routes ne peuvent pas toujours être observées sur le même épisode ; l’économie reste alors une **estimation comparative fondée sur des mesures**, avec portée et incertitude.

Les heures prédites, les heures mesurées dans les épisodes et le gain net estimé restent dans trois champs distincts. Une valeur inconnue utilise `null`, jamais zéro par défaut.

## 11. Investissement, réutilisation et double comptage

Le coût initial de conception, d’installation et de migration reçoit un identifiant stable. Il est déduit une seule fois sur le périmètre choisi. La maintenance récurrente reçoit ses propres événements.

Un épisode possède un identifiant de travail, un périmètre, une version de capacité et une famille de doublons. Le total d’une chaîne ne s’ajoute pas aux sous-totaux des composants qui expliquent ce même résultat. Les crédits attribués aux composants décrivent la répartition analytique ; ils ne créent pas de nouvelles heures.

Le [module public d’ablation](../../src/tristan/causal_credit.py) fournit une comparaison avec et sans composante. Ses contributions locales ne constituent pas une preuve causale générale et peuvent interagir. On ne somme pas automatiquement leurs différences pour reconstituer le gain de bout en bout.

La réutilisation future reçoit un pronostic séparé. Elle devient un résultat documenté lorsqu’un nouvel épisode se produit. Le point d’amortissement est atteint seulement lorsque les gains cumulés couvrent l’investissement observé selon la convention comptable retenue.

## 12. Croissance, accélération et choix des itérations

L’objectif est une croissance durable des capacités utiles et une diminution de la charge humaine. Une accélération strictement positive à chaque instant ne peut pas être garantie : pannes, régressions, apprentissage, saturation et changements de contexte existent.

La politique candidate maximise plutôt un gain net attendu, à horizon déclaré, sous contraintes de qualité, de ressources et de vérification. Elle conserve séparément valeur sociale, transmissibilité et heures économisées : un travail important peut produire peu d’économie immédiate.

On mesure la tendance sur une fenêtre définie avant l’analyse. Les itérations de maintenance, de reconstruction ou de correction peuvent avoir un gain immédiat négatif et une valeur ultérieure documentable. Elles restent visibles dans les comptes.

## 13. Publication reproductible et portée de licence

Ce dossier doit permettre à un lecteur de comprendre les notations, de reproduire le calcul illustratif et de contester les critères. Il contient une spécification, un exemple JSON fictif et un manifeste de portée.

La licence MIT incluse dans `LICENSE` s’applique uniquement aux nouveaux fichiers explicitement énumérés par `release_scope.json`. Elle ne modifie pas la licence du dépôt, des dépendances, des données ou des documents cités. Aucune source privée n’est nécessaire pour lire ce dossier.

L’exemple `human_work_ledger.example.json` contient des nombres inventés pour expliquer le calcul. Il n’est ni un reçu d’exécution, ni une mesure du Projet de Tristan, ni une preuve de gain financier. Ses champs signalent le statut illustratif ; une implémentation devra refuser son ingestion comme mesure réelle.

## 14. Critères de passage vers une implémentation

Une implémentation ultérieure devra vérifier les deux lignées, les références temporelles, la participation de tous les membres sélectionnés, la conservation des axes TOP et le typage des compositions. Elle devra également rejeter les doublons comptables et les changements silencieux de référence.

Un premier essai utile compare une mission réelle bornée avec sa méthode courante. Il préenregistre la prédiction, mesure les efforts humains, vérifie la qualité, conserve l’investissement et produit un delta R12 lié à la mission R9.

La réussite de ce dossier est documentaire : définitions explicites, sources publiques, calcul compréhensible et limites visibles. La réussite opérationnelle demandera des exécutions et des observations supplémentaires.

## Références publiques fixées

Les liens ci-dessous fixent les sources au commit public `f0eff43be8cf819ec68cc7f4d641f408446c8a59` :

- [Jarvis R9 — Ultra Closure](https://github.com/tardifmorencytristan-glitch/Tristan/blob/f0eff43be8cf819ec68cc7f4d641f408446c8a59/docs/JARVIS_R9_ULTRA_CLOSURE.md).
- [Jarvis R12 — Intent Reality Delta](https://github.com/tardifmorencytristan-glitch/Tristan/blob/f0eff43be8cf819ec68cc7f4d641f408446c8a59/docs/JARVIS_R12_INTENT_REALITY_DELTA.md).
- [Jarvis R8 — Final Fusion](https://github.com/tardifmorencytristan-glitch/Tristan/blob/f0eff43be8cf819ec68cc7f4d641f408446c8a59/docs/JARVIS_R8_FINAL_FUSION.md).
- [Prediction Ledger](https://github.com/tardifmorencytristan-glitch/Tristan/blob/f0eff43be8cf819ec68cc7f4d641f408446c8a59/src/tristan/prediction_ledger.py).
- [Causal Credit](https://github.com/tardifmorencytristan-glitch/Tristan/blob/f0eff43be8cf819ec68cc7f4d641f408446c8a59/src/tristan/causal_credit.py).

