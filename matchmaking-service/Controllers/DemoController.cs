using Microsoft.AspNetCore.Mvc;
using MatchmakingService.DTOs;

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

        /// <summary>
        /// Returns demo potential matches for a user
        /// </summary>
        [HttpGet("matches/{userId:int}")]
        public ActionResult<List<PotentialMatchDto>> GetDemoMatches(int userId, [FromQuery] int count = 10)
        {
            try
            {
                var demoMatches = GenerateDemoMatches(userId, count);
                _logger.LogInformation($"Generated {demoMatches.Count} demo matches for user {userId}");
                return Ok(demoMatches);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error generating demo matches for user {userId}");
                return StatusCode(500, "Error generating demo matches");
            }
        }

        /// <summary>
        /// Returns demo mutual matches (people who liked each other)
        /// </summary>
        [HttpGet("mutual-matches/{userId:int}")]
        public ActionResult<List<MutualMatchDto>> GetDemoMutualMatches(int userId)
        {
            try
            {
                var mutualMatches = GenerateDemoMutualMatches(userId);
                _logger.LogInformation($"Generated {mutualMatches.Count} demo mutual matches for user {userId}");
                return Ok(mutualMatches);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error generating demo mutual matches for user {userId}");
                return StatusCode(500, "Error generating demo mutual matches");
            }
        }

        /// <summary>
        /// Simulates a swipe action (like/pass) on a potential match
        /// </summary>
        [HttpPost("swipe")]
        public ActionResult<SwipeResultDto> DemoSwipe([FromBody] SwipeActionDto swipeDto)
        {
            try
            {
                // Simulate random match probability (20% chance of mutual match)
                var isMatch = Random.Shared.Next(1, 101) <= 20;

                var result = new SwipeResultDto
                {
                    IsMatch = isMatch,
                    MatchId = isMatch ? Random.Shared.Next(1000, 9999) : null,
                    Message = isMatch ? "It's a match! 💕" : "Keep swiping!"
                };

                _logger.LogInformation($"Demo swipe: User {swipeDto.UserId} {swipeDto.Action} user {swipeDto.TargetUserId}. Match: {isMatch}");
                return Ok(result);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing demo swipe");
                return StatusCode(500, "Error processing demo swipe");
            }
        }

        /// <summary>
        /// Returns demo conversations for a user
        /// </summary>
        [HttpGet("conversations/{userId:int}")]
        public ActionResult<List<ConversationDto>> GetDemoConversations(int userId)
        {
            try
            {
                var conversations = GenerateDemoConversations(userId);
                _logger.LogInformation($"Generated {conversations.Count} demo conversations for user {userId}");
                return Ok(conversations);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error generating demo conversations for user {userId}");
                return StatusCode(500, "Error generating demo conversations");
            }
        }

        /// <summary>
        /// Returns demo messages for a conversation
        /// </summary>
        [HttpGet("conversations/{conversationId:int}/messages")]
        public ActionResult<List<MessageDto>> GetDemoMessages(int conversationId, [FromQuery] int page = 1, [FromQuery] int pageSize = 20)
        {
            try
            {
                var messages = GenerateDemoMessages(conversationId, page, pageSize);
                _logger.LogInformation($"Generated {messages.Count} demo messages for conversation {conversationId}");
                return Ok(messages);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error generating demo messages for conversation {conversationId}");
                return StatusCode(500, "Error generating demo messages");
            }
        }

        /// <summary>
        /// Simulates sending a message in a conversation
        /// </summary>
        [HttpPost("conversations/{conversationId:int}/messages")]
        public ActionResult<MessageDto> SendDemoMessage(int conversationId, [FromBody] SendMessageDto messageDto)
        {
            try
            {
                var message = new MessageDto
                {
                    Id = Random.Shared.Next(10000, 99999),
                    ConversationId = conversationId,
                    SenderId = messageDto.SenderId,
                    Content = messageDto.Content,
                    MessageType = messageDto.MessageType ?? "text",
                    SentAt = DateTime.UtcNow,
                    IsRead = false,
                    IsDelivered = true
                };

                _logger.LogInformation($"Demo message sent in conversation {conversationId}");
                return Ok(message);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, $"Error sending demo message in conversation {conversationId}");
                return StatusCode(500, "Error sending demo message");
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
                Service = "MatchmakingService Demo Mode",
                AvailableEndpoints = new[]
                {
                    "GET /api/demo/matches/{userId}",
                    "GET /api/demo/mutual-matches/{userId}",
                    "POST /api/demo/swipe",
                    "GET /api/demo/conversations/{userId}",
                    "GET /api/demo/conversations/{conversationId}/messages",
                    "POST /api/demo/conversations/{conversationId}/messages"
                }
            });
        }

        #region Private Helper Methods

        private List<PotentialMatchDto> GenerateDemoMatches(int userId, int count)
        {
            var matches = new List<PotentialMatchDto>();
            var names = new[]
            {
                "Emma", "Sofia", "Isabella", "Olivia", "Ava", "Mia", "Amelia", "Charlotte", "Luna", "Harper"
            };

            var bios = new[]
            {
                "Love hiking and photography 📸",
                "Yoga instructor & coffee enthusiast ☕",
                "Chef who loves to cook for friends 👩‍🍳",
                "Adventure seeker and book lover 📚",
                "Dog mom and travel addict ✈️"
            };

            for (int i = 0; i < count; i++)
            {
                var profileId = userId * 100 + i + 1; // Generate unique IDs based on userId
                matches.Add(new PotentialMatchDto
                {
                    UserId = profileId,
                    Name = names[i % names.Length],
                    Age = 22 + (i % 15),
                    Bio = bios[i % bios.Length],
                    PhotoUrl = $"https://picsum.photos/400/600?random={profileId}",
                    Distance = Random.Shared.Next(1, 50),
                    CommonInterests = Random.Shared.Next(1, 6),
                    CompatibilityScore = Random.Shared.Next(70, 100),
                    IsOnline = i % 3 != 0,
                    LastActiveAt = DateTime.UtcNow.AddMinutes(-Random.Shared.Next(0, 1440))
                });
            }

            return matches;
        }

        private List<MutualMatchDto> GenerateDemoMutualMatches(int userId)
        {
            var mutualMatches = new List<MutualMatchDto>();
            var names = new[] { "Alice", "Sophie", "Emma", "Lila", "Nina" };

            for (int i = 0; i < 3; i++) // Generate 3 mutual matches
            {
                var matchId = userId * 10 + i + 1;
                mutualMatches.Add(new MutualMatchDto
                {
                    MatchId = matchId,
                    UserId = userId + 1000 + i,
                    Name = names[i % names.Length],
                    PhotoUrl = $"https://picsum.photos/400/600?random={matchId + 500}",
                    MatchedAt = DateTime.UtcNow.AddDays(-Random.Shared.Next(1, 30)),
                    LastMessageAt = DateTime.UtcNow.AddHours(-Random.Shared.Next(1, 48)),
                    UnreadMessages = Random.Shared.Next(0, 5),
                    HasConversation = true
                });
            }

            return mutualMatches;
        }

        private List<ConversationDto> GenerateDemoConversations(int userId)
        {
            var conversations = new List<ConversationDto>();
            var names = new[] { "Alice", "Sophie", "Emma" };
            var lastMessages = new[]
            {
                "Hey! How was your weekend?",
                "That restaurant looks amazing! 😍",
                "I love that hiking spot too!"
            };

            for (int i = 0; i < 3; i++)
            {
                conversations.Add(new ConversationDto
                {
                    Id = userId * 100 + i + 1,
                    MatchId = userId * 10 + i + 1,
                    ParticipantName = names[i],
                    ParticipantPhotoUrl = $"https://picsum.photos/400/600?random={userId + i + 600}",
                    LastMessage = lastMessages[i],
                    LastMessageAt = DateTime.UtcNow.AddHours(-Random.Shared.Next(1, 72)),
                    UnreadCount = Random.Shared.Next(0, 4),
                    IsActive = true
                });
            }

            return conversations;
        }

        private List<MessageDto> GenerateDemoMessages(int conversationId, int page, int pageSize)
        {
            var messages = new List<MessageDto>();
            var sampleMessages = new[]
            {
                "Hey! How's your day going?",
                "Great! Just finished a workout. How about you?",
                "Nice! I'm just relaxing at home. Any fun plans for the weekend?",
                "Thinking about going hiking. Want to join?",
                "That sounds amazing! I'd love to! 😊",
                "Perfect! I know a great trail with beautiful views.",
                "Can't wait! What time should we meet?",
                "How about 9 AM at the trail entrance?",
                "Sounds perfect! See you then! 🥾"
            };

            var totalMessages = sampleMessages.Length;
            var startIndex = (page - 1) * pageSize;
            var endIndex = Math.Min(startIndex + pageSize, totalMessages);

            for (int i = startIndex; i < endIndex; i++)
            {
                var messageId = conversationId * 1000 + i + 1;
                messages.Add(new MessageDto
                {
                    Id = messageId,
                    ConversationId = conversationId,
                    SenderId = i % 2 == 0 ? 1 : 2, // Alternate between two users
                    Content = sampleMessages[i],
                    MessageType = "text",
                    SentAt = DateTime.UtcNow.AddHours(-(totalMessages - i)),
                    IsRead = true,
                    IsDelivered = true
                });
            }

            return messages.OrderByDescending(m => m.SentAt).ToList();
        }

        #endregion
    }
}
