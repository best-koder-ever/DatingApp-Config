"""Configuration for bot-service."""
import os

# Service URLs (match docker-compose.yml ports)
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8090")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "DatingApp")
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "admin")
KEYCLOAK_ADMIN_PASS = os.getenv("KEYCLOAK_ADMIN_PASS", "admin")

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8080")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8082")
MATCHMAKING_URL = os.getenv("MATCHMAKING_URL", "http://localhost:8083")
SWIPE_SERVICE_URL = os.getenv("SWIPE_SERVICE_URL", "http://localhost:8086")
MESSAGING_URL = os.getenv("MESSAGING_URL", "http://localhost:8084")
PHOTO_SERVICE_URL = os.getenv("PHOTO_SERVICE_URL", "http://localhost:8085")

# Bot defaults
DEFAULT_BOT_COUNT = 50
DEFAULT_SWIPE_RIGHT_PROBABILITY = 0.30
DEFAULT_SWIPE_DELAY_SECONDS = 2.0
DEFAULT_MESSAGE_DELAY_SECONDS = 5.0
DEFAULT_BOT_PASSWORD = "BotPass123!"

# randomuser.me

# Dashboard
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "9091"))
DASHBOARD_TITLE = "🤖 DatingApp Bot Dashboard"

# Curated data for realistic Swedish dating profiles
INTERESTS_POOL = [
    "Hiking", "Cooking", "Photography", "Yoga", "Gaming", "Reading",
    "Travel", "Music", "Dancing", "Skiing", "Running", "Cycling",
    "Cinema", "Art", "Theatre", "Coffee", "Wine tasting", "Surfing",
    "Rock climbing", "Meditation", "Podcasts", "Board games",
    "Camping", "Kayaking", "Concerts", "Foodie", "Dogs", "Cats",
    "Gym", "Swimming", "Tennis", "Volleyball", "Fika", "Craft beer",
    "Sustainability", "Gardening", "Baking", "Fashion", "Tattoos",
    "Vinyl records", "Astronomy", "Languages", "Sushi", "Brunch",
]

OCCUPATIONS_POOL = [
    "Software Developer", "Nurse", "Teacher", "Designer", "Engineer",
    "Physiotherapist", "Architect", "Marketing Manager", "Chef",
    "Psychologist", "Journalist", "Veterinarian", "Entrepreneur",
    "Project Manager", "Data Analyst", "Barista", "Musician",
    "Personal Trainer", "Social Worker", "Pharmacist", "Pilot",
    "Dentist", "Photographer", "Consultant", "Researcher",
]

BIO_TEMPLATES = [
    "Love {interest1} and {interest2}. Looking for someone to share {interest3} with 🌟",
    "Passionate about {interest1}. {occupation} by day, {interest2} enthusiast by night ✨",
    "{occupation} who loves {interest1}. Let's grab a coffee and see where it goes ☕",
    "New in {city}! Into {interest1}, {interest2}, and long walks. Tell me your best joke 😄",
    "Adventurous {occupation}. Weekends are for {interest1} and {interest2}. Dog person 🐕",
    "Life's too short for boring conversations. {interest1} > Netflix. Change my mind 🤔",
    "{interest1} addict. Currently learning {interest2}. Will cook you {interest3} 🍳",
    "Genuine {occupation} looking for real connections. Bonus points if you like {interest1} 💫",
    "Half Swedish, fully passionate about {interest1}. Ask me about my {interest2} hobby!",
    "Not here to waste time. {occupation}, {interest1} lover, aspiring {interest2} expert 🎯",
]

PROMPT_QUESTIONS = [
    "A perfect weekend looks like...",
    "My most controversial opinion is...",
    "I'm looking for someone who...",
    "The way to my heart is...",
    "My simple pleasures are...",
    "I'll know it's love when...",
    "Two truths and a lie...",
    "My love language is...",
]

PROMPT_ANSWERS_POOL = [
    "Morning hike, followed by brunch and a good book in the park",
    "Pineapple absolutely belongs on pizza. Fight me.",
    "Can make me laugh even on a Monday morning",
    "Cooking together, music, and genuine conversations",
    "Fresh coffee, sunrise runs, and lazy Sunday mornings",
    "We can sit in comfortable silence together",
    "I've been skydiving, I speak 3 languages, I can't cook",
    "Quality time and acts of service, always",
    "Spontaneous road trips with no destination in mind",
    "A hot chocolate and a rainy day indoors",
    "Someone who challenges me to be better",
    "Good food, better company, and the occasional dance-off",
]

SWEDISH_CITIES = [
    "Stockholm", "Göteborg", "Malmö", "Uppsala", "Linköping",
    "Örebro", "Västerås", "Helsingborg", "Norrköping", "Jönköping",
    "Umeå", "Lund", "Borås", "Sundsvall", "Gävle",
]

RELATIONSHIP_GOALS = [
    "serious", "casual", "friendship", "open_to_anything",
]
