let allData = null;
let flatSkills = [];
let scrollSyncGuard = false;

function getDataSrc() {
  return document.body.dataset.benchmarksSrc || "benchmarks.json";
}

function getRatingColor(rating) {
  const colors = {
    vague: "secondary",
    regular: "warning",
    good: "primary",
    outstanding: "success",
  };
  return colors[rating] || "secondary";
}

function getImprovementColor(improvement) {
  const colors = {
    yes: "success",
    no: "danger",
    neutral: "secondary",
  };
  return colors[improvement] || "secondary";
}

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function extractCodeBlocks(text) {
  if (!text) return "";
  const blocks = [];
  const regex = /```[a-zA-Z0-9_-]*\\n([\\s\\S]*?)```/g;
  let match;
  while ((match = regex.exec(text)) !== null) {
    blocks.push(match[1].trim());
  }
  if (blocks.length === 0) {
    return text;
  }
  return blocks.join("\\n\\n// ---\\n\\n");
}

function normalizeTestHeaders(text) {
  if (!text) return "";
  return text
    .split("\\n")
    .map((line) =>
      line.startsWith("// Test:")
        ? "// === " + line.replace("// ", "") + " ==="
        : line
    )
    .join("\\n");
}

function syncScroll(containerA, containerB) {
  if (!containerA || !containerB) return;
  if (scrollSyncGuard) return;
  scrollSyncGuard = true;
  const ratio = containerA.scrollTop / (containerA.scrollHeight - containerA.clientHeight || 1);
  containerB.scrollTop = ratio * (containerB.scrollHeight - containerB.clientHeight);
  scrollSyncGuard = false;
}

function clearSelect(selectEl, defaultLabel) {
  while (selectEl.options.length > 0) {
    selectEl.remove(0);
  }
  const opt = document.createElement("option");
  opt.value = "";
  opt.textContent = defaultLabel;
  selectEl.appendChild(opt);
}

async function fetchData() {
  const src = getDataSrc();
  const response = await fetch(src, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load ${src}: ${response.status}`);
  }
  return response.json();
}

function renderSummary(summary) {
  const totalBenchmarks = document.getElementById("summary-total-benchmarks");
  const totalSkills = document.getElementById("summary-total-skills");
  const improvements = document.getElementById("summary-improvements");
  const improvementRate = document.getElementById("summary-improvement-rate");

  if (totalBenchmarks)
    totalBenchmarks.textContent = summary.total_benchmarks ?? 0;
  if (totalSkills) totalSkills.textContent = summary.total_skills ?? 0;
  if (improvements) improvements.textContent = summary.improvements ?? 0;
  if (improvementRate)
    improvementRate.textContent = `${summary.improvement_rate ?? 0}%`;
}

function populateFilters(data) {
  const providerSelect = document.getElementById("filter-provider");
  const modelSelect = document.getElementById("filter-model");
  const skillSelect = document.getElementById("filter-skill");

  const providers = new Set();
  const models = new Set();
  const skills = new Set();

  (data.benchmarks || []).forEach((benchmark) => {
    if (benchmark.provider) providers.add(benchmark.provider);
    if (benchmark.model) models.add(benchmark.model);
    (benchmark.skills || []).forEach((skill) => {
      if (skill.skill_name) skills.add(skill.skill_name);
    });
  });

  if (providerSelect) {
    clearSelect(providerSelect, "All Providers");
    Array.from(providers)
      .sort()
      .forEach((provider) => {
        const opt = document.createElement("option");
        opt.value = provider;
        opt.textContent = provider.charAt(0).toUpperCase() + provider.slice(1);
        providerSelect.appendChild(opt);
      });
  }

  if (modelSelect) {
    clearSelect(modelSelect, "All Models");
    Array.from(models)
      .sort()
      .forEach((model) => {
        const opt = document.createElement("option");
        opt.value = model;
        opt.textContent = model;
        modelSelect.appendChild(opt);
      });
  }

  if (skillSelect) {
    clearSelect(skillSelect, "All Skills");
    Array.from(skills)
      .sort()
      .forEach((skill) => {
        const opt = document.createElement("option");
        opt.value = skill;
        opt.textContent = skill;
        skillSelect.appendChild(opt);
      });
  }
}

function renderTable(benchmarks) {
  flatSkills = [];
  const tbody = document.getElementById("skills-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  benchmarks.forEach((benchmark) => {
    (benchmark.skills || []).forEach((skill) => {
      const normalizedSkill = {
        ...skill,
        provider: skill.provider || benchmark.provider || "unknown",
        model: skill.model || benchmark.model || "unknown",
      };
      const index = flatSkills.length;
      flatSkills.push(normalizedSkill);

      const row = document.createElement("tr");
      row.dataset.provider = (normalizedSkill.provider || "").toLowerCase();
      row.dataset.model = (normalizedSkill.model || "").toLowerCase();
      row.dataset.skill = (normalizedSkill.skill_name || "").toLowerCase();
      row.dataset.improvement = (
        normalizedSkill.improvement || ""
      ).toLowerCase();

      const baselineRating = normalizedSkill.baseline_rating || "vague";
      const skillRating = normalizedSkill.skill_rating || "vague";
      const improvement = normalizedSkill.improvement || "neutral";

      const improvementLabel =
        improvement === "yes"
          ? "Improvement"
          : improvement === "no"
            ? "Regression"
            : "Neutral";

      row.innerHTML = `
        <td>${escapeHtml(normalizedSkill.skill_name || "unknown")}</td>
        <td>${escapeHtml(normalizedSkill.provider || "unknown")}</td>
        <td>${escapeHtml(normalizedSkill.model || "unknown")}</td>
        <td><span class="badge bg-${getRatingColor(baselineRating)}">${escapeHtml(baselineRating)}</span></td>
        <td><span class="badge bg-${getRatingColor(skillRating)}">${escapeHtml(skillRating)}</span></td>
        <td><span class="badge bg-${getImprovementColor(improvement)}">${improvementLabel}</span></td>
        <td><button class="btn btn-sm btn-primary" data-skill-index="${index}">View</button></td>
      `;

      const button = row.querySelector("button");
      if (button) {
        button.addEventListener("click", () => showDetails(index));
      }

      tbody.appendChild(row);
    });
  });
}

function filterTable() {
  const provider = (
    document.getElementById("filter-provider")?.value || ""
  ).toLowerCase();
  const model = (
    document.getElementById("filter-model")?.value || ""
  ).toLowerCase();
  const skill = (
    document.getElementById("filter-skill")?.value || ""
  ).toLowerCase();
  const improvement = (
    document.getElementById("filter-improvement")?.value || ""
  ).toLowerCase();

  const rows = document.querySelectorAll("#skills-table-body tr");
  rows.forEach((row) => {
    const matchProvider = !provider || row.dataset.provider === provider;
    const matchModel = !model || row.dataset.model === model;
    const matchSkill = !skill || row.dataset.skill === skill;
    const matchImprovement =
      !improvement || row.dataset.improvement === improvement;

    row.style.display =
      matchProvider && matchModel && matchSkill && matchImprovement
        ? ""
        : "none";
  });
}

function showDetails(index) {
  const skill = flatSkills[index];
  if (!skill) return;

  const modalTitle = document.getElementById("detailModalTitle");
  if (modalTitle) {
    modalTitle.textContent = `Skill Details: ${skill.skill_name || "Unknown Skill"}`;
  }

  const judgment = skill.judgment || {};
  const beforeRating =
    judgment.option_a_rating || skill.baseline_rating || "vague";
  const afterRating = judgment.option_b_rating || skill.skill_rating || "vague";
  const overallBetter = judgment.overall_better || "Equal";
  const score = judgment.score ?? 0;
  const reasoning =
    skill.reasoning || judgment.reasoning || "No reasoning provided";

  const beforeRatingEl = document.getElementById("modal-before-rating");
  const afterRatingEl = document.getElementById("modal-after-rating");
  const betterEl = document.getElementById("modal-better");
  const scoreEl = document.getElementById("modal-score");
  const reasoningEl = document.getElementById("modal-reasoning");
  const codeBeforeEl = document.getElementById("code-before");
  const codeAfterEl = document.getElementById("code-after");
  const responseBeforeEl = document.getElementById("response-before");
  const responseAfterEl = document.getElementById("response-after");

  if (beforeRatingEl) beforeRatingEl.textContent = beforeRating;
  if (afterRatingEl) afterRatingEl.textContent = afterRating;
  if (betterEl) betterEl.textContent = overallBetter;
  if (scoreEl) scoreEl.textContent = score;
  if (reasoningEl)
    reasoningEl.innerHTML = escapeHtml(reasoning).replace(/\n/g, "<br>");

  const beforeFull = skill.before_code || "// No code generated";
  const afterFull = skill.after_code || "// No code generated";
  const beforeCode = normalizeTestHeaders(extractCodeBlocks(beforeFull));
  const afterCode = normalizeTestHeaders(extractCodeBlocks(afterFull));

  if (codeBeforeEl) codeBeforeEl.textContent = beforeCode;
  if (codeAfterEl) codeAfterEl.textContent = afterCode;
  if (responseBeforeEl) responseBeforeEl.textContent = beforeFull;
  if (responseAfterEl) responseAfterEl.textContent = afterFull;

  const modalEl = document.getElementById("detailModal");
  if (modalEl) {
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
    if (window.Prism) {
      Prism.highlightAllUnder(modalEl);
    }

    const beforeContainer = document.getElementById("modal-before-code");
    const afterContainer = document.getElementById("modal-after-code");
    if (beforeContainer && afterContainer) {
      beforeContainer.onscroll = () => syncScroll(beforeContainer, afterContainer);
      afterContainer.onscroll = () => syncScroll(afterContainer, beforeContainer);
    }
  }
}

function toggleExpand(id, button) {
  const container = document.getElementById(id);
  if (!container) return;
  const expanded = container.classList.toggle("expanded");
  if (button) {
    button.textContent = expanded ? "Collapse" : "Expand";
  }
}

async function refreshDashboard() {
  await loadDashboard();
}

async function loadDashboard() {
  try {
    const data = await fetchData();
    allData = data;
    renderSummary(data.summary || {});
    populateFilters(data);
    renderTable(data.benchmarks || []);
  } catch (error) {
    console.error("Failed to load dashboard data", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
});
