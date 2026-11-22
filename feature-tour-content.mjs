export const tourSections = {
  explorer: {
    path: "index.html",
    name: "Info Source Data Explorer",
    next: "my-info",
    en: [
      {
        title: "Find an institution",
        copy: "Search by institution name, then open a row to find its bilingual names, publication due date and original Info Source pages.",
        action: "Open Institutions", href: "table.html?dataset=institutions",
      },
      {
        title: "Read a Personal Information Bank",
        copy: "Search a PIB name or registration number. Open a record to see whose information it describes, why it is collected, how it is used and the published retention rules.",
        action: "Open PIBs", href: "table.html?dataset=pibs",
      },
      {
        title: "Browse Classes of Records",
        copy: "Look up an institution's program or activity to see the types of documents it publishes descriptions for. Open a row to read the bilingual entry.",
        action: "Open Classes of Records", href: "table.html?dataset=classes",
      },
      {
        title: "Trace a PIB to its related records",
        copy: "Find a PIB-to-class reference and check its resolution status. The linkage table shows which references match a published class and which still need review.",
        action: "Open PIB-to-class linkages", href: "table.html?dataset=links",
      },
      {
        title: "Look up a Standard PIB",
        copy: "Find government-wide Personal Information Banks used by multiple institutions. Search by bank number or name to see the published description.",
        action: "Open Standard PIBs", href: "table.html?dataset=standard-pibs",
      },
      {
        title: "Look up a Standard Class of Records",
        copy: "Search for a PRN or NDP code to identify the common administrative records covered by a standard class.",
        action: "Open Standard Classes", href: "table.html?dataset=standard-classes",
      },
      {
        title: "Browse personal information categories",
        copy: "Use the bilingual vocabulary to see examples of information types and compare the categories used to describe them.",
        action: "Open Categories", href: "table.html?dataset=categories",
      },
      {
        title: "Decode PIB types",
        copy: "Check the registration number series to distinguish public, particular, standard and legacy banks.",
        action: "Open PIB types", href: "table.html?dataset=pib-types",
      },
      {
        title: "Find privacy assessments",
        copy: "Search the assessment collection, open a result to review its details and follow the link to the source publication.",
        action: "Open Privacy Assessments", href: "privacy-assessments.html",
      },
      {
        title: "Follow relationships in the PI Network Explorer",
        copy: "Start from a PIB or privacy assessment, then select a connected node to see its details or make it the centre of the network.",
        action: "Open PI Network Explorer", href: "graph.html",
      },
      {
        title: "Link an Algorithmic Impact Assessment",
        copy: "Find an AIA to review its responsible senior official and any explicit references to privacy assessments or Personal Information Banks.",
        action: "Open Link AIA", href: "link-aia.html",
      },
      {
        title: "Trace a service to its Public Accounts codes",
        copy: "Find the 2025–2026 Chart of Accounts code reported for a service. Follow it to the core responsibility, accounting department or matching GC InfoBase records.",
        action: "See Public Accounts program codes", href: "#public-accounts-heading",
      },
      {
        title: "Inspect the network data model",
        copy: "See the kinds of records and relationships that make up the network, then inspect the fields available for each type.",
        action: "Open the data model", href: "data-model.html",
      },
      {
        title: "Compare the holdings published by institutions",
        copy: "Use the overview charts to see which institutions have the most published holdings and how institution-specific PIBs break down by type.",
        action: "See coverage and composition", href: "#insights-heading",
      },
      {
        title: "Check coverage and data quality",
        copy: "Read the bilingual coverage and linkage indicators, then check the collection audit before drawing conclusions from a gap.",
        action: "See data quality", href: "#quality-heading",
      },
      {
        title: "Compare My Info surveys",
        copy: "Open the survey comparison to see the available versions and choose the one you want to try.",
        action: "Compare surveys", href: "my_info_compare/",
      },
      {
        title: "Work with documents in Document Studio",
        copy: "Open or draft a bilingual document, inspect its structure and metadata, and preview it before exporting.",
        action: "Open Document Studio", href: "document-studio/",
      },
    ],
  },
  "my-info": {
    path: "my_info/",
    name: "My Info",
    next: "officials",
    en: [
      {
        title: "Answer a question about a federal program",
        copy: "Think about your own interactions with federal programs and use Continue to move through the survey. Your answers stay in this browser tab.",
        example: "Use Back to revise an answer or Clear answers to start over.",
        action: "Go to the survey", href: "#survey-card",
      },
      {
        title: "Try a fictional life story",
        copy: "Open Explore example life stories and results. Choose a persona and select Results to see a worked example with fictional answers.",
        example: "Each persona shows how a different set of interactions changes the estimate.",
        action: "Browse example stories", href: "#persona-examples",
      },
      {
        title: "Read the retention estimate",
        copy: "After completing the survey or opening a persona's results, check the retention group and expand the explanation on a result to see why the bank was matched.",
        example: "Likely still held means the approximate date is within the published retention period.",
        action: "Go to results or examples", href: "#results-region",
      },
      {
        title: "Follow a result to its source",
        copy: "Select a bank title to read its entry in the Data Explorer. You can also follow the categories and publication links to see what information the institution describes.",
        example: "Look for the bank number, information categories and source links on a result.",
        action: "Go to results or examples", href: "#results-region",
      },
    ],
    fr: [
      {
        title: "Répondez à une question sur un programme fédéral",
        copy: "Pensez à vos interactions avec les programmes fédéraux et sélectionnez Continuer pour avancer. Vos réponses restent dans cet onglet du navigateur.",
        example: "Utilisez Retour pour modifier une réponse ou Effacer les réponses pour recommencer.",
        action: "Aller au questionnaire", href: "#survey-card",
      },
      {
        title: "Explorez un parcours de vie fictif",
        copy: "Ouvrez la section des exemples de parcours de vie. Choisissez un profil, puis sélectionnez Résultats pour consulter un exemple basé sur des réponses fictives.",
        example: "Chaque profil montre comment différentes interactions modifient l’estimation.",
        action: "Parcourir les exemples", href: "#persona-examples",
      },
      {
        title: "Interprétez l’estimation de conservation",
        copy: "Après avoir rempli le questionnaire ou ouvert les résultats d’un profil, consultez l’état de conservation et développez l’explication pour voir pourquoi le fichier a été retenu.",
        example: "« Probablement encore conservés » signifie que la date approximative se situe dans la période de conservation publiée.",
        action: "Voir les résultats ou les exemples", href: "#results-region",
      },
      {
        title: "Remontez à la source d’un résultat",
        copy: "Sélectionnez le titre d’un fichier pour lire sa fiche dans l’explorateur. Consultez aussi les catégories et les liens de publication pour voir les renseignements que l’institution décrit.",
        example: "Repérez le numéro du fichier, les catégories de renseignements et les liens vers les sources.",
        action: "Voir les résultats ou les exemples", href: "#results-region",
      },
    ],
  },
  officials: {
    path: "gc_snr_officials/",
    name: "Senior Officials Transparency",
    next: "explorer",
    en: [
      {
        title: "See how public records connect",
        copy: "Open the identity-resolution diagram to see how a shared reference could help connect records across disclosure sources.",
        example: "Compare the records in the diagram with the appointment and disclosure sources listed below it.",
        action: "Go to the diagram", href: "#identity-diagram",
      },
      {
        title: "Search and filter candidate people",
        copy: "Search by name, role, title or institution. Use Source coverage and Consistency to narrow the list to the evidence you want to review.",
        example: "Choose Possible same-person matches from the Consistency filter to focus on linked name variants.",
        action: "Go to search", href: "#search",
      },
      {
        title: "Sort by observations or dates",
        copy: "Sort by observation count to find candidates with more source records, or use First observation and Last observation to compare the dates captured by the sources.",
        example: "Observation dates mark the earliest and latest evidence available for a candidate.",
        action: "Go to sorting", href: "#sortOrder",
      },
      {
        title: "Review a candidate and their source records",
        copy: "Select a name to compare original names, positions and institutions. Open a source link to check the evidence, or use Search Orders in Council to look for supporting orders.",
        example: "Identity likelihood is a review score. Check the source records before treating a suggested match as the same person.",
        action: "Go to candidate records", href: "#candidate-records",
      },
      {
        title: "Check source coverage and freshness",
        copy: "Review the Source coverage panel, then open About this explorer for refresh dates, source downloads and details on how observations and matching scores are calculated.",
        example: "The panel includes appointment, designated-role, travel, hospitality and lobbying communication sources.",
        action: "Go to Source coverage", href: "#source-coverage",
      },
    ],
  },
};

export const tourLabels = {
  en: {
    launch: "Try the tour",
    tours: "Feature tours",
    close: "Close tour",
    previous: "Previous card",
    next: "Next card",
    count: (step, total) => `Card ${step} of ${total}`,
    nextSection: name => `Next page tour: ${name}`,
    firstSection: name => `Return to the ${name} tour`,
  },
  fr: {
    launch: "Essayer la visite guidée",
    tours: "Visites guidées",
    close: "Fermer la visite",
    previous: "Carte précédente",
    next: "Carte suivante",
    count: (step, total) => `Carte ${step} sur ${total}`,
    nextSection: name => `Visite de la page suivante : ${name}`,
    firstSection: name => `Revenir à la visite de ${name}`,
  },
};
