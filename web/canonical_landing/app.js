(() => {
  const states = {
    source: { label: 'SOURCE / INTAKE', status: 'SOURCE FOUND', note: 'Source material is present. The next decision is legibility.', copy: 'Start with the source document and its context before making a mark.' },
    mark: { label: 'MARK / EXTRACT', status: 'MARK EXTRACTED', note: 'The mark is isolated as an inspectable object, not a hidden side effect.', copy: 'Make the extracted mark legible before asking where it belongs.' },
    clean: { label: 'CLEAN / REVIEW', status: 'MARK CLEAN', note: 'A clean mark can be compared with its source before placement.', copy: 'Review the mark against the source. This is where uncertainty should surface.' },
    place: { label: 'PLACE / CONTEXT', status: 'PLACEMENT READY', note: 'Placement is shown with document context, scale, and date visible.', copy: 'Place the mark in context, with enough information to inspect the decision.' },
    ready: { label: 'READY / EXPORT', status: 'READY TO EXPORT', note: 'The prepared PDF is ready for the next explicit operator action.', copy: 'Ready means prepared for export, not signed in a browser or legally interpreted.' },
  };
  const steps = [...document.querySelectorAll('[data-completion-step]')];
  const state = document.querySelector('#completion-state');
  const status = document.querySelector('#completion-status');
  const note = document.querySelector('#completion-note');
  const copy = document.querySelector('#completion-copy');
  const advance = document.querySelector('#completion-advance');
  const board = document.querySelector('#completion-step-description');
  let index = 0;

  const activate = (name, moveFocus = false) => {
    const next = steps.findIndex((step) => step.dataset.completionStep === name);
    if (next < 0) return;
    index = next;
    const content = states[name];
    steps.forEach((step, stepIndex) => {
      const active = stepIndex === index;
      step.classList.toggle('is-active', active);
      step.setAttribute('aria-selected', String(active));
      step.setAttribute('aria-current', active ? 'step' : 'false');
      step.setAttribute('tabindex', active ? '0' : '-1');
    });
    state.textContent = content.label;
    status.textContent = content.status;
    note.textContent = content.note;
    copy.textContent = content.copy;
    advance.disabled = index === steps.length - 1;
    advance.innerHTML = advance.disabled ? 'Ready state <span aria-hidden="true">✓</span>' : 'Advance state <span aria-hidden="true">→</span>';
    if (moveFocus) steps[index].focus();
  };

  steps.forEach((step) => {
    step.addEventListener('click', () => activate(step.dataset.completionStep));
    step.addEventListener('keydown', (event) => {
      const keys = ['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'];
      if (!keys.includes(event.key)) return;
      event.preventDefault();
      if (event.key === 'Home') return activate(steps[0].dataset.completionStep, true);
      if (event.key === 'End') return activate(steps[steps.length - 1].dataset.completionStep, true);
      const direction = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? 1 : -1;
      activate(steps[(index + direction + steps.length) % steps.length].dataset.completionStep, true);
    });
  });
  advance.addEventListener('click', () => { if (index < steps.length - 1) activate(steps[index + 1].dataset.completionStep); board.focus(); });

  const localWorkspace = document.querySelectorAll('[data-local-workspace]');
  const localHost = ['localhost', '127.0.0.1', '[::1]'].includes(window.location.hostname);
  if (localHost) {
    const workspaceUrl = `${window.location.protocol}//${window.location.hostname}:8001/workspace-app/`;
    localWorkspace.forEach((link) => { link.href = workspaceUrl; });
    const workspaceNote = document.querySelector('#workspace-note');
    if (workspaceNote) workspaceNote.textContent = 'Local preview link targets the companion workspace on port 8001.';
  }
})();
