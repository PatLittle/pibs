export const number = value => new Intl.NumberFormat('en-CA').format(Number(value || 0));
export const fold = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('en-CA');
export const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
export const languageLabel = lang => lang === 'fr' ? 'Français' : 'English';
export function readableLabel(row) {
  return row.available_languages.length === 2 ? 'EN + FR' : row.available_languages.length ? `${languageLabel(row.available_languages[0])} only` : 'No readable copy';
}
export function filterRecords(records, state) {
  const query = fold(state.q).trim();
  return records.filter(row => (!state.department || row.institution_id === state.department)
    && (!query || fold([row.name_en, row.name_fr, row.gc_orgID, row.title_en, row.title_fr].join(' ')).includes(query))
    && (!state.availability || (state.availability === 'both' ? row.available_languages.length === 2 : state.availability === 'readable' ? row.available_languages.length > 0 : row.available_languages.length === 0)));
}
export function sortRecords(records, key, descending = false) {
  return [...records].sort((a, b) => ((String(a[key] || '').localeCompare(String(b[key] || ''), 'en', {numeric: true, sensitivity: 'base'}) || a.id.localeCompare(b.id)) * (descending ? -1 : 1)));
}
export function dateLabel(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Not recorded' : new Intl.DateTimeFormat('en-CA', {dateStyle: 'medium', timeZone: 'UTC'}).format(date) + ' (UTC)';
}
export async function getJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed (${response.status})`);
  return response.json();
}
export const statusLabel = status => ({exported: 'Readable collected copy', http_error: 'Source request failed', request_error: 'Source could not be reached', soft_error_page: 'Source returned an error page', not_pia_content: 'Source is not an assessment summary', language_mismatch: 'Source returned a different language', conversion_error: 'Document conversion failed', insufficient_content: 'Content needs review', unsupported_content_type: 'Document format not supported'}[status] || 'No collected copy');
