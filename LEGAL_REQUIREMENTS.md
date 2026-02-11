# ⚠️ LEGAL REQUIREMENTS - PRE-LAUNCH BLOCKERS

**Status**: ❌ NOT STARTED - BLOCKS APP STORE SUBMISSION  
**Priority**: 🔴 CRITICAL - Cannot launch without these  
**Created**: 2026-02-06

---

## 🚨 MANDATORY Before Launch

### 1. Privacy Policy (GDPR Compliant)
**Required by**: EU GDPR, Apple App Store, Google Play Store  
**Deadline**: Before ANY app store submission  
**Impact**: App rejection if missing

**What it must cover**:
- What personal data we collect (name, email, photos, location, messages, etc.)
- Why we collect it (matching algorithm, chat functionality)
- How long we store it
- Who we share it with (third parties, analytics)
- User rights (access, deletion, portability - GDPR Article 15-20)
- How users can exercise their rights
- Data retention policy
- Cookie usage
- How we protect data (encryption, security measures)

**Special for dating apps**:
- Explicitly mention photo storage and sharing
- Location data usage and precision
- Message privacy and encryption
- Match data and algorithms
- Photo moderation and AI processing
- Age verification compliance

**URL needed**: `https://dejting.se/privacy` or similar

---

### 2. Terms of Service / Terms & Conditions
**Required by**: Apple App Store, Google Play Store, Legal protection  
**Deadline**: Before ANY app store submission

**What it must cover**:
- User eligibility (18+ age requirement)
- Prohibited conduct (harassment, fake profiles, spam)
- Content ownership (photos, messages)
- Account termination conditions
- Limitation of liability
- Dispute resolution
- Intellectual property rights
- Payment terms (if premium features)
- Refund policy (if applicable)
- Governing law and jurisdiction

**URL needed**: `https://dejting.se/terms` or similar

---

### 3. Cookie Policy
**Required by**: EU ePrivacy Directive (Cookie Law)  
**Can be**: Separate page OR section in Privacy Policy

**What it must cover**:
- What cookies we use (analytics, session, preferences)
- Purpose of each cookie
- How users can manage/disable cookies
- Third-party cookies (Google Analytics, etc.)

**URL needed**: `https://dejting.se/cookies` or embedded in privacy policy

---

## 📋 Implementation Tasks

### Backend Tasks
- [ ] **Create static pages hosting** (Options: Simple HTML on server, CMS, GitHub Pages)
- [ ] **Set up URLs**: `/privacy`, `/terms`, `/cookies`
- [ ] **Ensure HTTPS** (required for App Store)
- [ ] **Add to YARP gateway routing** if needed

### Flutter Tasks
- [ ] **Make links clickable in Welcome Screen** (`url_launcher` package)
- [ ] **Add to Account Settings** (Privacy Policy, Terms links)
- [ ] **Add to registration flow** (checkbox: "I agree to Terms and Privacy Policy")
- [ ] **Test links open correctly** on iOS, Android, Web

### Legal Tasks
- [ ] **Generate initial drafts** (use GDPR template generators)
- [ ] **Customize for dating app specifics** (photos, location, messages, matching)
- [ ] **Legal review** (highly recommended before launch - €500-2000 one-time cost)
- [ ] **Translate to Swedish** if targeting Swedish users primarily
- [ ] **Add "Last Updated" date** and version control
- [ ] **Set up update notification system** (notify users if policies change)

---

## 🔗 Resources

### Free GDPR Generators
- **Termly**: https://termly.io/products/privacy-policy-generator/
- **PrivacyPolicies**: https://www.privacypolicies.com/
- **GDPR.eu Template**: https://gdpr.eu/privacy-notice/
- **Iubenda**: https://www.iubenda.com/ (freemium, good for dating apps)

### Dating App Specific Considerations
- **Match Group (Tinder/Hinge) Privacy Policy**: Study as reference
- **Bumble Privacy Policy**: Good example of photo/location handling
- **Age verification requirements**: Some jurisdictions require 18+ verification
- **Right to be forgotten**: Must implement profile deletion (already in US4)

### Legal Review
- **Tech lawyer specializing in apps**: €500-2000 for review
- **GDPR compliance check**: Worth investment before launch
- **Swedish law considerations**: Personuppgiftslagen (PUL) + GDPR

---

## ⚠️ Risks of Launching Without These

1. **App Store Rejection**: 100% rejection rate from Apple/Google
2. **GDPR Fines**: Up to €20 million or 4% of annual revenue
3. **User Lawsuits**: Liability for data breaches/misuse
4. **Reputational Damage**: Users distrust apps without policies
5. **Cannot Process Payments**: Payment processors require T&C
6. **Cannot Use Analytics**: Google Analytics requires privacy policy
7. **Cannot Use OAuth**: Google/Apple require privacy links

---

## ✅ Definition of Done

- [ ] Privacy Policy published at accessible URL
- [ ] Terms of Service published at accessible URL
- [ ] Cookie Policy published (or embedded in Privacy)
- [ ] All policies GDPR compliant
- [ ] Links clickable in Flutter app (Welcome Screen, Settings)
- [ ] Registration flow includes "I agree" checkbox
- [ ] Policies reviewed by legal professional (recommended)
- [ ] "Last Updated" dates present
- [ ] Email contact for data requests listed
- [ ] Right to deletion implemented (US4 Account Deletion feature)

---

## 🎯 Next Steps

1. **TODAY**: Use Termly/Iubenda to generate initial drafts (2-3 hours)
2. **THIS WEEK**: Customize for dating app specifics (photos, location, messages)
3. **BEFORE BETA**: Get legal review (budget €1000-1500)
4. **BEFORE LAUNCH**: Final approval and publication

---

**⚠️ DO NOT SUBMIT TO APP STORES WITHOUT COMPLETING THIS!**

Last updated: 2026-02-06  
Owner: Legal/Compliance (assign before launch)
