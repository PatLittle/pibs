"""Curated adaptive routes for compound My Info questionnaire gates.

The top-level taxonomy intentionally favours recall.  These routes provide the
smallest useful follow-up for interactions whose institution or PIB family can
be inferred from a concrete activity.  Selectors are deliberately explicit and
reviewable: no route relies on opaque similarity scoring.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


ADAPTIVE_ROUTE_VERSION = "1.0"


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


def adaptive_routes() -> list[dict[str, Any]]:
    """Return a JSON-serializable copy of the curated route contract."""

    return deepcopy([
        {**route, "options": list(route["options"])}
        for route in _ROUTES
    ])


def route_index(routes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(route["parent_question_code"]): route for route in routes}


def route_option_index(route: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(option["code"]): dict(option) for option in route["options"]}
