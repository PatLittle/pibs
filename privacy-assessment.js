import {getJson, dateLabel, languageLabel, statusLabel, fold, escapeHtml as esc} from './privacy-assessment-utils.js';

const $ = id => document.getElementById(id);
let assessment;
let requestedLanguage;
const params = new URLSearchParams(location.search);
function sourceDetails() {
  $('source-details').innerHTML = ['en', 'fr'].map(lang => {
    const source = assessment.languages[lang];
    if (!source) return `<h3>${languageLabel(lang)}</h3><p>No corresponding source was identified in the collection.</p>`;
    const url = /^https?:\/\//i.test(source.url || '') ? `<a href="${esc(source.url)}">${esc(source.url)}</a>` : 'Not recorded';
    return `<h3 lang="${lang}">${languageLabel(lang)}</h3><dl><dt>Availability</dt><dd>${esc(statusLabel(source.status))}</dd><dt>Source URL</dt><dd>${url}</dd><dt>HTTP response at collection</dt><dd>${esc(source.http_status ?? 'No response')}</dd><dt>Retrieved</dt><dd>${esc(dateLabel(source.checked_at_utc))}</dd>${source.anchor_type ? `<dt>Inline summary link</dt><dd>${source.anchor_type === 'text_fragment' ? 'Browser text fragment (the source has no native anchor)' : 'Native source anchor'}</dd>` : ''}</dl>`;
  }).join('');
}
function renderLanguage(lang, updateHistory = false) {
  const available = assessment.available_languages;
  const selected = available.includes(lang) ? lang : available[0] || (assessment.languages[lang] ? lang : Object.keys(assessment.languages)[0] || lang);
  const source = assessment.languages[selected];
  requestedLanguage = selected;
  const title = assessment['title_' + selected] || assessment.title_en || assessment.title_fr || 'Privacy assessment';
  $('assessment-title').textContent = title;
  $('assessment-title').lang = selected;
  document.title = `${title} - Privacy Assessments`;
  const institution = selected === 'fr' ? assessment.name_fr : assessment.name_en;
  $('assessment-institution').textContent = institution + (assessment.gc_orgID ? ` · GC organization ID ${assessment.gc_orgID}` : '');
  $('assessment-institution').lang = selected;
  for (const code of ['en', 'fr']) $('language-' + code).setAttribute('aria-pressed', String(code === selected));
  $('document-language').hidden = available.length !== 2;
  $('single-language').hidden = available.length !== 1;
  $('single-language').textContent = `Collected text available in ${languageLabel(selected)}.`;
  const rendered = source?.status === 'exported' && typeof source.html === 'string';
  $('document-body').innerHTML = rendered ? source.html : '';
  const firstHeading = $('document-body').firstElementChild;
  if (firstHeading?.tagName === 'H2' && fold(firstHeading.textContent.trim()) === fold(title.trim())) firstHeading.remove();
  $('document-body').lang = selected;
  $('document-body').hidden = !rendered;
  const safeSource = /^https?:\/\//i.test(source?.url || '');
  $('original-source').hidden = !safeSource;
  if (safeSource) $('original-source').href = source.url;
  $('download-markdown').hidden = !rendered;
  if (rendered) $('download-markdown').href = source.markdown_url;
  $('original-source').textContent = selected === 'fr' ? 'Source originale' : 'Original source';
  $('download-markdown').textContent = selected === 'fr' ? 'Télécharger le Markdown' : 'Download Markdown';
  $('document-provenance').textContent = source ? `Collected ${dateLabel(source.checked_at_utc)} · HTTP ${source.http_status ?? 'no response'}${source.kind === 'inline' ? ' · Summary extracted from the source page' : ''}` : 'No collected source for this language.';
  const notice = $('language-availability-notice');
  notice.hidden = available.length === 2;
  notice.textContent = available.length === 0 ? 'No readable copy is available for this entry. Source retrieval or content checks failed; see the source and availability details below.' : `Only the ${languageLabel(selected)} copy is available to read. See the source details for the other language’s collection status.`;
  $('reader-status').textContent = rendered ? `${languageLabel(selected)} assessment loaded.` : 'Assessment details loaded; collected text is unavailable.';
  $('reader-status').classList.add('wb-inv');
  $('reader-content').hidden = false;
  const url = new URL(location.href);
  url.searchParams.set('lang', selected);
  if (updateHistory) history.pushState(null, '', url);
  else history.replaceState(null, '', url);
  const header = document.querySelector('gcds-header');
  if (available.length === 2) {
    header.setAttribute('lang', selected);
    const alternate = new URL(url);
    alternate.searchParams.set('lang', selected === 'en' ? 'fr' : 'en');
    header.setAttribute('lang-href', alternate.href);
  }
}
async function init() {
  try {
    const catalogue = await getJson('data/privacy_assessments.json');
    const record = catalogue.records.find(row => row.institution_id === params.get('institution_id') && row.pia_id === params.get('pia_id'));
    if (!record) {
      $('assessment-title').textContent = 'Assessment not found';
      $('reader-status').textContent = 'This assessment link is missing or no longer in the catalogue. Return to all privacy assessments to select a record.';
      $('reader-status').setAttribute('role', 'alert');
      return;
    }
    assessment = await getJson(record.content_url);
    const back = new URL('privacy-assessments.html', location.href);
    back.search = params.get('from') || '';
    back.hash = 'assessments';
    $('back-to-assessments').href = back.href;
    $('assessment-type').textContent = assessment.type === 'Privacy assessment' ? 'Collected privacy assessment summary' : assessment.type;
    sourceDetails();
    renderLanguage(params.get('lang') === 'fr' ? 'fr' : 'en');
    for (const lang of ['en', 'fr']) $('language-' + lang).addEventListener('click', () => { if (lang !== requestedLanguage) renderLanguage(lang, true); });
    window.addEventListener('popstate', () => renderLanguage(new URLSearchParams(location.search).get('lang') || 'en'));
  } catch (error) {
    $('assessment-title').textContent = 'Assessment could not be loaded';
    $('reader-status').textContent = 'The collected document could not be loaded. Reload to try again, or return to the assessments table.';
    $('reader-status').setAttribute('role', 'alert');
  }
}
init();
