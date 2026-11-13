/* A navegação não depende de bibliotecas, servidor ou conexão com a internet. */
(() => {
  'use strict';
  const slides = Array.from(document.querySelectorAll('.slide'));
  const frame = document.querySelector('#frame');
  const fullscreenButton = document.querySelector('#fullscreen');
  const fullscreenLabel = document.querySelector('#fullscreen-label');
  const counter = document.querySelector('#counter');
  const live = document.querySelector('#live');
  const progress = document.querySelector('#progress-fill');
  const status = document.querySelector('#status');
  let current = 0;
  let statusTimer;
  let lastStep = 0;
  const initialHash = /^#slide-(\d+)$/.exec(location.hash);
  if (initialHash) current = Math.min(slides.length - 1, Math.max(0, Number(initialHash[1]) - 1));

  function fit() {
    const fullscreen = Boolean(document.fullscreenElement);
    const availableHeight = window.innerHeight - (fullscreen ? 0 : 66);
    const availableWidth = window.innerWidth - (fullscreen ? 0 : 32);
    const scale = Math.max(.01, Math.min(availableWidth / 1920, availableHeight / 1080));
    document.documentElement.style.setProperty('--scale', scale);
    frame.style.marginTop = fullscreen ? '0px' : '-33px';
  }
  function show(index, direction = 0) {
    if (index < 0 || index >= slides.length) return;
    slides.forEach((slide, i) => {
      slide.classList.toggle('is-active', i === index);
      slide.classList.remove('entering');
      slide.setAttribute('aria-hidden', String(i !== index));
      slide.inert = i !== index;
    });
    current = index;
    const slide = slides[index];
    if (direction) {
      slide.style.setProperty('--direction', direction);
      void slide.offsetWidth;
      slide.classList.add('entering');
    }
    const label = slide.dataset.title || `Slide ${index + 1}`;
    counter.textContent = `${String(index + 1).padStart(2, '0')} / ${slides.length}`;
    live.textContent = `Slide ${index + 1} de ${slides.length}: ${label}`;
    document.title = `${index + 1}. ${label} · DITE`;
    progress.style.width = `${(index + 1) / slides.length * 100}%`;
    try { history.replaceState(null, '', `#slide-${String(index + 1).padStart(2, '0')}`); } catch (_) { /* file:// também funciona. */ }
  }
  function notice(message) {
    clearTimeout(statusTimer);
    status.textContent = message;
    statusTimer = setTimeout(() => { status.textContent = ''; }, 5500);
  }
  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
      else notice('Use a opção de tela cheia do seu navegador.');
    } catch (_) { notice('Não foi possível ativar a tela cheia. Use a opção de tela cheia do navegador.'); }
  }
  fullscreenButton.addEventListener('click', () => { toggleFullscreen(); fullscreenButton.blur(); });
  document.addEventListener('fullscreenchange', () => {
    const fullscreen = Boolean(document.fullscreenElement);
    document.body.classList.toggle('presenting', fullscreen);
    fullscreenLabel.textContent = fullscreen ? 'Sair da tela cheia' : 'Tela cheia';
    fullscreenButton.setAttribute('aria-pressed', String(fullscreen));
    fullscreenButton.title = fullscreen ? 'Sair da tela cheia (F ou Esc)' : 'Tela cheia (F)';
    fit();
  });
  document.addEventListener('keydown', (event) => {
    if (event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.target.closest('input, textarea, select, [contenteditable="true"]')) return;
    if (event.key === 'ArrowRight' || event.key === 'ArrowLeft') {
      event.preventDefault();
      const now = performance.now();
      if (event.repeat && now - lastStep < 230) return;
      lastStep = now;
      show(current + (event.key === 'ArrowRight' ? 1 : -1), event.key === 'ArrowRight' ? 1 : -1);
    } else if (['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End', ' '].includes(event.key) && event.target.tagName !== 'BUTTON' && event.target.tagName !== 'A') {
      event.preventDefault();
    } else if (event.key.toLowerCase() === 'f' && !event.repeat) {
      event.preventDefault();
      toggleFullscreen();
    }
  });
  // Roda do mouse e gestos não deslocam nem trocam os slides.
  document.addEventListener('wheel', event => { if (!event.ctrlKey) event.preventDefault(); }, { passive: false });
  document.addEventListener('touchmove', event => event.preventDefault(), { passive: false });
  window.addEventListener('resize', fit);
  window.addEventListener('hashchange', () => {
    const match = /^#slide-(\d+)$/.exec(location.hash);
    if (match) show(Math.min(slides.length - 1, Math.max(0, Number(match[1]) - 1)));
  });
  show(current);
  fit();
})();
