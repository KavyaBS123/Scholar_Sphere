import streamlit as st
import pandas as pd
from datetime import datetime, date

st.set_page_config(
    page_title="Profile Setup - ScholarSphere",
    page_icon="👤",
    layout="wide"
)

def main():
    st.title("Profile Setup")
    
    # Initialize user profile if not exists
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'demographics': [],
            'field_of_study': '',
            'academic_level': '',
            'gpa': 0.0,
            'financial_need': '',
            'location': '',
            'interests': [],
            'extracurriculars': [],
            'career_goals': '',
            'graduation_year': 2024,
            'essay_topics_interested': [],
            'application_preferences': []
        }
    
    profile = st.session_state.user_profile
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Basic Info", "🎓 Academic", "💡 Interests & Goals", "⚙️ Preferences"])
    
    with tab1:
        st.header("Basic Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Demographics
            st.subheader("Demographics")
            demographics_options = [
                "Women in STEM",
                "LGBTQ+",
                "First-generation college student",
                "Underrepresented minority",
                "International student",
                "Veteran",
                "Student with disability",
                "Low-income background",
                "Rural/Small town background",
                "Single parent",
                "Non-traditional student (returning to education)"
            ]
            
            selected_demographics = st.multiselect(
                "Select all that apply to you:",
                demographics_options,
                default=profile['demographics'],
                help="This helps us find scholarships specifically designed for your background"
            )
            
            # Location
            location = st.text_input(
                "Location (State/Country):",
                value=profile['location'],
                placeholder="e.g., California, USA",
                help="Some scholarships are location-specific"
            )
            
            # Financial need
            financial_need = st.selectbox(
                "Financial Need Level:",
                ["", "High", "Moderate", "Low"],
                index=["", "High", "Moderate", "Low"].index(profile['financial_need']) if profile['financial_need'] else 0,
                help="This helps prioritize need-based scholarships"
            )
        
        with col2:
            # Academic level
            st.subheader("Academic Information")
            academic_level = st.selectbox(
                "Current Academic Level:",
                ["", "High School Senior", "Undergraduate Freshman", "Undergraduate Sophomore", 
                 "Undergraduate Junior", "Undergraduate Senior", "Graduate Student", "Doctoral Student"],
                index=0 if not profile['academic_level'] else ["", "High School Senior", "Undergraduate Freshman", 
                       "Undergraduate Sophomore", "Undergraduate Junior", "Undergraduate Senior", 
                       "Graduate Student", "Doctoral Student"].index(profile['academic_level']) if profile['academic_level'] in ["", "High School Senior", "Undergraduate Freshman", "Undergraduate Sophomore", "Undergraduate Junior", "Undergraduate Senior", "Graduate Student", "Doctoral Student"] else 0
            )
            
            # Expected graduation year
            current_year = datetime.now().year
            graduation_year = st.selectbox(
                "Expected Graduation Year:",
                list(range(current_year, current_year + 10)),
                index=profile['graduation_year'] - current_year if profile['graduation_year'] >= current_year else 0
            )
            
            # GPA
            gpa = st.number_input(
                "Current GPA:",
                min_value=0.0,
                max_value=4.0,
                value=float(profile['gpa']),
                step=0.1,
                help="Enter your current GPA on a 4.0 scale"
            )
    
    with tab2:
        st.header("Academic Focus")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Field of study
            field_options = [
                "", "Computer Science", "Engineering", "Medicine", "Nursing", "Business", 
                "Education", "Arts", "Social Sciences", "Natural Sciences", "Mathematics",
                "Psychology", "Biology", "Chemistry", "Physics", "Environmental Science",
                "Public Health", "Law", "Communications", "Other"
            ]
            
            field_of_study = st.selectbox(
                "Primary Field of Study:",
                field_options,
                index=field_options.index(profile['field_of_study']) if profile['field_of_study'] in field_options else 0
            )
            
            # Specific interests within field
            interests = st.text_area(
                "Specific Interests/Specializations:",
                value=", ".join(profile['interests']) if profile['interests'] else "",
                placeholder="e.g., Artificial Intelligence, Renewable Energy, Pediatric Medicine",
                help="List specific areas within your field that interest you"
            )
        
        with col2:
            # Extracurricular activities
            extracurricular_options = [
                "Student Government", "Research", "Internships", "Volunteer Work",
                "Sports/Athletics", "Music/Arts", "Debate/Speech", "Honor Societies",
                "STEM Clubs", "Cultural Organizations", "Religious Organizations",
                "Environmental Groups", "Community Service", "Leadership Roles",
                "Work Experience", "Entrepreneurship"
            ]
            
            selected_extracurriculars = st.multiselect(
                "Extracurricular Activities:",
                extracurricular_options,
                default=profile['extracurriculars'],
                help="Activities and involvement help match you with relevant scholarships"
            )
            
            # Career goals
            career_goals = st.text_area(
                "Career Goals:",
                value=profile['career_goals'],
                placeholder="Describe your career aspirations and how you plan to make an impact",
                help="Many scholarships look for students with clear goals and vision"
            )
    
    with tab3:
        st.header("Interests & Essay Topics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Essay topics of interest
            essay_topic_options = [
                "Leadership experiences", "Overcoming challenges", "Community service",
                "Diversity and inclusion", "Innovation and creativity", "Social justice",
                "Environmental sustainability", "Technology and society", "Healthcare access",
                "Education equity", "Economic development", "Cultural heritage",
                "Scientific research", "Entrepreneurship", "Global citizenship"
            ]
            
            essay_topics = st.multiselect(
                "Essay Topics You're Comfortable Writing About:",
                essay_topic_options,
                default=profile['essay_topics_interested'],
                help="This helps find scholarships with essay prompts you can excel at"
            )
        
        with col2:
            st.subheader("Additional Information")
            
            # Languages spoken
            languages = st.text_input(
                "Languages Spoken:",
                placeholder="e.g., English, Spanish, Mandarin",
                help="Some scholarships are for multilingual students"
            )
            
            # Special achievements
            achievements = st.text_area(
                "Notable Achievements/Awards:",
                placeholder="List any significant achievements, awards, or recognition",
                help="Helps match with merit-based scholarships"
            )
    
    with tab4:
        st.header("Application Preferences")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Application preferences
            application_pref_options = [
                "Online applications only", "Prefer shorter applications", 
                "Comfortable with essays", "Prefer video submissions",
                "Need-based focus", "Merit-based focus", "Local scholarships",
                "National scholarships", "Renewable scholarships"
            ]
            
            application_preferences = st.multiselect(
                "Application Preferences:",
                application_pref_options,
                default=profile['application_preferences'],
                help="Helps prioritize scholarships that match your application style"
            )
            
            # Notification preferences
            st.subheader("Notification Settings")
            email_notifications = st.checkbox("Email notifications for new matches", value=True)
            deadline_reminders = st.checkbox("Deadline reminders", value=True)
            weekly_digest = st.checkbox("Weekly scholarship digest", value=False)
        
        with col2:
            st.subheader("Scholarship Amount Preferences")
            
            # Preferred scholarship amounts
            min_amount_pref = st.number_input(
                "Minimum scholarship amount of interest:",
                min_value=0,
                max_value=100000,
                value=1000,
                step=500,
                help="Skip showing scholarships below this amount"
            )
            
            # Application timeline
            application_timeline = st.selectbox(
                "How far in advance do you prefer to know about deadlines?",
                ["1 month", "2 months", "3 months", "6 months", "1 year"],
                index=2
            )
    
    # Save profile button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            # Update profile with all the collected information
            st.session_state.user_profile.update({
                'demographics': selected_demographics,
                'field_of_study': field_of_study,
                'academic_level': academic_level,
                'gpa': gpa,
                'financial_need': financial_need,
                'location': location,
                'interests': [i.strip() for i in interests.split(",")] if interests else [],
                'extracurriculars': selected_extracurriculars,
                'career_goals': career_goals,
                'graduation_year': graduation_year,
                'essay_topics_interested': essay_topics,
                'application_preferences': application_preferences
            })
            
            st.success("✅ Profile saved successfully!")
            st.balloons()
            
            # Show profile completeness
            completeness = calculate_profile_completeness(st.session_state.user_profile)
            st.info(f"Your profile is {completeness}% complete")
    
    # Profile summary
    st.markdown("---")
    st.header("📋 Profile Summary")
    
    if any(st.session_state.user_profile.values()):
        display_profile_summary(st.session_state.user_profile)
    else:
        st.info("Complete the sections above to see your profile summary.")
    
    # Recommendations based on profile
    if st.session_state.user_profile['demographics'] or st.session_state.user_profile['field_of_study']:
        st.header("🎯 Profile-Based Recommendations")
        generate_profile_recommendations(st.session_state.user_profile)

def calculate_profile_completeness(profile):
    """Calculate what percentage of the profile is complete"""
    important_fields = [
        'demographics', 'field_of_study', 'academic_level', 'gpa',
        'financial_need', 'interests', 'career_goals', 'extracurriculars'
    ]
    
    completed_fields = 0
    for field in important_fields:
        if profile.get(field) and profile[field] != [] and profile[field] != '' and profile[field] != 0.0:
            completed_fields += 1
    
    return round((completed_fields / len(important_fields)) * 100)

def display_profile_summary(profile):
    """Display a summary of the user's profile"""
    col1, col2 = st.columns(2)
    
    with col1:
        if profile['demographics']:
            st.write(f"**Demographics:** {', '.join(profile['demographics'])}")
        
        if profile['field_of_study']:
            st.write(f"**Field of Study:** {profile['field_of_study']}")
        
        if profile['academic_level']:
            st.write(f"**Academic Level:** {profile['academic_level']}")
        
        if profile['gpa'] > 0:
            st.write(f"**GPA:** {profile['gpa']}")
        
        if profile['graduation_year']:
            st.write(f"**Expected Graduation:** {profile['graduation_year']}")
    
    with col2:
        if profile['financial_need']:
            st.write(f"**Financial Need:** {profile['financial_need']}")
        
        if profile['location']:
            st.write(f"**Location:** {profile['location']}")
        
        if profile['interests']:
            st.write(f"**Interests:** {', '.join(profile['interests'][:3])}{'...' if len(profile['interests']) > 3 else ''}")
        
        if profile['extracurriculars']:
            st.write(f"**Activities:** {', '.join(profile['extracurriculars'][:3])}{'...' if len(profile['extracurriculars']) > 3 else ''}")

def generate_profile_recommendations(profile):
    """Generate recommendations based on user profile"""
    recommendations = []
    
    # Demographic-based recommendations
    if "Women in STEM" in profile['demographics']:
        recommendations.append("🚀 Look for scholarships from organizations like Society of Women Engineers (SWE)")
    
    if "First-generation college student" in profile['demographics']:
        recommendations.append("🎓 Many universities offer specific scholarships for first-generation students")
    
    if "LGBTQ+" in profile['demographics']:
        recommendations.append("🏳️‍🌈 Consider scholarships from PFLAG, Point Foundation, and other LGBTQ+ organizations")
    
    # Field-based recommendations
    if profile['field_of_study'] == "Computer Science":
        recommendations.append("💻 Tech companies like Google, Microsoft, and Apple offer substantial scholarships")
    
    if profile['field_of_study'] == "Medicine":
        recommendations.append("🏥 Medical associations and hospitals often provide scholarships for future healthcare workers")
    
    # GPA-based recommendations
    if profile['gpa'] >= 3.5:
        recommendations.append("📚 Your high GPA qualifies you for many merit-based scholarships")
    
    # Financial need recommendations
    if profile['financial_need'] == "High":
        recommendations.append("💰 Focus on need-based scholarships and consider applying for federal financial aid")
    
    # Display recommendations
    if recommendations:
        for rec in recommendations:
            st.write(f"• {rec}")
    else:
        st.info("Complete more of your profile to get personalized recommendations!")

if __name__ == "__main__":
    main()
