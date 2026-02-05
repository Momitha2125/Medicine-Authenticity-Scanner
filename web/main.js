// main.js
const vid = document.getElementById('vid');
const qrEl = document.getElementById('qr');
const file = document.getElementById('file');
const prev = document.getElementById('prev');
const out = document.getElementById('out');

let lastQR = "";
let imgBlob = null;

// --- Start camera and scan QR ---
document.getElementById('start').onclick = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: { ideal: "environment" } }
    });
    vid.srcObject = stream;

    const reader = new ZXingBrowser.BrowserMultiFormatReader();
    reader.decodeFromVideoDevice(null, vid, (res) => {
      if (res) {
        lastQR = res.getText();
        qrEl.textContent = lastQR;
      }
    });
  } catch (err) {
    alert("Unable to open camera. Try using HTTPS or desktop browser.");
  }
};

// --- When file (photo) is selected ---
file.onchange = () => {
  const f = file.files[0];
  if (!f) return;
  imgBlob = f;
  prev.src = URL.createObjectURL(f);
  prev.style.display = 'block';
};

// --- When “Check” button is clicked ---
document.getElementById('send').onclick = async () => {
  if (!imgBlob) return alert("Please upload or take a photo first.");

  const form = new FormData();
  form.append("qr_payload", lastQR || "");
  form.append("medicine_id", "MED123");
  form.append("batch_no", "BATCH7");
  form.append("file", imgBlob, "pack.jpg");

  // --- Try backend connection (localhost first, fallback to 127.0.0.1) ---
  let json = null;
  try {
    // Try localhost
    const res = await fetch("http://localhost:8000/check", {
      method: "POST",
      body: form
    });
    json = await res.json();
  } catch (err1) {
    console.warn("localhost failed, trying 127.0.0.1...");
    try {
      const res = await fetch("http://127.0.0.1:8000/check", {
        method: "POST",
        body: form
      });
      json = await res.json();
    } catch (err2) {
      alert("❌ Cannot connect to backend! Make sure FastAPI is running on port 8000.");
      return;
    }
  }

  // --- Display result ---
  console.log(json);
  out.textContent = JSON.stringify(json, null, 2);
};
