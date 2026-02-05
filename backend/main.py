from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import hashlib, cv2, numpy as np, os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --- Reference images (you must have these files in /data) ---
REAL_REF_PATH = os.path.join(DATA_DIR, "real_01.webp")     # real medicine image
FAKE_REF_PATH = os.path.join(DATA_DIR, "fake_0002.jpg")    # fake medicine image

# --- Simple helpers ---
def sha256(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()

def load_img_bytes(b):
    arr = np.frombuffer(b, np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)

def ssim_like(a, b):
    """Simplified structural similarity measure"""
    A = cv2.resize(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), (400, 400))
    B = cv2.resize(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), (400, 400))
    mse = np.mean((A.astype("float") - B.astype("float")) ** 2)
    if mse == 0:
        return 1.0
    psnr = 20 * np.log10(255.0 / np.sqrt(mse))
    return max(0.0, min(1.0, (psnr - 20) / 20))  # 20..40 → 0..1

def orb_score(a, b):
    """Feature-based image similarity"""
    A = cv2.resize(cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), (600, 400))
    B = cv2.resize(cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), (600, 400))
    orb = cv2.ORB_create(nfeatures=800)
    k1, d1 = orb.detectAndCompute(A, None)
    k2, d2 = orb.detectAndCompute(B, None)
    if d1 is None or d2 is None:
        return 0.0
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(d1, d2)
    if not matches:
        return 0.0
    md = np.median([m.distance for m in matches])
    return 1.0 - min(md / 100.0, 1.0)

@app.post("/check")
async def check(
    qr_payload: str = Form(""),
    medicine_id: str = Form(""),
    batch_no: str = Form(""),
    medicine_name: str = Form(""),
    manufacturer: str = Form(""),
    manufacture_date: str = Form(""),
    expiry_date: str = Form(""),
    file: UploadFile = File(...)
):
    # --- Load uploaded file ---
    up = await file.read()
    user_img = load_img_bytes(up)

    # --- Load reference images ---
    real_img = cv2.imread(REAL_REF_PATH)
    fake_img = cv2.imread(FAKE_REF_PATH)
    if real_img is None or fake_img is None:
        return {"error": "Reference images missing in /data folder."}

    # --- Compute similarity to both real and fake ---
    ssim_real = ssim_like(user_img, real_img)
    ssim_fake = ssim_like(user_img, fake_img)
    orb_real = orb_score(user_img, real_img)
    orb_fake = orb_score(user_img, fake_img)

    real_score = round(0.4 * ssim_real + 0.6 * orb_real, 3)
    fake_score = round(0.4 * ssim_fake + 0.6 * orb_fake, 3)

    # --- Decide authenticity ---
    if real_score > fake_score and real_score >= 0.7:
        label = "authentic"
    elif fake_score > real_score and fake_score >= 0.65:
        label = "likely_fake"
    else:
        label = "suspicious"

    # --- Save uploaded image for record ---
    fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{label}.jpg"
    with open(os.path.join(DATA_DIR, fname), "wb") as f:
        f.write(up)

    # --- Return results ---
    return {
        "label": label,
        "img_score_real": real_score,
        "img_score_fake": fake_score,
        "medicine_name": medicine_name,
        "manufacturer": manufacturer,
        "manufacture_date": manufacture_date,
        "expiry_date": expiry_date,
        "medicine_id": medicine_id,
        "batch_no": batch_no,
        "checked_at": datetime.utcnow().isoformat()
    }
