"""Bilingual, source-linked examples for the My Info question gates.

These examples explain an interaction; they do not assert that a person appears
in a personal information bank.  ``pib_keys`` point to records in the repository
that support the example.  An empty key tuple marks a useful real-world example
for which the current local PIB inventory does not provide a direct record.

Keep this module separate from :mod:`my_info.interactions`: the survey can show
help progressively without making examples part of the matching rules.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InteractionExample:
    """One concrete activity and the federal organization involved."""

    institution_en: str
    institution_fr: str
    activity_en: str
    activity_fr: str
    pib_keys: tuple[str, ...]
    evidence_note_en: str = ""
    evidence_note_fr: str = ""


@dataclass(frozen=True)
class QuestionHelp:
    """Progressive help and routing guidance for a questionnaire gate."""

    familiarity: str
    examples: tuple[InteractionExample, ...]
    split_recommendation_en: str = ""
    split_recommendation_fr: str = ""


QUESTION_HELP: dict[str, QuestionHelp] = {
    "q_government_work": QuestionHelp(
        "mixed",
        (
            InteractionExample(
                "Public Service Commission of Canada",
                "Commission de la fonction publique du Canada",
                "Applying for a job in the federal public service",
                "Postuler à un emploi dans la fonction publique fédérale",
                ("PSU 911", "PSC PPU 040"),
            ),
            InteractionExample(
                "Treasury Board of Canada Secretariat or another federal employer",
                "Secrétariat du Conseil du Trésor du Canada ou un autre employeur fédéral",
                "Having an employee file, pay records, or leave records",
                "Avoir un dossier d'employé, un dossier de paie ou un dossier de congé",
                ("PSE 901", "PSE 903", "PSE 904"),
            ),
        ),
        "Split job applications from employment records; their dates and retention triggers differ.",
        "Séparer les demandes d'emploi des dossiers d'emploi; leurs dates et leurs déclencheurs de conservation diffèrent.",
    ),
    "q_money_programs": QuestionHelp(
        "mixed",
        (
            InteractionExample(
                "Employment and Social Development Canada / Service Canada",
                "Emploi et Développement social Canada / Service Canada",
                "Applying for Employment Insurance benefits",
                "Demander des prestations d'assurance-emploi",
                ("ESDC PPU 151",),
            ),
            InteractionExample(
                "Veterans Affairs Canada, with Service Canada",
                "Anciens Combattants Canada, avec Service Canada",
                "Applying for a veterans program or benefit through a Service Canada Centre",
                "Demander un programme ou une prestation pour vétérans dans un Centre Service Canada",
                ("ESDC PPU 701",),
            ),
        ),
        "Use named benefit families as child questions; 'other payment' is too broad to route reliably.",
        "Utiliser des familles de prestations nommées comme sous-questions; « autre paiement » est trop large pour orienter de façon fiable.",
    ),
    "q_tax_customs": QuestionHelp(
        "common",
        (
            InteractionExample(
                "Canada Revenue Agency",
                "Agence du revenu du Canada",
                "Filing a federal income tax return",
                "Produire une déclaration fédérale de revenus",
                (),
                "The activity is familiar, but the current local CRA extract has no direct tax-return PIB record.",
                "L'activité est familière, mais l'extrait local actuel de l'ARC ne contient pas de FRP direct sur les déclarations de revenus.",
            ),
            InteractionExample(
                "Canada Border Services Agency",
                "Agence des services frontaliers du Canada",
                "Declaring goods after returning to Canada",
                "Déclarer des marchandises au retour au Canada",
                ("CBSA PPU 018",),
            ),
        ),
        "Split taxes (CRA) from customs and duties (CBSA); a yes answer otherwise cannot identify the institution.",
        "Séparer les impôts (ARC) des douanes et droits (ASFC); une réponse affirmative ne permet sinon pas d'identifier l'institution.",
    ),
    "q_immigration": QuestionHelp(
        "mixed",
        (
            InteractionExample(
                "Immigration, Refugees and Citizenship Canada",
                "Immigration, Réfugiés et Citoyenneté Canada",
                "Applying for Canadian citizenship or a permanent resident card",
                "Demander la citoyenneté canadienne ou une carte de résident permanent",
                ("IRCC PPU 050", "IRCC PPU 067"),
            ),
            InteractionExample(
                "Immigration, Refugees and Citizenship Canada",
                "Immigration, Réfugiés et Citoyenneté Canada",
                "Applying for a visitor visa or visitor status",
                "Demander un visa de visiteur ou un statut de visiteur",
                ("IRCC PPU 055",),
            ),
        ),
        "Ask the process type next because citizenship, visitor, refugee, and permanent-residence records use different banks.",
        "Demander ensuite le type de processus, car les dossiers de citoyenneté, de visiteur, d'asile et de résidence permanente utilisent des FRP différents.",
    ),
    "q_travel_border": QuestionHelp(
        "common",
        (
            InteractionExample(
                "Immigration, Refugees and Citizenship Canada / Service Canada",
                "Immigration, Réfugiés et Citoyenneté Canada / Service Canada",
                "Applying for a Canadian passport",
                "Demander un passeport canadien",
                ("IRCC PPU 081", "ESDC PPU 708"),
            ),
            InteractionExample(
                "Canada Border Services Agency",
                "Agence des services frontaliers du Canada",
                "Crossing the border or applying for NEXUS",
                "Franchir la frontière ou demander l'adhésion à NEXUS",
                ("CBSA PPU 010", "CBSA PPU 031"),
            ),
        ),
        "International travel can imply a CBSA interaction, but passport and NEXUS applications should remain separate child routes.",
        "Un voyage international peut supposer une interaction avec l'ASFC, mais les demandes de passeport et de NEXUS devraient rester des parcours secondaires distincts.",
    ),
    "q_health_disability": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Employment and Social Development Canada / Service Canada",
                "Emploi et Développement social Canada / Service Canada",
                "Applying for the Canadian Dental Care Plan",
                "Demander le Régime canadien de soins dentaires",
                ("ESDC PPU 712",),
            ),
            InteractionExample(
                "Health Canada",
                "Santé Canada",
                "A health professional requesting special access to a medical device for a patient",
                "Un professionnel de la santé demandant l'accès spécial à un instrument médical pour un patient",
                ("HC PPU 430",),
            ),
        ),
        "Do not infer Health Canada from being a health professional or receiving ordinary provincial care; ask about a named federal program or report.",
        "Ne pas déduire Santé Canada du seul fait d'être un professionnel de la santé ou de recevoir des soins provinciaux ordinaires; demander plutôt un programme ou un signalement fédéral nommé.",
    ),
    "q_indigenous_services": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Indigenous Services Canada",
                "Services aux Autochtones Canada",
                "Receiving First Nations and Inuit home and community care",
                "Recevoir des soins à domicile et en milieu communautaire pour les Premières Nations et les Inuit",
                ("ISC PPU 019",),
            ),
            InteractionExample(
                "Indigenous Services Canada",
                "Services aux Autochtones Canada",
                "Applying for registration under the Indian Act or updating an Indian status record",
                "Demander l'inscription en vertu de la Loi sur les Indiens ou mettre à jour un dossier de statut d'Indien",
                ("ISC PPU 110",),
            ),
        ),
    ),
    "q_military_veterans": QuestionHelp(
        "mixed",
        (
            InteractionExample(
                "Department of National Defence / Canadian Armed Forces",
                "Ministère de la Défense nationale / Forces armées canadiennes",
                "Applying to join or serving in the Canadian Armed Forces",
                "Demander à s'enrôler ou servir dans les Forces armées canadiennes",
                ("DND PPU 025", "DND PPE 818"),
            ),
            InteractionExample(
                "Veterans Affairs Canada",
                "Anciens Combattants Canada",
                "Applying for a veterans program or benefit",
                "Demander un programme ou une prestation pour vétérans",
                ("ESDC PPU 701",),
            ),
        ),
        "Split military service (DND/CAF) from veterans services (VAC); both may be true and usually have different dates.",
        "Séparer le service militaire (MDN/FAC) des services aux vétérans (ACC); les deux peuvent être vrais et ont habituellement des dates différentes.",
    ),
    "q_education_training": QuestionHelp(
        "mixed",
        (
            InteractionExample(
                "Employment and Social Development Canada / Service Canada",
                "Emploi et Développement social Canada / Service Canada",
                "Receiving a Canada Student Grant or Canada Student Loan",
                "Recevoir une bourse ou un prêt d'études canadien",
                ("ESDC PPU 030",),
            ),
            InteractionExample(
                "Employment and Social Development Canada / Service Canada",
                "Emploi et Développement social Canada / Service Canada",
                "Receiving a Canada Apprentice Loan for Red Seal technical training",
                "Recevoir un prêt canadien aux apprentis pour une formation technique Sceau rouge",
                ("ESDC PPU 709",),
            ),
        ),
    ),
    "q_justice_safety": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Royal Canadian Mounted Police",
                "Gendarmerie royale du Canada",
                "Completing a security or reliability screening for work or a contract",
                "Faire l'objet d'un filtrage de sécurité ou de fiabilité pour un emploi ou un contrat",
                ("RCMP PPU 065", "PSU 917"),
            ),
            InteractionExample(
                "Correctional Service Canada",
                "Service correctionnel du Canada",
                "Being admitted to or released from a federal correctional institution",
                "Être admis dans un établissement correctionnel fédéral ou en être libéré",
                ("CSC PPU 025",),
            ),
        ),
        "Security screening, police matters, and corrections should be separate child routes because they involve different institutions and highly different contexts.",
        "Le filtrage de sécurité, les affaires policières et les services correctionnels devraient être des parcours secondaires distincts, car ils concernent des institutions et des contextes très différents.",
    ),
    "q_complaint_appeal": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Canadian Transportation Agency",
                "Office des transports du Canada",
                "Submitting a complaint about air travel",
                "Présenter une plainte concernant le transport aérien",
                ("CTA PPU 014",),
            ),
            InteractionExample(
                "Canada Border Services Agency",
                "Agence des services frontaliers du Canada",
                "Submitting a complaint or asking CBSA to review a decision",
                "Présenter une plainte ou demander à l'ASFC de réviser une décision",
                ("CBSA PPU 003", "CBSA PPU 005"),
            ),
        ),
    ),
    "q_access_privacy": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Treasury Board of Canada Secretariat",
                "Secrétariat du Conseil du Trésor du Canada",
                "Using the ATIP Online service to request government records or your personal information",
                "Utiliser le service d'AIPRP en ligne pour demander des documents gouvernementaux ou vos renseignements personnels",
                ("TBS PCE 805", "PSU 901"),
            ),
            InteractionExample(
                "Veterans Affairs Canada or another federal institution that holds the record",
                "Anciens Combattants Canada ou une autre institution fédérale qui détient le document",
                "Asking an institution to correct personal information in its files under the Privacy Act",
                "Demander à une institution de corriger des renseignements personnels dans ses dossiers en vertu de la Loi sur la protection des renseignements personnels",
                ("PSU 901",),
            ),
        ),
    ),
    "q_business_supplier": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Public Services and Procurement Canada or another contracting department",
                "Services publics et Approvisionnement Canada ou un autre ministère contractant",
                "Bidding on or performing a federal professional-services contract",
                "Soumissionner ou exécuter un marché fédéral de services professionnels",
                ("PSU 912",),
            ),
            InteractionExample(
                "Transport Canada",
                "Transports Canada",
                "Getting a Pleasure Craft Operator Card or licensing a pleasure craft",
                "Obtenir une carte de conducteur d'embarcation de plaisance ou un permis d'embarcation de plaisance",
                ("TC PPU 023", "TC PPU 044"),
            ),
            InteractionExample(
                "Royal Canadian Mounted Police",
                "Gendarmerie royale du Canada",
                "Applying for or renewing a firearms licence",
                "Demander ou renouveler un permis d'armes à feu",
                ("RCMP PPU 007", "RCMP PPU 100"),
            ),
        ),
        "Replace the broad business gate with named child routes. Firearms licensing, a boating card, and a vessel licence must not be treated as the same generic permit.",
        "Remplacer la vaste question sur les entreprises par des parcours secondaires nommés. Le permis d'armes à feu, la carte de conducteur d'embarcation et le permis de bâtiment ne doivent pas être traités comme un même permis générique.",
    ),
    "q_housing_property": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Indigenous Services Canada",
                "Services aux Autochtones Canada",
                "Using the On-Reserve Housing Program ministerial loan guarantee",
                "Utiliser la garantie d'emprunt ministérielle du Programme de logement dans les réserves",
                ("ISC PPU 011",),
            ),
            InteractionExample(
                "Department of National Defence / Canadian Armed Forces",
                "Ministère de la Défense nationale / Forces armées canadiennes",
                "Living in or applying for Canadian Forces housing",
                "Habiter dans un logement des Forces canadiennes ou en faire la demande",
                ("DND PPU 885",),
            ),
        ),
        "Ask about named federal programs; buying a home or having a mortgage alone does not establish a direct federal PIB interaction.",
        "Demander des programmes fédéraux nommés; l'achat d'une maison ou le simple fait d'avoir une hypothèque n'établit pas à lui seul une interaction directe avec un FRP fédéral.",
    ),
    "q_civic_contact": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Elections Canada",
                "Élections Canada",
                "Registering to vote or applying to vote by mail in a federal election",
                "S'inscrire pour voter ou demander de voter par la poste à une élection fédérale",
                (),
                "The example is a real federal interaction, but no Elections Canada record appears in the current local PIB extract.",
                "L'exemple est une interaction fédérale réelle, mais aucun dossier d'Élections Canada ne figure dans l'extrait local actuel des FRP.",
            ),
            InteractionExample(
                "Health Canada",
                "Santé Canada",
                "Taking part in a consultation on health-protection legislation",
                "Participer à une consultation sur une loi de protection de la santé",
                ("HC PPU 051",),
            ),
        ),
        "Split voting, petitions, direct correspondence, and consultations; they are not interchangeable and often route to different standard or institution-specific banks.",
        "Séparer le vote, les pétitions, la correspondance directe et les consultations; ces interactions ne sont pas interchangeables et mènent souvent à différents FRP ordinaires ou propres à une institution.",
    ),
    "q_culture_volunteer": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Canadian Heritage",
                "Patrimoine canadien",
                "Entering the Canada Day Challenge",
                "Participer au Défi de la fête du Canada",
                ("PCH PPU 027",),
            ),
            InteractionExample(
                "Canadian Heritage",
                "Patrimoine canadien",
                "Registering with a federally run volunteer program",
                "S'inscrire à un programme fédéral de bénévolat",
                ("PCH PPU 070",),
            ),
        ),
        "Prefer named programs. Simply visiting a park or museum does not necessarily create an identifiable personal record.",
        "Privilégier les programmes nommés. La simple visite d'un parc ou d'un musée ne crée pas nécessairement un dossier personnel identifiable.",
    ),
    "q_research_survey": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Health Canada",
                "Santé Canada",
                "Taking part in a study about pesticide exposure, air pollution, or another health risk",
                "Participer à une étude sur l'exposition aux pesticides, la pollution de l'air ou un autre risque pour la santé",
                ("HC PPU 035", "HC PPU 314"),
            ),
            InteractionExample(
                "Public Health Agency of Canada",
                "Agence de la santé publique du Canada",
                "Leading, reviewing, or supporting a PHAC research project",
                "Diriger, évaluer ou appuyer un projet de recherche de l'ASPC",
                ("PHAC PPU 290",),
            ),
        ),
        "Separate survey respondent or study participant from researcher or peer reviewer; the bank and information collected differ.",
        "Séparer le répondant à un sondage ou le participant à une étude du chercheur ou de l'évaluateur par les pairs; le FRP et les renseignements recueillis diffèrent.",
    ),
    "q_emergency": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Department of National Defence / Canadian Armed Forces",
                "Ministère de la Défense nationale / Forces armées canadiennes",
                "Receiving help in a search-and-rescue incident",
                "Recevoir de l'aide lors d'une opération de recherche et sauvetage",
                ("DND PPU 050",),
            ),
            InteractionExample(
                "Fisheries and Oceans Canada",
                "Pêches et Océans Canada",
                "Applying for temporary financial help after severe ice conditions affected a fishery",
                "Demander une aide financière temporaire après que de graves conditions de glace ont touché une pêche",
                ("DFO PPU 045",),
            ),
        ),
        "Ask which federal service responded; many emergency services are provincial, territorial, municipal, or delivered through another organization.",
        "Demander quel service fédéral est intervenu; de nombreux services d'urgence sont provinciaux, territoriaux, municipaux ou fournis par un autre organisme.",
    ),
    "q_family_vital": QuestionHelp(
        "unfamiliar",
        (
            InteractionExample(
                "Employment and Social Development Canada / Service Canada",
                "Emploi et Développement social Canada / Service Canada",
                "Applying for a Canada Pension Plan survivor or death benefit",
                "Demander une prestation de survivant ou de décès du Régime de pensions du Canada",
                ("ESDC PPU 146",),
            ),
            InteractionExample(
                "Indigenous Services Canada",
                "Services aux Autochtones Canada",
                "Having a First Nations estate administered by the department",
                "Faire administrer une succession des Premières Nations par le ministère",
                ("ISC PPU 105",),
            ),
        ),
        "Replace the broad life-event wording with named federal services. Birth, marriage, and death registration are ordinarily provincial or territorial activities.",
        "Remplacer le libellé général sur les événements de la vie par des services fédéraux nommés. L'enregistrement des naissances, mariages et décès relève habituellement des provinces ou des territoires.",
    ),
}


def help_for_question(question_code: str) -> QuestionHelp:
    """Return progressive help for a known question code."""

    return QUESTION_HELP[question_code]
