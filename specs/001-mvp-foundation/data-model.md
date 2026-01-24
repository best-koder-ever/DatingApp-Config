# Data Model Outline: DatingApp MVP Foundation

## Overview
This document summarizes the core entities and relationships required to support the MVP loop (onboarding → matching → messaging → safety).

## Entities

### MemberProfile
- `Id` (string, Keycloak user id)
- `DisplayName`
- `Age`
- `GenderIdentity`
- `Location` (geocoordinates + city)
- `Bio`
- `Interests` (collection of tags)
- `Preference` (relationship goals, distance range, age range)
- `OnboardingStatus` (Incomplete, Ready, Suspended)
- `CreatedAt` / `UpdatedAt`

### PhotoAsset
- `Id` (GUID)
- `OwnerId` (FK → MemberProfile)
- `StorageKey`
- `BlurKey`
- `PrivacyLevel` (Public, MatchOnly, Private, VIP)
- `ModerationScore`
- `ModerationStatus` (Pending, Approved, Rejected)
- `OrderIndex`
- `UploadedAt`

### Match
- `Id` (GUID)
- `MemberAId`
- `MemberBId`
- `CompatibilityScore`
- `Status` (Active, Blocked, Archived)
- `CreatedAt`
- `LastInteractionAt`

### SwipeEvent
- `Id` (GUID)
- `SwiperId`
- `TargetId`
- `Direction` (Like, Pass)
- `ScoreSnapshot`
- `CreatedAt`

### Message
- `Id` (GUID)
- `MatchId`
- `SenderId`
- `Body`
- `BodyType` (Text, PhotoReference)
- `DeliveryStatus` (Pending, Delivered, Read)
- `CreatedAt`
- `ReadAt`
- `ModerationFlag` (nullable)

### Report
- `Id` (GUID)
- `ReporterId`
- `SubjectType` (Profile, Photo, Message)
- `SubjectId`
- `Reason`
- `Status` (Open, InReview, Resolved)
- `ModeratorId` (nullable)
- `CreatedAt`
- `ResolvedAt` (nullable)

## Relationships
- One `MemberProfile` ↔ many `PhotoAsset`, `SwipeEvent`, `Match` (as either A or B), `Message` (via Match), `Report` (as reporter or subject).
- `Match` aggregates two members and feeds `Message` stream; cascade archive when both members block.
- `PhotoAsset` privacy levels influence matchmaking presentation logic (via YARP policies).
- `Report` ties to `Message` or `PhotoAsset` for moderation workflows.

## Derived Data & Views
- Daily candidate queue view combining `MemberProfile`, `SwipeEvent` history, compatibility score, distance.
- Messaging timeline view keyed by `MatchId` with unread count per participant.
- Safety dashboard summarizing open reports, top offenders, and response times.

## Data Governance
- Retain `Message` content for 90 days pending legal guidance (FR-011 clarification).
- Apply soft delete for `MemberProfile` to support account recovery and audit trails.
- Ensure all PII fields encrypted at rest via PostgreSQL column-level encryption (existing infrastructure check required).
