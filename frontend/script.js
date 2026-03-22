/**
 * ASTraCore++ — frontend: calls /compare and shows similarity percentage.
 */

(function () {
  const code1 = document.getElementById("code1");
  const code2 = document.getElementById("code2");
  const btn = document.getElementById("btnCompare");
  const scoreEl = document.getElementById("score");
  const errEl = document.getElementById("error");

  function setError(msg) {
    if (msg) {
      errEl.textContent = msg;
      errEl.hidden = false;
    } else {
      errEl.textContent = "";
      errEl.hidden = true;
    }
  }

  async function compare() {
    setError("");
    btn.disabled = true;
    scoreEl.textContent = "…";
    scoreEl.classList.add("muted");

    try {
      const res = await fetch("/compare", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code1: code1.value,
          code2: code2.value,
        }),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.error || "Request failed");
      }

      if (typeof data.similarity_percent !== "number") {
        throw new Error("Invalid response");
      }

      scoreEl.classList.remove("muted");
      scoreEl.textContent = data.similarity_percent.toFixed(2) + "%";
    } catch (e) {
      scoreEl.textContent = "—";
      scoreEl.classList.add("muted");
      setError(e.message || "Network error");
    } finally {
      btn.disabled = false;
    }
  }

  btn.addEventListener("click", compare);
})();
