import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ai_enhancer import AIEnhancer
from utils.clustering import ScholarshipClustering

st.set_page_config(
    page_title="Dashboard - ScholarSphere",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Dashboard")
    
    if 'data_manager' not in st.session_state:
        st.error("Please visit the main page first.")
        return
    
    dm = st.session_state.data_manager
    user_profile = st.session_state.user_profile
    
    if not user_profile['demographics'] and not user_profile['field_of_study']:
        st.warning("Complete your profile to see recommendations")
        return
    
    scholarships_df = dm.get_scholarships_df()
    
    # Initialize AI enhancer
    ai_enhancer = AIEnhancer()
    
    # Get personalized recommendations
    st.header("Recommended for You")
    
    # Filter scholarships based on user profile
    filtered_scholarships = filter_scholarships_for_user(scholarships_df, user_profile)
    
    if filtered_scholarships.empty:
        st.info("No matches found. Update your profile for better results.")
        return
    
    # Display top recommendations
    top_recommendations = filtered_scholarships.head(3)
    
    for idx, (_, scholarship) in enumerate(top_recommendations.iterrows()):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"🏆 {scholarship['title']}")
                
                # Description
                st.write(f"**Description:** {scholarship['description'][:200]}...")
                
                st.write(f"**Category:** {scholarship['category']}")
                st.write(f"**Target Demographics:** {', '.join(scholarship['target_demographics'])}")
                st.write(f"**Eligibility:** {scholarship['eligibility_criteria']}")
                st.write(f"**Deadline:** {scholarship['deadline']}")
            
            with col2:
                st.metric("Award Amount", f"${scholarship['amount']:,}")
                st.metric("GPA Required", f"{scholarship['gpa_requirement']}")
                
                # Match score calculation
                match_score = calculate_match_score(scholarship, user_profile)
                st.metric("Match Score", f"{match_score}%")
                
                if st.button(f"Apply Now", key=f"apply_{idx}"):
                    st.success(f"Redirecting to application for {scholarship['title']}")
            
            st.markdown("---")
    
    # Analytics section
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("📈 Your Opportunity Landscape")
        
        # Amount distribution of matching scholarships
        fig_amounts = px.histogram(
            filtered_scholarships, 
            x='amount',
            bins=20,
            title="Distribution of Scholarship Amounts (Your Matches)",
            labels={'amount': 'Award Amount ($)', 'count': 'Number of Scholarships'}
        )
        fig_amounts.update_layout(showlegend=False)
        st.plotly_chart(fig_amounts, use_container_width=True)
        
        # Category breakdown
        category_counts = filtered_scholarships['category'].value_counts()
        fig_categories = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Scholarship Categories (Your Matches)"
        )
        st.plotly_chart(fig_categories, use_container_width=True)
    
    with col2:
        st.header("🎯 Match Quality Analysis")
        
        # Calculate match scores for all filtered scholarships
        match_scores = []
        for _, scholarship in filtered_scholarships.iterrows():
            score = calculate_match_score(scholarship, user_profile)
            match_scores.append(score)
        
        filtered_scholarships_with_scores = filtered_scholarships.copy()
        filtered_scholarships_with_scores['match_score'] = match_scores
        
        # Match score distribution
        fig_scores = px.histogram(
            filtered_scholarships_with_scores,
            x='match_score',
            bins=15,
            title="Distribution of Match Scores",
            labels={'match_score': 'Match Score (%)', 'count': 'Number of Scholarships'}
        )
        st.plotly_chart(fig_scores, use_container_width=True)
        
        # Top categories by average match score
        category_scores = filtered_scholarships_with_scores.groupby('category')['match_score'].mean().sort_values(ascending=False)
        fig_category_scores = px.bar(
            x=category_scores.values,
            y=category_scores.index,
            orientation='h',
            title="Average Match Score by Category",
            labels={'x': 'Average Match Score (%)', 'y': 'Category'}
        )
        st.plotly_chart(fig_category_scores, use_container_width=True)
    
    # Deadline tracking
    st.header("⏰ Upcoming Deadlines")
    
    # Convert deadline to datetime and sort
    filtered_scholarships['deadline_date'] = pd.to_datetime(filtered_scholarships['deadline'])
    upcoming_deadlines = filtered_scholarships.sort_values('deadline_date').head(10)
    
    deadline_data = []
    for _, scholarship in upcoming_deadlines.iterrows():
        days_until = (scholarship['deadline_date'] - pd.Timestamp.now()).days
        deadline_data.append({
            'Scholarship': scholarship['title'],
            'Deadline': scholarship['deadline'],
            'Days Until': max(0, days_until),
            'Amount': f"${scholarship['amount']:,}",
            'Category': scholarship['category']
        })
    
    deadline_df = pd.DataFrame(deadline_data)
    st.dataframe(deadline_df, use_container_width=True)
    
    # Action items
    st.header("✅ Recommended Actions")
    
    urgent_deadlines = deadline_df[deadline_df['Days Until'] <= 30]
    if not urgent_deadlines.empty:
        st.warning(f"⚠️ {len(urgent_deadlines)} scholarships have deadlines within 30 days!")
        for _, deadline in urgent_deadlines.iterrows():
            st.write(f"• **{deadline['Scholarship']}** - {deadline['Days Until']} days remaining")
    
    st.info("💡 **Tips for Success:**")
    st.write("• Start applications early - most scholarships require essays and recommendations")
    st.write("• Keep your profile updated to discover new opportunities")
    st.write("• Set up deadline reminders for scholarships you're interested in")
    st.write("• Consider scholarships with lower match scores - they might have less competition")

def filter_scholarships_for_user(scholarships_df, user_profile):
    """Filter scholarships based on user profile"""
    filtered_df = scholarships_df.copy()
    
    # Filter by demographics
    if user_profile['demographics']:
        demographic_mask = scholarships_df['target_demographics'].apply(
            lambda x: any(demo in user_profile['demographics'] for demo in x)
        )
        filtered_df = filtered_df[demographic_mask]
    
    # Filter by field of study
    if user_profile['field_of_study']:
        field_mask = scholarships_df['category'].str.contains(
            user_profile['field_of_study'], case=False, na=False
        )
        filtered_df = filtered_df[field_mask | 
                                 scholarships_df['target_demographics'].apply(
                                     lambda x: user_profile['field_of_study'].lower() in ' '.join(x).lower()
                                 )]
    
    # Filter by academic level
    if user_profile['academic_level']:
        level_mask = scholarships_df['eligibility_criteria'].str.contains(
            user_profile['academic_level'], case=False, na=False
        )
        filtered_df = filtered_df[level_mask]
    
    return filtered_df

def calculate_match_score(scholarship, user_profile):
    """Calculate a match score between scholarship and user profile"""
    score = 0
    max_score = 0
    
    # Demographics match (40% weight)
    max_score += 40
    if user_profile['demographics']:
        demographic_matches = sum(1 for demo in user_profile['demographics'] 
                                if demo in scholarship['target_demographics'])
        if demographic_matches > 0:
            score += min(40, (demographic_matches / len(user_profile['demographics'])) * 40)
    
    # Field of study match (30% weight)
    max_score += 30
    if user_profile['field_of_study']:
        if (user_profile['field_of_study'].lower() in scholarship['category'].lower() or
            any(user_profile['field_of_study'].lower() in demo.lower() 
                for demo in scholarship['target_demographics'])):
            score += 30
    
    # Academic level match (20% weight)
    max_score += 20
    if user_profile['academic_level']:
        if user_profile['academic_level'].lower() in scholarship['eligibility_criteria'].lower():
            score += 20
    
    # General eligibility (10% weight)
    max_score += 10
    score += 10  # Assume basic eligibility
    
    return round((score / max_score) * 100) if max_score > 0 else 0

if __name__ == "__main__":
    main()
