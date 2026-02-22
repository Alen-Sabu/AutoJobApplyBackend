# Database seed

Loads sample data into all tables: **users**, **profiles**, **jobs**, **user_setups**, **automations**, **user_jobs**.  
`site_settings` is created by migration (one row); it is not modified by the seeder.

## Run (from project root `AutoJobApplyBackend`)

```bash
# First time or to reset and re-seed (clears users, jobs, profiles, user_setups, automations, user_jobs)
python -m app.seed.run --reset

# Optional: number of jobs to create (default 250)
python -m app.seed.run --reset --job-count 400

# If DB already has users, run without --reset will exit without changes
python -m app.seed.run
```

## Data created

- **50 users** (2 admins: admin@crypgo.com, super@crypgo.com; 48 regular). Password for all: `Password123!`
- **Profiles** for every user
- **~200–400 jobs** (titles, companies, locations, sources)
- **User setups** for every user (about 2/3 marked complete)
- **~96 automations** across users (templates: React, Python, Node, DevOps, etc.)
- **Up to 800 user_jobs** (saved/applied links between users and jobs, some linked to automations)

Ensure migrations are applied before seeding: `python -m alembic -c app/alembic.ini upgrade head`
