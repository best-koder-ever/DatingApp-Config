// filepath: UserService/Controllers/UserProfilesController.cs
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using UserService.Data;
using UserService.Models;

namespace UserService.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class UserProfilesController : ControllerBase
    {
        private readonly ApplicationDbContext _context;

        public UserProfilesController(ApplicationDbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Retrieves all user profiles.
        /// </summary>
        /// <returns>A list of user profiles.</returns>
        [HttpGet]
        [Authorize]
        public async Task<ActionResult<IEnumerable<UserProfile>>> GetUserProfiles()
        {
            // Get the authenticated user's ID from the JWT claims
            var userIdClaim = User.Claims.FirstOrDefault(c => c.Type == "sub" || c.Type.EndsWith("/nameidentifier"));
            string? currentUserId = null;
            if (userIdClaim != null)
            {
                currentUserId = userIdClaim.Value;
            }

            var profiles = await _context.UserProfiles.ToListAsync();
            if (!string.IsNullOrEmpty(currentUserId))
            {
                profiles = profiles.Where(p => p.Id.ToString() != currentUserId).ToList();
            }
            return profiles;
        }

        /// <summary>
        /// Debug endpoint to show current user's authentication status and claims.
        /// </summary>
        [HttpGet("debug-auth")]
        public IActionResult DebugAuth()
        {
            return Ok(new {
                IsAuthenticated = User.Identity?.IsAuthenticated,
                AuthenticationType = User.Identity?.AuthenticationType,
                Claims = User.Claims.Select(c => new { c.Type, c.Value }).ToList()
            });
        }

        /// <summary>
        /// Retrieves a specific user profile by ID.
        /// </summary>
        /// <param name="id">The ID of the user profile.</param>
        /// <returns>The user profile if found, or a not found message.</returns>
        [HttpGet("{id:int}")]
        public async Task<ActionResult<UserProfile>> GetUserProfile([FromRoute] int id)
        {
            var userProfile = await _context.UserProfiles.FindAsync(id);

            if (userProfile == null)
            {
                return NotFound();
            }

            return userProfile;
        }

        /// <summary>
        /// Updates a specific user profile by ID.
        /// </summary>
        /// <param name="id">The ID of the user profile.</param>
        /// <param name="userProfile">The updated user profile data.</param>
        /// <returns>No content if the update is successful, or an error message.</returns>
        [HttpPut("{id:int}")]
        public async Task<IActionResult> PutUserProfile(int id, UserProfile userProfile)
        {
            if (id != userProfile.Id)
            {
                return BadRequest();
            }

            _context.Entry(userProfile).State = EntityState.Modified;

            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!UserProfileExists(id))
                {
                    return NotFound();
                }
                else
                {
                    throw;
                }
            }

            return NoContent();
        }

        /// <summary>
        /// Creates a new user profile.
        /// </summary>
        /// <param name="userProfile">The user profile data to create.</param>
        /// <returns>The created user profile.</returns>
        [HttpPost]
        public async Task<ActionResult<UserProfile>> PostUserProfile(UserProfile userProfile)
        {
            _context.UserProfiles.Add(userProfile);
            await _context.SaveChangesAsync();

            return CreatedAtAction("GetUserProfile", new { id = userProfile.Id }, userProfile);
        }

        /// <summary>
        /// Deletes a specific user profile by ID.
        /// </summary>
        /// <param name="id">The ID of the user profile.</param>
        /// <returns>No content if the deletion is successful, or a not found message.</returns>
        [HttpDelete("{id:int}")]
        public async Task<IActionResult> DeleteUserProfile(int id)
        {
            var userProfile = await _context.UserProfiles.FindAsync(id);
            if (userProfile == null)
            {
                return NotFound();
            }

            _context.UserProfiles.Remove(userProfile);
            await _context.SaveChangesAsync();

            return NoContent();
        }

        private bool UserProfileExists(int id)
        {
            return _context.UserProfiles.Any(e => e.Id == id);
        }
    }
}