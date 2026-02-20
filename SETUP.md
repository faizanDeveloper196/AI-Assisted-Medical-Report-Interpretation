# Project Setup Guide

Follow these steps to set up the **AI-Assisted Medical Report Interpretation** project on a new machine.

## Prerequisites

1.  **Python** (3.10 or higher)
2.  **Ollama** (for AI interpretation)
3.  **Poppler** (for PDF processing)

---

## 1. Environment Setup

### Clone the Repository

```bash
git clone <repository-url>
cd AI-Assisted-Medical-Report-Interpretation
```

### Create a Virtual Environment (Recommended)

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

---

## 2. Install Python Dependencies

Run the following command to install all required Python libraries:

```bash
pip install -r requirements/requirements.txt
```

---

## 3. Install System Dependencies

### Poppler (Required for PDF to Image conversion)

**Windows:**

1.  Download the latest binary from [Github](https://github.com/oschwartz10612/poppler-windows/releases/).
2.  Extract the zip file.
3.  Add the `bin` folder to your System PATH environment variable.
    - _Example:_ `C:\Program Files\poppler-24.02.0\Library\bin`

**Mac:**

```bash
brew install poppler
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-get install poppler-utils
```

---

## 4. Install & Run AI Model (Ollama)

1.  Download and install [Ollama](https://ollama.com/).
2.  Open a terminal and pull the required model:
    ```bash
    ollama pull llama3:8b
    ```
3.  Start the Ollama server (keep this running):
    ```bash
    ollama serve
    ```

---

## 5. Run the Project

1.  Apply database migrations:
    ```bash
    python manage.py migrate
    ```
2.  Start the development server:
    ```bash
    python manage.py runserver
    ```
3.  Open your browser at `http://127.0.0.1:8000/`.
