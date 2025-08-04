using System;
using Xunit;
using Microsoft.EntityFrameworkCore;
using UserService.Data;
using UserService.Models;

namespace UserService.Tests
{
    public class UserProfileDbTests
    {
        [Fact]
        public void CanInsertAndRetrieveUserProfile_FromDbContext()
        {
            var options = new DbContextOptionsBuilder<ApplicationDbContext>()
                .UseInMemoryDatabase(databaseName: "TestUserProfileDb")
                .Options;
            using var context = new ApplicationDbContext(options);
            var profile = new UserProfile
            {
                Name = "Db User",
                Bio = "Db bio",
                ProfilePictureUrl = "https://i.pravatar.cc/150?u=db@example.com",
                Preferences = "Db, Test",
                Email = "db@example.com",
                Gender = "Other",
                Location = "Db City",
                Interests = "Db",
                DateOfBirth = DateTime.Now.AddYears(-30),
                CreatedAt = DateTime.Now,
                LastActiveAt = DateTime.Now,
                IsVerified = true
            };
            context.UserProfiles.Add(profile);
            context.SaveChanges();
            var retrieved = context.UserProfiles.FirstOrDefaultAsync(u => u.Email == "db@example.com").Result;
            Assert.NotNull(retrieved);
            Assert.Equal("Db User", retrieved.Name);
            Assert.True(retrieved.IsVerified);
        }
    }
}
