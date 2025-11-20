# Environment Variables Auto-Loading Guide

## How to Automatically Load `.env` Files in Python Scripts

When you click the "Run File" button in Cursor (or any IDE), Python scripts **don't automatically pick up environment variables** from `settings.json` or your shell configuration. The solution is to use **`python-dotenv`** to load them from a `.env` file.

---

## The Pattern (Copy This!)

Add these 2 lines at the **very top** of any Python file that needs environment variables:

```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

# Now you can use os.environ.get() and it will work!
import os
my_var = os.environ.get("MY_VARIABLE")
```

---

## What About `settings.json`?

### VS Code/Cursor `settings.json`
The `.vscode/settings.json` file is for **IDE-specific configuration**:

```json
{
  "terminal.integrated.env.osx": {
    "DATABRICKS_HOST": "https://your-workspace.cloud.databricks.com",
    "MLFLOW_TRACKING_URI": "databricks"
  }
}
```

**What it does:**
- ✅ Sets environment variables for the **integrated terminal** in VS Code/Cursor
- ✅ Useful for terminal commands like `python my_script.py`
- ❌ Does **NOT** work with "Run File" button or debugger
- ❌ Not portable (other developers need to recreate it)

**Why use `.env` instead:**
- ✅ Works with "Run File" button
- ✅ Works everywhere (terminal, debugger, Jupyter, CI/CD)
- ✅ Portable - just copy `.env.example` to `.env`
- ✅ Standard practice in Python projects

**Bottom line:** Use `settings.json` for IDE preferences. Use `.env` + `load_dotenv()` for environment variables.

---

## How It Works

1. **`.env` file** - Contains your environment variables (one per line)
   ```bash
   DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
   DATABRICKS_TOKEN=dapi1234567890abcdef
   MLFLOW_TRACKING_URI=databricks
   MLFLOW_EXPERIMENT_ID=1234567890
   ```

2. **`load_dotenv()`** - Reads the `.env` file and loads all variables into `os.environ`
   - Automatically finds `.env` in the current directory or parent directories
   - Does NOT overwrite existing environment variables (safe to use)
   - Silent if `.env` doesn't exist (won't crash)

3. **`os.environ.get()`** - Now works as expected!
   ```python
   tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
   # Returns: "databricks"
   ```

---

## Why This Matters

### ❌ Without `load_dotenv()`:
- Clicking "Run File" button → Environment variables are `None`
- You have to manually export variables in terminal first
- Inconsistent behavior between terminal and IDE

### ✅ With `load_dotenv()`:
- Clicking "Run File" button → Automatically loads `.env`
- Works the same in terminal, IDE, Jupyter, anywhere
- No manual setup needed
- Credentials stay secure in `.env` (which is in `.gitignore`)

---

## Real Example from This Project

### File: `agent.py`
```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import mlflow
import os
from databricks.sdk import WorkspaceClient

# These now work automatically!
host = os.environ.get('MLFLOW_TRACKING_URI')
exp_id = os.environ.get('MLFLOW_EXPERIMENT_ID')
tok = os.environ.get('DATABRICKS_TOKEN')

w = WorkspaceClient()
client = w.serving_endpoints.get_open_ai_client()
```

### File: `scorers/register_scorers.py`
```python
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

import mlflow
import os

# Now these work when clicking "Run File"
experiment_id = os.environ.get("MLFLOW_EXPERIMENT_ID")
mlflow_tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")
```

---

## Setup Instructions

### 1. Install `python-dotenv`
```bash
pip install python-dotenv
```

Or add to `requirements.txt`:
```
python-dotenv>=1.0.0
```

### 2. Create `.env` File
In your project root, create a `.env` file:

```bash
# .env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi1234567890abcdef
MLFLOW_TRACKING_URI=databricks
MLFLOW_EXPERIMENT_ID=1234567890
OPENAI_API_KEY=sk-proj-...
```

### 3. Add `.env` to `.gitignore`
**IMPORTANT:** Never commit `.env` to git!

```bash
# .gitignore
.env
```

### 4. Use in Any Python File
```python
from dotenv import load_dotenv
load_dotenv()

import os

# All your environment variables are now available!
my_secret = os.environ.get("MY_SECRET_KEY")
```

---

## Advanced Usage

### Load from Specific File
```python
from dotenv import load_dotenv

# Load from a different file
load_dotenv(".env.production")
```

### Override Existing Variables
```python
# By default, load_dotenv() does NOT override existing env vars
load_dotenv()  # Safe, won't overwrite

# To override existing vars:
load_dotenv(override=True)
```

### Check if Variable Exists
```python
import os

api_key = os.environ.get("API_KEY")
if api_key is None:
    raise ValueError("API_KEY not set in .env file!")
```

### Use with Default Values
```python
import os

# Provide a default if not set
model = os.environ.get("MODEL_NAME", "gpt-4")  # Defaults to "gpt-4"
```

---

## Common Patterns

### Pattern 1: Configuration Module
Create a `config.py`:

```python
from dotenv import load_dotenv
import os

load_dotenv()

# Export as module-level constants
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN")
MLFLOW_TRACKING_URI = os.environ.get("MLFLOW_TRACKING_URI")
EXPERIMENT_ID = os.environ.get("MLFLOW_EXPERIMENT_ID")
```

Then in other files:
```python
from config import DATABRICKS_HOST, EXPERIMENT_ID
```

### Pattern 2: Validation on Load
```python
from dotenv import load_dotenv
import os

load_dotenv()

# Validate required variables
REQUIRED_VARS = ["DATABRICKS_HOST", "DATABRICKS_TOKEN"]
missing = [var for var in REQUIRED_VARS if not os.environ.get(var)]

if missing:
    raise ValueError(f"Missing required env vars: {missing}")
```

---

## Troubleshooting

### Issue: Variables still `None` after `load_dotenv()`

**Check:**
1. ✅ Is `.env` in the project root directory?
2. ✅ Is the variable name spelled correctly?
3. ✅ No spaces around `=` in `.env` file
4. ✅ No quotes needed (unless the value has spaces)

**Example `.env` format:**
```bash
# ✅ Correct
MY_VAR=my_value
MY_VAR_WITH_SPACES=hello world

# ❌ Wrong
MY_VAR = my_value     # No spaces around =
MY_VAR="my_value"     # No quotes needed
```

### Issue: `.env` not loading in subdirectory

```python
from dotenv import load_dotenv, find_dotenv

# Automatically searches parent directories
load_dotenv(find_dotenv())
```

---

## Security Best Practices

### ✅ DO:
- Keep `.env` in `.gitignore`
- Use different `.env` files for dev/staging/prod
- Provide `.env.example` template for team members
- Rotate secrets regularly

### ❌ DON'T:
- Commit `.env` to git
- Share `.env` via Slack/email
- Hardcode secrets in Python files
- Use production credentials in development

---

## Example `.env.example` Template

Create this as a template for your team:

```bash
# .env.example
# Copy this to .env and fill in your actual values

# Databricks Configuration
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi_your_token_here

# MLflow Configuration
MLFLOW_TRACKING_URI=databricks
MLFLOW_EXPERIMENT_ID=your_experiment_id

# OpenAI (if needed)
OPENAI_API_KEY=sk-proj-your-key-here
```

Team members can then:
```bash
cp .env.example .env
# Edit .env with their actual credentials
```

---

## Summary: Copy This Snippet

**Add to the top of ANY Python file that needs environment variables:**

```python
from dotenv import load_dotenv
load_dotenv()  # Auto-loads .env file

import os

# Now all your environment variables work!
my_var = os.environ.get("MY_VARIABLE")
```

**That's it!** Works with:
- ✅ "Run File" button in Cursor/VS Code
- ✅ Terminal: `python my_script.py`
- ✅ Jupyter notebooks
- ✅ Databricks (still works, no harm)
- ✅ CI/CD pipelines

---

**Remember:** `load_dotenv()` at the top of every file = environment variables just work! 🎉

