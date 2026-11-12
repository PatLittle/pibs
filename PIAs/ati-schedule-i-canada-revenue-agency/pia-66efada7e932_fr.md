---
title: "Sommaire de l’évaluation des facteurs relatifs à la vie privée – infrastructure des données"
institution_id: "ati-schedule-i-canada-revenue-agency"
language: "fr"
source_url: "https://www.canada.ca/fr/agence-revenu/services/a-propos-agence-revenu-canada-arc/protection-vos-renseignements-personnels/evaluation-facteurs-relatifs-a-vie-privee/sommaire-evaluation-facteurs-relatifs-a-vie-privee-infrastructure-donnees.html"
retrieved_at_utc: "2026-11-12T05:49:14.116727+00:00"
http_status: 200
source_sha256: "d5945caea21a3b2290bb1798f8e4e010920df3ad79f41580fd69a27e60c48728"
content_kind: "page"
---

# Sommaire de l’évaluation des facteurs relatifs à la vie privée – infrastructure des données

### **Introduction**

Le présent document constitue un sommaire de l’évaluation des facteurs relatifs à la vie privée réalisée à l’égard de l’infrastructure des données, préparée par la Division de l’analyse et des solutions de données (DASD) de l’Agence du revenu du Canada (ARC). La DASD est responsable de développer et de tenir à jour les magasins de données et les environnements de données qui sont utilisés aux fins de recherche, d’analyse, de mesure du rendement, d’établissement de rapports et d’aide à la décision concernant les charges de travail du Recouvrement et de l’Observation à l’ARC. Cette ÉFVP a été entreprise en vue d’analyser les risques relatifs à la vie privée concernant les renseignements confidentiels sur les contribuables conservés et utilisés dans ces fonds de données et de faire état des mesures de sécurité en place pour atténuer ces risques.

### **Résumé**

Les objectifs de cette évaluation des facteurs relatifs à la vie privée (ÉFVP) sont d’analyser les environnements de données et les magasins de données des [niveaux de l’infrastructure des données exploratoires et de la recherche, de l’établissement de rapports et de l’analyse (RRA)] à la DASD, afin de déterminer les enjeux et les risques relatifs à la vie privée et de fournir un plan de gestion des risques relatifs à la vie privée en vue d’éliminer ou de réduire ces risques à un niveau acceptable.

L’initiative du Recouvrement intégré des recettes (RIR) a été établie afin de fournir des outils opérationnels techniques et spécialisés en vue d’appuyer la transformation des activités à l’ARC. Elle découle de plusieurs facteurs, y compris la Stratégie de l’ARC de 2010, la Stratégie de développement des marchés de l’ARC, la croissance continue du nombre de comptes débiteurs et d’inventaires vieillissants, les politiques et objectifs du gouvernement du Canada concernant le renouvellement des mécanismes de prestation de services existants afin de mieux servir les Canadiens, et les rapports de 1994 et de 2006 du Bureau du vérificateur général (BVG). En particulier, les recommandations suivantes du BVG ont entraîné le développement des niveaux spécialisés du magasin de données qui seront abordés dans la présente ÉFVP.

- L’Agence du revenu du Canada devrait déterminer les données dont elle a besoin pour analyser la composition de ses créances fiscales, les recueillir et élaborer de meilleures stratégies de recouvrement.

- L’Agence du revenu du Canada devrait améliorer considérablement sa gestion de l’information pour la rendre complète et exhaustive. Elle devrait mettre au point des techniques et des sources d’information fiables afin de déterminer régulièrement les résultats de ses efforts de recouvrement et fonder sur cette information les décisions qu’elle prend au sujet de chacun de ses principaux modes et de ses principales mesures de recouvrement.

- L’Agence du revenu du Canada devrait mettre sur pied un système automatisé de cotation du risque que présentent les créances fiscales plus exhaustif, mettre sans cesse à jour les cotes de risque et les utiliser pour établir l’ordre de priorité de la charge de travail dans tout le processus de recouvrement.

En vue de répondre aux objectifs et aux recommandations décrites ci-dessus, les magasins de données exploratoires et de RRA ont été développés et les données sélectionnées des contribuables y ont été entrées. Ces données proviennent des divers systèmes sources de l’ARC et ont été recueillies par l’Agence dans le cadre de l’administration et de l’exécution des programmes et des lois qui relèvent du mandat de l’ARC. Les renseignements concernent différents secteurs de recettes, y compris (sans toutefois s’y limiter) l’impôt sur le revenu des particuliers (T1), l’impôt sur le revenu des sociétés (T2), la TPS/TVH et les autres prélèvements, et sont utilisés à différentes fins selon le niveau.

**Le niveau exploratoire**

Les magasins de données au niveau exploratoire ne sont pas utilisés dans la production et ne seront pas utilisés pour prendre des décisions administratives au sujet des contribuables. Ces magasins sont utilisés afin de comprendre les données, de formuler des exigences en matière de données, d’appuyer les activités d’analyse des données, de mieux comprendre les métadonnées, de déterminer la valeur potentielle des données de systèmes sources et de mettre au point des modèles d’exploration de données. Le niveau exploratoire appuie l’évaluation de l’exactitude des données et l’élaboration d’un modèle opérationnel; il permet d’élaborer un prototype et une validation de principe et la mise à l’essai de nouveaux ensembles d’outils par les entreprises utilisatrices.

**Le niveau de la recherche, de l’établissement de rapports et de l’analyse (RRA)**

Les magasins de données au niveau de la RRA sont utilisés dans la production et peuvent être utilisés dans un processus administratif de prise de décision. Ce niveau est utilisé afin de permettre aux membres du personnel et à la direction de l’Administration centrale d’analyser les données en vue de découvrir de nouveaux faits et de nouvelles relations à l’appui des activités opérationnelles. Cela comprend la recherche sur la gestion des créances afin de comprendre la croissance de l’inventaire et la répartition des créances en souffrance, les demandes de renseignements ponctuelles, la détermination et l’analyse des tendances, l’examen de l’efficacité des stratégies et des mesures de recouvrement existantes, l’évaluation des programmes et l’analyse de leur rendement, la mise au point des modèles d’exploration de données prédictives et l’établissement des règles administratives.

### **Analyse des dix principes relatifs à la vie privée**

**Principe 1 : Responsabilité relative aux renseignements personnels**

L’ARC a désigné la Section de l’infrastructure des données (anciennement la SRID) afin d’assumer la responsabilité de la protection et du contrôle des renseignements personnels conservés et utilisés dans les magasins de données de la DASD. Ces magasins ont été développés conformément aux politiques de l’ARC en matière de gestion de l’information, de sécurité et de confidentialité, et aucun tiers ne participe avec les autres ministères ou le secteur privé.

**Principe 2 : Collecte des renseignements personnels**

Ces magasins de données contiennent une importante quantité de renseignements personnels sur les contribuables. Toutefois, aucun nouveau renseignement n’est recueilli. Toutes les données sont obtenues à titre de copies à partir des divers systèmes sources de l’ARC et ont été recueillies dans le cadre de l’administration et de l’exécution des lois et des programmes qui relèvent du mandat de l’ARC. La *Loi de l’impôt sur le revenu*, la *Loi sur la taxe d’accise* et la *Loi sur l’Agence du revenu du Canada* fournissent à l’ARC le pouvoir législatif nécessaire pour recueillir ces renseignements personnels et les utiliser à ces fins.

**Principe 3 : Consentement**

La DASD n’obtient aucun consentement auprès des contribuables. Les renseignements sont recueillis à partir des déclarations de revenus des particuliers, des demandes de prestations et de crédits et de divers autres formulaires remplis par les contribuables concernant les programmes administrés par l’ARC et hébergés dans les systèmes sources qui alimentent les données aux magasins de données de la DASD. Lorsque les contribuables fournissent ces renseignements à l’ARC, ils sont au courant que ces derniers seront utilisés aux fins d’administration et d’exécution des programmes et des lois qui relèvent de l’Agence et le consentement est donc implicite. De plus, la déclaration de revenus des particuliers (T1) et ses annexes contiennent un énoncé qui informe les contribuables que les renseignements recueillis seront conservés dans le fichier de renseignements personnels (FRP) ARC PPU 005; ce FRP peut être visualisé en ligne par le grand public et décrit les fins auxquelles les renseignements seront utilisés.

**Principe 4 : Utilisation des renseignements personnels**

La *Loi de l’impôt sur le revenu*, la *Loi sur la taxe d’accise*, la *Loi sur l’assurance-emploi* et d’autres lois du Parlement confèrent à l’Agence l’autorité législative d’utiliser ces renseignements personnels à ces fins. Tous les renseignements contenus dans ces magasins de données sont utilisés aux fins de l’administration et de l’exécution des programmes et des lois qui relèvent du mandat de l’ARC de façon conforme aux fins pour lesquelles ils ont été recueillis.

**Principe 5 : Divulgation et destruction des renseignements personnels**

Les renseignements personnels ne seront divulgués ni au public ni aux autres ministères; ils seront divulgués uniquement à l’échelle de l’Agence, aux fins décrites dans le résumé ci‑dessus. Les données au niveau de la RRA sont conservées conformément à la Politique sur la gestion de l’information de l’Agence. Les données au niveau exploratoire sont volatiles et ont une durée de vie limitée, ne sont pas utilisées pour prendre des décisions administratives au sujet des contribuables et ne sont donc pas conservées pendant la période minimale de deux ans. Des vérifications périodiques sont effectuées afin de déterminer les magasins de données qui ne sont plus utilisés et les propriétaires d’entreprise sont consultés afin de déterminer si un magasin de données n’est plus nécessaire et le moment où il ne l’est plus.

**Principe 6 : Exactitude des renseignements personnels**

Les données contenues au niveau de la RRA sont une copie des données de la production; un contrôle de la qualité est effectué par les propriétaires d’entreprise des systèmes sources qui ont saisi les renseignements au départ. Les données au niveau exploratoire ne sont pas mises à jour et ce niveau est conçu pour contenir des données temporaires. Lorsque des éléments de données provenant du niveau exploratoire sont utilisés pour valider des modèles d’exploration de données prédictifs, leur exactitude est d’abord vérifiée au moyen d’une comparaison avec les renseignements conservés dans le système source.

**Principe 7 : Protection des renseignements personnels**

L’environnement informatique de l’ARC fournit une sécurité suffisante pour les renseignements contenus dans les environnements de l’infrastructure des données. Des évaluations de la menace et des risques et des énoncés de sensibilité ont été réalisés et des procédures sont en place pour l’utilisation, la sécurité et la divulgation de renseignements personnels au sujet des postes de travail, des supports amovibles et des lecteurs locaux. Les droits d’accès sont fournis uniquement aux entreprises utilisatrices autorisées et aux travailleurs du domaine de la technologie de l’information dans le cas où ils doivent connaître les renseignements et tous les accès sont enregistrés par l’ID utilisateur. Les politiques en matière de sécurité et de confidentialité de l’ARC, qui décrivent en détail les lignes directrices et les exigences en matière de protection des renseignements personnels des contribuables contre la perte, le vol et la consultation, la divulgation, l’utilisation ou la modification non autorisées, seront respectées.

**Principe 8 : Transparence des renseignements**

La catégorie de documents ARC DGSC 550 a été créée et publiée en ligne sur *Info Source* et un fichier de renseignements personnels (FRP) a été rédigé (il sera probablement publié dans *Info Source* en 2013) et décrit les types de renseignements personnels contenus dans les magasins de données de la DASD, ainsi que les fins de recouvrement et les usages compatibles de ces renseignements. Cela fournit au grand public assez de renseignements pour qu’il comprenne clairement les fonctions de ce secteur de travail et la façon dont ils utilisent les renseignements personnels.

**Principe 9 : Accès des particuliers aux renseignements personnels**

La page [www.arc.gc.ca/aiprp](https://www.canada.ca/fr/agence-revenu/organisation/a-propos-agence-revenu-canada-arc/acces-a-information-protection-renseignements-personnels-a-agence-revenu-canada.html) du site Web de l’ARC fournit des renseignements visant à aider les contribuables à faire des demandes d’accès à l’information et à la protection des renseignements personnels (AIPRP), et une catégorie de documents, ainsi qu’un FRP seront accessibles en ligne dans *Info Source*. Ces ressources permettront aux membres du public de faire des demandes de renseignements éclairées au sujet de ces magasins de données.

**Principe 10 : Possibilité de porter plainte à l’égard du non-respect des principes**

Les procédures officielles relatives aux plaintes élaborées par la Direction de l’accès à l’information et de la protection des renseignements personnels seront traitées par les propriétaires d’entreprise du système source. Puisque les renseignements contenus dans les magasins de données de la DASD constituent une copie des données de production, toute question concernant l’exactitude des renseignements doit être traitée au niveau du système source, où les renseignements ont été recueillis ou créés.
