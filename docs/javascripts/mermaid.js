const mermaidConfig = {
  startOnLoad: false,
  securityLevel: "loose",
  theme: "default",
};

let mermaidInitialized = false;

function looksLikeMermaid(text) {
  const source = (text || "").trim();
  return /^(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph|quadrantChart|requirementDiagram|c4Context|sankey-beta|xychart-beta)\b/m.test(
    source,
  );
}

function renderMermaid() {
  if (typeof mermaid === "undefined") {
    return;
  }

  if (!mermaidInitialized) {
    mermaid.initialize(mermaidConfig);
    mermaidInitialized = true;
  }

  const allCodeNodes = document.querySelectorAll("pre code");
  for (const codeNode of allCodeNodes) {
    const pre = codeNode.closest("pre");
    if (!pre) {
      continue;
    }

    const isMermaidClass =
      codeNode.classList.contains("language-mermaid") ||
      pre.classList.contains("mermaid");
    const isMermaidText = looksLikeMermaid(codeNode.textContent);

    if (!isMermaidClass && !isMermaidText) {
      continue;
    }

    pre.classList.add("mermaid");
    pre.textContent = (codeNode.textContent || "").trim();
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
