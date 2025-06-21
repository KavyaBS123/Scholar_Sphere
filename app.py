import streamlit as st
import pandas as pd
from utils.database_manager import DatabaseManager
from utils.scholarship_data import get_initial_scholarship_data

# Configure page
st.set_page_config(
    page_title="ScholarSphere - Scholarship Discovery Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database manager
@st.cache_resource
def init_database_manager():
    dm = DatabaseManager()
    # Load scholarships from database or authentic sources
    dm.load_scholarships()
    return dm

def main():
    # Initialize session state
    if 'data_manager' not in st.session_state:
        st.session_state.data_manager = init_database_manager()
    
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
    st.markdown("### Scholarship Discovery Platform")
    
    # Sidebar for profile setup
    with st.sidebar:
        st.header("Profile")
        
        # Demographics
        demographics_options = [
            "Women in STEM", "LGBTQ+", "First-generation college student",
            "Underrepresented minority", "International student", "Veteran",
            "Student with disability", "Low-income background"
        ]
        selected_demographics = st.multiselect(
            "Demographics:",
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
            "Field:",
            field_options,
            index=field_options.index(st.session_state.user_profile['field_of_study']) 
            if st.session_state.user_profile['field_of_study'] in field_options else 0
        )
        
        # Academic level
        academic_level = st.selectbox(
            "Level:",
            ["High School", "Undergraduate", "Graduate", "Doctoral"],
            index=["High School", "Undergraduate", "Graduate", "Doctoral"].index(st.session_state.user_profile['academic_level'])
            if st.session_state.user_profile['academic_level'] else 0
        )
        
        # Update profile
        if st.button("Update"):
            st.session_state.user_profile.update({
                'demographics': selected_demographics,
                'field_of_study': field_of_study,
                'academic_level': academic_level
            })
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
    
    # Recent scholarships
    st.header("Featured Scholarships")
    
    featured_scholarships = scholarships_df.head(5)
    
    for _, scholarship in featured_scholarships.iterrows():
        with st.expander(f"{scholarship['title']} - ${scholarship['amount']:,}"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Category:** {scholarship['category']}")
                st.write(f"**Demographics:** {', '.join(scholarship['target_demographics'])}")
                st.write(f"**Deadline:** {scholarship['deadline']}")
                st.write(scholarship['description'][:150] + "...")
            
            with col2:
                st.metric("Amount", f"${scholarship['amount']:,}")
                st.metric("GPA", f"{scholarship['gpa_requirement']}")
                if st.button("Details", key=f"detail_{scholarship.name}"):
                    st.switch_page("pages/2_Search_Scholarships.py")

if __name__ == "__main__":
    main()
