/* HQ Studio — interface (sem build). */

/* ---------- Utilidades ---------- */
const $ = (selector, root = document) => root.querySelector(selector);
const esc = (v = '') => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const plural = (n, one, many) => `${n} ${n === 1 ? one : many}`;
const store = {
  get(key) { try { return localStorage.getItem(key); } catch { return null; } },
  set(key, value) { try { localStorage.setItem(key, value); } catch { /* armazenamento indisponível */ } },
  del(key) { try { localStorage.removeItem(key); } catch { /* armazenamento indisponível */ } },
};

const ICONS = {
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  chevronLeft: '<path d="m15 18-6-6 6-6"/>',
  chevronRight: '<path d="m9 18 6-6-6-6"/>',
  trash: '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>',
  history: '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
  sparkles: '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
  wand: '<path d="m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72"/><path d="m14 7 3 3"/><path d="M5 6v4"/><path d="M19 14v4"/><path d="M10 2v2"/><path d="M7 8H3"/><path d="M21 16h-4"/><path d="M11 3H9"/>',
  refresh: '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/><path d="M8 16H3v5"/>',
  book: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
  folder: '<path d="M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/>',
  user: '<circle cx="12" cy="8" r="5"/><path d="M20 21a8 8 0 0 0-16 0"/>',
  package: '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><path d="m3.3 7 8.7 5 8.7-5"/>',
  mapPin: '<path d="M20 10c0 5-5.54 10.19-7.4 11.8a1 1 0 0 1-1.2 0C9.54 20.19 4 15 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
  image: '<rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.09-3.09a2 2 0 0 0-2.82 0L6 21"/>',
  alert: '<circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
  check: '<path d="M20 6 9 17l-5-5"/>',
  maximize: '<path d="M15 3h6v6"/><path d="M9 21H3v-6"/><path d="M21 3l-7 7"/><path d="M3 21l7-7"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m17 8-5-5-5 5"/><path d="M12 3v12"/>',
  pencil: '<path d="M21.17 6.81a1 1 0 0 0-3.99-3.99L3.84 16.17a2 2 0 0 0-.5.83l-1.32 4.35a.5.5 0 0 0 .62.62l4.35-1.32a2 2 0 0 0 .83-.5z"/><path d="m15 5 4 4"/>',
  eye: '<path d="M2.06 12.35a1 1 0 0 1 0-.7 10.75 10.75 0 0 1 19.88 0 1 1 0 0 1 0 .7 10.75 10.75 0 0 1-19.88 0"/><circle cx="12" cy="12" r="3"/>',
  panels: '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 12h18"/><path d="M12 3v18"/>',
  library: '<path d="m16 6 4 14"/><path d="M12 6v14"/><path d="M8 8v12"/><path d="M4 4v16"/>',
  arrowLeft: '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  star: '<path d="M11.5 2.3a.6.6 0 0 1 1 0l2.6 5.3 5.8.9a.6.6 0 0 1 .3 1l-4.2 4.1 1 5.8a.6.6 0 0 1-.9.6L12 17.3l-5.2 2.7a.6.6 0 0 1-.9-.6l1-5.8-4.2-4.1a.6.6 0 0 1 .3-1l5.8-.9z"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  crop: '<path d="M6 2v14a2 2 0 0 0 2 2h14"/><path d="M18 22V8a2 2 0 0 0-2-2H2"/>',
  undo: '<path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 0 11H11"/>',
  hardDrive: '<path d="M22 12H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/><path d="M6 16h.01"/><path d="M10 16h.01"/>',
};
const icon = (name, cls = '') => `<svg class="icon${cls ? ' ' + cls : ''}" viewBox="0 0 24 24" aria-hidden="true" focusable="false">${ICONS[name] || ''}</svg>`;

const KINDS = {
  character: {label: 'Personagem', plural: 'Personagens', newLabel: 'Novo personagem', saveLabel: 'Salvar personagem', icon: 'user',
    namePh: 'Ex.: Régis', descPh: 'Como deve aparecer no desenho? Rosto, cabelo, roupas, cores marcantes…'},
  object: {label: 'Objeto', plural: 'Objetos', newLabel: 'Novo objeto', saveLabel: 'Salvar objeto', icon: 'package',
    namePh: 'Ex.: Panetone gigante', descPh: 'Formato, tamanho, cores, detalhes que não podem mudar…'},
  location: {label: 'Local', plural: 'Locais', newLabel: 'Novo local', saveLabel: 'Salvar local', icon: 'mapPin',
    namePh: 'Ex.: Cozinha da vó', descPh: 'Ambiente, iluminação, móveis, cores, época…'},
};
const kindOf = a => KINDS[a.kind] || KINDS.character;
const DEFAULT_STYLE = 'HQ humorística brasileira, traço expressivo, cores vibrantes.';

/* ---------- Estado ---------- */
const state = {
  projects: [], project: null, comics: [], comic: null, assets: [], frames: [], providers: [],
  covers: {}, comicFrames: {},
  screen: 'overview',          // overview | library | comic
  libraryReturn: null,         // HQ de onde a biblioteca foi aberta
  comicsQuery: '',             // busca na página de HQs
  libKind: 'all', libQuery: '',
  view: store.get('hq-view') === 'read' ? 'read' : 'edit',
  provider: store.get('hq-provider') || 'demo',
};
const saveTimers = new Map();
let mutationSeq = 0;

const editorText = () => state.project?.text_mode === 'editor';
const isBusy = f => f.status === 'queued' || f.status === 'processing';
const frameById = id => state.frames.find(f => f.id === id);
const frameSig = f => `${f.status}|${f.image_path || ''}|${f.message || ''}|${f.provider || ''}|${JSON.stringify(f.balloons || [])}|${f.format}|${JSON.stringify(f.credits || {})}`;
const FORMATS = {landscape: 'Paisagem', portrait: 'Retrato', square: 'Quadrado'};
const frameLabel = f => f.kind === 'cover' ? 'Capa' : f.kind === 'credits' ? 'Créditos' : `Quadro ${f.position}`;
const providerName = id => (state.providers.find(p => p.id === id)?.name || id || '').replace(/\s*\(.*?\)\s*/g, ' ').trim();

/* ---------- API ---------- */
async function api(path, options = {}) {
  const res = await fetch('/api' + path, options);
  let data;
  try { data = await res.json(); } catch { data = null; }
  if (!res.ok) throw new Error(typeof data?.detail === 'string' ? data.detail : `Erro ${res.status}`);
  return data;
}
const json = (method, body) => ({method, headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)});

/* ---------- Feedback ---------- */
let toastTimer;
function toast(message, type = 'ok') {
  const node = $('#toast');
  node.innerHTML = `${icon(type === 'error' ? 'alert' : 'check')}<span>${esc(message)}</span>`;
  node.classList.toggle('error', type === 'error');
  node.classList.add('visible');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => node.classList.remove('visible'), type === 'error' ? 6000 : 3200);
}
function fail(error) {
  const message = error?.message || String(error);
  const slot = modal.open && $('#modal-body .modal-error');
  if (slot) { slot.hidden = false; $('span', slot).textContent = message; return; }
  toast(message, 'error');
}

/* ---------- Modal ---------- */
const modal = $('#modal');
function modalShell(titleHtml, bodyHtml, subtitleHtml = '') {
  return `<div class="modal-head"><div><h2 id="modal-title">${titleHtml}</h2>${subtitleHtml ? `<p>${subtitleHtml}</p>` : ''}</div>
    <button class="icon-btn" type="button" data-action="close-modal" aria-label="Fechar">${icon('x')}</button></div>
    <div class="modal-content"><div class="modal-error" role="alert" hidden>${icon('alert')}<span></span></div>${bodyHtml}</div>`;
}
function openModal(html, {size = 'md', kind = ''} = {}) {
  $('#modal-body').innerHTML = html;
  modal.dataset.size = size;
  modal.dataset.kind = kind;
  if (!modal.open) modal.showModal();
  const target = $('#modal-body [autofocus]') || $('#modal-body [data-action="close-modal"]');
  target?.focus();
}
function closeModal() { if (modal.open) modal.close(); }
modal.addEventListener('click', e => { if (e.target === modal) closeModal(); });
// O evento chega depois do fechamento; se outro modal já abriu nesse meio-tempo, não apaga o conteúdo dele.
modal.addEventListener('close', () => {
  // Fechar o editor de balões grava o que ainda estava na espera.
  if (balloonEditor && modal.dataset.kind === 'balloons') {
    const ed = balloonEditor;
    balloonEditor = null;
    if (ed.timer) saveBalloons(ed).catch(fail);
  }
  if (modal.open) return; $('#modal-body').innerHTML = ''; modal.dataset.kind = ''; });

/* ---------- Navegação lateral (mobile) ---------- */
function toggleNav(open) {
  const shell = $('#shell');
  const value = open ?? !shell.classList.contains('nav-open');
  shell.classList.toggle('nav-open', value);
  $('#menu-btn').setAttribute('aria-expanded', String(value));
}

/* ---------- Clientes de IA ---------- */
function renderProviders() {
  const select = $('#provider');
  select.innerHTML = state.providers.map(p =>
    `<option value="${esc(p.id)}" ${p.available ? '' : 'disabled'}>${esc(p.name)}${p.available ? '' : ' — não instalado'}</option>`).join('');
  if (!state.providers.some(p => p.id === state.provider && p.available)) state.provider = 'demo';
  select.value = state.provider;
  updateProviderNote();
  renderGenOptions();
}
/* Modelo e esforço do agente, guardados por cliente. Esforço baixo por padrão: o agente só
   repassa o pedido ao gerador de imagem, então raciocinar muito gasta tokens sem melhorar o quadro. */
const EFFORT_LABELS = {low: 'Esforço baixo', medium: 'Esforço médio', high: 'Esforço alto', xhigh: 'Esforço muito alto', max: 'Esforço máximo'};
const DEFAULT_EFFORT = 'low';
function currentProvider() { return state.providers.find(p => p.id === state.provider); }
function generationOptions() {
  const p = currentProvider();
  if (!p) return {model: '', effort: ''};
  const model = store.get(`hq-model-${p.id}`) || '';
  const effort = store.get(`hq-effort-${p.id}`) ?? DEFAULT_EFFORT;
  return {
    model: p.models.some(m => m.id === model) ? model : '',
    effort: p.efforts.includes(effort) ? effort : '',
  };
}
function renderGenOptions() {
  const p = currentProvider();
  const box = $('#gen-options');
  const hasOptions = !!p && (p.models.length || p.efforts.length);
  box.hidden = !hasOptions;
  if (!hasOptions) return;
  const {model, effort} = generationOptions();
  $('#model').hidden = !p.models.length;
  $('#model').innerHTML = `<option value="">Modelo padrão</option>` + p.models.map(m => `<option value="${esc(m.id)}">${esc(m.name)}</option>`).join('');
  $('#model').value = model;
  $('#effort').hidden = !p.efforts.length;
  $('#effort').innerHTML = `<option value="">Esforço padrão</option>` + p.efforts.map(e => `<option value="${esc(e)}">${EFFORT_LABELS[e] || e}</option>`).join('');
  $('#effort').value = effort;
}
function updateProviderNote() {
  const note = state.providers.find(p => p.id === state.provider)?.note || '';
  $('#provider-note').textContent = note;
  $('#provider').title = note;
}

/* ---------- Pedaços de interface ---------- */
function avatar(a, size = 'sm') {
  const k = kindOf(a);
  return a.image_path
    ? `<img class="avatar ${size}" src="${esc(a.image_path)}" alt="">`
    : `<span class="avatar ${size} kind-${esc(a.kind)}">${icon(k.icon)}</span>`;
}
function kindTag(a) {
  const k = kindOf(a);
  return `<span class="kind-tag kind-${esc(a.kind)}">${icon(k.icon)}${k.label}</span>`;
}
function emptyHtml({iconName, title, text, action = ''}) {
  return `<div class="empty"><div class="empty-icon">${icon(iconName)}</div><h3>${title}</h3><p>${text}</p>${action}</div>`;
}
function tipHtml(key, html) {
  if (store.get(`hq-tip-${key}`)) return '';
  return `<div class="tip">${icon('info')}<p>${html}</p>
    <button class="icon-btn sm" type="button" data-action="dismiss-tip" data-tip="${key}" aria-label="Dispensar dica" title="Dispensar">${icon('x')}</button></div>`;
}
function navItem({action, id, active, iconHtml, label, meta = ''}) {
  return `<button class="nav-item${active ? ' active' : ''}" type="button" data-action="${action}" data-id="${esc(id)}" ${active ? 'aria-current="page"' : ''}>
    ${iconHtml}<span class="nav-label">${esc(label)}</span>${meta !== '' ? `<span class="nav-meta">${meta}</span>` : ''}</button>`;
}

/* ---------- Barra lateral ---------- */
function sidebarHtml() {
  const projects = state.projects.map(p => navItem({
    action: 'project', id: p.id, active: state.project?.id === p.id, iconHtml: icon('folder'), label: p.name,
  })).join('');
  let html = `<nav class="side-section" aria-label="Projetos">
    <div class="side-head"><span class="side-label">Projetos</span>
      <button class="icon-btn sm" type="button" data-action="new-project" aria-label="Novo projeto" title="Novo projeto">${icon('plus')}</button></div>
    <div class="side-list">${projects || '<p class="side-empty">Nenhum projeto ainda.</p>'}</div></nav>`;

  if (state.project) {
    // "HQs" abre a página de HQs; a seta mostra/esconde as HQs dentro dele.
    const open = store.get('hq-nav-comics') !== '0';
    const comics = state.comics.map(c => navItem({
      action: 'comic', id: c.id, active: state.screen === 'comic' && state.comic?.id === c.id, iconHtml: icon('book'), label: c.title,
      meta: state.covers[c.id]?.count ?? '',
    })).join('');
    html += `<nav class="side-section" aria-label="Projeto"><div class="side-list">
        <div class="nav-group${open ? ' open' : ''}">
          <div class="nav-row">
            <button class="icon-btn sm nav-toggle" type="button" data-action="toggle-comics-nav" aria-expanded="${open}" aria-controls="nav-comics" title="${open ? 'Esconder' : 'Mostrar'} as HQs">${icon('chevronRight')}</button>
            ${navItem({action: 'comics', id: '', active: state.screen === 'comics', iconHtml: icon('panels'), label: 'HQs', meta: state.comics.length})}
            <button class="icon-btn sm" type="button" data-action="new-comic" aria-label="Nova HQ" title="Nova HQ">${icon('plus')}</button>
          </div>
          <div class="nav-sub" id="nav-comics" ${open ? '' : 'hidden'}>
            ${comics || '<button class="side-link" type="button" data-action="new-comic">Criar a primeira HQ</button>'}
          </div>
        </div>
        ${navItem({action: 'library', id: '', active: state.screen === 'library', iconHtml: icon('library'), label: 'Biblioteca', meta: state.assets.length})}
      </div></nav>`;
  }
  return html + `<div class="side-foot">${icon('hardDrive')}Dados salvos neste computador</div>`;
}

/* ---------- Tela inicial (sem projetos) ---------- */
function projectFields(prefix) {
  return `<div class="field"><label for="${prefix}-name">Nome do projeto</label>
      <input id="${prefix}-name" name="name" required maxlength="100" placeholder="Ex.: Especial de Natal" ${prefix === 'modal' ? 'autofocus' : ''}></div>
    <div class="field"><label for="${prefix}-style">Estilo padrão das HQs</label>
      <textarea id="${prefix}-style" name="style" rows="3" maxlength="800">${esc(DEFAULT_STYLE)}</textarea>
      <p class="help">Vem preenchido em cada HQ nova; cada HQ pode ter o próprio estilo (traço, cores, clima).</p></div>`;
}
function welcomeHtml() {
  return `<section class="welcome">
    <div class="welcome-art" aria-hidden="true"><span></span><span></span><span></span></div>
    <h1>Crie seu primeiro projeto</h1>
    <p class="lead">Um projeto guarda o estilo visual e a biblioteca de personagens, objetos e locais que você reaproveita em todas as HQs dele.</p>
    <form class="form card-form" data-form="project">
      ${projectFields('welcome')}
      <button class="btn primary lg" type="submit">Criar projeto</button>
    </form>
    <ol class="steps">
      <li><span class="num">1</span><span>Crie o projeto e defina o estilo.</span></li>
      <li><span class="num">2</span><span>Cadastre personagens, objetos e locais.</span></li>
      <li><span class="num">3</span><span>Escreva os quadros e gere as imagens.</span></li>
    </ol>
  </section>`;
}

/* ---------- Visão geral do projeto ---------- */
function comicCardHtml(c) {
  const info = state.covers[c.id];
  const cover = info?.cover ? `<img src="${esc(info.cover)}" alt="" loading="lazy">` : icon('panels');
  const meta = !info ? '' : info.count ? `${plural(info.count, 'quadro', 'quadros')} · ${info.done} com imagem` : 'Nenhum quadro ainda';
  return `<button class="comic-card" type="button" data-action="comic" data-id="${esc(c.id)}">
    <div class="comic-cover">${cover}</div>
    <div class="comic-info"><strong>${esc(c.title)}</strong><span>${meta}</span></div></button>`;
}
/* ---------- Página de HQs ---------- */
function hqCardHtml(c) {
  const info = state.covers[c.id];
  const id = esc(c.id);
  const cover = info?.cover ? `<img src="${esc(info.cover)}" alt="" loading="lazy">` : icon('panels');
  const meta = !info ? '' : info.count ? `${plural(info.count, 'quadro', 'quadros')} · ${info.done} com imagem` : 'Nenhum quadro ainda';
  const context = (c.context || '').trim();
  return `<article class="hq-card" data-hq-card="${id}">
    <button class="hq-cover" type="button" data-action="comic" data-id="${id}" aria-label="Abrir ${esc(c.title)}">${cover}</button>
    <div class="hq-body">
      <strong title="${esc(c.title)}">${esc(c.title)}</strong>
      <span class="hq-meta">${meta}</span>
      ${context ? `<p class="hq-context">${esc(context)}</p>` : ''}
    </div>
    <div class="hq-actions">
      <button class="btn primary sm" type="button" data-action="comic" data-id="${id}">${icon('book')}Abrir</button>
      <button class="icon-btn sm" type="button" data-action="comic-edit-open" data-id="${id}" title="Editar título, roteiro e figurinos" aria-label="Editar ${esc(c.title)}">${icon('pencil')}</button>
      <button class="icon-btn sm" type="button" data-action="export-comic" data-id="${id}" title="Exportar PDF" aria-label="Exportar ${esc(c.title)} em PDF" ${info?.done ? '' : 'disabled'}>${icon('download')}</button>
      <button class="icon-btn sm danger" type="button" data-action="comic-delete" data-id="${id}" title="Excluir HQ" aria-label="Excluir ${esc(c.title)}">${icon('trash')}</button>
    </div></article>`;
}
function comicsResultsHtml() {
  if (!state.comics.length) {
    return emptyHtml({iconName: 'panels', title: 'Nenhuma HQ ainda',
      text: 'Cada HQ tem seus próprios quadros, capa e créditos, e usa a biblioteca do projeto.',
      action: `<button class="btn primary" type="button" data-action="new-comic">${icon('plus')}Criar HQ</button>`});
  }
  const q = norm(state.comicsQuery.trim());
  const items = state.comics.filter(c => !q || norm(`${c.title} ${c.context || ''}`).includes(q));
  if (!items.length) {
    return emptyHtml({iconName: 'search', title: `Nada encontrado para “${esc(state.comicsQuery.trim())}”`,
      text: 'Busque pelo título ou por algo do roteiro.',
      action: `<button class="btn secondary" type="button" data-action="comics-clear">Limpar busca</button>`});
  }
  return `<div class="hq-grid">${items.map(hqCardHtml).join('')}
    ${q ? '' : `<button class="hq-card add" type="button" data-action="new-comic">${icon('plus')}<span>Nova HQ</span></button>`}</div>`;
}
function comicsHtml() {
  const p = state.project;
  return `<div class="page">
    <header class="page-head">
      <div><nav class="crumbs" aria-label="Você está em"><button type="button" data-action="overview">${esc(p.name)}</button>${icon('chevronRight')}<span>HQs</span></nav>
        <h1 class="page-title">HQs</h1>
        <p class="page-desc">Todas as HQs de <b>${esc(p.name)}</b>. Abra para continuar, edite o título e o roteiro, exporte em PDF ou exclua.</p></div>
      <div class="page-actions"><button class="btn primary" type="button" data-action="new-comic">${icon('plus')}Nova HQ</button></div>
    </header>
    ${state.comics.length ? `<div class="lib-toolbar"><span></span>
      <label class="search">${icon('search')}<span class="sr-only">Buscar HQs</span>
        <input type="search" id="comics-search" placeholder="Buscar por título ou roteiro" value="${esc(state.comicsQuery)}" autocomplete="off"></label></div>` : ''}
    <div id="comics-results">${comicsResultsHtml()}</div>
  </div>`;
}

/* Exporta qualquer HQ (da página de HQs ou de dentro dela) em PDF. */
async function exportComic(comic) {
  await flushSaves();
  const res = await fetch(`/api/comics/${comic.id}/export.pdf`);
  if (!res.ok) {
    let detail = `Erro ${res.status}`;
    try { detail = (await res.json()).detail || detail; } catch { /* resposta sem JSON */ }
    throw new Error(detail);
  }
  const skipped = Number(res.headers.get('X-Skipped-Frames') || 0);
  const url = URL.createObjectURL(await res.blob());
  const link = Object.assign(document.createElement('a'), {href: url, download: `${comic.title}.pdf`});
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10000);
  toast(skipped ? `PDF baixado. ${plural(skipped, 'quadro sem imagem ficou', 'quadros sem imagem ficaram')} de fora.` : 'PDF baixado');
}

function overviewHtml() {
  const p = state.project;
  const comics = state.comics.length
    ? `<div class="comic-grid">${state.comics.map(comicCardHtml).join('')}
        <button class="comic-card add" type="button" data-action="new-comic">${icon('plus')}<span>Nova HQ</span></button></div>`
    : emptyHtml({iconName: 'book', title: 'Nenhuma HQ neste projeto',
        text: 'Cada HQ tem sua própria sequência de quadros e usa a biblioteca do projeto.',
        action: `<button class="btn primary" type="button" data-action="new-comic">${icon('plus')}Criar HQ</button>`});
  const STRIP_MAX = 12;
  const extra = state.assets.length - STRIP_MAX;
  const library = state.assets.length
    ? `<div class="lib-strip">${state.assets.slice(0, STRIP_MAX).map(a =>
        `<button class="lib-chip kind-${esc(a.kind)}" type="button" data-action="asset" data-id="${esc(a.id)}" title="${esc(kindOf(a).label)}">${avatar(a, 'sm')}<span>${esc(a.name)}</span></button>`).join('')}
        ${extra > 0 ? `<button class="lib-chip more" type="button" data-action="library">+${extra} na biblioteca</button>` : ''}</div>`
    : emptyHtml({iconName: 'library', title: 'Biblioteca vazia',
        text: 'Cadastre personagens, objetos e locais com descrição e foto. Eles serão enviados à IA sempre que citados num quadro.',
        action: `<button class="btn primary" type="button" data-action="new-asset" data-kind="character">${icon('plus')}Novo personagem</button>`});
  return `<div class="page">
    <header class="page-head">
      <div><p class="eyebrow">Projeto</p><h1 class="page-title">${esc(p.name)}</h1>
        <p class="page-desc"><b>Estilo padrão das HQs:</b> ${esc(p.style) || '—'}</p></div>
      <div class="page-actions"><button class="btn primary" type="button" data-action="new-comic">${icon('plus')}Nova HQ</button></div>
    </header>
    <section class="section first">
      <div class="section-head"><h2>HQs <span class="count">${state.comics.length}</span></h2></div>
      ${comics}
    </section>
    <section class="section">
      <div class="section-head">
        <div><h2>Biblioteca <span class="count">${state.assets.length}</span></h2>
          <p class="section-desc">Compartilhada por todas as HQs do projeto. Cite o nome ou um apelido na descrição de um quadro e a ficha vai junto para a IA.</p></div>
        ${state.assets.length ? `<button class="btn secondary" type="button" data-action="library">${icon('library')}Abrir biblioteca</button>` : ''}
      </div>
      ${library}
    </section>
  </div>`;
}

/* ---------- Biblioteca ---------- */
const splitAliases = a => a.aliases.split(',').map(s => s.trim()).filter(Boolean);

/* Em quais HQs/quadros a referência é citada (mesma regra usada na geração). */
function usageOf(asset) {
  return state.comics.map(comic => ({
    comic,
    positions: (state.comicFrames[comic.id] || []).filter(f => castOf(f).some(c => c.asset.id === asset.id)).map(f => f.position),
  })).filter(u => u.positions.length);
}
const usageCount = asset => usageOf(asset).reduce((n, u) => n + u.positions.length, 0);

function libCardHtml(a) {
  const k = kindOf(a);
  const aliases = splitAliases(a);
  const uses = usageCount(a);
  const text = a.description || a.personality;
  return `<button class="lib-card kind-${esc(a.kind)}" type="button" data-action="asset" data-id="${esc(a.id)}" data-asset-card="${esc(a.id)}">
    <div class="lib-media">${a.image_path ? `<img src="${esc(a.image_path)}" alt="" loading="lazy">` : icon(k.icon)}</div>
    <div class="lib-body">
      <strong>${esc(a.name)}</strong>
      ${aliases.length ? `<span class="aliases">Também: ${esc(aliases.join(', '))}</span>` : ''}
      <p>${text ? esc(text) : '<span class="opt">Sem descrição</span>'}</p>
      <span class="lib-usage${uses ? ' used' : ''}">${icon('panels')}${uses ? `Em ${plural(uses, 'quadro', 'quadros')}` : 'Ainda não usado'}</span>
    </div></button>`;
}
function libraryResultsHtml() {
  if (!state.assets.length) {
    return emptyHtml({iconName: 'library', title: 'Sua biblioteca está vazia',
      text: 'Cadastre os personagens, objetos e locais das suas histórias. Quando você citar o nome deles num quadro, a ficha e a foto vão junto para a IA.',
      action: `<div class="page-actions">${Object.entries(KINDS).map(([kind, k], i) =>
        `<button class="btn ${i === 0 ? 'primary' : 'secondary'}" type="button" data-action="new-asset" data-kind="${kind}">${icon(k.icon)}${k.newLabel}</button>`).join('')}</div>`});
  }
  const q = norm(state.libQuery.trim());
  const matches = a => !q || norm([a.name, a.aliases, a.description, a.personality].join(' ')).includes(q);
  const kinds = state.libKind === 'all' ? Object.keys(KINDS) : [state.libKind];
  let total = 0;
  const groups = kinds.map(kind => {
    const k = KINDS[kind];
    const items = state.assets.filter(a => a.kind === kind && matches(a));
    total += items.length;
    if (q && !items.length) return '';
    const add = q ? '' : `<button class="lib-card add kind-${kind}" type="button" data-action="new-asset" data-kind="${kind}">${icon('plus')}<span>${k.newLabel}</span></button>`;
    const title = state.libKind === 'all'
      ? `<h2 class="lib-group-title kind-${kind}">${icon(k.icon)}${k.plural}<span class="count">${items.length}</span></h2>` : '';
    return `<section class="lib-group">${title}<div class="lib-grid">${items.map(libCardHtml).join('')}${add}</div></section>`;
  }).join('');
  if (q && !total) {
    return emptyHtml({iconName: 'search', title: `Nada encontrado para “${esc(state.libQuery.trim())}”`,
      text: 'Confira a grafia, busque por um apelido ou cadastre uma nova referência.',
      action: `<button class="btn secondary" type="button" data-action="lib-clear">Limpar busca</button>`});
  }
  return groups;
}
function libraryHtml() {
  const p = state.project;
  const counts = {all: state.assets.length};
  for (const kind of Object.keys(KINDS)) counts[kind] = state.assets.filter(a => a.kind === kind).length;
  const tabs = [['all', 'Todos', ''], ...Object.entries(KINDS).map(([kind, k]) => [kind, k.plural, k.icon])].map(([kind, label, ic]) =>
    `<button type="button" data-action="lib-kind" data-kind="${kind}" aria-pressed="${state.libKind === kind}" aria-label="${label} (${counts[kind]})">
      ${ic ? icon(ic) : ''}<span class="tab-text${ic ? ' hide-sm' : ''}">${label}</span><span class="tab-count">${counts[kind]}</span></button>`).join('');
  const newKind = state.libKind === 'all' ? 'character' : state.libKind;
  const nav = state.libraryReturn
    ? `<button class="back-link" type="button" data-action="comic" data-id="${esc(state.libraryReturn.id)}">${icon('arrowLeft')}Voltar para “${esc(state.libraryReturn.title)}”</button>`
    : `<nav class="crumbs" aria-label="Você está em"><button type="button" data-action="overview">${esc(p.name)}</button>${icon('chevronRight')}<span>Biblioteca</span></nav>`;
  return `<div class="page">
    <header class="page-head">
      <div>${nav}<h1 class="page-title">Biblioteca</h1>
        <p class="page-desc">Personagens, objetos e locais de <b>${esc(p.name)}</b>, disponíveis em todas as HQs do projeto. Cite o nome ou um apelido na descrição de um quadro e a ficha vai junto para a IA.</p></div>
      <div class="page-actions"><button class="btn primary" type="button" data-action="new-asset" data-kind="${newKind}">${icon('plus')}${KINDS[newKind].newLabel}</button></div>
    </header>
    ${state.assets.length ? `<div class="lib-toolbar">
      <div class="segmented tabs" role="group" aria-label="Filtrar por tipo">${tabs}</div>
      <label class="search">${icon('search')}<span class="sr-only">Buscar na biblioteca</span>
        <input type="search" id="lib-search" placeholder="Buscar por nome, apelido ou descrição" value="${esc(state.libQuery)}" autocomplete="off"></label>
    </div>` : ''}
    <div id="lib-results">${libraryResultsHtml()}</div>
  </div>`;
}

/* ---------- Editor da HQ ---------- */
const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
function matchingAssets(description, assets = state.assets) {
  const value = norm(description || '');
  return assets.filter(a => [a.name, ...a.aliases.split(',')].some(term => {
    const t = norm(term.trim()); if (!t) return false;
    const pos = value.indexOf(t); if (pos < 0) return false;
    const before = value[pos - 1] || ' ', after = value[pos + t.length] || ' ';
    return !/[a-z0-9]/.test(before) && !/[a-z0-9]/.test(after);
  }));
}
/* Elenco do quadro (mesma regra do servidor): citados no texto + incluídos à mão − removidos à mão. */
function castOf(f, entries = f.cast || []) {
  const byId = new Map(entries.map(c => [c.asset_id, c]));
  const detected = new Set(matchingAssets(f.description).map(a => a.id));
  return state.assets
    .filter(a => { const e = byId.get(a.id); return e ? e.included : detected.has(a.id); })
    .map(a => ({asset: a, role: byId.get(a.id)?.role || '', detected: detected.has(a.id)}))
    .sort((x, y) => (x.asset.kind !== 'character') - (y.asset.kind !== 'character'));
}
function refsHtml(f) {
  const cast = castOf(f);
  const edit = state.assets.length
    ? `<button class="ref-chip cast-edit" type="button" data-action="cast" data-id="${esc(f.id)}" title="Quem aparece e o papel de cada um">${icon('users')}${cast.length ? 'Elenco' : 'Definir elenco'}</button>` : '';
  if (cast.length) {
    return `<span class="refs-label">Elenco:</span>` + cast.map(({asset: a, role}) =>
      `<button class="ref-chip kind-${esc(a.kind)}" type="button" data-action="asset" data-id="${esc(a.id)}" title="${esc(role ? `${a.name}: ${role}` : `Ver ficha (${kindOf(a).label})`)}">${avatar(a, 'xs')}${esc(a.name)}${role ? `<small>${esc(role)}</small>` : ''}</button>`).join('') + edit;
  }
  const link = '<button class="link" type="button" data-action="library">biblioteca</button>';
  return state.assets.length
    ? `<span class="refs-hint">Cite nomes da ${link} ou</span>${edit}`
    : `<span class="refs-hint">Dica: cadastre personagens na ${link} para manter a consistência.</span>`;
}
function comicMetaHtml() {
  const n = state.frames.length;
  if (!n) return 'Nenhum quadro ainda';
  const done = state.frames.filter(f => f.image_path).length;
  const busy = state.frames.filter(isBusy).length;
  const errors = state.frames.filter(f => f.status === 'error').length;
  const parts = [plural(n, 'quadro', 'quadros'), `${done} com imagem`];
  if (busy) parts.push(`<span class="meta-busy"><span class="spinner xs"></span>${busy} gerando</span>`);
  if (errors) parts.push(`<span class="meta-err">${plural(errors, 'com erro', 'com erro')}</span>`);
  return parts.join('<span class="sep">·</span>');
}
function creditsHtml(f) {
  const c = f.credits || {};
  const lines = (c.lines || []).map(l => `<li><b>${esc(l.name)}</b>${l.role ? `<span>${esc(l.role)}</span>` : ''}</li>`).join('');
  return `<div class="credits-page"><h3>${esc(c.heading || 'Elenco')}</h3><p class="credits-title">${esc(state.comic?.title || '')}</p>
    <ul>${lines || '<li><span>Nenhum nome ainda</span></li>'}</ul>${c.footer ? `<p class="credits-footer">${esc(c.footer)}</p>` : ''}</div>`;
}
function previewHtml(f) {
  if (f.kind === 'credits') return `<button class="preview-btn credits-btn" type="button" data-action="credits" data-id="${esc(f.id)}" aria-label="Editar créditos">${creditsHtml(f)}</button>`;
  const busy = isBusy(f);
  let html = f.image_path
    ? `<button class="preview-btn" type="button" data-action="zoom" data-id="${esc(f.id)}" aria-label="Ampliar quadro ${f.position}">
         <span class="art"><img src="${esc(f.image_path)}" alt="Imagem do quadro ${f.position}" loading="lazy">${editorText() ? balloonLayerHtml(f.balloons, false, f.id) : ''}</span><span class="zoom-hint">${icon('maximize')}</span></button>`
    : `<div class="preview-empty">${busy ? '' : `${icon('image')}<span>Ainda sem imagem</span>`}</div>`;
  if (busy) {
    html += `<div class="preview-overlay"><span class="spinner"></span><span>${f.status === 'queued' ? 'Na fila…' : 'Gerando imagem…'}</span></div>`;
  } else if (f.status === 'error') {
    html += `<span class="badge err">${icon('alert')}Falhou</span>`;
  } else if (f.image_path && f.provider) {
    html += `<span class="badge" title="Gerado com ${esc(providerName(f.provider))}">${icon('check')}${esc(providerName(f.provider))}</span>`;
  }
  return html;
}
function toolsHtml(f) {
  const busy = isBusy(f);
  const i = state.frames.findIndex(x => x.id === f.id);
  const first = i <= 0, last = i === state.frames.length - 1;
  const n = f.position;
  return `<button class="icon-btn sm" type="button" data-action="move" data-id="${esc(f.id)}" data-direction="left" title="Mover para a esquerda" aria-label="Mover quadro ${n} para a esquerda" ${busy || first ? 'disabled' : ''}>${icon('chevronLeft')}</button>
    <button class="icon-btn sm" type="button" data-action="move" data-id="${esc(f.id)}" data-direction="right" title="Mover para a direita" aria-label="Mover quadro ${n} para a direita" ${busy || last ? 'disabled' : ''}>${icon('chevronRight')}</button>
    <button class="icon-btn sm" type="button" data-action="history" data-id="${esc(f.id)}" title="Versões anteriores" aria-label="Versões do quadro ${n}" ${f.image_path ? '' : 'disabled'}>${icon('history')}</button>
    <button class="icon-btn sm danger" type="button" data-action="delete" data-id="${esc(f.id)}" title="Excluir quadro" aria-label="Excluir quadro ${n}" ${busy ? 'disabled' : ''}>${icon('trash')}</button>`;
}
function actionsHtml(f) {
  const id = esc(f.id);
  if (isBusy(f)) {
    return `<button class="btn secondary block" type="button" disabled><span class="spinner xs"></span>${f.status === 'queued' ? 'Na fila…' : 'Gerando…'}</button>`;
  }
  if (!f.image_path) {
    const label = f.status === 'error' ? 'Tentar novamente' : f.kind === 'cover' ? 'Gerar capa' : 'Gerar quadro';
    return `<button class="btn primary block" type="button" data-action="generate" data-id="${id}" data-refine="false" title="Ctrl+Enter">${icon('sparkles')}${label}</button>`;
  }
  return `<button class="btn primary" type="button" data-action="generate" data-id="${id}" data-refine="true" title="Nova versão usando a imagem atual como base (Ctrl+Enter)">${icon('wand')}Refinar</button>
    <button class="btn secondary" type="button" data-action="generate" data-id="${id}" data-refine="false" title="Gerar uma imagem nova só a partir da descrição">${icon('refresh')}Gerar do zero</button>`;
}
function frameHtml(f) {
  const id = esc(f.id);
  const busy = isBusy(f);
  const head = `<header class="frame-head"><span class="frame-num">${f.position}</span><strong>${frameLabel(f)}</strong>
      <div class="frame-tools">${toolsHtml(f)}</div></header>`;
  if (f.kind === 'credits') {
    return `<article class="frame kind-credits" data-frame="${id}" data-sig="${esc(frameSig(f))}" aria-label="Créditos">${head}
      <div class="frame-preview">${previewHtml(f)}</div>
      <p class="help">Montados com os nomes da biblioteca, sem IA: nada de nome inventado. Entram no PDF como a última página.</p>
      <div class="frame-actions"><button class="btn primary block" type="button" data-action="credits" data-id="${id}">${icon('pencil')}Editar créditos</button></div></article>`;
  }
  const formats = Object.entries(FORMATS).map(([value, label]) => `<option value="${value}" ${f.format === value ? 'selected' : ''}>${label}</option>`).join('');
  return `<article class="frame${f.kind === 'cover' ? ' kind-cover' : ''}${busy ? ' is-busy' : ''}${f.status === 'error' ? ' is-error' : ''}" data-frame="${id}" data-sig="${esc(frameSig(f))}" aria-label="${frameLabel(f)}">
    ${head}
    <div class="frame-preview">${previewHtml(f)}</div>
    <div class="frame-error" role="alert" ${f.status === 'error' ? '' : 'hidden'}>${icon('alert')}<span>${esc(f.message || '')}</span></div>
    <div class="field">
      <div class="card-options">
        <select class="mini-select" data-kind="${id}" aria-label="Tipo do card" ${busy ? 'disabled' : ''}>
          <option value="panel" ${f.kind !== 'cover' ? 'selected' : ''}>Quadro</option><option value="cover" ${f.kind === 'cover' ? 'selected' : ''}>Capa</option></select>
        <select class="mini-select" data-format="${id}" aria-label="Formato da imagem" title="Formato da próxima imagem gerada">${formats}</select></div>
      <div class="field-row"><label for="scene-${id}">${f.kind === 'cover' ? 'Como é a capa?' : 'O que acontece neste quadro?'}</label><span class="save-state" data-save="${id}" aria-live="polite"></span></div>
      <textarea id="scene-${id}" rows="4" data-description="${id}" maxlength="6000" placeholder="${f.kind === 'cover' ? 'Ex.: Régis gigante e sombrio ao fundo, Rafa de Noel no carro cheio de presentes, Filipão esperançoso. O título vai em destaque.' : 'Ex.: Régis encara Brunão, que segura um panetone gigante…'}">${esc(f.description)}</textarea>
    </div>
    <div class="refs" data-refs="${id}">${refsHtml(f)}</div>
    <div class="attachments" data-attachments="${id}">${attachmentsHtml(f)}</div>
    <div class="card-attach">
      <label class="btn ghost sm" title="Anexar imagem a este card">${icon('paperclip')}Imagem
        <input class="sr-only" type="file" multiple accept="image/*" data-frame-file="${id}"></label>
      <button class="btn ghost sm" type="button" data-action="paste-image" title="Cola a imagem copiada (Ctrl+V na descrição também funciona)">${icon('clipboard')}Colar</button></div>
    ${editorText() ? `<div class="dialog" data-dialog="${id}">${dialogSummaryHtml(f)}</div>` : ''}
    <div class="refine" data-refine-box ${f.image_path ? '' : 'hidden'}>
      <label class="label" for="feedback-${id}">O que mudar na próxima versão? <span class="opt">opcional</span></label>
      <textarea id="feedback-${id}" rows="2" data-feedback="${id}" maxlength="2000" placeholder="Ex.: mantenha o cenário, mas deixe a expressão mais constrangida">${esc(f.feedback || '')}</textarea>
    </div>
    <div class="frame-actions">${actionsHtml(f)}</div>
  </article>`;
}
function readerHtml() {
  return `<div class="reader"><div class="comic-page">${state.frames.map(f => {
    if (f.kind === 'credits') return `<figure class="panel kind-credits"><figcaption>${f.position}</figcaption>${creditsHtml(f)}</figure>`;
    const busy = isBusy(f);
    const body = f.image_path
      ? `<button class="preview-btn" type="button" data-action="zoom" data-id="${esc(f.id)}" aria-label="Ampliar quadro ${f.position}"><span class="art"><img src="${esc(f.image_path)}" alt="Quadro ${f.position}" loading="lazy">${editorText() ? balloonLayerHtml(f.balloons, false, f.id) : ''}</span></button>`
      : `<div class="panel-empty">${busy ? `<span class="status-line"><span class="spinner xs"></span>${f.status === 'queued' ? 'Na fila' : 'Gerando'}</span>` : ''}
           <p>${esc(f.description) || 'Quadro sem descrição'}</p></div>`;
    return `<figure class="panel${f.kind === 'cover' ? ' kind-cover' : ''}"><figcaption>${f.position}</figcaption>${body}</figure>`;
  }).join('')}</div></div>`;
}
function contextCardHtml() {
  const context = (state.comic.context || '').trim();
  if (!context) {
    return `<div class="context-card empty-context">${icon('book')}
      <p><b>Sem roteiro.</b> Conte do que se trata esta HQ para a IA entender a história e gerar quadros mais coerentes.</p>
      <button class="btn secondary sm" type="button" data-action="edit-comic">${icon('plus')}Adicionar roteiro</button></div>`;
  }
  const long = context.length > 260 || context.split('\n').length > 3;
  return `<section class="context-card">
    <div class="context-head">${icon('book')}<h2>Roteiro e contexto</h2><span class="context-note">enviado à IA em todos os quadros</span>
      <button class="btn ghost sm" type="button" data-action="edit-comic">${icon('pencil')}Editar</button></div>
    <p class="context-text">${esc(context)}</p>
    ${long ? '<button class="link context-more" type="button" data-action="toggle-context">Mostrar tudo</button>' : ''}
  </section>`;
}
function comicHtml() {
  const edit = state.view === 'edit';
  let body;
  if (!state.frames.length) {
    body = emptyHtml({iconName: 'panels', title: 'Nenhum quadro ainda',
      text: 'Cada card é um quadro (ou a capa). Escreva o que acontece, com as falas entre aspas, e gere. Ao gerar, os cards anteriores vão junto como contexto da história.',
      action: `<button class="btn primary" type="button" data-action="add-frame">${icon('plus')}Adicionar primeiro card</button>`});
  } else if (edit) {
    body = tipHtml('cards', 'Cada card é um quadro ou a capa: escolha o tipo, escreva o que acontece (falas entre aspas) e clique em <b>Gerar</b> (ou <kbd>Ctrl</kbd>+<kbd>Enter</kbd>). Os cards anteriores vão junto como contexto. Para corrigir, escreva em “O que mudar” e use <b>Refinar</b>. Cole imagens com <kbd>Ctrl</kbd>+<kbd>V</kbd> na descrição do card.')
      + `<div class="timeline" id="timeline">${state.frames.map(frameHtml).join('')}
        <button class="add-frame" type="button" data-action="add-frame">${icon('plus')}<span>Novo quadro</span></button></div>`;
  } else {
    body = `<div id="reader" data-sig="${esc(state.frames.map(frameSig).join(';'))}">${readerHtml()}</div>`;
  }
  return `<div class="page wide">
    <header class="page-head">
      <div><nav class="crumbs" aria-label="Você está em"><button type="button" data-action="overview">${esc(state.project.name)}</button>${icon('chevronRight')}<span>HQ</span></nav>
        <h1 class="page-title">${esc(state.comic.title)}</h1>
        <p class="page-meta" id="comic-meta">${comicMetaHtml()}</p>
        <p class="comic-style"><b>Estilo visual:</b> ${esc(state.comic.style || state.project.style) || '—'}
          <button class="link" type="button" data-action="edit-comic">alterar</button></p></div>
      <div class="page-actions">
        <div class="segmented" role="group" aria-label="Quem escreve os balões" title="Vale para todas as HQs do projeto">
          <button type="button" data-action="text-mode" data-mode="ai" aria-pressed="${!editorText()}" title="A IA desenha balões e narração na imagem, com as falas que você escrever">${icon('sparkles')}IA desenha balões</button>
          <button type="button" data-action="text-mode" data-mode="editor" aria-pressed="${editorText()}" title="A imagem vem sem texto e você posiciona os balões no editor">${icon('speech')}Eu posiciono</button>
        </div>
        <div class="segmented" role="group" aria-label="Modo de visualização">
          <button type="button" data-action="view" data-view="edit" aria-pressed="${edit}">${icon('pencil')}Editar</button>
          <button type="button" data-action="view" data-view="read" aria-pressed="${!edit}">${icon('eye')}Ler</button>
        </div>
        <button class="btn secondary" type="button" data-action="add-credits" title="Página de créditos com os nomes da biblioteca">${icon('users')}Créditos</button>
        <button class="btn primary" type="button" data-action="export-pdf" title="Uma página por quadro, pronta para mandar">${icon('download')}Exportar PDF</button>
      </div>
    </header>
    ${contextCardHtml()}
    ${body}
  </div>`;
}

/* ---------- Anexos: imagens que o autor manda junto com o texto ---------- */
const MAX_ATTACHMENTS = 4;
function attachmentsHtml(f) {
  const list = f.attachments || [];
  if (!list.length) return '';
  return `<span class="refs-label">${icon('paperclip')}Anexos:</span>${list.map((a, i) => `<span class="thumb">
      <img src="${esc(a.image_path)}" alt="Anexo ${i + 1}">
      <button type="button" class="thumb-x" data-action="attachment-delete" data-id="${esc(f.id)}" data-att="${esc(a.id)}" title="Tirar anexo" aria-label="Tirar anexo ${i + 1}">${icon('x')}</button></span>`).join('')}`;
}
async function attachToFrame(id, files) {
  const f = frameById(id);
  if ((f.attachments || []).length + files.length > MAX_ATTACHMENTS) throw new Error(`Cada card aceita até ${MAX_ATTACHMENTS} imagens anexadas.`);
  await uploadAttachments(id, files);
  toast(`${plural(files.length, 'imagem anexada', 'imagens anexadas')} ao ${f.kind === 'cover' ? 'card da capa' : `quadro ${f.position}`}`);
}
function renderAttachments(f) {
  const box = $(`[data-attachments="${f.id}"]`);
  if (box) box.innerHTML = attachmentsHtml(f);
}
const imageFiles = list => [...(list || [])].filter(f => /^image\/(png|jpeg|webp)$/.test(f.type));
/* Imagens copiadas de outros apps (Slack, navegador, print) chegam de jeitos diferentes:
   como arquivo, como item da área de transferência ou como HTML com <img>. Junta tudo e
   converte o que não for PNG/JPG/WebP (GIF, BMP…) para PNG. */
async function toSupportedImage(blob, name = 'colada') {
  if (/^image\/(png|jpeg|webp)$/.test(blob.type)) return blob instanceof File ? blob : new File([blob], `${name}.${blob.type.split('/')[1]}`, {type: blob.type});
  const bitmap = await createImageBitmap(blob);
  const canvas = Object.assign(document.createElement('canvas'), {width: bitmap.width, height: bitmap.height});
  canvas.getContext('2d').drawImage(bitmap, 0, 0);
  const png = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
  return new File([png], `${name}.png`, {type: 'image/png'});
}
function htmlImageSources(html) {
  if (!html) return [];
  return [...new DOMParser().parseFromString(html, 'text/html').querySelectorAll('img[src]')].map(img => img.src);
}
async function imagesFromSources(sources) {
  const out = [];
  for (const src of sources) {
    try {
      const res = await fetch(src);
      const blob = await res.blob();
      if (res.ok && blob.type.startsWith('image/')) out.push(await toSupportedImage(blob));
    } catch { /* imagem protegida (ex.: arquivo privado do Slack): tratada na mensagem abaixo */ }
  }
  if (sources.length && !out.length) {
    throw new Error('Não deu para pegar essa imagem: o site onde ela está não deixa. No Slack, abra a imagem e use “Copiar imagem”, ou baixe e arraste o arquivo para cá.');
  }
  return out;
}
// HTML com <img> só conta quando não veio texto junto: assim colar uma mensagem com emojis continua colando o texto.
const hasClipboardImage = dt => [...(dt?.items || [])].some(i => i.kind === 'file' && i.type.startsWith('image/'))
  || (/<img\s/i.test(dt?.getData?.('text/html') || '') && !(dt.getData('text/plain') || '').trim());
async function clipboardImages(dt) {
  const blobs = [...(dt.items || [])].filter(i => i.kind === 'file' && i.type.startsWith('image/')).map(i => i.getAsFile()).filter(Boolean);
  if (blobs.length) return Promise.all(blobs.map(b => toSupportedImage(b)));
  return imagesFromSources(htmlImageSources(dt.getData('text/html')));
}
async function readClipboardImages() {
  if (!navigator.clipboard?.read) throw new Error('Este navegador não deixa ler a área de transferência por botão. Use Ctrl+V.');
  let items;
  try { items = await navigator.clipboard.read(); }
  catch { throw new Error('O navegador não liberou a área de transferência. Permita o acesso ou use Ctrl+V.'); }
  const files = [], sources = [];
  for (const item of items) {
    const type = item.types.find(t => t.startsWith('image/'));
    if (type) files.push(await toSupportedImage(await item.getType(type)));
    else if (item.types.includes('text/html')) sources.push(...htmlImageSources(await (await item.getType('text/html')).text()));
  }
  if (!files.length) files.push(...await imagesFromSources(sources));
  if (!files.length) throw new Error('Não há imagem copiada. Copie uma imagem (no Slack: abra a imagem e “Copiar imagem”) e tente de novo.');
  return files;
}
async function uploadAttachments(frameId, files) {
  let frame;
  for (const file of files) {
    const data = new FormData();
    data.append('image', file, file.name || 'colada.png');
    frame = await api(`/frames/${frameId}/attachments`, {method: 'POST', body: data});
  }
  if (frame) {
    const f = frameById(frameId);
    if (f) { f.attachments = frame.attachments; renderAttachments(f); }
  }
}
/* ---------- Créditos ---------- */
function creditRowHtml(line = {name: '', role: ''}) {
  return `<li class="credit-row"><input data-credit-name maxlength="120" value="${esc(line.name)}" placeholder="Nome" aria-label="Nome">
    <input data-credit-role maxlength="300" value="${esc(line.role)}" placeholder="Papel (ex.: O Noel do Paraguai)" aria-label="Papel">
    <button type="button" class="icon-btn sm danger" data-action="credit-remove" aria-label="Tirar linha">${icon('x')}</button></li>`;
}
function openCredits(id) {
  const f = frameById(id);
  const c = f.credits || {};
  openModal(modalShell('Créditos', `<form class="form" data-form="credits" data-id="${esc(id)}">
      <div class="field"><label for="credit-heading">Título da página</label><input id="credit-heading" name="heading" maxlength="120" value="${esc(c.heading || 'Elenco')}"></div>
      <div class="field"><span class="label">Personagens</span><ul class="credit-list" data-credit-list>${(c.lines || []).map(creditRowHtml).join('')}</ul>
        <div class="credit-tools"><button class="btn secondary sm" type="button" data-action="credit-add">${icon('plus')}Linha</button>
          <button class="btn ghost sm" type="button" data-action="credit-sync" title="Acrescenta quem está na biblioteca e ainda não aparece aqui">${icon('library')}Puxar da biblioteca</button></div></div>
      <div class="field"><label for="credit-footer">Rodapé <span class="opt">opcional</span></label>
        <textarea id="credit-footer" name="footer" rows="2" maxlength="1000" placeholder="Ex.: Gabriel — o grande diretor e sol nas horas vagas">${esc(c.footer || '')}</textarea></div>
      <div class="modal-foot"><button class="btn secondary" type="button" data-action="close-modal">Cancelar</button>
        <button class="btn primary" type="submit">Salvar créditos</button></div></form>`,
    'Só o que você escrever aqui aparece na página.'), {size: 'lg'});
}

/* ---------- Render ---------- */
function renderSidebar() { $('#sidebar').innerHTML = sidebarHtml(); }
function renderMain({top = false} = {}) {
  const main = $('#main');
  const screen = !state.project ? 'welcome' : state.screen === 'comic' && !state.comic ? 'overview' : state.screen;
  main.innerHTML = {welcome: welcomeHtml, library: libraryHtml, comic: comicHtml, comics: comicsHtml}[screen]?.() ?? overviewHtml();
  if (top) main.scrollTop = 0;
  const title = screen === 'comic' ? state.comic.title : screen === 'library' ? `Biblioteca · ${state.project.name}`
    : screen === 'comics' ? `HQs · ${state.project.name}` : state.project?.name;
  document.title = title ? `${title} · HQ Studio` : 'HQ Studio';
}
function render(opts) { renderSidebar(); renderMain(opts); }

/* Atualiza só o que mudou nos cartões, sem recriar os campos de texto. */
function refreshFrames() {
  const meta = $('#comic-meta');
  if (meta) meta.innerHTML = comicMetaHtml();
  const reader = $('#reader');
  if (reader) {
    const sig = state.frames.map(frameSig).join(';');
    if (reader.dataset.sig !== sig) { reader.dataset.sig = sig; reader.innerHTML = readerHtml(); }
    return;
  }
  for (const f of state.frames) {
    const card = $(`[data-frame="${f.id}"]`);
    if (!card) continue;
    const sig = frameSig(f);
    if (card.dataset.sig === sig) continue;
    card.dataset.sig = sig;
    card.classList.toggle('is-busy', isBusy(f));
    card.classList.toggle('is-error', f.status === 'error');
    $('.frame-tools', card).innerHTML = toolsHtml(f);
    $('.frame-preview', card).innerHTML = previewHtml(f);
    const error = $('.frame-error', card);
    error.hidden = f.status !== 'error';
    $('span', error).textContent = f.message || '';
    $('[data-refine-box]', card).hidden = !f.image_path;
    $('.frame-actions', card).innerHTML = actionsHtml(f);
  }
}

/* ---------- Dados ---------- */
const summarize = frames => ({
  count: frames.length,
  done: frames.filter(f => f.image_path).length,
  cover: (frames.find(f => f.kind === 'cover' && f.image_path) || frames.find(f => f.image_path))?.image_path || null,
});
async function loadCovers() {
  const entries = await Promise.all(state.comics.map(async c => {
    try { return [c.id, await api(`/comics/${c.id}/frames`)]; } catch { return [c.id, null]; }
  }));
  state.comicFrames = Object.fromEntries(entries.filter(([, frames]) => frames));
  state.covers = Object.fromEntries(entries.map(([id, frames]) => [id, frames ? summarize(frames) : null]));
}
function updateCover() {
  if (!state.comic) return;
  state.covers[state.comic.id] = summarize(state.frames);
  state.comicFrames[state.comic.id] = state.frames;
}

/* Mantém o que o usuário digitou e ainda não foi salvo. */
function mergeLocal(frames) {
  const local = new Map(state.frames.map(f => [f.id, f]));
  return frames.map(f => {
    const old = local.get(f.id);
    if (!old) return f;
    return {...f, description: saveTimers.has(f.id) ? old.description : f.description, feedback: old.feedback ?? f.feedback,
      balloons: balloonEditor?.frameId === f.id ? old.balloons : f.balloons};
  });
}
async function reloadFrames() {
  state.frames = mergeLocal(await api(`/comics/${state.comic.id}/frames`));
  updateCover();
}

async function loadProject(id, {restoreComic = false} = {}) {
  const reset = {comic: null, frames: [], screen: 'overview', libraryReturn: null, libKind: 'all', libQuery: ''};
  if (!id) {
    Object.assign(state, reset, {project: null, comics: [], assets: [], covers: {}, comicFrames: {}});
    render({top: true});
    return;
  }
  const [project, comics, assets] = await Promise.all([api(`/projects/${id}`), api(`/projects/${id}/comics`), api(`/projects/${id}/assets`)]);
  Object.assign(state, reset, {project, comics, assets});
  store.set('hq-project', id);
  await loadCovers();
  const last = restoreComic ? store.get(`hq-comic-${id}`) : null;
  if (last && comics.some(c => c.id === last)) await loadComic(last);
  else { store.del(`hq-comic-${id}`); render({top: true}); }
}
async function loadComic(id) {
  const comic = state.comics.find(c => c.id === id);
  if (!comic) return;
  const frames = await api(`/comics/${id}/frames`);
  Object.assign(state, {comic, frames, screen: 'comic', libraryReturn: null});
  store.set(`hq-comic-${state.project.id}`, id);
  updateCover();
  render({top: true});
}

/* ---------- Salvamento automático ---------- */
const saveFadeTimers = new Map();
function setSaveState(id, mode) {
  const el = $(`[data-save="${id}"]`);
  if (!el) return;
  clearTimeout(saveFadeTimers.get(id));
  el.classList.remove('err', 'fade');
  if (mode === 'saving') el.textContent = 'Salvando…';
  else if (mode === 'error') { el.classList.add('err'); el.textContent = 'Não foi salvo'; }
  else if (mode === 'saved') {
    el.innerHTML = `${icon('check')}Salvo`;
    saveFadeTimers.set(id, setTimeout(() => el.classList.add('fade'), 1800));
  } else el.textContent = '';
}
async function saveDescription(id) {
  clearTimeout(saveTimers.get(id));
  saveTimers.delete(id);
  const el = $(`[data-description="${id}"]`);
  const description = el ? el.value : frameById(id)?.description;
  if (description == null) return;
  setSaveState(id, 'saving');
  try {
    const saved = await api(`/frames/${id}`, json('PATCH', {description}));
    const f = frameById(id);
    if (f && !saveTimers.has(id)) f.description = saved.description;
    setSaveState(id, 'saved');
  } catch (error) {
    setSaveState(id, 'error');
    throw error;
  }
}
const flushSaves = () => Promise.all([...saveTimers.keys()].map(saveDescription));

/* ---------- Formulários (modais) ---------- */
function projectFormHtml() {
  return modalShell('Novo projeto', `<form class="form" data-form="project">
    ${projectFields('modal')}
    <div class="modal-foot"><button class="btn secondary" type="button" data-action="close-modal">Cancelar</button>
      <button class="btn primary" type="submit">Criar projeto</button></div></form>`,
    'Guarda o estilo visual e a biblioteca de referências das suas HQs.');
}
const CONTEXT_PH = 'Ex.: Na ceia de Natal da família, Régis (que odeia o Natal) tenta passar despercebido. Brunão, o primo desastrado, chega com um panetone gigante e tudo dá errado. Tom: comédia constrangedora. Começo: chegada na casa da vó; meio: briga pelo panetone; fim: todos rindo da bagunça.';
function comicFormHtml(comic = null) {
  const edit = !!comic;
  return modalShell(edit ? 'Editar HQ' : 'Nova HQ', `<form class="form" data-form="${edit ? 'comic-edit' : 'comic'}" ${edit ? `data-id="${esc(comic.id)}"` : ''}>
    <div class="field"><label for="comic-title">Título da história</label>
      <input id="comic-title" name="title" required maxlength="120" placeholder="Ex.: A ceia constrangedora" value="${esc(comic?.title || '')}" ${edit ? '' : 'autofocus'}></div>
    <div class="field"><label for="comic-style">Estilo visual desta HQ</label>
      <textarea id="comic-style" name="style" rows="2" maxlength="800" placeholder="Ex.: HQ de heróis semirrealista, cores vibrantes">${esc(comic?.style ?? state.project.style ?? '')}</textarea>
      <p class="help">Traço, cores e clima só desta HQ. As fotos e fichas da biblioteca do projeto continuam valendo.</p></div>
    <div class="field"><label for="comic-context">Roteiro e contexto <span class="opt">opcional</span></label>
      <textarea id="comic-context" name="context" rows="7" maxlength="6000" placeholder="${esc(CONTEXT_PH)}" ${edit ? 'autofocus' : ''}>${esc(comic?.context || '')}</textarea>
      <p class="help">Vai junto para a IA em todos os quadros desta HQ. Conte do que se trata a história, o tom, onde e quando acontece e como os personagens se relacionam.</p></div>
    ${costumeFieldsHtml(comic)}
    <div class="modal-foot"><button class="btn secondary" type="button" data-action="close-modal">Cancelar</button>
      <button class="btn primary" type="submit">${edit ? 'Salvar' : 'Criar HQ'}</button></div></form>`,
    `No projeto <b>${esc(state.project.name)}</b>, com a mesma biblioteca de referências.`, );
}
function costumeFieldsHtml(comic) {
  const characters = state.assets.filter(a => a.kind === 'character');
  if (!characters.length) return '';
  const costumes = comic?.costumes || {};
  return `<fieldset class="field costumes"><legend>Figurino nesta HQ <span class="opt">opcional</span></legend>
    <p class="help">Roupa ou visual que o personagem usa só nesta história. O rosto continua vindo das fotos da ficha.</p>
    <div class="costume-list">${characters.map(a => `<label class="costume-row">${avatar(a, 'xs')}<span>${esc(a.name)}</span>
      <input name="costume:${esc(a.id)}" maxlength="600" value="${esc(costumes[a.id] || '')}" placeholder="Ex.: roupa de Papai Noel"></label>`).join('')}</div></fieldset>`;
}
const costumesFrom = data => Object.fromEntries([...data.entries()]
  .filter(([key]) => key.startsWith('costume:')).map(([key, value]) => [key.slice(8), String(value)]));

function assetFormHtml(kind = 'character', asset = null) {
  if (asset) kind = asset.kind;
  if (!KINDS[kind]) kind = 'character';
  const k = KINDS[kind];
  const kinds = Object.entries(KINDS).map(([value, opt]) =>
    `<label class="kind-opt kind-${value}"><input type="radio" name="kind" value="${value}" ${value === kind ? 'checked' : ''}><span>${icon(opt.icon)}${opt.label}</span></label>`).join('');
  const v = field => esc(asset?.[field] || '');
  const photos = asset ? '' : `<div class="field"><span class="label">Fotos de referência <span class="opt">opcional, até 12</span></span>
      <label class="photo-drop"><input class="sr-only" type="file" name="images" multiple accept="image/png,image/jpeg,image/webp" data-photo>
        <span class="photo-preview">${icon('upload')}</span>
        <span class="photo-text"><strong data-photo-name>Escolher imagens</strong><small>Rosto de frente, de perfil e sorrindo ajudam a IA a reconhecer. Dá para colar com Ctrl+V.</small></span></label>
      <button class="btn ghost sm paste-btn" type="button" data-action="paste-image">${icon('clipboard')}Colar imagem copiada</button></div>`;
  const traits = kind === 'character' ? 'Ex.: rosto redondo mas corpo normal, não é gordo; barba rala; cabelo preto curto' : 'Ex.: logotipo sempre visível; cor vermelha';
  return modalShell(asset ? `Editar ${esc(asset.name)}` : k.newLabel, `<form class="form" data-form="${asset ? 'asset-edit' : 'asset'}" ${asset ? `data-id="${esc(asset.id)}"` : ''}>
    ${asset ? '' : `<fieldset class="field"><legend>Tipo</legend><div class="kind-picker">${kinds}</div></fieldset>`}
    <div class="grid-2">
      <div class="field"><label for="asset-name">Nome</label><input id="asset-name" name="name" maxlength="100" required placeholder="${esc(k.namePh)}" value="${v('name')}" autofocus></div>
      <div class="field"><label for="asset-aliases">Apelidos <span class="opt">opcional</span></label><input id="asset-aliases" name="aliases" maxlength="600" placeholder="Ex.: Reginho, Regis" value="${v('aliases')}"></div>
    </div>
    <p class="help">O nome e os apelidos (separados por vírgula) colocam a ficha no elenco quando aparecem na descrição de um quadro. Papéis também servem de apelido (ex.: “Noel”).</p>
    <div class="field"><label for="asset-desc">Aparência <span class="opt">opcional</span></label>
      <textarea id="asset-desc" name="description" rows="3" maxlength="2000" placeholder="${esc(k.descPh)}">${v('description')}</textarea>
      <p class="help">As fotos já servem de referência visual. Use este campo para detalhes que elas não mostram.</p></div>
    <div class="grid-2">
      <div class="field"><label for="asset-traits">Nunca pode mudar <span class="opt">opcional</span></label>
        <textarea id="asset-traits" name="traits" rows="2" maxlength="1000" placeholder="${esc(traits)}">${v('traits')}</textarea></div>
      <div class="field"><label for="asset-avoid">Erros a evitar <span class="opt">opcional</span></label>
        <textarea id="asset-avoid" name="avoid" rows="2" maxlength="1000" placeholder="Ex.: deixar gordo demais; confundir com o Rafa">${v('avoid')}</textarea></div>
    </div>
    <div class="field"><label for="asset-personality">Personalidade ou comportamento <span class="opt">opcional</span></label>
      <textarea id="asset-personality" name="personality" rows="2" maxlength="2000" placeholder="Ex.: mal-humorado, odeia o Natal">${v('personality')}</textarea></div>
    ${photos}
    <div class="modal-foot"><button class="btn secondary" type="button" data-action="${asset ? 'asset' : 'close-modal'}" ${asset ? `data-id="${esc(asset.id)}"` : ''}>Cancelar</button>
      <button class="btn primary" type="submit" data-save-label>${asset ? 'Salvar alterações' : k.saveLabel}</button></div></form>`,
    asset ? kindTag(asset) : `Fica na biblioteca de <b>${esc(state.project.name)}</b>, disponível para todas as HQs do projeto.`);
}
function applyKindToForm(form, kind) {
  const k = KINDS[kind];
  if (!k) return;
  $('#modal-title').textContent = k.newLabel;
  $('[data-save-label]', form).textContent = k.saveLabel;
  $('#asset-name', form).placeholder = k.namePh;
  $('#asset-desc', form).placeholder = k.descPh;
}
function previewPhoto(input) {
  const drop = input.closest('.photo-drop');
  const files = [...(input.files || [])];
  const preview = $('.photo-preview', drop), name = $('[data-photo-name]', drop);
  if (files.length > 12) { input.value = ''; fail(new Error('Escolha até 12 fotos.')); }
  const chosen = [...(input.files || [])];
  if (chosen.length) {
    preview.innerHTML = `<img src="${URL.createObjectURL(chosen[0])}" alt="">`;
    name.textContent = chosen.length === 1 ? chosen[0].name : plural(chosen.length, 'foto', 'fotos');
  } else {
    preview.innerHTML = icon('upload');
    name.textContent = 'Escolher imagens';
  }
}

/* ---------- Modais de leitura ---------- */
function openAsset(id) {
  const a = state.assets.find(x => x.id === id);
  if (!a) return;
  const k = kindOf(a);
  const aliases = splitAliases(a);
  const block = (title, text) => `<div class="detail-block"><h3>${title}</h3>${text ? `<p>${esc(text)}</p>` : '<p class="none">Não informado</p>'}</div>`;
  const uses = usageOf(a);
  const usage = `<div class="detail-block"><h3>Aparece em</h3>${uses.length
    ? `<ul class="usage-list">${uses.map(u => `<li><button class="usage-link" type="button" data-action="comic" data-id="${esc(u.comic.id)}">
        ${icon('book')}<span>${esc(u.comic.title)}</span><small>${u.positions.length === 1 ? 'quadro' : 'quadros'} ${u.positions.join(', ')}</small></button></li>`).join('')}</ul>`
    : '<p class="none">Ainda não foi citado em nenhum quadro.</p>'}</div>`;
  const photos = a.photos || [];
  const gallery = `<div class="photo-grid">${photos.map((ph, i) => `<figure class="photo-tile${i === 0 ? ' principal' : ''}">
      <img src="${esc(ph.image_path)}" alt="Foto ${i + 1} de ${esc(a.name)}" loading="lazy">
      ${i === 0 ? `<span class="photo-tag">${icon('star')}Principal</span>` : ph.source === 'frame' ? `<span class="photo-tag">${icon('crop')}De um quadro</span>` : ''}
      <div class="photo-actions">
        ${i === 0 ? '' : `<button class="icon-btn sm" type="button" data-action="photo-principal" data-id="${esc(a.id)}" data-photo="${esc(ph.id)}" title="Usar como principal" aria-label="Usar foto ${i + 1} como principal">${icon('star')}</button>`}
        <button class="icon-btn sm danger" type="button" data-action="photo-delete" data-id="${esc(a.id)}" data-photo="${esc(ph.id)}" title="Excluir foto" aria-label="Excluir foto ${i + 1}">${icon('trash')}</button>
      </div></figure>`).join('')}
    ${photos.length < 12 ? `<label class="photo-tile add" title="Adicionar fotos"><input class="sr-only" type="file" multiple accept="image/*" data-add-photo="${esc(a.id)}">${icon('plus')}<span>Foto</span></label>
      <button class="photo-tile add" type="button" data-action="paste-image" title="Cola a imagem copiada (Ctrl+V também funciona)">${icon('clipboard')}<span>Colar</span></button>` : ''}</div>`;
  const body = `<div class="asset-detail kind-${esc(a.kind)}">
    <div class="asset-detail-media">${a.image_path ? `<img src="${esc(a.image_path)}" alt="Foto principal de ${esc(a.name)}">` : icon(k.icon)}</div>
    <div class="asset-detail-body">
      <div class="detail-block"><h3>Fotos de referência <span class="count">${photos.length}</span></h3>${gallery}
        <p class="help">Até 3 fotos por personagem vão para a IA, a principal primeiro. No quadro ampliado, “Aprovar visual” guarda um recorte aqui.</p></div>
      ${aliases.length ? `<div class="detail-block"><h3>Também chamado de</h3><div class="chips">${aliases.map(x => `<span class="chip">${esc(x)}</span>`).join('')}</div></div>` : ''}
      ${block('Aparência', a.description)}
      ${a.traits ? block('Nunca pode mudar', a.traits) : ''}
      ${a.avoid ? block('Erros a evitar', a.avoid) : ''}
      ${block('Personalidade ou comportamento', a.personality)}
      ${usage}
      <div class="modal-foot detail-foot">
        <button class="btn ghost danger-text" type="button" data-action="asset-delete" data-id="${esc(a.id)}">${icon('trash')}Excluir ficha</button>
        <button class="btn secondary" type="button" data-action="asset-edit" data-id="${esc(a.id)}">${icon('pencil')}Editar</button></div>
    </div></div>`;
  openModal(modalShell(esc(a.name), body, kindTag(a)), {size: 'lg'});
}
function replaceAsset(asset) {
  state.assets = state.assets.map(a => a.id === asset.id ? asset : a);
  render();
}

/* ---------- Elenco do quadro ---------- */
let castDraft = null;   // {frameId, entries: Map(asset_id → {included, role})}
function castModalHtml() {
  const f = frameById(castDraft.frameId);
  const detected = new Set(matchingAssets(f.description).map(a => a.id));
  const entries = [...castDraft.entries].map(([asset_id, e]) => ({asset_id, ...e}));
  const cast = castOf(f, entries);
  const inCast = new Set(cast.map(c => c.asset.id));
  const removed = state.assets.filter(a => detected.has(a.id) && !inCast.has(a.id));
  const others = state.assets.filter(a => !inCast.has(a.id) && !detected.has(a.id));
  const rows = cast.map(({asset: a, role, detected: auto}) => `<li class="cast-row kind-${esc(a.kind)}">${avatar(a, 'sm')}
      <div class="cast-name"><strong>${esc(a.name)}</strong><small>${auto ? 'citado na descrição' : 'adicionado à mão'}${(a.photos || []).length ? ` · ${plural(Math.min(a.photos.length, 3), 'foto', 'fotos')}` : ' · sem foto'}</small></div>
      <input data-cast-role="${esc(a.id)}" maxlength="300" value="${esc(role)}" placeholder="Papel na cena (ex.: Noel ao volante)" aria-label="Papel de ${esc(a.name)} neste quadro">
      <button class="icon-btn sm danger" type="button" data-action="cast-remove" data-id="${esc(a.id)}" title="Tirar do quadro" aria-label="Tirar ${esc(a.name)} do quadro">${icon('x')}</button></li>`).join('');
  const removedHtml = removed.length ? `<div class="cast-removed"><span class="label">Citados mas fora do quadro:</span>${removed.map(a =>
      `<button class="ref-chip kind-${esc(a.kind)} off" type="button" data-action="cast-restore" data-id="${esc(a.id)}" title="Voltar para o quadro">${avatar(a, 'xs')}${esc(a.name)}${icon('undo')}</button>`).join('')}</div>` : '';
  const add = others.length ? `<label class="cast-add">${icon('plus')}<span class="sr-only">Adicionar ao quadro</span>
      <select data-cast-add><option value="">Adicionar ao quadro…</option>${others.map(a => `<option value="${esc(a.id)}">${esc(a.name)} (${esc(kindOf(a).label)})</option>`).join('')}</select></label>` : '';
  return modalShell(`Elenco do quadro ${f.position}`, `<div class="form">
      <p class="help">Só quem está aqui vai para a IA, cada um com as próprias fotos e o papel que você escrever. Isso evita rostos trocados.</p>
      ${rows ? `<ul class="cast-list">${rows}</ul>` : '<p class="none">Ninguém no quadro ainda.</p>'}
      ${add}${removedHtml}
      <div class="modal-foot"><button class="btn secondary" type="button" data-action="close-modal">Cancelar</button>
        <button class="btn primary" type="button" data-action="cast-save">Salvar elenco</button></div></div>`,
    'Personagens, objetos e locais que aparecem nesta cena');
}
function readCastRoles() {
  for (const input of document.querySelectorAll('[data-cast-role]')) {
    const id = input.dataset.castRole;
    const e = castDraft.entries.get(id);
    if (input.value.trim() || e) castDraft.entries.set(id, {included: e ? e.included : true, role: input.value});
  }
}
function rerenderCast() { readCastRoles(); openModal(castModalHtml(), {size: 'lg'}); }

/* ---------- Aprovar visual: recorte de um quadro vira foto da ficha ---------- */
let crop = null;   // {x, y, w, h} em pixels da imagem exibida
function approveBarHtml(f) {
  const cast = castOf(f).filter(c => c.asset.kind === 'character').map(c => c.asset);
  const rest = state.assets.filter(a => !cast.includes(a));
  const options = [...cast, ...rest].map(a => `<option value="${esc(a.id)}">${esc(a.name)}${cast.includes(a) ? '' : ` (${esc(kindOf(a).label)})`}</option>`).join('');
  return `<div class="approve-bar" data-approve>
    <p>${icon('crop')}<span>Arraste sobre o rosto para recortar (sem recorte, vai a imagem inteira). O recorte entra nas fotos da ficha e passa a guiar os próximos quadros.</span></p>
    <div class="approve-controls"><select data-approve-asset aria-label="Ficha que recebe o recorte">${options}</select>
      <label class="check"><input type="checkbox" data-approve-principal> Virar foto principal</label>
      <button class="btn secondary sm" type="button" data-action="approve-cancel">Cancelar</button>
      <button class="btn primary sm" type="button" data-action="approve-save" data-id="${esc(f.id)}">${icon('check')}Salvar na ficha</button></div></div>`;
}
function setupCrop(stage) {
  const img = $('img', stage), box = $('.crop-box', stage);
  let start = null;
  const point = e => { const r = img.getBoundingClientRect(); return {x: Math.min(Math.max(e.clientX - r.left, 0), r.width), y: Math.min(Math.max(e.clientY - r.top, 0), r.height)}; };
  const draw = () => {
    box.hidden = !crop;
    if (crop) Object.assign(box.style, {left: `${crop.x}px`, top: `${crop.y}px`, width: `${crop.w}px`, height: `${crop.h}px`});
  };
  stage.onpointerdown = e => { if (e.target.closest('button')) return; start = point(e); crop = null; draw(); stage.setPointerCapture(e.pointerId); };
  stage.onpointermove = e => {
    if (!start) return;
    const p = point(e);
    crop = {x: Math.min(start.x, p.x), y: Math.min(start.y, p.y), w: Math.abs(p.x - start.x), h: Math.abs(p.y - start.y)};
    draw();
  };
  stage.onpointerup = () => { start = null; if (crop && (crop.w < 12 || crop.h < 12)) { crop = null; draw(); } };
}
async function croppedBlob(img) {
  const scale = img.naturalWidth / img.clientWidth;
  const r = crop ? {x: crop.x * scale, y: crop.y * scale, w: crop.w * scale, h: crop.h * scale}
                 : {x: 0, y: 0, w: img.naturalWidth, h: img.naturalHeight};
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(r.w); canvas.height = Math.round(r.h);
  canvas.getContext('2d').drawImage(img, r.x, r.y, r.w, r.h, 0, 0, canvas.width, canvas.height);
  return new Promise((resolve, reject) => canvas.toBlob(b => b ? resolve(b) : reject(new Error('Não foi possível recortar a imagem.')), 'image/png'));
}

function formatDate(value) {
  if (!value) return '';
  const iso = String(value).replace(' ', 'T');
  const d = new Date(/Z|[+-]\d\d:?\d\d$/.test(iso) ? iso : iso + 'Z');
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString('pt-BR', {day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit'});
}
function openLightbox(id) {
  const withImage = state.frames.filter(f => f.image_path);
  const i = withImage.findIndex(f => f.id === id);
  const f = withImage[i];
  if (!f) return;
  const prev = withImage[i - 1], next = withImage[i + 1];
  crop = null;
  const body = `<div class="lightbox-stage">
      <div class="crop-wrap art"><img src="${esc(f.image_path)}" alt="Quadro ${f.position}">${editorText() ? balloonLayerHtml(f.balloons, false, f.id) : ''}<div class="crop-box" hidden></div></div>
      <button class="lb-nav prev" type="button" data-action="zoom" data-id="${esc(prev?.id || '')}" aria-label="Quadro anterior" ${prev ? '' : 'disabled'}>${icon('chevronLeft')}</button>
      <button class="lb-nav next" type="button" data-action="zoom" data-id="${esc(next?.id || '')}" aria-label="Próximo quadro" ${next ? '' : 'disabled'}>${icon('chevronRight')}</button>
    </div>
    <div class="lightbox-foot">${f.description ? `<p class="lightbox-caption">${esc(f.description)}</p>` : '<span></span>'}
      ${state.assets.length ? `<button class="btn secondary sm" type="button" data-action="approve" data-id="${esc(f.id)}" title="Guardar este visual como referência de um personagem">${icon('crop')}Aprovar visual</button>` : ''}</div>`;
  openModal(modalShell(`Quadro ${f.position}`, body, `${esc(state.comic.title)} · ${i + 1} de ${withImage.length} com imagem`), {size: 'xl', kind: 'lightbox'});
}

/* ---------- Balões e narração ---------- */
const BALLOON_TYPES = {
  speech: {label: 'Fala', icon: 'speech'},
  thought: {label: 'Pensamento', icon: 'thought'},
  shout: {label: 'Grito', icon: 'shout'},
  caption: {label: 'Narração', icon: 'caption'},
};
// Formas desenhadas num quadrado 100×100 e esticadas até o tamanho do balão.
const SHAPES = (() => {
  const ring = (n, radius) => Array.from({length: n}, (_, i) => {
    const a = (i / n) * Math.PI * 2 - Math.PI / 2, r = radius(i);
    return [50 + Math.cos(a) * r * 0.98, 50 + Math.sin(a) * r * 0.96];
  });
  const cloud = ring(13, () => 44);
  const cloudPath = `M${cloud[0].join(' ')}` + cloud.map((_, i) => {
    const [x1, y1] = cloud[i], [x2, y2] = cloud[(i + 1) % cloud.length];
    const r = Math.hypot(x2 - x1, y2 - y1) * 0.6;
    return ` A${r} ${r} 0 0 1 ${x2.toFixed(1)} ${y2.toFixed(1)}`;
  }).join('') + 'Z';
  const burst = ring(22, i => i % 2 ? 37 + (i % 3) * 2 : 51).map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ');
  return {
    speech: '<ellipse cx="50" cy="50" rx="49" ry="48"/>',
    thought: `<path d="${cloudPath}"/>`,
    shout: `<polygon points="${burst}"/>`,
    caption: '<rect x="0.5" y="0.5" width="99" height="99"/>',
  };
})();
Object.assign(ICONS, {
  speech: '<path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/>',
  thought: '<path d="M17.5 15H10a4.5 4.5 0 1 1 3.6-7.2A3.6 3.6 0 1 1 17.5 15Z"/><circle cx="7" cy="18.5" r="1.6"/><circle cx="3.6" cy="21.4" r=".9"/>',
  shout: '<path d="m12 2 2.4 5.2L20 5l-2.2 5.6L23 13l-5.4 1.6L19 20l-5-2.6L12 23l-2-5.6L5 20l1.4-5.4L1 13l5.2-2.4L4 5l5.6 2.2Z"/>',
  caption: '<rect width="18" height="12" x="3" y="6" rx="1"/><path d="M7 10h10"/><path d="M7 14h6"/>',
  minus: '<path d="M5 12h14"/>',
  download: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="m7 10 5 5 5-5"/><path d="M12 15V3"/>',
  clipboard: '<rect width="8" height="4" x="8" y="2" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
  paperclip: '<path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.57a2 2 0 0 1-2.83-2.83l8.49-8.48"/>',
});

function balloonHtml(b, edit = false) {
  const type = BALLOON_TYPES[b.type] ? b.type : 'speech';
  return `<div class="balloon b-${type}${edit && balloonEditor?.selected === b.id ? ' selected' : ''}" data-b="${esc(b.id)}"
      style="left:${b.x}%;top:${b.y}%;width:${b.w}%;--w:${b.w};--s:${b.size || 1}">
    <svg class="b-shape" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">${SHAPES[type]}</svg>
    <span class="b-text">${esc(b.text) || (edit ? '<span class="b-empty">Escreva o texto</span>' : '')}</span>
    ${edit ? '<span class="b-resize" data-resize title="Arraste para mudar a largura"></span>' : ''}</div>`;
}
function balloonLayerHtml(balloons = [], edit = false, frameId = '') {
  const list = balloons.filter(b => edit || b.text.trim());
  if (!list.length && !edit) return '';
  const handles = edit ? list.filter(b => b.tail && b.type !== 'caption').map(b =>
    `<span class="tail-handle${balloonEditor?.selected === b.id ? ' selected' : ''}" data-tail="${esc(b.id)}" style="left:${b.tail.x}%;top:${b.tail.y}%" title="Arraste para apontar o balão"></span>`).join('') : '';
  return `<div class="balloon-layer${edit ? ' editing' : ''}" data-of="${esc(frameId)}" aria-hidden="${edit ? 'false' : 'true'}">
    <svg class="tails"></svg>${list.map(b => balloonHtml(b, edit)).join('')}${handles}</div>`;
}

/* Rabichos dependem da altura real do balão, então são desenhados depois, em pixels. */
function layoutTails(layer) {
  const svg = layer.querySelector(':scope > .tails');
  const W = layer.clientWidth, H = layer.clientHeight;
  if (!svg || !W || !H) return;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const stroke = Math.max(1, W * 0.0035);
  const balloons = layer.closest('[data-editor]') ? balloonEditor?.balloons || [] : frameById(layer.dataset.of)?.balloons || [];
  let out = '';
  for (const el of layer.querySelectorAll(':scope > .balloon')) {
    const b = balloons.find(x => x.id === el.dataset.b);
    if (!b?.tail || b.type === 'caption') continue;
    const cx = el.offsetLeft + el.offsetWidth / 2, cy = el.offsetTop + el.offsetHeight / 2;
    const tx = b.tail.x / 100 * W, ty = b.tail.y / 100 * H;
    const len = Math.hypot(tx - cx, ty - cy);
    if (len < 2) continue;
    const nx = -(ty - cy) / len, ny = (tx - cx) / len;
    if (b.type === 'thought') {
      // Bolinhas que diminuem do balão até a boca de quem pensa.
      const edge = Math.min(el.offsetWidth, el.offsetHeight) / 2;
      for (const [t, r] of [[0.45, 0.03], [0.7, 0.022], [0.92, 0.014]]) {
        const d = edge + (len - edge) * t;
        out += `<circle cx="${cx + (tx - cx) / len * d}" cy="${cy + (ty - cy) / len * d}" r="${W * r}" stroke-width="${stroke}"/>`;
      }
    } else {
      const half = Math.min(el.offsetWidth * 0.14, W * 0.035);
      out += `<path d="M${cx + nx * half} ${cy + ny * half} L${tx} ${ty} L${cx - nx * half} ${cy - ny * half}Z" stroke-width="${stroke}" class="t-${b.type}"/>`;
    }
  }
  svg.innerHTML = out;
}
const tailObserver = new ResizeObserver(entries => entries.forEach(e => layoutTails(e.target)));
new MutationObserver(records => {
  for (const r of records) for (const node of r.addedNodes) {
    if (node.nodeType !== 1) continue;
    const layers = node.matches('.balloon-layer') ? [node] : node.querySelectorAll('.balloon-layer');
    layers.forEach(l => tailObserver.observe(l));
  }
}).observe(document.body, {childList: true, subtree: true});
document.fonts?.ready.then(() => document.querySelectorAll('.balloon-layer').forEach(layoutTails));

function dialogSummaryHtml(f) {
  const list = (f.balloons || []).filter(b => b.text.trim());
  const names = Object.fromEntries(state.assets.map(a => [a.id, a.name]));
  const lines = list.slice(0, 3).map(b => `<li>${icon(BALLOON_TYPES[b.type]?.icon || 'speech')}<b>${esc(b.type === 'caption' ? 'Narração' : names[b.speaker] || 'Alguém')}:</b> ${esc(b.text)}</li>`).join('');
  return `${lines ? `<ul class="dialog-lines">${lines}${list.length > 3 ? `<li class="more">+${list.length - 3}</li>` : ''}</ul>` : ''}
    <button class="btn ghost sm dialog-btn" type="button" data-action="balloons" data-id="${esc(f.id)}">${icon('speech')}${list.length ? 'Editar balões' : 'Balões e narração'}</button>`;
}

/* ---------- Editor de balões ---------- */
let balloonEditor = null;   // {frameId, balloons, selected, timer}
const newId = () => Math.random().toString(36).slice(2, 10);
function editorFrame() { return frameById(balloonEditor.frameId); }

function addBalloon(type) {
  const list = balloonEditor.balloons;
  const f = editorFrame();
  if (type === 'caption') {
    const n = list.filter(b => b.type === 'caption').length;
    list.push({id: newId(), type, text: '', speaker: '', x: 2, y: Math.min(2 + n * 11, 80), w: 32, size: 1, tail: null});
  } else {
    const n = list.filter(b => b.type !== 'caption').length;
    // Duas colunas à direita da narração, descendo: os novos não nascem um em cima do outro.
    const x = 38 + (n % 2) * 32, y = Math.min(4 + Math.floor(n / 2) * 24, 70);
    const characters = castOf(f).filter(c => c.asset.kind === 'character').map(c => c.asset.id);
    const used = new Set(list.map(b => b.speaker));
    list.push({id: newId(), type, text: '', speaker: characters.find(id => !used.has(id)) || characters[0] || '',
      x, y, w: type === 'shout' ? 30 : 26, size: 1, tail: {x: x + 6, y: y + 34}});
  }
  balloonEditor.selected = list.at(-1).id;
}
function speakerOptions(b) {
  const f = editorFrame();
  const cast = castOf(f).filter(c => c.asset.kind === 'character').map(c => c.asset);
  const rest = state.assets.filter(a => a.kind === 'character' && !cast.includes(a));
  const opt = a => `<option value="${esc(a.id)}" ${a.id === b.speaker ? 'selected' : ''}>${esc(a.name)}</option>`;
  return `<option value="">Quem fala?</option>${cast.map(opt).join('')}${rest.length ? `<optgroup label="Fora do elenco">${rest.map(opt).join('')}</optgroup>` : ''}`;
}
function balloonItemHtml(b, i) {
  const types = Object.entries(BALLOON_TYPES).map(([type, t]) =>
    `<button type="button" class="icon-btn sm" data-action="b-type" data-id="${esc(b.id)}" data-type="${type}" aria-pressed="${b.type === type}" title="${t.label}" aria-label="${t.label}">${icon(t.icon)}</button>`).join('');
  return `<li class="b-item${balloonEditor.selected === b.id ? ' selected' : ''}" data-b-item="${esc(b.id)}">
    <div class="b-item-head"><span class="b-num">${i + 1}</span><div class="b-types" role="group" aria-label="Tipo do balão">${types}</div>
      <button type="button" class="icon-btn sm" data-action="b-move" data-id="${esc(b.id)}" data-dir="-1" title="Ler antes" aria-label="Ler antes" ${i === 0 ? 'disabled' : ''}>${icon('chevronLeft')}</button>
      <button type="button" class="icon-btn sm danger" data-action="b-delete" data-id="${esc(b.id)}" title="Excluir balão" aria-label="Excluir balão ${i + 1}">${icon('trash')}</button></div>
    ${b.type === 'caption' ? '' : `<select data-b-speaker="${esc(b.id)}" aria-label="Quem fala">${speakerOptions(b)}</select>`}
    <textarea data-b-text="${esc(b.id)}" rows="2" maxlength="600" placeholder="${b.type === 'caption' ? 'Ex.: Em algum lugar da fronteira…' : 'Ex.: Carga liberada!'}">${esc(b.text)}</textarea>
    <div class="b-size"><span>Letra</span>
      <button type="button" class="icon-btn sm" data-action="b-size" data-id="${esc(b.id)}" data-dir="-1" aria-label="Diminuir letra">${icon('minus')}</button>
      <span class="b-size-val">${Math.round((b.size || 1) * 100)}%</span>
      <button type="button" class="icon-btn sm" data-action="b-size" data-id="${esc(b.id)}" data-dir="1" aria-label="Aumentar letra">${icon('plus')}</button></div></li>`;
}
function editorStageHtml() {
  const f = editorFrame();
  const art = f.image_path
    ? `<img src="${esc(f.image_path)}" alt="Quadro ${f.position}" draggable="false">`
    : `<div class="art-placeholder"><p>${esc(f.description) || 'Quadro sem imagem'}</p><small>Sem imagem ainda: os balões ficam na posição e vão para cima da imagem quando ela for gerada.</small></div>`;
  return `<div class="art editor-art" data-editor>${art}${balloonLayerHtml(balloonEditor.balloons, true)}</div>`;
}
function editorPanelHtml() {
  const list = balloonEditor.balloons;
  const adds = Object.entries(BALLOON_TYPES).map(([type, t]) =>
    `<button class="btn secondary sm" type="button" data-action="b-add" data-type="${type}">${icon(t.icon)}${t.label}</button>`).join('');
  return `<div class="b-adds">${adds}</div>
    ${list.length ? `<ol class="b-list">${list.map(balloonItemHtml).join('')}</ol>`
      : '<p class="none">Nenhum balão ainda. Adicione uma fala ou uma narração; depois arraste na imagem para posicionar.</p>'}`;
}
function openBalloonEditor(id) {
  const f = frameById(id);
  if (!f) return;
  balloonEditor = {frameId: id, balloons: structuredClone(f.balloons || []), selected: f.balloons?.[0]?.id || null, timer: null};
  const body = `<div class="b-editor">
      <div class="b-stage" data-b-stage>${editorStageHtml()}</div>
      <div class="b-panel" data-b-panel>${editorPanelHtml()}</div></div>
    <div class="b-foot"><span class="help">Arraste o balão para mover, a borda direita para alargar e a bolinha para apontar quem fala. Tudo é salvo sozinho.</span>
      <span class="save-state" data-b-save></span>
      <button class="btn primary" type="button" data-action="close-modal">Concluir</button></div>`;
  openModal(modalShell(`Balões do quadro ${f.position}`, body, 'Falas, pensamentos, gritos e narração ficam por cima da imagem e não somem ao gerar de novo.'), {size: 'xl', kind: 'balloons'});
}
function refreshEditor({panel = true} = {}) {
  const stage = $('[data-b-stage]');
  if (!stage) return;
  stage.innerHTML = editorStageHtml();
  if (panel) {
    const scroll = $('[data-b-panel]').scrollTop;
    $('[data-b-panel]').innerHTML = editorPanelHtml();
    $('[data-b-panel]').scrollTop = scroll;
  }
}
function selectBalloon(id) {
  balloonEditor.selected = id;
  document.querySelectorAll('[data-editor] .balloon, [data-editor] .tail-handle').forEach(el =>
    el.classList.toggle('selected', (el.dataset.b || el.dataset.tail) === id));
  document.querySelectorAll('[data-b-item]').forEach(el => el.classList.toggle('selected', el.dataset.bItem === id));
  $(`[data-b-item="${id}"]`)?.scrollIntoView({block: 'nearest'});
}
function queueBalloonSave() {
  const ed = balloonEditor;
  clearTimeout(ed.timer);
  const el = $('[data-b-save]');
  if (el) { el.classList.remove('err', 'fade'); el.textContent = 'Salvando…'; }
  ed.timer = setTimeout(() => saveBalloons(ed), 500);
}
async function saveBalloons(ed) {
  clearTimeout(ed.timer);
  ed.timer = null;
  const round = n => Math.round(n * 10) / 10;
  const balloons = ed.balloons.map(b => ({...b, x: round(b.x), y: round(b.y), w: round(b.w),
    tail: b.tail ? {x: round(b.tail.x), y: round(b.tail.y)} : null}));
  const el = $('[data-b-save]');
  try {
    const saved = await api(`/frames/${ed.frameId}/balloons`, json('PUT', {balloons}));
    const f = frameById(ed.frameId);
    if (f) {
      f.balloons = saved.balloons;
      const dialog = $(`[data-dialog="${f.id}"]`);
      if (dialog) dialog.innerHTML = dialogSummaryHtml(f);
      updateCover();
      refreshFrames();
    }
    if (el && !ed.timer) { el.innerHTML = `${icon('check')}Salvo`; }
  } catch (error) {
    if (el) { el.classList.add('err'); el.textContent = 'Não foi salvo'; }
    throw error;
  }
}
const balloonOf = id => balloonEditor?.balloons.find(b => b.id === id);

/* Arrastar no editor: mover balão, alargar ou apontar o rabicho. Tudo em % da imagem. */
document.addEventListener('pointerdown', e => {
  const layer = e.target.closest('[data-editor] .balloon-layer');
  if (!layer || e.button !== 0) return;
  const tail = e.target.closest('[data-tail]'), body = e.target.closest('.balloon');
  const id = tail?.dataset.tail || body?.dataset.b;
  if (!id) return;
  e.preventDefault();
  selectBalloon(id);
  const b = balloonOf(id);
  const rect = layer.getBoundingClientRect();
  const pct = ev => ({x: (ev.clientX - rect.left) / rect.width * 100, y: (ev.clientY - rect.top) / rect.height * 100});
  const start = pct(e), orig = structuredClone(b);
  const mode = tail ? 'tail' : e.target.closest('[data-resize]') ? 'resize' : 'move';
  const el = $(`.balloon[data-b="${id}"]`, layer), handle = $(`[data-tail="${id}"]`, layer);
  const clamp = (v, lo, hi) => Math.min(Math.max(v, lo), hi);
  const move = ev => {
    const p = pct(ev), dx = p.x - start.x, dy = p.y - start.y;
    if (mode === 'tail') {
      b.tail = {x: clamp(orig.tail.x + dx, -10, 110), y: clamp(orig.tail.y + dy, -10, 110)};
      handle.style.left = `${b.tail.x}%`; handle.style.top = `${b.tail.y}%`;
    } else if (mode === 'resize') {
      b.w = clamp(orig.w + dx, 8, 100 - b.x);
      el.style.width = `${b.w}%`;
      el.style.setProperty('--w', b.w);
    } else {
      b.x = clamp(orig.x + dx, -5, 100 - b.w + 5); b.y = clamp(orig.y + dy, -5, 95);
      el.style.left = `${b.x}%`; el.style.top = `${b.y}%`;
      if (b.tail) {
        // O rabicho acompanha o balão, para não ficar apontando para outro lugar sem querer.
        b.tail = {x: orig.tail.x + (b.x - orig.x), y: orig.tail.y + (b.y - orig.y)};
        if (handle) { handle.style.left = `${b.tail.x}%`; handle.style.top = `${b.tail.y}%`; }
      }
    }
    layoutTails(layer);
  };
  const up = () => {
    window.removeEventListener('pointermove', move);
    window.removeEventListener('pointerup', up);
    if (JSON.stringify(orig) !== JSON.stringify(b)) queueBalloonSave();
  };
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', up);
});

/* ---------- Ações ---------- */
const actions = {
  async project(id) {
    await flushSaves(); toggleNav(false);
    await loadProject(id);
  },
  async comic(id) {
    await flushSaves(); toggleNav(false); closeModal();
    await loadComic(id);
  },
  async overview() {
    if (!state.project) return;
    await flushSaves(); toggleNav(false);
    Object.assign(state, {comic: null, frames: [], screen: 'overview', libraryReturn: null});
    store.del(`hq-comic-${state.project.id}`);
    await loadCovers();
    render({top: true});
  },
  async library() {
    if (!state.project) return;
    await flushSaves(); toggleNav(false); closeModal();
    if (state.screen === 'comic' && state.comic) state.libraryReturn = {id: state.comic.id, title: state.comic.title};
    else if (state.screen !== 'library') state.libraryReturn = null;
    Object.assign(state, {comic: null, frames: [], screen: 'library', libQuery: ''});
    await loadCovers();
    render({top: true});
  },
  'lib-kind'(_, btn) {
    state.libKind = btn.dataset.kind in KINDS ? btn.dataset.kind : 'all';
    renderMain();
    $(`[data-action="lib-kind"][data-kind="${state.libKind}"]`)?.focus();
  },
  'lib-clear'() {
    state.libQuery = '';
    renderMain();
    $('#lib-search')?.focus();
  },
  async comics() {
    if (!state.project) return;
    await flushSaves(); toggleNav(false); closeModal();
    Object.assign(state, {comic: null, frames: [], screen: 'comics', libraryReturn: null, comicsQuery: ''});
    await loadCovers();
    render({top: true});
  },
  'toggle-comics-nav'() {
    store.set('hq-nav-comics', store.get('hq-nav-comics') === '0' ? '1' : '0');
    renderSidebar();
    $('[data-action="toggle-comics-nav"]')?.focus();
  },
  'comics-clear'() {
    state.comicsQuery = '';
    renderMain();
    $('#comics-search')?.focus();
  },
  'comic-edit-open'(id) {
    const comic = state.comics.find(c => c.id === id);
    if (comic) openModal(comicFormHtml(comic));
  },
  async 'export-comic'(id) {
    const comic = state.comics.find(c => c.id === id);
    if (comic) await exportComic(comic);
  },
  'comic-delete'(id) {
    const comic = state.comics.find(c => c.id === id);
    if (!comic) return;
    const info = state.covers[id];
    const lost = info?.count
      ? `Os <b>${plural(info.count, 'quadro', 'quadros')}</b> dela${info.done ? `, as imagens geradas e as versões anteriores` : ''} serão apagados.`
      : 'Ela ainda não tem quadros.';
    openModal(modalShell(`Excluir “${esc(comic.title)}”?`, `<div class="form">
        <p>${lost} <b>Não dá para desfazer.</b></p>
        <p class="help">A biblioteca de personagens, objetos e locais continua no projeto. Se quiser guardar a HQ, exporte o PDF antes.</p>
        <div class="modal-foot">
          ${info?.done ? `<button class="btn ghost" type="button" data-action="export-comic" data-id="${esc(id)}">${icon('download')}Exportar PDF antes</button>` : ''}
          <button class="btn secondary" type="button" data-action="close-modal">Cancelar</button>
          <button class="btn primary danger-fill" type="button" data-action="comic-delete-confirm" data-id="${esc(id)}">${icon('trash')}Excluir HQ</button></div></div>`),
      {size: 'md'});
  },
  async 'comic-delete-confirm'(id) {
    const comic = state.comics.find(c => c.id === id);
    if (!comic) return;
    await flushSaves();
    await api(`/comics/${id}`, {method: 'DELETE'});
    state.comics = state.comics.filter(c => c.id !== id);
    delete state.covers[id];
    delete state.comicFrames[id];
    if (store.get(`hq-comic-${state.project.id}`) === id) store.del(`hq-comic-${state.project.id}`);
    if (state.comic?.id === id) Object.assign(state, {comic: null, frames: [], screen: 'comics'});
    closeModal();
    render();
    toast(`“${comic.title}” excluída`);
  },
  'new-project'() { toggleNav(false); openModal(projectFormHtml()); },
  'new-comic'() { toggleNav(false); openModal(comicFormHtml()); },
  'edit-comic'() { if (state.comic) openModal(comicFormHtml(state.comic)); },
  'toggle-context'(_, btn) {
    const box = btn.closest('.context-card');
    const open = box.classList.toggle('expanded');
    btn.textContent = open ? 'Mostrar menos' : 'Mostrar tudo';
  },
  'new-asset'(_, btn) { toggleNav(false); openModal(assetFormHtml(btn.dataset.kind)); },
  asset(id) { toggleNav(false); openAsset(id); },
  'close-modal'() { closeModal(); },
  reload() { location.reload(); },
  view(_, btn) {
    state.view = btn.dataset.view === 'read' ? 'read' : 'edit';
    store.set('hq-view', state.view);
    renderMain();
  },
  'dismiss-tip'(_, btn) {
    store.set(`hq-tip-${btn.dataset.tip}`, '1');
    btn.closest('.tip')?.remove();
  },
  async 'add-frame'() {
    mutationSeq++;
    await flushSaves();
    const frame = await api(`/comics/${state.comic.id}/frames`, {method: 'POST'});
    await reloadFrames();
    if (state.view !== 'edit') { state.view = 'edit'; store.set('hq-view', 'edit'); }
    render();
    requestAnimationFrame(() => {
      $(`[data-frame="${frame.id}"]`)?.scrollIntoView({behavior: 'smooth', block: 'nearest', inline: 'nearest'});
      $(`[data-description="${frame.id}"]`)?.focus({preventScroll: true});
    });
  },
  async generate(id, btn) {
    const textarea = $(`[data-description="${id}"]`);
    if (!(textarea?.value ?? frameById(id)?.description ?? '').trim()) {
      textarea?.focus();
      throw new Error('Descreva o que acontece no quadro antes de gerar.');
    }
    mutationSeq++;
    await saveDescription(id);
    const feedback = $(`[data-feedback="${id}"]`)?.value || '';
    const updated = await api(`/frames/${id}/generate`, json('POST', {provider: state.provider, feedback, refine: btn.dataset.refine === 'true', ...generationOptions()}));
    state.frames = mergeLocal(state.frames.map(f => f.id === id ? updated : f));
    refreshFrames();
    toast(`Quadro ${updated.position} enviado para geração`);
  },
  async move(id, btn) {
    mutationSeq++;
    await flushSaves();
    await api(`/frames/${id}/move/${btn.dataset.direction}`, {method: 'POST'});
    await reloadFrames();
    renderMain();
    $(`[data-frame="${id}"] [data-action="move"][data-direction="${btn.dataset.direction}"]:not(:disabled)`)?.focus();
  },
  async delete(id) {
    const f = frameById(id);
    if (!confirm(`Excluir o quadro ${f?.position ?? ''}? As versões geradas dele também deixam de aparecer.`)) return;
    mutationSeq++;
    await flushSaves();
    await api(`/frames/${id}`, {method: 'DELETE'});
    await reloadFrames();
    render();
    toast('Quadro excluído');
  },
  async history(id) {
    const f = frameById(id);
    const versions = await api(`/frames/${id}/versions`);
    const body = versions.length
      ? `<p class="modal-sub">Escolha uma versão para voltar a usá-la neste quadro.</p>
         <div class="version-grid">${versions.map(v => {
           const current = v.image_path === f?.image_path;
           return `<button class="version" type="button" data-action="restore" data-id="${esc(id)}" data-version="${esc(v.id)}" ${current ? 'disabled aria-current="true"' : ''}>
             <div class="version-img"><img src="${esc(v.image_path)}" alt="" loading="lazy"></div>
             <div class="version-meta"><span>${esc(formatDate(v.created_at))}</span>${current ? `<span class="current">${icon('check')}Em uso</span>` : `<span>${esc(providerName(v.provider))}</span>`}</div>
             ${v.feedback ? `<p class="version-fb">“${esc(v.feedback)}”</p>` : ''}</button>`;
         }).join('')}</div>`
      : emptyHtml({iconName: 'history', title: 'Nenhuma versão ainda', text: 'Cada imagem gerada para este quadro fica guardada aqui.'});
    openModal(modalShell(`Versões do quadro ${f?.position ?? ''}`, body, plural(versions.length, 'versão salva', 'versões salvas')), {size: 'lg'});
  },
  async restore(id, btn) {
    mutationSeq++;
    await api(`/frames/${id}/versions/${btn.dataset.version}/restore`, {method: 'POST'});
    await reloadFrames();
    closeModal();
    refreshFrames();
    toast('Versão restaurada');
  },
  zoom(id) { if (id) openLightbox(id); },
  balloons(id) { openBalloonEditor(id); },
  async 'text-mode'(_, btn) {
    const mode = btn.dataset.mode === 'editor' ? 'editor' : 'ai';
    if (mode === state.project.text_mode) return;
    state.project = await api(`/projects/${state.project.id}/text-mode`, json('PATCH', {text_mode: mode}));
    render();
    toast(mode === 'ai' ? 'A IA vai desenhar os balões nos próximos quadros gerados' : 'Os próximos quadros vêm sem texto; posicione os balões no editor');
  },
  credits(id) { openCredits(id); },
  async 'paste-image'(_, btn) { await receiveImages(await readClipboardImages(), btn); },
  async 'add-credits'() {
    mutationSeq++;
    await flushSaves();
    const frame = await api(`/comics/${state.comic.id}/frames`, json('POST', {kind: 'credits'}));
    await reloadFrames();
    render();
    openCredits(frame.id);
  },
  'credit-add'() { $('[data-credit-list]').insertAdjacentHTML('beforeend', creditRowHtml()); $('[data-credit-list] li:last-child input')?.focus(); },
  'credit-remove'(_, btn) { btn.closest('li').remove(); },
  'credit-sync'() {
    const present = new Set([...document.querySelectorAll('[data-credit-name]')].map(i => norm(i.value.trim())));
    const missing = state.assets.filter(a => a.kind === 'character' && !present.has(norm(a.name)));
    $('[data-credit-list]').insertAdjacentHTML('beforeend', missing.map(a => creditRowHtml({name: a.name, role: ''})).join(''));
    toast(missing.length ? plural(missing.length, 'nome acrescentado', 'nomes acrescentados') : 'Todos da biblioteca já estão aqui');
  },
  async 'export-pdf'() { await exportComic(state.comic); },
  async 'attachment-delete'(id, btn) {
    const updated = await api(`/frames/${id}/attachments/${btn.dataset.att}`, {method: 'DELETE'});
    const f = frameById(id);
    if (f) { f.attachments = updated.attachments; renderAttachments(f); }
  },
  'b-add'(_, btn) { addBalloon(btn.dataset.type); refreshEditor(); queueBalloonSave(); $(`[data-b-text="${balloonEditor.selected}"]`)?.focus(); },
  'b-type'(id, btn) {
    const b = balloonOf(id);
    const type = btn.dataset.type;
    if (type !== 'caption' && !b.tail) b.tail = {x: b.x + b.w / 2, y: b.y + 30};
    b.type = type;
    selectBalloon(id);
    refreshEditor();
    queueBalloonSave();
  },
  'b-delete'(id) {
    balloonEditor.balloons = balloonEditor.balloons.filter(b => b.id !== id);
    if (balloonEditor.selected === id) balloonEditor.selected = balloonEditor.balloons[0]?.id || null;
    refreshEditor();
    queueBalloonSave();
  },
  'b-move'(id) {
    const list = balloonEditor.balloons, i = list.findIndex(b => b.id === id);
    if (i > 0) [list[i - 1], list[i]] = [list[i], list[i - 1]];
    refreshEditor();
    queueBalloonSave();
  },
  'b-size'(id, btn) {
    const b = balloonOf(id);
    b.size = Math.min(2.5, Math.max(0.5, Math.round(((b.size || 1) + Number(btn.dataset.dir) * 0.1) * 10) / 10));
    refreshEditor();
    queueBalloonSave();
  },
  'asset-edit'(id) {
    const a = state.assets.find(x => x.id === id);
    if (a) openModal(assetFormHtml(a.kind, a));
  },
  async 'asset-delete'(id) {
    const a = state.assets.find(x => x.id === id);
    if (!a || !confirm(`Excluir “${a.name}” da biblioteca? As fotos dele também serão apagadas.`)) return;
    await api(`/assets/${id}`, {method: 'DELETE'});
    state.assets = state.assets.filter(x => x.id !== id);
    if (state.comic) await reloadFrames();
    closeModal();
    render();
    toast(`“${a.name}” excluído`);
  },
  async 'photo-principal'(id, btn) {
    replaceAsset(await api(`/assets/${id}/photos/${btn.dataset.photo}/principal`, {method: 'POST'}));
    openAsset(id);
  },
  async 'photo-delete'(id, btn) {
    if (!confirm('Excluir esta foto de referência?')) return;
    replaceAsset(await api(`/assets/${id}/photos/${btn.dataset.photo}`, {method: 'DELETE'}));
    openAsset(id);
  },
  cast(id) {
    const f = frameById(id);
    if (!f) return;
    castDraft = {frameId: id, entries: new Map((f.cast || []).map(c => [c.asset_id, {included: c.included, role: c.role}]))};
    openModal(castModalHtml(), {size: 'lg'});
  },
  'cast-remove'(id) {
    readCastRoles();
    const detected = matchingAssets(frameById(castDraft.frameId).description).some(a => a.id === id);
    if (detected) castDraft.entries.set(id, {included: false, role: ''});
    else castDraft.entries.delete(id);
    rerenderCast();
  },
  'cast-restore'(id) { readCastRoles(); castDraft.entries.delete(id); rerenderCast(); },
  async 'cast-save'() {
    readCastRoles();
    const f = frameById(castDraft.frameId);
    const detected = new Set(matchingAssets(f.description).map(a => a.id));
    // Guarda só o que difere do automático: remoções, papéis e quem não é citado no texto.
    const items = [...castDraft.entries].map(([asset_id, e]) => ({asset_id, included: e.included, role: e.role.trim()}))
      .filter(e => !e.included || e.role || !detected.has(e.asset_id));
    mutationSeq++;
    const updated = await api(`/frames/${f.id}/cast`, json('PUT', {items}));
    f.cast = updated.cast;
    updateCover();
    closeModal();
    const refs = $(`[data-refs="${f.id}"]`);
    if (refs) refs.innerHTML = refsHtml(f);
    toast(`Elenco do quadro ${f.position} salvo`);
  },
  approve(id, btn) {
    const foot = btn.closest('.lightbox-foot');
    foot.insertAdjacentHTML('afterend', approveBarHtml(frameById(id)));
    btn.hidden = true;
    const stage = $('.lightbox-stage');
    stage.classList.add('cropping');
    setupCrop($('.crop-wrap', stage));
  },
  'approve-cancel'() { openLightbox($('[data-action="approve-save"]').dataset.id); },
  async 'approve-save'(id) {
    const assetId = $('[data-approve-asset]').value;
    const a = state.assets.find(x => x.id === assetId);
    if (!a) throw new Error('Escolha a ficha que recebe o recorte.');
    const data = new FormData();
    data.append('image', await croppedBlob($('.crop-wrap img')), 'recorte.png');
    data.append('source', 'frame');
    data.append('principal', String($('[data-approve-principal]').checked));
    replaceAsset(await api(`/assets/${assetId}/photos`, {method: 'POST', body: data}));
    openLightbox(id);
    toast(`Visual guardado nas fotos de “${a.name}”`);
  },
};

/* ---------- Eventos ---------- */
document.addEventListener('click', async e => {
  const btn = e.target.closest('[data-action]');
  if (!btn || btn.disabled) return;
  const handler = actions[btn.dataset.action];
  if (!handler) return;
  btn.disabled = true;
  try { await handler(btn.dataset.id, btn); }
  catch (error) { fail(error); }
  finally { if (btn.isConnected) btn.disabled = false; }
});

document.addEventListener('submit', async e => {
  const form = e.target.closest('[data-form]');
  if (!form) return;
  e.preventDefault();
  const button = form.querySelector('button[type="submit"]');
  if (button) button.disabled = true;
  const data = new FormData(form);
  try {
    if (form.dataset.form === 'credits') {
      const lines = [...form.querySelectorAll('.credit-row')].map(row => ({
        name: $('[data-credit-name]', row).value, role: $('[data-credit-role]', row).value}));
      const updated = await api(`/frames/${form.dataset.id}/credits`, json('PUT', {heading: data.get('heading') || 'Elenco', footer: data.get('footer') || '', lines}));
      state.frames = state.frames.map(f => f.id === updated.id ? {...f, credits: updated.credits} : f);
      closeModal();
      refreshFrames();
      toast('Créditos salvos');
    } else if (form.dataset.form === 'project') {
      const p = await api('/projects', json('POST', {name: data.get('name'), style: data.get('style')}));
      state.projects = await api('/projects');
      closeModal();
      await loadProject(p.id);
      toast('Projeto criado');
    } else if (form.dataset.form === 'comic') {
      await flushSaves();
      const comic = await api(`/projects/${state.project.id}/comics`, json('POST', {title: data.get('title'), context: data.get('context') || '', style: data.get('style') || ''}));
      const costumes = costumesFrom(data);
      if (Object.values(costumes).some(v => v.trim())) await api(`/comics/${comic.id}/costumes`, json('PUT', {costumes}));
      state.comics = await api(`/projects/${state.project.id}/comics`);
      closeModal();
      await loadComic(comic.id);
      toast('HQ criada');
    } else if (form.dataset.form === 'comic-edit') {
      const comicId = form.dataset.id || state.comic.id;
      await api(`/comics/${comicId}`, json('PATCH', {title: data.get('title'), context: data.get('context') || '', style: data.get('style') || ''}));
      const updated = await api(`/comics/${comicId}/costumes`, json('PUT', {costumes: costumesFrom(data)}));
      state.comics = state.comics.map(c => c.id === updated.id ? updated : c);
      if (state.comic?.id === updated.id) state.comic = updated;
      closeModal();
      render();
      toast('HQ atualizada');
    } else if (form.dataset.form === 'asset-edit') {
      const body = Object.fromEntries(['name', 'aliases', 'description', 'personality', 'traits', 'avoid'].map(k => [k, data.get(k) || '']));
      const updated = await api(`/assets/${form.dataset.id}`, json('PATCH', body));
      replaceAsset(updated);
      openAsset(updated.id);
      toast('Ficha atualizada');
    } else if (form.dataset.form === 'asset') {
      if (!data.getAll('images').some(f => f.size)) data.delete('images');
      const created = await api(`/projects/${state.project.id}/assets`, {method: 'POST', body: data});
      state.assets = await api(`/projects/${state.project.id}/assets`);
      closeModal();
      if (state.screen === 'library') {
        state.libQuery = '';
        if (state.libKind !== 'all' && state.libKind !== created.kind) state.libKind = created.kind;
      }
      render();
      const card = $(`[data-asset-card="${created.id}"]`);
      if (card) {
        card.classList.add('is-new');
        card.scrollIntoView({behavior: 'smooth', block: 'nearest'});
      }
      toast(`${kindOf(created).label} “${created.name}” adicionado à biblioteca`);
    }
  } catch (error) {
    fail(error);
  } finally {
    if (button?.isConnected) button.disabled = false;
  }
});

document.addEventListener('input', e => {
  const target = e.target;
  if (target.matches('[data-description]')) {
    const id = target.dataset.description;
    const f = frameById(id);
    if (f) f.description = target.value;
    const refs = $(`[data-refs="${id}"]`);
    if (refs && f) refs.innerHTML = refsHtml(f);
    setSaveState(id, '');
    clearTimeout(saveTimers.get(id));
    saveTimers.set(id, setTimeout(() => saveDescription(id).catch(fail), 700));
  } else if (target.matches('[data-b-text]')) {
    const b = balloonOf(target.dataset.bText);
    if (!b) return;
    b.text = target.value;
    const el = $(`[data-editor] .balloon[data-b="${b.id}"] .b-text`);
    if (el) el.innerHTML = esc(b.text) || '<span class="b-empty">Escreva o texto</span>';
    document.querySelectorAll('[data-editor] .balloon-layer').forEach(layoutTails);
    queueBalloonSave();
  } else if (target.matches('[data-feedback]')) {
    const f = frameById(target.dataset.feedback);
    if (f) f.feedback = target.value;
  } else if (target.id === 'comics-search') {
    state.comicsQuery = target.value;
    $('#comics-results').innerHTML = comicsResultsHtml();
  } else if (target.id === 'lib-search') {
    state.libQuery = target.value;
    $('#lib-results').innerHTML = libraryResultsHtml();
  }
});

document.addEventListener('change', e => {
  if (e.target.matches('[data-photo]')) previewPhoto(e.target);
  if (e.target.matches('[data-add-photo]')) addPhotos(e.target).catch(fail);
  if (e.target.matches('[data-format]')) {
    const id = e.target.dataset.format;
    api(`/frames/${id}/format`, json('PATCH', {format: e.target.value})).then(updated => {
      const f = frameById(id);
      if (f) f.format = updated.format;
      toast(`${FORMATS[updated.format]}: vale para a próxima imagem gerada`);
    }).catch(fail);
  }
  if (e.target.matches('[data-frame-file]')) {
    const input = e.target;
    Promise.all([...input.files].map(f => toSupportedImage(f, f.name.replace(/\.[^.]+$/, ''))))
      .then(files => attachToFrame(input.dataset.frameFile, files)).catch(fail).finally(() => { input.value = ''; });
  }
  if (e.target.matches('[data-kind]')) {
    const id = e.target.dataset.kind;
    api(`/frames/${id}/kind`, json('PATCH', {kind: e.target.value})).then(updated => {
      state.frames = state.frames.map(f => f.id === id ? {...f, kind: updated.kind, format: updated.format} : f);
      render();
      toast(updated.kind === 'cover' ? 'Card virou capa (retrato, com o título da HQ)' : 'Card virou quadro');
    }).catch(fail);
  }
  if (e.target.matches('[data-b-speaker]')) { balloonOf(e.target.dataset.bSpeaker).speaker = e.target.value; queueBalloonSave(); }
  if (e.target.matches('[data-cast-add]') && e.target.value) {
    readCastRoles();
    castDraft.entries.set(e.target.value, {included: true, role: ''});
    rerenderCast();
    $(`[data-cast-role="${e.target.value}"]`)?.focus();
  }
  if (e.target.matches('[data-form="asset"] input[name="kind"]')) applyKindToForm(e.target.form, e.target.value);
});

async function addPhotos(input, list = input.files, {reopen = true} = {}) {
  const id = input.dataset.addPhoto;
  const files = await Promise.all([...list].map(f => toSupportedImage(f)));
  let asset;
  for (const file of files) {
    const data = new FormData();
    data.append('image', file);
    asset = await api(`/assets/${id}/photos`, {method: 'POST', body: data});
  }
  if (asset) {
    replaceAsset(asset);
    if (reopen) openAsset(id);
    toast(plural(files.length, 'foto adicionada', 'fotos adicionadas') + (reopen ? '' : ` à ficha de ${asset.name}`));
  }
}

/* Colar (Ctrl+V) ou arrastar imagens: vão para onde faz sentido na tela aberta. */
async function receiveImages(list, target) {
  const files = imageFiles(list);
  if (!files.length) return false;
  const assetPhotos = modal.open && $('#modal-body [data-add-photo]');
  const assetForm = modal.open && $('#modal-body [data-form="asset"] [data-photo]');
  const assetEdit = modal.open && $('#modal-body [data-form="asset-edit"]');
  const card = target?.closest?.('[data-frame]');
  const description = target?.closest?.('[data-description]') || (card && $('[data-description]', card));
  if (assetPhotos) await addPhotos(assetPhotos, files);
  else if (assetEdit) await addPhotos({dataset: {addPhoto: assetEdit.dataset.id}}, files, {reopen: false});
  else if (assetForm) {
    const merged = new DataTransfer();
    [...assetForm.files, ...files].slice(0, 12).forEach(f => merged.items.add(f));
    assetForm.files = merged.files;
    previewPhoto(assetForm);
  } else if (description && !modal.open) {
    await attachToFrame(description.dataset.description, files);
  } else {
    toast('Para usar a imagem, cole na descrição de um card ou com a ficha de um personagem aberta.', 'error');
    return false;
  }
  return true;
}
document.addEventListener('paste', e => {
  if (!hasClipboardImage(e.clipboardData)) return;
  e.preventDefault();
  clipboardImages(e.clipboardData).then(files => receiveImages(files, e.target)).catch(fail);
});
document.addEventListener('dragover', e => {
  if (![...(e.dataTransfer?.items || [])].some(i => i.kind === 'file')) return;
  e.preventDefault();
  e.target.closest?.('.photo-drop, .photo-tile.add, .frame')?.classList.add('drop-hover');
});
document.addEventListener('dragleave', e => e.target.closest?.('.drop-hover')?.classList.remove('drop-hover'));
document.addEventListener('drop', e => {
  if (!e.dataTransfer?.files?.length && !hasClipboardImage(e.dataTransfer)) return;
  e.preventDefault();
  document.querySelectorAll('.drop-hover').forEach(el => el.classList.remove('drop-hover'));
  // Soltar sobre um card anexa a ele.
  const card = e.target.closest?.('[data-frame]');
  const target = card ? $('[data-description]', card) : e.target;
  const dt = e.dataTransfer;
  clipboardImages(dt).then(files => receiveImages(files, target)).catch(fail);
});

document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && $('#shell').classList.contains('nav-open')) toggleNav(false);
  if (modal.open && modal.dataset.kind === 'lightbox' && !$('[data-approve]') && (e.key === 'ArrowLeft' || e.key === 'ArrowRight')) {
    const nav = $(`.lb-nav.${e.key === 'ArrowLeft' ? 'prev' : 'next'}`);
    if (nav && !nav.disabled) { e.preventDefault(); nav.click(); }
  }
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && e.target.matches('[data-description], [data-feedback]')) {
    const button = e.target.closest('[data-frame]')?.querySelector('.frame-actions [data-action="generate"]');
    if (button && !button.disabled) { e.preventDefault(); button.click(); }
  }
});

$('#provider').addEventListener('change', e => {
  state.provider = e.target.value;
  store.set('hq-provider', state.provider);
  updateProviderNote();
  renderGenOptions();
});
$('#model').addEventListener('change', e => store.set(`hq-model-${state.provider}`, e.target.value));
$('#effort').addEventListener('change', e => store.set(`hq-effort-${state.provider}`, e.target.value));
$('#menu-btn').addEventListener('click', () => toggleNav());
$('#scrim').addEventListener('click', () => toggleNav(false));

/* ---------- Atualização periódica da fila ---------- */
async function poll() {
  if (!state.comic || document.hidden) return;
  const comicId = state.comic.id, seq = mutationSeq;
  try {
    const frames = await api(`/comics/${comicId}/frames`);
    if (state.comic?.id !== comicId || seq !== mutationSeq) return;
    const structural = frames.length !== state.frames.length || frames.some((f, i) => f.id !== state.frames[i]?.id);
    state.frames = mergeLocal(frames);
    updateCover();
    if (structural) render(); else refreshFrames();
  } catch { /* Um erro de rede eventual será informado na próxima ação. */ }
}

/* ---------- Início ---------- */
async function init() {
  try {
    state.providers = await api('/providers');
    renderProviders();
    state.projects = await api('/projects');
    const stored = store.get('hq-project');
    await loadProject(state.projects.find(p => p.id === stored)?.id || state.projects[0]?.id || null, {restoreComic: true});
    setInterval(poll, 2000);
  } catch (error) {
    renderSidebar();
    $('#main').innerHTML = `<div class="page">${emptyHtml({iconName: 'alert', title: 'Não foi possível carregar o editor',
      text: esc(error?.message || String(error)), action: '<button class="btn secondary" type="button" data-action="reload">Tentar de novo</button>'})}</div>`;
  }
}
init();
