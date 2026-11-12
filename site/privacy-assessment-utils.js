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
    && (!query || fold([row.name_en, row.name_fr, row.gc_orgID, row.title_en, row.title_fr, ...(row.pib_ids || []), ...(row.cor_ids || [])].join(' ')).includes(query))
    && (!state.references || (state.references === 'pibs' ? row.pib_count > 0 : row.cor_count > 0))
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

export function referenceLinks(items = []) {
  return items.map(item => {
    const match = item.matched_records?.[0];
    if (!match) return escapeHtml(item.id);
    const params = new URLSearchParams({dataset: match.dataset, open: 'record'});
    if (match.institution_id) params.set('institution_id', match.institution_id);
    params.set(match.dataset.includes('pibs') ? 'bank_number_key' : 'record_number', match.record_id);
    return `<a href="table.html?${escapeHtml(params)}">${escapeHtml(item.id)}</a>`;
  });
}
export function referenceList(items = []) {
  const links = referenceLinks(items);
  if (!links.length) return '<span class="muted">None identified</span>';
  const list = values => '<ul class="reference-list">' + values.map(value => `<li>${value}</li>`).join('') + '</ul>';
  return list(links.slice(0, 3)) + (links.length > 3 ? `<details class="reference-more"><summary>${links.length - 3} more</summary>${list(links.slice(3))}</details>` : '');
}
export function wordCounts(row) {
  return ['en', 'fr'].map(lang => `<span class="word-count-line">${lang.toUpperCase()}: ${row['word_count_' + lang] == null ? '—' : number(row['word_count_' + lang])}</span>`).join('');
}
