const topologyData = {
  local: {
    status: "Available now",
    title: "Local execution",
    summary: "The desktop app operates without sync. Documents, signature assets, workflow state, and audit records remain on the customer’s device.",
    facts: [["Execution", "On the customer’s device"], ["Authority", "Local device"], ["Promise", "Core work remains viable offline"]],
    caveat: "Current product evidence supports the local desktop workflow. It does not imply that every future delivery mode is already available."
  },
  cloud: {
    status: "Product direction, not a current availability claim",
    title: "Cloud-native SignKit",
    summary: "The web product may become a complete cloud-native option, with its own execution, storage, recovery, audit, and support obligations. It must use the same canonical product and workflow model.",
    facts: [["Execution", "Cloud-native service"], ["Authority", "Cloud contract to be defined"], ["Promise", "Only after capability, identity, and proof gates close"]],
    caveat: "The minimum viable identity, tenancy, recovery, sync, and source-of-truth contract is still an open product decision."
  },
  hybrid: {
    status: "Product direction, not a current availability claim",
    title: "Hybrid coordination",
    summary: "Local and cloud components synchronize only capabilities and data the customer explicitly enables. Local execution stays viable while connected coordination adds value.",
    facts: [["Execution", "Local plus enabled cloud coordination"], ["Authority", "Explicit capability matrix required"], ["Promise", "No silent sync or duplicate product model"]],
    caveat: "The sync boundary, conflict model, and authoritative-state rules remain open until the Local, Cloud, and Hybrid capability contract is decided."
  }
};

const topologyTabs = [...document.querySelectorAll(".topology-tab")];
const status = document.querySelector("#topology-status");
const title = document.querySelector("#topology-title");
const summary = document.querySelector("#topology-summary");
const facts = document.querySelector("#topology-facts");
const caveat = document.querySelector("#topology-caveat");

function selectTopology(key) {
  const model = topologyData[key];
  if (!model) return;
  topologyTabs.forEach((tab) => {
    const active = tab.dataset.topology === key;
    tab.classList.toggle("is-active", active);
    tab.setAttribute("aria-selected", String(active));
  });
  status.textContent = model.status;
  title.textContent = model.title;
  summary.textContent = model.summary;
  facts.replaceChildren(...model.facts.map(([term, definition]) => {
    const row = document.createElement("div");
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = term;
    dd.textContent = definition;
    row.append(dt, dd);
    return row;
  }));
  caveat.textContent = model.caveat;
}

topologyTabs.forEach((tab) => tab.addEventListener("click", () => selectTopology(tab.dataset.topology)));
