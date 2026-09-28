"""Small, source-checked retention ledger; omitted rules require interpretation.

The source quote is validated verbatim by the builder. Unspecified starts,
age/death branches and mixed-document schedules never borrow an activity date.
"""

from my_info_v2.catalog import record


def rule(owner, bank, event, en, fr, mode, years, quote):
    return {"record_id": record(owner, bank), "event": event, "event_label_en": en,
            "event_label_fr": fr, "mode": mode, "years": years,
            "source_field": "retention_en", "source_quote": quote}


RULES = [
    rule("CSA", "CSA PPU 020", "event_occurred", "the mission launch took place", "le lancement de la mission a eu lieu", "fixed", 2,
         "Records will be retained for 2 years after the mission launch it concerned and then will be destroyed."),
    rule("DND", "DND PPE 818", "service_ended", "you were released from the Canadian Forces", "vous avez été libéré des Forces canadiennes", "archive_after", 5,
         "Records are retained for five years after release from the CF and then transferred to Library and Archives Canada."),
    rule("CBSA", "CBSA PPU 018", "event_occurred", "the most recent declaration card or kiosk receipt was dated", "la plus récente carte de déclaration ou le reçu de la borne a été daté", "fixed", 7,
         "Files are retained for seven years from the date stamped on the traveller's declaration card (date of the interview between the traveller and the border services officer or date stamped on the traveller receipt when the traveller uses the Automated Border Clearance or NEXUS kiosk). After this period, the records are destroyed."),
    rule("CBSA", "CBSA PPU 003", "file_closed", "CBSA closed the complaint file", "l'ASFC a fermé le dossier de plainte", "minimum", 6,
         "Files are retained for six (6) years after the file is closed."),
    rule("HC", "HC PPU 440", "last_action", "the last administrative action on your dental-plan record took place", "la dernière mesure administrative concernant votre dossier de soins dentaires a eu lieu", "minimum", 2,
         "Personal information will be retained for a minimum of two (2) years after the last administrative action and will follow the disposition standards set out by Library and Archives Canada."),
    rule("PCH", "PCH PPU 070", "service_ended", "you left the volunteer program", "vous avez quitté le programme de bénévolat", "fixed", 2,
         "Records are kept for two years after a volunteer leaves and then destroyed."),
]
