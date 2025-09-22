using Microsoft.AspNetCore.Mvc;
using AuthService.DTOs;

namespace AuthService.Controllers
{
    [Route("api/demo")]
    [ApiController]
    public class DemoController : ControllerBase
    {
        private readonly ILogger<DemoController> _logger;

        public DemoController(ILogger<DemoController> logger)
        {
            _logger = logger;
        }

        /// <summary>
        /// Demo registration that always succeeds with predefined responses
        /// </summary>
        [HttpPost("register")]
        public ActionResult<AuthResponseDto> DemoRegister([FromBody] RegisterDto registerDto)
        {
            try
            {
                // Generate a demo user ID based on email hash
                var userId = Math.Abs(registerDto.Email.GetHashCode()) % 10000 + 1;

                var response = new AuthResponseDto
                {
                    Success = true,
                    Message = "Demo registration successful",
                    UserId = userId,
                    Email = registerDto.Email,
                    Token = GenerateDemoToken(userId, registerDto.Email),
                    RefreshToken = GenerateDemoRefreshToken(),
                    ExpiresAt = DateTime.UtcNow.AddHours(24),
                    UserProfile = new UserProfileSummaryDto
                    {
                        Id = userId,
                        Name = registerDto.FullName,
                        Email = registerDto.Email,
                        IsVerified = false,
                        IsOnline = true,
                        LastActiveAt = DateTime.UtcNow,
                        CreatedAt = DateTime.UtcNow
                    }
                };

                _logger.LogInformation($"Demo registration successful for {registerDto.Email}");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in demo registration");
                return StatusCode(500, "Demo registration error");
            }
        }

        /// <summary>
        /// Demo login that accepts any credentials and returns success
        /// </summary>
        [HttpPost("login")]
        public ActionResult<AuthResponseDto> DemoLogin([FromBody] LoginDto loginDto)
        {
            try
            {
                // Generate consistent user ID for demo
                var userId = Math.Abs(loginDto.Email.GetHashCode()) % 10000 + 1;

                var response = new AuthResponseDto
                {
                    Success = true,
                    Message = "Demo login successful",
                    UserId = userId,
                    Email = loginDto.Email,
                    Token = GenerateDemoToken(userId, loginDto.Email),
                    RefreshToken = GenerateDemoRefreshToken(),
                    ExpiresAt = DateTime.UtcNow.AddHours(24),
                    UserProfile = new UserProfileSummaryDto
                    {
                        Id = userId,
                        Name = GetDemoNameFromEmail(loginDto.Email),
                        Email = loginDto.Email,
                        IsVerified = true,
                        IsOnline = true,
                        LastActiveAt = DateTime.UtcNow,
                        CreatedAt = DateTime.UtcNow.AddDays(-Random.Shared.Next(1, 365))
                    }
                };

                _logger.LogInformation($"Demo login successful for {loginDto.Email}");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in demo login");
                return StatusCode(500, "Demo login error");
            }
        }

        /// <summary>
        /// Demo token refresh that always succeeds
        /// </summary>
        [HttpPost("refresh")]
        public ActionResult<TokenRefreshResponseDto> DemoRefreshToken([FromBody] RefreshTokenDto refreshDto)
        {
            try
            {
                var response = new TokenRefreshResponseDto
                {
                    Success = true,
                    Token = GenerateDemoToken(1, "demo@example.com"),
                    RefreshToken = GenerateDemoRefreshToken(),
                    ExpiresAt = DateTime.UtcNow.AddHours(24)
                };

                _logger.LogInformation("Demo token refresh successful");
                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in demo token refresh");
                return StatusCode(500, "Demo token refresh error");
            }
        }

        /// <summary>
        /// Demo logout that always succeeds
        /// </summary>
        [HttpPost("logout")]
        public IActionResult DemoLogout()
        {
            try
            {
                _logger.LogInformation("Demo logout successful");
                return Ok(new { Success = true, Message = "Demo logout successful" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in demo logout");
                return StatusCode(500, "Demo logout error");
            }
        }

        /// <summary>
        /// Demo password reset that always succeeds
        /// </summary>
        [HttpPost("forgot-password")]
        public IActionResult DemoForgotPassword([FromBody] ForgotPasswordDto forgotPasswordDto)
        {
            try
            {
                _logger.LogInformation($"Demo password reset requested for {forgotPasswordDto.Email}");
                return Ok(new 
                { 
                    Success = true, 
                    Message = "Demo password reset email sent (simulated)",
                    ResetCode = "DEMO123" // In real app, this wouldn't be returned
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in demo password reset");
                return StatusCode(500, "Demo password reset error");
            }
        }

        /// <summary>
        /// Demo email verification that always succeeds
        /// </summary>
        [HttpPost("verify-email")]
        public IActionResult DemoVerifyEmail([FromBody] VerifyEmailDto verifyEmailDto)
        {
            try
            {
                _logger.LogInformation($"Demo email verification for code {verifyEmailDto.VerificationCode}");
                return Ok(new
                {
                    Success = true,
                    Message = "Demo email verification successful"
                });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error in demo email verification");
                return StatusCode(500, "Demo email verification error");
            }
        }

        /// <summary>
        /// Returns demo user accounts for testing
        /// </summary>
        [HttpGet("test-accounts")]
        public ActionResult<List<object>> GetDemoTestAccounts()
        {
            try
            {
                var testAccounts = new[]
                {
                    new { Email = "alice@demo.com", Password = "password123", FullName = "Alice Johnson" },
                    new { Email = "bob@demo.com", Password = "password123", FullName = "Bob Smith" },
                    new { Email = "carol@demo.com", Password = "password123", FullName = "Carol Williams" },
                    new { Email = "demo@example.com", Password = "demo123", FullName = "Demo User" },
                    new { Email = "test@test.com", Password = "test123", FullName = "Test User" }
                };

                _logger.LogInformation("Returned demo test accounts");
                return Ok(testAccounts);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting demo test accounts");
                return StatusCode(500, "Error getting demo test accounts");
            }
        }

        /// <summary>
        /// Health check for demo endpoints
        /// </summary>
        [HttpGet("health")]
        public IActionResult DemoHealthCheck()
        {
            return Ok(new
            {
                Status = "Healthy",
                Timestamp = DateTime.UtcNow,
                Service = "AuthService Demo Mode",
                AvailableEndpoints = new[]
                {
                    "POST /api/demo/register",
                    "POST /api/demo/login",
                    "POST /api/demo/refresh",
                    "POST /api/demo/logout",
                    "POST /api/demo/forgot-password",
                    "POST /api/demo/verify-email",
                    "GET /api/demo/test-accounts"
                }
            });
        }

        #region Private Helper Methods

        private string GenerateDemoToken(int userId, string email)
        {
            // Generate a fake JWT-like token for demo purposes
            var header = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes("{\"alg\":\"HS256\",\"typ\":\"JWT\"}"));
            var payload = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes($"{{\"sub\":\"{userId}\",\"email\":\"{email}\",\"exp\":{DateTimeOffset.UtcNow.AddHours(24).ToUnixTimeSeconds()}}}"));
            var signature = Convert.ToBase64String(System.Text.Encoding.UTF8.GetBytes("demo_signature"));
            
            return $"{header}.{payload}.{signature}";
        }

        private string GenerateDemoRefreshToken()
        {
            return $"demo_refresh_{Guid.NewGuid():N}";
        }

        private string GetDemoNameFromEmail(string email)
        {
            var localPart = email.Split('@')[0];
            return localPart.Split('.').Length > 1 
                ? string.Join(" ", localPart.Split('.').Select(part => char.ToUpper(part[0]) + part.Substring(1)))
                : char.ToUpper(localPart[0]) + localPart.Substring(1);
        }

        #endregion
    }
}
