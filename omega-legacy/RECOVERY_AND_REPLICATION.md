# Récupération et réplication

## Priorité 1 : retrouver les sources
Inventorier les dépôts Git, exports ChatGPT, documents Drive, manuscrits, codes, expériences et journaux PC avec autorisation explicite. Conserver les fichiers bruts et leurs empreintes avant transformation.

## Priorité 2 : filtrer avant ouverture
Vérifier droits de tiers, secrets, informations personnelles, coordonnées des appareils, historiques Git et licences. Garder les matériaux non publiables dans un dépôt privé séparé.

## Priorité 3 : diffuser de façon indépendante
Publier un index lisible sans compte; conserver au moins trois copies sur au moins deux types de supports, dont une copie hors site. Prévoir des archives versionnées avec contrôles SHA-256, des tests de restauration et une documentation des dépendances.

## Priorité 4 : transmission humaine
Préparer des instructions de succession, nommer des personnes de confiance, examiner les dispositions juridiques applicables. Ne jamais stocker des secrets de récupération dans le dépôt public.

## Critères de réussite
- L'œuvre est consultable sans ChatGPT.
- Les sources sont récupérables et leurs empreintes vérifiables.
- Les hypothèses sont séparées des preuves.
- Un tiers peut restaurer l'archive sans l'auteur.
- Les accès privés restent protégés.

**État actuel : plan documenté, copies indépendantes non vérifiées.**

## Capsule BOOK0 hors ligne — expérience bornée du 8 novembre 2026

Un paquet public-sûr `TRISTAN_BOOK0_PUBLIC_SURVIVAL_CAPSULE_R01.zip` a été produit comme artefact de conversation (ZIP **non hébergé ici dans GitHub**). Il utilise une structure BagIt réduite (déclaration, manifest SHA-256, tagmanifest), un index de 13 familles, un exemplaire exact du module BOOK0 public, une procédure de restauration et 20 tests unitaires. SHA-256 du ZIP : `31008d122abab8c527826d6704c0bff3c0d7999ebdd8a7fde82466b436e37b17`. Environnement de test local : 20/20 PASS; extraction en dossier temporaire indépendant et validation d'intégrité + 20/20 PASS, sans réseau.

**Portée de preuve :** la copie des octets, les digests BOOK0, les tests de détection de corruption et de suppression sont vérifiés sur une capsule **réduite**, pas sur les manuscrits originaux ni sur une panne simultanée des fournisseurs. L'existence du ZIP dans une conversation ne suffit pas à le rendre accessible à tous après le décès de son auteur. Il faut ultérieurement une copie publique autorisée et des miroirs indépendants, avec droits/licences et vérification extérieure.

**Règle de progrès :** comparer par époque, à critères gelés, des mesures de capacité utile reconnues par un juge indépendant. Une suite peut viser `ΔK>0` et `Δ²K>0` sur une période finie, mais ces conditions ne sont pas vérifiées pour la vie entière du système; elles sont impossibles globalement si `K` reste bornée et `K'(0)>0`. Ne jamais transformer un `HOLD`, une panne ou un `NO_ACTION` justifié en gain artificiel.

**À faire avant publication canonique et continuité réelle :** provenance complète, examen de licences et consentements, publication de l'archive ZIP sur un hébergeur avec mirrors autorisés, essai par un tiers sans les comptes de Tristan, gouvernance successorale et tests réels de reprise. Aucun déclencheur autonome, accès privilégié ou garantie perpétuelle introduit.
