const API = "http://127.0.0.1:8000/api";

document.addEventListener("DOMContentLoaded", checkStatus);

async function checkStatus() {
  try {
    const res = await fetch(API + "/status");
    const s = await res.json();

    if (s.data) {
      document.getElementById("statusData").innerText = "🟢 Ready";
      document.getElementById("btnData").innerText = "Data Generated Successfully";
      document.getElementById("btnData").disabled = true;
    }
    if (s.model) {
      document.getElementById("statusModel").innerText = "🟢 Ready";
      document.getElementById("btnTrain").innerText = "Models Trained Successfully";
      document.getElementById("btnTrain").disabled = true;
    }
  } catch (e) {
    console.error("Backend offline?", e);
  }
}

async function runData() {
  document.getElementById("btnData").disabled = true;
  document.getElementById("loaderData").style.display = "block";
  await fetch(API + "/generate-data", { method: "POST" });

  // polling is lazy but works for demo)
  const interval = setInterval(async () => {
    const res = await fetch(API + "/status");
    const s = await res.json();
    if (s.data) {
      clearInterval(interval);
      document.getElementById("loaderData").style.display = "none";
      checkStatus();
    }
  }, 2000);
}

async function runTrain() {
  document.getElementById("btnTrain").disabled = true;
  document.getElementById("loaderTrain").style.display = "block";

  const res = await fetch(API + "/train", { method: "POST" });
  if (!res.ok) {
    alert("Please generate data first!");
    document.getElementById("loaderTrain").style.display = "none";
    document.getElementById("btnTrain").disabled = false;
    return;
  }

  const interval = setInterval(async () => {
    const res = await fetch(API + "/status");
    const s = await res.json();
    if (s.model) {
      clearInterval(interval);
      document.getElementById("loaderTrain").style.display = "none";
      checkStatus();
    }
  }, 2000);
}

async function runPredict() {
  const personaId = document.getElementById("personaSelect").value;
  const btn = document.getElementById("btnPredict");

  btn.disabled = true;
  btn.innerText = "Generating...";

  try {
    const res = await fetch(API + "/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: personaId }),
    });

    if (!res.ok) {
      alert("Ensure models are trained first!");
      throw new Error("Models not ready");
    }

    const data = await res.json();

    document.getElementById("results").style.display = "block";
    document.getElementById("waBubble").innerText = data.message;
  } catch (e) {
    console.error(e);
  } finally {
    btn.disabled = false;
    btn.innerText = "Generate Campaign";
  }
}
