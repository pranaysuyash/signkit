const stages = {
  extract: {
    source: "../../../Docs/review/assets/current-premium-runtime-capture-20260731/06_07_selection_drawn_20260731_174301.png",
    alt: "Current SignKit extraction workspace showing an authorized selection from a source image",
    caption: "Make a deliberate selection from the source, then refine it in the desktop workspace.",
    counter: "01 / 03"
  },
  place: {
    source: "../../../Docs/review/assets/current-runtime-capture-20260731/18_19_pdf_loaded_20260731_174025.png",
    alt: "Current SignKit PDF signing workspace with a loaded PDF",
    caption: "Move into the PDF workspace when the document is ready for the next precise step.",
    counter: "02 / 03"
  },
  keep: {
    source: "../../../Docs/review/assets/current-premium-product-surfaces-20260731/06_vault_20260731_174419.png",
    alt: "Current SignKit Vault workspace",
    caption: "The current Vault is a workspace surface for retaining the context that makes repeat document work possible.",
    counter: "03 / 03"
  }
};

const image = document.querySelector("#workflow-image");
const caption = document.querySelector("#workflow-caption");
const counter = document.querySelector("#workflow-counter");
const tabs = [...document.querySelectorAll(".stage-tab")];

function selectStage(key) {
  const stage = stages[key];
  if (!stage || !image) return;
  tabs.forEach((tab) => {
    const active = tab.dataset.screen === key;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  image.classList.add("is-changing");
  window.setTimeout(() => {
    image.src = stage.source;
    image.alt = stage.alt;
    caption.textContent = stage.caption;
    counter.textContent = stage.counter;
    image.classList.remove("is-changing");
  }, 180);
}

tabs.forEach((tab) => tab.addEventListener("click", () => selectStage(tab.dataset.screen)));

const motionOkay = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (motionOkay) {
  const parallaxItems = [...document.querySelectorAll("[data-parallax]")];
  document.querySelector(".hero")?.addEventListener("pointermove", (event) => {
    const x = event.clientX / window.innerWidth - .5;
    const y = event.clientY / window.innerHeight - .5;
    parallaxItems.forEach((element) => {
      const depth = Number(element.dataset.parallax);
      element.style.translate = `${x * depth * 1000}px ${y * depth * 700}px`;
    });
  });
}
