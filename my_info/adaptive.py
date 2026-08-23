"""Curated adaptive routes for compound My Info questionnaire gates.

The top-level taxonomy intentionally favours recall.  These routes provide the
smallest useful follow-up for interactions whose institution or PIB family can
be inferred from a concrete activity.  Selectors are deliberately explicit and
reviewable: no route relies on opaque similarity scoring.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


ADAPTIVE_ROUTE_VERSION = "2.0"


def _option(
    code: str,
    label_en: str,
    label_fr: str,
    institution_en: str,
    institution_fr: str,
    *,
    bank_numbers: tuple[str, ...] = (),
    coverage: str = "direct",
    fallback_to_parent: bool = False,
) -> dict[str, Any]:
    return {
        "code": code,
        "label_en": label_en,
        "label_fr": label_fr,
        "institution_en": institution_en,
        "institution_fr": institution_fr,
        "coverage": coverage,
        "ask_timing": True,
        "selectors": {"bank_numbers": list(bank_numbers)},
        "fallback_to_parent": fallback_to_parent,
    }


_ROUTES: tuple[dict[str, Any], ...] = (
    {
        "parent_question_code": "q_government_work",
        "prompt_en": "Which federal work situations apply to you? Select all that apply.",
        "prompt_fr": "Quelles situations de travail fédéral s'appliquent à vous? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "federal_job_application",
                "I applied for a federal job",
                "J'ai postulé à un emploi fédéral",
                "Public Service Commission of Canada or the hiring department",
                "Commission de la fonction publique du Canada ou ministère d'embauche",
                bank_numbers=("PSU 911", "PSE 902", "PSC PPU 040", "PSC PCU 025"),
            ),
            _option(
                "federal_employee",
                "I worked for the federal government",
                "J'ai travaillé pour le gouvernement fédéral",
                "The person's federal employer and central personnel systems",
                "Employeur fédéral de la personne et systèmes centraux de personnel",
                bank_numbers=(
                    "PSE 901", "PSE 903", "PSE 904", "PSE 906", "PSE 907",
                    "PSE 911", "PSE 912", "PSE 914", "PSE 918", "PSE 919",
                    "PSE 920",
                ),
            ),
            _option(
                "other_federal_work_service",
                "Another federal work-related service",
                "Un autre service lié au travail fédéral",
                "Government of Canada institution involved",
                "Institution du gouvernement du Canada concernée",
                coverage="fallback",
                fallback_to_parent=True,
            ),
        ),
    },
    {
        "parent_question_code": "q_money_programs",
        "prompt_en": "What kind of federal payment or support was it? Select all that apply.",
        "prompt_fr": "Quel type de paiement ou de soutien fédéral était-ce? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "employment_pay_reimbursement",
                "Federal employee pay, benefits or reimbursement",
                "Paie, avantages sociaux ou remboursement d'un employé fédéral",
                "The person's federal employer and Treasury Board systems",
                "Employeur fédéral de la personne et systèmes du Conseil du Trésor",
                bank_numbers=("PSU 931", "PSE 904"),
            ),
            _option(
                "employment_insurance",
                "Employment Insurance",
                "Assurance-emploi",
                "Employment and Social Development Canada / Service Canada",
                "Emploi et Développement social Canada / Service Canada",
                bank_numbers=("ESDC PPU 151", "ESDC PPU 180", "ESDC PPU 501"),
            ),
            _option(
                "cpp_oas",
                "Canada Pension Plan or Old Age Security",
                "Régime de pensions du Canada ou Sécurité de la vieillesse",
                "Employment and Social Development Canada / Service Canada",
                "Emploi et Développement social Canada / Service Canada",
                bank_numbers=("ESDC PPU 140", "ESDC PPU 146"),
            ),
            _option(
                "veterans_payment",
                "A veterans benefit or payment",
                "Une prestation ou un paiement pour vétérans",
                "Veterans Affairs Canada, sometimes delivered with Service Canada",
                "Anciens Combattants Canada, parfois avec Service Canada",
                bank_numbers=("VAC PPU 040", "VAC PPU 200", "VAC PPU 710", "VAC PPU 715", "ACC PPU 350", "ESDC PPU 701"),
            ),
            _option(
                "other_payment_program",
                "Another grant, loan, benefit or payment",
                "Une autre subvention, un autre prêt, une autre prestation ou un autre paiement",
                "Federal institution that ran the program",
                "Institution fédérale responsable du programme",
                coverage="fallback",
                fallback_to_parent=True,
            ),
        ),
    },
    {
        "parent_question_code": "q_tax_customs",
        "prompt_en": "Which of these have you done? Select all that apply.",
        "prompt_fr": "Qu'avez-vous fait parmi les choix suivants? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "federal_tax_return",
                "Filed a federal income tax return",
                "Produit une déclaration fédérale de revenus",
                "Canada Revenue Agency",
                "Agence du revenu du Canada",
                coverage="inventory_gap",
            ),
            _option(
                "customs_declaration",
                "Declared goods or paid duties at the border",
                "Déclaré des marchandises ou payé des droits à la frontière",
                "Canada Border Services Agency",
                "Agence des services frontaliers du Canada",
                bank_numbers=("CBSA PPU 018",),
            ),
            _option(
                "other_tax_customs",
                "Another federal tax or customs interaction",
                "Une autre interaction fédérale liée aux impôts ou aux douanes",
                "Canada Revenue Agency or Canada Border Services Agency",
                "Agence du revenu du Canada ou Agence des services frontaliers du Canada",
                coverage="fallback",
                fallback_to_parent=True,
            ),
        ),
    },
    {
        "parent_question_code": "q_travel_border",
        "prompt_en": "Which travel or border interactions apply? Select all that apply.",
        "prompt_fr": "Quelles interactions de voyage ou à la frontière s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "passport_application",
                "Applied for a Canadian passport",
                "Demandé un passeport canadien",
                "Immigration, Refugees and Citizenship Canada / Service Canada",
                "Immigration, Réfugiés et Citoyenneté Canada / Service Canada",
                bank_numbers=("IRCC PPU 081", "ESDC PPU 708"),
            ),
            _option(
                "border_crossing",
                "Crossed Canada's international border",
                "Franchi la frontière internationale du Canada",
                "Canada Border Services Agency",
                "Agence des services frontaliers du Canada",
                bank_numbers=("CBSA PPU 008", "CBSA PPU 010", "CBSA PPU 014", "CBSA PPU 018"),
            ),
            _option(
                "trusted_traveller",
                "Applied for or used NEXUS or another trusted-traveller program",
                "Demandé ou utilisé NEXUS ou un autre programme de voyageurs dignes de confiance",
                "Canada Border Services Agency",
                "Agence des services frontaliers du Canada",
                bank_numbers=("CBSA PPU 013", "CBSA PPU 031"),
            ),
            _option(
                "other_travel_border",
                "Another federal travel or border interaction",
                "Une autre interaction fédérale liée au voyage ou à la frontière",
                "Federal institution involved",
                "Institution fédérale concernée",
                coverage="fallback",
                fallback_to_parent=True,
            ),
        ),
    },
    {
        "parent_question_code": "q_military_veterans",
        "prompt_en": "Which military or veterans situations apply? Select all that apply.",
        "prompt_fr": "Quelles situations militaires ou liées aux vétérans s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "caf_service",
                "Applied to join or served in the Canadian Armed Forces",
                "Demandé à m'enrôler ou servi dans les Forces armées canadiennes",
                "Department of National Defence / Canadian Armed Forces and Library and Archives Canada",
                "Ministère de la Défense nationale / Forces armées canadiennes et Bibliothèque et Archives Canada",
                bank_numbers=("DND PPU 025", "DND PPE 818", "LAC PPU 024"),
            ),
            _option(
                "veterans_program",
                "Applied for or used a veterans program",
                "Demandé ou utilisé un programme pour vétérans",
                "Veterans Affairs Canada, sometimes delivered with Service Canada",
                "Anciens Combattants Canada, parfois avec Service Canada",
                bank_numbers=("VAC PPU 040", "VAC PPU 200", "VAC PPU 710", "VAC PPU 715", "ACC PPU 350", "ESDC PPU 701"),
            ),
            _option(
                "other_military_veterans",
                "Another military or veterans interaction",
                "Une autre interaction militaire ou liée aux vétérans",
                "National Defence or Veterans Affairs Canada",
                "Défense nationale ou Anciens Combattants Canada",
                coverage="fallback",
                fallback_to_parent=True,
            ),
        ),
    },
    {
        "parent_question_code": "q_justice_safety",
        "prompt_en": "What kind of federal public-safety interaction was it? Select all that apply.",
        "prompt_fr": "Quel type d'interaction fédérale en matière de sécurité publique était-ce? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "security_screening",
                "A job, airport, port or government security screening",
                "Un filtrage de sécurité pour un emploi, un aéroport, un port ou le gouvernement",
                "The screening institution, such as Transport Canada or a federal employer",
                "Institution responsable, comme Transports Canada ou un employeur fédéral",
                bank_numbers=("PSU 917", "DND PPU 834", "RCMP PPU 065", "TC PPU 093"),
            ),
            _option(
                "police_law_enforcement",
                "A federal police or law-enforcement matter",
                "Une affaire de police fédérale ou d'application de la loi",
                "Royal Canadian Mounted Police or another federal enforcement institution",
                "Gendarmerie royale du Canada ou autre institution fédérale d'application de la loi",
                bank_numbers=(
                    "RCMP PPU 005", "RCMP PPU 010", "RCMP PPU 015", "RCMP PPU 025",
                    "RCMP PPU 030", "RCMP PPU 075", "RCMP PPU 095", "RCMP PPU 139",
                    "RCMP PPU 202", "RCMP PPU 203",
                ),
                coverage="partial",
            ),
            _option(
                "corrections_parole",
                "A federal corrections, parole or record-suspension matter",
                "Une affaire fédérale de services correctionnels, de libération conditionnelle ou de suspension du casier",
                "Correctional Service Canada or Parole Board of Canada",
                "Service correctionnel Canada ou Commission des libérations conditionnelles du Canada",
                bank_numbers=(
                    "CSC PPU 025", "CSC PPU 030", "CSC PPU 035", "CSC PPU 040",
                    "CSC PPU 042", "CSC PPU 045", "CSC PPU 060", "CSC PPU 065",
                    "CSC PPU 070", "CSC PPU 075", "CSC PPU 080", "CSC PPU 082",
                    "CSC PPU 110", "CSC PPU 115", "CSC PPU 125", "CSC PPU 135",
                    "PBC PPU 005", "PBC PPU 010", "PBC PPU 015",
                ),
            ),
            _option(
                "other_justice_safety",
                "Another federal law-enforcement or public-safety matter",
                "Une autre affaire fédérale d'application de la loi ou de sécurité publique",
                "Federal institution involved",
                "Institution fédérale concernée",
                coverage="fallback",
                fallback_to_parent=True,
            ),
        ),
    },
    {
        "parent_question_code": "q_business_supplier",
        "prompt_en": "Which business, licence or permit interactions apply? Select all that apply.",
        "prompt_fr": "Quelles interactions liées aux entreprises, licences ou permis s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "federal_contract",
                "Bid on or held a federal government contract",
                "Soumissionné ou détenu un marché du gouvernement fédéral",
                "The contracting department and Public Services and Procurement Canada",
                "Ministère contractant et Services publics et Approvisionnement Canada",
                bank_numbers=("PSU 912",),
                coverage="partial",
            ),
            _option(
                "aviation_licence_clearance",
                "Held a federal aviation licence, medical certificate or airport clearance",
                "Détenu une licence d'aviation, un certificat médical ou une habilitation aéroportuaire fédérale",
                "Transport Canada",
                "Transports Canada",
                bank_numbers=("TC PPU 005", "TC PPU 011", "TC PPU 020", "TC PPU 031", "TC PPU 085", "TC PPU 093"),
            ),
            _option(
                "other_business_regulatory",
                "Another federal business, licence, inspection or permit interaction",
                "Une autre interaction fédérale liée à une entreprise, une licence, une inspection ou un permis",
                "Federal regulator or institution involved",
                "Organisme de réglementation ou institution fédérale concernée",
                coverage="fallback",
                fallback_to_parent=True,
            ),
        ),
    },
    {
        "parent_question_code": "q_firearms",
        "prompt_en": "Which firearms-program interactions apply? Select all that apply.",
        "prompt_fr": "Quelles interactions avec le programme des armes à feu s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "firearms_licence",
                "Applied for, renewed or held a firearms licence",
                "Demandé, renouvelé ou détenu un permis d'armes à feu",
                "Royal Canadian Mounted Police / Canadian Firearms Program",
                "Gendarmerie royale du Canada / Programme canadien des armes à feu",
                bank_numbers=("RCMP PPU 007", "RCMP PPU 037", "RCMP PPU 100"),
            ),
            _option(
                "restricted_firearm_registration",
                "Registered a restricted or prohibited firearm",
                "Enregistré une arme à feu à autorisation restreinte ou prohibée",
                "Royal Canadian Mounted Police / Canadian Firearms Program",
                "Gendarmerie royale du Canada / Programme canadien des armes à feu",
                bank_numbers=("RCMP PPU 037", "RCMP PPU 100", "RCMP PPU 101"),
            ),
            _option(
                "other_firearms_program",
                "Another Canadian Firearms Program interaction",
                "Une autre interaction avec le Programme canadien des armes à feu",
                "Royal Canadian Mounted Police",
                "Gendarmerie royale du Canada",
                coverage="fallback",
                bank_numbers=("RCMP PPU 007", "RCMP PPU 037", "RCMP PPU 100", "RCMP PPU 101"),
            ),
        ),
    },
    {
        "parent_question_code": "q_boating",
        "prompt_en": "Which federal boating interactions apply? Select all that apply.",
        "prompt_fr": "Quelles interactions fédérales liées à la navigation s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option(
                "pleasure_craft_operator_card",
                "Got a Pleasure Craft Operator Card",
                "Obtenu une carte de conducteur d'embarcation de plaisance",
                "Transport Canada",
                "Transports Canada",
                bank_numbers=("TC PPU 023",),
            ),
            _option(
                "pleasure_craft_licence",
                "Licensed a pleasure craft",
                "Obtenu un permis d'embarcation de plaisance",
                "Transport Canada",
                "Transports Canada",
                bank_numbers=("TC PPU 044",),
            ),
            _option(
                "vessel_registration",
                "Registered a vessel with Transport Canada",
                "Immatriculé un bâtiment auprès de Transports Canada",
                "Transport Canada",
                "Transports Canada",
                bank_numbers=("TC PPU 041",),
            ),
            _option(
                "professional_seafarer",
                "Got a federal seafarer certificate or identity document",
                "Obtenu un brevet ou une pièce d'identité fédérale de marin",
                "Transport Canada",
                "Transports Canada",
                bank_numbers=("TC PPU 030", "TC PPU 040"),
            ),
            _option(
                "other_federal_boating",
                "Another Transport Canada boating interaction",
                "Une autre interaction nautique avec Transports Canada",
                "Transport Canada",
                "Transports Canada",
                bank_numbers=("TC PPU 021", "TC PPU 023", "TC PPU 041", "TC PPU 044", "TC PPU 048"),
                coverage="partial",
            ),
        ),
    },
)


_BETA_ROUTES: tuple[dict[str, Any], ...] = (
    {
        "parent_question_code": "q_immigration",
        "prompt_en": "Which immigration or citizenship processes apply? Select all that apply.",
        "prompt_fr": "Quelles démarches d'immigration ou de citoyenneté s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("citizenship_permanent_resident", "Canadian citizenship or a permanent resident card", "Citoyenneté canadienne ou carte de résident permanent", "Immigration, Refugees and Citizenship Canada", "Immigration, Réfugiés et Citoyenneté Canada", bank_numbers=("IRCC PPU 050", "IRCC PPU 067")),
            _option("visitor_visa_status", "A visitor visa or visitor status", "Visa de visiteur ou statut de visiteur", "Immigration, Refugees and Citizenship Canada", "Immigration, Réfugiés et Citoyenneté Canada", bank_numbers=("IRCC PPU 055",)),
            _option("other_immigration_process", "Another immigration, refugee or citizenship process", "Une autre démarche d'immigration, de réfugié ou de citoyenneté", "Immigration, Refugees and Citizenship Canada", "Immigration, Réfugiés et Citoyenneté Canada", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_health_disability",
        "prompt_en": "Which federal health or disability services apply? Select all that apply.",
        "prompt_fr": "Quels services fédéraux de santé ou d'invalidité s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("canadian_dental_care_plan", "The Canadian Dental Care Plan", "Régime canadien de soins dentaires", "Employment and Social Development Canada / Service Canada", "Emploi et Développement social Canada / Service Canada", bank_numbers=("ESDC PPU 712",)),
            _option("medical_device_special_access", "Special access to a medical device", "Accès spécial à un instrument médical", "Health Canada", "Santé Canada", bank_numbers=("HC PPU 430",)),
            _option("other_federal_health_support", "Another named federal health, rehabilitation or disability service", "Un autre service fédéral nommé de santé, de réadaptation ou d'invalidité", "Federal institution that ran the service", "Institution fédérale responsable du service", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_indigenous_services",
        "prompt_en": "Which federal Indigenous services apply? Select all that apply.",
        "prompt_fr": "Quels services fédéraux aux Autochtones s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("first_nations_home_care", "First Nations and Inuit home or community care", "Soins à domicile ou communautaires pour les Premières Nations et les Inuit", "Indigenous Services Canada", "Services aux Autochtones Canada", bank_numbers=("ISC PPU 019",)),
            _option("indian_status_registration", "Registration under the Indian Act or an Indian status record update", "Inscription en vertu de la Loi sur les Indiens ou mise à jour d'un dossier de statut d'Indien", "Indigenous Services Canada", "Services aux Autochtones Canada", bank_numbers=("ISC PPU 110",)),
            _option("other_indigenous_service", "Another federal First Nations, Inuit or Métis service", "Un autre service fédéral destiné aux Premières Nations, aux Inuit ou aux Métis", "Federal institution that ran the service", "Institution fédérale responsable du service", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_education_training",
        "prompt_en": "Which federal education or training support applies? Select all that apply.",
        "prompt_fr": "Quel soutien fédéral aux études ou à la formation s'applique? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("canada_student_aid", "A Canada Student Grant or Canada Student Loan", "Bourse canadienne pour étudiants ou prêt d'études canadien", "Employment and Social Development Canada / Service Canada", "Emploi et Développement social Canada / Service Canada", bank_numbers=("ESDC PPU 030",)),
            _option("canada_apprentice_loan", "A Canada Apprentice Loan", "Prêt canadien aux apprentis", "Employment and Social Development Canada / Service Canada", "Emploi et Développement social Canada / Service Canada", bank_numbers=("ESDC PPU 709",)),
            _option("other_education_training", "Another federal scholarship, training or education program", "Un autre programme fédéral de bourse, de formation ou d'études", "Federal institution that ran the program", "Institution fédérale responsable du programme", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_complaint_appeal",
        "prompt_en": "Which federal complaint or review applies? Select all that apply.",
        "prompt_fr": "Quelle plainte ou révision fédérale s'applique? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("air_travel_complaint", "An air-travel complaint", "Plainte concernant le transport aérien", "Canadian Transportation Agency", "Office des transports du Canada", bank_numbers=("CTA PPU 014",)),
            _option("cbsa_complaint_review", "A CBSA complaint or request to review a decision", "Plainte à l'ASFC ou demande de révision d'une décision", "Canada Border Services Agency", "Agence des services frontaliers du Canada", bank_numbers=("CBSA PPU 003", "CBSA PPU 005")),
            _option("other_complaint_appeal", "Another federal complaint, grievance or appeal", "Une autre plainte, un autre grief ou un autre appel fédéral", "Federal institution or tribunal involved", "Institution ou tribunal fédéral concerné", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_access_privacy",
        "prompt_en": "What did you ask a federal office to do? Select all that apply.",
        "prompt_fr": "Qu'avez-vous demandé à un bureau fédéral de faire? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("access_information_request", "Give me government records or my personal information", "Me donner des documents gouvernementaux ou mes renseignements personnels", "The federal institution involved, including requests sent through the ATIP Online service", "Institution fédérale concernée, y compris les demandes envoyées par le service AIPRP en ligne", bank_numbers=("TBS PCE 805", "PSU 901")),
            _option("personal_information_correction", "Correct personal information in a federal file", "Corriger des renseignements personnels dans un dossier fédéral", "The federal institution that holds the record", "Institution fédérale qui détient le dossier", bank_numbers=("PSU 901",)),
            _option("other_access_privacy", "Another access or privacy request", "Une autre demande d'accès ou de protection des renseignements personnels", "Federal institution involved", "Institution fédérale concernée", bank_numbers=("PSU 901",), coverage="partial"),
        ),
    },
    {
        "parent_question_code": "q_housing_property",
        "prompt_en": "Which named federal housing service applies? Select all that apply.",
        "prompt_fr": "Quel service fédéral de logement nommé s'applique? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("on_reserve_housing", "The On-Reserve Housing Program or its loan guarantee", "Programme de logement dans les réserves ou sa garantie de prêt", "Indigenous Services Canada", "Services aux Autochtones Canada", bank_numbers=("ISC PPU 011",)),
            _option("canadian_forces_housing", "Canadian Forces housing", "Logements des Forces canadiennes", "Department of National Defence / Canadian Armed Forces", "Ministère de la Défense nationale / Forces armées canadiennes", bank_numbers=("DND PPU 885",)),
            _option("other_federal_housing", "Another named federal housing or home-buying program", "Un autre programme fédéral nommé de logement ou d'achat d'une habitation", "Federal institution that ran the program", "Institution fédérale responsable du programme", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_civic_contact",
        "prompt_en": "Which civic or public-participation activities apply? Select all that apply.",
        "prompt_fr": "Quelles activités civiques ou de participation publique s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("federal_election", "Registered or applied to vote in a federal election", "Inscription ou demande de vote à une élection fédérale", "Elections Canada", "Élections Canada", coverage="inventory_gap"),
            _option("federal_consultation", "Took part in a federal public consultation", "Participation à une consultation publique fédérale", "The department conducting the consultation, such as Health Canada", "Ministère responsable de la consultation, comme Santé Canada", bank_numbers=("HC PPU 051",), coverage="partial"),
            _option("other_civic_contact", "Contacted a federal office, signed a petition or took part in another way", "Communication avec un bureau fédéral, signature d'une pétition ou autre participation", "Federal institution involved", "Institution fédérale concernée", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_culture_volunteer",
        "prompt_en": "Which federal culture, recreation or volunteer activities apply? Select all that apply.",
        "prompt_fr": "Quelles activités fédérales de culture, de loisirs ou de bénévolat s'appliquent? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("canada_day_challenge", "Entered the Canada Day Challenge", "Participation au Défi de la fête du Canada", "Canadian Heritage", "Patrimoine canadien", bank_numbers=("PCH PPU 027",)),
            _option("federal_volunteer_program", "Registered with a federally run volunteer program", "Inscription à un programme de bénévolat fédéral", "Canadian Heritage or the federal institution running the program", "Patrimoine canadien ou institution fédérale responsable du programme", bank_numbers=("PCH PPU 070",), coverage="partial"),
            _option("other_culture_recreation", "Another named federal arts, sport, heritage or parks activity", "Une autre activité fédérale nommée liée aux arts, aux sports, au patrimoine ou aux parcs", "Federal institution that ran the activity", "Institution fédérale responsable de l'activité", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_research_survey",
        "prompt_en": "What was your role in federal research? Select all that apply.",
        "prompt_fr": "Quel était votre rôle dans la recherche fédérale? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("research_participant", "I answered a survey, joined a study or took part in testing", "J'ai répondu à un sondage, participé à une étude ou pris part à des essais", "The institution conducting the research, such as Health Canada", "Institution responsable de la recherche, comme Santé Canada", bank_numbers=("HC PPU 035", "HC PPU 314"), coverage="partial"),
            _option("researcher_reviewer", "I led, reviewed or supported a federal research project", "J'ai dirigé, évalué ou soutenu un projet de recherche fédéral", "The research institution, such as the Public Health Agency of Canada", "Institution de recherche, comme l'Agence de la santé publique du Canada", bank_numbers=("PHAC PPU 290",), coverage="partial"),
            _option("other_research_survey", "Another federal research, survey or focus-group activity", "Une autre activité fédérale de recherche, de sondage ou de groupe de discussion", "Federal institution that ran the activity", "Institution fédérale responsable de l'activité", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_emergency",
        "prompt_en": "Which federal emergency service helped you? Select all that apply.",
        "prompt_fr": "Quel service d'urgence fédéral vous a aidé? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("search_and_rescue", "A Canadian Armed Forces search-and-rescue response", "Intervention de recherche et sauvetage des Forces armées canadiennes", "Department of National Defence / Canadian Armed Forces", "Ministère de la Défense nationale / Forces armées canadiennes", bank_numbers=("DND PPU 050",)),
            _option("fishery_ice_assistance", "Temporary fishery help after severe ice conditions", "Aide temporaire aux pêches après de graves conditions de glace", "Fisheries and Oceans Canada", "Pêches et Océans Canada", bank_numbers=("DFO PPU 045",)),
            _option("other_federal_emergency", "Another named federal emergency or disaster service", "Un autre service fédéral nommé d'urgence ou de catastrophe", "Federal institution that provided the service", "Institution fédérale qui a fourni le service", coverage="fallback", fallback_to_parent=True),
        ),
    },
    {
        "parent_question_code": "q_family_vital",
        "prompt_en": "Which named federal life-event service applies? Select all that apply.",
        "prompt_fr": "Quel service fédéral nommé lié à un événement de vie s'applique? Sélectionnez toutes les réponses pertinentes.",
        "options": (
            _option("cpp_survivor_death_benefit", "A Canada Pension Plan survivor or death benefit", "Prestation de survivant ou de décès du Régime de pensions du Canada", "Employment and Social Development Canada / Service Canada", "Emploi et Développement social Canada / Service Canada", bank_numbers=("ESDC PPU 146",)),
            _option("first_nations_estate", "Administration of a First Nations estate", "Administration d'une succession des Premières Nations", "Indigenous Services Canada", "Services aux Autochtones Canada", bank_numbers=("ISC PPU 105",)),
            _option("other_federal_life_event", "Another named federal birth, marriage, divorce, adoption or death service", "Un autre service fédéral nommé lié à une naissance, un mariage, un divorce, une adoption ou un décès", "Federal institution that ran the service", "Institution fédérale responsable du service", coverage="fallback", fallback_to_parent=True),
        ),
    },
)


def adaptive_routes() -> list[dict[str, Any]]:
    """Return a JSON-serializable copy of the curated route contract."""

    return deepcopy([
        {**route, "options": list(route["options"])}
        for route in _ROUTES + _BETA_ROUTES
    ])


def route_index(routes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(route["parent_question_code"]): route for route in routes}


def route_option_index(route: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(option["code"]): dict(option) for option in route["options"]}
