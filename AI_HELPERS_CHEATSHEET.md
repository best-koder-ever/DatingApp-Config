# AI Helpers - Quick Cheatsheet (60 seconds)

**Read this FIRST in every conversation!**

## 🚨 Core Philosophy
**"Make the Invisible Visible"** - AI can verify state WITHOUT asking user

## ✅ ALWAYS Use These

### 1. Before Writing ANY Test
```bash
python3 scripts/ai-verify-state.py
# Shows: User Mappings: 5, Profiles: 254, Swipes: 12, Matches: 2, Messages: 2
# Takes 1 second (vs asking user = 5 minutes)
```

### 2. In EVERY Flutter Test
```dart
import 'helpers/test_assertions.dart';
import 'helpers/database_queries.dart';

setUpAll(() async {
  await TestAssertions.assertFixturesLoaded(); // ← ALWAYS include!
});
```

### 3. When Debugging
```dart
// Instead of asking user "what's in database?":
await TestDatabaseQueries.printCurrentState();
```

### 4. Get Fixture Users
```dart
// Instead of guessing IDs:
final bob = await TestDatabaseQueries.getFixtureUser('bob');
// Available: alice, bob, charlie, diana, erik
```

### 5. Reset Environment
```bash
# Instead of 6 manual steps:
make test-clean
```

## 📊 Known Facts (Never Ask User)

- **Fixture Users**: alice (1), bob (2), charlie (3), diana (4), erik (5)
- **Known Matches**: bob↔charlie, diana→erik
- **Database Ports**: SwipeServiceDb:3310, UserServiceDb:3308, MessagingDb:3312

## 🎯 When to Use What

| Need | Use This | NOT This |
|------|----------|----------|
| Check database state | `python3 scripts/ai-verify-state.py` | Ask user to run SQL |
| Verify fixtures loaded | `python3 scripts/ai-verify-state.py --assert-minimal` | Write test and run it |
| Get user info | `getFixtureUser('bob')` | Guess ID or search API |
| Reset environment | `make test-clean` | 6 manual commands |
| Debug test failure | `printCurrentState()` | Ask user to check |

## 💡 Impact

**Before helpers**: AI asks 15-20 questions, 10+ minutes per task  
**After helpers**: AI asks 3-5 questions, <1 minute per task  
**Speedup**: ~10x faster development

## 📚 Full Documentation

- **[.ai-context.json](.ai-context.json)** - Machine-readable (parse this!)
- **[AI_HELPER_STRATEGIES.md](AI_HELPER_STRATEGIES.md)** - Complete guide (500+ lines)
- **[AI_HELPERS_README.md](AI_HELPERS_README.md)** - Quick reference

---

**🚀 Remember**: Always check state BEFORE asking user!
