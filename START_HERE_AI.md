# START HERE - AI Assistant Guide

**📍 You are here**: DatingApp project with AI helper system

## 🚨 CRITICAL - Read in Order

### 1️⃣ First 60 Seconds (REQUIRED)
```bash
# Read this cheatsheet FIRST:
cat AI_HELPERS_CHEATSHEET.md

# Parse machine-readable context:
cat .ai-context.json
```

### 2️⃣ Before ANY Work
```bash
# Check database state (1 second):
python3 scripts/ai-verify-state.py
```

### 3️⃣ In Every Flutter Test
```dart
import 'helpers/test_assertions.dart';

setUpAll(() async {
  await TestAssertions.assertFixturesLoaded(); // ← ALWAYS!
});
```

---

## 🎯 The Rule

**NEVER ask user for database state** - Use helpers instead!

### ❌ Old Way (Slow)
```
AI: "Can you check how many profiles are in the database?"
User: *runs SQL query*
User: "254 profiles"
AI: *continues work*
⏱️ 5 minutes wasted
```

### ✅ New Way (Fast)
```bash
python3 scripts/ai-verify-state.py
# Output: Profiles: 254
⏱️ 1 second
```

---

## 📚 Full Documentation Hierarchy

```
START_HERE_AI.md           ← You are here (1 min)
├── AI_HELPERS_CHEATSHEET.md  ← Quick reference (60 sec)
├── .ai-context.json          ← Machine-readable context
├── AI_HELPERS_README.md      ← Quick reference guide (5 min)
└── AI_HELPER_STRATEGIES.md   ← Complete guide (30 min)
```

---

## 🚀 Quick Commands

| What | Command | Time |
|------|---------|------|
| Check state | `python3 scripts/ai-verify-state.py` | 1 sec |
| Verify fixtures | `python3 scripts/ai-verify-state.py --assert-minimal` | 1 sec |
| Reset environment | `make test-clean` | 30 sec |
| Health check | `make health-check` | 5 sec |

---

## 💡 Known Facts (Never Ask!)

- **Fixture Users**: alice, bob, charlie, diana, erik
- **Known Matches**: bob↔charlie, diana→erik
- **Database Ports**: SwipeServiceDb:3310, UserServiceDb:3308, MessagingDb:3312

---

**Remember**: Use helpers FIRST, ask user LAST! 🎯
