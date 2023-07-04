UPDATE holiday_allowance
SET remaining_holiday_allowance = 
    CASE 
        WHEN remaining_holiday_allowance - ? >= 0 
        THEN remaining_holiday_allowance - ? 
        ELSE 0 
    END
WHERE user_id = (
    SELECT users.user_id
    FROM users
    JOIN emails ON emails.user_id = users.user_id
    WHERE emails.email = ?
    LIMIT 1
);
