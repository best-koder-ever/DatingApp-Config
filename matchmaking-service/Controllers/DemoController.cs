using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
namespace MatchmakingService.Controllers
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
            _logger.LogWarning("MatchmakingService demo endpoint {Endpoint} was called after deprecation.", endpoint);
            return StatusCode(StatusCodes.Status410Gone, new
            {
                message = "MatchmakingService demo mode has been retired. Please integrate with the production matchmaking APIs via the YARP gateway.",
                endpoint
            });
        }

        [HttpGet("matches/{userId:int}")]
        public IActionResult GetDemoMatches() => DemoEndpointRemoved("GET /api/demo/matches/{userId}");

        [HttpGet("mutual-matches/{userId:int}")]
        public IActionResult GetDemoMutualMatches() => DemoEndpointRemoved("GET /api/demo/mutual-matches/{userId}");

        [HttpPost("swipe")]
        public IActionResult DemoSwipe() => DemoEndpointRemoved("POST /api/demo/swipe");

        [HttpGet("conversations/{userId:int}")]
        public IActionResult GetDemoConversations() => DemoEndpointRemoved("GET /api/demo/conversations/{userId}");

        [HttpGet("conversations/{conversationId:int}/messages")]
        public IActionResult GetDemoMessages() => DemoEndpointRemoved("GET /api/demo/conversations/{conversationId}/messages");

        [HttpPost("conversations/{conversationId:int}/messages")]
        public IActionResult SendDemoMessage() => DemoEndpointRemoved("POST /api/demo/conversations/{conversationId}/messages");

        [HttpGet("health")]
        public IActionResult DemoHealthCheck()
        {
            _logger.LogInformation("MatchmakingService demo health endpoint requested after retirement.");
            return StatusCode(StatusCodes.Status410Gone, new
            {
                message = "Demo mode has been retired. Use /health on the production controllers instead."
            });
        }
    }
}
