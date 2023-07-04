SELECT h.date
FROM holidays h
JOIN users u
ON h.user_id = u.user_id
JOIN emails e
ON u.user_id = e.user_id
WHERE e.email = ?
ORDER BY h.date ASC;