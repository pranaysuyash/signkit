const workflow = {
  source: {
    image: "../../../Docs/review/assets/current-premium-runtime-capture-20260731/06_07_selection_drawn_20260731_174301.png",
    alt: "Current SignKit source selection workspace",
    caption: "Current desktop capture: source selection and processing controls."
  },
  refine: {
    image: "../../../Docs/review/assets/current-premium-runtime-capture-20260731/10_11_extraction_result_20260731_174311.png",
    alt: "Current SignKit extraction workspace with processing result visible",
    caption: "Current desktop capture: extraction result in the workspace."
  },
  pdf: {
    image: "../../../Docs/review/assets/current-premium-runtime-capture-20260731/21_22_pdf_workflow_complete_20260731_174332.png",
    alt: "Current SignKit PDF workspace with a completed sample workflow",
    caption: "Current desktop capture: PDF workspace with the completed sample workflow."
  }
};

const image = document.querySelector("#workflow-image");
const caption = document.querySelector("#workflow-caption");
const tabs = [...document.querySelectorAll(".workflow-tab")];

function showWorkflowStep(step) {
  const detail = workflow[step];
  if (!detail) return;
  tabs.forEach((tab) => {
    const active = tab.dataset.step === step;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  image.classList.add("changing");
  window.setTimeout(() => {
    image.src = detail.image;
    image.alt = detail.alt;
    caption.textContent = detail.caption;
    image.classList.remove("changing");
  }, 160);
}

tabs.forEach((tab) => tab.addEventListener("click", () => showWorkflowStep(tab.dataset.step)));
