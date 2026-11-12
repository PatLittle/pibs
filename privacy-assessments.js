import {number, filterRecords, sortRecords, readableLabel, escapeHtml as esc, getJson, dateLabel} from './privacy-assessment-utils.js';

const $ = id => document.getElementById(id);
let catalogue;
const keys = ['name_en', 'name_fr', 'gc_orgID', 'title_en', 'title_fr'];
let state;
function readState() {
  const params = new URLSearchParams(location.search);
  return {department: params.get('department') || '', q: params.get('q') || '', availability: ['both', 'readable', 'none'].includes(params.get('availability')) ? params.get('availability') : '',
    page: Math.max(1, Number.parseInt(params.get('page'), 10) || 1), size: [10, 25, 50, 100].includes(Number(params.get('size'))) ? Number(params.get('size')) : 25,
    sort: keys.includes(params.get('sort')) ? params.get('sort') : 'name_en', descending: params.get('order') === 'desc'};
}
function writeState() {
  const params = new URLSearchParams();
  for (const key of ['department', 'q', 'availability']) if (state[key]) params.set(key, state[key]);
  if (state.page !== 1) params.set('page', state.page);
  if (state.size !== 25) params.set('size', state.size);
  if (state.sort !== 'name_en') params.set('sort', state.sort);
  if (state.descending) params.set('order', 'desc');
  const search = params.toString();
  history.replaceState(null, '', location.pathname + (search ? '?' + search : '') + location.hash);
}
function controls() {
  $('department').value = state.department;
  $('assessment-search').value = state.q;
  $('availability').value = state.availability;
  $('page-size').value = state.size;
}
function renderBars(id, items) {
  const maximum = Math.max(1, ...items.map(item => item.count));
  $(id).innerHTML = items.map(item => `<div class="bar-row"><div class="bar-row__label"><span>${item.href ? `<a href="${esc(item.href)}">${esc(item.label)}</a>` : esc(item.label)}</span><strong>${number(item.count)}</strong></div><div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:${100 * item.count / maximum}%"></div></div></div>`).join('');
}
function overview() {
  const {summary} = catalogue;
  for (const [id, value] of [['stat-assessments', summary.records], ['stat-departments', summary.departments], ['stat-documents', summary.markdown_exports], ['stat-bilingual', summary.availability.both]]) $(id).textContent = number(value);
  $('collection-date').textContent = 'Collection updated: ' + dateLabel(catalogue.collection_generated_at_utc) + '. Counts include all repository entries, including sources that need review.';
  renderBars('language-bars', [{label: 'Both English and French', count: summary.availability.both || 0}, {label: 'English only', count: summary.availability.en || 0}, {label: 'French only', count: summary.availability.fr || 0}, {label: 'No readable copy', count: summary.availability.none || 0}]);
  renderBars('department-bars', summary.top_departments.map(dept => ({label: dept.name_en, count: dept.count, href: `privacy-assessments.html?department=${encodeURIComponent(dept.institution_id)}#assessments`}))); 
}
function render() {
  const filtered = sortRecords(filterRecords(catalogue.records, state), state.sort, state.descending);
  const pages = Math.max(1, Math.ceil(filtered.length / state.size));
  state.page = Math.min(state.page, pages);
  writeState();
  const start = (state.page - 1) * state.size;
  const records = filtered.slice(start, start + state.size);
  $('assessment-status').textContent = filtered.length ? `${number(filtered.length)} of ${number(catalogue.records.length)} assessments · Showing ${number(start + 1)}–${number(start + records.length)}` : 'No assessments match your filters. Try another department or clear your search.';
  $('assessment-rows').innerHTML = records.length ? records.map(row => {
    const params = new URLSearchParams({institution_id: row.institution_id, pia_id: row.pia_id, lang: row.available_languages.includes('en') ? 'en' : row.available_languages[0] || (row.sources.en ? 'en' : 'fr'), from: location.search});
    const badge = `<span class="assessment-badge${row.available_languages.length ? '' : ' assessment-badge--warning'}">${readableLabel(row)}</span>`;
    const type = row.type !== 'Privacy assessment' ? `<span class="assessment-badge assessment-badge--warning">${esc(row.type)}</span>` : '';
    return `<tr><td>${esc(row.name_en || 'Not recorded')}</td><td lang="fr">${esc(row.name_fr || 'Non disponible')}</td><td>${esc(row.gc_orgID || 'Not recorded')}</td><td lang="en">${esc(row.title_en || 'English title not available')}<div>${badge}${type}</div></td><td lang="fr">${esc(row.title_fr || 'Titre français non disponible')}</td><td><a class="button-link button-link--small" href="privacy-assessment.html?${esc(params)}" aria-label="${esc('Open ' + (row.title_en || row.title_fr || 'assessment'))}">Open</a></td></tr>`;
  }).join('') : '<tr><td colspan="6" class="empty-results">No matching assessments. Use Clear filters to start again.</td></tr>';
  $('assessment-pagination').hidden = filtered.length === 0;
  $('page-summary').textContent = `Page ${state.page} of ${pages}`;
  for (const id of ['page-first', 'page-previous']) $(id).disabled = state.page === 1;
  for (const id of ['page-next', 'page-last']) $(id).disabled = state.page === pages;
  for (const button of document.querySelectorAll('[data-sort]')) {
    const active = button.dataset.sort === state.sort;
    button.closest('th').removeAttribute('aria-sort');
    if (active) button.closest('th').setAttribute('aria-sort', state.descending ? 'descending' : 'ascending');
    button.querySelector('.sort-indicator').textContent = active ? state.descending ? ' ↓' : ' ↑' : '';
  }
}
async function init() {
  try {
    catalogue = await getJson('data/privacy_assessments.json');
    for (const dept of catalogue.departments) $('department').add(new Option(dept.name_en, dept.institution_id));
    state = readState();
    // Keep unknown department IDs as an explicit empty selection rather than silently showing all records.
    if (state.department && !catalogue.departments.some(dept => dept.institution_id === state.department)) $('department').add(new Option('Unknown department', state.department));
    controls(); overview(); render();
    $('assessment-filters').addEventListener('submit', event => event.preventDefault());
    for (const [id, key, eventName] of [['department', 'department', 'change'], ['assessment-search', 'q', 'input'], ['availability', 'availability', 'change'], ['page-size', 'size', 'change']]) $(id).addEventListener(eventName, event => { state[key] = key === 'size' ? Number(event.target.value) : event.target.value; state.page = 1; render(); });
    $('clear-filters').addEventListener('click', () => { state = {...state, department: '', q: '', availability: '', page: 1}; controls(); render(); });
    for (const button of document.querySelectorAll('[data-sort]')) button.addEventListener('click', () => { state.descending = state.sort === button.dataset.sort ? !state.descending : false; state.sort = button.dataset.sort; state.page = 1; render(); });
    for (const [id, target] of [['page-first', () => 1], ['page-previous', () => state.page - 1], ['page-next', () => state.page + 1], ['page-last', () => Math.max(1, Math.ceil(filterRecords(catalogue.records, state).length / state.size))]]) $(id).addEventListener('click', () => {state.page = target(); render(); $('assessment-status').scrollIntoView({block: 'nearest'});});
    window.addEventListener('popstate', () => {state = readState(); controls(); render();});
  } catch (error) {
    $('assessment-status').textContent = 'The assessment catalogue could not be loaded. Reload this page to try again, or browse the source collection linked in the footer.';
    $('assessment-status').setAttribute('role', 'alert');
    $('collection-date').textContent = 'Holdings metrics are currently unavailable.';
  }
}
init();
