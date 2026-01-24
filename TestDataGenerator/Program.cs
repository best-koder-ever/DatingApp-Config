using System.Reflection;
using Bogus;
using MatchmakingService.Data;
using MatchmakingService.Models;
using Microsoft.EntityFrameworkCore;
using AuthService.Models; // Import the User model
using AuthService.Data; // Import ApplicationDbContext for AuthService
using Microsoft.AspNetCore.Identity; // Added for PasswordHasher
using System.Text;
using System.Net;
using System.Net.Http; // Added for HttpClient
using System.Net.Http.Headers;
using System.Net.Http.Json; // Added for PostAsJsonAsync
using AuthService.DTOs; // Assuming RegisterDto is in this namespace
using UserService.Data; // For ApplicationDbContext
using UserService.Models; // For UserProfile
using System.Globalization;
using System.Linq;
using System.Text.Json; // Added for configuration parsing
using TestDataGenerator.Profiles; // Added for demo profiles

class Program
{
    // Environment configuration
    private static EnvironmentConfig? _config;
    private static string _environment = "local"; // Default environment
    
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
    private static string UserServiceApiUrl = "http://localhost:8082"; // Default UserService URL

    private enum CreationMode
    {
        DirectInsert,
        ApiCall
    }

    static async Task Main(string[] args) // Changed to async Task
    {
        Console.WriteLine("🎯 TestDataGenerator - Enhanced with Environment Support");
        Console.WriteLine("======================================================");
        
        // Load environment configuration
        await LoadEnvironmentConfig(args);
        
        // --- Batch mode for automation ---
        if (args.Length > 0)
        {
            int userCount = 0;
            var explicitUsers = new List<RegisterDto>();
            bool useApi = false;
            bool useDirect = false;
            bool runScenarios = false;
            
            for (int i = 0; i < args.Length; i++)
            {
                switch (args[i])
                {
                    case "--environment":
                        if (i + 1 < args.Length)
                        {
                            _environment = args[i + 1];
                            await LoadEnvironmentConfig(args);
                            i++;
                        }
                        break;
                    case "--run-scenarios":
                        runScenarios = true;
                        break;
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
                    case "--UserService-url":
                        if (i + 1 < args.Length)
                        {
                            UserServiceApiUrl = args[i + 1];
                            i++;
                        }
                        break;
                    case "--create-fixed-testuser":
                        // Always add a fixed test user
                        explicitUsers.Add(new RegisterDto
                        {
                            Email = "testuser@example.com",
                            Password = "TestPassword123!",
                            ConfirmPassword = "TestPassword123!",
                            Username = "testuser",
                            PhoneNumber = "1234567890"
                        });
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
                // Use demo profile users in demo environment
                if (_environment == "demo" && _config?.DataProfile?.UserCount > 0)
                {
                    Console.WriteLine("🎭 Creating demo profile users...");
                    var sharedDemoUsers = DemoProfile.GetDemoUsers().Take(userCount).ToList();
                    
                    // Convert to AuthService.DTOs.RegisterDto
                    var demoUsers = sharedDemoUsers.Select(u => new AuthService.DTOs.RegisterDto
                    {
                        Username = u.Username,
                        Email = u.Email,
                        Password = u.Password,
                        ConfirmPassword = u.ConfirmPassword,
                        PhoneNumber = u.PhoneNumber,
                        ProfilePicture = u.ProfilePicture
                    }).ToList();
                    
                    if (_userCreationMode == CreationMode.ApiCall)
                    {
                        await CreateExplicitUsersViaApiAsync(demoUsers, seedUserService: true);
                    }
                    else
                    {
                        CreateExplicitUsersDirectly(demoUsers);
                    }
                }
                else
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
            }
            
            // Run demo scenarios if requested
            if (runScenarios)
            {
                await RunDemoScenarios();
            }
            
            Console.WriteLine($"✅ Batch mode complete for {_environment} environment. Exiting.");
            return;
        }

        // END TEMPORARY TEST CODE

        // Show status dashboard immediately on startup
        ShowStatusOverview();

        // Original Main method loop:
        while (true)
        {
            Console.Clear();
            ShowStatusOverview();
            Console.WriteLine("========================================");
            Console.WriteLine("|         Test Data Generator          |");

            Console.WriteLine("========================================");
            Console.WriteLine("| R. Reset All Databases               |");
            Console.WriteLine("| 0. Select Target Database            |");
            Console.WriteLine("| 1. Create Users                      |");
            Console.WriteLine("| 2. Create Swipes                     |");
            Console.WriteLine("| 3. Create Mutual Matches             |");
            Console.WriteLine("| 4. Create Messages                   |");
            Console.WriteLine("| 5. Set Database Connection (Custom)  |");
            Console.WriteLine("| S. Show Status Overview              |");
            Console.WriteLine("| 7. Select User Creation Mode         |");
            Console.WriteLine("| 8. Create 2 Users via Auth API       |");
            Console.WriteLine("| 9. Create Users in Auth & User Svc   |");
            Console.WriteLine("| 6. Exit                              |");
            Console.WriteLine("========================================");
            Console.WriteLine($"Current DB: {GetDbName(_selectedDb)}");
            Console.WriteLine($"Current User Creation Mode: {_userCreationMode}");
            Console.Write("Select an option: ");

            var choice = Console.ReadLine();

            switch (choice)
            {
                case "R":
                case "r":
                    await ResetAllDatabasesMenu();
                    break;
                case "0":
                    SelectTargetDatabase();
                    break;
                case "1":
                    await CheckResetPromptAndCreateUsers();
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
                case "S":
                case "s":
                    ShowStatusOverview();
                    break;
                case "6":
                    Console.WriteLine("Exiting...");
                    return;
                case "7":
                    SelectUserCreationMode();
                    break;
                case "8":
                    _selectedDb = "1";
                    _userCreationMode = CreationMode.ApiCall;
                    Console.WriteLine($"Current DB set to: {GetDbName(_selectedDb)}");
                    Console.WriteLine($"Current User Creation Mode set to: {_userCreationMode}");
                    await CheckResetPromptAndCreateUsers(2, true);
                    Console.WriteLine("Finished creating 2 users via API. Press any key to return to menu.");
                    Console.ReadKey();
                    break;
                case "9":
                    await CheckResetPromptAndCreateUsersInAuthAndUserServiceMenu();
                    break;
                default:
                    Console.WriteLine("Invalid option. Press any key to try again.");
                    Console.ReadKey();
                    break;
            }
        }
    }

    // Show status overview for AuthServiceDb and UserServiceDb
    static void ShowStatusOverview()
    {
        Console.Clear();
        Console.WriteLine("========== STATUS DASHBOARD ==========");
        var results = new List<(string Db, string Table, int? Count, string? Error)>();
        results.Add(GetDbUserCount("AuthServiceDb", DbOptions["1"], "AspNetUsers"));
        results.Add(GetDbUserCount("UserServiceDb", DbOptions["2"], "UserProfiles"));
        // Optionally add more DBs here

        Console.WriteLine("|   Database         |   Table         |   Count   |");
        Console.WriteLine("---------------------------------------------------");
        foreach (var r in results)
        {
            if (r.Error == null)
            {
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine($"| {r.Db,-17} | {r.Table,-14} | {r.Count,8}   |");
            }
            else
            {
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine($"| {r.Db,-17} | {r.Table,-14} | ERROR    |");
                Console.WriteLine($"  [ERROR] {r.Error}");
            }
            Console.ResetColor();
        }
        Console.WriteLine("=====================================");
        Console.WriteLine("Press any key to return to menu.");
        Console.ReadKey();
    }

    static (string Db, string Table, int? Count, string? Error) GetDbUserCount(string dbName, string connectionString, string tableName)
    {
        try
        {
            using var conn = new MySqlConnector.MySqlConnection(connectionString);
            conn.Open();
            using var cmd = conn.CreateCommand();
            cmd.CommandText = $"SELECT COUNT(*) FROM {tableName}";
            var count = Convert.ToInt32(cmd.ExecuteScalar());
            return (dbName, tableName, count, null);
        }
        catch (Exception ex)
        {
            return (dbName, tableName, null, ex.Message);
        }
    }
    // Menu option to reset all databases
    public static async Task ResetAllDatabasesMenu()
    {
        try
        {
            Console.WriteLine("This will reset (drop and recreate/migrate) all service databases. Are you sure? (y/n)");
            var confirm = Console.ReadLine();
            if (confirm?.ToLower() == "y")
            {
                await ResetAllDatabases();
                Console.WriteLine("All databases have been reset. Press any key to return to menu.");
            }
            else
            {
                Console.WriteLine("Reset cancelled. Press any key to return to menu.");
            }
        }
        catch (Exception ex)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[ERROR] Exception during database reset: {ex.Message}\n{ex.StackTrace}");
            Console.ResetColor();
        }
        Console.ReadKey();
    }

    // Actually reset all DBs (calls shell scripts or dotnet ef database update for each service)
    public static async Task ResetAllDatabases()
    {
        // You can replace these with your actual reset/migrate commands or scripts
        var resetCommands = new[]
        {
            "cd ../../AuthService && dotnet ef database drop -f && dotnet ef database update",
            "cd ../../UserService && dotnet ef database drop -f && dotnet ef database update",
            "cd ../../MatchmakingService && dotnet ef database drop -f && dotnet ef database update",
            "cd ../../swipe-service && dotnet ef database drop -f && dotnet ef database update"
        };
        foreach (var cmd in resetCommands)
        {
            try
            {
                var psi = new System.Diagnostics.ProcessStartInfo("bash", $"-c \"{cmd}\"")
                {
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                using var process = System.Diagnostics.Process.Start(psi);
                if (process != null)
                {
                    string output = await process.StandardOutput.ReadToEndAsync();
                    string error = await process.StandardError.ReadToEndAsync();
                    process.WaitForExit();
                    Console.WriteLine($"[Reset] {cmd}\n{output}\n{error}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"[ERROR] Failed to reset DB with command: {cmd}\n{ex.Message}");
            }
        }
    }

    // Prompt to reset DBs before creating users
    static async Task CheckResetPromptAndCreateUsers(int userCount = -1, bool seedUserService = false)
    {
        try
        {
            Console.Write("Do you want to reset all databases before creating users? (y/n): ");
            var input = Console.ReadLine();
            if (input?.ToLower() == "y")
            {
                await ResetAllDatabases();
            }
            if (userCount > 0)
            {
                if (_userCreationMode == CreationMode.ApiCall)
                    await CreateUsersViaApiAsync(userCount, seedUserService);
                else
                    CreateUsersDirectly(userCount);
            }
            else
            {
                await CreateUsers();
            }
        }
        catch (Exception ex)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[ERROR] Exception during user creation: {ex.Message}\n{ex.StackTrace}");
            Console.ResetColor();
        }
    }

    // Prompt to reset DBs before creating users in both Auth & User Service
    static async Task CheckResetPromptAndCreateUsersInAuthAndUserServiceMenu()
    {
        try
        {
            Console.Write("Do you want to reset all databases before creating users? (y/n): ");
            var input = Console.ReadLine();
            if (input?.ToLower() == "y")
            {
                await ResetAllDatabases();
            }
            await CreateUsersInAuthAndUserServiceMenu();
        }
        catch (Exception ex)
        {
            Console.ForegroundColor = ConsoleColor.Red;
            Console.WriteLine($"[ERROR] Exception during user creation in both services: {ex.Message}\n{ex.StackTrace}");
            Console.ResetColor();
        }
    }

    // New menu option for creating users in both Auth and User Service
    public static async Task CreateUsersInAuthAndUserServiceMenu()
    {
        Console.Write("Enter the number of users to create in both Auth and User Service: ");
        if (int.TryParse(Console.ReadLine(), out int userCount) && userCount > 0)
        {
            await CreateUsersViaApiAsync(userCount, seedUserService: true);
            Console.WriteLine($"Created {userCount} users in both Auth and User Service. Press any key to return to menu.");
        }
        else
        {
            Console.WriteLine("Invalid number. Press any key to return to the menu.");
        }
        Console.ReadKey();
    }

    static void SelectUserCreationMode()
    {
        Console.WriteLine("Select User Creation Mode:");
        Console.WriteLine("1. Direct Database Insert");
        Console.WriteLine("2. API Call");
        Console.Write("Enter choice: ");
        string? choice = Console.ReadLine();
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
        if (!string.IsNullOrEmpty(dbChoice) && DbOptions.TryGetValue(dbChoice, out var connStr))
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

        try
        {
            if (_selectedDb == "1") // AuthServiceDb
            {
                var authOptions = new DbContextOptionsBuilder<AuthService.Data.ApplicationDbContext>()
                    .UseMySql(_connectionString, new MySqlServerVersion(new Version(8, 0, 28)))
                    .Options;
                using var authContext = new AuthService.Data.ApplicationDbContext(authOptions);

                var passwordHasher = new PasswordHasher<AuthService.Models.User>();

                var faker = new Faker<AuthService.Models.User>()
                    .RuleFor(u => u.UserName, (f, u) => f.Internet.UserName())
                    .RuleFor(u => u.NormalizedUserName, (f, u) => u.UserName?.ToUpperInvariant())
                    .RuleFor(u => u.Email, (f, u) => f.Internet.Email())
                    .RuleFor(u => u.NormalizedEmail, (f, u) => u.Email?.ToUpperInvariant())
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
                    .RuleFor(u => u.LastActive, (f, u) => f.Date.Recent(30));

                var users = faker.Generate(userCount);
                authContext.Users.AddRange(users);
                authContext.SaveChanges();
                Console.WriteLine($"Created {userCount} users directly in AuthServiceDb.");
            }
            else if (_selectedDb == "2") // UserServiceDb direct insert
            {
                var options = new DbContextOptionsBuilder<UserService.Data.ApplicationDbContext>()
                    .UseMySql(_connectionString, new MySqlServerVersion(new Version(8, 0, 28)))
                    .Options;
                using var context = new UserService.Data.ApplicationDbContext(options);
                var faker = new Faker<UserService.Models.UserProfile>()
                    .RuleFor(u => u.Name, (f, u) => f.Name.FullName())
                    .RuleFor(u => u.Bio, (f, u) => f.Lorem.Sentence(10))
                    .RuleFor(u => u.ProfilePictureUrl, (f, u) => $"https://i.pravatar.cc/150?u={f.Internet.Email()}")
                    .RuleFor(u => u.Preferences, (f, u) => string.Join(", ", f.Lorem.Words(5)))
                    .RuleFor(u => u.Email, (f, u) => f.Internet.Email())
                    .RuleFor(u => u.Gender, (f, u) => f.PickRandom(new[] { "Male", "Female", "Other" }))
                    .RuleFor(u => u.Location, (f, u) => f.Address.City())
                    .RuleFor(u => u.Interests, (f, u) => string.Join(", ", f.Lorem.Words(3)))
                    .RuleFor(u => u.DateOfBirth, (f, u) => f.Date.Past(30, DateTime.Now.AddYears(-18)))
                    .RuleFor(u => u.CreatedAt, (f, u) => DateTime.Now)
                    .RuleFor(u => u.LastActiveAt, (f, u) => f.Date.Recent(30))
                    .RuleFor(u => u.IsVerified, (f, u) => false);
                var profiles = faker.Generate(userCount);
                context.UserProfiles.AddRange(profiles);
                context.SaveChanges();
                Console.WriteLine($"Created {userCount} user profiles directly in UserServiceDb.");
            }
            else
            {
                Console.WriteLine($"User creation for {GetDbName(_selectedDb)} is not implemented for direct insert.");
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"[ERROR] Failed to create users: {ex.Message}");
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
                                Console.WriteLine($"Seeded user profile for {registerDto.Email} in UserService.");
                            else
                                Console.WriteLine($"Failed to seed user profile for {registerDto.Email} in UserService.");
                        }
                        else
                        {
                            Console.WriteLine($"Failed to login for {registerDto.Email} to seed UserService profile.");
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
            try
            {
                var response = await httpClient.PostAsJsonAsync($"{AuthApiServiceUrl}/api/auth/register", user);
                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine($"Successfully created user: {user.Email} via API.");
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
            // Always try to seed UserService profile if requested
            if (seedUserService)
            {
                var token = await LoginAndGetJwtAsync(user.Email, user.Password);
                if (token != null)
                {
                    var ok = await PostUserProfileAsync(token, user.Username, "Test user bio", user.ProfilePicture, "Testing, Automation");
                    if (ok)
                        Console.WriteLine($"Seeded user profile for {user.Email} in UserService.");
                    else
                        Console.WriteLine($"Failed to seed user profile for {user.Email} in UserService.");
                }
                else
                {
                    Console.WriteLine($"Failed to login for {user.Email} to seed UserService profile.");
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

    // --- Environment Configuration Methods ---
    static async Task LoadEnvironmentConfig(string[] args)
    {
        try
        {
            string configPath = $"Configurations/{_environment}.json";
            
            if (File.Exists(configPath))
            {
                Console.WriteLine($"📋 Loading configuration for environment: {_environment}");
                string json = await File.ReadAllTextAsync(configPath);
                _config = JsonSerializer.Deserialize<EnvironmentConfig>(json, new JsonSerializerOptions 
                { 
                    PropertyNameCaseInsensitive = true 
                });
                
                // Update connection strings with environment suffix
                UpdateConnectionStringsForEnvironment();
                
                // Update API URLs from config
                if (_config?.ApiEndpoints != null)
                {
                    AuthApiServiceUrl = _config.ApiEndpoints.ContainsKey("AuthService") 
                        ? _config.ApiEndpoints["AuthService"] 
                        : AuthApiServiceUrl;
                    UserServiceApiUrl = _config.ApiEndpoints.ContainsKey("UserService") 
                        ? _config.ApiEndpoints["UserService"] 
                        : UserServiceApiUrl;
                }
                
                Console.WriteLine($"✅ Configuration loaded for {_environment} environment");
            }
            else
            {
                Console.WriteLine($"⚠️  No configuration found for {_environment}, using defaults");
                _config = new EnvironmentConfig { Environment = _environment };
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error loading configuration: {ex.Message}");
            _config = new EnvironmentConfig { Environment = _environment };
        }
    }
    
    static void UpdateConnectionStringsForEnvironment()
    {
        if (_config?.DatabaseConnection != null)
        {
            // Use specific database connection from config
            _connectionString = _config.DatabaseConnection;
            DbOptions["1"] = _connectionString; // Update auth service connection
        }
        else if (_config?.DatabaseSuffix != null)
        {
            var updatedDbOptions = new Dictionary<string, string>();
            foreach (var kvp in DbOptions)
            {
                string connectionString = kvp.Value;
                // Update database names with environment suffix
                connectionString = connectionString.Replace("Database=AuthServiceDb", $"Database=auth_service{_config.DatabaseSuffix}");
                connectionString = connectionString.Replace("Database=UserServiceDb", $"Database=user_service{_config.DatabaseSuffix}");
                connectionString = connectionString.Replace("Database=MatchmakingServiceDb", $"Database=matchmaking_service{_config.DatabaseSuffix}");
                connectionString = connectionString.Replace("Database=SwipeServiceDb", $"Database=swipe_service{_config.DatabaseSuffix}");
                updatedDbOptions[kvp.Key] = connectionString;
            }
            
            // Update the DbOptions dictionary
            DbOptions.Clear();
            foreach (var kvp in updatedDbOptions)
            {
                DbOptions[kvp.Key] = kvp.Value;
            }
            
            _connectionString = DbOptions[_selectedDb];
        }
    }
    
    static async Task RunDemoScenarios()
    {
        if (_environment != "demo")
        {
            Console.WriteLine("❌ Demo scenarios can only be run in demo environment");
            return;
        }

        var options = SignupScenarioOptions.From(_config);
        using var httpClient = new HttpClient
        {
            Timeout = options.RequestTimeout
        };
        httpClient.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

    Console.WriteLine("🎬 Running automated signup -> match scenario...");
        var scenario = new SignupToMatchScenario(httpClient, options);
        var result = await scenario.ExecuteAsync();

        foreach (var log in result.Logs)
        {
            Console.WriteLine(log);
        }

    if (result.IsSuccess)
        {
            var matchText = result.MatchId.HasValue
                ? result.MatchId.Value.ToString(CultureInfo.InvariantCulture)
                : "unknown";
            Console.WriteLine($"✅ Scenario completed successfully. MatchId: {matchText}");
        }
        else
        {
            Console.WriteLine("❌ Scenario failed.");
            Console.WriteLine($"Reason: {result.ErrorMessage}");
        }
    }

    private sealed record SignupScenarioOptions(
        string KeycloakBaseUrl,
        string KeycloakRealm,
        string KeycloakAdminUser,
        string KeycloakAdminPassword,
        string ClientId,
        string ClientScopes,
        string DemoUserPassword,
        string UserServiceBaseUrl,
        string UserServiceHealthUrl,
        string SwipeServiceBaseUrl,
        string SwipeServiceHealthUrl,
        string MatchmakingServiceBaseUrl,
        string MatchmakingHealthUrl,
        string GatewayHealthUrl,
        TimeSpan RequestTimeout)
    {
        public static SignupScenarioOptions From(EnvironmentConfig? config)
        {
            static string ResolveEndpoint(EnvironmentConfig? cfg, string key, string? environmentValue, string fallback)
            {
                if (!string.IsNullOrWhiteSpace(environmentValue))
                {
                    return environmentValue.TrimEnd('/');
                }

                if (cfg?.ApiEndpoints != null && cfg.ApiEndpoints.TryGetValue(key, out var configured) && !string.IsNullOrWhiteSpace(configured))
                {
                    return configured.TrimEnd('/');
                }

                return fallback.TrimEnd('/');
            }

            var keycloakBase = (Environment.GetEnvironmentVariable("KEYCLOAK_URL") ?? "http://localhost:8090").TrimEnd('/');
            var keycloakRealm = Environment.GetEnvironmentVariable("KEYCLOAK_REALM") ?? "DatingApp";
            var keycloakAdmin = Environment.GetEnvironmentVariable("KEYCLOAK_ADMIN") ?? "admin";
            var keycloakAdminPassword = Environment.GetEnvironmentVariable("KEYCLOAK_ADMIN_PASSWORD") ?? "admin";
            var clientId = Environment.GetEnvironmentVariable("KEYCLOAK_CLIENT_ID") ?? "dejtingapp-flutter";
            var clientScopes = Environment.GetEnvironmentVariable("KEYCLOAK_CLIENT_SCOPES") ?? "openid profile email offline_access";
            var demoPassword = Environment.GetEnvironmentVariable("DEMO_USER_PASSWORD") ?? "Demo123!";

            var userServiceBase = ResolveEndpoint(config, "UserService", Environment.GetEnvironmentVariable("USER_SERVICE_URL"), "http://localhost:8082");
            var swipeServiceBase = ResolveEndpoint(config, "SwipeService", Environment.GetEnvironmentVariable("SWIPE_SERVICE_URL"), "http://localhost:8087");
            var matchmakingBase = ResolveEndpoint(config, "MatchmakingService", Environment.GetEnvironmentVariable("MATCHMAKING_SERVICE_URL"), "http://localhost:8083");

            var gatewayHealth = Environment.GetEnvironmentVariable("DATINGAPP_GATEWAY_HEALTH") ?? "http://localhost:8080/health";

            var userServiceApi = $"{userServiceBase}/api/UserProfiles";
            var swipeServiceApi = $"{swipeServiceBase}/api/Swipes";
            var matchmakingApi = $"{matchmakingBase}/api/Matchmaking";

            var userServiceHealth = $"{userServiceBase}/health";
            var swipeServiceHealth = $"{swipeServiceBase}/health";
            var matchmakingHealth = $"{matchmakingBase}/health";

            return new SignupScenarioOptions(
                KeycloakBaseUrl: keycloakBase,
                KeycloakRealm: keycloakRealm,
                KeycloakAdminUser: keycloakAdmin,
                KeycloakAdminPassword: keycloakAdminPassword,
                ClientId: clientId,
                ClientScopes: clientScopes,
                DemoUserPassword: demoPassword,
                UserServiceBaseUrl: userServiceApi,
                UserServiceHealthUrl: userServiceHealth,
                SwipeServiceBaseUrl: swipeServiceApi,
                SwipeServiceHealthUrl: swipeServiceHealth,
                MatchmakingServiceBaseUrl: matchmakingApi,
                MatchmakingHealthUrl: matchmakingHealth,
                GatewayHealthUrl: gatewayHealth,
                RequestTimeout: TimeSpan.FromSeconds(20));
        }
    }

    private sealed class SignupToMatchScenario
    {
        private readonly HttpClient _httpClient;
        private readonly SignupScenarioOptions _options;
        private readonly JsonSerializerOptions _jsonOptions = new() { PropertyNameCaseInsensitive = true };
        private readonly Random _random = new();

        public SignupToMatchScenario(HttpClient httpClient, SignupScenarioOptions options)
        {
            _httpClient = httpClient;
            _options = options;
        }

        public async Task<ScenarioResult> ExecuteAsync()
        {
            var logs = new List<string>();
            try
            {
                await EnsureHealthAsync(logs);

                var adminToken = await AcquireAdminTokenAsync(logs);
                var primaryUser = await ProvisionKeycloakUserAsync("signup_demo_a", adminToken, logs);
                var secondaryUser = await ProvisionKeycloakUserAsync("signup_demo_b", adminToken, logs);

                primaryUser.Token = await AcquireUserTokenAsync(primaryUser.Username, primaryUser.Password, logs);
                secondaryUser.Token = await AcquireUserTokenAsync(secondaryUser.Username, secondaryUser.Password, logs);

                primaryUser.ProfileId = await CreateUserProfileAsync(primaryUser, logs);
                secondaryUser.ProfileId = await CreateUserProfileAsync(secondaryUser, logs);

                await RecordSwipeAsync(primaryUser.ProfileId!.Value, secondaryUser.ProfileId!.Value, primaryUser.Token!, logs);
                await RecordSwipeAsync(secondaryUser.ProfileId!.Value, primaryUser.ProfileId!.Value, secondaryUser.Token!, logs);

                var matchId = await WaitForMatchAsync(primaryUser.ProfileId.Value, primaryUser.Token!, logs);

                return ScenarioResult.Success(matchId, logs);
            }
            catch (Exception ex)
            {
                logs.Add($"[ERROR] {ex.Message}");
                return ScenarioResult.Failure(ex.Message, logs);
            }
        }

        private async Task EnsureHealthAsync(List<string> logs)
        {
            var checks = new List<(string Name, string Url)>
            {
                ("Keycloak", $"{_options.KeycloakBaseUrl}/realms/{_options.KeycloakRealm}"),
                ("UserService", _options.UserServiceHealthUrl),
                ("SwipeService", _options.SwipeServiceHealthUrl),
                ("MatchmakingService", _options.MatchmakingHealthUrl),
                ("Gateway", _options.GatewayHealthUrl)
            };

            foreach (var (name, url) in checks)
            {
                if (string.IsNullOrWhiteSpace(url))
                {
                    continue;
                }

                try
                {
                    using var response = await _httpClient.GetAsync(url);
                    if (!response.IsSuccessStatusCode)
                    {
                        var status = (int)response.StatusCode;
                        throw new InvalidOperationException($"{name} health returned {status}");
                    }
                    logs.Add($"[HEALTH] {name}: {(int)response.StatusCode}");
                }
                catch (Exception ex)
                {
                    throw new InvalidOperationException($"{name} health check failed: {ex.Message}", ex);
                }
            }
        }

        private async Task<string> AcquireAdminTokenAsync(List<string> logs)
        {
            var data = new Dictionary<string, string>
            {
                ["grant_type"] = "password",
                ["client_id"] = "admin-cli",
                ["username"] = _options.KeycloakAdminUser,
                ["password"] = _options.KeycloakAdminPassword
            };

            using var response = await _httpClient.PostAsync(
                $"{_options.KeycloakBaseUrl}/realms/master/protocol/openid-connect/token",
                new FormUrlEncodedContent(data));

            if (!response.IsSuccessStatusCode)
            {
                var status = (int)response.StatusCode;
                var body = await response.Content.ReadAsStringAsync();
                throw new InvalidOperationException($"Failed to acquire Keycloak admin token ({status}): {body}");
            }

            var payload = await response.Content.ReadAsStringAsync();
            using var document = JsonDocument.Parse(payload);
            var token = document.RootElement.TryGetProperty("access_token", out var accessToken)
                ? accessToken.GetString()
                : null;

            if (string.IsNullOrWhiteSpace(token))
            {
                throw new InvalidOperationException("Keycloak admin token missing access_token field");
            }

            logs.Add("[KEYCLOAK] Admin token acquired");
            return token;
        }

        private async Task<ScenarioUser> ProvisionKeycloakUserAsync(string prefix, string adminToken, List<string> logs)
        {
            var suffix = Guid.NewGuid().ToString("N")[..8];
            var username = $"{prefix}_{suffix}".ToLowerInvariant();
            var email = $"{username}@demo.local";

            var (firstName, lastName, gender, preferences) = prefix.Equals("signup_demo_b", StringComparison.OrdinalIgnoreCase)
                ? ("Casey", "Scenario", "Female", "Male")
                : ("Avery", "Scenario", "Male", "Female");

            var user = new ScenarioUser(username, email, _options.DemoUserPassword, firstName, lastName, gender, preferences);

            var payload = new
            {
                username = user.Username,
                email = user.Email,
                firstName = user.FirstName,
                lastName = user.LastName,
                enabled = true,
                emailVerified = true,
                realmRoles = new[] { "user" }
            };

            var request = new HttpRequestMessage(HttpMethod.Post, $"{_options.KeycloakBaseUrl}/admin/realms/{_options.KeycloakRealm}/users")
            {
                Content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json")
            };
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", adminToken);

            using var response = await _httpClient.SendAsync(request);
            if (response.StatusCode == HttpStatusCode.Created)
            {
                user.KeycloakId = ExtractTrailingSegment(response.Headers.Location?.ToString());
                logs.Add($"[KEYCLOAK] Created user {user.Username}");
            }
            else if (response.StatusCode == HttpStatusCode.Conflict)
            {
                user.KeycloakId = await FindKeycloakUserAsync(user.Username, adminToken);
                logs.Add($"[KEYCLOAK] Reusing existing user {user.Username}");
            }
            else
            {
                var body = await response.Content.ReadAsStringAsync();
                var status = (int)response.StatusCode;
                throw new InvalidOperationException($"Keycloak user creation failed ({status}): {body}");
            }

            user.KeycloakId ??= await FindKeycloakUserAsync(user.Username, adminToken);
            if (string.IsNullOrWhiteSpace(user.KeycloakId))
            {
                throw new InvalidOperationException($"Unable to resolve Keycloak ID for {user.Username}");
            }

            await SetKeycloakPasswordAsync(user.KeycloakId, adminToken);
            return user;
        }

        private async Task SetKeycloakPasswordAsync(string userId, string adminToken)
        {
            var payload = new { type = "password", value = _options.DemoUserPassword, temporary = false };
            var request = new HttpRequestMessage(HttpMethod.Put, $"{_options.KeycloakBaseUrl}/admin/realms/{_options.KeycloakRealm}/users/{userId}/reset-password")
            {
                Content = new StringContent(JsonSerializer.Serialize(payload), Encoding.UTF8, "application/json")
            };
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", adminToken);

            using var response = await _httpClient.SendAsync(request);
            if (!response.IsSuccessStatusCode)
            {
                var body = await response.Content.ReadAsStringAsync();
                var status = (int)response.StatusCode;
                throw new InvalidOperationException($"Failed to set password for Keycloak user {userId} ({status}): {body}");
            }
        }

        private async Task<string> AcquireUserTokenAsync(string username, string password, List<string> logs)
        {
            var data = new Dictionary<string, string>
            {
                ["grant_type"] = "password",
                ["client_id"] = _options.ClientId,
                ["username"] = username,
                ["password"] = password,
                ["scope"] = _options.ClientScopes
            };

            using var response = await _httpClient.PostAsync(
                $"{_options.KeycloakBaseUrl}/realms/{_options.KeycloakRealm}/protocol/openid-connect/token",
                new FormUrlEncodedContent(data));

            if (!response.IsSuccessStatusCode)
            {
                var body = await response.Content.ReadAsStringAsync();
                var status = (int)response.StatusCode;
                throw new InvalidOperationException($"Failed to acquire token for {username} ({status}): {body}");
            }

            var payload = await response.Content.ReadAsStringAsync();
            using var document = JsonDocument.Parse(payload);
            var token = document.RootElement.TryGetProperty("access_token", out var accessToken)
                ? accessToken.GetString()
                : null;

            if (string.IsNullOrWhiteSpace(token))
            {
                throw new InvalidOperationException($"Token response for {username} missing access_token field");
            }

            logs.Add($"[KEYCLOAK] Token issued for {username}");
            return token;
        }

        private async Task<int> CreateUserProfileAsync(ScenarioUser user, List<string> logs)
        {
            if (string.IsNullOrWhiteSpace(user.Token))
            {
                throw new InvalidOperationException($"Cannot create profile for {user.Username} without token");
            }

            var age = _random.Next(24, 34);
            var birthDate = DateTime.UtcNow.AddYears(-age).AddDays(-_random.Next(0, 365));

            var payload = new
            {
                name = user.FullName,
                email = user.Email,
                bio = "Automated scenario profile used to validate signup to match flow.",
                gender = user.Gender,
                preferences = user.Preferences,
                dateOfBirth = birthDate,
                city = "Stockholm",
                state = "Stockholm County",
                country = "Sweden",
                latitude = 59.3293,
                longitude = 18.0686,
                occupation = "Automation Engineer",
                education = "University Degree",
                interests = new[] { "Hiking", "Technology", "Food" },
                languages = new[] { "English", "Swedish" },
                height = 170 + _random.Next(0, 15),
                religion = "None",
                smokingStatus = "Never",
                drinkingStatus = "Socially",
                wantsChildren = true,
                hasChildren = false,
                relationshipType = "Long-term relationship"
            };

            var request = new HttpRequestMessage(HttpMethod.Post, _options.UserServiceBaseUrl)
            {
                Content = JsonContent.Create(payload)
            };
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", user.Token);

            using var response = await _httpClient.SendAsync(request);
            if (response.StatusCode == HttpStatusCode.Conflict)
            {
                throw new InvalidOperationException($"Profile already exists for {user.Email}");
            }

            if (!response.IsSuccessStatusCode)
            {
                var body = await response.Content.ReadAsStringAsync();
                var status = (int)response.StatusCode;
                throw new InvalidOperationException($"User profile creation failed ({status}): {body}");
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            var profileId = ExtractProfileId(response, responseBody);
            logs.Add($"[PROFILE] Created profile {profileId} for {user.Username}");
            return profileId;
        }

        private async Task RecordSwipeAsync(int actorId, int targetId, string token, List<string> logs)
        {
            var payload = new { userId = actorId, targetUserId = targetId, isLike = true };
            var request = new HttpRequestMessage(HttpMethod.Post, _options.SwipeServiceBaseUrl)
            {
                Content = JsonContent.Create(payload)
            };
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

            using var response = await _httpClient.SendAsync(request);
            if (!response.IsSuccessStatusCode)
            {
                var body = await response.Content.ReadAsStringAsync();
                var status = (int)response.StatusCode;
                throw new InvalidOperationException($"Swipe failed ({status}): {body}");
            }

            var responseBody = await response.Content.ReadAsStringAsync();
            var mutual = false;
            if (!string.IsNullOrWhiteSpace(responseBody))
            {
                try
                {
                    using var document = JsonDocument.Parse(responseBody);
                    if (document.RootElement.TryGetProperty("isMutualMatch", out var mutualElement) && mutualElement.ValueKind == JsonValueKind.True)
                    {
                        mutual = true;
                    }
                }
                catch (JsonException)
                {
                    // Ignore parsing errors for optional response data
                }
            }

            var suffix = mutual ? " (mutual match detected)" : string.Empty;
            logs.Add($"[SWIPE] {actorId} liked {targetId}{suffix}");
        }

        private async Task<int?> WaitForMatchAsync(int userId, string token, List<string> logs)
        {
            const int maxAttempts = 6;
            for (var attempt = 1; attempt <= maxAttempts; attempt++)
            {
                var matches = await GetSwipeMatchesAsync(userId, token);
                if (matches.Count > 0)
                {
                    var matchId = matches[0].Id;
                    logs.Add($"[MATCH] Found mutual match for user {userId} on attempt {attempt}. MatchId: {matchId}");
                    return matchId;
                }

                await Task.Delay(TimeSpan.FromSeconds(1));
            }

            throw new InvalidOperationException($"No mutual match detected for user {userId} after waiting.");
        }

        private async Task<List<SwipeMatchDto>> GetSwipeMatchesAsync(int userId, string token)
        {
            var request = new HttpRequestMessage(HttpMethod.Get, $"{_options.SwipeServiceBaseUrl}/matches/{userId}");
            request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

            using var response = await _httpClient.SendAsync(request);
            if (!response.IsSuccessStatusCode)
            {
                var body = await response.Content.ReadAsStringAsync();
                var status = (int)response.StatusCode;
                throw new InvalidOperationException($"Failed to retrieve matches ({status}): {body}");
            }

            var content = await response.Content.ReadAsStringAsync();
            if (string.IsNullOrWhiteSpace(content))
            {
                return new List<SwipeMatchDto>();
            }

            return JsonSerializer.Deserialize<List<SwipeMatchDto>>(content, _jsonOptions) ?? new List<SwipeMatchDto>();
        }

        private async Task<string?> FindKeycloakUserAsync(string username, string adminToken)
        {
            var request = new HttpRequestMessage(HttpMethod.Get, $"{_options.KeycloakBaseUrl}/admin/realms/{_options.KeycloakRealm}/users?username={Uri.EscapeDataString(username)}")
            {
                Headers =
                {
                    Authorization = new AuthenticationHeaderValue("Bearer", adminToken)
                }
            };

            using var response = await _httpClient.SendAsync(request);
            if (!response.IsSuccessStatusCode)
            {
                return null;
            }

            var payload = await response.Content.ReadAsStringAsync();
            using var document = JsonDocument.Parse(payload);
            if (document.RootElement.ValueKind != JsonValueKind.Array || document.RootElement.GetArrayLength() == 0)
            {
                return null;
            }

            var first = document.RootElement[0];
            if (first.TryGetProperty("id", out var idProperty))
            {
                return idProperty.GetString();
            }

            return null;
        }

        private static string ExtractTrailingSegment(string? location)
        {
            if (string.IsNullOrWhiteSpace(location))
            {
                return string.Empty;
            }

            if (Uri.TryCreate(location, UriKind.Absolute, out var absolute))
            {
                if (absolute.Segments.Length > 0)
                {
                    return absolute.Segments[^1].Trim('/');
                }
            }
            else if (Uri.TryCreate(location, UriKind.Relative, out var relative))
            {
                var segments = relative.ToString().Trim('/').Split('/', StringSplitOptions.RemoveEmptyEntries);
                if (segments.Length > 0)
                {
                    return segments[^1];
                }
            }

            var parts = location.Trim('/').Split('/', StringSplitOptions.RemoveEmptyEntries);
            return parts.Length > 0 ? parts[^1] : string.Empty;
        }

        private static int ExtractProfileId(HttpResponseMessage response, string body)
        {
            if (response.Headers.Location != null)
            {
                var candidate = ExtractTrailingSegment(response.Headers.Location.ToString());
                if (int.TryParse(candidate, NumberStyles.Integer, CultureInfo.InvariantCulture, out var locationId))
                {
                    return locationId;
                }
            }

            if (!string.IsNullOrWhiteSpace(body))
            {
                try
                {
                    using var document = JsonDocument.Parse(body);
                    if (document.RootElement.ValueKind == JsonValueKind.Object)
                    {
                        if (document.RootElement.TryGetProperty("id", out var idProperty) && idProperty.ValueKind == JsonValueKind.Number)
                        {
                            return idProperty.GetInt32();
                        }

                        if (document.RootElement.TryGetProperty("Id", out var idPropertyPascal) && idPropertyPascal.ValueKind == JsonValueKind.Number)
                        {
                            return idPropertyPascal.GetInt32();
                        }

                        if (document.RootElement.TryGetProperty("value", out var valueProperty) && valueProperty.ValueKind == JsonValueKind.Object)
                        {
                            if (valueProperty.TryGetProperty("id", out var nestedId) && nestedId.ValueKind == JsonValueKind.Number)
                            {
                                return nestedId.GetInt32();
                            }

                            if (valueProperty.TryGetProperty("Id", out var nestedIdPascal) && nestedIdPascal.ValueKind == JsonValueKind.Number)
                            {
                                return nestedIdPascal.GetInt32();
                            }
                        }
                    }
                }
                catch (JsonException)
                {
                    // Ignore parsing errors and fall through to exception below
                }
            }

            throw new InvalidOperationException("Unable to determine created profile identifier from response.");
        }
    }

    private sealed class ScenarioResult
    {
        private ScenarioResult(bool isSuccess, int? matchId, string? errorMessage, IReadOnlyList<string> logs)
        {
            IsSuccess = isSuccess;
            MatchId = matchId;
            ErrorMessage = errorMessage;
            Logs = logs;
        }

        public bool IsSuccess { get; }
        public int? MatchId { get; }
        public string? ErrorMessage { get; }
        public IReadOnlyList<string> Logs { get; }

        public static ScenarioResult Success(int? matchId, List<string> logs) =>
            new ScenarioResult(true, matchId, null, logs.ToArray());

        public static ScenarioResult Failure(string? errorMessage, List<string> logs) =>
            new ScenarioResult(false, null, errorMessage, logs.ToArray());
    }

    private sealed class ScenarioUser
    {
        public ScenarioUser(string username, string email, string password, string firstName, string lastName, string gender, string preferences)
        {
            Username = username;
            Email = email;
            Password = password;
            FirstName = firstName;
            LastName = lastName;
            Gender = gender;
            Preferences = preferences;
        }

        public string Username { get; }
        public string Email { get; }
        public string Password { get; }
        public string FirstName { get; }
        public string LastName { get; }
        public string Gender { get; }
        public string Preferences { get; }
        public string FullName => $"{FirstName} {LastName}";
        public string? KeycloakId { get; set; }
        public string? Token { get; set; }
        public int? ProfileId { get; set; }
    }

    private sealed record SwipeMatchDto(int Id, int MatchedUserId);


    // --- STUBS for missing menu methods to fix build ---
    static void CreateSwipes() { Console.WriteLine("[STUB] CreateSwipes not implemented."); Console.ReadKey(); }
    static void CreateMutualMatches() { Console.WriteLine("[STUB] CreateMutualMatches not implemented."); Console.ReadKey(); }
    static void CreateMessages() { Console.WriteLine("[STUB] CreateMessages not implemented."); Console.ReadKey(); }
    static void SetDatabaseConnection() { Console.WriteLine("[STUB] SetDatabaseConnection not implemented."); Console.ReadKey(); }
}

// --- Environment Configuration Classes ---
public class EnvironmentConfig
{
    public string Environment { get; set; } = "local";
    public string DatabaseSuffix { get; set; } = "";
    public string? DatabaseConnection { get; set; }
    public DataProfile DataProfile { get; set; } = new();
    public Dictionary<string, string> ApiEndpoints { get; set; } = new();
    public Features Features { get; set; } = new();
}

public class DataProfile
{
    public int UserCount { get; set; } = 10;
    public bool TestUsersOnly { get; set; } = false;
    public bool SafetyMode { get; set; } = false;
    public double MatchPercentage { get; set; } = 0.2;
    public string MessageDensity { get; set; } = "medium";
    public int PhotosPerUser { get; set; } = 3;
    public string DataRetention { get; set; } = "indefinite";
    public List<DemoScenarioConfig> DemoScenarios { get; set; } = new();
}

public class DemoScenarioConfig
{
    public string Name { get; set; } = "";
    public string[] Users { get; set; } = Array.Empty<string>();
    public string Script { get; set; } = "";
}

public class Features
{
    public bool ResetOnStartup { get; set; } = false;
    public bool GeneratePhotos { get; set; } = false;
    public bool CreateRealTimeMessages { get; set; } = false;
    public bool EnableAnalytics { get; set; } = true;
    public bool RequireAuthentication { get; set; } = false;
}
