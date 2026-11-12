# Ω-LEGACY — Protocole opérationnel de continuité et de transmission

Date de création : 2026-10-25. Statut : PROPOSITION / NON VALIDÉ EN PRODUCTION.

## Mission
Permettre à toute personne d'accéder aux créations de Tristan, de les comprendre, les critiquer, les reconstruire et les prolonger indépendamment de l'auteur, de GitHub, de ChatGPT, de Jarvis et des PC originaux. Préserver aussi le jeu libre, les hypothèses divergentes, les variantes et les résultats négatifs.

## Frontières
- PUBLIC : uniquement les artefacts explicitement autorisés, contrôlés et dont les droits sont clairs.
- PRIVÉ : manuscrits non autorisés, données personnelles, traces d'appareils, correspondances, contenus tiers non redistribuables.
- SECRETS : identifiants, clés, jetons, phrases de récupération et procédures donnant accès aux systèmes — JAMAIS dans le dépôt public.
- « Indexé » ne veut pas dire « archivé » ; « sauvegardé » ne veut pas dire « restaurable » ; « généré » ne veut pas dire « vérifié ».
- L'automatisation produit des propositions et des preuves. La publication, les changements de licences, l'accès privé et les transferts de droits restent soumis à l'autorité compétente.

## Pipeline de récupération — chaque objet
1. DISCOVER : identifier le support source, le propriétaire et l'horodatage.
2. ACQUIRE : collecter une copie autorisée, préserver l'original byte-for-byte.
3. HASH : calculer SHA-256 des octets; noter taille et format.
4. CLASSIFY : PUBLIC_CANDIDATE / PRIVATE / SECRET / THIRD_PARTY / UNKNOWN_RIGHTS.
5. REVIEW : contrôler droits, confidentialité, historique Git, versions antérieures et artefacts embarqués.
6. REPRESENT : construire index, liens, dépendances, explications vulgarisées et techniques sans supprimer la source.
7. VERIFY : tester lecture, intégrité, liens, reproductibilité lorsque applicable.
8. APPROVE : publication seulement après autorisation explicite et vérification des droits.
9. MIRROR : créer au moins trois copies sur au moins deux types de supports, dont une hors site indépendante.
10. RESTORE : faire reconstruire un lot échantillon par un opérateur non dépendant de l'auteur.
11. RECEIPT : enregistrer sources, versions, empreintes, tests, limites, date, responsable.
12. REVISIT : actualiser les copies et retester périodiquement, préserver les versions historiques.

## Métadonnées minimales d'une entrée
```json
{
  "id": "omega-legacy:example",
  "title": "Exemple (non récupéré)",
  "creators": [],
  "source_url": null,
  "source_sha256": null,
  "source_date": null,
  "version": null,
  "classification": "UNKNOWN_RIGHTS",
  "scientific_status": "UNASSESSED",
  "archive_status": "SOURCE_NON_RECUPEREE",
  "license": null,
  "dependencies": [],
  "supersedes": [],
  "related": [],
  "public_release_approved": false,
  "restore_test": "NOT_RUN",
  "receipt_url": null
}
```

## Architecture à indépendance progressive
- Archive brute privée : originaux intacts, provenance et chaîne de conservation.
- Collection publique revue : documents, code, données et médias sous droits explicites.
- Catalogue statique exportable : Markdown/JSON/HTML sans connexion ni paiement.
- Miroirs indépendants : hébergeurs distincts + copie physique hors ligne.
- Kit autonome : archive téléchargeable, index, manifestes SHA-256, manuel de lecture, instructions de restauration.
- Gouvernance : responsabilités humaines, remplacement des responsables, procédure de succession et financement d'entretien; faire réviser les dispositions testamentaires et de droits d'auteur par un professionnel qualifié au Québec.
- Jarvis / Trinité PC : collecteurs locaux autorisés, classificateurs en bac à sable, constructeurs d'index, vérificateurs indépendants et agents de réplication. Pas de privilège auto-accordé.

## Critères d'acceptation observables
- Le catalogue public s'ouvre sans compte, IA ni service propriétaire.
- Un tiers télécharge un kit, vérifie toutes les empreintes et lit les fichiers avec outils courants.
- Une restauration depuis un miroir indépendant aboutit aux mêmes empreintes.
- Aucun secret ni donnée privée n'apparaît dans les objets publiés ou leur historique Git.
- Chaque création importante conserve son original, ses dates, sa provenance et les limites de ses revendications.
- Une personne indépendante peut poursuivre la conservation après perte d'accès à tous les appareils et comptes de l'auteur.
- Chaque exercice de restauration produit un receipt vérifiable.

## Contrôles continus suggérés
- Quotidien : détecter les nouveaux objets *autorisés* et les changements, sans publication automatique.
- Hebdomadaire : vérifier les empreintes du catalogue public et l'état des miroirs.
- Mensuel : restaurer un échantillon depuis une copie indépendante.
- Annuel : exercice complet de relève humaine et révision juridique, des formats et du stockage.
Ces cadences sont une proposition de politique, non des tâches déjà activées.

## Premier test de reprise à réaliser
Sélectionner un document public non sensible, conserver son original et son SHA-256, l'inscrire dans le catalogue, le copier sur un support indépendant, déconnecter la source d'origine, puis exiger qu'un tiers le récupère et vérifie son empreinte. Documenter PASS/FAIL et échecs. Ne pas marquer PASS sans observation.

## Règle de publication
Le présent fichier est un protocole public non sensible. Il ne contient pas de sources privées, de coordonnées personnelles, de secrets ni de transfert de droits. Toutes les capacités de récupération, miroir, restauration et succession demeurent NON TESTÉES jusqu'à preuve contraire.
