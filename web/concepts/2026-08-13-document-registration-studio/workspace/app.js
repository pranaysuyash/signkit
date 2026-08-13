(() => {
  const data = {
    acknowledgement: { index: 'RECORD / 01', title: 'Acknowledgement', subtitle: 'Mark extracted / needs review', evidence: 'Source and mark retained', recovery: 'Review source before export' },
    placement: { index: 'RECORD / 02', title: 'Placement preparation', subtitle: 'Context aligned / local', evidence: 'Prepared PDF and placement visible', recovery: 'Return to placement context' },
    receipt: { index: 'RECORD / 03', title: 'Inspection receipt', subtitle: 'Source retained / logged', evidence: 'Local inspection receipt', recovery: 'Open source reference' }
  };
  const records = [...document.querySelectorAll('[data-record]')];
  const title = document.getElementById('passport-title');
  const subtitle = document.getElementById('passport-subtitle');
  const evidence = document.getElementById('passport-evidence');
  const recovery = document.getElementById('passport-recovery');
  const index = document.getElementById('passport-index');
  const feedback = document.getElementById('workspace-feedback');
  const count = document.getElementById('toolbar-count');
  const reviewButton = document.getElementById('mark-review');
  const select = (name) => {
    const record = records.find((item) => item.dataset.record === name);
    if (!record) return;
    const selected = data[name];
    records.forEach((item) => { const active = item === record; item.classList.toggle('is-active', active); item.setAttribute('aria-pressed', String(active)); });
    title.textContent = selected.title; subtitle.textContent = selected.subtitle; evidence.textContent = selected.evidence; recovery.textContent = selected.recovery; index.textContent = selected.index;
    reviewButton.disabled = record.dataset.status !== 'review';
    feedback.textContent = `Selected record: ${name}. No backend state changed.`;
  };
  records.forEach((record) => record.addEventListener('click', () => select(record.dataset.record)));
  document.querySelectorAll('[data-filter]').forEach((button) => button.addEventListener('click', () => {
    const filter = button.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach((item) => { item.classList.toggle('is-active', item === button); item.setAttribute('aria-pressed', String(item === button)); });
    let visible = 0;
    records.forEach((record) => { const show = filter === 'all' || record.dataset.status === filter; record.hidden = !show; if (show) visible += 1; });
    count.textContent = `${visible} record${visible === 1 ? '' : 's'} / illustrative`;
    feedback.textContent = `Filter: ${filter}. No backend state changed.`;
  }));
  reviewButton.addEventListener('click', () => { reviewButton.textContent = 'Review noted'; feedback.textContent = 'Review note recorded for this candidate view only. No backend state changed.'; });
  document.getElementById('new-record').addEventListener('click', () => { feedback.textContent = 'New record is a future workflow. No backend state changed.'; });
})();
