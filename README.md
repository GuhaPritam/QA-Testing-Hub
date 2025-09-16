### 1. Clone the Repository
````markdown
git clone git@github.com:GuhaPritam/QA-Testing-Hub.git
cd QA-Testing-Hub
````

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

**Windows (PowerShell):**

```bash
.\venv\Scripts\Activate
```

If you get a `script running is disabled` error, run:

```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Linux**

```bash
source venv/bin/activate
```

### 4. Install Dependencies

Install all dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
pip list / pip freeze
```

