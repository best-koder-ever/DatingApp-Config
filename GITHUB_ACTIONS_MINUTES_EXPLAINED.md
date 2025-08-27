# ⏱️ GitHub Actions Minutes - How They're Counted

## 🎯 **When Do Minutes Get Consumed?**

### **✅ Minutes ARE Counted When:**
1. **Workflow triggers execute** (push, pull request, scheduled, manual)
2. **Jobs are running** (from start to completion)
3. **Setup time** (downloading actions, setting up environment)
4. **Cleanup time** (uploading artifacts, cleanup tasks)

### **❌ Minutes ARE NOT Counted When:**
- Code sits in your repository (static storage)
- Workflows are disabled or skipped
- No triggers are activated
- Repository just exists on GitHub

---

## 🚀 **What Triggers Your Pipeline?**

### **Your Current Pipeline Triggers:**
```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
```

### **When Minutes Get Used:**
| Action | Minutes Consumed | Example |
|--------|------------------|---------|
| **Push to main** | ✅ ~40-50 minutes | `git push origin main` |
| **Create Pull Request** | ✅ ~40-50 minutes | Opening PR to main |
| **Push to feature branch** | ❌ 0 minutes | `git push origin feature/login` |
| **Just browsing code** | ❌ 0 minutes | Looking at files on GitHub |
| **Repository existing** | ❌ 0 minutes | Repo just sitting there |

---

## 📊 **Detailed Minute Breakdown**

### **Your Pipeline Steps & Time:**
```yaml
# ⏱️ Time breakdown for each run:

1. Setup (Ubuntu runner)           ~2-3 minutes
2. Checkout code                   ~1 minute  
3. Setup Flutter                   ~3-5 minutes
4. Flutter tests                   ~5-8 minutes
5. Setup .NET (5 services)         ~3-5 minutes
6. .NET tests (parallel)           ~10-15 minutes
7. Docker builds                   ~10-15 minutes
8. E2E tests                       ~5-10 minutes
9. Cleanup & artifacts             ~2-3 minutes

TOTAL: ~40-50 minutes per run
```

### **Real Examples:**
```bash
# These actions consume minutes:
git push origin main                    # ✅ Triggers full pipeline (~45 min)
git push origin main --force           # ✅ Triggers full pipeline (~45 min)
# Create PR from GitHub web UI          # ✅ Triggers full pipeline (~45 min)

# These actions DON'T consume minutes:
git push origin feature/new-login      # ❌ No trigger (not main branch)
git commit -m "Local changes"          # ❌ No trigger (not pushed)
# Browse files on github.com           # ❌ No trigger (just viewing)
# Edit README on GitHub web            # ❌ No trigger (if not main branch)
```

---

## 🎛️ **Controlling When Minutes Are Used**

### **1. Branch-Based Control:**
```yaml
# Current: Only main branch triggers
on:
  push:
    branches: [ main ]

# Alternative: Multiple branches
on:
  push:
    branches: [ main, develop, staging ]  # More triggers = more minutes

# Alternative: All branches (expensive!)
on:
  push:  # Any branch = lots of minutes!
```

### **2. Path-Based Control:**
```yaml
# Only run when specific files change
on:
  push:
    branches: [ main ]
    paths:
      - '**/*.cs'        # Only .NET changes
      - '**/*.dart'      # Only Flutter changes
      - 'docker/**'     # Only Docker changes
      # Ignores: README, docs, etc.
```

### **3. Skip Commits:**
```bash
# Skip pipeline entirely with commit message:
git commit -m "Update docs [skip ci]"
git push origin main  # ❌ NO minutes consumed!
```

---

## 📈 **Your Usage Scenarios**

### **Scenario 1: Conservative Development**
```bash
# Daily workflow:
git checkout -b feature/new-feature    # ❌ 0 minutes
# ... develop and test locally
git push origin feature/new-feature    # ❌ 0 minutes (not main)
# Create PR, review, merge to main      # ✅ 45 minutes (1 run)

Daily cost: 45 minutes
Monthly: 45 × 20 working days = 900 minutes ✅ FREE
```

### **Scenario 2: Moderate Development**
```bash
# Multiple pushes to main per day:
git push origin main  # Morning   ✅ 45 minutes
git push origin main  # Afternoon ✅ 45 minutes

Daily cost: 90 minutes  
Monthly: 90 × 22 days = 1,980 minutes ✅ FREE (just under limit!)
```

### **Scenario 3: Heavy Development**
```bash
# Many main branch pushes:
git push origin main  # ✅ 45 min (morning)
git push origin main  # ✅ 45 min (afternoon) 
git push origin main  # ✅ 45 min (evening)
# + Pull requests from team members

Daily cost: 135+ minutes
Monthly: 135 × 25 days = 3,375 minutes ❌ 1,375 over = $11/month
```

---

## 🛡️ **Optimization Strategies**

### **1. Develop on Feature Branches:**
```bash
# Best practice workflow:
git checkout -b feature/user-profile        # ❌ 0 minutes
git push origin feature/user-profile        # ❌ 0 minutes
# ... multiple pushes to feature branch     # ❌ 0 minutes each
# When ready:
git checkout main && git merge feature/...  # ✅ Only 1 run (45 min)
```

### **2. Batch Changes:**
```bash
# Instead of:
git commit -m "Fix bug 1" && git push      # ✅ 45 minutes
git commit -m "Fix bug 2" && git push      # ✅ 45 minutes  
git commit -m "Fix bug 3" && git push      # ✅ 45 minutes
# Total: 135 minutes

# Do this:
git commit -m "Fix bug 1"                  # Local only
git commit -m "Fix bug 2"                  # Local only
git commit -m "Fix bug 3"                  # Local only
git push                                   # ✅ Only 45 minutes!
```

### **3. Smart Triggers:**
```yaml
# Add to your workflow to skip docs/readme changes:
on:
  push:
    branches: [ main ]
    paths-ignore:
      - '**/*.md'
      - 'docs/**'
      - '**/*.txt'
```

---

## 💡 **Key Takeaways**

1. **Minutes only count when workflows RUN** (not when code exists)
2. **Your trigger: Push to main branch** = ~45 minutes per push
3. **Feature branches = FREE** (no pipeline runs)
4. **Pull requests to main = Pipeline runs** (~45 minutes)
5. **Local commits = FREE** until you push

### **Your Realistic Usage:**
- **Conservative**: 15-20 pushes to main/month = 900-1,200 minutes ✅ FREE
- **Moderate**: 30-40 pushes to main/month = 1,800-2,400 minutes ≈ $3/month  
- **Heavy**: 60+ pushes to main/month = 3,600+ minutes ≈ $13/month

**🎯 Use feature branches for development, only push to main when ready!**
