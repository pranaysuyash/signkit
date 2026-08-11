const cleanupControl = document.querySelector("#cleanup-control");
const cleanupOutput = document.querySelector("#cleanup-output");
const cleanupValue = document.querySelector("#cleanup-value");
const assetStage = document.querySelector("#asset-stage");
const saveAssetButton = document.querySelector("#save-asset");
const placeAssetButton = document.querySelector("#place-asset");
const assetStatus = document.querySelector("#asset-status");
const signatureField = document.querySelector("#signature-field");
const caseState = document.querySelector("#case-state");
const receipt = document.querySelector("#case-receipt");
const steps = [...document.querySelectorAll("[data-case-step]")];

let assetSaved = false;
let placed = false;

function setCurrentStep(name) {
  steps.forEach((step) => step.classList.toggle("is-current", step.dataset.caseStep === name));
}

function updateCleanup({ announceStage = true } = {}) {
  const value = Number(cleanupControl.value);
  cleanupOutput.textContent = `${value}%`;
  cleanupValue.textContent = `${value}%`;
  assetStage.style.setProperty("--signature-opacity", Math.max(0.55, value / 100));
  assetStage.style.setProperty("--signature-contrast", 1 + value / 105);
  if (announceStage && !assetSaved && !placed) {
    setCurrentStep("refine");
    caseState.textContent = "Step 2 of 3 · inspect the cleanup";
  }
}

function updateReceipt() {
  receipt.innerHTML = `<span><b>Source</b> local sample</span><span><b>Asset</b> ${assetSaved ? "saved locally in concept" : "not saved"}</span><span><b>PDF</b> ${placed ? "placement shown in concept" : "not changed"}</span>`;
}

function saveAsset() {
  assetSaved = true;
  setCurrentStep("place");
  caseState.textContent = "Step 3 of 3 · choose the PDF field";
  assetStatus.textContent = "Local asset saved in this interactive concept. You can now place it in the target PDF.";
  saveAssetButton.innerHTML = 'Local asset ready <span aria-hidden="true">✓</span>';
  updateReceipt();
}

function placeAsset() {
  if (!assetSaved) {
    saveAsset();
  }
  placed = true;
  signatureField.classList.add("is-placed");
  setCurrentStep("ready");
  caseState.textContent = "Ready · placement is visible on Page 1";
  placeAssetButton.innerHTML = 'Placement shown <span aria-hidden="true">✓</span>';
  assetStatus.textContent = "The prepared asset is now shown in the chosen target field.";
  updateReceipt();
}

cleanupControl.addEventListener("input", () => updateCleanup());
saveAssetButton.addEventListener("click", saveAsset);
placeAssetButton.addEventListener("click", placeAsset);

assetStage.setAttribute("draggable", "true");
assetStage.addEventListener("dragstart", (event) => {
  event.dataTransfer.setData("text/plain", "prepared-signature");
  event.dataTransfer.effectAllowed = "copy";
});
signatureField.addEventListener("dragover", (event) => {
  event.preventDefault();
  event.dataTransfer.dropEffect = "copy";
});
signatureField.addEventListener("drop", (event) => {
  event.preventDefault();
  if (event.dataTransfer.getData("text/plain") === "prepared-signature") {
    placeAsset();
  }
});

updateCleanup({ announceStage: false });
updateReceipt();
