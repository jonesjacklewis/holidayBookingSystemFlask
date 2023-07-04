SELECT ha.remaining_holiday_allowance
FROM holiday_allowance ha
JOIN users ON users.user_id = ha.user_id
JOIN emails ON emails.user_id = users.user_id
WHERE emails.email = ?