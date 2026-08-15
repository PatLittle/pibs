# PIBs relational data model

The machine-readable model is [`data_model.json`](data_model.json). Its hub is the
authoritative `institution_registry.institution_id`; `gc_orgID` remains an optional external
identifier and is not used as a filesystem or relational key.

```mermaid
erDiagram
    INSTITUTION_REGISTRY ||--o{ INSTITUTION_CLASSES_OF_RECORDS : publishes
    INSTITUTION_REGISTRY ||--o{ INSTITUTION_PERSONAL_INFORMATION_BANKS : publishes
    INSTITUTION_PERSONAL_INFORMATION_BANKS ||--o{ PIB_COR_LINKS : identifies
    INSTITUTION_CLASSES_OF_RECORDS ||--o{ PIB_COR_LINKS : may_resolve_to
    STANDARD_CLASSES_OF_RECORDS ||--o{ PIB_COR_LINKS : may_resolve_to
    PIB_TYPE_VALUES ||--o{ INSTITUTION_PERSONAL_INFORMATION_BANKS : controls_type
    PIB_TYPE_VALUES ||--o{ STANDARD_PERSONAL_INFORMATION_BANKS : controls_type
```

`pib_cor_links.csv` normalizes the many-to-many relationship currently embedded in the
English and French `related_record_number` text. Its `relationship_scope` distinguishes
institution-specific from standard Classes of Records, and `resolved` makes unresolved source
references auditable rather than silently discarding them.

`pi_categories_en_fr.csv` is a controlled vocabulary, but current Info Source publications do
not provide explicit category assignments for each PIB. The model therefore records it as an
available vocabulary without inferring assignments from narrative descriptions.
