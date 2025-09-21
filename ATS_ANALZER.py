import re
import json
import difflib
import docx
from collections import Counter
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import pdfplumber  
import google.generativeai as genai

# Configure API key
GEMINI_API_KEY = 'AIzaSyDxU1HXewyjHMy5vX9R8St-089c_V3X3jA'
genai.configure(api_key=GEMINI_API_KEY)

# ---------- Config & helpers ----------
STOPWORDS = {"and","or","the","a","an","to","for","of","in","on","with","by","from",
    "as","is","are","be","that","this","we","our","you","your","at","it",
    "using","use","used","will","can","ability","including","was","were","been",
    "have","has","had","do","does","did","would","could","should","may","might",
    "shall","must","need","want","like","get","got","go","went","come","came"}

HARD_SKILLS = [
    # Programming & Data Manipulation
    "python", "r", "sql", "matlab", "sas", "bash", "vba", "scala", "java", "c++", "javascript",
    "numpy", "pandas", "scipy", "dplyr", "data analysis", "data cleaning", "data wrangling",
    "etl", "data preprocessing", "feature engineering", "data modeling", "data pipelines", "data integration",
    "data mining", "data transformation", "data validation", "data quality", "data profiling",
    "web scraping", "api development", "json", "xml", "csv handling", "database design",
    
    # Advanced Programming Libraries
    "scikit-learn", "tensorflow", "keras", "pytorch", "xgboost", "lightgbm", "catboost",
    "statsmodels", "plotly", "bokeh", "altair", "streamlit", "flask", "django",
    "jupyter", "anaconda", "conda", "pip", "git", "github", "gitlab", "docker", "kubernetes",
    
    # Data Visualization & Business Intelligence
    "matplotlib", "seaborn", "ggplot2", "plotly", "tableau", "power bi", "qlik", "looker",
    "dash", "data visualization", "interactive visualization", "dashboarding", "reporting", 
    "business intelligence", "excel dashboards", "google data studio", "qlikview", "qliksense",
    "report automation", "kpi reporting", "presentation of insights", "insight communication",
    "data storytelling", "executive dashboards", "operational dashboards", "real-time dashboards",
    "infographics", "chart design", "visual analytics", "self-service bi", "embedded analytics",
    
    # Machine Learning & AI (Expanded)
    "machine learning", "deep learning", "artificial intelligence", "predictive modeling", 
    "classification", "regression", "clustering", "reinforcement learning", "neural networks", 
    "model evaluation", "model deployment", "model monitoring", "mlops", "feature selection",
    "dimensionality reduction", "ensemble methods", "random forest", "decision trees",
    "support vector machines", "logistic regression", "linear regression", "naive bayes",
    "k-means", "hierarchical clustering", "dbscan", "principal component analysis", "pca",
    "natural language processing", "nlp", "computer vision", "cv", "text mining",
    "sentiment analysis", "topic modeling", "recommendation systems", "forecasting models",
    "time series forecasting", "anomaly detection", "fraud detection", "churn prediction",
    "a/b testing", "multivariate testing", "experimental design", "causal inference",
    "hyperparameter tuning", "cross-validation", "model selection", "feature importance",
    
    # Statistics & Advanced Analytics
    "statistics", "probability", "linear algebra", "calculus", "bayesian statistics",
    "hypothesis testing", "statistical modeling", "time series analysis", "econometrics",
    "quantitative analysis", "optimization", "variance analysis", "financial statistics",
    "descriptive statistics", "inferential statistics", "correlation analysis", "regression analysis",
    "anova", "chi-square", "t-test", "z-test", "confidence intervals", "p-values",
    "statistical significance", "effect size", "power analysis", "sampling methods",
    "monte carlo simulation", "bootstrapping", "survival analysis", "multivariate analysis",
    "factor analysis", "discriminant analysis", "conjoint analysis", "cluster analysis",
    
    # Database & Big Data Technologies
    "sql server", "mysql", "postgresql", "oracle", "sqlite", "mongodb", "nosql",
    "hadoop", "spark", "pyspark", "hive", "pig", "kafka", "elasticsearch", "redis",
    "big data", "data engineering", "etl pipelines", "data warehousing", "data lakes",
    "snowflake", "redshift", "bigquery", "databricks", "azure synapse", "teradata",
    "cassandra", "hbase", "neo4j", "graph databases", "data modeling", "dimensional modeling",
    "star schema", "snowflake schema", "olap", "oltp", "data governance", "data lineage",
    
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "amazon web services", "microsoft azure",
    "s3", "ec2", "lambda", "azure functions", "cloud functions", "cloud computing",
    "serverless", "microservices", "api gateway", "cloud storage", "cloud databases",
    "terraform", "cloudformation", "ansible", "jenkins", "ci/cd", "devops",
    "containerization", "orchestration", "monitoring", "logging", "alerting",
    
    # Business Analysis & Domain Knowledge
    "market research", "financial modeling", "customer behavior analysis", "call center metrics",
    "real estate analytics", "business analytics", "kpi monitoring", "emerging technologies", 
    "ai platforms", "economics", "microeconomics", "macroeconomics", "sales analytics", 
    "marketing analytics", "pricing strategy", "consumer insights", "brand analytics", 
    "competitive analysis", "product management analytics", "campaign performance analysis", 
    "operations management", "management operations", "risk management", "risk analysis", 
    "evaluate performance", "business strategy", "supply chain analytics", "inventory analysis", 
    "sales forecasting", "financial analysis", "budgeting", "cost analysis", "profitability analysis",
    "revenue analysis", "margin analysis", "variance analysis", "trend analysis", "cohort analysis",
    "funnel analysis", "conversion analysis", "attribution modeling", "customer lifetime value",
    "customer acquisition cost", "churn analysis", "retention analysis", "segmentation analysis",
    "market sizing", "market penetration", "brand equity", "price elasticity", "demand forecasting",
    "inventory optimization", "supply chain optimization", "logistics analytics", "procurement analytics",
    
    # CRM & Marketing Tools
    "crm tools", "salesforce", "hubspot", "marketo", "pardot", "eloqua", "mailchimp",
    "google analytics", "google ads", "facebook ads", "linkedin ads", "sem", "seo",
    "social media analytics", "web analytics", "email marketing", "marketing automation",
    "lead scoring", "customer segmentation", "loyalty program analysis", "campaign optimization",
    "adobe analytics", "mixpanel", "amplitude", "segment", "kissmetrics", "hotjar",
    
    # Financial & Investment Analysis
    "financial modeling", "valuation models", "dcf", "discounted cash flow", "npv", "irr",
    "capm", "wacc", "financial ratios", "ratio analysis", "credit analysis", "risk modeling",
    "portfolio optimization", "asset pricing", "derivatives", "options pricing", "var",
    "value at risk", "stress testing", "scenario analysis", "sensitivity analysis",
    "monte carlo methods", "black-scholes", "binomial models", "fixed income", "equity analysis",
    "commodity analysis", "fx analysis", "algorithmic trading", "quantitative finance",
    
    # Specialized Analytics Tools
    "alteryx", "sas enterprise", "spss", "stata", "minitab", "jmp", "knime", "rapidminer",
    "weka", "orange", "h2o", "dataiku", "palantir", "sisense", "domo", "tibco spotfire",
    "mathematica", "wolfram", "origin", "sigmaplot", "prism", "jamovi", "jasp",
    
    # Productivity & Project Management
    "automation", "api integration", "excel", "advanced excel", "power query", "dax",
    "google sheets", "microsoft office", "project management tools", "jira", "confluence", 
    "notion", "asana", "trello", "monday.com", "smartsheet", "airtable", "slack",
    "teams", "zoom", "power automate", "zapier", "ifttt", "workflow automation",
    
    # Feasibility Studies & Economics
    "feasibility studies", "economic analysis", "cost-benefit analysis", "business case development",
    "market feasibility", "technical feasibility", "financial feasibility", "operational feasibility",
    "swot analysis", "pestle analysis", "porter's five forces", "business model canvas",
    "lean canvas", "value proposition", "competitive positioning", "market entry strategies",
    "go-to-market strategy", "product launch", "market validation", "customer discovery",
    "mvp development", "agile methodology", "scrum", "kanban", "design thinking",
    "user experience research", "customer journey mapping", "process optimization",
    "continuous improvement", "six sigma", "lean manufacturing", "kaizen", "tqm"
]

SOFT_SKILLS = [
    # Core Communication & Interpersonal Skills
    "communication", "verbal communication", "written communication", "presentation skills",
    "public speaking", "storytelling", "active listening", "interpersonal skills", "empathy",
    "emotional intelligence", "persuasion", "influencing", "negotiation", "conflict resolution",
    "diplomacy", "tact", "cultural sensitivity", "cross-cultural communication", "multilingual",
    "client communication", "stakeholder communication", "executive communication",
    "technical writing", "business writing", "report writing", "documentation skills",
    
    # Leadership & Management
    "leadership", "team leadership", "project leadership", "thought leadership", "mentoring", 
    "coaching", "team building", "team management", "people management", "talent development",
    "succession planning", "performance management", "feedback delivery", "motivation",
    "delegation", "empowerment", "change management", "organizational development",
    "strategic leadership", "visionary leadership", "servant leadership", "transformational leadership",
    "decision making", "strategic thinking", "executive presence", "board presentation",
    
    # Collaboration & Teamwork
    "teamwork", "collaboration", "cross-functional collaboration", "matrix management",
    "virtual team management", "remote collaboration", "partnership building", "relationship building",
    "networking", "community building", "alliance management", "vendor management",
    "supplier relationship management", "customer relationship management", "account management",
    "stakeholder management", "stakeholder engagement", "consensus building",
    
    # Problem Solving & Analysis
    "problem solving", "analytical thinking", "critical thinking", "strategic thinking",
    "systems thinking", "design thinking", "creative thinking", "innovative thinking",
    "logical reasoning", "deductive reasoning", "inductive reasoning", "pattern recognition",
    "root cause analysis", "troubleshooting", "debugging", "hypothesis testing",
    "research skills", "investigative skills", "fact-finding", "information gathering",
    "synthesis", "evaluation", "assessment", "judgment", "decision analysis",
    
    # Project & Time Management
    "project management", "program management", "portfolio management", "time management",
    "priority management", "resource management", "budget management", "scope management",
    "risk management", "quality management", "change control", "milestone tracking",
    "deadline management", "workflow optimization", "process improvement", "efficiency optimization",
    "productivity enhancement", "multitasking", "organization", "planning", "scheduling",
    "coordination", "logistics", "execution", "monitoring", "control", "closure",
    
    # Adaptability & Learning
    "adaptability", "flexibility", "agility", "resilience", "stress management", "composure",
    "emotional regulation", "self-awareness", "self-management", "continuous learning",
    "lifelong learning", "curiosity", "growth mindset", "learning agility", "knowledge transfer",
    "skill development", "professional development", "career development", "upskilling",
    "reskilling", "innovation", "creativity", "experimentation", "prototyping", "iteration",
    
    # Business & Commercial Acumen
    "business acumen", "commercial awareness", "market knowledge", "industry expertise",
    "competitive intelligence", "customer focus", "customer-centricity", "service orientation",
    "quality focus", "excellence orientation", "results orientation", "performance orientation",
    "outcome focus", "value creation", "profit consciousness", "cost awareness", "roi focus",
    "business development", "sales acumen", "marketing acumen", "financial acumen",
    
    # Data & Analytics Specific Soft Skills
    "data storytelling", "insight generation", "pattern identification", "trend analysis",
    "business translation", "technical translation", "complexity simplification", "visualization design",
    "dashboard design", "report optimization", "data-driven mindset", "evidence-based thinking",
    "scientific approach", "methodical thinking", "attention to detail", "accuracy focus",
    "quality assurance mindset", "validation mindset", "verification skills", "audit mindset",
    "compliance awareness", "governance mindset", "ethical data use", "privacy awareness",
    
    # Client & Stakeholder Management
    "client engagement", "client relationship management", "customer success", "account growth",
    "client retention", "client satisfaction", "service delivery", "expectation management",
    "requirement gathering", "needs analysis", "solution design", "consultative approach",
    "advisory skills", "trusted advisor", "business partnering", "value demonstration",
    "roi demonstration", "business case development", "proposal writing", "contract negotiation",
    
    # Training & Knowledge Sharing
    "training", "teaching", "knowledge sharing", "mentoring trainees", "skill transfer",
    "workshop facilitation", "training design", "curriculum development", "adult learning",
    "peer coaching", "reverse mentoring", "community of practice", "best practice sharing",
    "lessons learned", "post-mortem facilitation", "retrospective facilitation",
    
    # Innovation & Change
    "innovation management", "change leadership", "transformation leadership", "digital transformation",
    "cultural change", "process reengineering", "business process improvement", "optimization",
    "automation mindset", "efficiency mindset", "lean thinking", "waste elimination",
    "value stream mapping", "continuous improvement mindset", "kaizen mindset", "agile mindset",
    "scrum master", "product owner", "design sprint facilitation", "ideation facilitation",
    
    # Risk & Compliance
    "risk awareness", "risk assessment", "risk mitigation", "compliance mindset", "audit readiness",
    "internal controls", "governance awareness", "regulatory knowledge", "policy adherence",
    "ethical conduct", "integrity", "transparency", "accountability", "responsibility",
    "fiduciary responsibility", "stewardship", "due diligence", "quality assurance",
    
    # Sales & Marketing Soft Skills
    "sales orientation", "revenue generation", "pipeline management", "lead qualification",
    "opportunity identification", "relationship selling", "solution selling", "consultative selling",
    "value-based selling", "competitive selling", "objection handling", "closing skills",
    "follow-up", "customer advocacy", "reference building", "case study development",
    "thought leadership", "content marketing", "social selling", "digital marketing",
    "brand building", "reputation management", "crisis communication", "pr skills"
]

def normalize(text):
    """Enhanced normalization with better handling of special characters and compound terms"""
    text = text.lower()
    # Preserve important compound terms and technical terms
    text = re.sub(r'[_\-\•\,\(\)\[\]\{\}\:\;\|]', ' ', text)
    # Handle common separators that should become spaces
    text = re.sub(r'[/\\&]', ' ', text)
    # Preserve dots in version numbers and percentages
    text = re.sub(r'(?<!\d)\.(?!\d)', ' ', text)
    # Clean up multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    """Enhanced tokenization with better compound word and technical term handling"""
    text = normalize(text)
    # Find all potential tokens including compound terms
    tokens = []
    
    # First pass: get individual words
    words = re.findall(r"[a-z0-9\+\#\.\%]+", text)
    words = [w for w in words if w not in STOPWORDS and len(w) > 1]
    tokens.extend(words)
    
    # Second pass: look for common compound terms in the full text
    compound_patterns = [
        r"data\s+analysis", r"machine\s+learning", r"business\s+intelligence",
        r"data\s+science", r"statistical\s+modeling", r"project\s+management",
        r"customer\s+relationship\s+management", r"supply\s+chain", r"financial\s+modeling",
        r"market\s+research", r"competitive\s+analysis", r"feasibility\s+studies",
        r"cost\s+benefit\s+analysis", r"return\s+on\s+investment", r"key\s+performance\s+indicators"
    ]
    
    for pattern in compound_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            compound_term = match.replace(' ', ' ')
            tokens.append(compound_term)
    
    return list(set(tokens))  # Remove duplicates

def fuzzy_match(word, candidate_list, threshold=0.80):
    """Enhanced fuzzy matching with better similarity detection"""
    word_normalized = normalize(word)
    for candidate in candidate_list:
        candidate_normalized = normalize(candidate)
        
        # Exact match
        if word_normalized == candidate_normalized:
            return True
            
        # Substring match for compound terms
        if len(word_normalized) > 5 and word_normalized in candidate_normalized:
            return True
        if len(candidate_normalized) > 5 and candidate_normalized in word_normalized:
            return True
            
        # Fuzzy match
        ratio = difflib.SequenceMatcher(None, word_normalized, candidate_normalized).ratio()
        if ratio >= threshold:
            return True
            
        # Handle partial matches for compound skills
        word_parts = word_normalized.split()
        candidate_parts = candidate_normalized.split()
        if len(word_parts) > 1 and len(candidate_parts) > 1:
            common_parts = set(word_parts) & set(candidate_parts)
            if len(common_parts) >= min(len(word_parts), len(candidate_parts)) * 0.6:
                return True
    
    return False

def enhanced_skill_extraction(text, skill_list):
    """Enhanced skill extraction with better compound term detection"""
    found_skills = []
    text_normalized = normalize(text)
    
    for skill in skill_list:
        skill_normalized = normalize(skill)
        
        # Direct substring search for compound terms
        if len(skill_normalized.split()) > 1:
            if skill_normalized in text_normalized:
                found_skills.append(skill)
                continue
        
        # Token-based matching
        text_tokens = set(tokenize(text))
        if skill_normalized in text_tokens or fuzzy_match(skill_normalized, text_tokens):
            found_skills.append(skill)
    
    return found_skills

def analyze_cv(cv_text, jd_text):
    """Enhanced CV analysis with improved scoring algorithm"""
    cv_tokens = set(tokenize(cv_text))
    jd_tokens = set(tokenize(jd_text))

    # Enhanced skill filtering based on JD relevance
    relevant_hard = enhanced_skill_extraction(jd_text, HARD_SKILLS)
    relevant_soft = enhanced_skill_extraction(jd_text, SOFT_SKILLS)

    # Enhanced skill matching in CV
    found_hard = enhanced_skill_extraction(cv_text, relevant_hard)
    missing_hard = [s for s in relevant_hard if s not in found_hard]

    found_soft = enhanced_skill_extraction(cv_text, relevant_soft)
    missing_soft = [s for s in relevant_soft if s not in found_soft]

    # Enhanced keyword analysis with better weighting
    present, missing, fuzzy = [], [], []
    for kw in jd_tokens:
        if len(kw) < 3:  # Skip very short keywords
            continue
        if kw in cv_tokens:
            present.append(kw)
        elif fuzzy_match(kw, cv_tokens):
            fuzzy.append(kw)
        else:
            missing.append(kw)

    # Enhanced sections check
    sections = {
        "summary": ["summary", "profile", "objective", "about"],
        "experience": ["experience", "employment", "work history", "career"],
        "education": ["education", "academic", "qualifications", "degree"],
        "skills": ["skills", "competencies", "expertise", "abilities"],
        "projects": ["projects", "portfolio", "accomplishments"],
        "certifications": ["certifications", "certificates", "credentials", "licenses"]
    }
    
    found_sections = []
    cv_lower = cv_text.lower()
    for section, keywords in sections.items():
        if any(kw in cv_lower for kw in keywords):
            found_sections.append(section)

    # Enhanced measurable results detection
    measurable_patterns = [
        r"\d+%", r"\$\d+", r"\d+k", r"\d+m", r"\d+\s*million",
        r"increased.*\d+", r"improved.*\d+", r"reduced.*\d+",
        r"achieved.*\d+", r"exceeded.*\d+", r"generated.*\d+",
        r"\d+\s*years?\s+of\s+experience", r"\d+\+\s*years?"
    ]
    
    measurable_count = sum(len(re.findall(pattern, cv_text, re.IGNORECASE)) 
                          for pattern in measurable_patterns)
    measurable_score = min(measurable_count / 5, 1.0)  # Normalize to 0-1

    # Word count analysis
    words = cv_text.split()
    word_count = len(words)
    optimal_length = 800  # Optimal CV length
    length_score = min(word_count / optimal_length, 1.0) * 0.8 + 0.2  # Base score of 0.2

    # Enhanced scoring with better weighting
    total_keywords = len(present) + len(missing) + len(fuzzy)
    keyword_score = ((len(present) * 1.0 + len(fuzzy) * 0.6) / max(1, total_keywords)) if total_keywords > 0 else 1.0
    
    hard_score = len(found_hard) / max(1, len(relevant_hard)) if relevant_hard else 1
    soft_score = len(found_soft) / max(1, len(relevant_soft)) if relevant_soft else 1
    section_score = len(found_sections) / len(sections)

    # Final score calculation with improved weights
    final_score = (
        0.35 * keyword_score +      # Reduced weight for keywords
        0.30 * hard_score +         # Increased weight for hard skills
        0.15 * soft_score +         # Maintained soft skills weight
        0.10 * section_score +      # Maintained section weight
        0.10 * (0.6 * length_score + 0.4 * measurable_score)  # Enhanced content quality
    ) * 100

    return {
        "final_score": round(final_score, 1),
        "keywords_present": present,
        "keywords_missing": missing,
        "keywords_fuzzy": fuzzy,
        "hard_skills_found": found_hard,
        "hard_skills_missing": missing_hard,
        "soft_skills_found": found_soft,
        "soft_skills_missing": missing_soft,
        "sections_found": found_sections,
        "measurable_results": measurable_count > 0,
        "measurable_count": measurable_count,
        "word_count": word_count,
        "issues": {
            "hard_skills": len(missing_hard),
            "soft_skills": len(missing_soft),
            "sections_missing": [s for s in sections if s not in found_sections],
            "low_word_count": word_count < 600,
            "missing_measurable": measurable_count == 0,
            "too_long": word_count > 1200
        }
    }

def analyze_formatting(cv_text):
    """Enhanced formatting analysis"""
    results = {}
    lines = cv_text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    paragraphs = [p for p in cv_text.split('\n\n') if p.strip()]
    
    # Analyze paragraph lengths
    long_paragraphs = [p for p in paragraphs if len(p.split()) > 50]
    
    # Detect bullet points and structure
    bullet_lines = [line for line in lines if re.match(r'^\s*[\-\*\•]\s', line)]
    numbered_lines = [line for line in lines if re.match(r'^\s*\d+[\.\)]\s', line)]
    
    # Analyze text structure
    results['structure_score'] = min(100, (len(bullet_lines) + len(numbered_lines)) * 5)
    results['long_paragraphs'] = len(long_paragraphs)
    results['bullet_usage'] = len(bullet_lines)
    results['numbered_usage'] = len(numbered_lines)
    results['line_count'] = len(non_empty_lines)
    results['paragraph_count'] = len(paragraphs)
    
    # Check for contact information
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    
    has_email = bool(re.search(email_pattern, cv_text))
    has_phone = bool(re.search(phone_pattern, cv_text))
    
    results['contact_info'] = {
        'email': has_email,
        'phone': has_phone,
        'score': (has_email + has_phone) * 50
    }
    
    # Check for URLs/LinkedIn
    url_pattern = r'https?://[^\s]+|www\.[^\s]+|linkedin\.com/in/[^\s]+'
    has_urls = bool(re.search(url_pattern, cv_text, re.IGNORECASE))
    results['web_presence'] = has_urls
    
    # Overall formatting score
    format_score = (
        results['structure_score'] * 0.3 +
        results['contact_info']['score'] * 0.4 +
        (100 if has_urls else 0) * 0.1 +
        max(0, 100 - results['long_paragraphs'] * 10) * 0.2
    )
    
    results['overall_format_score'] = min(100, format_score)
    
    return results

def generate_improvement_tips(analysis_result, formatting_result):
    """Generate comprehensive improvement tips"""
    tips = []
    
    # Hard skills tips
    if analysis_result['issues']['hard_skills'] > 0:
        missing_critical = analysis_result['hard_skills_missing'][:5]
        tips.append(f"🎯 Add these key technical skills: {', '.join(missing_critical)}")
    
    # Soft skills tips
    if analysis_result['issues']['soft_skills'] > 0:
        missing_soft = analysis_result['soft_skills_missing'][:3]
        tips.append(f"🤝 Include these soft skills: {', '.join(missing_soft)}")
    
    # Content quality tips
    if analysis_result['measurable_count'] < 3:
        tips.append("📊 Add more quantified achievements (percentages, dollar amounts, metrics)")
    
    if analysis_result['word_count'] < 600:
        tips.append("📝 Expand your CV content - aim for 800-1000 words for better detail")
    elif analysis_result['word_count'] > 1200:
        tips.append("✂️ Consider condensing your CV - it's quite lengthy")
    
    # Section tips
    missing_sections = analysis_result['issues']['sections_missing']
    if missing_sections:
        tips.append(f"🗂️ Add missing sections: {', '.join(missing_sections[:3])}")
    
    # Formatting tips
    if formatting_result['long_paragraphs'] > 2:
        tips.append("📄 Break down long paragraphs for better readability")
    
    if formatting_result['bullet_usage'] < 5:
        tips.append("• Use more bullet points to highlight achievements and responsibilities")
    
    if not formatting_result['contact_info']['email']:
        tips.append("📧 Include your email address")
    
    if not formatting_result['contact_info']['phone']:
        tips.append("📱 Include your phone number")
    
    if not formatting_result['web_presence']:
        tips.append("🌐 Add your LinkedIn profile or portfolio website")
    
    # Keywords tips
    if len(analysis_result['keywords_missing']) > 10:
        critical_missing = analysis_result['keywords_missing'][:5]
        tips.append(f"🔍 Include these important keywords: {', '.join(critical_missing)}")
    
    return tips

def read_docx(file_path):
    """Read content from Word document"""
    try:
        doc = docx.Document(file_path)
        content = []
        for paragraph in doc.paragraphs:
            content.append(paragraph.text)
        return '\n'.join(content)
    except Exception as e:
        raise Exception(f"Error reading Word document: {e}")

def read_pdf(file_path):
    """Read content from PDF"""
    try:
        content = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    content += page_text + "\n"
        return content
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")

def read_text_file(file_path):
    """Read content from text file with encoding detection"""
    encodings = ['utf-8', 'cp1252', 'iso-8859-1', 'utf-16']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise Exception("Could not decode the text file. Please ensure it's in a supported encoding.")

# ---------- Enhanced GUI ----------
class EnhancedATSOptimizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Professional ATS CV Optimizer - Enhanced Edition")
        self.root.geometry("1300x750")
        self.root.state('zoomed')  # للويندوز - يفتح الويندو maximized
        self.root.configure(bg="#f8fafc")
        self.root.minsize(1200, 800)
        
        # Enhanced styling
        self.setup_styles()
        
        # Main container with padding
        main_container = tk.Frame(self.root, bg="#f8fafc")
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        content_frame = tk.Frame(main_container, bg="#f8fafc")
        content_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Left panel (Results Dashboard)
        left_panel = tk.Frame(content_frame, bg="white", relief='solid', bd=1)
        left_panel.pack(side='left', fill='y', padx=(0, 15))
        left_panel.configure(width=280)
        left_panel.pack_propagate(False)
        
        # Right panel (Input and Analysis)
        right_panel = tk.Frame(content_frame, bg="#f8fafc")
        right_panel.pack(side='right', fill='both', expand=True)
        
        self.create_left_panel(left_panel)
        self.create_right_panel(right_panel)
        
        # Initialize data
        self.analysis_result = None
        self.formatting_result = None
        self.current_file_path = None
        self._set_default_values()

    def setup_styles(self):
        """Setup enhanced UI styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#1a365d")
        style.configure("Subheader.TLabel", font=("Segoe UI", 12), foreground="#64748b")
        style.configure("Score.TLabel", font=("Segoe UI", 28, "bold"), foreground="#059669")
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), foreground="#374151")
        style.configure("Detail.TLabel", font=("Segoe UI", 9), foreground="#6b7280")
        style.configure("Success.TButton", background="#10b981", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", background="#3b82f6", foreground="white", font=("Segoe UI", 10, "bold"))
        style.configure("Secondary.TButton", background="#64748b", foreground="white", font=("Segoe UI", 10))

    def create_header(self, parent):
        """Create application header"""
        header_frame = tk.Frame(parent, bg="#f8fafc")
        header_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="Professional ATS CV Optimizer", style="Header.TLabel")
        title_label.pack(anchor='w')
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Optimize your CV for Data Analysis, Business Intelligence, Marketing & Sales roles", 
                                  style="Subheader.TLabel")
        subtitle_label.pack(anchor='w', pady=(5, 0))

    def create_left_panel(self, parent):
        """Create enhanced left panel with results dashboard"""
        # Header
        header = tk.Frame(parent, bg="white")
        header.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header, text="CV Analysis Results", 
                 font=("Segoe UI", 14, "bold"), background="white").pack(anchor='w')
        ttk.Label(header, text="Comprehensive ATS Compatibility Check", 
                 font=("Segoe UI", 10), background="white", foreground="#64748b").pack(anchor='w')
        
        # Score Gauge Section
        gauge_section = tk.Frame(parent, bg="white")
        gauge_section.pack(pady=10)
        
        self.gauge_canvas = tk.Canvas(gauge_section, width=200, height=200, bg="white", highlightthickness=0)
        self.gauge_canvas.pack()
        self._draw_enhanced_gauge(0)
        
        # Score interpretation
        score_info = tk.Frame(parent, bg="white")
        score_info.pack(pady=10, padx=20, fill='x')
        self.score_status_label = ttk.Label(score_info, text="Upload CV to analyze", 
                                          font=("Segoe UI", 10), background="white", foreground="#64748b")
        self.score_status_label.pack()
        
        # Action Buttons
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack(pady=15, padx=20, fill='x')
        
        analyze_btn = tk.Button(button_frame, text="🔍 Analyze CV", 
                               command=self.analyze_cv_gui,
                               bg="#10b981", fg="white", font=("Segoe UI", 10, "bold"),
                               relief='flat', padx=20, pady=8)
        analyze_btn.pack(fill='x', pady=(0, 10))
        
        optimize_btn = tk.Button(button_frame, text="🚀 AI Optimize", 
                                command=self.optimize_cv,
                                bg="#f59e0b", fg="white", font=("Segoe UI", 10, "bold"),
                                relief='flat', padx=20, pady=8)
        optimize_btn.pack(fill='x')
        
        # Progress Metrics
        metrics_frame = tk.LabelFrame(parent, text="Performance Metrics", 
                                    bg="white", font=("Segoe UI", 11, "bold"))
        metrics_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        self.progress_items = {}
        metrics = [
            ("🔍 Keyword Match", "keyword_match"),
            ("💼 Hard Skills", "hard_skills"), 
            ("🤝 Soft Skills", "soft_skills"),
            ("📊 Content Quality", "content_quality"),
            ("🎨 Format Score", "formatting")
        ]
        
        for display_name, key in metrics:
            self.create_progress_item(metrics_frame, display_name, key)
        
        # Tips Section
        tips_frame = tk.LabelFrame(parent, text="Quick Tips", 
                                 bg="white", font=("Segoe UI", 11, "bold"))
        tips_frame.pack(fill='both', expand=True, padx=20, pady=(10, 20))
        
        self.tips_text = tk.Text(tips_frame, height=8, font=("Segoe UI", 9), 
                               wrap=tk.WORD, bg="#f8fafc", relief='flat', padx=10, pady=10)
        tips_scrollbar = ttk.Scrollbar(tips_frame, orient="vertical", command=self.tips_text.yview)
        self.tips_text.configure(yscrollcommand=tips_scrollbar.set)
        
        self.tips_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        tips_scrollbar.pack(side="right", fill="y", pady=5)

    def create_progress_item(self, parent, name, key):
        """Create individual progress item"""
        item_frame = tk.Frame(parent, bg="white")
        item_frame.pack(fill='x', padx=10, pady=5)
        
        label = tk.Label(item_frame, text=name, bg="white", font=("Segoe UI", 9, "bold"))
        label.pack(anchor='w')
        
        progress_container = tk.Frame(item_frame, bg="white")
        progress_container.pack(fill='x', pady=(2, 0))
        
        progress_bar = ttk.Progressbar(progress_container, orient='horizontal', 
                                     length=220, mode='determinate')
        progress_bar.pack(side='left', fill='x', expand=True)
        
        percentage_label = tk.Label(progress_container, text="0%", bg="white", 
                                  font=("Segoe UI", 8), width=4)
        percentage_label.pack(side='right', padx=(5, 0))
        
        self.progress_items[key] = {
            'bar': progress_bar,
            'label': percentage_label
        }

    def create_right_panel(self, parent):
        """Create enhanced right panel with horizontal layout"""
        
        # Top section - horizontal layout for inputs
        top_section = tk.Frame(parent, bg="#f8fafc")
        top_section.pack(fill='x', pady=(0, 15))
        
        # Input Section with horizontal layout
        input_frame = tk.LabelFrame(top_section, text="📝 Input Data", 
                                bg="#f8fafc", font=("Segoe UI", 11, "bold"))
        input_frame.pack(fill='x')
        
        # Container for side-by-side inputs
        inputs_container = tk.Frame(input_frame, bg="#f8fafc")
        inputs_container.pack(fill='x', padx=10, pady=10)
        
        # Left side - Job Description
        jd_frame = tk.Frame(inputs_container, bg="#f8fafc")
        jd_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        jd_label = tk.Label(jd_frame, text="Job Description:", 
                        bg="#f8fafc", font=("Segoe UI", 10, "bold"))
        jd_label.pack(anchor='w', pady=(0, 3))
        
        jd_container = tk.Frame(jd_frame, bg="white", relief='solid', bd=1)
        jd_container.pack(fill='both', expand=True)
        
        self.jd_text = scrolledtext.ScrolledText(jd_container, height=4, 
                                            font=("Consolas", 9), wrap=tk.WORD,
                                            relief='flat', padx=8, pady=8)
        self.jd_text.pack(fill='both', expand=True)
        
        # Right side - CV Input
        cv_frame = tk.Frame(inputs_container, bg="#f8fafc")
        cv_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        cv_header = tk.Frame(cv_frame, bg="#f8fafc")
        cv_header.pack(fill='x', pady=(0, 3))
        
        cv_label = tk.Label(cv_header, text="Your CV Content:", 
                        bg="#f8fafc", font=("Segoe UI", 10, "bold"))
        cv_label.pack(side='left')
        
        # Upload button next to CV label
        upload_small_btn = tk.Button(cv_header, text="📁 Upload PDF", 
                                command=self.upload_cv_file,
                                bg="#3b82f6", fg="white", font=("Segoe UI", 8),
                                relief='flat', padx=10, pady=2)
        upload_small_btn.pack(side='right')
        
        cv_container = tk.Frame(cv_frame, bg="white", relief='solid', bd=1)
        cv_container.pack(fill='both', expand=True)
        
        self.cv_text = scrolledtext.ScrolledText(cv_container, height=4, 
                                            font=("Consolas", 9), wrap=tk.WORD,
                                            relief='flat', padx=8, pady=8)
        self.cv_text.pack(fill='both', expand=True)
        
        # Bottom section - Results (bigger area)
        results_frame = tk.LabelFrame(parent, text="📊 Analysis Results", 
                                    bg="#f8fafc", font=("Segoe UI", 12, "bold"))
        results_frame.pack(fill='both', expand=True)
        
        self.create_results_tabs(results_frame)

    def create_results_tabs(self, parent):
        """Create enhanced results tabs"""
        tab_container = tk.Frame(parent, bg="#f8fafc")
        tab_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        self.notebook = ttk.Notebook(tab_container)
        self.notebook.pack(fill='both', expand=True)
        
        # Define tabs with icons and descriptions
        tabs_info = [
            ("📋 Summary", "summary", "Overall analysis results"),
            ("🛠️ Hard Skills", "hard_skills", "Technical skills analysis"),
            ("🤝 Soft Skills", "soft_skills", "Interpersonal skills analysis"), 
            ("📄 Content Analysis", "content", "Structure and content quality"),
            ("💡 Recommendations", "tips", "Improvement suggestions"),
            ("🤖 AI Optimized CV", "optimized", "AI-enhanced version"),
            ("🎨 Formatting Check", "formatting", "Layout and presentation")
        ]
        
        self.tab_widgets = {}
        
        for tab_name, tab_key, description in tabs_info:
            tab_frame = tk.Frame(self.notebook, bg="white")
            self.notebook.add(tab_frame, text=tab_name)
            
            # Tab header with description
            header = tk.Frame(tab_frame, bg="#f8fafc")
            header.pack(fill='x', padx=10, pady=10)
            header.pack_propagate(False)
            
            desc_label = tk.Label(header, text=description, 
                                bg="#f8fafc", font=("Segoe UI", 10), 
                                foreground="#64748b")
            desc_label.pack(anchor='w', pady=8)
            
            # Content area
            content_frame = tk.Frame(tab_frame, bg="white")
            content_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
            
            text_widget = scrolledtext.ScrolledText(content_frame, 
                                                  font=("Segoe UI", 10), 
                                                  wrap=tk.WORD, relief='flat',
                                                  bg="white", padx=15, pady=15)
            text_widget.pack(fill='both', expand=True)
            
            self.tab_widgets[tab_key] = text_widget

    def _draw_enhanced_gauge(self, percent):
        """Draw enhanced circular progress gauge"""
        c = self.gauge_canvas
        c.delete("all")
        
        w, h = 200, 200
        cx, cy = w//2, h//2
        outer_r = 80
        inner_r = 65
        
        # Background circle
        c.create_oval(cx-outer_r-15, cy-outer_r-15, cx+outer_r+15, cy+outer_r+15, 
                     fill="#f1f5f9", outline="")
        
        # Outer ring background
        c.create_oval(cx-outer_r, cy-outer_r, cx+outer_r, cy+outer_r, 
                     fill="#ffffff", outline="#e2e8f0", width=2)
        
        # Progress track
        c.create_arc(cx-outer_r, cy-outer_r, cx+outer_r, cy+outer_r, 
                    start=90, extent=360, style='arc', width=20, outline="#e2e8f0")
        
        # Progress arc
        if percent > 0:
            extent = 360 * min(percent, 100) / 100
            color = self._get_score_color(percent)
            c.create_arc(cx-outer_r, cy-outer_r, cx+outer_r, cy+outer_r, 
                        start=90, extent=-extent, style='arc', width=20, outline=color)
        
        # Inner circle
        c.create_oval(cx-inner_r, cy-inner_r, cx+inner_r, cy+inner_r, 
                     fill="#ffffff", outline="#f1f5f9", width=3)
        
        # Score text
        c.create_text(cx, cy-10, text=f"{percent}%", 
                     font=("Segoe UI", 24, "bold"), fill="#1f2937")
        
        # Status text
        status = self._get_score_status(percent)
        c.create_text(cx, cy+20, text=status, 
                     font=("Segoe UI", 12, "bold"), fill=self._get_score_color(percent))
        
        # Small metrics around the gauge
        c.create_text(cx, cy+45, text="ATS Compatibility Score", 
                     font=("Segoe UI", 10), fill="#6b7280")

    def _get_score_color(self, percent):
        """Get color based on score"""
        if percent >= 85:
            return "#059669"  # Green
        elif percent >= 70:
            return "#d97706"  # Amber
        elif percent >= 50:
            return "#dc2626"  # Red
        else:
            return "#7c2d12"  # Dark red

    def _get_score_status(self, percent):
        """Get status text based on score"""
        if percent >= 85:
            return "Excellent"
        elif percent >= 70:
            return "Good"
        elif percent >= 50:
            return "Fair"
        else:
            return "Needs Work"

    def update_progress_item(self, key, value, max_value=100):
        """Update progress bar and percentage"""
        if key in self.progress_items:
            percentage = min(100, (value / max_value) * 100) if max_value > 0 else 0
            self.progress_items[key]['bar']['value'] = percentage
            self.progress_items[key]['label'].config(text=f"{int(percentage)}%")

    def _set_default_values(self):
        """Set default progress values"""
        defaults = {
            "keyword_match": 45,
            "hard_skills": 60,
            "soft_skills": 70,
            "content_quality": 55,
            "formatting": 65
        }
        
        for key, value in defaults.items():
            self.update_progress_item(key, value)
        
        # Set default tips
        default_tips = [
            "💡 Upload your CV file to get started",
            "📝 Paste a relevant job description",
            "🎯 The system will analyze keyword matches",
            "📊 Get specific improvement recommendations",
            "🚀 Use AI optimization for enhanced results"
        ]
        
        self.tips_text.delete("1.0", "end")
        for tip in default_tips:
            self.tips_text.insert("end", f"{tip}\n\n")

    def upload_cv_file(self):
        """Enhanced file upload with multiple format support"""
        file_path = filedialog.askopenfilename(
            title="Select CV File",
            filetypes=[
                ("All supported", "*.pdf;*.docx;*.doc;*.txt"),
                ("PDF files", "*.pdf"),
                ("Word documents", "*.docx;*.doc"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            content = ""
            file_ext = file_path.lower().split('.')[-1]
            
            if file_ext == 'pdf':
                content = read_pdf(file_path)
            elif file_ext in ['docx', 'doc']:
                content = read_docx(file_path)
            elif file_ext == 'txt':
                content = read_text_file(file_path)
            else:
                messagebox.showwarning("Unsupported Format", 
                                     "Please select a PDF, Word document, or text file.")
                return
            
            if not content.strip():
                messagebox.showwarning("Empty File", 
                                     "The selected file appears to be empty or could not be read.")
                return
            
            self.cv_text.delete("1.0", "end")
            self.cv_text.insert("1.0", content)
            self.current_file_path = file_path
            
            filename = file_path.split('/')[-1]
            messagebox.showinfo("Upload Successful", 
                              f"Successfully loaded: {filename}\n\nClick 'Analyze CV' to proceed.")
            
        except Exception as e:
            messagebox.showerror("Upload Error", f"Could not load file:\n{str(e)}")

    def analyze_cv_gui(self):
        """Enhanced CV analysis with comprehensive feedback"""
        cv_content = self.cv_text.get("1.0", "end").strip()
        jd_content = self.jd_text.get("1.0", "end").strip()
        
        if not cv_content:
            messagebox.showwarning("Missing CV", "Please provide your CV content or upload a CV file.")
            return
        
        if not jd_content:
            messagebox.showwarning("Missing Job Description", 
                                 "Please paste the job description you're targeting.")
            return
        
        try:
            # Perform analysis
            self.analysis_result = analyze_cv(cv_content, jd_content)
            print(f"Analysis completed. Hard skills found: {len(self.analysis_result['hard_skills_found'])}")
            print(f"Hard skills missing: {len(self.analysis_result['hard_skills_missing'])}")
            self.formatting_result = analyze_formatting(cv_content)
            
            # Update gauge
            score = self.analysis_result["final_score"]
            self._draw_enhanced_gauge(int(score))
            
            # Update status
            status_text = f"{self._get_score_status(score)} - {score}% ATS Match"
            self.score_status_label.config(text=status_text, 
                                         foreground=self._get_score_color(score))
            
            # Update progress bars
            self.update_analysis_metrics()
            
            # Update all tabs
            self.update_all_tabs()
            
            # Update tips
            self.update_tips_section()
            
            messagebox.showinfo("Analysis Complete", 
                              f"CV analysis completed!\n\nATS Compatibility: {score}%\n\nCheck the results tabs for detailed insights.")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{str(e)}")

    def update_analysis_metrics(self):
        """Update progress bars based on analysis results"""
        if not self.analysis_result:
            return
        
        r = self.analysis_result
        
        # Keyword match score
        total_kw = len(r['keywords_present']) + len(r['keywords_missing']) + len(r['keywords_fuzzy'])
        kw_score = ((len(r['keywords_present']) + 0.6 * len(r['keywords_fuzzy'])) / max(1, total_kw)) * 100
        self.update_progress_item("keyword_match", kw_score)
        
        # Hard skills score  
        hard_total = len(r['hard_skills_found']) + len(r['hard_skills_missing'])
        hard_score = (len(r['hard_skills_found']) / max(1, hard_total)) * 100
        self.update_progress_item("hard_skills", hard_score)
        
        # Soft skills score
        soft_total = len(r['soft_skills_found']) + len(r['soft_skills_missing'])
        soft_score = (len(r['soft_skills_found']) / max(1, soft_total)) * 100
        self.update_progress_item("soft_skills", soft_score)
        
        # Content quality (sections + measurable results + word count)
        sections_score = (len(r['sections_found']) / 6) * 100
        word_score = min(r['word_count'] / 800, 1.0) * 100
        measurable_score = (r['measurable_count'] / 5) * 100
        content_score = (sections_score * 0.4 + word_score * 0.3 + measurable_score * 0.3)
        self.update_progress_item("content_quality", content_score)
        
        # Formatting score
        if self.formatting_result:
            format_score = self.formatting_result.get('overall_format_score', 65)
            self.update_progress_item("formatting", format_score)

    def update_all_tabs(self):
        """Update content in all result tabs"""
        if not self.analysis_result:
            return
        
        r = self.analysis_result
        f = self.formatting_result
        
        # Summary tab
        self.update_summary_tab(r, f)
        
        # Hard skills tab
        try:
            self.update_skills_tab(r, 'hard_skills', r['hard_skills_found'], r['hard_skills_missing'])
            print(f"Hard Skills Found: {len(r['hard_skills_found'])}")  # للتحقق
            print(f"Hard Skills Missing: {len(r['hard_skills_missing'])}")  # للتحقق
        except Exception as e:
            print(f"Error updating hard skills tab: {e}")

        try:
            self.update_skills_tab(r, 'soft_skills', r['soft_skills_found'], r['soft_skills_missing'])
            print(f"Soft Skills Found: {len(r['soft_skills_found'])}")  # للتحقق
            print(f"Soft Skills Missing: {len(r['soft_skills_missing'])}")  # للتحقق
        except Exception as e:
            print(f"Error updating soft skills tab: {e}")
        
        # Content analysis tab
        self.update_content_tab(r, f)
        
        # Tips tab
        self.update_recommendations_tab(r, f)
        
        # Formatting tab
        self.update_formatting_tab(f)

    def update_summary_tab(self, analysis, formatting):
        """Update summary tab with comprehensive overview"""
        widget = self.tab_widgets['summary']
        widget.delete("1.0", "end")
        
        # Header
        widget.insert("end", "🎯 CV ANALYSIS SUMMARY\n", "header")
        widget.insert("end", "=" * 50 + "\n\n", "separator")
        
        # Overall Score
        score = analysis['final_score']
        status = self._get_score_status(score)
        widget.insert("end", f"📊 ATS Compatibility Score: {score}% ({status})\n\n", "score")
        
        # Key Metrics
        widget.insert("end", "📈 KEY METRICS\n", "subheader")
        widget.insert("end", f"• Word Count: {analysis['word_count']} words\n")
        widget.insert("end", f"• Measurable Results: {analysis['measurable_count']} found\n")
        widget.insert("end", f"• Sections Found: {len(analysis['sections_found'])}/6\n")
        widget.insert("end", f"• Keywords Present: {len(analysis['keywords_present'])}\n")
        widget.insert("end", f"• Keywords Missing: {len(analysis['keywords_missing'])}\n\n")
        
        # Skills Summary
        widget.insert("end", "🛠️ SKILLS ANALYSIS\n", "subheader")
        widget.insert("end", f"• Hard Skills Found: {len(analysis['hard_skills_found'])}\n")
        widget.insert("end", f"• Hard Skills Missing: {len(analysis['hard_skills_missing'])}\n")
        widget.insert("end", f"• Soft Skills Found: {len(analysis['soft_skills_found'])}\n")
        widget.insert("end", f"• Soft Skills Missing: {len(analysis['soft_skills_missing'])}\n\n")
        
        # Top Missing Keywords (limited to avoid clutter)
        if analysis['keywords_missing']:
            widget.insert("end", "🔍 TOP MISSING KEYWORDS\n", "subheader")
            top_missing = analysis['keywords_missing'][:10]
            for kw in top_missing:
                widget.insert("end", f"• {kw}\n")
            if len(analysis['keywords_missing']) > 10:
                widget.insert("end", f"... and {len(analysis['keywords_missing']) - 10} more\n")
            widget.insert("end", "\n")
        
        # Issues Summary
        issues = analysis['issues']
        if any(issues.values()):
            widget.insert("end", "⚠️ ISSUES TO ADDRESS\n", "subheader")
            if issues.get('low_word_count'):
                widget.insert("end", "• CV is too short - consider adding more detail\n")
            if issues.get('too_long'):
                widget.insert("end", "• CV is quite long - consider condensing\n")
            if issues.get('missing_measurable'):
                widget.insert("end", "• Add quantified achievements and metrics\n")
            if issues.get('sections_missing'):
                missing = ', '.join(issues['sections_missing'])
                widget.insert("end", f"• Missing sections: {missing}\n")

    def update_skills_tab(self, analysis, tab_key, found_skills, missing_skills):
        """Update skills tabs with detailed analysis"""
        widget = self.tab_widgets[tab_key]
        widget.delete("1.0", "end")
        
        skill_type = "Hard Skills" if tab_key == 'hard_skills' else "Soft Skills"
        icon = "🛠️" if tab_key == 'hard_skills' else "🤝"
        
        # Header
        widget.insert("end", f"{icon} {skill_type.upper()} ANALYSIS\n")
        widget.insert("end", "=" * 50 + "\n\n")
        
        # Found skills
        if found_skills:
            widget.insert("end", f"✅ FOUND IN YOUR CV ({len(found_skills)})\n")
            widget.insert("end", "-" * 30 + "\n")
            for skill in sorted(found_skills):
                widget.insert("end", f"• {skill}\n")
            widget.insert("end", "\n")
        else:
            widget.insert("end", "❌ NO MATCHING SKILLS FOUND\n\n")
        
        # Missing skills
        if missing_skills:
            widget.insert("end", f"❌ MISSING FROM YOUR CV ({len(missing_skills)})\n")
            widget.insert("end", "-" * 30 + "\n")
            for skill in sorted(missing_skills):
                widget.insert("end", f"• {skill}\n")
            widget.insert("end", "\n")
        else:
            widget.insert("end", "✅ ALL REQUIRED SKILLS PRESENT\n\n")
        
        # Recommendations
        widget.insert("end", "💡 RECOMMENDATIONS\n")
        if missing_skills:
            priority_skills = missing_skills[:5]
            widget.insert("end", "Focus on adding these high-priority skills:\n")
            for skill in priority_skills:
                widget.insert("end", f"  🎯 {skill}\n")
        else:
            widget.insert("end", f"Great job! Your CV includes all relevant {skill_type.lower()} from the job description.\n")
    def update_content_tab(self, analysis, formatting):
        """Update content analysis tab"""
        widget = self.tab_widgets['content']
        widget.delete("1.0", "end")
        
        # Header
        widget.insert("end", "📄 CONTENT ANALYSIS\n")
        widget.insert("end", "=" * 50 + "\n\n")
        
        # Word count analysis
        word_count = analysis['word_count']
        widget.insert("end", "📝 LENGTH ANALYSIS\n")
        widget.insert("end", f"• Total words: {word_count}\n")
        
        if word_count < 600:
            widget.insert("end", "  ⚠️ Too short - consider adding more detail\n")
        elif word_count > 1200:
            widget.insert("end", "  ⚠️ Quite long - consider condensing\n")
        else:
            widget.insert("end", "  ✅ Good length\n")
        
        widget.insert("end", f"• Recommended range: 800-1000 words\n\n")
        
        # Measurable results analysis
        widget.insert("end", "📊 QUANTIFIABLE ACHIEVEMENTS\n")
        widget.insert("end", f"• Measurable results found: {analysis['measurable_count']}\n")
        if analysis['measurable_count'] > 0:
            widget.insert("end", "  ✅ Good use of metrics and numbers\n")
        else:
            widget.insert("end", "  ⚠️ Consider adding quantified achievements\n")
        widget.insert("end", "\n")
        
        # Sections analysis
        widget.insert("end", "🗂️ SECTIONS ANALYSIS\n")
        widget.insert("end", f"• Sections found: {len(analysis['sections_found'])}/6\n")
        
        if analysis['sections_found']:
            widget.insert("end", "Present sections:\n")
            for section in analysis['sections_found']:
                widget.insert("end", f"  ✅ {section.title()}\n")
        
        if analysis['issues']['sections_missing']:
            widget.insert("end", "Missing sections:\n")
            for section in analysis['issues']['sections_missing']:
                widget.insert("end", f"  ❌ {section.title()}\n")
        
        widget.insert("end", "\n")
        
        # Keywords analysis
        widget.insert("end", "🔍 KEYWORD ANALYSIS\n")
        total_kw = len(analysis['keywords_present']) + len(analysis['keywords_missing']) + len(analysis['keywords_fuzzy'])
        widget.insert("end", f"• Total relevant keywords: {total_kw}\n")
        widget.insert("end", f"• Exact matches: {len(analysis['keywords_present'])}\n")
        widget.insert("end", f"• Fuzzy matches: {len(analysis['keywords_fuzzy'])}\n")
        widget.insert("end", f"• Missing: {len(analysis['keywords_missing'])}\n")
        
        if total_kw > 0:
            match_rate = ((len(analysis['keywords_present']) + 0.6 * len(analysis['keywords_fuzzy'])) / total_kw) * 100
            widget.insert("end", f"• Match rate: {match_rate:.1f}%\n")
        
        # Show specific missing keywords
        if analysis['keywords_missing']:
            widget.insert("end", "\n🔍 TOP MISSING KEYWORDS:\n")
            top_missing = analysis['keywords_missing'][:10]
            for kw in top_missing:
                widget.insert("end", f"  • {kw}\n")
            if len(analysis['keywords_missing']) > 10:
                widget.insert("end", f"  ... and {len(analysis['keywords_missing']) - 10} more\n")

    def update_recommendations_tab(self, analysis, formatting):
        """Update recommendations tab with actionable tips"""
        widget = self.tab_widgets['tips']
        widget.delete("1.0", "end")
        
        # Header
        widget.insert("end", "💡 IMPROVEMENT RECOMMENDATIONS\n", "header")
        widget.insert("end", "=" * 50 + "\n\n", "separator")
        
        tips = generate_improvement_tips(analysis, formatting)
        
        if tips:
            widget.insert("end", "🎯 PRIORITY ACTIONS\n", "subheader")
            for i, tip in enumerate(tips, 1):
                widget.insert("end", f"{i}. {tip}\n\n")
        
        # Additional strategic advice
        widget.insert("end", "🚀 STRATEGIC ADVICE\n", "subheader")
        
        score = analysis['final_score']
        if score >= 85:
            widget.insert("end", "Your CV is well-optimized for ATS systems! Focus on:\n")
            widget.insert("end", "• Tailoring for specific roles\n")
            widget.insert("end", "• Highlighting unique value propositions\n")
            widget.insert("end", "• Adding recent achievements\n")
        elif score >= 70:
            widget.insert("end", "Your CV has good ATS compatibility. Key improvements:\n")
            widget.insert("end", "• Add missing technical skills\n")
            widget.insert("end", "• Include more quantified results\n")
            widget.insert("end", "• Optimize keyword density\n")
        else:
            widget.insert("end", "Significant improvements needed for ATS optimization:\n")
            widget.insert("end", "• Major keyword gaps to address\n")
            widget.insert("end", "• Structure and format enhancements\n")
            widget.insert("end", "• Content quality improvements\n")
        
        widget.insert("end", "\n")
        
        # Industry-specific advice
        widget.insert("end", "🏭 INDUSTRY-SPECIFIC TIPS\n", "subheader")
        widget.insert("end", "Based on common requirements in data/analytics roles:\n")
        widget.insert("end", "• Emphasize programming languages (Python, R, SQL)\n")
        widget.insert("end", "• Highlight visualization tools (Tableau, Power BI)\n")
        widget.insert("end", "• Showcase statistical analysis experience\n")
        widget.insert("end", "• Include business impact metrics\n")
        widget.insert("end", "• Mention collaborative project experience\n")

    def update_formatting_tab(self, formatting):
        """Update formatting analysis tab"""
        widget = self.tab_widgets['formatting']
        widget.delete("1.0", "end")
        
        if not formatting:
            widget.insert("end", "No formatting analysis available. Please run CV analysis first.")
            return
        
        # Header
        widget.insert("end", "🎨 FORMATTING ANALYSIS\n", "header")
        widget.insert("end", "=" * 50 + "\n\n", "separator")
        
        # Overall formatting score
        overall_score = formatting.get('overall_format_score', 0)
        widget.insert("end", f"📊 Overall Formatting Score: {overall_score:.1f}%\n\n")
        
        # Structure analysis
        widget.insert("end", "📋 STRUCTURE ANALYSIS\n", "subheader")
        widget.insert("end", f"• Line count: {formatting.get('line_count', 0)}\n")
        widget.insert("end", f"• Paragraph count: {formatting.get('paragraph_count', 0)}\n")
        widget.insert("end", f"• Bullet points: {formatting.get('bullet_usage', 0)}\n")
        widget.insert("end", f"• Numbered lists: {formatting.get('numbered_usage', 0)}\n")
        widget.insert("end", f"• Long paragraphs: {formatting.get('long_paragraphs', 0)}\n\n")
        
        # Contact information
        widget.insert("end", "📞 CONTACT INFORMATION\n", "subheader")
        contact_info = formatting.get('contact_info', {})
        
        email_status = "✅ Present" if contact_info.get('email') else "❌ Missing"
        phone_status = "✅ Present" if contact_info.get('phone') else "❌ Missing"
        
        widget.insert("end", f"• Email: {email_status}\n")
        widget.insert("end", f"• Phone: {phone_status}\n")
        widget.insert("end", f"• Contact score: {contact_info.get('score', 0)}%\n\n")
        
        # Web presence
        widget.insert("end", "🌐 WEB PRESENCE\n", "subheader")
        web_status = "✅ Found" if formatting.get('web_presence') else "❌ Not found"
        widget.insert("end", f"• URLs/LinkedIn: {web_status}\n\n")
        
        # Recommendations
        widget.insert("end", "💡 FORMATTING RECOMMENDATIONS\n", "subheader")
        
        if formatting.get('long_paragraphs', 0) > 2:
            widget.insert("end", "• Break down long paragraphs for better readability\n")
        
        if formatting.get('bullet_usage', 0) < 5:
            widget.insert("end", "• Use more bullet points to highlight key information\n")
        
        if not contact_info.get('email'):
            widget.insert("end", "• Add your email address\n")
        
        if not contact_info.get('phone'):
            widget.insert("end", "• Include your phone number\n")
        
        if not formatting.get('web_presence'):
            widget.insert("end", "• Add your LinkedIn profile or portfolio website\n")
        
        if formatting.get('structure_score', 0) < 50:
            widget.insert("end", "• Improve document structure with more organized sections\n")

    def update_tips_section(self):
        """Update the tips section in the left panel"""
        if not self.analysis_result:
            return
        
        tips = generate_improvement_tips(self.analysis_result, self.formatting_result)
        
        self.tips_text.delete("1.0", "end")
        
        # Add header
        self.tips_text.insert("end", "🎯 Quick Improvements\n", "header")
        self.tips_text.insert("end", "-" * 25 + "\n\n")
        
        # Add top 5 tips
        for i, tip in enumerate(tips[:5], 1):
            self.tips_text.insert("end", f"{i}. {tip}\n\n")
        
        if len(tips) > 5:
            self.tips_text.insert("end", f"... and {len(tips) - 5} more recommendations in the detailed analysis.")

    def optimize_cv(self):
        """AI-powered CV optimization using Gemini"""
        cv_content = self.cv_text.get("1.0", "end").strip()
        jd_content = self.jd_text.get("1.0", "end").strip()
        
        if not cv_content or not jd_content:
            messagebox.showwarning("Missing Information", 
                                 "Please provide both CV content and job description for AI optimization.")
            return
        
        try:
            # Show progress dialog
            progress_window = tk.Toplevel(self.root)
            progress_window.title("AI Optimization in Progress")
            progress_window.geometry("400x150")
            progress_window.transient(self.root)
            progress_window.grab_set()
            
            # Center the progress window
            progress_window.update_idletasks()
            x = (progress_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (progress_window.winfo_screenheight() // 2) - (150 // 2)
            progress_window.geometry(f"400x150+{x}+{y}")
            
            progress_label = tk.Label(progress_window, 
                                    text="AI is analyzing and optimizing your CV...", 
                                    font=("Segoe UI", 12), pady=20)
            progress_label.pack()
            
            progress_bar = ttk.Progressbar(progress_window, mode='indeterminate', length=300)
            progress_bar.pack(pady=20)
            progress_bar.start()
            
            self.root.update()
            
            # Create prompt for Gemini
            optimization_prompt = f"""
            You are a professional CV optimization expert specializing in ATS (Applicant Tracking System) optimization.
            
            Please analyze and optimize the following CV for the given job description:
            
            JOB DESCRIPTION:
            {jd_content}
            
            CURRENT CV:
            {cv_content}
            
            Please provide:
            1. An optimized version of the CV that maintains the candidate's authentic experience while improving ATS compatibility
            2. Focus on keyword optimization, better structure, and quantified achievements
            3. Maintain the original tone and truthfulness - don't fabricate experience
            4. Improve formatting and readability
            5. Ensure all critical skills from the job description are appropriately highlighted if present in the original CV
            
            Return only the optimized CV content, formatted professionally.
            """
            
            # Call Gemini API
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(optimization_prompt)
            
            progress_bar.stop()
            progress_window.destroy()
            
            # Update the optimized CV tab
            optimized_content = response.text
            self.tab_widgets['optimized'].delete("1.0", "end")
            self.tab_widgets['optimized'].insert("1.0", optimized_content)
            
            # Switch to optimized tab
            self.notebook.select(5)  # Optimized CV tab index
            
            messagebox.showinfo("Optimization Complete", 
                              "Your CV has been optimized using AI!\n\nCheck the 'AI Optimized CV' tab to see the enhanced version.")
            
        except Exception as e:
            if 'progress_window' in locals():
                progress_window.destroy()
            
            error_msg = str(e)
            if "API_KEY" in error_msg or "authentication" in error_msg.lower():
                messagebox.showerror("API Error", 
                                   "AI optimization requires a valid Gemini API key. Please check your API configuration.")
            else:
                messagebox.showerror("Optimization Error", f"AI optimization failed:\n{error_msg}")

# ---------- Main Application ----------
def main():
    """Main application entry point"""
    try:
        root = tk.Tk()
        app = EnhancedATSOptimizerApp(root)
        
        # Set up window closing protocol
        def on_closing():
            if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the application
        root.mainloop()
        
    except Exception as e:
        print(f"Application startup error: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{e}")

if __name__ == "__main__":
    print("Starting Enhanced ATS CV Optimizer...")
    print("Loading dependencies...")
    main()
    print("Application closed.")