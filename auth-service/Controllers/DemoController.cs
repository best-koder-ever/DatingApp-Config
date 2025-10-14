using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;

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

        private IActionResult DemoEndpointRemoved(string endpoint)
        {
            _logger.LogWarning("AuthService demo endpoint {Endpoint} was called after deprecation.", endpoint);
            return StatusCode(StatusCodes.Status410Gone, new
            {
                message = "AuthService demo mode has been retired. Please authenticate via Keycloak using the production endpoints.",
                endpoint
            });
        }

        [HttpPost("register")]
        public IActionResult DemoRegister() => DemoEndpointRemoved("POST /api/demo/register");

        [HttpPost("login")]
        public IActionResult DemoLogin() => DemoEndpointRemoved("POST /api/demo/login");

        [HttpPost("refresh")]
        public IActionResult DemoRefreshToken() => DemoEndpointRemoved("POST /api/demo/refresh");

        [HttpPost("logout")]
        public IActionResult DemoLogout() => DemoEndpointRemoved("POST /api/demo/logout");

        [HttpPost("forgot-password")]
        public IActionResult DemoForgotPassword() => DemoEndpointRemoved("POST /api/demo/forgot-password");

        [HttpPost("verify-email")]
        public IActionResult DemoVerifyEmail() => DemoEndpointRemoved("POST /api/demo/verify-email");

        [HttpGet("test-accounts")]
        public IActionResult GetDemoTestAccounts() => DemoEndpointRemoved("GET /api/demo/test-accounts");

        [HttpGet("health")]
        public IActionResult DemoHealthCheck()
        {
            _logger.LogInformation("AuthService demo health endpoint requested after retirement.");
            return StatusCode(StatusCodes.Status410Gone, new
            {
                message = "Demo mode has been retired. Use the production /health endpoint instead."
            });
        }
    }
}
