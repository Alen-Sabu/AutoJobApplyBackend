"""
Seed runner: insert data into all tables.
Uses SessionLocal from app.core.database. Run from project root:
  cd AutoJobApplyBackend && python -m app.seed.run
Optionally: python -m app.seed.run --reset  to clear seed data first.
"""
import sys
import argparse

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.profile import Profile
from app.models.job import Job
from app.models.company import Company
from app.models.user_job import UserJob, UserJobStatus
from app.models.user_setup import UserSetup
from app.models.automation import Automation
from app.services.auth_service import AuthService
from app.seed.data import USER_ROWS, SEED_PASSWORD, build_job_rows, AUTOMATION_TEMPLATES, COMPANY_ROWS


def _hash_password(db: Session, password: str) -> str:
    return AuthService(db).get_password_hash(password)


def _clear_seed_data(db: Session) -> None:
    """Delete data in FK-safe order so we can re-seed."""
    db.query(UserJob).delete()
    db.query(Automation).delete()
    db.query(UserSetup).delete()
    db.query(Profile).delete()
    db.query(Job).delete()
    db.query(Company).delete()
    db.query(User).delete()
    db.commit()


def _slugify(name: str) -> str:
    s = name.lower().replace(" ", "-")
    return "".join(c for c in s if c.isalnum() or c == "-").strip("-") or "company"


def seed_users(db: Session, password: str) -> list[User]:
    hashed = _hash_password(db, password)
    users = []
    for row in USER_ROWS:
        u = User(
            email=row["email"],
            hashed_password=hashed,
            full_name=row.get("full_name"),
            username=row.get("username"),
            is_superuser=row.get("is_superuser", False),
            is_active=True,
            role="user",
        )
        db.add(u)
        users.append(u)
    db.commit()
    for u in users:
        db.refresh(u)
    return users


def seed_company_users(db: Session, password: str) -> list[tuple[User, Company]]:
    """Create users with role=company and their Company rows."""
    hashed = _hash_password(db, password)
    pairs: list[tuple[User, Company]] = []
    for row in COMPANY_ROWS:
        u = User(
            email=row["email"],
            hashed_password=hashed,
            full_name=row.get("full_name"),
            username=None,
            is_superuser=False,
            is_active=True,
            role="company",
        )
        db.add(u)
        db.flush()  # get u.id
        slug = _slugify(row["company_name"])
        existing = db.query(Company).filter(Company.slug == slug).first()
        if existing:
            slug = f"{slug}-{u.id}"
        c = Company(
            user_id=u.id,
            company_name=row["company_name"],
            slug=slug,
            description=row.get("description"),
            website=row.get("website"),
        )
        db.add(c)
        pairs.append((u, c))
    db.commit()
    for u, c in pairs:
        db.refresh(u)
        db.refresh(c)
    return pairs


def seed_profiles(db: Session, users: list[User]) -> None:
    for user in users:
        if db.query(Profile).filter(Profile.user_id == user.id).first():
            continue
        name_parts = (user.full_name or "User").split(" ", 1)
        first_name = name_parts[0] if name_parts else None
        last_name = name_parts[1] if len(name_parts) > 1 else None
        p = Profile(
            user_id=user.id,
            first_name=first_name,
            last_name=last_name,
            headline=f"Software Engineer at {user.email.split('@')[0].title()}",
            primary_location="Remote",
            years_experience="5+",
            top_skills="Python, JavaScript, React, SQL",
        )
        db.add(p)
    db.commit()


def seed_jobs(db: Session, count: int = 250) -> list[Job]:
    rows = build_job_rows(count)
    jobs = []
    for r in rows:
        j = Job(
            title=r["title"],
            company=r["company"],
            location=r.get("location"),
            description=r.get("description"),
            job_url=r.get("job_url"),
            salary_range=r.get("salary_range"),
            job_type=r.get("job_type"),
            source=r.get("source"),
            external_id=r.get("external_id"),
            status=r.get("status", "pending"),
        )
        db.add(j)
        jobs.append(j)
    db.commit()
    for j in jobs:
        db.refresh(j)
    return jobs


def seed_company_jobs(db: Session, companies: list[Company]) -> list[Job]:
    """Create a few jobs per company with company_id set."""
    from app.seed.data import JOB_TITLES, LOCATIONS, JOB_TYPES, SOURCES
    import random
    random.seed(43)
    jobs = []
    for co in companies:
        for _ in range(random.randint(2, 5)):
            title = random.choice(JOB_TITLES)
            loc = random.choice(LOCATIONS)
            j = Job(
                title=title,
                company=co.company_name,
                company_id=co.id,
                location=loc,
                description=f"Join {co.company_name} as {title}. Great team and growth.",
                job_url=None,
                salary_range=f"${random.randint(80, 200)}k - ${random.randint(120, 280)}k" if random.random() > 0.3 else None,
                job_type=random.choice(JOB_TYPES),
                source=random.choice(SOURCES),
                external_id=None,
                status=random.choice(["pending", "approved", "approved"]),
            )
            db.add(j)
            jobs.append(j)
    db.commit()
    for j in jobs:
        db.refresh(j)
    return jobs


def seed_user_setups(db: Session, users: list[User]) -> None:
    for i, user in enumerate(users):
        if db.query(UserSetup).filter(UserSetup.user_id == user.id).first():
            continue
        complete = i % 3 != 0  # about 2/3 complete
        us = UserSetup(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone="+1 555 000 0000" if complete else None,
            location="Remote" if complete else None,
            linkedin_url=f"https://linkedin.com/in/{user.username}" if user.username and complete else None,
            years_experience="5" if complete else None,
            top_skills="Python, React, SQL" if complete else None,
            setup_complete=complete,
        )
        db.add(us)
    db.commit()


def seed_automations(db: Session, users: list[User]) -> list[Automation]:
    automations = []
    # Skip first two (admins); assign automations to regular users
    regular = [u for u in users if not getattr(u, "is_superuser", False)][: max(1, len(users) - 2)]
    for i, user in enumerate(regular):
        for j, tmpl in enumerate(AUTOMATION_TEMPLATES):
            if (i + j) % 4 == 0:  # give each user a subset of automation types
                a = Automation(
                    user_id=user.id,
                    name=tmpl["name"],
                    target_titles=tmpl["target_titles"],
                    locations=tmpl["locations"],
                    daily_limit=tmpl["daily_limit"],
                    platforms=tmpl["platforms"],
                    status="running" if j % 2 == 0 else "paused",
                    total_applied=(i + j) * 3,
                )
                db.add(a)
                automations.append(a)
    db.commit()
    for a in automations:
        db.refresh(a)
    return automations


def seed_user_jobs(db: Session, users: list[User], jobs: list[Job], automations: list[Automation]) -> None:
    from random import choice, randint

    regular_users = [u for u in users if not getattr(u, "is_superuser", False)]
    if not regular_users or not jobs:
        return
    auto_by_user: dict[int, list[Automation]] = {}
    for a in automations:
        auto_by_user.setdefault(a.user_id, []).append(a)
    # Track (user_id, job_id) we've added this run to avoid duplicates before commit
    seen: set[tuple[int, int]] = set()
    target = min(800, len(regular_users) * 50)
    attempts = 0
    max_attempts = target * 3
    while len(seen) < target and attempts < max_attempts:
        attempts += 1
        user = choice(regular_users)
        job = choice(jobs)
        key = (user.id, job.id)
        if key in seen:
            continue
        existing = db.query(UserJob).filter(
            UserJob.user_id == user.id,
            UserJob.job_id == job.id,
        ).first()
        if existing:
            seen.add(key)
            continue
        seen.add(key)
        autos = auto_by_user.get(user.id, [])
        automation_id = choice(autos).id if autos and randint(0, 1) else None
        status = choice(list(UserJobStatus))
        uj = UserJob(
            user_id=user.id,
            job_id=job.id,
            automation_id=automation_id,
            status=status,
        )
        db.add(uj)
    db.commit()


def run_all(db: Session, *, reset: bool = False, job_count: int = 250) -> None:
    if reset:
        _clear_seed_data(db)
    users = db.query(User).filter(User.role == "user").all()
    if users and not reset:
        print("Database already has users. Use --reset to clear and re-seed.")
        return
    if not users:
        users = seed_users(db, SEED_PASSWORD)
        print(f"Seeded {len(users)} users.")
    company_pairs = seed_company_users(db, SEED_PASSWORD)
    companies = [c for _, c in company_pairs]
    print(f"Seeded {len(companies)} companies.")
    seed_profiles(db, users)
    print("Seeded profiles.")
    jobs = db.query(Job).all()
    if not jobs:
        jobs = seed_jobs(db, job_count)
        print(f"Seeded {len(jobs)} jobs.")
        company_jobs = seed_company_jobs(db, companies)
        jobs = list(jobs) + list(company_jobs)
        print(f"Seeded {len(company_jobs)} company-owned jobs.")
    seed_user_setups(db, users)
    print("Seeded user_setups.")
    automations = db.query(Automation).all()
    if not automations:
        automations = seed_automations(db, users)
        print(f"Seeded {len(automations)} automations.")
    seed_user_jobs(db, users, jobs, automations)
    print("Seeded user_jobs.")
    print("Done.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed the database with sample data.")
    parser.add_argument("--reset", action="store_true", help="Clear existing seed data (users, jobs, etc.) then seed.")
    parser.add_argument("--job-count", type=int, default=250, help="Number of jobs to create (default 250).")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        run_all(db, reset=args.reset, job_count=args.job_count)
    except Exception as e:
        print(f"Seed failed: {e}", file=sys.stderr)
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
