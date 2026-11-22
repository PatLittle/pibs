# Public Accounts program codes and joins

The 2025–2026 Program Codes list from Public Services and Procurement Canada
connects the Service Inventory to GC InfoBase records on spending, staffing and
performance. The program code supplies the common key. The institution registry
resolves the organization in each system using its own identifier.

[Open the Chart of Accounts resource](https://open.canada.ca/data/en/dataset/3c371e57-d487-49fa-bb0d-352ae8dd6e4e/resource/467a253b-fd0e-4123-acb3-7641252d8ffe)
· [Open the GC InfoBase resources](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f)
· [Download the joined tables and audit](https://patlittle.github.io/pibs/index.html#public-accounts)

## What joined

| Source or relationship | Observed | Resolved |
| --- | ---: | ---: |
| Chart source data rows | 1,233 | 1,439 distinct codes after separating programs from core responsibilities |
| Accounting entity and department-number pairs | 137 | 113 pairs across 83 registry institutions |
| Service Inventory program references for 2025–2026 | 169 | 158 links covering 134 services and 52 owner-code pairs |
| Owner-scoped Service Inventory catalogue codes | 648 | 554 shared codes |
| GC InfoBase expenditures and FTE program keys | 1,146 | 1,110 |
| GC InfoBase performance activity keys | 905 | 868 |
| GC InfoBase Federal Programs typed keys with an organization and code | 1,668 | 1,222 |

The Chart includes 1,115 inventory programs, 310 core responsibilities and 14
non-budgetary codes. It supplies classifications and descriptions. Financial
amounts, employee counts and indicator values remain in their InfoBase sources.
The English Chart snapshot supplies the graph's source labels.

## Join keys

| Relationship | Key | Resolution rule |
| --- | --- | --- |
| Chart program to core responsibility | `(fiscal_yr, accounts_entity, parent_code)` | Read the published core code on the same source row. |
| Chart accounting department to institution | Parsed department number to `institution_registry.rg` | Parse each semicolon-delimited entry, keep leading zeros, and require one registry institution per number. |
| Annual Service Inventory reference to Chart code | `(fiscal_yr, owner_org, service_id, program_id)` to `(fiscal_yr, accounts_entity, account_code)` | Resolve the inventory owner through the registry. Require one Chart code scoped to that entity and accounting department. |
| Service catalogue to Chart code | `(owner_org, program_id)` to the Chart code and entity | The code occurs in both catalogues. The fiscal year identifies the Chart snapshot. |
| Chart code to GC InfoBase | `(fiscal_yr, program_code, institution_id)` | Resolve Chart `rg` and InfoBase organization ID independently in the registry. Both must lead to the same institution. Require one eligible Chart code and agree on activity type when the source publishes it. |

The department field can name an accounting department for another entity.
For a program join, the Chart entity must also match the department label or
a registry name for that department. Internal services codes such as `ISS01`
repeat across entities and are scoped accordingly. Department number `096`
has two registry candidates and stays ambiguous. The Chart's two source rows
without a department and the 11 annual service references without a Chart match
remain in the source or audit. Rows with multiple eligible InfoBase source IDs
are excluded from that source-specific join.

## Follow a real example

[CIHR's Public Notices of funding opportunities (service 1121)](https://patlittle.github.io/pibs/graph.html?node=service%3Acihr-irsc%3A1121)
reports `BUI01`, `BUI02` and `BUI03` in 2025–2026. The Chart lists them
under core responsibility `BUI00`, Funding Health Research and Training.
The registry connects Receiver General department `061` to GC InfoBase
organization `74`. Follow `BUI01` to its matching Federal Programs and
spending/FTE records, or `BUI00` to the core responsibility performance records.

IRCC's Study Permit service `1428` reports `BGD02` in 2023–2024 and
2024–2025. The 2025–2026 Chart and InfoBase also contain `BGD02`. The graph
exposes that match from the program catalogue, while the service retains its
actual reporting years. Program and accounting links do not indicate that a
PIB or assessment covers the program.

## Reproduce the build

The publisher's English CSV is stored losslessly in
`data/public_accounts/cp-pc-2526-eng.csv.gz`. The uncompressed SHA-256 is
`d21f4f0672e1f08d0476e5b3c19da836044a5216539fe41b8fa3ee1272c22cb8`.
Source ordinals count data rows from 1, after the header. The InfoBase key
snapshot keeps only organization identifiers, literal codes, activity types,
source program IDs, and counts. It was queried November 21, 2026.

| GC InfoBase resource | Fiscal year filter | Identifier fields |
| --- | --- | --- |
| [Expenditures and FTE](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/64774bc1-c90a-4ae2-a3ac-d9b50673a895) | `fy_ef = 2025-2026` | `organization_id`, `program_id` |
| [Performance](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/09c15494-788e-4991-ad00-2bd905c4f225) | `fy_ef = 2025-26` | `org_id`, `activity_id`, `activity_level` |
| [Federal Programs](https://open.canada.ca/data/en/dataset/a35cf382-690c-4221-a971-cf0fd189a46f/resource/8d3cd22d-15b0-468a-bb75-c1e736107c45) | `year = 2025` | `organization_id`, `program_code`, `type`, `id` |

Run `python -m scripts.public_accounts`, `python scripts/build_graph.py`,
and `python scripts/build_network_schema.py` from the repository root to
regenerate the CSV tables, join audit, graph and field catalogue offline.
The Pages build runs these steps automatically.
