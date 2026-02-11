# Legal Compliance Task - PRE-LAUNCH BLOCKER

**Task ID**: T-LEGAL-001  
**Priority**: 🔴 P0 - CRITICAL BLOCKER  
**Status**: ❌ Not Started  
**Blocking**: App Store submission, Public launch, GDPR compliance  
**Effort**: 8-12 hours (draft) + €1000-1500 (legal review)  
**Created**: 2026-02-06

---

## 📋 Task Description

Create and publish mandatory legal documentation required for dating app launch, including Privacy Policy, Terms of Service, and Cookie Policy. These are legally required by GDPR, Apple App Store, and Google Play Store.

**Without these**: App cannot be submitted to stores and faces GDPR fines up to €20M.

---

## ✅ Acceptance Criteria

### Privacy Policy
- [ ] GDPR Article 13 compliant (all 14 required elements)
- [ ] Covers dating-specific data: photos, location, messages, matching
- [ ] Published at accessible URL (e.g., `https://dejting.se/privacy`)
- [ ] Includes "Last Updated" date
- [ ] Provides contact email for data requests
- [ ] Explains user rights (access, deletion, portability)
- [ ] Mobile-responsive design (readable on phone)

### Terms of Service
- [ ] 18+ age requirement clearly stated
- [ ] Prohibited conduct defined (harassment, fake profiles, spam)
- [ ] Account termination conditions
- [ ] Content ownership and licensing
- [ ] Limitation of liability
- [ ] Dispute resolution process
- [ ] Published at accessible URL (e.g., `https://dejting.se/terms`)

### Cookie Policy
- [ ] All cookies documented (analytics, session, preferences)
- [ ] Third-party cookies listed (Google Analytics, etc.)
- [ ] User opt-out instructions
- [ ] Published at URL or embedded in Privacy Policy

### Implementation
- [ ] Links clickable in Flutter Welcome Screen
- [ ] Links in Account Settings screen
- [ ] "I agree to Terms and Privacy Policy" checkbox in registration
- [ ] All links tested on iOS, Android, Web
- [ ] URLs use HTTPS (required by App Store)

### Legal Review
- [ ] Initial drafts generated using GDPR templates
- [ ] Customized for dating app specifics
- [ ] Reviewed by tech lawyer (budget €1000-1500)
- [ ] Swedish translation (if targeting Sweden primarily)
- [ ] Final approval documented

---

## 🔧 Implementation Details

### Step 1: Generate Initial Drafts (2-3 hours)
Use GDPR template generators:
- **Termly**: https://termly.io/products/privacy-policy-generator/
- **Iubenda**: https://www.iubenda.com/ (recommended for dating apps)
- **PrivacyPolicies**: https://www.privacypolicies.com/

**Input needed**:
- Company name: DejTing AB (or similar)
- Contact email: privacy@dejting.se
- Website: https://dejting.se
- App name: DejTing
- Data collected: Name, email, birthday, gender, location, photos, messages, swipes, matches
- Data usage: Matching algorithm, chat, profile display, analytics
- Third parties: Google Analytics, Keycloak, Photo storage (S3/similar), SMS provider (Twilio)
- Retention period: Active accounts + 30 days after deletion request

### Step 2: Customize for Dating App (3-4 hours)
Add specific sections:
- **Photo Privacy**: Blur feature, visibility controls, moderation
- **Location Data**: Precision (city-level), matching purposes only
- **Messages**: E2E encryption status, retention policy
- **Matching Algorithm**: How scores calculated, what data used
- **Safety Features**: Blocking, reporting, photo moderation
- **Age Verification**: How 18+ requirement enforced
- **Data Deletion**: Right to be forgotten implementation (US4 feature)

### Step 3: Host Static Pages (2 hours)
Options:
1. **Simple HTML on YARP** (easiest):
   - Create `dejting-yarp/wwwroot/legal/privacy.html`
   - Create `dejting-yarp/wwwroot/legal/terms.html`
   - Configure YARP to serve static files
   
2. **GitHub Pages** (free CDN):
   - Repository: `dejting-legal-docs`
   - Deploy to: `https://legal.dejting.se`
   
3. **WordPress/Hugo** (if need CMS):
   - Simple CMS for non-technical updates
   - Version control built-in

### Step 4: Flutter Implementation (2 hours)
Update Welcome Screen:
```dart
// Make terms clickable
RichText(
  text: TextSpan(
    children: [
      TextSpan(text: 'By tapping Log In or Continue, you agree to our '),
      TextSpan(
        text: 'Terms',
        style: TextStyle(decoration: TextDecoration.underline),
        recognizer: TapGestureRecognizer()
          ..onTap = () => launchUrl(Uri.parse('https://dejting.se/terms')),
      ),
      // ... Privacy Policy, Cookie Policy links
    ],
  ),
)
```

Add registration checkbox:
```dart
CheckboxListTile(
  value: agreedToTerms,
  title: Text('I agree to Terms of Service and Privacy Policy'),
  onChanged: (value) => setState(() => agreedToTerms = value),
)
// Disable "Create Account" button if not checked
```

### Step 5: Legal Review (vendor task)
- **Find tech lawyer**: Search for "GDPR compliance lawyer" or "app privacy lawyer"
- **Budget**: €1000-1500 for review + revisions
- **Timeline**: 1-2 weeks (include in launch timeline)
- **Deliverable**: Signed approval letter

---

## 📊 Dependencies

**Blocks**:
- App Store submission (Apple, Google)
- Public beta launch
- Production deployment
- Payment processing setup
- Marketing campaigns

**Depends on**:
- Company entity formation (for legal signatories)
- Domain registration (dejting.se or similar)
- Company email setup (privacy@dejting.se)

---

## 🎯 Timeline

| Phase | Duration | Responsible |
|-------|----------|------------|
| Generate drafts | 2-3 hours | Developer |
| Customize for dating app | 3-4 hours | Developer + Product |
| Host static pages | 2 hours | Developer |
| Flutter implementation | 2 hours | Developer |
| Legal review (vendor) | 1-2 weeks | External lawyer |
| Translation (if needed) | 3-5 days | Translator |
| Final approval | 1 day | Legal + Product |

**Total estimate**: 10-15 hours developer time + 1-2 weeks vendor time

---

## 💰 Budget

- **GDPR template generator**: €0-50/month (Termly/Iubenda)
- **Legal review**: €1000-1500 (one-time)
- **Swedish translation**: €200-400 (if needed)
- **Hosting**: €0 (use existing infrastructure)

**Total**: €1200-1950

---

## 🔗 References

- **Full guide**: `/home/m/development/DatingApp/LEGAL_REQUIREMENTS.md`
- **GDPR official text**: https://gdpr.eu/
- **Apple review guidelines**: https://developer.apple.com/app-store/review/guidelines/#privacy
- **Google Play policy**: https://play.google.com/about/privacy-security-deception/user-data/
- **Example - Tinder Privacy**: https://policies.tinder.com/privacy
- **Example - Bumble Privacy**: https://bumble.com/en-us/privacy

---

## ⚠️ Risks if Skipped

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| App Store rejection | 100% | Critical | Complete before submission |
| GDPR fine | Medium | €20M max | Complete before EU users |
| User lawsuit | Low | High | Legal review required |
| Cannot use OAuth | 100% | Critical | Google/Apple require policy URLs |
| Reputational damage | High | Medium | Professional policies build trust |

---

## 📝 Notes

- Dating apps handle **extra sensitive data** (intimate photos, location, romantic preferences)
- GDPR has **stricter requirements** for "special categories of personal data"
- Some EU countries require explicit consent for profiling/automated decisions (matching algorithm)
- Right to deletion (GDPR Article 17) already implemented in US4 - document in policy
- Consider **data protection impact assessment (DPIA)** before launch (GDPR Article 35)

---

**Status**: This task MUST be completed before any public launch or app store submission.

**Owner**: Assign to legal/compliance lead or senior developer  
**Reviewer**: Tech lawyer (external)  
**Approver**: CEO/Founder

Last updated: 2026-02-06
