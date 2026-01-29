const API = "http://127.0.0.1:8000/api";

document.addEventListener("DOMContentLoaded", () => {
  checkStatus(false);
});

async function checkStatus(updateLoaders = false) {
  try {
    const res = await fetch(API + "/status");
    const s = await res.json();

    if (s.data) {
      markComplete("statusData", "btnData", "loaderData", "✅ Data Ready");
      unlockStep("step2");
    } else if (!updateLoaders) {
      resetStep("statusData", "btnData", "loaderData", "Generate Data");
    }

    if (s.model) {
      markComplete(
        "statusModel",
        "btnTrain",
        "loaderTrain",
        "✅ Models Trained",
      );
      unlockStep("step3");
    } else if (!updateLoaders && s.data) {
      resetStep("statusModel", "btnTrain", "loaderTrain", "Train Models");
    }

    return s;
  } catch (e) {
    console.error("Server offline?", e);
  }
}


async function runData() {
  setLoading("btnData", "loaderData");

  await fetch(API + "/generate-data", { method: "POST" });

  pollUntil(async () => {
    const s = await checkStatus(true);
    return s.data === true;
  });
}

async function runTrain() {
  setLoading("btnTrain", "loaderTrain");

  await fetch(API + "/train", { method: "POST" });

  pollUntil(async () => {
    const s = await checkStatus(true);
    return s.model === true;
  });
}

async function runPredict() {
  const btn = document.getElementById("btnPredict");
  btn.innerText = "⏳ Generating...";
  btn.disabled = true;

  const pid = document.getElementById("personaSelect").value;

  try {
    const res = await fetch(API + "/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: pid, name: pid, description: "test" }),
    });

    const data = await res.json();
    renderResults(data);
  } catch (e) {
    alert("Error generating prediction");
  } finally {
    btn.innerText = "✨ Generate Campaign";
    btn.disabled = false;
  }
}

let currentMessage = "";

function renderResults(data) {
  document.getElementById("results").classList.remove("hidden");

  document.getElementById("optTime").innerText =
    data.optimal_hours[0] + ":00 IST";

  const prodList = data.products
    .map((p) => `• ${p.title} - ₹${p.price}`)
    .join("\n");
  const cleanMessage = `${data.headline}\n\n${prodList}`;

  document.getElementById("waBubble").innerText = cleanMessage;
  currentMessage = cleanMessage;
}

function copyToClipboard() {
  if (!currentMessage) return;
  navigator.clipboard.writeText(currentMessage).then(() => {
    const btn = document.getElementById("btnCopy");
    const originalText = btn.innerText;
    btn.innerText = "✅ Copied!";
    btn.style.background = "#10b981";

    setTimeout(() => {
      btn.innerText = originalText;
      btn.style.background = "#333";
    }, 2000);
  });
}

// Polls a condition every 1 second until true
async function pollUntil(checkFn) {
  const interval = setInterval(async () => {
    const isDone = await checkFn();
    if (isDone) {
      clearInterval(interval);
    }
  }, 1000);
}

function setLoading(btnId, loaderId) {
  document.getElementById(btnId).disabled = true;
  document.getElementById(loaderId).style.display = "block";
}

function markComplete(badgeId, btnId, loaderId, btnText) {
  // Update Badge
  const badge = document.getElementById(badgeId);
  if (badge) {
    badge.innerText = "🟢 Ready";
    badge.classList.add("ready");
  }

  // Hide Loader
  const loader = document.getElementById(loaderId);
  if (loader) loader.style.display = "none";

  // Disable Button
  const btn = document.getElementById(btnId);
  if (btn) {
    btn.innerText = btnText;
    btn.disabled = true;
    btn.classList.add("btn-done");
  }
}

function resetStep(badgeId, btnId, loaderId, btnText) {
  const badge = document.getElementById(badgeId);
  if (badge) {
    badge.innerText = "🔴 Missing";
    badge.classList.remove("ready");
  }

  const loader = document.getElementById(loaderId);
  if (loader) loader.style.display = "none";

  const btn = document.getElementById(btnId);
  if (btn) {
    btn.innerText = btnText;
    btn.disabled = false;
    btn.classList.remove("btn-done");
  }
}

function unlockStep(stepId) {
  const step = document.getElementById(stepId);
  if (step) step.classList.remove("locked");
}
