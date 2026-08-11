const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

const transformRange = document.querySelector('[data-transform]');
const transformStatus = document.querySelector('#transform-status');
const sourcePaper = document.querySelector('.paper-source');
const targetPaper = document.querySelector('.paper-target');
const cleanSignature = document.querySelector('.clean-signature');

function updateTransformation(value) {
  const progress = Number(value) / 100;
  sourcePaper.style.transform = `translate(${progress * -115}px, ${progress * -22}px) rotate(${-2 - progress * 7}deg)`;
  sourcePaper.style.opacity = `${1 - progress * 0.58}`;
  targetPaper.style.transform = `translate(${progress * 26}px, ${progress * -8}px) rotate(${8 - progress * 7}deg)`;
  cleanSignature.style.opacity = `${Math.max(0, (progress - 0.28) * 1.4)}`;
  cleanSignature.style.transform = `translateX(${(1 - progress) * -80}px) scale(${0.82 + progress * 0.18})`;
  const message = progress < 0.35 ? 'Signature is selected in the source document.' : progress < 0.76 ? 'Signature is separating from the scanned document.' : 'Signature is clean and placed on the PDF.';
  transformStatus.textContent = message;
}

if (transformRange) {
  transformRange.addEventListener('input', (event) => updateTransformation(event.target.value));
  updateTransformation(transformRange.value);
}

document.querySelector('[data-demo-trigger]')?.addEventListener('click', () => {
  transformRange?.focus();
  transformRange?.animate([{ transform: 'scaleX(1)' }, { transform: 'scaleX(1.04)' }, { transform: 'scaleX(1)' }], { duration: 560, easing: 'ease-out' });
});

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('in-view');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.13 });
document.querySelectorAll('.reveal').forEach((element) => revealObserver.observe(element));

const header = document.querySelector('[data-header]');
window.addEventListener('scroll', () => {
  header?.classList.toggle('is-scrolled', window.scrollY > 16);
}, { passive: true });

const menuButton = document.querySelector('.menu-button');
const mobileNav = document.querySelector('#mobile-nav');
menuButton?.addEventListener('click', () => {
  const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
  menuButton.setAttribute('aria-expanded', String(!isOpen));
  mobileNav.hidden = isOpen;
});
mobileNav?.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
  menuButton?.setAttribute('aria-expanded', 'false');
  mobileNav.hidden = true;
}));

const vaultStatus = document.querySelector('.vault-status');
document.querySelectorAll('.vault-card').forEach((card) => {
  card.addEventListener('click', () => {
    document.querySelectorAll('.vault-card').forEach((item) => item.classList.remove('selected'));
    card.classList.add('selected');
    vaultStatus.textContent = `${card.dataset.mark} is selected in this illustrative Vault.`;
  });
});
document.querySelector('.vault-add')?.addEventListener('click', () => {
  vaultStatus.textContent = 'In the real app, this is where you add a cleaned signature to the Vault.';
});

const featureTabs = Array.from(document.querySelectorAll('[data-feature-tab]'));
const featurePanels = Array.from(document.querySelectorAll('[data-feature-panel]'));

function selectFeature(feature) {
  featureTabs.forEach((tab) => {
    const selected = tab.dataset.featureTab === feature;
    tab.classList.toggle('is-active', selected);
    tab.setAttribute('aria-selected', String(selected));
    tab.tabIndex = selected ? 0 : -1;
  });
  featurePanels.forEach((panel) => {
    const selected = panel.dataset.featurePanel === feature;
    panel.hidden = !selected;
    panel.classList.toggle('is-active', selected);
  });
}

featureTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectFeature(tab.dataset.featureTab));
  tab.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const nextIndex = event.key === 'Home' ? 0 : event.key === 'End' ? featureTabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + featureTabs.length) % featureTabs.length;
    featureTabs[nextIndex].focus();
    selectFeature(featureTabs[nextIndex].dataset.featureTab);
  });
});

const stage = document.querySelector('[data-stage]');
const cursor = document.querySelector('.cursor-ink');
if (!reduceMotion.matches && stage && cursor && window.matchMedia('(pointer:fine)').matches) {
  window.addEventListener('pointermove', (event) => {
    cursor.style.left = `${event.clientX}px`;
    cursor.style.top = `${event.clientY}px`;
  }, { passive: true });
  stage.addEventListener('pointermove', (event) => {
    const bounds = stage.getBoundingClientRect();
    const x = (event.clientX - bounds.left) / bounds.width - 0.5;
    const y = (event.clientY - bounds.top) / bounds.height - 0.5;
    document.querySelector('.paper-stack').style.transform = `translate(${x * 9}px, ${y * 10}px) rotate(${x * 1.2}deg)`;
    cursor.classList.add('active');
  });
  stage.addEventListener('pointerleave', () => {
    document.querySelector('.paper-stack').style.transform = '';
    cursor.classList.remove('active');
  });
}
