"""Reviewed activity selectors for the separate V2 prototype.

Titles/keywords never select personal results. Each institutional selector is
scoped to a publisher, and each activity names the eligible role or program.
The build adds verbatim population/purpose evidence to every selector.
"""

GROUPS = [
    ("everyday", "Everyday records, travel and voting", "Dossiers courants, voyages et vote"),
    ("benefits", "Benefits, pensions and health", "Prestations, pensions et santé"),
    ("military", "Military service and veterans", "Service militaire et vétérans"),
    ("work", "Federal jobs and workplace", "Emplois et milieu de travail fédéraux"),
    ("business", "Contracts, licences and property", "Marchés, permis et propriété"),
    ("learning", "Education, research and community programs", "Études, recherche et programmes communautaires"),
    ("justice", "Complaints, reviews and safety", "Plaintes, recours et sécurité"),
    ("contact", "Requests, contact and public events", "Demandes, communications et événements publics"),
]

INSTITUTIONS = {
    "ESDC": "department-of-employment-and-social-development",
    "IRCC": "department-of-citizenship-and-immigration",
    "VAC": "department-of-veterans-affairs",
    "DND": "department-of-national-defence",
    "CBSA": "canada-border-services-agency",
    "EC": "office-of-the-chief-electoral-officer",
    "TC": "department-of-transport",
    "RCMP": "royal-canadian-mounted-police",
    "ERC": "royal-canadian-mounted-police-external-review-committee",
    "PCH": "department-of-canadian-heritage",
    "GAC": "department-of-foreign-affairs-trade-and-development",
    "HC": "department-of-health",
    "PHAC": "public-health-agency-of-canada",
    "ISC": "department-of-indigenous-services",
    "CSA": "canadian-space-agency",
    "CRA": "canada-revenue-agency",
}


def institution(code):
    return "ati-schedule-i-" + INSTITUTIONS[code]


def record(owner, bank):
    return f"institution:{institution(owner)}:{bank}" if owner else f"standard:{bank}"


def activity(identifier, group, en, fr, owner=None, banks=(), *, scope="inferred", help_en="", help_fr="", coverage="reviewed"):
    return {
        "id": identifier, "group": group, "label_en": en, "label_fr": fr,
        "help_en": help_en, "help_fr": help_fr,
        "record_ids": [record(owner, bank) for bank in banks],
        "institution_ids": [institution(owner)] if owner else [],
        "scope": scope, "coverage": coverage,
        "reason_en": "The selected activity and role match the published purpose and population shown below.",
        "reason_fr": "L'activité et le rôle choisis correspondent à la fin et à la population décrites ci-dessous.",
    }


ACTIVITIES = [
    activity("tax_return", "everyday", "Filed a federal income tax return", "Produit une déclaration fédérale de revenus", "CRA", coverage="source_gap", help_en="CRA is the place to start. This collected inventory does not yet support a reviewed personal tax-return match.", help_fr="Commencez par l'ARC. L'inventaire recueilli ne permet pas encore une correspondance examinée pour votre déclaration de revenus."),
    activity("federal_vote", "everyday", "Registered or voted in a federal election", "Inscription ou vote à une élection fédérale", "EC", ("ELECTIONS PPU 037",), help_en="Registration and identification records; this does not describe how you voted.", help_fr="Dossiers d'inscription et d'identification; ils ne décrivent pas votre choix de vote."),
    activity("passport", "everyday", "Applied for or renewed a Canadian passport", "Demandé ou renouvelé un passeport canadien", "IRCC", ("IRCC PPU 081",)),
    activity("passport_service_canada", "everyday", "Used Service Canada to apply for a passport", "Demandé un passeport par l'intermédiaire de Service Canada", "ESDC", ("ESDC PPU 708",), help_en="Select this too if Service Canada received your passport application.", help_fr="Cochez aussi cette activité si Service Canada a reçu votre demande de passeport."),
    activity("passport_reference", "everyday", "Was named as a passport guarantor, reference or emergency contact", "Nommé comme répondant, référence ou personne à contacter en cas d'urgence pour un passeport", "IRCC", ("IRCC PPU 081",), help_en="An example of information supplied by somebody else.", help_fr="Exemple de renseignements fournis par une autre personne."),
    activity("border_crossing", "everyday", "Entered Canada and made a traveller declaration", "Entré au Canada et fait une déclaration de voyageur", "CBSA", ("CBSA PPU 018",), help_en="A crossing alone does not imply a NEXUS, penalty, officer interview or customs-payment record.", help_fr="Un passage à la frontière ne suppose pas un dossier NEXUS, une pénalité, une entrevue ou un paiement de droits."),
    activity("commercial_arrival", "everyday", "Travelled to Canada on a commercial flight or other commercial carrier", "Voyagé vers le Canada à bord d'un transporteur commercial", "CBSA", ("CBSA PPU 008",)),
    activity("nexus", "everyday", "Applied for or renewed NEXUS membership", "Demandé ou renouvelé une adhésion NEXUS", "CBSA", ("CBSA PPU 031",)),
    activity("remote_border_permit", "everyday", "Applied for a Remote Area Border Crossing permit", "Demandé un permis de passage à la frontière dans une région éloignée", "CBSA", ("CBSA PPU 013",)),
    activity("customs_payment", "everyday", "Had duties or taxes assessed on goods brought into Canada", "Fait évaluer des droits ou taxes sur des biens apportés au Canada", "CBSA", ("CBSA PPU 010",)),
    activity("citizenship", "everyday", "Applied for citizenship or a citizenship certificate", "Demandé la citoyenneté ou un certificat de citoyenneté", "IRCC", ("IRCC PPU 050",)),
    activity("economic_immigration", "everyday", "Submitted an Express Entry profile or economic permanent-residence application", "Soumis un profil Entrée express ou une demande de résidence permanente économique", "IRCC", ("IRCC PPU 042",)),
    activity("consular_help", "everyday", "Registered with a Canadian mission abroad or sought consular help", "Inscrit auprès d'une mission canadienne à l'étranger ou demandé une aide consulaire", "GAC", ("GAC PPU 010",)),
    activity("ei", "benefits", "Applied for Employment Insurance benefits", "Demandé des prestations d'assurance-emploi", "ESDC", ("ESDC PPU 150",)),
    activity("cpp", "benefits", "Applied for or received a Canada Pension Plan benefit", "Demandé ou reçu une prestation du Régime de pensions du Canada", "ESDC", ("ESDC PPU 146",)),
    activity("oas", "benefits", "Applied for or received Old Age Security, GIS or an Allowance", "Demandé ou reçu la Sécurité de la vieillesse, le SRG ou une allocation", "ESDC", ("ESDC PPU 116",)),
    activity("sin", "benefits", "Applied for or updated a Social Insurance Number", "Demandé ou mis à jour un numéro d'assurance sociale", "ESDC", ("ESDC PPU 390",)),
    activity("rdsp", "benefits", "Was a beneficiary or holder of a Registered Disability Savings Plan", "Bénéficiaire ou titulaire d'un régime enregistré d'épargne-invalidité", "ESDC", ("ESDC PPU 038",)),
    activity("dental_plan", "benefits", "Applied for the Canadian Dental Care Plan", "Demandé le Régime canadien de soins dentaires", "HC", ("HC PPU 440",), help_en="Health Canada's description includes administration with Service Canada and its contracted provider.", help_fr="La description de Santé Canada comprend l'administration avec Service Canada et son fournisseur sous contrat."),
    activity("caf_application", "military", "Applied to join the Canadian Armed Forces", "Demandé à m'enrôler dans les Forces armées canadiennes", "DND", ("DND PPU 025",), help_en="Applying does not imply you served or had a member personnel file.", help_fr="Une demande d'enrôlement ne signifie pas que vous avez servi ou eu un dossier de membre."),
    activity("caf_regular_service", "military", "Served in the Regular Force", "Servi dans la Force régulière", "DND", ("DND PPE 818",), help_en="The source bank specifies Regular Force members. Reserve service can be explored in the program directory.", help_fr="Le fichier vise les membres de la Force régulière. Le répertoire permet d'explorer les dossiers de la Réserve."),
    activity("veterans_unknown", "military", "Used a veterans benefit but do not know its name", "Utilisé une prestation pour vétérans sans en connaître le nom", "VAC", coverage="needs_detail", help_en="Veterans Affairs is inferred. Choose a specific benefit below or explore its programs to identify relevant records.", help_fr="Anciens Combattants est identifié. Choisissez une prestation précise ci-dessous ou explorez ses programmes."),
    activity("veterans_education", "military", "Applied for Veterans Affairs' Education and Training Benefit", "Demandé la prestation pour études et formation d'Anciens Combattants", "VAC", ("VAC PPU 710",)),
    activity("veterans_income", "military", "Applied for Veterans Affairs' Income Replacement Benefit", "Demandé la prestation de remplacement du revenu d'Anciens Combattants", "VAC", ("VAC PPU 715",)),
    activity("war_veterans_allowance", "military", "Applied for the War Veterans Allowance", "Demandé l'allocation aux anciens combattants", "VAC", ("VAC PPU 040",)),
    activity("agent_orange", "military", "Applied for the Agent Orange ex-gratia payment related to CFB Gagetown in 1966–1967", "Demandé le paiement à titre gracieux pour l'agent Orange lié à la BFC Gagetown en 1966–1967", "VAC", ("VAC PPU 200",), help_en="Historical and narrowly defined program. It is never inferred from receiving another veterans benefit.", help_fr="Programme historique à portée précise. Il n'est jamais déduit d'une autre prestation pour vétérans."),
    activity("military_housing", "military", "Applied for or occupied housing managed by National Defence", "Demandé ou occupé un logement géré par la Défense nationale", "DND", ("DND PPU 885",)),
    activity("federal_job", "work", "Applied for a federal civilian job", "Postulé à un emploi civil fédéral", None, ("PSE 902",), scope="choose_institution"),
    activity("federal_employee", "work", "Worked as a federal civilian employee", "Travaillé comme fonctionnaire fédéral civil", None, ("PSE 901", "PSE 904"), scope="choose_institution", help_en="Choose the employer. Military service and contracts have separate activities.", help_fr="Choisissez l'employeur. Le service militaire et les marchés sont des activités distinctes."),
    activity("employee_grievance", "work", "Filed a grievance as a federal civilian employee", "Déposé un grief comme fonctionnaire fédéral civil", None, ("PSE 910",), scope="choose_institution"),
    activity("employee_assistance", "work", "Used an Employee Assistance Program offered by a federal employer", "Utilisé un programme d'aide aux employés d'un employeur fédéral", None, ("PSE 916",), scope="choose_institution"),
    activity("security_screening", "work", "Completed a federal personnel security screening", "Fait l'objet d'un filtrage de sécurité du personnel fédéral", None, ("PSU 917",), scope="choose_institution"),
    activity("professional_contract", "business", "Bid on or held a federal professional-services contract", "Soumissionné ou obtenu un marché fédéral de services professionnels", None, ("PSU 912",), scope="choose_institution"),
    activity("aviation_licence", "business", "Applied for a flight-crew or air-traffic-controller licence", "Demandé une licence de membre d'équipage de conduite ou de contrôleur aérien", "TC", ("TC PPU 005",)),
    activity("transport_clearance", "business", "Applied for an airport or marine-facility security clearance", "Demandé une habilitation de sécurité pour un aéroport ou une installation maritime", "TC", ("TC PPU 093",)),
    activity("boating_card", "business", "Obtained a Pleasure Craft Operator Card or an online-test token", "Obtenu une carte de conducteur d'embarcation de plaisance ou un jeton d'examen en ligne", "TC", ("TC PPU 023",)),
    activity("pleasure_craft_licence", "business", "Licensed, transferred or cancelled a pleasure-craft licence", "Obtenu, transféré ou annulé un permis d'embarcation de plaisance", "TC", ("TC PPU 044",)),
    activity("vessel_registration", "business", "Registered a vessel with Transport Canada", "Immatriculé un bâtiment auprès de Transports Canada", "TC", ("TC PPU 041",)),
    activity("firearms_licence", "business", "Applied for a firearms licence or related authorization", "Demandé un permis d'armes à feu ou une autorisation connexe", "RCMP", ("RCMP PPU 100",)),
    activity("firearm_registration", "business", "Applied to register a firearm", "Demandé l'enregistrement d'une arme à feu", "RCMP", ("RCMP PPU 037",)),
    activity("student_finance", "learning", "Applied for Canada Student Loans or Grants, repayment assistance or loan forgiveness", "Demandé un prêt ou une bourse d'études du Canada, une aide au remboursement ou une remise de prêt", "ESDC", ("ESDC PPU 030",)),
    activity("resp", "learning", "Was a beneficiary or subscriber of a Registered Education Savings Plan", "Bénéficiaire ou souscripteur d'un régime enregistré d'épargne-études", "ESDC", ("ESDC PPU 506",)),
    activity("phac_research", "learning", "Led, reviewed or supported a Public Health Agency research project", "Dirigé, examiné ou soutenu un projet de recherche de l'Agence de la santé publique", "PHAC", ("PHAC PPU 290",)),
    activity("on_reserve_loan", "learning", "Received an on-reserve housing loan backed by a Ministerial Loan Guarantee", "Reçu un prêt au logement dans une réserve garanti par une garantie d'emprunt ministérielle", "ISC", ("ISC PPU 011",)),
    activity("first_nations_estate", "learning", "Was involved in a First Nations estate administered by Indigenous Services", "Participé à une succession des Premières Nations administrée par Services aux Autochtones", "ISC", ("ISC PPU 105",), help_en="The published population concerns people residing or ordinarily resident on reserve and specified relatives or representatives.", help_fr="La population publiée vise les personnes résidant habituellement dans une réserve et certains proches ou représentants."),
    activity("cbsa_complaint", "justice", "Complained to CBSA about its staff or procedures", "Porté plainte à l'ASFC au sujet de son personnel ou de ses procédures", "CBSA", ("CBSA PPU 003",)),
    activity("cbsa_recourse", "justice", "Asked CBSA to review an enforcement decision or seizure", "Demandé à l'ASFC de réviser une décision d'exécution ou une saisie", "CBSA", ("CBSA PPU 005",)),
    activity("erc_grievance", "justice", "Was an RCMP member whose grievance was referred to the External Review Committee under the former RCMP Act", "Membre de la GRC dont le grief a été renvoyé au Comité externe d'examen sous l'ancienne Loi sur la GRC", "ERC", ("ERC PPU 802",), help_en="A public complaint about police does not establish this referral or employment role.", help_fr="Une plainte du public contre la police ne prouve pas ce renvoi ni ce rôle d'employé."),
    activity("other_complaint", "justice", "Made another complaint or appeal to a federal organization", "Présenté une autre plainte ou un autre appel à une organisation fédérale", scope="choose_institution", coverage="needs_detail", help_en="Choose the organization, then explore its programs. The complaint type is needed to identify the appropriate bank.", help_fr="Choisissez l'organisation, puis explorez ses programmes. Il faut connaître le type de plainte pour trouver le bon fichier."),
    activity("search_rescue", "justice", "Was the subject of or provided information for a military search-and-rescue operation", "Visé par une opération militaire de recherche et sauvetage ou fourni des renseignements à son sujet", "DND", ("DND PPU 050",)),
    activity("access_request", "contact", "Made a formal access-to-information, personal-information or correction request", "Présenté une demande officielle d'accès à l'information, de renseignements personnels ou de correction", None, ("PSU 901",), scope="choose_institution"),
    activity("executive_correspondence", "contact", "Wrote to a federal minister or head of an institution", "Écrit à un ministre fédéral ou au dirigeant d'une institution", None, ("PSU 902",), scope="choose_institution"),
    activity("health_consultation", "contact", "Took part in a Health Canada health-protection consultation", "Participé à une consultation de Santé Canada sur la protection de la santé", "HC", ("HC PPU 051",)),
    activity("space_launch", "contact", "Registered with the Canadian Space Agency to attend a mission launch", "Inscrit auprès de l'Agence spatiale canadienne pour assister au lancement d'une mission", "CSA", ("CSA PPU 020",)),
    activity("heritage_volunteer", "contact", "Registered with Canadian Heritage's Volunteer Centre", "Inscrit au Centre de bénévolat de Patrimoine canadien", "PCH", ("PCH PPU 070",)),
    activity("canada_day_challenge", "contact", "Entered the Canada Day Challenge as a youth, or was their parent or guardian", "Participé au Défi de la fête du Canada comme jeune, parent ou tuteur", "PCH", ("PCH PPU 027",)),
]
