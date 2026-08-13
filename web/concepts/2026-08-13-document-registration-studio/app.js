(() => {
  const states = {
    source: { label: 'SOURCE / INTAKE', status: 'SOURCE FOUND', note: 'Source material is present. The next decision is legibility.', description: 'Start with the source document and its context before making a mark.' },
    mark: { label: 'MARK / EXTRACT', status: 'MARK EXTRACTED', note: 'The mark is isolated as an inspectable object, not a hidden side effect.', description: 'Make the extracted mark legible before asking where it belongs.' },
    clean: { label: 'CLEAN / REVIEW', status: 'MARK CLEAN', note: 'A clean mark can be compared with its source before placement.', description: 'Review the mark against the source. This is where uncertainty should surface.' },
    place: { label: 'PLACE / CONTEXT', status: 'PLACEMENT READY', note: 'Placement is shown with document context, scale, and date visible.', description: 'Place the mark in context, with enough information to inspect the decision.' },
    ready: { label: 'READY / EXPORT', status: 'READY TO EXPORT', note: 'The prepared PDF is ready for the next explicit operator action.', description: 'Ready means prepared for export, not signed in a browser or legally interpreted.' }
  };
  const buttons = [...document.querySelectorAll('[data-stage]')];
  const state = document.getElementById('case-state');
  const markStatus = document.getElementById('mark-status');
  const markNote = document.getElementById('mark-note');
  const description = document.getElementById('case-description');
  const action = document.getElementById('case-action');
  const board = document.getElementById('case-board');
  let index = 0;
  const activate = (name, moveFocus = false) => {
    const next = buttons.findIndex((button) => button.dataset.stage === name);
    if (next < 0) return;
    index = next;
    const content = states[name];
    buttons.forEach((button, buttonIndex) => {
      const active = buttonIndex === index;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-selected', String(active));
    });
    state.textContent = content.label;
    markStatus.textContent = content.status;
    markNote.textContent = content.note;
    description.textContent = content.description;
    action.disabled = index === buttons.length - 1;
    action.innerHTML = action.disabled ? 'Ready state <span aria-hidden="true">✓</span>' : 'Advance state <span aria-hidden="true">→</span>';
    if (moveFocus) buttons[index].focus();
  };
  buttons.forEach((button) => button.addEventListener('click', () => activate(button.dataset.stage)));
  buttons.forEach((button) => button.addEventListener('focus', () => {
    const focusedIndex = buttons.indexOf(button);
    if (focusedIndex >= 0) index = focusedIndex;
  }));
  buttons.forEach((button) => button.addEventListener('keydown', (event) => {
    const keys = ['ArrowRight', 'ArrowDown', 'ArrowLeft', 'ArrowUp', 'Home', 'End'];
    if (!keys.includes(event.key)) return;
    event.preventDefault();
    if (event.key === 'Home') return activate(buttons[0].dataset.stage, true);
    if (event.key === 'End') return activate(buttons[buttons.length - 1].dataset.stage, true);
    const direction = event.key === 'ArrowRight' || event.key === 'ArrowDown' ? 1 : -1;
    const next = (index + direction + buttons.length) % buttons.length;
    activate(buttons[next].dataset.stage, true);
  }));
  action.addEventListener('click', () => {
    if (index < buttons.length - 1) activate(buttons[index + 1].dataset.stage);
    board.focus();
  });
})();
