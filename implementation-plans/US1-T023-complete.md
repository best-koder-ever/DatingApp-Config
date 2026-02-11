# Complete Implementation Plan: T023 UserService Wizard Endpoints

**Task**: T023 - UserService wizard endpoints for multi-step profile creation  
**Duration**: ~2 hours  
**Status**: 50% complete (enum + model done, need migration + DTOs + endpoints)  
**Generated**: 2025-01-20  

## ✅ Already Completed

1. Created `UserService/Models/OnboardingStatus.cs`:
   ```csharp
   public enum OnboardingStatus
   {
       Incomplete = 0,  // User in wizard
       Ready = 1,       // Can see matches
       Suspended = 2    // Blocked/moderated
   }
   ```

2. Modified `UserService/Models/UserProfile.cs`:
   - Added `public OnboardingStatus OnboardingStatus { get; set; } = OnboardingStatus.Incomplete;`
   - Added `public DateTime? OnboardingCompletedAt { get; set; }`

## 🔨 Implementation Steps (Execute in Order)

### Step 1: Create EF Core Migration (5 minutes)

```bash
cd /home/m/development/DatingApp/UserService
dotnet ef migrations add AddOnboardingStatus -o Data/Migrations
```

**Verify migration file contains**:
- `migrationBuilder.AddColumn<int>("OnboardingStatus", defaultValue: 0)`
- `migrationBuilder.AddColumn<DateTime?>("OnboardingCompletedAt", nullable: true)`

### Step 2: Create Wizard DTOs (10 minutes)

Create `UserService/DTOs/WizardStepBasicInfoDto.cs`:

```csharp
namespace UserService.DTOs;

/// <summary>
/// Step 1: Basic profile information (name, DOB, gender)
/// </summary>
public class WizardStepBasicInfoDto
{
    public required string FirstName { get; set; }
    public required string LastName { get; set; }
    public required DateTime DateOfBirth { get; set; }
    public required string Gender { get; set; }
    
    // Validation: Age 18+
    public bool IsValid() => 
        !string.IsNullOrWhiteSpace(FirstName) &&
        !string.IsNullOrWhiteSpace(LastName) &&
        DateOfBirth < DateTime.UtcNow.AddYears(-18);
}
```

Create `UserService/DTOs/WizardStepPreferencesDto.cs`:

```csharp
namespace UserService.DTOs;

/// <summary>
/// Step 2: Search preferences (age range, distance, etc.)
/// </summary>
public class WizardStepPreferencesDto
{
    public int MinAge { get; set; } = 18;
    public int MaxAge { get; set; } = 99;
    public int MaxDistance { get; set; } = 50; // km
    public string? PreferredGender { get; set; }
    
    // Optional: Bio text
    public string? Bio { get; set; }
    
    public bool IsValid() =>
        MinAge >= 18 &&
        MaxAge >= MinAge &&
        MaxDistance > 0;
}
```

Create `UserService/DTOs/WizardStepPhotosDto.cs`:

```csharp
namespace UserService.DTOs;

/// <summary>
/// Step 3: Photo upload confirmation (actual upload via PhotoService)
/// </summary>
public class WizardStepPhotosDto
{
    public required List<string> PhotoUrls { get; set; }
    
    /// <summary>
    /// Minimum 1 photo required to complete wizard
    /// </summary>
    public bool IsValid() => PhotoUrls.Count >= 1;
}
```

### Step 3: Update UserProfileDetailDto (5 minutes)

Edit `UserService/DTOs/UserProfileDetailDto.cs`:

**Find** (around line 10):
```csharp
public class UserProfileDetailDto
{
    public Guid UserId { get; set; }
    public string? FirstName { get; set; }
    // ... existing properties ...
```

**Add after existing properties**:
```csharp
    // Onboarding status
    public OnboardingStatus OnboardingStatus { get; set; }
    public DateTime? OnboardingCompletedAt { get; set; }
```

### Step 4: Create Wizard Command (15 minutes)

Create `UserService/Commands/UpdateWizardStepCommand.cs`:

```csharp
using MediatR;
using UserService.DTOs;
using UserService.Models;

namespace UserService.Commands;

/// <summary>
/// Command to update a specific wizard step
/// </summary>
public record UpdateWizardStepCommand : IRequest<UserProfile>
{
    public Guid UserId { get; init; }
    public int Step { get; init; } // 1, 2, or 3
    
    // Step-specific data (only one will be populated)
    public WizardStepBasicInfoDto? BasicInfo { get; init; }
    public WizardStepPreferencesDto? Preferences { get; init; }
    public WizardStepPhotosDto? Photos { get; init; }
}
```

Create `UserService/Handlers/UpdateWizardStepHandler.cs`:

```csharp
using MediatR;
using Microsoft.EntityFrameworkCore;
using UserService.Commands;
using UserService.Data;
using UserService.Models;

namespace UserService.Handlers;

public class UpdateWizardStepHandler : IRequestHandler<UpdateWizardStepCommand, UserProfile>
{
    private readonly ApplicationDbContext _context;
    private readonly ILogger<UpdateWizardStepHandler> _logger;

    public UpdateWizardStepHandler(
        ApplicationDbContext context,
        ILogger<UpdateWizardStepHandler> logger)
    {
        _context = context;
        _logger = logger;
    }

    public async Task<UserProfile> Handle(UpdateWizardStepCommand request, CancellationToken cancellationToken)
    {
        var profile = await _context.UserProfiles
            .FirstOrDefaultAsync(p => p.UserId == request.UserId, cancellationToken);
        
        if (profile == null)
        {
            // Create new profile if doesn't exist
            profile = new UserProfile { UserId = request.UserId };
            _context.UserProfiles.Add(profile);
        }

        switch (request.Step)
        {
            case 1: // Basic info
                if (request.BasicInfo == null || !request.BasicInfo.IsValid())
                    throw new ArgumentException("Invalid basic info");
                
                profile.FirstName = request.BasicInfo.FirstName;
                profile.LastName = request.BasicInfo.LastName;
                profile.DateOfBirth = request.BasicInfo.DateOfBirth;
                profile.Gender = request.BasicInfo.Gender;
                _logger.LogInformation("Updated wizard step 1 for user {UserId}", request.UserId);
                break;

            case 2: // Preferences
                if (request.Preferences == null || !request.Preferences.IsValid())
                    throw new ArgumentException("Invalid preferences");
                
                profile.MinAge = request.Preferences.MinAge;
                profile.MaxAge = request.Preferences.MaxAge;
                profile.MaxDistance = request.Preferences.MaxDistance;
                profile.PreferredGender = request.Preferences.PreferredGender;
                profile.Bio = request.Preferences.Bio;
                _logger.LogInformation("Updated wizard step 2 for user {UserId}", request.UserId);
                break;

            case 3: // Photos + completion
                if (request.Photos == null || !request.Photos.IsValid())
                    throw new ArgumentException("At least 1 photo required");
                
                // Mark wizard complete
                profile.OnboardingStatus = OnboardingStatus.Ready;
                profile.OnboardingCompletedAt = DateTime.UtcNow;
                profile.IsActive = true;
                _logger.LogInformation("Completed wizard for user {UserId}", request.UserId);
                break;

            default:
                throw new ArgumentException($"Invalid step: {request.Step}");
        }

        await _context.SaveChangesAsync(cancellationToken);
        return profile;
    }
}
```

### Step 5: Create Wizard Controller Endpoints (20 minutes)

Create `UserService/Controllers/WizardController.cs`:

```csharp
using MediatR;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using UserService.Commands;
using UserService.DTOs;
using System.Security.Claims;

namespace UserService.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class WizardController : ControllerBase
{
    private readonly IMediator _mediator;
    private readonly ILogger<WizardController> _logger;

    public WizardController(IMediator mediator, ILogger<WizardController> logger)
    {
        _mediator = mediator;
        _logger = logger;
    }

    /// <summary>
    /// Update wizard step 1: Basic profile information
    /// </summary>
    [HttpPatch("step/1")]
    [ProducesResponseType(typeof(UserProfileDetailDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> UpdateStepBasicInfo([FromBody] WizardStepBasicInfoDto dto)
    {
        var userId = GetUserIdFromClaims();
        
        var command = new UpdateWizardStepCommand
        {
            UserId = userId,
            Step = 1,
            BasicInfo = dto
        };

        try
        {
            var profile = await _mediator.Send(command);
            return Ok(MapToDetailDto(profile));
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    /// <summary>
    /// Update wizard step 2: Search preferences
    /// </summary>
    [HttpPatch("step/2")]
    [ProducesResponseType(typeof(UserProfileDetailDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> UpdateStepPreferences([FromBody] WizardStepPreferencesDto dto)
    {
        var userId = GetUserIdFromClaims();
        
        var command = new UpdateWizardStepCommand
        {
            UserId = userId,
            Step = 2,
            Preferences = dto
        };

        try
        {
            var profile = await _mediator.Send(command);
            return Ok(MapToDetailDto(profile));
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    /// <summary>
    /// Complete wizard step 3: Photos uploaded (marks profile as Ready)
    /// </summary>
    [HttpPatch("step/3")]
    [ProducesResponseType(typeof(UserProfileDetailDto), StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CompleteWizard([FromBody] WizardStepPhotosDto dto)
    {
        var userId = GetUserIdFromClaims();
        
        var command = new UpdateWizardStepCommand
        {
            UserId = userId,
            Step = 3,
            Photos = dto
        };

        try
        {
            var profile = await _mediator.Send(command);
            _logger.LogInformation("User {UserId} completed onboarding wizard", userId);
            return Ok(MapToDetailDto(profile));
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { error = ex.Message });
        }
    }

    private Guid GetUserIdFromClaims()
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value
                          ?? User.FindFirst("sub")?.Value;
        
        if (string.IsNullOrEmpty(userIdClaim) || !Guid.TryParse(userIdClaim, out var userId))
        {
            throw new UnauthorizedAccessException("Invalid user claims");
        }
        
        return userId;
    }

    private UserProfileDetailDto MapToDetailDto(UserProfile profile)
    {
        return new UserProfileDetailDto
        {
            UserId = profile.UserId,
            FirstName = profile.FirstName,
            LastName = profile.LastName,
            DateOfBirth = profile.DateOfBirth,
            Gender = profile.Gender,
            Bio = profile.Bio,
            OnboardingStatus = profile.OnboardingStatus,
            OnboardingCompletedAt = profile.OnboardingCompletedAt,
            // ... map other properties as needed
        };
    }
}
```

### Step 6: Apply Migration (2 minutes)

```bash
cd /home/m/development/DatingApp
./infrastructure/start.sh  # Ensure DB is running
cd UserService
dotnet ef database update
```

**Verify**:
```bash
# Check UserProfiles table has new columns
dotnet ef migrations list
```

### Step 7: Build and Test (10 minutes)

```bash
cd /home/m/development/DatingApp/UserService
dotnet build

# Run existing tests
dotnet test

# Manual API test
curl -X PATCH http://localhost:5001/api/wizard/step/1 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "John",
    "lastName": "Doe",
    "dateOfBirth": "1990-01-01",
    "gender": "male"
  }'
```

### Step 8: Update API Contracts (5 minutes)

Edit `dejting-yarp/Contracts/api-spec.md`:

**Add under UserService section**:
```markdown
#### Wizard Endpoints

**PATCH /api/wizard/step/1** - Update basic info  
Request:
```json
{
  "firstName": "John",
  "lastName": "Doe",
  "dateOfBirth": "1990-01-01",
  "gender": "male"
}
```

**PATCH /api/wizard/step/2** - Update preferences  
Request:
```json
{
  "minAge": 25,
  "maxAge": 35,
  "maxDistance": 50,
  "preferredGender": "female",
  "bio": "Love hiking and coffee"
}
```

**PATCH /api/wizard/step/3** - Complete wizard  
Request:
```json
{
  "photoUrls": ["https://photo-service/photos/abc123"]
}
```

Response (all steps):
```json
{
  "userId": "guid",
  "firstName": "John",
  "onboardingStatus": 1,  // 0=Incomplete, 1=Ready, 2=Suspended
  "onboardingCompletedAt": "2025-01-20T12:00:00Z"
}
```
```

### Step 9: Mark T023 Complete (5 minutes)

Edit `specs/001-mvp-foundation/tasks.md`:

**Find T023**:
```markdown
- [ ] **T023**: UserService wizard endpoints
```

**Replace with**:
```markdown
- [x] **T023**: UserService wizard endpoints  
  **Evidence**: WizardController.cs with 3 PATCH endpoints, UpdateWizardStepCommand handler, OnboardingStatus enum, EF migration AddOnboardingStatus  
  **Completion**: 2025-01-20  
  **Files**: UserService/Controllers/WizardController.cs, UserService/Commands/UpdateWizardStepCommand.cs, UserService/Handlers/UpdateWizardStepHandler.cs
```

### Step 10: Commit and Push (3 minutes)

```bash
cd /home/m/development/DatingApp

# Use gita workflow (per AI_COLLABORATION_GUIDE.md - never manual git loops)
./gita-workflow.sh commit "T023: Complete wizard endpoints with 3-step flow

- Created WizardController with PATCH /api/wizard/step/{1,2,3} endpoints
- Added UpdateWizardStepCommand + handler for multi-step persistence
- Created wizard DTOs (BasicInfo, Preferences, Photos)
- Added OnboardingStatus enum (Incomplete/Ready/Suspended)
- EF Core migration: AddOnboardingStatus columns
- Updated UserProfile model with wizard tracking fields
- Updated API contracts in dejting-yarp/Contracts/api-spec.md

Wizard flow:
1. PATCH step/1 → firstName, lastName, DOB, gender
2. PATCH step/2 → age/distance preferences, bio
3. PATCH step/3 → photo confirmation → status=Ready, IsActive=true

Closes T023 blocker for US1 profile onboarding"
```

## ✅ Success Criteria

1. **Migration Applied**: `OnboardingStatus` and `OnboardingCompletedAt` columns exist in UserProfiles table
2. **Endpoints Work**: Can PATCH /api/wizard/step/1, 2, 3 with valid JWT token
3. **Status Transitions**: Profile starts with Incomplete(0), ends with Ready(1) after step 3
4. **Validation**: Invalid data (age < 18, no photos) returns 400 Bad Request
5. **Tests Pass**: `dotnet test UserService` shows 0 failures
6. **Task Marked Complete**: T023 has [x] checkbox in tasks.md

## 🚀 Next Tasks After T023

1. **T025**: Database migration deployment strategy (apply to shared dev DB)
2. **T026**: Flutter wizard UI (3-screen flow matching these endpoints)
3. **T028**: Profile onboarding integration test (E2E wizard flow)
4. **T029**: Keycloak-first test automation (replace TestDataGenerator)

## 📝 Notes

- **Photo Upload**: Step 3 only validates photo URLs exist (actual upload handled by PhotoService)
- **Idempotency**: All PATCH endpoints are idempotent - can call multiple times without side effects
- **Security**: All endpoints require [Authorize] - JWT token from Keycloak
- **Error Handling**: ArgumentException for validation → 400 Bad Request
- **Logging**: All steps logged with user ID for audit trail

## 🐛 Troubleshooting

**Migration fails**:
```bash
# Drop and recreate DB (dev only!)
dotnet ef database drop --force
dotnet ef database update
```

**"Invalid user claims" error**:
- Check JWT token has `sub` or `NameIdentifier` claim
- Verify Keycloak client mapper includes user ID

**Tests fail**:
- Ensure ApplicationDbContext is mocked
- Check OnboardingStatus enum is imported in test files

---

**Estimated Total Time**: 1.5 - 2 hours  
**Ready to Execute**: Yes - all code provided, just copy/paste files  
**Dependencies**: ✅ Keycloak configured (T022), ✅ OnboardingStatus enum created
