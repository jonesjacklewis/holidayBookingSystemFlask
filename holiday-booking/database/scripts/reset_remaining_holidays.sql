UPDATE holiday_allowance
SET remaining_holiday_allowance = (
    SELECT dflt_value
    FROM pragma_table_info('holiday_allowance')
    WHERE name = 'remaining_holiday_allowance'
)
WHERE user_id = (
    SELECT users.user_id
    FROM users
    JOIN emails ON emails.user_id = users.user_id
    WHERE emails.email = ?
    LIMIT 1
);
