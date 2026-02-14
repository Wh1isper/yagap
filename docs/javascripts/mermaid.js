const mermaidConfig = {
  startOnLoad: false,
  securityLevel: "loose",
  theme: "default",
};

let mermaidInitialized = false;

function renderMermaid() {
  if (typeof mermaid === "undefined") {
    return;
  }

  if (!mermaidInitialized) {
    mermaid.initialize(mermaidConfig);
    mermaidInitialized = true;
  }

  const nodes = document.querySelectorAll("pre.mermaid");
  if (!nodes.length) {
    return;
  }

  for (const node of nodes) {
    node.removeAttribute("data-processed");
  }

  mermaid.run({ nodes });
}

if (typeof document$ !== "undefined") {
  document$.subscribe(renderMermaid);
} else {
  document.addEventListener("DOMContentLoaded", renderMermaid);
}
