using System;
using Xunit;
using UserService.Models;

namespace UserService.Tests
{
    public class UserProfileTests
    {
        [Fact]
        public void CanCreateUserProfile_WithValidData()
        {
            var profile = new UserProfile
            {
                Name = "Test User",
                Bio = "Test bio",
                ProfilePictureUrl = "https://i.pravatar.cc/150?u=test@example.com",
                Preferences = "Testing, Automation",
                Email = "test@example.com",
                Gender = "Other",
                Location = "Test City",
                Interests = "Testing",
                DateOfBirth = DateTime.Now.AddYears(-25),
                CreatedAt = DateTime.Now,
                LastActiveAt = DateTime.Now,
                IsVerified = false
            };
            Assert.Equal("Test User", profile.Name);
            Assert.Equal("test@example.com", profile.Email);
            Assert.False(profile.IsVerified);
        }
    }
}
