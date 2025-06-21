import streamlit as st
import pandas as pd
from utils.data_manager import DataManager
from utils.scholarship_data import get_initial_scholarship_data

# Configure page
st.set_page_config(
    page_title="ScholarSphere - Scholarship Discovery Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data manager
@st.cache_resource
def init_data_manager():
    dm = DataManager()
    # Load initial scholarship data
    scholarships = get_initial_scholarship_data()
    dm.load_scholarships(scholarships)
    return dm

def main():
    # Initialize session state
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = init_data_manager()
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'demographics': [],
            'field_of_study': '',
            'academic_level': '',
            'gpa': 0.0,
            'financial_need': '',
            'location': '',
            'interests': []
        }

    # Main header
    st.title("🎓 ScholarSphere")
    st.markdown("### AI-Enhanced Scholarship Discovery for Underrepresented Students")
    
    # Welcome message
    st.markdown("""
    Welcome to ScholarSphere! Our platform uses AI to help underrepresented students discover 
    relevant scholarships through advanced filtering, clustering visualizations, and personalized recommendations.
    
    **Get started by:**
    1. Setting up your profile in the sidebar
    2. Exploring scholarships through our dashboard
    3. Using advanced search and clustering features
    """)
    
    # Sidebar for quick profile setup
    with st.sidebar:
        st.header("Quick Profile Setup")
        
        # Demographics
        demographics_options = [
            "Women in STEM", "LGBTQ+", "First-generation college student",
            "Underrepresented minority", "International student", "Veteran",
            "Student with disability", "Low-income background"
        ]
        selected_demographics = st.multiselect(
            "Select demographics that apply to you:",
            demographics_options,
            default=st.session_state.user_profile['demographics']
        )
        
        # Field of study
        field_options = [
            "Computer Science", "Engineering", "Medicine", "Business",
            "Education", "Arts", "Social Sciences", "Natural Sciences",
            "Mathematics", "Nursing", "Other"
        ]
        field_of_study = st.selectbox(
            "Field of Study:",
            field_options,
            index=field_options.index(st.session_state.user_profile['field_of_study']) 
            if st.session_state.user_profile['field_of_study'] in field_options else 0
        )
        
        # Academic level
        academic_level = st.selectbox(
            "Academic Level:",
            ["High School", "Undergraduate", "Graduate", "Doctoral"],
            index=["High School", "Undergraduate", "Graduate", "Doctoral"].index(st.session_state.user_profile['academic_level'])
            if st.session_state.user_profile['academic_level'] else 0
        )
        
        # Update profile
        if st.button("Update Profile"):
            st.session_state.user_profile.update({
                'demographics': selected_demographics,
                'field_of_study': field_of_study,
                'academic_level': academic_level
            })
            st.success("Profile updated!")
            st.rerun()
    
    # Statistics overview
    dm = st.session_state.data_manager
    scholarships_df = dm.get_scholarships_df()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Scholarships", len(scholarships_df))
    
    with col2:
        avg_amount = scholarships_df['amount'].mean()
        st.metric("Average Award", f"${avg_amount:,.0f}")
    
    with col3:
        unique_categories = scholarships_df['category'].nunique()
        st.metric("Categories", unique_categories)
    
    with col4:
        # Count scholarships matching user demographics
        user_demographics = st.session_state.user_profile['demographics']
        if user_demographics:
            matching_scholarships = scholarships_df[
                scholarships_df['target_demographics'].apply(
                    lambda x: any(demo in x for demo in user_demographics)
                )
            ]
            st.metric("Matches for You", len(matching_scholarships))
        else:
            st.metric("Setup Profile", "👈")
    
    # Recent scholarships preview
    st.header("Featured Scholarships")
    
    # Display top 5 scholarships
    featured_scholarships = scholarships_df.head(5)
    
    for _, scholarship in featured_scholarships.iterrows():
        with st.expander(f"🎯 {scholarship['title']} - ${scholarship['amount']:,}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Category:** {scholarship['category']}")
                st.write(f"**Target Demographics:** {', '.join(scholarship['target_demographics'])}")
                st.write(f"**Deadline:** {scholarship['deadline']}")
                st.write(f"**Description:** {scholarship['description'][:200]}...")
            
            with col2:
                st.write(f"**Amount:** ${scholarship['amount']:,}")
                st.write(f"**GPA Requirement:** {scholarship['gpa_requirement']}")
                if st.button(f"View Details", key=f"detail_{scholarship.name}"):
                    st.info("Navigate to Search Scholarships page for full details")
    
    # Call to action
    st.markdown("---")
    st.markdown("""
    ### Ready to find your perfect scholarship?
    
    Use the navigation menu to explore:
    - **Dashboard:** Get personalized recommendations
    - **Search Scholarships:** Advanced filtering and search
    - **Scholarship Clusters:** Visual exploration of opportunities
    - **Profile Setup:** Complete your detailed profile
    """)

if __name__ == "__main__":
    main()
