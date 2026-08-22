"""Evidence-based assignment of the official personal-information categories.

The source PIB descriptions often enumerate their data elements using the same
labels as ``pi_categories_en_fr.csv``.  This module deliberately favours those
explicit labels and narrow, bilingual examples over broad topical inference.
Every assignment therefore retains the source field and matched text that made
the rule fire.  Concepts present in PIB text but absent from the 25-row English
taxonomy are reported separately instead of being forced into a category.
"""

from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Mapping, Pattern

from .model import PibRecord


DEFAULT_CATEGORY_PATH = Path(__file__).resolve().parents[1] / "pi_categories_en_fr.csv"


@dataclass(frozen=True)
class CategoryDefinition:
    category_id: str
    name_en: str
    name_fr: str
    examples_en: str
    examples_fr: str


@dataclass(frozen=True)
class CategoryEvidence:
    """One inspectable text match supporting an assignment."""

    field: str
    language: str
    matched_text: str
    rule: str
    confidence: float


@dataclass(frozen=True)
class CategoryAssignment:
    category_id: str
    name_en: str
    name_fr: str
    confidence: float
    evidence: tuple[CategoryEvidence, ...]


@dataclass(frozen=True)
class UnmappedEvidence:
    """A source concept for which the official 25-category list has no match."""

    concept: str
    field: str
    language: str
    matched_text: str


@dataclass(frozen=True)
class RecordCategoryResult:
    record_id: str
    assignments: tuple[CategoryAssignment, ...]
    ambiguous: bool
    unclassified: bool
    ambiguity_reasons: tuple[str, ...]
    unmapped_evidence: tuple[UnmappedEvidence, ...]

    @property
    def category_ids(self) -> tuple[str, ...]:
        return tuple(assignment.category_id for assignment in self.assignments)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation for derived datasets."""

        result = asdict(self)
        result["category_ids"] = list(self.category_ids)
        return result


@dataclass(frozen=True)
class _Rule:
    category_id: str
    rule: str
    confidence: float
    en: tuple[str, ...] = ()
    fr: tuple[str, ...] = ()


@dataclass(frozen=True)
class _CompiledRule:
    category_id: str
    rule: str
    confidence: float
    language: str
    patterns: tuple[Pattern[str], ...]


def _enumerated(term: str, *, french: bool = False) -> str:
    """Constrain a short/generic term to a personal-information list."""

    if french:
        anchor = (
            r"(?:renseignements personnels|cat[ée]gories de renseignements|"
            r"donn[ée]es personnelles)"
        )
    else:
        anchor = (
            r"(?:personal information|categories of personal information|"
            r"personal data elements)"
        )
    return rf"{anchor}[^.!?]{{0,1800}}?(?P<evidence>{term})"


# Rules are intentionally conservative.  Exact taxonomy labels generally score
# 1.0.  Precise examples score 0.90-0.95.  Historically overloaded labels such
# as "credit information" are retained at lower confidence and flag the record.
_RULES: tuple[_Rule, ...] = (
    _Rule(
        "PI_CAT-1",
        "explicit biographical information",
        1.0,
        (r"\bbiographical information\b",),
        (r"\brenseignements biographiques\b",),
    ),
    _Rule(
        "PI_CAT-1",
        "biographical example",
        0.90,
        (
            r"\b(?:curricul(?:um vitae|a vitae)|work history|employment history|family information|family data|marital status|hobbies and interests)\b",
            r"\bdata on (?:their )?children\b",
        ),
        (
            r"\b(?:curriculum vit[æe]|ant[ée]c[ée]dents professionnels|renseignements sur la famille|donn[ée]es familiales|[ée]tat matrimonial|passe[- ]temps)\b",
            r"\bdonn[ée]es (?:sur|concernant) (?:leurs?|ses) enfants\b",
        ),
    ),
    _Rule(
        "PI_CAT-2",
        "explicit biometric information",
        1.0,
        (r"\bbiometric (?:information|data)\b",),
        (r"\bdonn[ée]es biom[ée]triques\b|\brenseignements biom[ée]triques\b",),
    ),
    _Rule(
        "PI_CAT-2",
        "biometric identifier",
        0.95,
        (
            r"\b(?:fingerprints?|finger prints?|hand prints?|palm prints?|DNA|iris scan|retina(?:l)? scan|facial recognition|voiceprints?|blood type)\b",
        ),
        (
            r"\b(?:empreintes? digitales?|empreintes? de (?:la )?main|empreintes? palmaires?|ADN|balayage (?:oculaire|de l['’]iris)|reconnaissance faciale|empreintes? vocales?|groupe sanguin)\b",
        ),
    ),
    _Rule(
        "PI_CAT-3",
        "explicit contact information",
        1.0,
        (r"\bcontact information\b",),
        (r"\bcoordonn[ée]es\b",),
    ),
    _Rule(
        "PI_CAT-3",
        "contact detail",
        0.92,
        (
            r"\b(?:mailing|postal|residential|home|work|e-?mail) address(?:es)?\b",
            r"\b(?:telephone|phone|fax|cell(?:ular)? phone|mobile phone) number(?:s)?\b",
            r"\bnames? and addresses?\b|\baddresses? and (?:telephone|phone) numbers?\b",
        ),
        (
            r"\badresse(?:s)? (?:postale(?:s)?|r[ée]sidentielle(?:s)?|personnelle(?:s)?|professionnelle(?:s)?|[ée]lectronique(?:s)?)\b",
            r"\bnum[ée]ro(?:s)? de (?:t[ée]l[ée]phone|t[ée]l[ée]copieur|cellulaire)\b",
            r"\bnoms? et adresses?\b|\badresses? et num[ée]ros? de t[ée]l[ée]phone\b",
        ),
    ),
    _Rule(
        "PI_CAT-4",
        "citizenship or immigration status",
        0.97,
        (
            r"\b(?:citizenship status|citizenship information|citizenship data|immigration status|nationality|landed immigrant|permanent resident status)\b",
        ),
        (
            r"\b(?:statut de citoyennet[ée]|renseignements sur la citoyennet[ée]|donn[ée]es sur la citoyennet[ée]|statut d['’]immigration|nationalit[ée]|immigrant re[çc]u|statut de r[ée]sident permanent)\b",
        ),
    ),
    _Rule(
        "PI_CAT-5",
        "credit or payment card information",
        0.98,
        (
            r"\b(?:credit|debit|payment) card (?:information|details|number|numbers|data)\b",
            r"\bcredit card\b",
            r"\bcard ?holder['’]s name\b",
        ),
        (
            r"\brenseignements (?:ayant trait|relatifs?) [àa] (?:une|la) carte de cr[ée]dit\b",
            r"\b(?:num[ée]ro|renseignements) de carte de (?:cr[ée]dit|d[ée]bit)\b",
        ),
    ),
    _Rule(
        "PI_CAT-6",
        "explicit credit history",
        1.0,
        (r"\bcredit history\b",),
        (r"\bant[ée]c[ée]dents en mati[èe]re de cr[ée]dit\b",),
    ),
    _Rule(
        "PI_CAT-6",
        "credit assessment information",
        0.79,
        (
            r"\bcredit information\b",
            r"\b(?:credit reports?|credit scores?|credit checks?|credit bureaus?|bankruptc(?:y|ies)|third[- ]party collections?)\b",
        ),
        (
            r"\brenseignements (?:sur|relatifs? au) cr[ée]dit\b",
            r"\b(?:rapports? de solvabilit[ée]|cotes? de cr[ée]dit|v[ée]rifications? de cr[ée]dit|bureaux? de cr[ée]dit|faillites?|recouvrements? par un tiers)\b",
        ),
    ),
    _Rule(
        "PI_CAT-7",
        "criminal check or history",
        0.99,
        (
            r"\b(?:criminal (?:checks?|record checks?|history|records?|charges?|convictions?)|criminal checks?/history|law enforcement record checks?|police record checks?|pardons?)\b",
        ),
        (
            r"\b(?:v[ée]rifications? (?:de|du) casier judiciaire|ant[ée]c[ée]dents criminels?|casiers? judiciaires?|accusations? criminelles?|condamnations?|v[ée]rifications? des dossiers? de la police|pardons?)\b",
        ),
    ),
    _Rule(
        "PI_CAT-8",
        "date of birth",
        1.0,
        (r"\b(?:date of birth|birth date)\b",),
        (r"\bdate de naissance\b",),
    ),
    _Rule(
        "PI_CAT-9",
        "date of death",
        1.0,
        (r"\bdate of death\b",),
        (r"\bdate (?:du|de) d[ée]c[èe]s\b",),
    ),
    _Rule(
        "PI_CAT-10",
        "employee identification number",
        1.0,
        (
            r"\bemployee identification numbers?\b",
            r"\b(?:personal record identifier|personnel record identifier|RCMP regimental number|Canadian Forces service number)\b",
            r"\bunique employee number\b",
        ),
        (
            r"\bnum[ée]ros? d['’]identification d['’]employ[ée]\b",
            r"\b(?:code d['’]identification de dossier personnel|num[ée]ro matricule (?:de la GRC|des Forces canadiennes))\b",
        ),
    ),
    _Rule(
        "PI_CAT-11",
        "employment equity information",
        1.0,
        (r"\bemployment equity information\b|\bemployee equity information\b|\bemployment equity groups?\b",),
        (r"\brenseignements sur l['’][ée]quit[ée] en mati[èe]re d['’]emploi\b|\bgroupes? vis[ée]s? par l['’][ée]quit[ée] en mati[èe]re d['’]emploi\b",),
    ),
    _Rule(
        "PI_CAT-12",
        "explicit employee personnel information",
        1.0,
        (r"\bemployee personnel information\b|\bemployee information\b",),
        (r"\brenseignements personnels de l['’]employ[ée]\b|\brenseignements sur (?:les )?employ[ée]s\b",),
    ),
    _Rule(
        "PI_CAT-12",
        "employee personnel record",
        0.90,
        (
            r"\b(?:attendance and leave|leave records?|disciplinary action|performance (?:reviews?|appraisals?)|security clearance|alternative work arrangements?|training and development)\b",
            r"\b(?:personnel files?|employee records?|salary information)\b",
        ),
        (
            r"\b(?:pr[ée]sences? et (?:des )?cong[ée]s|mesures? disciplinaires?|examens? du rendement|[ée]valuations? du rendement|cote de s[ée]curit[ée]|r[ée]gimes? de travail non conventionnels?|formation et perfectionnement)\b",
            r"\b(?:dossiers? du personnel|dossiers? d['’]employ[ée]s|renseignements sur le salaire)\b",
        ),
    ),
    _Rule(
        "PI_CAT-13",
        "explicit financial information",
        1.0,
        (r"\bfinancial information\b",),
        (r"\brenseignements financiers\b",),
    ),
    _Rule(
        "PI_CAT-13",
        "financial account or asset",
        0.93,
        (
            r"\b(?:bank account|account numbers?|direct deposit|mortgages?|investments?|garnishment|financial institution information)\b",
        ),
        (
            r"\b(?:compte bancaire|num[ée]ros? de compte|d[ée]p[ôo]t direct|hypoth[èe]ques?|investissements?|saisie-arr[êe]t|renseignements sur l['’]institution financi[èe]re)\b",
        ),
    ),
    _Rule(
        "PI_CAT-14",
        "gender",
        0.99,
        (r"\bgender\b|\bsex/gender\b", _enumerated(r"\bsex\b")),
        (r"\bsexe/genre\b|\bgenre\b", _enumerated(r"\bsexe\b", french=True)),
    ),
    _Rule(
        "PI_CAT-15",
        "language information",
        0.97,
        (
            r"\b(?:language preference|preferred (?:official )?language|official language (?:of choice|proficiency|qualification)|mother tongue|languages? spoken)\b",
        ),
        (
            r"\b(?:pr[ée]f[ée]rence linguistique|langue (?:officielle )?pr[ée]f[ée]r[ée]e|langue officielle de choix|comp[ée]tences? linguistiques?|langue maternelle|langues? parl[ée]es?)\b",
        ),
    ),
    _Rule(
        "PI_CAT-15",
        "language in personal-information enumeration",
        0.90,
        (_enumerated(r"\blanguage\b"),),
        (_enumerated(r"\blangue\b", french=True),),
    ),
    _Rule(
        "PI_CAT-16",
        "explicit medical information",
        1.0,
        (r"\bmedical information\b|\bmedical and psychological (?:information|records)\b",),
        (r"\brenseignements m[ée]dicaux\b|\bdossiers m[ée]dicaux et psychologiques\b",),
    ),
    _Rule(
        "PI_CAT-16",
        "medical condition or assessment",
        0.94,
        (
            r"\b(?:medical conditions?|medical records?|medical certificates?|psychological assessments?|physical disabilit(?:y|ies)|medical needs?|health information|fitness for work|blood type)\b",
        ),
        (
            r"\b(?:conditions? m[ée]dicales?|dossiers? m[ée]dicaux|certificats? m[ée]dicaux|[ée]valuations? psychologiques?|incapacit[ée]s? physiques?|besoins? m[ée]dicaux|renseignements sur la sant[ée]|aptitude au travail|groupe sanguin)\b",
        ),
    ),
    _Rule(
        "PI_CAT-17",
        "name in personal-information enumeration",
        0.98,
        (
            _enumerated(r"\b(?:full )?names?\b"),
            r"\b(?:full name|individual['’]s name|applicant['’]s name|surname|family name|given names?|maiden name|nicknames?|aliases?)\b",
            r"\bnames? and addresses?\b",
        ),
        (
            _enumerated(r"\bnoms?(?: complet)?\b", french=True),
            r"\b(?:nom de famille|pr[ée]noms?|nom de jeune fille|surnoms?|pseudonymes?)\b",
            r"\bnoms? et adresses?\b",
        ),
    ),
    _Rule(
        "PI_CAT-18",
        "opinions or views",
        0.99,
        (
            r"\b(?:opinions? (?:and|or) views?|views? and opinions?) of,? or about,? individuals?\b",
            r"\bopinions? or assessments? of an individual['’]s character\b",
            r"\b(?:views and opinions|opinions and views)\b",
        ),
        (
            r"\bopinions? et points? de vue (?:sur|concernant) (?:des )?individus?\b",
            r"\bopinions? ou [ée]valuations? (?:du caract[èe]re|sur une personne)\b",
        ),
    ),
    _Rule(
        "PI_CAT-19",
        "explicit other identification number",
        1.0,
        (r"\bother (?:identification|identifying|identity) numbers?\b",),
        (r"\bautres? num[ée]ros? d['’]identit[ée]\b|\bautres? num[ée]ros? d['’]identification\b",),
    ),
    _Rule(
        "PI_CAT-19",
        "non-employee identifier",
        0.91,
        (
            r"\b(?:driver['’]s licen[cs]e|fishing licen[cs]e|passport number|client identifier|unique client identifier|student number|licen[cs]e number|permit number|taxpayer identification number)\b",
        ),
        (
            r"\b(?:permis de conduire|permis de p[êe]che|num[ée]ro de passeport|identificateur de client|identificateur unique de client|num[ée]ro d['’][ée]tudiant|num[ée]ro de permis|num[ée]ro d['’]identification fiscale)\b",
        ),
    ),
    _Rule(
        "PI_CAT-20",
        "photograph or recorded image",
        0.99,
        (
            r"\b(?:photographs?|photography|photos?|digital photographs?|recorded visual images?|image recordings?)\b",
        ),
        (
            r"\b(?:photographies?|photos?|images? visuelles? enregistr[ée]es?|enregistrements? d['’]images?)\b",
        ),
    ),
    _Rule(
        "PI_CAT-21",
        "explicit physical attributes",
        1.0,
        (r"\bphysical attributes?\b",),
        (r"\bsignes? distinctifs?\b|\battributs? physiques?\b",),
    ),
    _Rule(
        "PI_CAT-21",
        "physical characteristic",
        0.94,
        (
            r"\b(?:height|weight|hair colou?r|eye colou?r|scars?|tattoos?|body piercings?|physical markings?)\b",
        ),
        (
            r"\b(?:taille|poids|couleur des cheveux|couleur des yeux|cicatrices?|tatouages?|per[çc]ages? corporels?|marques? physiques?)\b",
        ),
    ),
    _Rule(
        "PI_CAT-22",
        "place of birth",
        1.0,
        (r"\b(?:place|country) of birth\b",),
        (r"\b(?:lieu|pays) de naissance\b",),
    ),
    _Rule(
        "PI_CAT-23",
        "place of death",
        1.0,
        (r"\bplace of death\b",),
        (r"\blieu (?:du|de) d[ée]c[èe]s\b",),
    ),
    _Rule(
        "PI_CAT-24",
        "signature",
        1.0,
        (r"\bsignatures?\b",),
        (r"\bsignatures?\b",),
    ),
    _Rule(
        "PI_CAT-25",
        "Social Insurance Number",
        1.0,
        (r"\bSocial Insurance Numbers?\b|\bSIN\b",),
        (r"\bnum[ée]ros? d['’]assurance sociale\b|\bNAS\b",),
    ),
)


_UNMAPPED_PATTERNS: tuple[tuple[str, str, str], ...] = (
    ("education", r"\b(?:educational|education) information\b|\beducation records?\b", r"\brenseignements sur les [ée]tudes\b|\bdossiers scolaires\b"),
    ("travel", r"\btravel information\b|\btravel history\b", r"\brenseignements sur les voyages\b|\bant[ée]c[ée]dents de voyage\b"),
    ("religion", r"\breligious affiliation\b|\breligion\b", r"\bappartenance religieuse\b|\breligion\b"),
    ("race or ethnicity", r"\b(?:race|ethnic origin|ethnicity)\b", r"\b(?:race|origine ethnique|ethnicit[ée])\b"),
    ("digital or network identifier", r"\b(?:Internet Protocol|IP) address(?:es)?\b|\buser names? and passwords?\b", r"\badresses? (?:de protocole Internet|IP)\b|\bnoms? d['’]utilisateur et mots? de passe\b"),
    ("audio or video recording", r"\b(?:audio|video) recordings?\b", r"\benregistrements? (?:audio|vid[ée]o|sonores?)\b"),
    ("vehicle information", r"\bvehicle (?:identification|information)\b", r"\brenseignements sur (?:le|les) v[ée]hicules?\b",),
)


def _compile_rules() -> tuple[_CompiledRule, ...]:
    compiled: list[_CompiledRule] = []
    for rule in _RULES:
        for language, patterns in (("en", rule.en), ("fr", rule.fr)):
            if patterns:
                compiled.append(
                    _CompiledRule(
                        category_id=rule.category_id,
                        rule=rule.rule,
                        confidence=rule.confidence,
                        language=language,
                        patterns=tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns),
                    )
                )
    return tuple(compiled)


_COMPILED_RULES = _compile_rules()
_COMPILED_UNMAPPED = tuple(
    (
        concept,
        re.compile(en, re.IGNORECASE),
        re.compile(fr, re.IGNORECASE),
    )
    for concept, en, fr in _UNMAPPED_PATTERNS
)


def load_category_definitions(path: Path = DEFAULT_CATEGORY_PATH) -> dict[str, CategoryDefinition]:
    """Load and strictly validate the canonical 25-row category taxonomy."""

    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    expected_columns = {"PI_CAT_ID", "name_en", "name_fr", "examples_en", "examples_fr"}
    if not rows or set(rows[0]) != expected_columns:
        raise ValueError(f"Unexpected category columns in {path}")
    definitions = {
        row["PI_CAT_ID"]: CategoryDefinition(
            category_id=row["PI_CAT_ID"],
            name_en=row["name_en"],
            name_fr=row["name_fr"],
            examples_en=row["examples_en"],
            examples_fr=row["examples_fr"],
        )
        for row in rows
    }
    expected_ids = {f"PI_CAT-{number}" for number in range(1, 26)}
    if len(definitions) != len(rows) or set(definitions) != expected_ids:
        raise ValueError("Category taxonomy must contain each ID PI_CAT-1 through PI_CAT-25 exactly once")
    return definitions


def _source_fields(record: PibRecord | Mapping[str, str]) -> tuple[tuple[str, str, str], ...]:
    """Return only fields that describe the bank's personal information."""

    if isinstance(record, Mapping):
        get = lambda name: str(record.get(name, "") or "")
    else:
        get = lambda name: str(getattr(record, name, "") or "")
    return tuple(
        (field, language, unicodedata.normalize("NFKC", get(field)))
        for field, language in (
            ("description_en", "en"),
            ("description_fr", "fr"),
            ("class_of_individuals_en", "en"),
            ("class_of_individuals_fr", "fr"),
            ("note_en", "en"),
            ("note_fr", "fr"),
            ("purpose_en", "en"),
            ("purpose_fr", "fr"),
            ("consistent_uses_en", "en"),
            ("consistent_uses_fr", "fr"),
        )
        if get(field).strip()
    )


def _record_id(record: PibRecord | Mapping[str, str]) -> str:
    if isinstance(record, Mapping):
        if record.get("record_id"):
            return str(record["record_id"])
        scope = "standard" if "entry_title_en" in record else "institution"
        institution = str(record.get("institution_id", "") or "")
        key = str(record.get("bank_number_key", "") or "")
        return f"{scope}:{institution + ':' if institution else ''}{key}"
    return record.record_id


def _matched_text(match: re.Match[str]) -> str:
    if "evidence" in match.re.groupindex and match.group("evidence"):
        return match.group("evidence")
    return match.group(0)


def classify_record(
    record: PibRecord | Mapping[str, str],
    definitions: Mapping[str, CategoryDefinition] | None = None,
) -> RecordCategoryResult:
    """Assign every supportable category to one PIB record.

    Multi-label results are ordered by numeric ``PI_CAT`` ID.  A result is
    ambiguous when it contains an intentionally lower-confidence assignment or
    a recognized source concept missing from the official taxonomy.
    """

    definitions = definitions or load_category_definitions()
    evidence_by_category: dict[str, list[CategoryEvidence]] = {}
    source_fields = _source_fields(record)
    for rule in _COMPILED_RULES:
        for field, language, text in source_fields:
            if language != rule.language:
                continue
            for pattern in rule.patterns:
                match = pattern.search(text)
                if not match:
                    continue
                evidence = CategoryEvidence(
                    field=field,
                    language=language,
                    matched_text=_matched_text(match),
                    rule=rule.rule,
                    confidence=rule.confidence,
                )
                bucket = evidence_by_category.setdefault(rule.category_id, [])
                if evidence not in bucket:
                    bucket.append(evidence)

    unmapped: list[UnmappedEvidence] = []
    for concept, pattern_en, pattern_fr in _COMPILED_UNMAPPED:
        for field, language, text in source_fields:
            pattern = pattern_en if language == "en" else pattern_fr
            match = pattern.search(text)
            if match:
                evidence = UnmappedEvidence(concept, field, language, match.group(0))
                if evidence not in unmapped:
                    unmapped.append(evidence)

    assignments: list[CategoryAssignment] = []
    for category_id in sorted(evidence_by_category, key=lambda value: int(value.split("-")[1])):
        definition = definitions.get(category_id)
        if definition is None:
            raise ValueError(f"Rules reference missing category definition {category_id}")
        evidence = tuple(
            sorted(
                evidence_by_category[category_id],
                key=lambda item: (-item.confidence, item.field, item.matched_text.casefold()),
            )
        )
        assignments.append(
            CategoryAssignment(
                category_id=category_id,
                name_en=definition.name_en,
                name_fr=definition.name_fr,
                confidence=max(item.confidence for item in evidence),
                evidence=evidence,
            )
        )

    ambiguity_reasons: list[str] = []
    low_confidence = [item.category_id for item in assignments if item.confidence < 0.80]
    if low_confidence:
        ambiguity_reasons.append(
            "lower-confidence overloaded source labels: " + ", ".join(low_confidence)
        )
    if unmapped:
        ambiguity_reasons.append(
            "source concepts absent from the 25-category taxonomy: "
            + ", ".join(sorted({item.concept for item in unmapped}))
        )
    unclassified = not assignments
    if unclassified:
        ambiguity_reasons.append("no supported category evidence found")
    return RecordCategoryResult(
        record_id=_record_id(record),
        assignments=tuple(assignments),
        ambiguous=bool(ambiguity_reasons),
        unclassified=unclassified,
        ambiguity_reasons=tuple(ambiguity_reasons),
        unmapped_evidence=tuple(unmapped),
    )


def classify_records(
    records: Iterable[PibRecord | Mapping[str, str]],
    definitions: Mapping[str, CategoryDefinition] | None = None,
) -> list[RecordCategoryResult]:
    """Classify a corpus while loading the taxonomy only once."""

    definitions = definitions or load_category_definitions()
    return [classify_record(record, definitions) for record in records]
