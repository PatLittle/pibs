// Every available value remains inspectable, including bilingual and nested fields.
// Loading pointers are implementation details, not attributes of a source record.
export function nodeAttributes(node, attributes = {}) {
  const { attribute_url, attributes: inline, ...metadata } = node;
  const values = { ...metadata, ...(inline || {}), ...attributes };
  const first = ['pib_type', 'personal_information_categories', 'pib_type_details',
    'survey_version', 'impact_level', 'senior_official', 'senior_official_uid',
    'purpose_en', 'purpose_fr', 'description_en', 'description_fr',
    'class_of_individuals_en', 'class_of_individuals_fr', 'consistent_uses_en', 'consistent_uses_fr',
    'retention_disposal_en', 'retention_disposal_fr', 'document_types_en', 'document_types_fr'];
  return Object.fromEntries([...new Set([...first.filter(k => k in values), ...Object.keys(values)])].map(k => [k, values[k]]));
}
export function attributeLabel(key, translate) {
  const match = /^(.*)_(en|fr)$/.exec(key);
  const base = match ? match[1] : key;
  const translated = translate(base);
  const label = translated !== base ? translated : base.replace(/_/g, ' ').replace(/^./, c => c.toUpperCase());
  return label + (match ? ' (' + match[2].toUpperCase() + ')' : '');
}
