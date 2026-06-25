'use strict';

/* ─── TELEGRAM ───────────────────────────── */
const TG_TOKEN   = '8650746508:AAEUc9iDvWD0GdGGcSaHHZFMphuwaaQqT7g';
const TG_CHAT_ID = '490873482';
const TG_API     = `https://api.telegram.org/bot${TG_TOKEN}/sendMessage`;

async function sendToTelegram(text) {
  try {
    await fetch(TG_API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: TG_CHAT_ID, text, parse_mode: 'Markdown' }),
    });
  } catch {}
}

/* ─── UTILS ─────────────────────────────── */
const $ = id => document.getElementById(id);
const $$ = sel => document.querySelectorAll(sel);

/* ─── HEADER: shadow on scroll ──────────── */
const header = $('header');
if (header) {
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
}

/* ─── BURGER MENU ────────────────────────── */
const burger = $('burger');
const nav    = $('nav');
if (burger && nav) {
  burger.addEventListener('click', () => {
    const open = burger.classList.toggle('open');
    nav.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', String(open));
  });
  nav.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
      burger.classList.remove('open');
      nav.classList.remove('open');
      burger.setAttribute('aria-expanded', 'false');
    });
  });
}

/* ─── SMOOTH SCROLL ──────────────────────── */
document.addEventListener('click', e => {
  const link = e.target.closest('a[href^="#"]');
  if (!link) return;
  const target = document.querySelector(link.getAttribute('href'));
  if (!target) return;
  e.preventDefault();
  const top = target.getBoundingClientRect().top + window.scrollY - 80;
  window.scrollTo({ top, behavior: 'smooth' });
});

/* ─── PHONE MASK ─────────────────────────── */
function applyPhoneMask(input) {
  input.addEventListener('input', function () {
    let d = this.value.replace(/\D/g, '').slice(0, 11);
    if (d.startsWith('8')) d = '7' + d.slice(1);
    if (d && !d.startsWith('7')) d = '7' + d;
    let out = '';
    if (d.length > 0) out = '+7';
    if (d.length > 1) out += ' (' + d.slice(1, 4);
    if (d.length >= 4) out += ') ' + d.slice(4, 7);
    if (d.length >= 7) out += '-' + d.slice(7, 9);
    if (d.length >= 9) out += '-' + d.slice(9, 11);
    this.value = out;
  });
}
$$('.js-phone-mask').forEach(applyPhoneMask);

/* ─── MODAL ──────────────────────────────── */
const modal       = $('modal');
const modalClose  = $('modalClose');
const modalOverlay = $('modalOverlay');
const modalForm   = $('modalForm');
const modalSuccess = $('modalSuccess');

function openModal() {
  if (!modal) return;
  modal.classList.add('open');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  if (!modal) return;
  modal.classList.remove('open');
  document.body.style.overflow = '';
}

$$('.js-open-modal').forEach(btn => btn.addEventListener('click', openModal));
if (modalClose)   modalClose.addEventListener('click', closeModal);
if (modalOverlay) modalOverlay.addEventListener('click', closeModal);
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });

if (modalForm) {
  modalForm.addEventListener('submit', async e => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(modalForm));
    try {
      const text =
        `🔔 *Новая заявка — Заказать звонок*\n\n` +
        `👤 *Имя:* ${data.name || '—'}\n` +
        `📞 *Телефон:* ${data.phone || '—'}`;
      await sendToTelegram(text);
    } catch {}
    modalForm.classList.add('hidden');
    modalSuccess.classList.remove('hidden');
    setTimeout(closeModal, 2500);
  });
}

/* ─── LEAD FORM ──────────────────────────── */
const leadForm    = $('leadForm');
const leadSuccess = $('leadSuccess');

if (leadForm) {
  leadForm.addEventListener('submit', async e => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(leadForm));
    try {
      let text =
        `🔔 *Новая заявка — Расчёт стоимости*\n\n` +
        `👤 *Имя:* ${data.name || '—'}\n` +
        `📞 *Телефон:* ${data.phone || '—'}`;
      if (data.email)   text += `\n📧 *Email:* ${data.email}`;
      if (data.comment) text += `\n💬 *Комментарий:* ${data.comment}`;
      await sendToTelegram(text);
    } catch {}
    leadForm.classList.add('hidden');
    leadSuccess.classList.remove('hidden');
  });
}

/* ─── PRODUCTION TOGGLE ──────────────────── */
const productionToggle = $('productionToggle');
const productionMore   = $('productionMore');

if (productionToggle && productionMore) {
  productionToggle.addEventListener('click', () => {
    const isOpen = !productionMore.classList.contains('hidden');
    productionMore.classList.toggle('hidden', isOpen);
    productionToggle.textContent = isOpen
      ? 'Подробнее о производстве'
      : 'Скрыть';
  });
}

/* ─── GALLERY LIGHTBOX ───────────────────── */
const lightbox        = $('lightbox');
const lightboxOverlay = $('lightboxOverlay');
const lightboxClose   = $('lightboxClose');
const lightboxImg     = $('lightboxImg');
const lightboxCaption = $('lightboxCaption');
const lightboxPrev    = $('lightboxPrev');
const lightboxNext    = $('lightboxNext');

const galleryItems = Array.from($$('.gallery__item'));
let lightboxIndex  = 0;

function showLightbox(index) {
  if (!lightbox || !galleryItems.length) return;
  lightboxIndex = (index + galleryItems.length) % galleryItems.length;
  const item = galleryItems[lightboxIndex];
  lightboxImg.style.backgroundImage    = item.style.backgroundImage;
  lightboxImg.style.backgroundSize     = 'cover';
  lightboxImg.style.backgroundPosition = 'center';
  lightboxImg.style.backgroundColor    = '#1A1A1A';
  lightboxCaption.textContent  = item.dataset.caption || '';
  lightbox.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
}
function closeLightbox() {
  if (!lightbox) return;
  lightbox.classList.add('hidden');
  document.body.style.overflow = '';
}

galleryItems.forEach(item => {
  item.addEventListener('click', () => showLightbox(parseInt(item.dataset.index, 10)));
});
if (lightboxClose)   lightboxClose.addEventListener('click', closeLightbox);
if (lightboxOverlay) lightboxOverlay.addEventListener('click', closeLightbox);
if (lightboxPrev)    lightboxPrev.addEventListener('click', () => showLightbox(lightboxIndex - 1));
if (lightboxNext)    lightboxNext.addEventListener('click', () => showLightbox(lightboxIndex + 1));

document.addEventListener('keydown', e => {
  if (lightbox && !lightbox.classList.contains('hidden')) {
    if (e.key === 'ArrowLeft')  showLightbox(lightboxIndex - 1);
    if (e.key === 'ArrowRight') showLightbox(lightboxIndex + 1);
    if (e.key === 'Escape')     closeLightbox();
  }
});

/* ─── REVIEWS CAROUSEL ───────────────────── */
const reviewsTrack = $('reviewsTrack');
const reviewPrev   = $('reviewPrev');
const reviewNext   = $('reviewNext');
const dotsWrap     = $('reviewDots');

let reviewIndex = 0;
const reviewCards = reviewsTrack ? Array.from(reviewsTrack.children) : [];
const reviewTotal = reviewCards.length;

function buildDots() {
  if (!dotsWrap) return;
  dotsWrap.innerHTML = '';
  reviewCards.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'reviews__dot' + (i === 0 ? ' active' : '');
    dot.setAttribute('aria-label', `Отзыв ${i + 1}`);
    dot.addEventListener('click', () => goToReview(i));
    dotsWrap.appendChild(dot);
  });
}

function goToReview(index) {
  reviewIndex = (index + reviewTotal) % reviewTotal;
  if (reviewsTrack) {
    reviewsTrack.style.transform = `translateX(-${reviewIndex * 100}%)`;
  }
  dotsWrap && dotsWrap.querySelectorAll('.reviews__dot').forEach((d, i) => {
    d.classList.toggle('active', i === reviewIndex);
  });
}

if (reviewPrev) reviewPrev.addEventListener('click', () => goToReview(reviewIndex - 1));
if (reviewNext) reviewNext.addEventListener('click', () => goToReview(reviewIndex + 1));
buildDots();

/* ─── FAQ ACCORDION ──────────────────────── */
$$('.faq-question').forEach(btn => {
  btn.addEventListener('click', () => {
    const item   = btn.closest('.faq-item');
    const isOpen = item.classList.contains('open');
    $$('.faq-item.open').forEach(el => el.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

/* ─── REVEAL ON SCROLL ───────────────────── */
const revealObserver = new IntersectionObserver(entries => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

$$('.reveal').forEach(el => revealObserver.observe(el));

/* ─── MOBILE INFINITE SLIDERS ───────────── */
function initSlider(trackId, prevId, nextId, perPage) {
  if (window.innerWidth > 768) return;

  const track   = $(trackId);
  const prevBtn = $(prevId);
  const nextBtn = $(nextId);
  if (!track || !prevBtn || !nextBtn) return;

  const origItems = Array.from(track.children);
  const total     = origItems.length;

  // Prefix clones: last perPage originals inserted at start
  origItems.slice(-perPage).forEach(el => {
    const c = el.cloneNode(true);
    c.classList.add('sl-clone');
    c.setAttribute('aria-hidden', 'true');
    track.insertBefore(c, track.firstChild);
  });

  // Suffix clones: first perPage originals appended at end
  origItems.slice(0, perPage).forEach(el => {
    const c = el.cloneNode(true);
    c.classList.add('sl-clone');
    c.setAttribute('aria-hidden', 'true');
    track.appendChild(c);
  });

  let cur  = perPage; // start after prefix clones
  let busy = false;

  function itemW() {
    return track.children[cur] ? track.children[cur].offsetWidth : 0;
  }

  function setPos(animate) {
    track.style.transition = animate
      ? 'transform 0.42s cubic-bezier(0.16,1,0.3,1)'
      : 'none';
    track.style.transform = `translateX(-${cur * itemW()}px)`;
    if (!animate) void track.offsetWidth; // force reflow
  }

  function go(dir) {
    if (busy) return;
    busy = true;
    cur += dir * perPage;
    setPos(true);
    setTimeout(() => {
      if (cur >= total + perPage) { cur = perPage; setPos(false); }
      if (cur < perPage)          { cur = total;   setPos(false); }
      busy = false;
    }, 450);
  }

  prevBtn.addEventListener('click', () => go(-1));
  nextBtn.addEventListener('click', () => go(1));
  setPos(false);
}

initSlider('productsTrack', 'productsPrev', 'productsNext', 1);
initSlider('paletteTrack',  'palettePrev',  'paletteNext',  2);
initSlider('galleryTrack',  'galleryPrev',  'galleryNext',  1);
