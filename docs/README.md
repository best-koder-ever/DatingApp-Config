# DatingApp Documentation

**Living documentation** - Updated as features ship, not frozen specs.

---

## 📚 Documentation Structure

```
docs/
├── features/           # What's built (user stories + implementation status)
├── architecture/       # How it works (system design + decisions)
├── api/                # API reference (endpoints + contracts)
└── runbooks/           # Operations (deployment + troubleshooting)
```

---

## 🎯 Quick Navigation

### For Product/Business
- **[Feature Catalog](features/README.md)** - What features exist? What's the status?
- **[CHANGELOG.md](../CHANGELOG.md)** - What shipped when?
- **[Dashboard](../specs/001-mvp-foundation/DASHBOARD.md)** - Current progress metrics

### For Developers
- **[Architecture Overview](architecture/OVERVIEW.md)** - System design
- **[API Reference](api/README.md)** - Endpoint documentation  
- **[Runbooks](runbooks/)** - How to deploy, debug, operate

### For Planning
- **[Original Spec](../specs/001-mvp-foundation/spec.md)** - Initial user stories (frozen)
- **[Tasks](../specs/001-mvp-foundation/tasks.md)** - Implementation checklist
- **[GitHub Project](https://github.com/users/best-koder-ever/projects/2)** - Live task board

---

## 🔄 Keeping Docs Fresh

### When You Ship a Feature:
1. Update `docs/features/<user-story>.md` with "✅ Implemented" status
2. Add entry to `CHANGELOG.md` under `[Unreleased]`
3. Run `./scripts/generate_dashboard.sh` to refresh metrics
4. Update `docs/api/` if endpoints changed

### When You Make Architecture Decisions:
1. Create `docs/architecture/decisions/00X-title.md` (ADR)
2. Update `docs/architecture/OVERVIEW.md` if structure changed

### Monthly:
1. Review feature docs for accuracy
2. Archive old `[Unreleased]` to versioned

 release in CHANGELOG
3. Prune stale information

---

## 📖 Documentation Philosophy

**Specs (specs/) = Planning** - What we PLANNED to build (frozen blueprint)  
**Docs (docs/) = Reality** - What we ACTUALLY built (living truth)

✅ **DO**: Update docs/ when shipping features
❌ **DON'T**: Change specs/ after work starts (historical record)

---

*Last updated: 2026-01-24*
