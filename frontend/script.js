/**
 * ASTraCore++ — frontend: /analyze (Code Analysis) and /compare (Plagiarism).
 */

(function () {
  // ——— Code Analysis ———
  const analysisCode = document.getElementById("analysisCode");
  const btnAnalyze = document.getElementById("btnAnalyze");
  const analysisOutput = document.getElementById("analysisOutput");
  const analysisError = document.getElementById("analysisError");
  const analysisWarnings = document.getElementById("analysisWarnings");
  const analysisWarningsEmpty = document.getElementById("analysisWarningsEmpty");
  const analysisTokensBody = document.getElementById("analysisTokensBody");
  const analysisTokensEmpty = document.getElementById("analysisTokensEmpty");

  // ——— Plagiarism ———
  const compareCodeA = document.getElementById("compareCodeA");
  const compareCodeB = document.getElementById("compareCodeB");
  const btnCompare = document.getElementById("btnCompare");
  const compareOutput = document.getElementById("compareOutput");
  const compareError = document.getElementById("compareError");
  const compareScore = document.getElementById("compareScore");
  const compareProgressFill = document.getElementById("compareProgressFill");
  const compareExplanation = document.getElementById("compareExplanation");
  const compareCodeAWarnings = document.getElementById("compareCodeAWarnings");
  const compareCodeAWarningsEmpty = document.getElementById("compareCodeAWarningsEmpty");

  function setHidden(el, hidden) {
    el.hidden = !!hidden;
  }

  function showAnalysisError(msg) {
    if (msg) {
      analysisError.textContent = msg;
      setHidden(analysisError, false);
    } else {
      analysisError.textContent = "";
      setHidden(analysisError, true);
    }
  }

  function showCompareError(msg) {
    if (msg) {
      compareError.textContent = msg;
      setHidden(compareError, false);
    } else {
      compareError.textContent = "";
      setHidden(compareError, true);
    }
  }

  /**
   * Map similarity % to a short explanation (thresholds per spec).
   */
  function getSimilarityExplanation(pct) {
    if (pct > 80) {
      return {
        text: "Highly similar (possible plagiarism)",
        tier: "high",
      };
    }
    if (pct >= 50) {
      return {
        text: "Moderately similar",
        tier: "mid",
      };
    }
    return {
      text: "Low similarity",
      tier: "low",
    };
  }

  function renderWarningsList(ul, emptyEl, warnings) {
    ul.innerHTML = "";
    if (!warnings || warnings.length === 0) {
      setHidden(emptyEl, false);
      return;
    }
    setHidden(emptyEl, true);
    warnings.forEach(function (w) {
      const li = document.createElement("li");
      li.textContent = w;
      ul.appendChild(li);
    });
  }

  function renderTokensTable(tbody, emptyEl, tokens) {
    tbody.innerHTML = "";
    if (!tokens || tokens.length === 0) {
      setHidden(emptyEl, false);
      return;
    }
    setHidden(emptyEl, true);
    tokens.forEach(function (pair, idx) {
      const tr = document.createElement("tr");
      const td0 = document.createElement("td");
      const td1 = document.createElement("td");
      const td2 = document.createElement("td");
      td0.textContent = String(idx + 1);
      td1.textContent = pair[0];
      td2.textContent = pair[1];
      tr.appendChild(td0);
      tr.appendChild(td1);
      tr.appendChild(td2);
      tbody.appendChild(tr);
    });
  }

  function setProgressBar(fillEl, pct) {
    const clamped = Math.max(0, Math.min(100, pct));
    fillEl.style.width = clamped + "%";
    fillEl.classList.remove("mid", "low");
    if (clamped < 50) {
      fillEl.classList.add("low");
    } else if (clamped <= 80) {
      fillEl.classList.add("mid");
    }
  }

  /**
   * POST /analyze — show warnings and token table.
   */
  async function analyze() {
    showAnalysisError("");
    btnAnalyze.disabled = true;
    setHidden(analysisOutput, false);

    try {
      const res = await fetch("/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: analysisCode.value }),
      });

      const data = await res.json().catch(function () {
        return {};
      });

      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }

      if (!Array.isArray(data.tokens) || !Array.isArray(data.warnings)) {
        throw new Error("Invalid response");
      }

      renderWarningsList(analysisWarnings, analysisWarningsEmpty, data.warnings);
      renderTokensTable(analysisTokensBody, analysisTokensEmpty, data.tokens);
    } catch (e) {
      showAnalysisError(e.message || "Network error");
      renderWarningsList(analysisWarnings, analysisWarningsEmpty, []);
      renderTokensTable(analysisTokensBody, analysisTokensEmpty, []);
    } finally {
      btnAnalyze.disabled = false;
    }
  }

  /**
   * POST /compare — similarity + explanation + progress bar.
   * Optionally POST /analyze on Code A for warnings.
   */
  async function compare() {
    showCompareError("");
    btnCompare.disabled = true;
    compareScore.textContent = "…";
    compareScore.classList.add("muted");
    compareExplanation.textContent = "";
    compareExplanation.className = "explanation";
    setProgressBar(compareProgressFill, 0);
    setHidden(compareOutput, false);

    try {
      const res = await fetch("/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code1: compareCodeA.value,
          code2: compareCodeB.value,
        }),
      });

      const data = await res.json().catch(function () {
        return {};
      });

      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }

      if (typeof data.similarity_percent !== "number") {
        throw new Error("Invalid response");
      }

      const pct = data.similarity_percent;
      const fixed = pct.toFixed(2);

      compareScore.classList.remove("muted");
      compareScore.textContent = "Similarity: " + fixed + "%";

      setProgressBar(compareProgressFill, pct);

      const expl = getSimilarityExplanation(pct);
      compareExplanation.textContent = expl.text;
      compareExplanation.className = "explanation " + expl.tier;

      // Optional: warnings for Code A via existing /analyze API
      try {
        const ar = await fetch("/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: compareCodeA.value }),
        });
        const ad = await ar.json().catch(function () {
          return {};
        });
        if (ar.ok && Array.isArray(ad.warnings)) {
          renderWarningsList(compareCodeAWarnings, compareCodeAWarningsEmpty, ad.warnings);
        } else {
          renderWarningsList(compareCodeAWarnings, compareCodeAWarningsEmpty, []);
        }
      } catch (_e) {
        renderWarningsList(compareCodeAWarnings, compareCodeAWarningsEmpty, []);
      }
    } catch (e) {
      compareScore.textContent = "—";
      compareScore.classList.add("muted");
      compareExplanation.textContent = "";
      setProgressBar(compareProgressFill, 0);
      showCompareError(e.message || "Network error");
      renderWarningsList(compareCodeAWarnings, compareCodeAWarningsEmpty, []);
    } finally {
      btnCompare.disabled = false;
    }
  }

  btnAnalyze.addEventListener("click", analyze);
  btnCompare.addEventListener("click", compare);
})();
