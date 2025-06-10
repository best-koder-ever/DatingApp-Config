using System.Reflection;
using Bogus;
using MatchmakingService.Data;
using MatchmakingService.Models;
using Microsoft.EntityFrameworkCore;
using AuthService.Models; // Import the User model
using AuthService.Data; // Import ApplicationDbContext for AuthService
using Microsoft.AspNetCore.Identity; // Added for PasswordHasher
using System.Text;
using System.Net.Http; // Added for HttpClient
using System.Net.Http.Json; // Added for PostAsJsonAsync
using AuthService.DTOs; // Assuming RegisterDto is in this namespace

class Program
{
    private static readonly Dictionary<string, string> DbOptions = new()
    {
        { "1", "Server=127.0.0.1;Port=3307;Database=AuthServiceDb;User=authuser;Password=authuser_password;" },
        { "2", "Server=127.0.0.1;Port=3308;Database=UserServiceDb;User=userservice_user;Password=userservice_user_password;" },
        { "3", "Server=127.0.0.1;Port=3309;Database=MatchmakingServiceDb;User=matchmakingservice_user;Password=matchmakingservice_user_password;" },
        { "4", "Server=127.0.0.1;Port=3310;Database=SwipeServiceDb;User=swipeservice_user;Password=swipeservice_user_password;" }
    };
    private static string _selectedDb = "1"; // Default to AuthServiceDb
    private static string _connectionString = DbOptions[_selectedDb]; // Initialize based on default _selectedDb

    private static CreationMode _userCreationMode = CreationMode.DirectInsert; // Default
    private static string AuthApiServiceUrl = Environment.GetEnvironmentVariable("AUTH_API_URL") ?? "http://localhost:8081"; // Configurable: AuthService URL
    private static string UserServiceApiUrl = "http://localhost:8082"; // Default user-service URL

    private enum CreationMode
    {
        DirectInsert,
        ApiCall
    }

    static async Task Main(string[] args) // Changed to async Task
    {
        // --- Batch mode for automation ---
        if (args.Length > 0)
        {
            int userCount = 0;
            var explicitUsers = new List<RegisterDto>();
            bool useApi = false;
            bool useDirect = false;
            for (int i = 0; i < args.Length; i++)
            {
                switch (args[i])
                {
                    case "--create-users":
                        if (i + 1 < args.Length && int.TryParse(args[i + 1], out int n))
                        {
                            userCount = n;
                            i++;
                        }
                        break;
                    case "--api":
                        useApi = true;
                        break;
                    case "--direct":
                        useDirect = true;
                        break;
                    case "--user":
                        if (i + 1 < args.Length)
                        {
                            var parts = args[i + 1].Split(':');
                            if (parts.Length >= 2)
                            {
                                explicitUsers.Add(new RegisterDto
                                {
                                    Email = parts[0],
                                    Password = parts[1],
                                    ConfirmPassword = parts[1],
                                    Username = parts[0].Split('@')[0],
                                    PhoneNumber = "1234567890"
                                });
                            }
                            i++;
                        }
                        break;
                    case "--user-service-url":
                        if (i + 1 < args.Length)
                        {
                            UserServiceApiUrl = args[i + 1];
                            i++;
                        }
                        break;
                }
            }
            if (useApi) _userCreationMode = CreationMode.ApiCall;
            if (useDirect) _userCreationMode = CreationMode.DirectInsert;
            _selectedDb = "1"; // Always AuthServiceDb for user creation
            _connectionString = DbOptions[_selectedDb];
            // Create explicit users first
            if (explicitUsers.Count > 0)
            {
                if (_userCreationMode == CreationMode.ApiCall)
                {
                    await CreateExplicitUsersViaApiAsync(explicitUsers, seedUserService: true);
                }
                else
                {
                    CreateExplicitUsersDirectly(explicitUsers);
                }
            }
            // Then create random users if requested
            if (userCount > 0)
            {
                if (_userCreationMode == CreationMode.ApiCall)
                {
                    await CreateUsersViaApiAsync(userCount, seedUserService: true);
                }
                else
                {
                    CreateUsersDirectly(userCount);
                }
            }
            Console.WriteLine("Batch mode complete. Exiting.");
            return;
        }

        // END TEMPORARY TEST CODE

        // Original Main method loop:
        while (true)
        {
            Console.Clear();
            Console.WriteLine("========================================");
            Console.WriteLine("|         Test Data Generator          |");
            Console.WriteLine("========================================");
            Console.WriteLine("| 0. Select Target Database            |");
            Console.WriteLine("| 1. Create Users                      |");
            Console.WriteLine("| 2. Create Swipes                     |");
            Console.WriteLine("| 3. Create Mutual Matches             |");
            Console.WriteLine("| 4. Create Messages                   |");
            Console.WriteLine("| 5. Set Database Connection (Custom)  |");
            Console.WriteLine("| 6. Exit                              |");
            Console.WriteLine("| 7. Select User Creation Mode         |"); // New option
            Console.WriteLine("| 8. Create 2 Users via Auth API     |"); // Added new option
            Console.WriteLine("========================================");
            Console.WriteLine($"Current DB: {GetDbName(_selectedDb)}");
            Console.WriteLine($"Current User Creation Mode: {_userCreationMode}"); // Display current mode
            Console.Write("Select an option: ");

            var choice = Console.ReadLine();

            switch (choice)
            {
                case "0":
                    SelectTargetDatabase();
                    break;
                case "1":
                    await CreateUsers(); // Changed to await
                    break;
                case "2":
                    CreateSwipes();
                    break;
                case "3":
                    CreateMutualMatches();
                    break;
                case "4":
                    CreateMessages();
                    break;
                case "5":
                    SetDatabaseConnection();
                    break;
                case "6":
                    Console.WriteLine("Exiting...");
                    return;
                case "7":
                    SelectUserCreationMode(); // New case
                    break;
                case "8": // Added new case
                    _selectedDb = "1"; // Ensure AuthServiceDb is selected
                    _userCreationMode = CreationMode.ApiCall; // Ensure API call mode
                    Console.WriteLine($"Current DB set to: {GetDbName(_selectedDb)}");
                    Console.WriteLine($"Current User Creation Mode set to: {_userCreationMode}");
                    await CreateUsersViaApiAsync(2, seedUserService: true); // Create 2 users via API
                    Console.WriteLine("Finished creating 2 users via API. Press any key to return to menu.");
                    Console.ReadKey();
                    break;
                default:
                    Console.WriteLine("Invalid option. Press any key to try again.");
                    Console.ReadKey();
                    break;
            }
        }
    }

    static void SelectUserCreationMode()
    {
        Console.WriteLine("Select User Creation Mode:");
        Console.WriteLine("1. Direct Database Insert");
        Console.WriteLine("2. API Call");
        Console.Write("Enter choice: ");
        string choice = Console.ReadLine();
        switch (choice)
        {
            case "1":
                _userCreationMode = CreationMode.DirectInsert;
                Console.WriteLine("User creation mode set to Direct Database Insert.");
                break;
            case "2":
                _userCreationMode = CreationMode.ApiCall;
                Console.WriteLine("User creation mode set to API Call.");
                break;
            default:
                Console.WriteLine("Invalid choice.");
                break;
        }
        Console.WriteLine("Returning to main menu...");
        Console.ReadKey();
    }

    static string GetDbName(string dbKey)
    {
        return dbKey switch
        {
            "1" => "AuthServiceDb",
            "2" => "UserServiceDb",
            "3" => "MatchmakingServiceDb",
            "4" => "SwipeServiceDb",
            _ => "Custom/Unknown"
        };
    }

    static bool TestDatabaseConnection(string connectionString)
    {
        try
        {
            var builder = new MySqlConnector.MySqlConnectionStringBuilder(connectionString);
            using var conn = new MySqlConnector.MySqlConnection(builder.ConnectionString);
            conn.Open();
            conn.Close();
            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] Could not connect to database: {ex.Message}");
            return false;
        }
    }

    static void SelectTargetDatabase()
    {
        Console.WriteLine("Select the target database:");
        Console.WriteLine("1. Auth Service DB");
        Console.WriteLine("2. User Service DB");
        Console.WriteLine("3. Matchmaking Service DB");
        Console.WriteLine("4. Swipe Service DB");
        Console.Write("Enter choice: ");
        var dbChoice = Console.ReadLine();
        if (DbOptions.TryGetValue(dbChoice, out var connStr))
        {
            _connectionString = connStr;
            _selectedDb = dbChoice;
            Console.WriteLine($"Target database set to {GetDbName(dbChoice)}!");
            // Test connection before proceeding
            if (!TestDatabaseConnection(_connectionString))
            {
                Console.WriteLine("[ERROR] Database is not available. Please start the database container or check your connection settings.");
            }
            else
            {
                Console.WriteLine("Database connection successful!");
            }
        }
        else
        {
            Console.WriteLine("Invalid choice.");
        }
        Console.WriteLine("Returning to main menu...");
        Console.ReadKey();
    }

    static async Task CreateUsers() // Changed to async Task
    {
        Console.Write("Enter the number of users to create: ");
        if (int.TryParse(Console.ReadLine(), out int userCount))
        {
            if (_userCreationMode == CreationMode.ApiCall)
            {
                await CreateUsersViaApiAsync(userCount);
            }
            else // DirectInsert
            {
                CreateUsersDirectly(userCount);
            }
            Console.WriteLine("Users creation process finished.");
        }
        else
        {
            Console.WriteLine("Invalid number. Press any key to return to the menu.");
        }
        Console.ReadKey();
    }

    static void CreateUsersDirectly(int userCount)
    {
        Console.WriteLine($"Creating {userCount} users directly in {GetDbName(_selectedDb)}...");

        if (_selectedDb == "1") // AuthServiceDb
        {
            var authOptions = new DbContextOptionsBuilder<AuthService.Data.ApplicationDbContext>()
                .UseMySql(_connectionString, new MySqlServerVersion(new Version(8, 0, 28)))
                .Options;
            using var authContext = new AuthService.Data.ApplicationDbContext(authOptions);

            var passwordHasher = new PasswordHasher<AuthService.Models.User>();

            var faker = new Faker<AuthService.Models.User>()
                .RuleFor(u => u.UserName, (f, u) => f.Internet.UserName())
                .RuleFor(u => u.NormalizedUserName, (f, u) => u.UserName.ToUpperInvariant())
                .RuleFor(u => u.Email, (f, u) => f.Internet.Email())
                .RuleFor(u => u.NormalizedEmail, (f, u) => u.Email.ToUpperInvariant())
                .RuleFor(u => u.EmailConfirmed, f => false)
                .RuleFor(u => u.PasswordHash, (f, u) => passwordHasher.HashPassword(u, "P@$$wOrd"))
                .RuleFor(u => u.SecurityStamp, f => Guid.NewGuid().ToString().ToUpperInvariant())
                .RuleFor(u => u.ConcurrencyStamp, f => Guid.NewGuid().ToString())
                .RuleFor(u => u.PhoneNumber, f => f.Phone.PhoneNumber())
                .RuleFor(u => u.PhoneNumberConfirmed, f => false)
                .RuleFor(u => u.TwoFactorEnabled, f => false)
                .RuleFor(u => u.LockoutEnabled, f => true)
                .RuleFor(u => u.LockoutEnd, f => (DateTimeOffset?)null)
                .RuleFor(u => u.AccessFailedCount, f => 0)
                .RuleFor(u => u.DateOfBirth, (f, u) => f.Date.Past(50, DateTime.Now.AddYears(-18)))
                .RuleFor(u => u.Bio, (f, u) => f.Lorem.Sentence(10))
                .RuleFor(u => u.ProfilePicture, (f, u) => $"https://i.pravatar.cc/150?u={u.Email}")
                .RuleFor(u => u.Gender, (f, u) => f.PickRandom(new[] { "Male", "Female", "Other", "Prefer not to say" }))
                .RuleFor(u => u.Location, (f, u) => f.Address.City())
                .RuleFor(u => u.Interests, (f, u) => string.Join(", ", f.Lorem.Words(f.Random.Int(3, 7))))
                .RuleFor(u => u.LastActive, (f, u) => f.Date.Recent(days: 30));

            var users = faker.Generate(userCount);
            authContext.Users.AddRange(users);
            authContext.SaveChanges();
        }
        else
        {
            Console.WriteLine($"User creation for {GetDbName(_selectedDb)} is not implemented with a specific User model for direct insert. Using MatchmakingDbContext as a fallback (may cause errors).");
            // ... (existing fallback logic for other DBs, which might need review)
            var options = new DbContextOptionsBuilder<MatchmakingDbContext>()
                .UseMySql(_connectionString, new MySqlServerVersion(new Version(8, 0, 28)))
                .Options;
            using var context = new MatchmakingDbContext(options);
            var faker = new Faker<User>() // This 'User' is ambiguous. Assuming AuthService.Models.User for properties
                .RuleFor(u => u.UserName, (f, u) => f.Internet.UserName())
                .RuleFor(u => u.Email, (f, u) => f.Internet.Email())
                .RuleFor(u => u.Bio, (f, u) => f.Lorem.Sentence())
                .RuleFor(u => u.ProfilePicture, (f, u) => f.Internet.Avatar())
                .RuleFor(u => u.DateOfBirth, (f, u) => f.Date.Past(30, DateTime.Now.AddYears(-18)))
                .RuleFor(u => u.Gender, (f, u) => f.PickRandom(new[] { "Male", "Female", "Other" }))
                .RuleFor(u => u.Location, (f, u) => f.Address.City())
                .RuleFor(u => u.Interests, (f, u) => string.Join(", ", f.Lorem.Words(3)))
                .RuleFor(u => u.LastActive, (f, u) => f.Date.Recent());
            var users = faker.Generate(userCount);
            Console.WriteLine("Fallback user creation logic needs review for correct DbContext and User model.");
        }
    }

    static async Task CreateUsersViaApiAsync(int userCount, bool seedUserService = false)
    {
        Console.WriteLine($"Creating {userCount} users via API call to AuthService ({AuthApiServiceUrl})...");
        if (_selectedDb != "1")
        {
            Console.WriteLine("API user creation is currently only configured for AuthServiceDb (selectedDb = 1).");
            Console.WriteLine("Please select AuthServiceDb (option 1) as the target database to use API creation mode.");
            return;
        }
        using var httpClient = new HttpClient();
        for (int i = 0; i < userCount; i++)
        {
            var fakerForDto = new Bogus.Faker<RegisterDto>()
                .RuleFor(dto => dto.Username, f => f.Internet.UserName())
                .RuleFor(dto => dto.Email, f => f.Internet.Email())
                .RuleFor(dto => dto.Password, f => "P@$$wOrd123!")
                .RuleFor(dto => dto.ConfirmPassword, (f, dto) => dto.Password)
                .RuleFor(dto => dto.PhoneNumber, f => f.Phone.PhoneNumber())
                .RuleFor(dto => dto.ProfilePicture, (f, dto) => $"https://i.pravatar.cc/150?u={dto.Email}");
            var registerDto = fakerForDto.Generate();
            try
            {
                var response = await httpClient.PostAsJsonAsync($"{AuthApiServiceUrl}/api/auth/register", registerDto);
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Successfully created user: {registerDto.Username} via API.");
                    if (seedUserService)
                    {
                        var token = await LoginAndGetJwtAsync(registerDto.Email, registerDto.Password);
                        if (token != null)
                        {
                            var ok = await PostUserProfileAsync(token, registerDto.Username, "Test user bio", registerDto.ProfilePicture, "Testing, Automation");
                            if (ok)
                                Console.WriteLine($"Seeded user profile for {registerDto.Email} in user-service.");
                            else
                                Console.WriteLine($"Failed to seed user profile for {registerDto.Email} in user-service.");
                        }
                        else
                        {
                            Console.WriteLine($"Failed to login for {registerDto.Email} to seed user-service profile.");
                        }
                    }
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Failed to create user {registerDto.Username} via API. Status: {response.StatusCode}, Error: {errorContent}");
                }
            }
            catch (HttpRequestException ex)
            {
                Console.WriteLine($"API request failed for user {registerDto.Username}: {ex.Message}. Ensure AuthService is running at {AuthApiServiceUrl}.");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception while calling API for user {registerDto.Username}: {ex.Message}");
            }
        }
    }

    // --- UserService profile seeding helpers ---
    private static async Task<string?> LoginAndGetJwtAsync(string email, string password)
    {
        using var httpClient = new HttpClient();
        var loginPayload = new { email, password };
        var response = await httpClient.PostAsJsonAsync($"{AuthApiServiceUrl}/api/Auth/login", loginPayload);
        if (!response.IsSuccessStatusCode) return null;
        var json = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        return json != null && json.ContainsKey("token") ? json["token"]?.ToString() : null;
    }

    private static async Task<bool> PostUserProfileAsync(string token, string name, string bio, string profilePictureUrl, string preferences)
    {
        using var httpClient = new HttpClient();
        httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {token}");
        var profile = new
        {
            name,
            bio,
            profilePictureUrl,
            preferences
        };
        var response = await httpClient.PostAsJsonAsync($"{UserServiceApiUrl}/api/UserProfiles", profile);
        return response.IsSuccessStatusCode;
    }

    static async Task CreateExplicitUsersViaApiAsync(List<RegisterDto> users, bool seedUserService = false)
    {
        using var httpClient = new HttpClient();
        foreach (var user in users)
        {
            if (string.IsNullOrWhiteSpace(user.ProfilePicture))
                user.ProfilePicture = $"https://i.pravatar.cc/150?u={user.Email}";
            bool registered = false;
            try
            {
                var response = await httpClient.PostAsJsonAsync($"{AuthApiServiceUrl}/api/auth/register", user);
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Successfully created user: {user.Email} via API.");
                    registered = true;
                }
                else
                {
                    var errorContent = await response.Content.ReadAsStringAsync();
                    Console.WriteLine($"Failed to create user {user.Email} via API. Status: {response.StatusCode}, Error: {errorContent}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception while calling API for user {user.Email}: {ex.Message}");
            }
            // Always try to seed user-service profile if requested
            if (seedUserService)
            {
                var token = await LoginAndGetJwtAsync(user.Email, user.Password);
                if (token != null)
                {
                    var ok = await PostUserProfileAsync(token, user.Username, "Test user bio", user.ProfilePicture, "Testing, Automation");
                    if (ok)
                        Console.WriteLine($"Seeded user profile for {user.Email} in user-service.");
                    else
                        Console.WriteLine($"Failed to seed user profile for {user.Email} in user-service.");
                }
                else
                {
                    Console.WriteLine($"Failed to login for {user.Email} to seed user-service profile.");
                }
            }
        }
    }

    static void CreateExplicitUsersDirectly(List<RegisterDto> users)
    {
        var authOptions = new DbContextOptionsBuilder<AuthService.Data.ApplicationDbContext>()
            .UseMySql(_connectionString, new MySqlServerVersion(new Version(8, 0, 28)))
            .Options;
        using var authContext = new AuthService.Data.ApplicationDbContext(authOptions);
        var passwordHasher = new PasswordHasher<AuthService.Models.User>();
        foreach (var dto in users)
        {
            var user = new AuthService.Models.User
            {
                UserName = dto.Username,
                NormalizedUserName = dto.Username.ToUpperInvariant(),
                Email = dto.Email,
                NormalizedEmail = dto.Email.ToUpperInvariant(),
                EmailConfirmed = true,
                PhoneNumber = dto.PhoneNumber,
                PhoneNumberConfirmed = true,
                SecurityStamp = Guid.NewGuid().ToString().ToUpperInvariant(),
                ConcurrencyStamp = Guid.NewGuid().ToString(),
                DateOfBirth = DateTime.Now.AddYears(-25),
                Bio = "Test user bio",
                ProfilePicture = $"https://i.pravatar.cc/150?u={dto.Email}",
                Gender = "Other",
                Location = "Test City",
                Interests = "Testing",
                LastActive = DateTime.Now
            };
            user.PasswordHash = passwordHasher.HashPassword(user, dto.Password);
            authContext.Users.Add(user);
            Console.WriteLine($"Created user {dto.Email} directly in DB.");
        }
        authContext.SaveChanges();
    }

    // --- STUBS for missing menu methods to fix build ---
    static void CreateSwipes() { Console.WriteLine("[STUB] CreateSwipes not implemented."); Console.ReadKey(); }
    static void CreateMutualMatches() { Console.WriteLine("[STUB] CreateMutualMatches not implemented."); Console.ReadKey(); }
    static void CreateMessages() { Console.WriteLine("[STUB] CreateMessages not implemented."); Console.ReadKey(); }
    static void SetDatabaseConnection() { Console.WriteLine("[STUB] SetDatabaseConnection not implemented."); Console.ReadKey(); }
}
