#!/bin/bash
# Quick backend status check - just count records in key tables

echo "==================================================================="
echo "Backend Services Status - Database Record Counts"
echo "==================================================================="

echo ""
echo "UserService (Port 3308):"
mysql -h 127.0.0.1 -P 3308 -u root -proot_password -D UserServiceDb -e "
    SELECT 'UserProfiles' as Table_Name, COUNT(*) as Count FROM UserProfiles
    UNION ALL
    SELECT 'Photos', COUNT(*) FROM Photos;" 2>/dev/null || echo "  ❌ Cannot connect"

echo ""
echo "SwipeService (Port 3310):"
mysql -h 127.0.0.1 -P 3310 -u root -proot_password -D SwipeServiceDb -e "
    SELECT 'UserProfileMappings' as Table_Name, COUNT(*) as Count FROM UserProfileMappings
    UNION ALL
    SELECT 'Swipes', COUNT(*) FROM Swipes
    UNION ALL
    SELECT 'Matches', COUNT(*) FROM Matches WHERE IsActive = 1;" 2>/dev/null || echo "  ❌ Cannot connect"

echo ""
echo "MatchmakingService (Port 3309):"
mysql -h 127.0.0.1 -P 3309 -u root -proot_password -D MatchmakingDb -e "
    SELECT 'CandidateScores' as Table_Name, COUNT(*) as Count FROM CandidateScores;" 2>/dev/null || echo "  ❌ Cannot connect"

echo ""
echo "PhotoService (Port 3311):"
mysql -h 127.0.0.1 -P 3311 -u root -proot_password -D PhotoDb -e "
    SELECT 'PhotoMetadata' as Table_Name, COUNT(*) as Count FROM PhotoMetadata;" 2>/dev/null || echo "  ❌ Cannot connect"

echo ""
echo "MessagingService (Port 3306):"
mysql -h 127.0.0.1 -P 3306 -u root -D MessagingServiceDb -e "
    SELECT 'Messages' as Table_Name, COUNT(*) as Count FROM Messages;" 2>/dev/null || echo "  ❌ Cannot connect or database doesn't exist"

echo ""
echo "==================================================================="
echo "Backend Services Running:"
echo "==================================================================="
ps aux | grep -E "UserService|MatchmakingService|SwipeService|MessagingService|PhotoService" | grep -v grep | awk '{print $11, $12, $13, $14}'

echo ""
