SELECT u.username
FROM users u
JOIN emails e ON u.user_id = e.user_id
WHERE e.email = ?