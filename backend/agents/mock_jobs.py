"""
Extended mock job database — used when JSearch API is unavailable or for demo.
Covers software, data, design, marketing, finance domains.
"""

MOCK_JOBS = [
    # Software Engineering
    {
        "source": "naukri", "source_job_id": "naukri_se_001",
        "source_url": "https://www.naukri.com/jobs/software-engineer-infosys",
        "title": "Software Engineer — Fresher", "company": "Infosys",
        "company_logo": "", "location": "Bangalore, India", "job_type": "full_time",
        "salary_min": 350000, "salary_max": 600000, "salary_currency": "INR",
        "description": "Join Infosys as a Software Engineer. Work on enterprise applications, cloud migrations, and digital transformation projects. You will be part of Agile teams delivering solutions for global clients across BFSI, retail, and healthcare sectors.",
        "requirements": ["B.Tech/BE in CS or related", "60%+ aggregate", "Strong programming fundamentals", "Good communication skills"],
        "skills_required": ["Java", "Python", "SQL", "Data Structures", "Algorithms", "OOP"],
        "experience_required": "0", "posted_at": None,
    },
    {
        "source": "naukri", "source_job_id": "naukri_se_002",
        "source_url": "https://www.naukri.com/jobs/get-wipro",
        "title": "Graduate Engineer Trainee", "company": "Wipro",
        "company_logo": "", "location": "Hyderabad, India", "job_type": "full_time",
        "salary_min": 330000, "salary_max": 550000, "salary_currency": "INR",
        "description": "Wipro is hiring Graduate Engineer Trainees for our technology division. Selected candidates will undergo a 3-month training program before being placed on live projects.",
        "requirements": ["B.Tech/BE any discipline", "60%+ aggregate", "No active backlogs"],
        "skills_required": ["C", "C++", "DBMS", "OS", "Computer Networks"],
        "experience_required": "0", "posted_at": None,
    },
    # Data Science / ML
    {
        "source": "internshala", "source_job_id": "intern_ds_001",
        "source_url": "https://internshala.com/internship/data-science-razorpay",
        "title": "Data Science Intern", "company": "Razorpay",
        "company_logo": "", "location": "Bangalore, India", "job_type": "internship",
        "salary_min": 30000, "salary_max": 50000, "salary_currency": "INR",
        "description": "Work with Razorpay's data team to build ML models for fraud detection, payment success optimization, and customer segmentation. You'll work with petabyte-scale transaction data.",
        "requirements": ["Strong Python skills", "ML fundamentals", "Statistics knowledge", "Currently pursuing or completed B.Tech/M.Tech"],
        "skills_required": ["Python", "Machine Learning", "Pandas", "Scikit-learn", "SQL", "Statistics"],
        "experience_required": "0", "posted_at": None,
    },
    {
        "source": "naukri", "source_job_id": "naukri_ds_001",
        "source_url": "https://www.naukri.com/jobs/junior-data-analyst-tcs",
        "title": "Junior Data Analyst", "company": "TCS",
        "company_logo": "", "location": "Mumbai, India", "job_type": "full_time",
        "salary_min": 360000, "salary_max": 650000, "salary_currency": "INR",
        "description": "TCS is looking for data analysts passionate about numbers and business insights. You will analyze large datasets, build dashboards, and present findings to stakeholders.",
        "requirements": ["Degree in Statistics/Math/CS/Economics", "SQL proficiency", "Excel advanced", "Business acumen"],
        "skills_required": ["SQL", "Excel", "Python", "Tableau", "Power BI", "Data Visualization"],
        "experience_required": "0", "posted_at": None,
    },
    # Product Management
    {
        "source": "internshala", "source_job_id": "intern_pm_001",
        "source_url": "https://internshala.com/internship/product-management-meesho",
        "title": "Product Management Intern", "company": "Meesho",
        "company_logo": "", "location": "Bangalore, India", "job_type": "internship",
        "salary_min": 20000, "salary_max": 35000, "salary_currency": "INR",
        "description": "Work directly with senior PMs on Meesho's seller platform. Drive feature launches, analyze product metrics, run A/B tests, and coordinate with engineering and design teams.",
        "requirements": ["Strong analytical skills", "Excellent communication", "Interest in e-commerce", "Structured thinking"],
        "skills_required": ["Product Thinking", "SQL", "Excel", "Figma", "A/B Testing", "Data Analysis"],
        "experience_required": "0", "posted_at": None,
    },
    # Design
    {
        "source": "internshala", "source_job_id": "intern_ux_001",
        "source_url": "https://internshala.com/internship/ux-design-swiggy",
        "title": "UI/UX Design Intern", "company": "Swiggy",
        "company_logo": "", "location": "Bangalore, India", "job_type": "internship",
        "salary_min": 15000, "salary_max": 25000, "salary_currency": "INR",
        "description": "Join Swiggy's design team to create delightful experiences for millions of users. Work on the consumer app, restaurant partner dashboard, and internal tools.",
        "requirements": ["Portfolio of design work", "Proficiency in Figma", "Understanding of UX principles", "Attention to detail"],
        "skills_required": ["Figma", "UI Design", "UX Research", "Prototyping", "Design Systems", "Wireframing"],
        "experience_required": "0", "posted_at": None,
    },
    # Remote / Full stack
    {
        "source": "linkedin", "source_job_id": "li_fs_001",
        "source_url": "https://linkedin.com/jobs/fullstack-remote",
        "title": "Junior Full Stack Developer", "company": "Groww",
        "company_logo": "", "location": "Remote, India", "job_type": "remote",
        "salary_min": 400000, "salary_max": 700000, "salary_currency": "INR",
        "description": "Groww is building the next generation of financial products for India. Join us as a full stack developer to work on high-scale systems serving 10M+ users. Fully remote role with flexible hours.",
        "requirements": ["Proficiency in React + Node.js or Python", "Understanding of REST APIs", "Basic database knowledge", "Self-motivated"],
        "skills_required": ["React", "Node.js", "JavaScript", "REST APIs", "PostgreSQL", "Git"],
        "experience_required": "0", "posted_at": None,
    },
    # Marketing
    {
        "source": "internshala", "source_job_id": "intern_mkt_001",
        "source_url": "https://internshala.com/internship/digital-marketing-zomato",
        "title": "Digital Marketing Intern", "company": "Zomato",
        "company_logo": "", "location": "Gurugram, India", "job_type": "internship",
        "salary_min": 12000, "salary_max": 20000, "salary_currency": "INR",
        "description": "Work with Zomato's growth marketing team on campaigns that reach millions. Own social media calendars, analyze campaign performance, and assist with influencer partnerships.",
        "requirements": ["Strong communication skills", "Creativity", "Interest in digital marketing", "Basic analytics knowledge"],
        "skills_required": ["Social Media Marketing", "Google Analytics", "Content Creation", "SEO", "Excel", "Copywriting"],
        "experience_required": "0", "posted_at": None,
    },
    # Finance
    {
        "source": "naukri", "source_job_id": "naukri_fin_001",
        "source_url": "https://www.naukri.com/jobs/finance-analyst-deloitte",
        "title": "Finance Analyst — Campus Hire", "company": "Deloitte",
        "company_logo": "", "location": "Mumbai, India", "job_type": "full_time",
        "salary_min": 700000, "salary_max": 900000, "salary_currency": "INR",
        "description": "Deloitte's campus program for Finance graduates. Work on financial advisory, audit, and consulting projects for Fortune 500 clients. Intensive 6-month training program included.",
        "requirements": ["B.Com/BBA/MBA Finance", "Strong Excel and financial modeling", "Attention to detail", "CA Foundation preferred"],
        "skills_required": ["Financial Modeling", "Excel", "Accounting", "Financial Analysis", "PowerPoint", "Communication"],
        "experience_required": "0", "posted_at": None,
    },
    # AI / ML Engineer
    {
        "source": "linkedin", "source_job_id": "li_ai_001",
        "source_url": "https://linkedin.com/jobs/ai-engineer-freshworks",
        "title": "Junior AI Engineer", "company": "Freshworks",
        "company_logo": "", "location": "Chennai, India", "job_type": "full_time",
        "salary_min": 600000, "salary_max": 900000, "salary_currency": "INR",
        "description": "Join Freshworks AI team to build intelligent features for our CRM, helpdesk, and marketing products. Work on NLP, recommendation systems, and AI-powered automation used by 60,000+ businesses globally.",
        "requirements": ["Strong Python", "ML/DL fundamentals", "NLP experience preferred", "B.Tech CS/Data Science"],
        "skills_required": ["Python", "NLP", "Machine Learning", "Deep Learning", "PyTorch", "LLMs", "REST APIs"],
        "experience_required": "0", "posted_at": None,
    },
]
