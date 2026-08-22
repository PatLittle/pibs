"""Deterministic citizen-interaction features for the My Info questionnaire.

The source PIB tables are descriptive inventories, not evidence that a named
person appears in a bank.  This module therefore produces *candidate* paths
through a questionnaire.  Every label includes the exact source-field excerpt
that caused it to be assigned so that later review and tuning stay auditable.

The public API deliberately accepts either source schema in this repository:
``spib_en_fr.csv`` (standard PIBs) or ``pib_table_en_fr_all.csv``
(institution-specific PIBs).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import re
from typing import Iterable, Mapping, Pattern, Sequence


@dataclass(frozen=True)
class Rule:
    code: str
    label_en: str
    label_fr: str
    patterns: tuple[str, ...]


@dataclass(frozen=True)
class QuestionGroup:
    code: str
    question_en: str
    question_fr: str
    topic_codes: tuple[str, ...] = ()
    role_codes: tuple[str, ...] = ()
    action_codes: tuple[str, ...] = ()


# A match in a title/class is intentionally stronger than the same phrase in a
# note or in an institution name.  Confidence is about the label assignment,
# never about whether the government actually holds a person's information.
FIELD_CONFIDENCE = {
    "title_en": 0.96,
    "title_fr": 0.96,
    "class_of_individuals_en": 0.94,
    "class_of_individuals_fr": 0.94,
    "purpose_en": 0.88,
    "purpose_fr": 0.88,
    "description_en": 0.84,
    "description_fr": 0.84,
    "consistent_uses_en": 0.72,
    "consistent_uses_fr": 0.72,
    "note_en": 0.66,
    "note_fr": 0.66,
    "institution_name_en": 0.58,
    "institution_name_fr": 0.58,
}


TOPIC_RULES = (
    Rule("government_employment", "Government employment", "Emploi au gouvernement", (
        r"\b(?:government|public service|federal) employ(?:ee|ment|er)s?\b", r"\bpersonnel\b",
        r"\bpayroll\b", r"\bpension(?:er|s)?\b", r"\bstaff relations?\b", r"\bworkplace\b",
        r"\b(?:fonction publique|employ[eé]s?|emploi|personnel|paie|pension)\b",
    )),
    Rule("benefits_support", "Benefits and income support", "Prestations et soutien du revenu", (
        r"\b(?:benefit|allowance|income support|compensation|rebate|subsid(?:y|ies)|employment insurance)\b",
        r"\b(?:old age security|canada pension plan|social assistance)\b",
        r"\b(?:prestation|allocation|soutien du revenu|indemnisation|remboursement|assurance[- ]emploi)\w*\b",
    )),
    Rule("grants_contributions", "Grants and contributions", "Subventions et contributions", (
        r"\b(?:grant|contribution|funding application|funding program|award|scholarship|bursar(?:y|ies))s?\b",
        r"\b(?:subvention|contribution|financement|bourse)s?\b",
    )),
    Rule("tax_customs_duties", "Taxes, customs and duties", "Impôts, douanes et droits", (
        r"\b(?:income tax|taxpayer|tax return|taxation|excise|customs dut(?:y|ies)|customs declaration|tariff)\b",
        r"\b(?:imp[oô]t|contribuable|d[ée]claration de revenus|accise|douane|tarif)s?\b",
    )),
    Rule("immigration_citizenship", "Immigration and citizenship", "Immigration et citoyenneté", (
        r"\b(?:immigration|immigrant|refugee|asylum|citizenship|permanent residen(?:t|ce)|temporary resident|visa|newcomer|resettlement)\w*\b",
        r"\b(?:immigration|immigrant|r[ée]fugi[ée]|asile|citoyennet[ée]|r[ée]sident permanent|visa|nouvel arrivant|r[ée]installation)\w*\b",
    )),
    Rule("travel_border", "Travel, passports and the border", "Voyages, passeports et frontière", (
        r"\b(?:passport|travel(?:ler|led|ling)?|border crossing|port of entry|nexus|customs declaration|aviation security)\b",
        r"\b(?:passeport|voyageur|voyage|fronti[eè]re|point d.entry|d[ée]claration douani[eè]re|s[ûu]ret[ée] a[ée]rienne)\w*\b",
    )),
    Rule("health_disability", "Health and disability", "Santé et invalidité", (
        r"\b(?:health|medical|patient|disabilit(?:y|ies)|illness|injur(?:y|ies)|prescription|dental|mental health|medical device)\b",
        r"\b(?:sant[ée]|m[ée]dical|patient|invalidit[ée]|handicap|maladie|blessure|ordonnance|dentaire|sant[ée] mentale)\w*\b",
    )),
    Rule("indigenous_services", "First Nations, Inuit and Métis services", "Services aux Premières Nations, aux Inuit et aux Métis", (
        r"\b(?:first nations?|inuit|m[ée]tis|indigenous|aboriginal|indian status|status indian|reserve)\b",
        r"\b(?:premi[eè]res nations?|inuit|m[ée]tis|autochtone|statut d.indien|r[ée]serve)\w*\b",
    )),
    Rule("veterans_military", "Military and veterans services", "Services militaires et aux vétérans", (
        r"\b(?:veteran|armed forces|military|canadian forces|caf member|service member|national defence)\w*\b",
        r"\b(?:v[ée]t[ée]ran|forces arm[ée]es|militaire|forces canadiennes|d[ée]fense nationale)\w*\b",
    )),
    Rule("education_training", "Education, student aid and training", "Études, aide aux étudiants et formation", (
        r"\b(?:student|school|education|college|universit(?:y|ies)|student loan|apprentice|training program|scholarship|bursar(?:y|ies))s?\b",
        r"\b(?:[ée]tudiant|[ée]cole|[ée]tudes|coll[eè]ge|universit[ée]|pr[êe]t [ée]tudiant|apprenti|formation|bourse)s?\b",
    )),
    Rule("justice_public_safety", "Law enforcement, corrections and public safety", "Application de la loi, services correctionnels et sécurité publique", (
        r"\b(?:offender|inmate|prisoner|police|law enforcement|criminal|correctional|parole|probation|arrest|detention|security screening|investigation)\w*\b",
        r"\b(?:d[ée]linquant|d[ée]tenu|prisonnier|police|application de la loi|criminel|correctionnel|lib[ée]ration conditionnelle|arrestation|enqu[êe]te)\w*\b",
    )),
    Rule("complaints_appeals_legal", "Complaints, appeals and legal proceedings", "Plaintes, appels et procédures judiciaires", (
        r"\b(?:complainant|complaint|grievance|appeal|tribunal|litigant|litigation|lawsuit|legal proceeding|human rights)\w*\b",
        r"\b(?:plaignant|plainte|grief|appel|tribunal|litige|poursuite|proc[ée]dure judiciaire|droits de la personne)\w*\b",
    )),
    Rule("access_privacy", "Access to information and privacy requests", "Demandes d’accès à l’information et de protection des renseignements personnels", (
        r"\b(?:access to information|privacy act|personal information request|correct(?:ion)? of personal information|atip)\b",
        r"\b(?:acc[eè]s [àa] l.information|loi sur la protection des renseignements personnels|demande de renseignements personnels|aiprp)\b",
    )),
    Rule("payments_debt", "Payments, reimbursements and debts", "Paiements, remboursements et dettes", (
        r"\b(?:accounts? payable|accounts? receivable|payment|reimbursement|expense claim|debt|debtor|overpayment|loan repayment|direct deposit)\w*\b",
        r"\b(?:comptes? cr[ée]diteurs?|comptes? d[ée]biteurs?|paiement|remboursement|dette|d[ée]biteur|trop[- ]per[çc]u|d[ée]p[oô]t direct)\w*\b",
    )),
    Rule("contracts_procurement", "Contracts, procurement and supplying government", "Marchés, approvisionnement et fourniture au gouvernement", (
        r"\b(?:contractor|supplier|vendor|procurement|contracting|contract|bidder|tender|acquisition card|professional services)\w*\b",
        r"\b(?:entrepreneur|fournisseur|approvisionnement|march[ée]|soumissionnaire|appel d.offres|carte d.achat|services professionnels)\w*\b",
    )),
    Rule("business_regulation", "Business, licensing and regulation", "Entreprises, permis et réglementation", (
        r"\b(?:business owner|self-employed|company|corporation|licen[cs]e|permit|registration|regulated|regulatory|inspection|compliance)\w*\b",
        r"\b(?:propri[ée]taire d.entreprise|travailleur autonome|soci[ée]t[ée]|permis|inscription|r[ée]glement[ée]|inspection|conformit[ée])\w*\b",
    )),
    Rule("housing_property", "Housing and property", "Logement et propriété", (
        r"\b(?:housing|homeowner|home buyer|mortgage|property owner|tenant|landlord|residential propert|real estate)\w*\b",
        r"\b(?:logement|propri[ée]taire|acheteur d.une maison|hypoth[eè]que|locataire|immeuble|bien immobilier)\w*\b",
    )),
    Rule("transport_licensing", "Vehicles and transportation", "Véhicules et transport", (
        r"\b(?:driver|vehicle|motor carrier|vessel|aircraft|pilot|aviation|marine transportation|railway|transportation licence)\w*\b",
        r"\b(?:conducteur|v[ée]hicule|transporteur routier|navire|a[ée]ronef|pilote|aviation|transport maritime|chemin de fer)\w*\b",
    )),
    Rule("democratic_civic", "Elections and democratic participation", "Élections et participation démocratique", (
        r"\b(?:voter|elector|election|candidate|political part(?:y|ies)|member of parliament|petition|lobbyist)\w*\b",
        r"\b(?:[ée]lecteur|vote|[ée]lection|candidat|parti politique|d[ée]put[ée]|p[ée]tition|lobbyiste)\w*\b",
    )),
    Rule("communications_engagement", "Contacting government and public engagement", "Communications avec le gouvernement et participation publique", (
        r"\b(?:public inquiry|correspondence|mailing list|subscription|newsletter|consultation|public engagement|stakeholder|ministerial correspondence)\w*\b",
        r"\b(?:demande de renseignements|correspondance|liste d.envoi|abonnement|bulletin|consultation|participation publique|intervenant)\w*\b",
    )),
    Rule("culture_recreation_volunteering", "Culture, recreation and volunteering", "Culture, loisirs et bénévolat", (
        r"\b(?:artist|arts?|athlete|sport|cultur(?:e|al)|heritage|volunteer|museum|historic site|national park|recreation|fishing|hunting)\w*\b",
        r"\b(?:artiste|arts?|athl[eè]te|sport|culture|patrimoine|b[ée]n[ée]vole|mus[ée]e|lieu historique|parc national|loisir|p[êe]che|chasse)\w*\b",
    )),
    Rule("research_surveys", "Research, surveys and testing", "Recherche, sondages et tests", (
        r"\b(?:research participant|research study|survey|questionnaire|focus group|clinical trial|test participant)\w*\b",
        r"\b(?:participant [àa] la recherche|[ée]tude de recherche|sondage|questionnaire|groupe de discussion|essai clinique)\w*\b",
    )),
    Rule("emergency_assistance", "Emergencies and disaster assistance", "Urgences et aide en cas de catastrophe", (
        r"\b(?:emergency|disaster|evacuation|business continuity|disruption of services|emergency assistance)\w*\b",
        r"\b(?:urgence|catastrophe|[ée]vacuation|continuit[ée] des activit[ée]s|interruption des services|aide d.urgence)\w*\b",
    )),
    Rule("family_vital_events", "Family and vital events", "Famille et événements de la vie", (
        r"\b(?:birth registration|birth certificate|marriage|divorce|adoption|child support|death certificate|vital statistics)\w*\b",
        r"\b(?:enregistrement de naissance|certificat de naissance|mariage|divorce|adoption|pension alimentaire|certificat de d[ée]c[eè]s|[ée]tat civil)\w*\b",
    )),
)


ROLE_RULES = (
    Rule("government_employee", "Current or former government employee", "Employé actuel ou ancien du gouvernement", (
        r"\b(?:current|former)?\s*(?:government|public service|federal) employees?\b", r"\bemployees? of (?:the )?(?:government )?institution\b",
        r"\b(?:employ[ée]s? (?:actuels? ou anciens? )?(?:du gouvernement|de la fonction publique|de l.institution))\b",
    )),
    Rule("job_applicant", "Job applicant or candidate", "Candidat à un emploi", (
        r"\b(?:job|employment) applicants?\b", r"\b(?:candidates? for employment|seeking employment|appl(?:y|ied|ication) for (?:a )?(?:job|position|employment))\b",
        r"\b(?:candidats? [àa] (?:un )?emploi|demandeurs? d.emploi|postul[ée])\w*\b",
    )),
    Rule("contractor_supplier", "Contractor, supplier or vendor", "Entrepreneur ou fournisseur", (
        r"\b(?:contractor|supplier|vendor|bidder|service provider|consultant)s?\b",
        r"\b(?:entrepreneur|fournisseur|soumissionnaire|prestataire de services|consultant)s?\b",
    )),
    Rule("program_applicant_recipient", "Program applicant or recipient", "Demandeur ou bénéficiaire d’un programme", (
        r"\b(?:program|benefit|grant|loan|funding) applicants?\b", r"\b(?:benefit|program|grant|loan|funding) recipients?\b", r"\bclaimants?\b",
        r"\b(?:demandeurs?|b[ée]n[ée]ficiaires?) (?:d.un |de |du )?(?:programme|prestation|subvention|pr[êe]t|financement)\b",
    )),
    Rule("representative_guardian", "Representative, guardian or attorney", "Représentant, tuteur ou mandataire", (
        r"\b(?:authorized |legal )?representatives?\b", r"\b(?:guardian|power of attorney|legal counsel|agent acting on behalf)\b",
        r"\b(?:repr[ée]sentant|tuteur|procuration|conseiller juridique|mandataire)s?\b",
    )),
    Rule("family_dependent", "Family member or dependant", "Membre de la famille ou personne à charge", (
        r"\b(?:family members?|spous(?:e|es)|common-law partners?|dependants?|dependents?|children|parents|next of kin)\b",
        r"\b(?:membres? de la famille|conjoints?|personnes? [àa] charge|enfants?|parents?|plus proche parent)\b",
    )),
    Rule("student_learner", "Student, apprentice or learner", "Étudiant, apprenti ou participant à une formation", (
        r"\b(?:student|apprentice|trainee|intern)s?\b", r"\b(?:[ée]tudiant|apprenti|stagiaire)s?\b",
    )),
    Rule("immigrant_refugee_newcomer", "Immigrant, refugee or citizenship applicant", "Immigrant, réfugié ou demandeur de citoyenneté", (
        r"\b(?:immigrants?|refugees?|asylum seekers?|citizenship applicants?|permanent residents?|visa applicants?|newcomers?)\b",
        r"\b(?:immigrants?|r[ée]fugi[ée]s?|demandeurs? d.asile|demandeurs? de citoyennet[ée]|r[ée]sidents? permanents?|nouveaux arrivants?)\b",
    )),
    Rule("traveller", "Traveller or border-program participant", "Voyageur ou participant à un programme frontalier", (
        r"\b(?:travellers?|passengers?|passport holders?|nexus (?:members?|applicants?))\b", r"\b(?:voyageurs?|passagers?|titulaires? de passeport)\b",
    )),
    Rule("veteran_service_member", "Veteran or military member", "Vétéran ou militaire", (
        r"\b(?:veterans?|armed forces members?|military members?|caf members?|service members?)\b",
        r"\b(?:v[ée]t[ée]rans?|membres? des forces arm[ée]es|militaires?)\b",
    )),
    Rule("indigenous_person", "First Nations, Inuit or Métis person", "Membre des Premières Nations, Inuit ou Métis", (
        r"\b(?:first nations? members?|inuit|m[ée]tis|indigenous (?:people|persons?|individuals?)|status indians?)\b",
        r"\b(?:membres? des premi[eè]res nations|inuit|m[ée]tis|personnes? autochtones?|indiens? inscrits?)\b",
    )),
    Rule("patient_disabled_person", "Patient or person with a disability", "Patient ou personne en situation de handicap", (
        r"\b(?:patients?|persons? with disabilities|people with disabilities|disabled (?:persons?|individuals?)|medical patients?)\b",
        r"\b(?:patients?|personnes? (?:handicap[ée]es?|en situation de handicap))\b",
    )),
    Rule("justice_involved", "Person involved with law enforcement or corrections", "Personne visée par la justice ou les services correctionnels", (
        r"\b(?:offenders?|inmates?|prisoners?|parolees?|probationers?|suspects?|accused persons?|detainees?)\b",
        r"\b(?:d[ée]linquants?|d[ée]tenus?|prisonniers?|lib[ée]r[ée]s conditionnels?|suspects?|accus[ée]s?)\b",
    )),
    Rule("complainant_appellant", "Complainant, appellant or grievant", "Plaignant, appelant ou auteur d’un grief", (
        r"\b(?:complainants?|appellants?|grievors?|litigants?|respondents?)\b", r"\b(?:plaignants?|appelants?|auteurs? d.un grief|parties? au litige|intim[ée]s?)\b",
    )),
    Rule("victim_witness", "Victim or witness", "Victime ou témoin", (
        r"\b(?:victims?|witnesses?)\b", r"\b(?:victimes?|t[ée]moins?)\b",
    )),
    Rule("business_professional", "Business owner or regulated professional", "Propriétaire d’entreprise ou professionnel réglementé", (
        r"\b(?:business owners?|self-employed individuals?|regulated professionals?|licen[cs]e holders?|operators?)\b",
        r"\b(?:propri[ée]taires? d.entreprise|travailleurs? autonomes?|professionnels? r[ée]glement[ée]s?|titulaires? de permis|exploitants?)\b",
    )),
    Rule("volunteer", "Volunteer", "Bénévole", (r"\bvolunteers?\b", r"\bb[ée]n[ée]voles?\b")),
    Rule("research_participant", "Research or survey participant", "Participant à une recherche ou à un sondage", (
        r"\b(?:research|study|survey|test) participants?\b", r"\bparticipants? [àa] (?:une |la )?(?:recherche|[ée]tude|sondage|test)\b",
    )),
    Rule("artist_athlete", "Artist, athlete or cultural participant", "Artiste, athlète ou participant culturel", (
        r"\b(?:artists?|athletes?|performers?|coaches?)\b", r"\b(?:artistes?|athl[eè]tes?|artistes-interpr[eè]tes?|entra[îi]neurs?)\b",
    )),
    Rule("property_owner_tenant", "Property owner, buyer or tenant", "Propriétaire, acheteur ou locataire", (
        r"\b(?:property owners?|homeowners?|home buyers?|tenants?|landlords?)\b", r"\b(?:propri[ée]taires?|acheteurs? de maison|locataires?)\b",
    )),
    Rule("deceased_next_of_kin", "Deceased person or next of kin", "Personne décédée ou proche parent", (
        r"\b(?:deceased persons?|estates?|executors?|next of kin)\b", r"\b(?:personnes? d[ée]c[ée]d[ée]es?|successions?|ex[ée]cuteurs? testamentaires?|plus proche parent)\b",
    )),
    Rule("member_general_public", "Member of the public", "Membre du public", (
        r"\b(?:general public|members? of the public|individual Canadians?|Canadian residents?)\b",
        r"\b(?:grand public|membres? du public|Canadiens?|r[ée]sidents? canadiens?)\b",
    )),
)


ACTION_RULES = (
    Rule("applied_for_job", "Applied or was considered for a government job", "A postulé ou a été considéré pour un emploi au gouvernement", (
        r"\b(?:job|employment) applications?\b", r"\bappl(?:y|ied|ication) for (?:a )?(?:job|position|employment)\b", r"\b(?:demande|candidature) d.emploi\b",
    )),
    Rule("worked_for_government", "Worked for the government", "A travaillé pour le gouvernement", (
        r"\b(?:employee personnel record|payroll|attendance and leave|employee performance|staffing action|occupational health)\b",
        r"\b(?:dossier du personnel|paie|pr[ée]sences? et cong[ée]s?|rendement de l.employ[ée]|dotation|sant[ée] au travail)\b",
    )),
    Rule("applied_for_program", "Applied for or took part in a program", "A demandé ou participé à un programme", (
        r"\b(?:application|registration|enrolment|enrollment|participation) (?:for|in|to) (?:the |a )?(?:program|benefit|service|grant|funding|loan)\b",
        r"\b(?:demande|inscription|participation) (?:[àa]|au|dans) (?:un |le )?(?:programme|prestation|service|subvention|financement|pr[êe]t)\b",
    )),
    Rule("received_money_support", "Received or was issued money or support", "A reçu un paiement ou du soutien", (
        r"\b(?:issued|received|provide[ds]?) (?:a )?(?:payment|benefit|grant|loan|allowance|reimbursement|compensation)\b",
        r"\b(?:payment of|payment for|direct deposit|financial assistance)\b", r"\b(?:re[çc]u|vers[ée]|accord[ée])\w* (?:un |une )?(?:paiement|prestation|subvention|pr[êe]t|allocation|indemnit[ée])\b",
    )),
    Rule("owed_or_paid_money", "Owed money to or paid the government", "Devait de l’argent au gouvernement ou lui a versé un paiement", (
        r"\b(?:accounts? receivable|debt collection|money owed|amounts? due|overpayment|repay(?:ment|ing))\b",
        r"\b(?:comptes? d[ée]biteurs?|recouvrement de cr[ée]ances|sommes? dues?|trop[- ]per[çc]u|remboursement d.un pr[êe]t)\b",
    )),
    Rule("filed_tax_customs", "Filed taxes or made a customs declaration", "A produit une déclaration fiscale ou douanière", (
        r"\b(?:filed? (?:an? )?(?:income )?tax return|tax return|customs declaration|declared goods|paid dut(?:y|ies))\b",
        r"\b(?:d[ée]claration de revenus|d[ée]claration douani[eè]re|d[ée]clar[ée] des marchandises|pay[ée] des droits)\b",
    )),
    Rule("travelled_crossed_border", "Travelled, applied for a passport or crossed the border", "A voyagé, demandé un passeport ou franchi la frontière", (
        r"\b(?:passport application|travelled|traveled|crossed the border|entered canada|departed canada|port of entry|passenger data)\b",
        r"\b(?:demande de passeport|voyag[ée]|franchi la fronti[eè]re|entr[ée] au canada|quitt[ée] le canada|point d.entr[ée]|donn[ée]es sur les passagers)\b",
    )),
    Rule("immigration_process", "Used an immigration, refugee or citizenship process", "A utilisé un processus d’immigration, d’asile ou de citoyenneté", (
        r"\b(?:immigration|refugee|asylum|citizenship|permanent residence|visa) applications?\b",
        r"\bapplications? for (?:citizenship|permanent residence|a visa|refugee protection)\b",
        r"\bdemandes? (?:d.immigration|d.asile|de citoyennet[ée]|de r[ée]sidence permanente|de visa)\b",
    )),
    Rule("requested_information_privacy", "Made an access, privacy or correction request", "A présenté une demande d’accès, de confidentialité ou de correction", (
        r"\b(?:formal requests?|requests?) (?:for access|to (?:obtain|access|correct) (?:personal )?information)\b", r"\baccess to information (?:act )?(?:and privacy act )?requests?\b",
        r"\bdemandes? (?:officielles? )?(?:d.acc[eè]s|de correction)\b",
    )),
    Rule("submitted_complaint_appeal", "Made a complaint, grievance or appeal", "A présenté une plainte, un grief ou un appel", (
        r"\b(?:filed?|made|submitted|lodged) (?:a )?(?:complaint|grievance|appeal)\b", r"\bcomplaints? (?:made|submitted|filed) by\b",
        r"\b(?:d[ée]pos[ée]|pr[ée]sent[ée]|formul[ée])\w* (?:une )?(?:plainte|grief|appel)\b",
    )),
    Rule("contracted_supplied", "Contracted with or supplied the government", "A conclu un marché avec le gouvernement ou lui a fourni des biens ou services", (
        r"\b(?:awarded contracts?|contracted with|provided (?:goods|services)|submitted bids?|procurement process)\b",
        r"\b(?:march[ée]s? attribu[ée]s?|fourni des (?:biens|services)|soumis? une offre|processus d.approvisionnement)\b",
    )),
    Rule("obtained_licence_permit", "Applied for or held a licence, permit or registration", "A demandé ou détenu une licence, un permis ou une inscription", (
        r"\b(?:appl(?:y|ied|ication) for|holders? of|issued) (?:a |an )?(?:licen[cs]e|permit|registration|certificate)\b",
        r"\b(?:demande|titulaire|d[ée]livrance) d.(?:une )?(?:licence|permis|inscription|certificat)\b",
    )),
    Rule("received_health_disability_service", "Received a health or disability-related service", "A reçu un service lié à la santé ou à l’invalidité", (
        r"\b(?:received|provided|delivery of) (?:medical|health|dental|disability|rehabilitation) (?:care|services?|benefits?|support)\b",
        r"\b(?:re[çc]u|fourni)\w* (?:des )?(?:soins|services|prestations) (?:m[ée]dicaux|de sant[ée]|dentaires|d.invalidit[ée]|de r[ée]adaptation)\b",
    )),
    Rule("studied_trained", "Studied, trained or received student aid", "A étudié, suivi une formation ou reçu de l’aide aux étudiants", (
        r"\b(?:student loan application|student financial assistance|enrolled in (?:a )?(?:school|course|training)|training participant)\b",
        r"\b(?:demande de pr[êe]t [ée]tudiant|aide financi[eè]re aux [ée]tudiants|inscrit [àa] (?:une )?(?:[ée]cole|formation)|participant [àa] la formation)\b",
    )),
    Rule("law_enforcement_corrections", "Was involved in a law-enforcement or correctional matter", "A été impliqué dans une affaire policière ou correctionnelle", (
        r"\b(?:arrested|detained|incarcerated|investigated|charged|convicted|on parole|under probation)\b",
        r"\b(?:arr[êe]t[ée]|d[ée]tenu|incarc[ée]r[ée]|fait l.objet d.une enqu[êe]te|accus[ée]|condamn[ée]|en libert[ée] conditionnelle)\w*\b",
    )),
    Rule("served_military", "Served in the Canadian Armed Forces", "A servi dans les Forces armées canadiennes", (
        r"\b(?:served|service) (?:in|with) (?:the )?(?:canadian )?(?:armed )?forces\b", r"\bcanadian armed forces service\b",
        r"\bservi dans les forces arm[ée]es canadiennes\b",
    )),
    Rule("participated_research_survey", "Took part in research, a survey or testing", "A participé à une recherche, un sondage ou un test", (
        r"\bparticipat(?:e|ed|ion) in (?:a |the )?(?:research|study|survey|test|focus group)\b",
        r"\bparticip[ée] [àa] (?:une |la )?(?:recherche|[ée]tude|sondage|test|groupe de discussion)\b",
    )),
    Rule("volunteered_participated_event", "Volunteered or participated in a public event", "A fait du bénévolat ou participé à un événement public", (
        r"\b(?:volunteer (?:activities|registration)|registered as a volunteer|event participants?)\b",
        r"\b(?:activit[ée]s? de b[ée]n[ée]volat|inscription (?:des |comme )?b[ée]n[ée]voles?|participants? [àa] (?:un )?[ée]v[ée]nement)\b",
    )),
    Rule("contacted_government", "Contacted government or joined an engagement activity", "A communiqué avec le gouvernement ou participé à une activité de mobilisation", (
        r"\b(?:submitted|sent|made) (?:an? )?(?:inquiry|correspondence|letter|email|petition)\b", r"\b(?:subscribed|registered) (?:to|for) (?:a )?(?:mailing list|newsletter|consultation)\b",
        r"\b(?:envoy[ée]|soumis|pr[ée]sent[ée])\w* (?:une )?(?:demande de renseignements|lettre|courriel|p[ée]tition)\b",
    )),
)


QUESTION_GROUPS = (
    QuestionGroup("q_government_work", "Have you ever applied to work for, worked for, or received an employment-related service from the Government of Canada?", "Avez-vous déjà postulé ou travaillé au gouvernement du Canada, ou reçu un service lié à cet emploi?", ("government_employment",), ("government_employee", "job_applicant"), ("applied_for_job", "worked_for_government")),
    QuestionGroup("q_money_programs", "Have you ever applied for or received a federal benefit, grant, loan, reimbursement or other payment?", "Avez-vous déjà demandé ou reçu une prestation, une subvention, un prêt, un remboursement ou un autre paiement fédéral?", ("benefits_support", "grants_contributions", "payments_debt"), ("program_applicant_recipient",), ("applied_for_program", "received_money_support", "owed_or_paid_money")),
    QuestionGroup("q_tax_customs", "Have you filed federal taxes, paid federal duties, or made a customs declaration?", "Avez-vous produit une déclaration de revenus fédérale, payé des droits fédéraux ou fait une déclaration douanière?", ("tax_customs_duties",), (), ("filed_tax_customs",)),
    QuestionGroup("q_immigration", "Have you used a Canadian immigration, refugee, visa, permanent-residence or citizenship process?", "Avez-vous utilisé un processus canadien d’immigration, d’asile, de visa, de résidence permanente ou de citoyenneté?", ("immigration_citizenship",), ("immigrant_refugee_newcomer",), ("immigration_process",)),
    QuestionGroup("q_travel_border", "Have you applied for a Canadian passport, crossed Canada’s border, or joined a trusted-traveller program?", "Avez-vous demandé un passeport canadien, franchi la frontière canadienne ou adhéré à un programme de voyageurs dignes de confiance?", ("travel_border",), ("traveller",), ("travelled_crossed_border",)),
    QuestionGroup("q_health_disability", "Have you received a federal health, dental, rehabilitation, disability or medical-device service?", "Avez-vous reçu un service fédéral de santé, de soins dentaires, de réadaptation, d’invalidité ou d’appareil médical?", ("health_disability",), ("patient_disabled_person",), ("received_health_disability_service",)),
    QuestionGroup("q_indigenous_services", "Have you used a federal service specifically for First Nations, Inuit or Métis people?", "Avez-vous utilisé un service fédéral destiné précisément aux membres des Premières Nations, aux Inuit ou aux Métis?", ("indigenous_services",), ("indigenous_person",)),
    QuestionGroup("q_military_veterans", "Have you served in the Canadian Armed Forces or used a federal veterans program?", "Avez-vous servi dans les Forces armées canadiennes ou utilisé un programme fédéral pour les vétérans?", ("veterans_military",), ("veteran_service_member",), ("served_military",)),
    QuestionGroup("q_education_training", "Have you applied for federal student aid, an apprenticeship, scholarship or training program?", "Avez-vous demandé une aide fédérale aux étudiants, un apprentissage, une bourse ou un programme de formation?", ("education_training",), ("student_learner",), ("studied_trained",)),
    QuestionGroup("q_justice_safety", "Have you been involved in a matter handled by federal law enforcement, security screening or corrections?", "Avez-vous été impliqué dans une affaire relevant de l’application de la loi fédérale, du filtrage de sécurité ou des services correctionnels?", ("justice_public_safety",), ("justice_involved", "victim_witness"), ("law_enforcement_corrections",)),
    QuestionGroup("q_complaint_appeal", "Have you made a complaint, grievance or appeal to a federal institution or tribunal?", "Avez-vous présenté une plainte, un grief ou un appel à une institution ou à un tribunal fédéral?", ("complaints_appeals_legal",), ("complainant_appellant",), ("submitted_complaint_appeal",)),
    QuestionGroup("q_access_privacy", "Have you made an access-to-information, personal-information access, or correction request?", "Avez-vous présenté une demande d’accès à l’information, d’accès à vos renseignements personnels ou de correction?", ("access_privacy",), (), ("requested_information_privacy",)),
    QuestionGroup("q_business_supplier", "Have you owned or operated a business, held a federal licence or permit, or contracted with the federal government?", "Avez-vous possédé ou exploité une entreprise, détenu une licence ou un permis fédéral, ou conclu un marché avec le gouvernement fédéral?", ("contracts_procurement", "business_regulation", "transport_licensing"), ("contractor_supplier", "business_professional"), ("contracted_supplied", "obtained_licence_permit")),
    QuestionGroup("q_firearms", "Have you applied for, renewed or held a Canadian firearms licence, or registered a restricted firearm?", "Avez-vous demandé, renouvelé ou détenu un permis canadien d'armes à feu, ou enregistré une arme à feu à autorisation restreinte?"),
    QuestionGroup("q_boating", "Have you held a Pleasure Craft Operator Card or licensed or registered a boat with Transport Canada?", "Avez-vous détenu une carte de conducteur d'embarcation de plaisance, ou obtenu un permis ou une immatriculation pour un bateau auprès de Transports Canada?"),
    QuestionGroup("q_housing_property", "Have you used a federal housing, mortgage, home-buying or property program?", "Avez-vous utilisé un programme fédéral de logement, d’hypothèque, d’achat d’une maison ou de propriété?", ("housing_property",), ("property_owner_tenant",)),
    QuestionGroup("q_civic_contact", "Have you contacted a federal institution, joined a consultation, signed a petition, or participated in a federal election process?", "Avez-vous communiqué avec une institution fédérale, participé à une consultation, signé une pétition ou pris part à un processus électoral fédéral?", ("communications_engagement", "democratic_civic"), (), ("contacted_government",)),
    QuestionGroup("q_culture_volunteer", "Have you participated in or volunteered for a federally run cultural, sport, recreation, heritage or park activity?", "Avez-vous participé ou fait du bénévolat à une activité fédérale de culture, de sport, de loisir, de patrimoine ou de parc?", ("culture_recreation_volunteering",), ("volunteer", "artist_athlete"), ("volunteered_participated_event",)),
    QuestionGroup("q_research_survey", "Have you taken part in federal research, a survey, testing or a focus group?", "Avez-vous participé à une recherche, un sondage, un test ou un groupe de discussion du gouvernement fédéral?", ("research_surveys",), ("research_participant",), ("participated_research_survey",)),
    QuestionGroup("q_emergency", "Have you requested or received federal help during an emergency, evacuation or disaster?", "Avez-vous demandé ou reçu de l’aide fédérale lors d’une urgence, d’une évacuation ou d’une catastrophe?", ("emergency_assistance",)),
    QuestionGroup("q_family_vital", "Have you used a federal service involving a birth, marriage, divorce, adoption, child support, death or estate?", "Avez-vous utilisé un service fédéral concernant une naissance, un mariage, un divorce, une adoption, une pension alimentaire, un décès ou une succession?", ("family_vital_events",), ("family_dependent", "deceased_next_of_kin")),
)


_COMPILED: dict[tuple[str, str], tuple[Pattern[str], ...]] = {}
_HINT_CACHE: dict[tuple[str, str], tuple[str, ...]] = {}


def _patterns(rule: Rule) -> tuple[Pattern[str], ...]:
    key = (rule.code, "|".join(rule.patterns))
    if key not in _COMPILED:
        _COMPILED[key] = tuple(re.compile(pattern, re.IGNORECASE) for pattern in rule.patterns)
    return _COMPILED[key]


def _hints(rule: Rule) -> tuple[str, ...]:
    """Extract safe literal pre-filters from the regular expressions.

    Every expression in this taxonomy contains at least one four-character
    literal.  Testing those cheap substrings first avoids repeatedly running
    dozens of regular expressions across the corpus's multi-kilobyte fields.
    The regex remains the authority; hints can only reject impossible matches.
    """
    key = (rule.code, "|".join(rule.patterns))
    if key not in _HINT_CACHE:
        values = {
            token.casefold()
            for pattern in rule.patterns
            for token in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", pattern)
        }
        _HINT_CACHE[key] = tuple(sorted(values, key=lambda value: (-len(value), value)))
    return _HINT_CACHE[key]


def _canonical_fields(record: Mapping[str, object]) -> dict[str, str]:
    """Return relevant bilingual fields under one schema-neutral vocabulary."""
    text = lambda key: str(record.get(key) or "").strip()
    return {
        "title_en": text("title_en") or text("entry_title_en"),
        "title_fr": text("title_fr") or text("entry_title_fr"),
        "class_of_individuals_en": text("class_of_individuals_en"),
        "class_of_individuals_fr": text("class_of_individuals_fr"),
        "purpose_en": text("purpose_en"),
        "purpose_fr": text("purpose_fr"),
        "description_en": text("description_en"),
        "description_fr": text("description_fr"),
        "consistent_uses_en": text("consistent_uses_en"),
        "consistent_uses_fr": text("consistent_uses_fr"),
        "note_en": text("note_en"),
        "note_fr": text("note_fr"),
        "institution_name_en": text("institution_name_en"),
        "institution_name_fr": text("institution_name_fr"),
    }


def _excerpt(text: str, start: int, end: int, radius: int = 68) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    value = re.sub(r"\s+", " ", text[left:right]).strip()
    return ("…" if left else "") + value + ("…" if right < len(text) else "")


def _match_rules(fields: Mapping[str, str], rules: Sequence[Rule]) -> list[dict[str, object]]:
    features: list[dict[str, object]] = []
    # The bilingual descriptions are translations of the same inventory text.
    # Prefer English when present and use French as a field-by-field fallback;
    # scanning both adds duplicate evidence without strengthening the inference.
    folded_fields = {
        field: text.casefold()
        for field, text in fields.items()
        if text and not (
            field.endswith("_fr") and fields.get(field[:-3] + "_en", "")
        )
    }
    for rule in rules:
        evidence: list[dict[str, object]] = []
        seen: set[tuple[str, int, int]] = set()
        for field, folded_text in folded_fields.items():
            text = fields[field]
            if not any(hint in folded_text for hint in _hints(rule)):
                continue
            for pattern in _patterns(rule):
                match = pattern.search(text)
                if not match:
                    continue
                marker = (field, match.start(), match.end())
                if marker in seen:
                    continue
                seen.add(marker)
                evidence.append({
                    "field": field,
                    "matched_text": match.group(0),
                    "excerpt": _excerpt(text, match.start(), match.end()),
                    "field_confidence": FIELD_CONFIDENCE[field],
                })
                break  # one independently reviewable match per field is enough
        if evidence:
            evidence.sort(key=lambda item: (-float(item["field_confidence"]), str(item["field"])))
            distinct_fields = len({str(item["field"]) for item in evidence})
            confidence = min(0.99, float(evidence[0]["field_confidence"]) + 0.02 * (distinct_fields - 1))
            features.append({
                "code": rule.code,
                "label_en": rule.label_en,
                "label_fr": rule.label_fr,
                "confidence": round(confidence, 2),
                "evidence": evidence[:4],
            })
    return sorted(features, key=lambda item: (-float(item["confidence"]), str(item["code"])))


def _record_key(record: Mapping[str, object]) -> str:
    return str(
        record.get("bank_number_key")
        or record.get("bank_number_en")
        or record.get("entry_id_en")
        or ""
    ).strip()


def _source_kind(record: Mapping[str, object], supplied: str | None) -> str:
    if supplied:
        return supplied
    return "institution_pib" if record.get("institution_id") else "standard_pib"


def _question_triggers(
    topics: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
    actions: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    feature_maps = {
        "topic": {str(item["code"]): item for item in topics},
        "role": {str(item["code"]): item for item in roles},
        "action": {str(item["code"]): item for item in actions},
    }
    triggers: list[dict[str, object]] = []
    for question in QUESTION_GROUPS:
        basis: list[dict[str, object]] = []
        for family, codes in (
            ("topic", question.topic_codes),
            ("role", question.role_codes),
            ("action", question.action_codes),
        ):
            for code in codes:
                feature = feature_maps[family].get(code)
                if feature:
                    basis.append({
                        "feature_type": family,
                        "feature_code": code,
                        "confidence": feature["confidence"],
                    })
        if basis:
            confidence = max(float(item["confidence"]) for item in basis)
            triggers.append({
                "code": question.code,
                "question_en": question.question_en,
                "question_fr": question.question_fr,
                "ask_when_matched_en": "If yes: About what year did this interaction last happen?",
                "ask_when_matched_fr": "Si oui : Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois?",
                "confidence": round(confidence, 2),
                "trigger_basis": basis,
            })
    return sorted(triggers, key=lambda item: (-float(item["confidence"]), str(item["code"])))


def _primary_question_triggers(
    candidate_triggers: Sequence[Mapping[str, object]],
    topics: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
    actions: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Remove content-only matches that should not drive a citizen question.

    PIB descriptions often enumerate information such as passports, tax details,
    medical information, or relatives even when the actual interaction is simply
    government employment. Those remain useful candidate evidence, but a question
    becomes primary only with a direct service action, title-level topic evidence,
    or compatible topic-and-role evidence.
    """

    feature_maps = {
        "topic": {str(item["code"]): item for item in topics},
        "role": {str(item["code"]): item for item in roles},
        "action": {str(item["code"]): item for item in actions},
    }

    def evidence_fields(feature: Mapping[str, object]) -> set[str]:
        return {str(item["field"]) for item in feature.get("evidence", [])}

    primary: list[dict[str, object]] = []
    for trigger in candidate_triggers:
        bases = list(trigger.get("trigger_basis") or [])
        selected = [
            (str(basis["feature_type"]), feature_maps[str(basis["feature_type"])].get(str(basis["feature_code"])))
            for basis in bases
        ]
        selected = [(family, feature) for family, feature in selected if feature]
        direct_action = any(
            family == "action"
            and float(feature["confidence"]) >= 0.84
            and evidence_fields(feature) & {
                "title_en", "title_fr", "class_of_individuals_en", "class_of_individuals_fr",
                "purpose_en", "purpose_fr", "description_en", "description_fr",
            }
            for family, feature in selected
        )
        title_topic = any(
            family == "topic"
            and evidence_fields(feature) & {"title_en", "title_fr"}
            for family, feature in selected
        )
        contextual_topic = any(
            family == "topic"
            and float(feature["confidence"]) >= 0.84
            and evidence_fields(feature) & {"title_en", "title_fr", "purpose_en", "purpose_fr"}
            for family, feature in selected
        )
        compatible_role = any(
            family == "role"
            and float(feature["confidence"]) >= 0.84
            and evidence_fields(feature) & {
                "title_en", "title_fr", "class_of_individuals_en", "class_of_individuals_fr",
            }
            for family, feature in selected
        )
        if direct_action or title_topic or (contextual_topic and compatible_role):
            primary.append(dict(trigger))
    return primary


def _caveats(
    fields: Mapping[str, str],
    topics: Sequence[Mapping[str, object]],
    roles: Sequence[Mapping[str, object]],
) -> list[dict[str, str]]:
    combined = " ".join(fields.values())
    role_codes = {str(item["code"]) for item in roles}
    topic_codes = {str(item["code"]) for item in topics}
    caveats: list[dict[str, str]] = []
    if "member_general_public" in role_codes:
        caveats.append({
            "code": "broad_population",
            "message_en": "The PIB describes the general public or another broad population; a topic answer is only a screening signal.",
            "message_fr": "Le FRP décrit le grand public ou une autre vaste population; une réponse thématique n’est qu’un signal de présélection.",
        })
    if role_codes & {"representative_guardian", "family_dependent", "victim_witness", "deceased_next_of_kin"}:
        caveats.append({
            "code": "possible_third_party_information",
            "message_en": "The PIB can contain information about representatives, relatives, dependants, victims, witnesses or other third parties who did not apply directly.",
            "message_fr": "Le FRP peut contenir des renseignements sur des représentants, proches, personnes à charge, victimes, témoins ou autres tiers qui n’ont pas présenté directement une demande.",
        })
    if re.search(r"\b(?:share[ds]?|disclos(?:e|ed|ure)|transfer(?:red)?|provided to another|communiqu[ée]s?|divulgu[ée]s?|transf[ée]r[ée]s?)\b", " ".join((fields["consistent_uses_en"], fields["consistent_uses_fr"])), re.I):
        caveats.append({
            "code": "possible_sharing",
            "message_en": "The consistent-uses text indicates that information may be shared or disclosed; related PIBs may also need to be considered.",
            "message_fr": "Le texte sur les usages compatibles indique que des renseignements peuvent être communiqués; des FRP connexes peuvent aussi devoir être examinés.",
        })
    if re.search(r"\b(?:ended|terminated|discontinued|no longer active|formerly|termin[ée]|abandonn[ée]|n.est plus actif|anciennement)\b", " ".join((fields["note_en"], fields["note_fr"])), re.I):
        caveats.append({
            "code": "historical_or_ended_bank",
            "message_en": "The source describes this bank as ended, discontinued or former. Apply its retention text before suggesting that records are still held.",
            "message_fr": "La source décrit ce FRP comme terminé, abandonné ou ancien. Il faut appliquer son texte de conservation avant de suggérer que les documents existent encore.",
        })
    if topic_codes & {"health_disability", "justice_public_safety"} or re.search(r"\b(?:social insurance number|sin|biometric|dna|medical diagnosis|security clearance|criminal record|num[ée]ro d.assurance sociale|biom[ée]trique|casier judiciaire)\b", combined, re.I):
        caveats.append({
            "code": "sensitive_context",
            "message_en": "This candidate involves potentially sensitive information. The questionnaire should use optional, non-stigmatizing wording and avoid collecting unnecessary details.",
            "message_fr": "Ce résultat potentiel concerne des renseignements possiblement sensibles. Le questionnaire devrait employer un libellé facultatif et non stigmatisant, sans recueillir de détails inutiles.",
        })
    return caveats


def derive_interaction_features(
    record: Mapping[str, object], *, source_kind: str | None = None
) -> dict[str, object]:
    """Derive auditable questionnaire features for one SPIB or institution PIB."""
    fields = _canonical_fields(record)
    topics = _match_rules(fields, TOPIC_RULES)
    roles = _match_rules(fields, ROLE_RULES)
    actions = _match_rules(fields, ACTION_RULES)
    triggers = _question_triggers(topics, roles, actions)
    primary_triggers = _primary_question_triggers(triggers, topics, roles, actions)
    return {
        "record_id": str(record.get("record_id") or _record_key(record)),
        "record_key": _record_key(record),
        "source_kind": _source_kind(record, source_kind),
        "interaction_topics": topics,
        "individual_roles": roles,
        "service_actions": actions,
        "question_triggers": triggers,
        "primary_question_triggers": primary_triggers,
        "privacy_caveats": _caveats(fields, topics, roles),
        "derivation": {
            "method": "deterministic_regex_v1",
            "holding_inference": "candidate_only",
            "time_follow_up_required": bool(primary_triggers),
        },
    }


def derive_many(
    records: Iterable[Mapping[str, object]], *, source_kind: str | None = None
) -> list[dict[str, object]]:
    return [derive_interaction_features(record, source_kind=source_kind) for record in records]


def questionnaire_questions() -> list[dict[str, object]]:
    """Return the stable, bilingual survey contract for a UI or agent.

    Examples and readability results are presentation metadata.  They never
    participate in PIB matching, so showing help cannot change a result.
    """

    # Local imports keep the matching taxonomy usable on its own and avoid
    # making progressive-help content part of the derivation rules.
    from .question_examples import help_for_question
    from .readability import PROPOSED_QUESTION_WORDING_EN, flesch_reading_ease

    rows: list[dict[str, object]] = []
    for item in QUESTION_GROUPS:
        help_text = help_for_question(item.code)
        current = flesch_reading_ease(item.question_en)
        candidate_question = PROPOSED_QUESTION_WORDING_EN.get(item.code, item.question_en)
        candidate = flesch_reading_ease(candidate_question)
        if help_text.familiarity == "unfamiliar":
            web_display = "inline"
            agent_offer = "proactive"
        elif help_text.familiarity == "mixed":
            web_display = "collapsed"
            agent_offer = "on_hesitation"
        else:
            web_display = "on_request"
            agent_offer = "on_request"

        rows.append({
            "code": item.code,
            "question_en": item.question_en,
            "question_fr": item.question_fr,
            "answer": {
                "type": "single_select",
                "values": ["yes", "no", "not_sure", "prefer_not_to_answer"],
            },
            "timing": {
                "ask_after": ["yes"],
                "response_type": "approximate_period_or_year",
                "prompt_en": "About what year did this interaction last happen?",
                "prompt_fr": "Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois?",
            },
            # Keep the legacy prompt fields during the contract transition.
            "ask_when_matched_en": "If yes: About what year did this interaction last happen?",
            "ask_when_matched_fr": "Si oui : Vers quelle année cette interaction a-t-elle eu lieu pour la dernière fois?",
            "readability_en": {
                "method": "flesch_reading_ease",
                "score": current.score,
                "band": current.band,
                "outlier_below_60": current.is_outlier,
                "candidate_question_en": candidate_question,
                "candidate_score": candidate.score,
                "candidate_band": candidate.band,
                # Readability alone cannot detect a semantically compound gate.
                # Preserve the independently reviewed routing recommendation.
                "adaptive_split_recommended": bool(help_text.split_recommendation_en),
            },
            "help": {
                "familiarity": help_text.familiarity,
                "web_display": web_display,
                "agent_offer": agent_offer,
                "examples": [
                    {
                        "institution_en": example.institution_en,
                        "institution_fr": example.institution_fr,
                        "activity_en": example.activity_en,
                        "activity_fr": example.activity_fr,
                        "source_pib_keys": list(example.pib_keys),
                        "evidence_note_en": example.evidence_note_en,
                        "evidence_note_fr": example.evidence_note_fr,
                    }
                    for example in help_text.examples
                ],
                "split_recommendation_en": help_text.split_recommendation_en,
                "split_recommendation_fr": help_text.split_recommendation_fr,
            },
        })
    return rows


def coverage_report(
    features: Iterable[Mapping[str, object]],
    *,
    question_field: str = "question_triggers",
) -> dict[str, object]:
    """Summarize corpus coverage and surface records requiring taxonomy review."""
    rows = list(features)
    unmatched: list[str] = []
    weak: list[str] = []
    topic_counts: Counter[str] = Counter()
    question_counts: Counter[str] = Counter()
    for row in rows:
        topics = list(row.get("interaction_topics") or [])
        if question_field in row:
            questions = list(row.get(question_field) or [])
        else:
            questions = list(row.get("question_triggers") or [])
        if not questions:
            unmatched.append(str(row.get("record_id") or row.get("record_key") or ""))
        if questions and max(float(item.get("confidence", 0)) for item in questions) < 0.84:
            weak.append(str(row.get("record_id") or row.get("record_key") or ""))
        topic_counts.update(str(item["code"]) for item in topics)
        question_counts.update(str(item["code"]) for item in questions)
    matched = len(rows) - len(unmatched)
    return {
        "record_count": len(rows),
        "matched_question_count": matched,
        "matched_question_rate": round(matched / len(rows), 4) if rows else 0.0,
        "unmatched_record_keys": unmatched,
        "weak_record_keys": weak,
        "topic_counts": dict(sorted(topic_counts.items())),
        "question_counts": dict(sorted(question_counts.items())),
    }
