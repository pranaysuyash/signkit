const stages = {
  source: {
    label: "01 / Select the mark",
    alt: "Illustrative SignKit source selection workspace concept",
    caption: "Illustrative concept: the selection remains visible while you prepare the signature.",
  },
  refine: {
    label: "02 / Review the extraction",
    alt: "Illustrative SignKit signature refinement workspace concept",
    caption: "Illustrative concept: inspect the cleaned mark before it enters the document.",
  },
  place: {
    label: "03 / Continue in the PDF",
    alt: "Illustrative SignKit PDF placement workspace concept",
    caption: "Illustrative concept: place the prepared mark in the PDF while it is still in context.",
  },
};

const image = document.querySelector("#stage-image");
const label = document.querySelector("#stage-label");
const caption = document.querySelector("#stage-caption");
const panel = document.querySelector("#workspace-screen");
const tabs = [...document.querySelectorAll(".workflow-step")];

function showStage(stageName) {
  const stage = stages[stageName];
  if (!stage) return;

  tabs.forEach((tab) => {
    const active = tab.dataset.stage === stageName;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  panel.setAttribute("aria-labelledby", `step-${stageName}`);
  panel.dataset.stage = stageName;

  image.classList.add("is-changing");
  window.setTimeout(() => {
    image.alt = stage.alt;
    label.textContent = stage.label;
    caption.textContent = stage.caption;
    image.classList.remove("is-changing");
  }, 130);
}

tabs.forEach((tab) => tab.addEventListener("click", () => showStage(tab.dataset.stage)));

tabs.forEach((tab, index) => {
  tab.addEventListener("keydown", (event) => {
    if (!["ArrowDown", "ArrowRight", "ArrowUp", "ArrowLeft"].includes(event.key)) return;
    event.preventDefault();
    const direction = ["ArrowDown", "ArrowRight"].includes(event.key) ? 1 : -1;
    const nextTab = tabs[(index + direction + tabs.length) % tabs.length];
    nextTab.focus();
    showStage(nextTab.dataset.stage);
  });
});
