INSERT INTO holidays (user_id, date)
SELECT u.user_id, ? 
FROM users u
JOIN emails e ON u.user_id = e.user_id
WHERE e.email = ?