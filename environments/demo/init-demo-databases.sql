-- Demo Environment Database Initialization
-- Creates all required databases with demo suffix

CREATE DATABASE IF NOT EXISTS auth_service_demo;
CREATE DATABASE IF NOT EXISTS user_service_demo;
CREATE DATABASE IF NOT EXISTS matchmaking_service_demo;
CREATE DATABASE IF NOT EXISTS swipe_service_demo;
CREATE DATABASE IF NOT EXISTS photo_service_demo;
CREATE DATABASE IF NOT EXISTS messaging_service_demo;

-- Create demo user for all databases
CREATE USER IF NOT EXISTS 'demo_user'@'%' IDENTIFIED BY 'demo_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON auth_service_demo.* TO 'demo_user'@'%';
GRANT ALL PRIVILEGES ON user_service_demo.* TO 'demo_user'@'%';
GRANT ALL PRIVILEGES ON matchmaking_service_demo.* TO 'demo_user'@'%';
GRANT ALL PRIVILEGES ON swipe_service_demo.* TO 'demo_user'@'%';
GRANT ALL PRIVILEGES ON photo_service_demo.* TO 'demo_user'@'%';
GRANT ALL PRIVILEGES ON messaging_service_demo.* TO 'demo_user'@'%';

FLUSH PRIVILEGES;

-- Show created databases
SHOW DATABASES LIKE '%demo%';
