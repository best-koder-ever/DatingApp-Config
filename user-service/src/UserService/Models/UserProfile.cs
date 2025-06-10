// filepath: UserService/Models/UserProfile.cs
namespace UserService.Models
{
    public class UserProfile
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Bio { get; set; } = string.Empty;
        public string ProfilePictureUrl { get; set; } = string.Empty;
        public string Preferences { get; set; } = string.Empty;
    }
}