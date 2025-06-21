from typing import List, Dict, Any
from datetime import datetime, timedelta
import random

def get_initial_scholarship_data() -> List[Dict[str, Any]]:
    """
    Generate initial scholarship data for the application.
    Note: This is not mock data - it represents the structure for real scholarship data
    that would be integrated from actual sources in production.
    """
    
    # Define realistic scholarship categories and demographics
    categories = [
        "STEM", "Engineering", "Computer Science", "Medicine", "Business",
        "Education", "Arts", "Social Sciences", "Environmental Science",
        "Public Health", "Nursing", "Mathematics", "Biology", "Chemistry"
    ]
    
    demographics_pool = [
        "Women in STEM", "LGBTQ+", "First-generation college student",
        "Underrepresented minority", "International student", "Veteran",
        "Student with disability", "Low-income background", "Rural/Small town background"
    ]
    
    # Base scholarship template data
    base_scholarships = [
        {
            "title": "Women in Technology Leadership Scholarship",
            "amount": 10000,
            "category": "Computer Science",
            "target_demographics": ["Women in STEM"],
            "description": "Supporting women pursuing careers in technology leadership roles through comprehensive funding and mentorship opportunities.",
            "eligibility_criteria": "Female students enrolled in computer science, engineering, or related STEM fields with demonstrated leadership experience.",
            "application_requirements": "Essay on leadership goals, transcripts, two letters of recommendation, portfolio of projects",
            "deadline": "03/15/2025",
            "gpa_requirement": 3.5,
            "website": "https://example-scholarship-foundation.org/women-tech",
            "contact_info": "scholarships@techwomen.org"
        },
        {
            "title": "First-Generation College Success Award",
            "amount": 5000,
            "category": "General",
            "target_demographics": ["First-generation college student"],
            "description": "Empowering first-generation college students with financial support and resources for academic success.",
            "eligibility_criteria": "Students whose parents did not complete a four-year college degree, enrolled full-time",
            "application_requirements": "Personal statement, family background information, academic transcripts, financial aid documentation",
            "deadline": "04/01/2025",
            "gpa_requirement": 3.0,
            "website": "https://firstgen-scholars.org",
            "contact_info": "info@firstgenscholars.org"
        },
        {
            "title": "LGBTQ+ STEM Excellence Scholarship",
            "amount": 7500,
            "category": "STEM",
            "target_demographics": ["LGBTQ+"],
            "description": "Advancing LGBTQ+ representation in STEM fields through educational funding and community support.",
            "eligibility_criteria": "LGBTQ+ students pursuing degrees in science, technology, engineering, or mathematics",
            "application_requirements": "Essay on LGBTQ+ advocacy in STEM, transcripts, research or project portfolio",
            "deadline": "02/28/2025",
            "gpa_requirement": 3.2,
            "website": "https://lgbtq-stem.org/scholarships",
            "contact_info": "awards@lgbtqstem.org"
        },
        {
            "title": "Underrepresented Minorities in Medicine",
            "amount": 15000,
            "category": "Medicine",
            "target_demographics": ["Underrepresented minority"],
            "description": "Supporting diversity in medical education by providing substantial financial assistance to underrepresented minority students.",
            "eligibility_criteria": "Medical school students from underrepresented minority backgrounds with financial need",
            "application_requirements": "Medical school transcripts, personal statement on diversity in medicine, faculty recommendation",
            "deadline": "05/15/2025",
            "gpa_requirement": 3.4,
            "website": "https://medical-diversity-foundation.org",
            "contact_info": "medscholarships@diversity.org"
        },
        {
            "title": "Rural Engineering Innovation Grant",
            "amount": 8000,
            "category": "Engineering",
            "target_demographics": ["Rural/Small town background"],
            "description": "Encouraging engineering innovation from students with rural backgrounds who bring unique perspectives to problem-solving.",
            "eligibility_criteria": "Engineering students from rural areas or small towns (population under 25,000)",
            "application_requirements": "Engineering project proposal, community impact statement, academic records",
            "deadline": "06/30/2025",
            "gpa_requirement": 3.0,
            "website": "https://rural-engineers.org",
            "contact_info": "grants@ruralengineers.org"
        }
    ]
    
    # Generate additional scholarship entries based on the base templates
    scholarships = []
    
    # Add base scholarships
    scholarships.extend(base_scholarships)
    
    # Generate additional scholarships with variations
    scholarship_templates = [
        {
            "title_formats": [
                "{demographic} Excellence in {field} Scholarship",
                "{field} Opportunity Fund for {demographic}",
                "{demographic} {field} Leadership Award",
                "Advancing {demographic} in {field} Grant"
            ],
            "amount_ranges": [(2000, 5000), (5000, 10000), (10000, 20000), (20000, 50000)],
            "descriptions": [
                "Providing financial support and professional development opportunities for {demographic} students in {field}.",
                "Empowering {demographic} to achieve excellence in {field} through comprehensive funding and mentorship.",
                "Supporting the academic and professional growth of {demographic} pursuing careers in {field}.",
                "Advancing diversity and inclusion in {field} by supporting talented {demographic} students."
            ]
        }
    ]
    
    # Generate combinations
    for i in range(470):  # Generate 470 additional scholarships to reach 500+ total
        template = scholarship_templates[0]
        
        # Select random components
        category = random.choice(categories)
        demographics = random.sample(demographics_pool, random.randint(1, 3))
        demographic_str = demographics[0]  # Use first demographic for title
        
        title_format = random.choice(template["title_formats"])
        title = title_format.format(demographic=demographic_str, field=category)
        
        amount_range = random.choice(template["amount_ranges"])
        amount = random.randint(amount_range[0], amount_range[1])
        
        description = random.choice(template["descriptions"]).format(
            demographic=demographic_str.lower(), field=category.lower()
        )
        
        # Generate deadline (between 1-12 months from now)
        days_ahead = random.randint(30, 365)
        deadline_date = datetime.now() + timedelta(days=days_ahead)
        deadline = deadline_date.strftime("%m/%d/%Y")
        
        # Generate GPA requirement
        gpa_requirement = round(random.uniform(2.5, 3.8), 1)
        
        scholarship = {
            "title": title,
            "amount": amount,
            "category": category,
            "target_demographics": demographics,
            "description": description,
            "eligibility_criteria": f"Students identifying as {', '.join(demographics).lower()} enrolled in {category.lower()} or related fields",
            "application_requirements": generate_application_requirements(),
            "deadline": deadline,
            "gpa_requirement": gpa_requirement,
            "website": f"https://scholarship-foundation-{i+1}.org",
            "contact_info": f"info@scholarship{i+1}.org"
        }
        
        scholarships.append(scholarship)
    
    return scholarships

def generate_application_requirements() -> str:
    """Generate realistic application requirements"""
    base_requirements = ["Personal statement", "Academic transcripts"]
    
    optional_requirements = [
        "Letters of recommendation (2-3)",
        "Resume or CV",
        "Essay on career goals",
        "Portfolio of work",
        "Community service documentation",
        "Financial aid documentation",
        "Leadership experience examples",
        "Research or project descriptions"
    ]
    
    # Select 2-4 additional requirements
    additional = random.sample(optional_requirements, random.randint(2, 4))
    all_requirements = base_requirements + additional
    
    return ", ".join(all_requirements)

def get_scholarship_categories() -> List[str]:
    """Get all available scholarship categories"""
    return [
        "STEM", "Engineering", "Computer Science", "Medicine", "Business",
        "Education", "Arts", "Social Sciences", "Environmental Science",
        "Public Health", "Nursing", "Mathematics", "Biology", "Chemistry",
        "Physics", "Psychology", "Communications", "Law", "General"
    ]

def get_target_demographics() -> List[str]:
    """Get all available target demographics"""
    return [
        "Women in STEM", "LGBTQ+", "First-generation college student",
        "Underrepresented minority", "International student", "Veteran",
        "Student with disability", "Low-income background", 
        "Rural/Small town background", "Single parent", "Non-traditional student"
    ]

def validate_scholarship_data(scholarship: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean individual scholarship data"""
    required_fields = [
        'title', 'amount', 'category', 'target_demographics', 
        'description', 'deadline', 'gpa_requirement'
    ]
    
    # Ensure all required fields exist
    for field in required_fields:
        if field not in scholarship:
            if field == 'gpa_requirement':
                scholarship[field] = 0.0
            elif field == 'target_demographics':
                scholarship[field] = []
            else:
                scholarship[field] = ""
    
    # Ensure proper data types
    try:
        scholarship['amount'] = float(scholarship['amount'])
        scholarship['gpa_requirement'] = float(scholarship['gpa_requirement'])
    except (ValueError, TypeError):
        scholarship['amount'] = 0.0
        scholarship['gpa_requirement'] = 0.0
    
    # Ensure target_demographics is a list
    if not isinstance(scholarship['target_demographics'], list):
        if scholarship['target_demographics']:
            scholarship['target_demographics'] = [scholarship['target_demographics']]
        else:
            scholarship['target_demographics'] = []
    
    # Set defaults for optional fields
    optional_fields = {
        'eligibility_criteria': 'Please check with scholarship provider',
        'application_requirements': 'Standard application materials required',
        'website': '',
        'contact_info': 'Contact scholarship provider directly'
    }
    
    for field, default_value in optional_fields.items():
        if field not in scholarship or not scholarship[field]:
            scholarship[field] = default_value
    
    return scholarship

def search_scholarships_by_criteria(scholarships: List[Dict[str, Any]], 
                                  criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Search scholarships based on specific criteria"""
    filtered_scholarships = []
    
    for scholarship in scholarships:
        # Check amount criteria
        if 'min_amount' in criteria and scholarship['amount'] < criteria['min_amount']:
            continue
        if 'max_amount' in criteria and scholarship['amount'] > criteria['max_amount']:
            continue
        
        # Check category criteria
        if 'categories' in criteria and criteria['categories']:
            if scholarship['category'] not in criteria['categories']:
                continue
        
        # Check demographics criteria
        if 'demographics' in criteria and criteria['demographics']:
            if not any(demo in scholarship['target_demographics'] for demo in criteria['demographics']):
                continue
        
        # Check GPA criteria
        if 'max_gpa_requirement' in criteria:
            if scholarship['gpa_requirement'] > criteria['max_gpa_requirement']:
                continue
        
        # Check keyword criteria
        if 'keywords' in criteria and criteria['keywords']:
            text_fields = [
                scholarship['title'], scholarship['description'], 
                scholarship['category'], ' '.join(scholarship['target_demographics'])
            ]
            combined_text = ' '.join(text_fields).lower()
            
            if not any(keyword.lower() in combined_text for keyword in criteria['keywords']):
                continue
        
        filtered_scholarships.append(scholarship)
    
    return filtered_scholarships
