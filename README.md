# Medicine Authenticity Scanner

**Hackathon Project | Healthcare Technology**

Counterfeit medicines pose a serious risk to public health. This project provides a quick and reliable way to verify the authenticity of medicines at the point of purchase using QR code verification and image-based similarity analysis.

---

## 🚀 Problem Statement
Consumers cannot easily distinguish between genuine and fake medicines because counterfeit packaging often looks identical to real products. There is a need for a **mobile-friendly, fast, and reliable system** to verify medicine authenticity.

---

## 🎯 Objectives
- Verify medicine authenticity using **QR code data**
- Compare uploaded medicine package images using **image similarity techniques**
- Classify medicines as:
  - ✅ Authentic  
  - ⚠️ Suspicious  
  - ❌ Likely Fake
- Provide a **web-based interface** for users

---

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python)
- **Frontend:** HTML, CSS, JavaScript
- **Image Processing:** ORB / SSIM-like similarity
- **Security:** SHA-256 hash generation
- **Others:** REST APIs, CORS

---

## ⚙️ How It Works
1. User scans a **QR code** from the medicine package
2. User uploads or captures an image of the package
3. Data is sent to the **FastAPI backend**
4. Backend verifies QR data and compares images
5. Result is displayed as **Authentic / Suspicious / Likely Fake**

---

## 📁 Project Structure
Medicine-Authenticity-Scanner/
│── backend/
│── web/
│── README.md

---

## 📌 Project Status
Developed as part of **Innovation Ignite Symposium 2025 – Mini Hackathon**.
