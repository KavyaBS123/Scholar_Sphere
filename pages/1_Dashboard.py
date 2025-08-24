import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ai_enhancer import AIEnhancer
from utils.ai_matching_engine import AdvancedAIMatchingEngine
from utils.clustering import ScholarshipClustering
import numpy as np

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
    
    # Initialize AI components
    ai_enhancer = AIEnhancer()
    ai_matcher = AdvancedAIMatchingEngine()
    
    # AI-Powered Personalized Dashboard
    st.header("🤖 AI-Powered Recommendations")
    
    # Get AI insights first
    if ai_matcher.is_available() and not scholarships_df.empty:
        with st.spinner("AI is analyzing scholarships for you..."):
            try:
                # Convert scholarships to list of dicts for AI analysis
                scholarships_list = scholarships_df.to_dict('records')
                
                # Get comprehensive analysis for top scholarships
                ai_analyses = ai_matcher.batch_analyze_scholarships(scholarships_list[:20], user_profile)
                
                # Generate dashboard insights
                dashboard_insights = ai_matcher.generate_ai_insights_dashboard(user_profile, ai_analyses)
                
                # Display AI insights
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    profile_strength = dashboard_insights.get('profile_strength_score', 0)
                    st.metric("Profile Strength", f"{profile_strength}%")
                    
                with col2:
                    if ai_analyses:
                        avg_eligibility = np.mean([a.get('overall_score', 0) for a in ai_analyses[:5]])
                        st.metric("Avg Eligibility Score", f"{avg_eligibility:.0f}%")
                    else:
                        st.metric("Avg Eligibility Score", "N/A")
                
                with col3:
                    if ai_analyses:
                        high_match_count = len([a for a in ai_analyses if a.get('overall_score', 0) >= 70])
                        st.metric("High-Match Scholarships", high_match_count)
                    else:
                        st.metric("High-Match Scholarships", 0)
                
                # Display key insights
                if dashboard_insights.get('key_insights'):
                    st.subheader("🎯 Key Insights")
                    for insight in dashboard_insights.get('key_insights', [])[:3]:
                        st.info(insight)
                
                # Display top AI-analyzed recommendations
                if ai_analyses:
                    st.subheader("Top AI-Matched Scholarships")
                    
                    for i, analysis in enumerate(ai_analyses[:3]):
                        scholarship_id = analysis.get('scholarship_id')
                        if scholarship_id:
                            # Find the scholarship in the dataframe
                            scholarship_row = scholarships_df[scholarships_df['id'] == scholarship_id]
                            if not scholarship_row.empty:
                                scholarship = scholarship_row.iloc[0]
                                display_ai_recommendation(scholarship, analysis, i)
                
            except Exception as e:
                st.error(f"AI analysis failed: {str(e)}")
                # Fallback to basic filtering
                filtered_scholarships = filter_scholarships_for_user(scholarships_df, user_profile)
                if not filtered_scholarships.empty:
                    top_recommendations = filtered_scholarships.head(3)
                    display_basic_recommendations(top_recommendations, user_profile)
    else:
        # Fallback to basic recommendations
        filtered_scholarships = filter_scholarships_for_user(scholarships_df, user_profile)
        
        if filtered_scholarships.empty:
            st.info("No matches found. Update your profile for better results.")
            return
        
        top_recommendations = filtered_scholarships.head(3)
        display_basic_recommendations(top_recommendations, user_profile)
    
    # Analytics section - only show if we have data
    if not scholarships_df.empty:
        # Get basic filtered scholarships for analytics
        filtered_scholarships = filter_scholarships_for_user(scholarships_df, user_profile)
        
        if not filtered_scholarships.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.header("📈 Your Opportunity Landscape")
                
                # Amount distribution of matching scholarships
                fig_amounts = px.histogram(
                    filtered_scholarships, 
                    x='amount',
                    nbins=20,
                    title="Distribution of Scholarship Amounts (Your Matches)",
                    labels={'amount': 'Award Amount ($)', 'count': 'Number of Scholarships'}
                )
                fig_amounts.update_layout(showlegend=False)
                st.plotly_chart(fig_amounts, use_container_width=True)
                
                # Category breakdown
                if 'category' in filtered_scholarships.columns:
                    category_counts = filtered_scholarships['category'].value_counts()
                    if not category_counts.empty:
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
                
                if match_scores:
                    filtered_scholarships_with_scores = filtered_scholarships.copy()
                    filtered_scholarships_with_scores['match_score'] = match_scores
                    
                    # Match score distribution
                    fig_scores = px.histogram(
                        filtered_scholarships_with_scores,
                        x='match_score',
                        nbins=15,
                        title="Distribution of Match Scores",
                        labels={'match_score': 'Match Score (%)', 'count': 'Number of Scholarships'}
                    )
                    st.plotly_chart(fig_scores, use_container_width=True)
                    
                    # Top categories by average match score
                    if 'category' in filtered_scholarships_with_scores.columns:
                        category_scores = filtered_scholarships_with_scores.groupby('category')['match_score'].mean().sort_values(ascending=False)
                        if not category_scores.empty:
                            fig_category_scores = px.bar(
                                x=category_scores.values,
                                y=category_scores.index,
                                orientation='h',
                                title="Average Match Score by Category",
                                labels={'x': 'Average Match Score (%)', 'y': 'Category'}
                            )
                            st.plotly_chart(fig_category_scores, use_container_width=True)
        else:
            st.info("Complete your profile to see analytics and recommendations.")
    
        # Deadline tracking
        st.header("⏰ Upcoming Deadlines")
        
        if not filtered_scholarships.empty and 'deadline' in filtered_scholarships.columns:
            try:
                # Convert deadline to datetime and sort
                filtered_scholarships_copy = filtered_scholarships.copy()
                filtered_scholarships_copy['deadline_date'] = pd.to_datetime(filtered_scholarships_copy['deadline'], errors='coerce')
                valid_deadlines = filtered_scholarships_copy.dropna(subset=['deadline_date'])
                
                if not valid_deadlines.empty:
                    upcoming_deadlines = valid_deadlines.sort_values('deadline_date').head(10)
                    
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
                    
                    if deadline_data:
                        deadline_df = pd.DataFrame(deadline_data)
                        st.dataframe(deadline_df, use_container_width=True)
                        
                        # Action items
                        st.header("✅ Recommended Actions")
                        
                        urgent_deadlines = deadline_df[deadline_df['Days Until'] <= 30]
                        if not urgent_deadlines.empty:
                            st.warning(f"⚠️ {len(urgent_deadlines)} scholarships have deadlines within 30 days!")
                            for _, deadline in urgent_deadlines.iterrows():
                                st.write(f"• **{deadline['Scholarship']}** - {deadline['Days Until']} days remaining")
                    else:
                        st.info("No upcoming deadlines found.")
                else:
                    st.info("No valid deadline information available.")
            except Exception as e:
                st.warning(f"Could not process deadline information: {str(e)}")
        else:
            st.info("No deadline information available.")
    
        # Tips section
        st.info("💡 **Tips for Success:**")
        st.write("• Start applications early - most scholarships require essays and recommendations")
        st.write("• Keep your profile updated to discover new opportunities")
        st.write("• Set up deadline reminders for scholarships you're interested in")
        st.write("• Consider scholarships with lower match scores - they might have less competition")
    else:
        st.info("No scholarship data available. Please check back later or contact support.")

def display_ai_recommendation(scholarship, analysis, index):
    """Display AI-enhanced scholarship recommendation"""
    with st.container():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Title with AI score indicator
            score = analysis.get('overall_score', 0)
            score_emoji = "🏆" if score >= 80 else "🏅" if score >= 60 else "📋"
            st.subheader(f"{score_emoji} {scholarship['title']}")
            
            # AI-generated summary if available
            if analysis.get('strengths'):
                st.write("**Why this is a great match:**")
                for strength in analysis.get('strengths', [])[:2]:
                    st.write(f"✅ {strength}")
            
            # Basic info
            st.write(f"**Category:** {scholarship['category']}")
            st.write(f"**Deadline:** {scholarship['deadline']}")
            
            # AI recommendations
            if analysis.get('recommendations'):
                with st.expander("AI Recommendations"):
                    for rec in analysis.get('recommendations', [])[:3]:
                        st.write(f"💡 {rec}")
        
        with col2:
            st.metric("Award Amount", f"${scholarship['amount']:,}")
            st.metric("AI Match Score", f"{score}%")
            
            success_prob = analysis.get('success_probability', 0)
            st.metric("Success Probability", f"{success_prob}%")
            
            difficulty = analysis.get('application_difficulty', 3)
            difficulty_map = {1: "Very Easy", 2: "Easy", 3: "Medium", 4: "Hard", 5: "Very Hard"}
            st.metric("Difficulty", difficulty_map.get(difficulty, "Medium"))
            
            # Action buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Analyze", key=f"analyze_{index}"):
                    st.switch_page("pages/8_AI_Application_Assistant.py")
            with col_btn2:
                if st.button("Apply", key=f"apply_{index}"):
                    # Add to application tracker
                    dm = st.session_state.data_manager
                    dm.add_application(scholarship['id'], scholarship['title'])
                    st.success("Added to your application tracker!")
        
        st.markdown("---")

def display_basic_recommendations(top_recommendations, user_profile):
    """Display basic recommendations without AI analysis"""
    for idx, (_, scholarship) in enumerate(top_recommendations.iterrows()):
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(f"🏆 {scholarship['title']}")
                st.write(f"**Description:** {scholarship['description'][:200]}...")
                st.write(f"**Category:** {scholarship['category']}")
                st.write(f"**Target Demographics:** {', '.join(scholarship['target_demographics'])}")
                st.write(f"**Deadline:** {scholarship['deadline']}")
            
            with col2:
                st.metric("Award Amount", f"${scholarship['amount']:,}")
                st.metric("GPA Required", f"{scholarship['gpa_requirement']}")
                match_score = calculate_match_score(scholarship, user_profile)
                st.metric("Match Score", f"{match_score}%")
                
                if st.button(f"Apply Now", key=f"apply_{idx}"):
                    dm = st.session_state.data_manager
                    dm.add_application(scholarship['id'], scholarship['title'])
                    st.success(f"Added {scholarship['title']} to your application tracker!")
            
            st.markdown("---")

def filter_scholarships_for_user(scholarships_df, user_profile):
    """Filter scholarships based on user profile"""
    if scholarships_df.empty:
        return scholarships_df
        
    filtered_df = scholarships_df.copy()
    
    # Filter by demographics
    if user_profile.get('demographics'):
        demographic_mask = scholarships_df['target_demographics'].apply(
            lambda x: any(demo in user_profile['demographics'] for demo in x) if isinstance(x, list) else False
        )
        filtered_df = filtered_df[demographic_mask]
    
    # Filter by field of study
    if user_profile.get('field_of_study'):
        field_mask = scholarships_df['category'].str.contains(
            user_profile['field_of_study'], case=False, na=False
        )
        filtered_df = filtered_df[field_mask | 
                                 scholarships_df['target_demographics'].apply(
                                     lambda x: user_profile['field_of_study'].lower() in ' '.join(x).lower() if isinstance(x, list) else False
                                 )]
    
    # Filter by academic level
    if user_profile.get('academic_level') and 'eligibility_criteria' in scholarships_df.columns:
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
