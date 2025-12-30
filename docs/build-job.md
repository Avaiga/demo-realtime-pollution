# Build Job Documentation

**Owner:** Zoha  
**Purpose:** Prepare application artifacts for containerization

---

## Overview

The Build Job is responsible for:
- Managing application configuration
- Verifying dependencies
- Preparing build artifacts
- Ensuring code quality before containerization

---

## Files Created

### 1. `src/config.py`
Centralized configuration management for the application.

**Usage:**
```python
from src.config import current_config

# Access configuration
print(current_config.HOST)
print(current_config.PORT)
```

### 2. `scripts/build.ps1`
Automated build script for Windows PowerShell.

**Usage:**
```powershell
.\scripts\build.ps1
```

---

## Testing the Build

**Step 1: Test config.py**
```python
python
>>> from src.config import current_config
>>> current_config.display_config()
>>> exit()
```

**Step 2: Run build script**
```powershell
.\scripts\build.ps1
```

---

## Deliverables Checklist

- [x] `src/config.py` created
- [x] `scripts/build.ps1` created
- [x] `docs/build-job.md` created
- [ ] Build script tested successfully
- [ ] Configuration tested successfully
- [ ] Changes committed and pushed

---
