"""
Seed data: large sets for users, jobs, profiles, user_setups, automations.
"""

# Default password for all seeded users (hash generated at runtime)
SEED_PASSWORD = "12345678"

# Users: mix of regular and a few admins (first two are admins for testing)
USER_ROWS = [
    {"email": "admin@crypgo.com", "full_name": "Admin User", "username": "admin", "is_superuser": True},
    {"email": "super@crypgo.com", "full_name": "Super Admin", "username": "superadmin", "is_superuser": True},
    {"email": "alice@example.com", "full_name": "Alice Smith", "username": "alice_s"},
    {"email": "bob@example.com", "full_name": "Bob Jones", "username": "bob_j"},
    {"email": "carol@example.com", "full_name": "Carol White", "username": "carol_w"},
    {"email": "dave@example.com", "full_name": "Dave Brown", "username": "dave_b"},
    {"email": "eve@example.com", "full_name": "Eve Davis", "username": "eve_d"},
    {"email": "frank@example.com", "full_name": "Frank Miller", "username": "frank_m"},
    {"email": "grace@example.com", "full_name": "Grace Lee", "username": "grace_l"},
    {"email": "henry@example.com", "full_name": "Henry Wilson", "username": "henry_w"},
    {"email": "ivy@example.com", "full_name": "Ivy Taylor", "username": "ivy_t"},
    {"email": "jack@example.com", "full_name": "Jack Anderson", "username": "jack_a"},
    {"email": "kate@example.com", "full_name": "Kate Thomas", "username": "kate_t"},
    {"email": "leo@example.com", "full_name": "Leo Jackson", "username": "leo_j"},
    {"email": "mia@example.com", "full_name": "Mia Martin", "username": "mia_m"},
    {"email": "noah@example.com", "full_name": "Noah Garcia", "username": "noah_g"},
    {"email": "olivia@example.com", "full_name": "Olivia Martinez", "username": "olivia_m"},
    {"email": "paul@example.com", "full_name": "Paul Robinson", "username": "paul_r"},
    {"email": "quinn@example.com", "full_name": "Quinn Clark", "username": "quinn_c"},
    {"email": "rachel@example.com", "full_name": "Rachel Lewis", "username": "rachel_l"},
    {"email": "sam@example.com", "full_name": "Sam Walker", "username": "sam_w"},
    {"email": "tina@example.com", "full_name": "Tina Hall", "username": "tina_h"},
    {"email": "uma@example.com", "full_name": "Uma Young", "username": "uma_y"},
    {"email": "victor@example.com", "full_name": "Victor King", "username": "victor_k"},
    {"email": "wendy@example.com", "full_name": "Wendy Wright", "username": "wendy_w"},
    {"email": "xavier@example.com", "full_name": "Xavier Lopez", "username": "xavier_l"},
    {"email": "yara@example.com", "full_name": "Yara Hill", "username": "yara_h"},
    {"email": "zane@example.com", "full_name": "Zane Scott", "username": "zane_s"},
    {"email": "amy@example.com", "full_name": "Amy Green", "username": "amy_g"},
    {"email": "ben@example.com", "full_name": "Ben Adams", "username": "ben_a"},
    {"email": "chloe@example.com", "full_name": "Chloe Nelson", "username": "chloe_n"},
    {"email": "dan@example.com", "full_name": "Dan Baker", "username": "dan_b"},
    {"email": "emma@example.com", "full_name": "Emma Carter", "username": "emma_c"},
    {"email": "felix@example.com", "full_name": "Felix Mitchell", "username": "felix_m"},
    {"email": "gina@example.com", "full_name": "Gina Perez", "username": "gina_p"},
    {"email": "hugo@example.com", "full_name": "Hugo Roberts", "username": "hugo_r"},
    {"email": "iris@example.com", "full_name": "Iris Turner", "username": "iris_t"},
    {"email": "jake@example.com", "full_name": "Jake Phillips", "username": "jake_p"},
    {"email": "luna@example.com", "full_name": "Luna Campbell", "username": "luna_c"},
    {"email": "marc@example.com", "full_name": "Marc Parker", "username": "marc_p"},
    {"email": "nina@example.com", "full_name": "Nina Evans", "username": "nina_e"},
    {"email": "omar@example.com", "full_name": "Omar Edwards", "username": "omar_e"},
    {"email": "pia@example.com", "full_name": "Pia Collins", "username": "pia_c"},
    {"email": "quinn2@example.com", "full_name": "Quinn Stewart", "username": "quinn_s"},
    {"email": "ryan@example.com", "full_name": "Ryan Sanchez", "username": "ryan_s"},
    {"email": "sara@example.com", "full_name": "Sara Morris", "username": "sara_m"},
    {"email": "tom@example.com", "full_name": "Tom Rogers", "username": "tom_r"},
    {"email": "una@example.com", "full_name": "Una Reed", "username": "una_r"},
    {"email": "vince@example.com", "full_name": "Vince Cook", "username": "vince_c"},
    {"email": "will@example.com", "full_name": "Will Morgan", "username": "will_m"},
]

# Job titles and companies for building a large job catalog
JOB_TITLES = [
    "Senior Software Engineer",
    "Frontend Developer",
    "Backend Engineer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Data Engineer",
    "Machine Learning Engineer",
    "Product Manager",
    "UX Designer",
    "Technical Lead",
    "React Developer",
    "Python Developer",
    "Java Developer",
    "Node.js Developer",
    "Cloud Architect",
    "Security Engineer",
    "Mobile Developer",
    "QA Engineer",
    "Scrum Master",
    "Data Scientist",
    "Engineering Manager",
    "Solutions Architect",
    "Site Reliability Engineer",
    "iOS Developer",
    "Android Developer",
]

COMPANIES = [
    "TechCorp", "DataFlow Inc", "CloudNine", "NextGen Labs", "ScaleUp",
    "CodeCraft", "DevHub", "ByteWorks", "LogicForge", "StackWave",
    "Nexus Systems", "PrimeLogic", "Vertex AI", "Nova Solutions", "Apex Tech",
    "Stellar Software", "Quantum Labs", "Pulse Systems", "Catalyst Inc", "Momentum IO",
    "Atlas Digital", "Horizon Tech", "Summit Labs", "Pinnacle Software", "Crest Systems",
    "Venture Build", "Spark Engineering", "Flux Labs", "Echo Tech", "Fusion Systems",
]

LOCATIONS = [
    "Remote", "New York, NY", "San Francisco, CA", "Austin, TX", "Seattle, WA",
    "Boston, MA", "Denver, CO", "Chicago, IL", "Los Angeles, CA", "London, UK",
    "Berlin, Germany", "Toronto, Canada", "Amsterdam, Netherlands", "Remote (US)",
    "Hybrid - NYC", "Hybrid - SF",
]

SOURCES = ["LinkedIn", "Indeed", "Wellfound", "RemoteOK", "Company Website", "Adzuna"]

JOB_TYPES = ["Full-time", "Contract", "Part-time", "Internship"]

# We'll generate many jobs by combining titles, companies, locations (data.py only holds constants; run.py builds the list)
def build_job_rows(count: int = 250):
    """Build a list of job dicts for seeding (deterministic from count)."""
    import random
    random.seed(42)
    jobs = []
    seen = set()
    for i in range(count):
        title = random.choice(JOB_TITLES)
        company = random.choice(COMPANIES)
        location = random.choice(LOCATIONS)
        key = (title, company, location)
        if key in seen:
            continue
        seen.add(key)
        jobs.append({
            "title": title,
            "company": company,
            "location": location,
            "description": f"Great opportunity for {title} at {company}. We are looking for talented individuals.",
            "job_url": f"https://example.com/jobs/{i+1}",
            "salary_range": f"${random.randint(80, 250)}k - ${random.randint(120, 350)}k" if random.random() > 0.3 else None,
            "job_type": random.choice(JOB_TYPES),
            "source": random.choice(SOURCES),
            "external_id": f"ext-{1000 + i}",
            "status": random.choice(["pending", "approved", "approved", "rejected"]),
        })
    return jobs

# Company users (employers): each gets a User (role=company) + Company row
COMPANY_ROWS = [
    {"email": "employer@techcorp.com", "full_name": "Jane Employer", "company_name": "TechCorp", "description": "Leading tech company.", "website": "https://techcorp.com"},
    {"email": "hr@dataflow.io", "full_name": "Bob HR", "company_name": "DataFlow Inc", "description": "Data infrastructure and analytics.", "website": "https://dataflow.io"},
    {"email": "recruiting@cloudnine.dev", "full_name": "Carol Recruiter", "company_name": "CloudNine", "description": "Cloud-native software.", "website": "https://cloudnine.dev"},
    {"email": "jobs@nextgenlabs.com", "full_name": "Dave Hiring", "company_name": "NextGen Labs", "description": "Innovation lab.", "website": None},
    {"email": "talent@scaleup.co", "full_name": "Eve Talent", "company_name": "ScaleUp", "description": "Scale-up hiring platform.", "website": "https://scaleup.co"},
]

# Automation name templates and configs for seeding
AUTOMATION_TEMPLATES = [
    {"name": "Senior React roles", "target_titles": "React, Frontend, TypeScript", "locations": "Remote, US", "daily_limit": 25, "platforms": ["LinkedIn", "Wellfound"]},
    {"name": "Backend Python", "target_titles": "Python, Django, FastAPI", "locations": "Remote", "daily_limit": 20, "platforms": ["LinkedIn", "Indeed"]},
    {"name": "Full-stack Node", "target_titles": "Node.js, Full Stack, JavaScript", "locations": "Remote, EU", "daily_limit": 30, "platforms": ["LinkedIn"]},
    {"name": "DevOps / SRE", "target_titles": "DevOps, SRE, AWS, Kubernetes", "locations": "Remote, US", "daily_limit": 15, "platforms": ["Indeed", "Wellfound"]},
    {"name": "Data Engineer", "target_titles": "Data Engineer, ETL, Spark", "locations": "Remote", "daily_limit": 20, "platforms": ["LinkedIn", "Indeed"]},
    {"name": "ML Engineer", "target_titles": "Machine Learning, ML, Python", "locations": "Remote, US", "daily_limit": 10, "platforms": ["LinkedIn"]},
    {"name": "Frontend EU", "target_titles": "Frontend, React, Vue", "locations": "EU, UK, Remote", "daily_limit": 25, "platforms": ["LinkedIn", "RemoteOK"]},
    {"name": "Mobile apps", "target_titles": "iOS, Android, React Native", "locations": "Remote", "daily_limit": 15, "platforms": ["Indeed"]},
]
