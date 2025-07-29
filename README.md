# Intelligent Document Verification System using LLMs

An AI-powered intelligent document processing tool that extracts text from structured identity documents like Aadhaar cards, PAN Cards and marksheets using Vision-Language Models (LLaMA), compares it with manually filled form data, and provides real-time mismatch detection and feedback.

---

## 📌 Features

- Upload identity document (e.g., Aadhaar card image)
- Extracts key fields like Name, DOB, Gender, Aadhaar Number using LLMs
- Real-time comparison with form field inputs
- Flags mismatches for user correction
- Supports manual override and confirmation before submission
- Simple UI for form input and image upload

---

## 🧰 Technologies Used

| Layer        | Tools & Libraries                        |
|--------------|------------------------------------------|
| Backend      | Python, Flask                            |
| AI Model     | LLaMA 3.2 Vision Instruct 11B            |
| Frontend     | HTML, CSS, JavaScript                    |
| Parsing      | `transformers`, `torch`, `Pillow`, etc.  |

---

## 📦 Installation

> ⚠️ **Requirements**:
> - Python 3.8+
> - pip
> - NVIDIA GPU (for faster inference) + CUDA (Optional but recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/vaibhavs211/Extraction-and-Verification-of-Semi-Categorized-Data.git
cd Extraction-and-Verification-of-Semi-Categorized-Data
````

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> 🔧 Also ensure PyTorch with CUDA is installed if you plan to run on GPU:
> [PyTorch Installation Guide](https://pytorch.org/get-started/locally/)

---

## 🚀 Running the Project

### 1. Start the Backend Server

```bash
python app.py
```

This will start the Flask backend at: `http://127.0.0.1:5000/`

### 2. Open Frontend in Browser

If it's a Flask-rendered HTML:

```bash
Go to: http://127.0.0.1:5000/
```

If frontend is in a separate folder (like React or HTML static files), open `index.html` from `/frontend/` directory in your browser.

---

## 🧠 How It Works

1. **User uploads** documents and fills a form.
2. The backend **passes the image to a vision-language model** which extracts the matching fields with the document type uploaded 
3. These fields are compared with form data.
4. Real-time **feedback and mismatch alerts** are shown to the user.
5. User can correct the mismatches or override.
6. Final verified data is submitted.

---



## ✅ Sample Use Cases

* Automated Aadhaar verification in eKYC forms
* Educational forms for student data validation
* Government benefit registration systems
* Pre-filled application verification tools

---


## 🤝 Contributing

PRs are welcome! Feel free to raise issues or contribute improvements.

---

## 📄 License

MIT License – Free to use and modify.

---

## 👤 Developed by

**Vaibhav Singhavi**
B.Tech CSE, RCOEM Nagpur


