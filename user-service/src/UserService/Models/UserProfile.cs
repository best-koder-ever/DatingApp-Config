// filepath: UserService/Models/UserProfile.cs
namespace UserService.Models
{
    public class UserProfile
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty; // Unique identifier for login and linking
        public string Bio { get; set; } = string.Empty;
        public string ProfilePictureUrl { get; set; } = string.Empty;
        public string Preferences { get; set; } = string.Empty; // e.g., "Men, Women, Both"
        public string Gender { get; set; } = string.Empty; // e.g., "Male", "Female", "Non-binary"
        public string SexualOrientation { get; set; } = string.Empty; // e.g., "Straight", "Gay", "Bisexual"
        public DateTime DateOfBirth { get; set; } // For age calculation
        public string Location { get; set; } = string.Empty; // City or coordinates
        public string PhotoUrls { get; set; } = string.Empty; // Comma-separated URLs for additional photos
        public string Occupation { get; set; } = string.Empty;
        public string Education { get; set; } = string.Empty;
        public string Interests { get; set; } = string.Empty; // e.g., "Hiking, Music, Movies"
        public string InstagramHandle { get; set; } = string.Empty;
        public string SpotifyTopArtists { get; set; } = string.Empty;
        public bool IsVerified { get; set; } = false;
        public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
        public DateTime LastActiveAt { get; set; } = DateTime.UtcNow;
    }
}