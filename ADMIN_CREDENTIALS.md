# Admin Credentials

## Default Admin Account

The admin user has been created with the following credentials:

- **Email:** `admin@talentschat.com`
- **Password:** `admin123`
- **Name:** Admin User

## Important Notes

1. **Only one admin user exists** - The system allows only one admin user.
2. **Admin access is restricted** - Only users with `is_admin=True` can access `/admin/*` routes.
3. **Regular users** can only access the Learning dashboard (`/learn`) to view lessons, quizzes, leaderboard, etc.
4. **Admin link in navigation** - The "Admin" link in the navigation bar is only visible to admin users.

## To Change Admin Password

You can change the admin password by:

1. Logging in as admin
2. Going to Profile settings (if password change is implemented)
3. Or directly updating the database

## Security Recommendations

- Change the default password after first login
- Keep the admin credentials secure
- The admin account has full access to create/edit/delete all learning content



