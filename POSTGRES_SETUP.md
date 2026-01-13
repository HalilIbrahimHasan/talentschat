# PostgreSQL Database Setup for Render.com

## Database Information

- **Hostname:** `dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com`
- **Port:** `5432`
- **Database:** `talentschatdb`
- **Username:** `talentschatdb_user`
- **Password:** `PexPT6558fFTGuly9RSPIe92nbVEMzEu`

## Connection String

```
postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb
```

## Setup Steps

### 1. Set Environment Variable in Render

1. Go to your Render.com dashboard
2. Select your web service (talentschat)
3. Go to "Environment" tab
4. Add a new environment variable:
   - **Key:** `DATABASE_URL`
   - **Value:** `postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb`

### 2. Initialize Database

**Option A: Run locally (if you have database access)**

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb"

# Run initialization script
python3 init_postgres_db.py
```

**Option B: Let the app initialize on first run**

The app will automatically create all tables on first startup if `DATABASE_URL` is set. You'll then need to create the admin user.

**Option C: Use Render Shell**

1. Go to your Render service
2. Click "Shell" tab
3. Run:
   ```bash
   export DATABASE_URL="postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb"
   python3 init_postgres_db.py
   ```

### 3. Create Admin User

If the database was initialized automatically (Option B), you can create the admin user using:

```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://talentschatdb_user:PexPT6558fFTGuly9RSPIe92nbVEMzEu@dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com:5432/talentschatdb"

# Run admin creation script
python3 create_admin.py
# Enter: admin@talentschat.com
# Enter: Admin User
# Enter: admin123
```

Or use the initialization script which automatically creates the admin user.

## Default Admin Credentials

- **Email:** `admin@talentschat.com`
- **Password:** `admin123`
- **Name:** `Admin User`

**⚠️ Important:** Change the admin password after first login!

## Verify Database Connection

You can verify the database connection using psql:

```bash
PGPASSWORD=PexPT6558fFTGuly9RSPIe92nbVEMzEu psql -h dpg-d5ir02n5r7bs73dk7cv0-a.oregon-postgres.render.com -U talentschatdb_user talentschatdb
```

Once connected, you can run:
```sql
\dt  -- List all tables
SELECT * FROM users;  -- View users
```

## Notes

- The initialization script (`init_postgres_db.py`) will:
  - Drop all existing tables (fresh start)
  - Create all tables from models
  - Create the admin user with default credentials
  
- If you want to preserve some data, modify the script before running it.

- The app automatically detects PostgreSQL vs SQLite and uses appropriate settings.

