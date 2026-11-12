---
title: "Système de gestion intégrée (SGI) – Évaluation des facteurs relatifs à la vie privée : Affaires mondiales Canada"
institution_id: "ati-schedule-i-department-of-foreign-affairs-trade-and-development"
language: "fr"
source_url: "https://international.canada.ca/fr/affaires-mondiales/organisation/transparence/aiprp/evaluation-facteur/sgi"
retrieved_at_utc: "2026-11-12T05:48:58.855954+00:00"
http_status: 200
source_sha256: "44d728355c6d8598f6b046f94bb42a6b98630a18f4d57b1b21ae39b5d98939e4"
content_kind: "page"
---

# Système de gestion intégrée (SGI) – Évaluation des facteurs relatifs à la vie privée : Affaires mondiales Canada

## Sommaire exécutif

Le Système de gestion intégrée (SGI) est, depuis 1998, le système ministériel de planification des ressources de l’organisation (PRO) utilisé pour la comptabilité, notamment l’enregistrement des transactions de relevés salariaux, le contrôle de gestion, l’établissement du budget, la gestion des stocks, l’approvisionnement et la comptabilité des immobilisations.

Toutes les transactions financières et matérielles du Ministère se trouvent dans le SGI.

Le système appartient à la Direction des systèmes financiers corporatifs (DSFC) et est configurée et appuyée par celle–ci. La gestion technique, quant à elle, relève de la Direction des solutions ministérielles d’entreprise.

Le SGI est classé en tant qu’application critique pour appuyer les activités de programmes pour le traitement des comptes payables et des transferts de fonds et doit, par conséquent, être conforme à la Gestion de la sécurité des technologies (GSTI), ce qui comprend une évaluation préliminaire des facteurs relatifs à la vie privée (ÉPFVP). En outre, depuis la mise en œuvre de la *Politique d’évaluation des facteurs relatifs à la vie privée* en mai 2002, une ÉPFVP n’avait pas été effectuée, et il était alors essentiel d’en effectuer une pour satisfaire aux exigences en matière de politiques de la GSTI et de l’ÉFVP.

L’architecture des systèmes corporatifs du MAECI est complexe et comprend des interfaces entre le SGI, le Système de gestion des ressources humaines (SGRH), le Système de gestion salariale (SGR) et les renseignements d’entreprise (BI–Cognos), de même que des interfaces avec des organismes centraux, d’autres applications internes et d’autres ministères.

Le champ de l’ÉPFVP comprenait des modules du SGI utilisés dans l’environnement de production en date de février 2009. Toutefois, TOUTES les interfaces d’entrée et de sortie du SGI avec les autres applications ont été exclues. Par conséquent, le champ de l’ÉPFVP comprenaient les modules du SGI suivants:

**FI :** Le module FI (comptabilité financière) appuie les exigences principales en matière de comptabilité et de finance du Ministère. C’est dans le cadre de ce module que les directeurs financiers ainsi que d’autres gestionnaires des missions et de l’Administration centrale peuvent examiner la position financière du Ministère en temps réel. Les renseignements sont opportuns et appuient adéquatement la prise de décisions et la planification stratégique. Le module FI (Comptabilité financière) est intégré aux autres modules du SGI, comme les modules MM (Gestion des matières), PP (Planification de la production), PM (Maintenance) et PS (Gestion de projets).

**FI–AA :** Le module Comptabilité des immobilisations (AA) est utilisé pour la gestion et le suivi des immobilisations corporelles. Dans le module de comptabilité financière, il sert de grand livre auxiliaire pour le grand livre général, fournissant des renseignements détaillés sur les transactions comprenant des immobilisations corporelles.

AA est utilisé par des utilisateurs spécialisés au sein de la Direction générale des biens et des bureaux de la gestion de l’information et de la technologie à la fois à l’Administration centrale et dans les missions. AA englobe le cycle de vie entier des immobilisations, de leur acquisition ou du début de leur construction jusqu’à leur cession. Ce module permet de calculer et de comptabiliser l’amortissement des immobilisations conformément aux plans d’amortissement du Ministère.

**MM :** Le module Gestion des articles appuie le cycle de vie complet de l’achat au paiement. Même si l’utilisation de ce module est obligatoire à l’Administration centrale, il est dans le processus d’être lancé dans les missions. Il comprend la fonctionnalité suivante :

## Achats

L’acquisition de biens et/ou de services est enregistrée dans le SGI par l’utilisation de demandes d’achat (PR) et/ou de bons de commande (PO). Les PR et les PO créent des engagements dans le module FM, et réduisent donc la réservation de fonds applicable ou le solde disponible. Une fois les biens reçus, les utilisateurs peuvent effectuer la transaction facultative d’entrée de biens. Afin d’optimiser les processus d’achat, il est également possible d’effectuer les demandes de prix/d’offres et d’enregistrer les accords d’achat à long terme dans le module MM.

### Contrôle des factures logistique (LIV)

Le contrôle des factures est une autre composante du module MM. En référence à un PO, le contrôle des factures vérifie l’exactitude du contenu, du prix et du calcul des factures. Lorsqu’une facture est enregistrée, le système crée un poste non soldé dans le compte fournisseur, poste qui est ensuite soldé par la Comptabilité financière au moment du paiement.

### Gestion des stocks (IM)

Faisant aussi partie du module MM, la composante Gestion des stocks sert à gérer le nombre et la valeur des articles gérés en stock. En plus d’offrir les fonctions nécessaires à la gestion des entrées et des sorties de marchandises quotidiennes, la composante Gestion des stocks peut être utilisée pour la planification des besoins de matières (MRP) afin de générer les recommandations d’approvisionnement et l’inventaire matériel utilisés aux fins de la vérification des stocks.

**CO :** Le module CO (Contrôle de gestion) permet une souplesse additionnelle en ce qui touche l’établissement de rapports au niveau du centre de coûts en vue de satisfaire aux exigences opérationnelles additionnelles. Le niveau additionnel de granularité appuie la fonction de contrôle et permet aux gestionnaires de mieux comprendre les coûts de programmes à la fois aux niveaux de l’Administration centrale que des missions.

Par exemple, les gestionnaires ont la capacité de créer des unités organisationnelles à un niveau moins élevé que le centre de fonds – p. ex. le Centre de coûts pour planifier, enregistrer et contrôler les transactions financières, et établir des rapports sur celles–ci. Il offre aussi l’utilisation de commandes internes (I/O) pour assurer un suivi des transactions financières dans un regroupement logique aux fins d’établissement de rapports et de règlement.

Actuellement, les centres de coûts et les numéros d’ordre interne sont utilisés.

**PM :** Le module Maintenance (PM) permet à l’utilisateur de gérer des pièces d’équipement de manière indépendante. Une pièce d’équipement est un objet individuel dont la gestion doit être assurée de façon indépendante dans le système, afin que vous puissiez :

- gérer les données individuelles du point de vue de la maintenance
- effectuer des tâches individuelles de maintenance
- tenir un dossier des tâches de maintenance effectuées
- recueillir et évaluer les données sur une longue période de temps

L’équipement et les fonctionnalités relatives aux postes techniques du module PM sont actuellement utilisés au MAECI.

Les pièces d’équipement peuvent être installées et démontées dans des postes fonctionnels. Un poste fonctionnel représente une zone de système où des pièces d’équipement peuvent être installées, démontées ou dans laquelle une tâche de maintenance peut être effectuée. La durée d’utilisation d’une pièce d’équipement à un poste fonctionnel est documentée au fil du temps. À l’heure actuelle, la Direction de l’approvisionnement, de la gestion du matériel et de la logistique utilise le module PM pour assurer le suivi de l’ameublement et du matériel de bureau tout au long de leur vie utile, tandis que Collection des arts visuels l’utilise pour assurer le suivi des éléments de représentation et des objets d’art. Enfin, la Direction générale de la gestion de l’information et de la technologie tient l’inventaire de ses biens TI, de leur acquisition à leur élimination, dans ITAMS, le système qui lie le module Maintenance au logiciel Remedy.

**SD :** Le module Administration des ventes (SD) est seulement utilisé par Passeport Canada. SD permet aux utilisateurs d’effectuer différentes transactions opérationnelles en fonction des documents de ventes définis dans le système. Passeport Canada l’utilise pour les bons de commande. Les entrées dans SD sont générées par l’intermédiaire d’une interface avec IRIS (non un module du SGI). Il existe un protocole d’entente entre le MAECI et Passeport Canada.

**SPL :** Le module Grand livre à vocation spéciale (SPL) permet à l’utilisateur de définir les grands livres aux fins d’établissement de rapports. Les grands livres définis par l’utilisateur peuvent être utilisés à titre de grands livres généraux ou de grands livres auxiliaires avec divers objets d’affectation des comptes. Les objets d’affectation des comptes peuvent être soit de dimensions SAP de diverses applications (comme le compte, le centre de coûts, le domaine opérationnel et le centre de profit) ou de dimensions définies selon le client (comme la région).

Le module SPL permet à l’utilisateur d’établir des rapports à divers niveaux en utilisant les valeurs des diverses composantes d’application. Les fonctions disponibles dans le SPL vous permettent de recueillir et de combiner des renseignements, de créer et de modifier les totaux et de distribuer les valeurs actuelles et prévues. Les valeurs sont transférées au SPL à partir d’autres modules SAP et systèmes externes.

Les renseignements personnels contenus dans le SGI sont limités et comprennent le nom du fournisseur et du client, le numéro d’entreprise, l’adresse domiciliaire ou d’entreprise, les numéros de compte bancaire et d’autres renseignements connexes pour le traitement des transactions. L’information est recueillie directement de ces personnes ou grâce à des ententes contractuelles. Un employé peut être un vendeur ou un fournisseur pour le traitement des paiements ou des récupérations. Dans tous les cas, le consentement à la collecte, à l’utilisation, à la divulgation et à l’élimination de leurs renseignements personnels est implicite dans les ententes contractuelles lorsqu’on fait des affaires avec le Ministère. Pour les employés, cela est implicite lors de la présentation des demandes de remboursement de frais de déplacement.

Le MAECI est également enregistré dans les catégories révisées de documents ordinaires du SCT PRN 914 (gestion financière), PRN 912 (approvisionnement et passation de marchés), PRN 934 (voyages) et de fichiers de renseignements personnels ordinaires du SCT PSU 912 (marchés de services professionnels) et PSU 909 (voyages), qui sont également dans la liste d’Info Source du Secrétariat du Conseil du Trésor.

Il y a environ 1 650 utilisateurs du SGI à l’Administration centrale et dans les missions à l’étranger. Toutefois, seulement 180 utilisateurs peuvent créer et maintenir des données de base pour le fournisseur et le client. L’accès au système est octroyé selon le principe d’accès sélectif en fonction des tâches de l’employé. L’accès au SGI est contrôlé et restreint par l’intermédiaire des rôles du SGI, des comptes d’utilisateur, d’une forte protection par le mot de passe, d’un suivi permanent, de pistes de vérification et de la présentation de rapports d’accès à la direction. En outre, une évaluation de la menace et des risques, achevée en décembre 2006, n’a pas soulevé des préoccupations de sécurité au sein du SGI.

Des sauvegardes de tout le système et des bases de données sont effectuées quotidiennement, et les bandes de bases de données essentielles sont conservées sur le site, au même endroit que les serveurs, dans une chambre forte à l’épreuve du feu.

L’actuel calendrier de conservation du Ministère pour les renseignements financiers et relatifs à l’administration est de sept ans. Le SGI contient à la fois des données de base pour lesquelles il y a un usage continu et des données permanentes (transactionnelles) qui sont actuellement disponibles depuis la mise en œuvre du SGI en 1998. La raison d’être de la conservation des données au–delà de la période de conservation de sept ans du Ministère est qu’il n’y a pas de solution d’archivage facilement disponible dans l’empreinte du SAP du gouvernement du Canada. La stratégie du SGI consiste à suivre l’empreinte et à archiver les données une fois que la fonctionnalité deviendra disponible pour les ministères. En ce moment, même si l’archivage est sur la liste des éléments à traiter par le Groupe SAP, sa date de disponibilité demeure inconnue.

Les personnes concernées par les renseignements ont droit à la protection de leurs renseignements personnels et à leur accès en vertu de la *Loi sur la protection des renseignements personnels*, sous réserve de certaines exceptions et exemptions.

En ce moment, on ne prévoit pas effectuer une ÉFVP complète. L’ÉPFVP avait été effectuée avant tout pour satisfaire aux exigences en matière de politiques de l’ÉVP du SCT et de la GSTI. En outre, les constatations et observations découlant de l’achèvement de l’ÉPFVP ont permis de conclure que les renseignements personnels contenus dans la SGI sont considérés comme étant de risque faible et qu’il n’y a aucun problème relatif à la vie privée à régler ou qui justifie la nécessité d’une ÉFVP complète.

## Risques relatifs à la vie privée

Les risques relatifs à la vie privée suivants ont été identifiés dans l’élaboration de l’ÉPFVP et sont considérés comme étant de niveau faible :

### Collecte, utilisation et exactitude des renseignements personnels

Le risque relatif à la collecte et à l’utilisation des renseignements personnels inexacts est faible étant donné que les renseignements personnels sont recueillis directement du fournisseur/client et des employés. Les mises à jour/la maintenance en cours des fichiers principaux des fournisseurs et des clients en fonction des contrats, des factures et de la rétroaction des fournisseurs/clients/employés contribuent à atténuer ce risque.

Un fournisseur ou un client peut être un employé du MAECI. Pour s’assurer que les renseignements bancaires, l’adresse et le nom sont exacts, un chèque annulé est fourni pour vérifier l’exactitude.

### Divulgation inappropriée des renseignements personnels

Le risque de divulguer de manière inappropriée des renseignements personnels est faible. La gestion du contrôle et la limitation de l’accès de l’utilisateur par l’intermédiaire des comptes d’utilisateur, d’une forte protection par le mot de passe, d’un suivi permanent et de la présentation de rapports d’accès à la direction constitue la stratégie d’atténuation pour ce risque. De même, le SGI a des pistes de vérification pour s’assurer que les changements effectués par les utilisateurs aux registres des données permanentes ou aux transactions sont suivis de manière appropriée.
