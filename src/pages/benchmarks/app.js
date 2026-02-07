let allData = null;
let flatSkills = [];
let currentSkill = null;
let currentSkillRuns = [];
let currentTestIndex = 0;

function logStatus(msg, isError = false) {
  const el = document.getElementById("modal-debug-status");
  if (el) {
    el.textContent = msg;
    el.className = isError ? "text-danger small fw-bold" : "text-muted small fw-normal";
  }
}

function toggleDebugInfo() {
  const el = document.getElementById("modal-debug-info");
  if (el) el.classList.toggle("d-none");
}

function getDataSrc() {
  const base = document.body.dataset.benchmarksSrc || "benchmarks.json";
  return `${base}?t=${Date.now()}`;
}

function syncStateToUrl() {
  const params = new URLSearchParams();

  // Filters
  const p = document.getElementById("filter-provider")?.value;
  const m = document.getElementById("filter-model")?.value;
  const s = document.getElementById("filter-skill")?.value;
  const i = document.getElementById("filter-improvement")?.value;

  if (p) params.set("p", p);
  if (m) params.set("m", m);
  if (s) params.set("s", s);
  if (i) params.set("i", i);

  // Modal state
  if (currentSkill) {
    params.set("v", currentSkill.skill_name);
    // Identify the specific run in the comparison list
    const runKey = `${currentSkill.provider}:${currentSkill.model}:${currentSkill.timestamp}`;
    params.set("r", runKey);

    const selector = document.getElementById("test-selector");
    if (selector && selector.value !== "0") {
      params.set("t", selector.value);
    }
  }

  const newUrl = window.location.pathname + (params.toString() ? "?" + params.toString() : "");
  window.history.replaceState({}, "", newUrl);
}

function loadStateFromUrl() {
  const params = new URLSearchParams(window.location.search);

  // Apply filters
  const selectors = { "filter-provider": "p", "filter-model": "m", "filter-skill": "s", "filter-improvement": "i" };
  for (const [id, param] of Object.entries(selectors)) {
    const el = document.getElementById(id);
    const val = params.get(param);
    if (el && val) {
      el.value = val;
    }
  }

  // Re-render table based on filters
  renderTable(allData.benchmarks || []);

  // Open modal if requested
  const viewSkill = params.get("v");
  if (viewSkill) {
    // Find skill in flatSkills
    const matchIdx = flatSkills.findIndex(s => s.skill_name === viewSkill);
    if (matchIdx !== -1) {
      showDetails(matchIdx);

      // If a specific run is requested in the modal
      const runKey = params.get("r");
      if (runKey) {
        const selector = document.getElementById("modal-model-selector");
        if (selector) {
          for (let i = 0; i < selector.options.length; i++) {
            const run = currentSkillRuns[i]; // Need to expose skillRuns
            const currentRunKey = `${run.provider}:${run.model}:${run.timestamp}`;
            if (currentRunKey === runKey) {
              selector.selectedIndex = i;
              renderModalContent(run);
              break;
            }
          }
        }
      }

      // If a specific test is requested
      const testIdx = params.get("t");
      if (testIdx) {
        const testSelector = document.getElementById("test-selector");
        if (testSelector) {
          testSelector.value = testIdx;
          currentTestIndex = parseInt(testIdx, 10);
          updateTestView();
        }
      }
    }
  }
}

function getRatingColor(rating) {
  const colors = { vague: "secondary", regular: "warning", good: "primary", outstanding: "success" };
  return colors[rating] || "secondary";
}

function getRatingStars(rating) {
  const stars = {
    vague: "⭐",
    regular: "⭐⭐",
    good: "⭐⭐⭐",
    outstanding: "⭐⭐⭐⭐"
  };
  return stars[rating] || "";
}

function getImprovementColor(improvement) {
  const colors = { yes: "success", no: "danger", neutral: "secondary" };
  return colors[improvement] || "secondary";
}

function escapeHtml(text) {
  if (!text) return "";
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function parseResponse(text) {
  if (!text) return { commentary: "No response.", files: [] };
  const files = [];
  const codeBlockRegex = /```(\w+)?[\s\r\n]*([\s\S]*?)```/g;
  let lastIndex = 0;
  let commentary = "";
  let match;
  let fileCount = 1;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    commentary += text.substring(lastIndex, match.index).trim() + "\n\n";
    let lang = (match[1] || "").trim().toLowerCase();
    const content = match[2];

    if (lang === 'py') lang = 'python';
    if (lang === 'js') lang = 'javascript';
    if (lang === 'ts') lang = 'typescript';

    const filenameMatch = content.match(/^(?:\/\/|#)\s*([a-zA-Z0-9_\-\.]+)/);
    let filename = filenameMatch ? filenameMatch[1] : `snippet_${fileCount}.${lang === 'python' ? 'py' : (lang === 'html' ? 'html' : (lang === 'css' ? 'css' : 'js'))}`;

    files.push({ name: filename, lang: lang || "javascript", content: content.trim() });
    fileCount++;
    lastIndex = codeBlockRegex.lastIndex;
  }
  commentary += text.substring(lastIndex).trim();
  return { commentary: commentary.trim(), files };
}

function renderFiles(paneId, files, codeViewId) {
  try {
    const listEl = document.getElementById(paneId + "-file-list");
    const codeViewEl = document.getElementById(codeViewId);

    if (!listEl || !codeViewEl) return;

    listEl.innerHTML = "";
    if (files.length === 0) {
      listEl.innerHTML = '<div class="list-group-item text-muted small">No code files found</div>';
      codeViewEl.textContent = "// No code extracted from response";
      codeViewEl.className = "language-none";
      return;
    }

    files.forEach((file, index) => {
      const btn = document.createElement("button");
      btn.className = "list-group-item list-group-item-action py-2 px-3 small border-0";
      btn.textContent = file.name;
      btn.onclick = () => {
        listEl.querySelectorAll("button").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");

        codeViewEl.textContent = file.content;
        codeViewEl.className = `language-${file.lang}`;

        if (window.Prism) {
          Prism.highlightElement(codeViewEl);
        }
      };
      listEl.appendChild(btn);
    });

    const firstBtn = listEl.querySelector("button");
    if (firstBtn) firstBtn.click();
  } catch (e) {
    logStatus(`renderFiles Error: ${e.message}`, true);
  }
}

function updateTestView() {
  try {
    if (!currentSkill || !currentSkill.tests || currentSkill.tests.length === 0) {
      logStatus("No test data available", true);
      return;
    }

    const test = currentSkill.tests[currentTestIndex];
    if (!test) return;

    logStatus(`Viewing: ${test.name}`);

    document.getElementById("test-input").textContent = test.input || "N/A";
    document.getElementById("test-expected").textContent = typeof test.expected === 'string'
      ? test.expected
      : JSON.stringify(test.expected, null, 2) || "N/A";

    const baselineData = parseResponse(test.baseline_response);
    const skillData = parseResponse(test.skill_response);

    document.getElementById("baseline-commentary").textContent = baselineData.commentary || "No commentary.";
    renderFiles("baseline", baselineData.files, "baseline-code-view");

    document.getElementById("skill-commentary").textContent = skillData.commentary || "No commentary.";
    renderFiles("skill", skillData.files, "skill-code-view");
  } catch (e) {
    logStatus(`updateTestView Error: ${e.message}`, true);
  }
}

function populateTestSelector(tests) {
  try {
    const selector = document.getElementById("test-selector");
    if (!selector) return;

    selector.innerHTML = "";
    tests.forEach((test, index) => {
      const opt = document.createElement("option");
      opt.value = index;
      opt.textContent = test.name || `Test ${index + 1}`;
      selector.appendChild(opt);
    });

    selector.onchange = (e) => {
      currentTestIndex = parseInt(e.target.value, 10);
      updateTestView();
      syncStateToUrl();
    };

    if (tests.length > 0) {
      currentTestIndex = 0;
      selector.value = 0;
      updateTestView();
    }
  } catch (e) {
    logStatus(`populateSelector Error: ${e.message}`, true);
  }
}

async function fetchData() {
  try {
    const src = getDataSrc();
    const response = await fetch(src, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  } catch (e) {
    alert(`Failed to load benchmark data: ${e.message}`);
    throw e;
  }
}

function getLogoPath(provider, model) {
  const m = (model || "").toLowerCase();
  const p = (provider || "").toLowerCase();

  // Model-specific overrides
  if (m.includes("gpt") || m.includes("openai")) return "logos/openai.png";
  if (m.includes("claude") || m.includes("anthropic")) return "logos/claude.png";
  if (m.includes("gemini") || m.includes("google")) return "logos/gemini.svg";

  // Provider-based defaults
  if (p === "ollama") return "logos/ollama.png";
  if (p === "codex") return "logos/openai.png";
  if (p === "anthropic") return "logos/claude.png";
  if (p === "google") return "logos/gemini.svg";
  if (p === "copilot") return "logos/claude.png"; // Default for our copilot haiku

  // Specific model fallback
  if (m.includes("qwen")) return "logos/ollama.png";
  if (m.includes("kimi")) return "logos/kimi.svg";

  return null;
}

function renderSummary(summary) {
  const tbody = document.getElementById("leaderboard-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  const leaderboard = summary.leaderboard || [];
  leaderboard.forEach((entry) => {
    const row = document.createElement("tr");
    const logo = getLogoPath(entry.provider, entry.model);
    const logoHtml = logo ? `<img src="${logo}" width="20" height="20" class="me-2" style="object-fit: contain;">` : "";

    const rate = entry.improvement_rate || 0;
    const statusClass = rate >= 70 ? "success" : (rate >= 40 ? "warning" : "danger");
    const statusText = rate >= 70 ? "ELITE" : (rate >= 40 ? "CAPABLE" : "RELIABLE?");

    row.innerHTML = `
      <td class="ps-4">
        <div class="d-flex align-items-center">
          ${logoHtml}
          <div>
            <div class="fw-bold text-dark">${escapeHtml(entry.model)}</div>
            <div class="text-muted small text-uppercase" style="font-size: 10px">${escapeHtml(entry.provider)}</div>
          </div>
        </div>
      </td>
      <td class="text-center fw-bold text-muted">${entry.total_tested}</td>
      <td class="text-center fw-bold text-success">${entry.improvements}</td>
      <td class="text-center">
        <div class="d-flex align-items-center justify-content-center">
          <div class="progress w-50 me-2" style="height: 6px;">
            <div class="progress-bar bg-${statusClass}" style="width: ${rate}%"></div>
          </div>
          <span class="fw-bold text-${statusClass}">${rate}%</span>
        </div>
      </td>
      <td class="pe-4 text-end">
        <span class="badge bg-${statusClass} opacity-75">${statusText}</span>
      </td>
    `;
    tbody.appendChild(row);
  });
}

function populateFilters(data) {
  const providerSelect = document.getElementById("filter-provider");
  const modelSelect = document.getElementById("filter-model");
  const skillSelect = document.getElementById("filter-skill");

  const providers = new Set();
  const models = new Set();
  const skills = new Set();

  (data.benchmarks || []).forEach((b) => {
    if (b.provider) providers.add(b.provider);
    if (b.model) models.add(b.model);
    (b.skills || []).forEach((s) => { if (s.skill_name) skills.add(s.skill_name); });
  });

  const fill = (sel, items, def) => {
    if (!sel) return;
    sel.innerHTML = `<option value="">${def}</option>`;
    Array.from(items).sort().forEach(i => {
      const o = document.createElement("option"); o.value = i; o.textContent = i; sel.appendChild(o);
    });
  };

  fill(providerSelect, providers, "ALL PROVIDERS");
  fill(modelSelect, models, "ALL MODELS");
  fill(skillSelect, skills, "ALL SKILLS");
}

function formatDate(iso) {
  if (!iso) return "N/A";
  try {
    const d = new Date(iso);
    return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch (e) { return iso; }
}

function renderTable(benchmarks) {
  flatSkills = [];
  const tbody = document.getElementById("skills-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  const pFilter = (document.getElementById("filter-provider")?.value || "").toLowerCase();
  const mFilter = (document.getElementById("filter-model")?.value || "").toLowerCase();
  const sFilter = (document.getElementById("filter-skill")?.value || "").toLowerCase();
  const iFilter = (document.getElementById("filter-improvement")?.value || "").toLowerCase();

  // 1. Flatten all skills
  const allRuns = [];
  benchmarks.forEach((b) => {
    (b.skills || []).forEach((s) => {
      allRuns.push({
        ...s,
        provider: s.provider || b.provider || "unknown",
        model: s.model || b.model || "unknown",
        timestamp: s.timestamp || b.timestamp || ""
      });
    });
  });

  // 2. Sort all by date desc
  allRuns.sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0));

  // 3. Filter and Deduplicate
  let visibleRuns = [];
  if (sFilter) {
    // If a specific skill is selected, show ALL historical runs for it (filtered by other fields too)
    visibleRuns = allRuns.filter(r => {
      const match = r.skill_name.toLowerCase() === sFilter &&
        (!pFilter || r.provider.toLowerCase() === pFilter) &&
        (!mFilter || r.model.toLowerCase() === mFilter) &&
        (!iFilter || r.improvement.toLowerCase() === iFilter);
      return match;
    });
  } else {
    // Deduplicate: only latest per Skill+Provider+Model
    const seen = new Set();
    allRuns.forEach(r => {
      const key = `${r.skill_name}|${r.provider}|${r.model}`;
      if (!seen.has(key)) {
        // Also apply filters
        const match = (!pFilter || r.provider.toLowerCase() === pFilter) &&
          (!mFilter || r.model.toLowerCase() === mFilter) &&
          (!iFilter || r.improvement.toLowerCase() === iFilter);
        if (match) {
          visibleRuns.push(r);
          seen.add(key);
        }
      }
    });
  }

  // 4. Render
  visibleRuns.forEach((norm) => {
    const idx = flatSkills.length;
    flatSkills.push(norm);

    const bRating = norm.baseline_rating || "vague";
    const sRating = norm.skill_rating || "vague";
    const imp = norm.improvement || "neutral";

    const row = document.createElement("tr");
    row.innerHTML = `
      <td class="ps-4">
        <div class="fw-bold text-dark">${escapeHtml(norm.skill_name)}</div>
        <div class="text-muted" style="font-size: 10px">v${escapeHtml(norm.skill_version || "1.0.0")}</div>
      </td>
      <td class="text-muted small">${escapeHtml(formatDate(norm.timestamp))}</td>
      <td class="text-muted small">${escapeHtml(norm.provider)}</td>
      <td class="text-muted small">${escapeHtml(norm.model)}</td>
      <td>
        <div class="mb-1" style="font-size: 12px">${getRatingStars(bRating)}</div>
        <span class="badge bg-${getRatingColor(bRating)} opacity-75">${bRating}</span>
      </td>
      <td>
        <div class="mb-1" style="font-size: 12px">${getRatingStars(sRating)}</div>
        <span class="badge bg-${getRatingColor(sRating)}">${sRating}</span>
      </td>
      <td><span class="badge bg-${getImprovementColor(imp)} rounded-pill px-3">${imp}</span></td>
      <td class="pe-4 text-end"><button class="btn btn-sm btn-primary shadow-sm" onclick="showDetails(${idx})">View</button></td>
    `;
    tbody.appendChild(row);
  });
}

function filterTable() {
  renderTable(allData.benchmarks || []);
  syncStateToUrl();
}

function showDetails(index) {
  try {
    const originSkill = flatSkills[index];
    if (!originSkill) return;

    // Find all runs for this same skill from ALL benchmarks (ignoring current filters)
    const allRuns = [];
    allData.benchmarks.forEach(b => {
      (b.skills || []).forEach(s => {
        if (s.skill_name === originSkill.skill_name) {
          allRuns.push({
            ...s,
            provider: s.provider || b.provider || "unknown",
            model: s.model || b.model || "unknown",
            timestamp: s.timestamp || b.timestamp || ""
          });
        }
      });
    });
    currentSkillRuns = allRuns;

    // Sort runs by date (desc)
    currentSkillRuns.sort((a, b) => new Date(b.timestamp || 0) - new Date(a.timestamp || 0));

    const selector = document.getElementById("modal-model-selector");
    selector.innerHTML = "";

    currentSkillRuns.forEach((run, i) => {
      const opt = document.createElement("option");
      opt.value = i;
      opt.textContent = `${run.provider.toUpperCase()}: ${run.model} (${formatDate(run.timestamp)})`;
      if (run === originSkill) opt.selected = true;
      selector.appendChild(opt);
    });

    selector.onchange = (e) => {
      const selectedRun = currentSkillRuns[parseInt(e.target.value, 10)];
      renderModalContent(selectedRun);
      syncStateToUrl();
    };

    renderModalContent(originSkill);

    const modalEl = document.getElementById("detailModal");
    const modal = new bootstrap.Modal(modalEl);

    // Clear URL params when modal is hidden
    modalEl.addEventListener('hidden.bs.modal', () => {
      currentSkill = null;
      syncStateToUrl();
    }, { once: true });

    modal.show();
    syncStateToUrl();
  } catch (e) {
    console.error("showDetails Error:", e);
    alert(`Failed to show details: ${e.message}`);
  }
}

function renderModalContent(skillData) {
  try {
    currentSkill = skillData;
    logStatus("Preparing view...");

    const debugJson = document.getElementById("debug-json");
    if (debugJson) debugJson.textContent = JSON.stringify(currentSkill, null, 2);

    document.getElementById("detailModalTitle").textContent = `${currentSkill.skill_name} (v${currentSkill.skill_version || "1.0.0"})`;

    const isError = currentSkill.judge_error === true;
    const j = currentSkill.judgment || {};
    const bRating = j.option_a_rating || currentSkill.baseline_rating || "vague";
    const aRating = j.option_b_rating || currentSkill.skill_rating || "vague";
    const better = j.overall_better || "Equal";

    document.getElementById("modal-score").textContent = isError ? "N/A" : (j.score ?? 0);
    const verdict = document.getElementById("modal-verdict");
    if (verdict) {
      if (isError) {
        verdict.textContent = 'JUDGE ERROR';
        verdict.className = `badge bg-warning text-dark ms-2`;
      } else {
        verdict.textContent = better === 'B' ? 'BETTER' : (better === 'A' ? 'WORSE' : 'EQUAL');
        verdict.className = `badge bg-${better === 'B' ? 'success' : (better === 'A' ? 'danger' : 'secondary')} ms-2`;
      }
    }
    document.getElementById("modal-before-rating").innerHTML = `<div class="mb-1" style="font-size: 14px">${getRatingStars(bRating)}</div>${bRating.toUpperCase()}`;
    document.getElementById("modal-after-rating").innerHTML = `<div class="mb-1" style="font-size: 14px">${getRatingStars(aRating)}</div>${aRating.toUpperCase()}`;

    const reasoningEl = document.getElementById("modal-reasoning");
    if (isError) {
      reasoningEl.innerHTML = '<span class="text-danger fw-bold">The LLM judge failed to provide a valid assessment for this skill run.</span>';
    } else {
      reasoningEl.innerHTML = escapeHtml(currentSkill.reasoning || j.reasoning || "No reasoning").replace(/\n/g, "<br>");
    }

    let tests = currentSkill.tests || [];
    if (tests.length === 0) {
      tests = [{ name: "Standard Test", input: "Data unavailable", expected: "Data unavailable", baseline_response: currentSkill.before_code || "", skill_response: currentSkill.after_code || "" }];
    }
    currentSkill.tests = tests;

    // Refresh the test selector and view
    populateTestSelector(tests);
  } catch (e) {
    console.error("renderModalContent Error:", e);
  }
}

async function loadDashboard() {
  try {
    const data = await fetchData();
    allData = data;
    renderSummary(data.summary || {});
    populateFilters(data);
    renderTable(data.benchmarks || []);
    loadStateFromUrl();
  } catch (error) {
    console.error("Dashboard Load Error", error);
    logStatus("Failed to load dashboard data", true);
  }
}

// Entry point: handle immediate execution or event-based
if (document.readyState === "complete" || document.readyState === "interactive") {
  loadDashboard();
} else {
  document.addEventListener("DOMContentLoaded", loadDashboard);
}

function refreshDashboard() { location.reload(); }
