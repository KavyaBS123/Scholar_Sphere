import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from utils.ai_matching_engine import AdvancedAIMatchingEngine
from utils.ai_enhancer import AIEnhancer

st.set_page_config(
    page_title="AI Application Assistant - ScholarSphere",
    page_icon="🤖",
    layout="wide"
)

def main():
    st.title("🤖 AI Application Assistant")
    
    if 'data_manager' not in st.session_state:
        st.error("Please visit the main page first.")
        return
    
    # Initialize AI components
    ai_matcher = AdvancedAIMatchingEngine()
    ai_enhancer = AIEnhancer()
    
    if not ai_matcher.is_available():
        st.warning("AI features require OpenAI API key. Some features may be limited.")
    
    # Get user data
    dm = st.session_state.data_manager
    user_profile = st.session_state.get('user_profile', {})
    scholarships_df = dm.get_scholarships_df()
    
    # Sidebar for scholarship selection
    st.sidebar.header("Select Scholarship")
    
    if scholarships_df.empty:
        st.sidebar.warning("No scholarships loaded.")
        selected_scholarship = None
    else:
        scholarship_options = {
            f"{row['title']} - ${row['amount']:,}": row 
            for _, row in scholarships_df.iterrows()
        }
        
        selected_title = st.sidebar.selectbox(
            "Choose a scholarship for AI assistance:",
            list(scholarship_options.keys())
        )
        selected_scholarship = scholarship_options[selected_title]
    
    if selected_scholarship is None:
        st.info("Please select a scholarship to get AI-powered application assistance.")
        return
    
    # Convert selected scholarship to dict
    scholarship_dict = selected_scholarship.to_dict()
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Eligibility Analysis", 
        "📝 Essay Assistant", 
        "📋 Application Strategy", 
        "📚 Requirements Guide",
        "🎯 Success Tips"
    ])
    
    with tab1:
        st.header("Comprehensive Eligibility Analysis")
        
        if st.button("Analyze Eligibility", type="primary", key="analyze_eligibility"):
            with st.spinner("Analyzing your eligibility..."):
                try:
                    analysis = ai_matcher.calculate_comprehensive_eligibility_score(
                        scholarship_dict, user_profile
                    )
                    
                    # Display overall score
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        score_color = "green" if analysis['overall_score'] >= 70 else "orange" if analysis['overall_score'] >= 50 else "red"
                        st.metric(
                            "Overall Eligibility Score",
                            f"{analysis['overall_score']}/100",
                            delta=None
                        )
                        st.markdown(f"<div style='color: {score_color}; font-weight: bold;'>{'Excellent' if analysis['overall_score'] >= 70 else 'Good' if analysis['overall_score'] >= 50 else 'Needs Improvement'}</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.metric("Success Probability", f"{analysis.get('success_probability', 0)}/100")
                    
                    with col3:
                        difficulty_map = {1: "Very Easy", 2: "Easy", 3: "Medium", 4: "Hard", 5: "Very Hard"}
                        difficulty = analysis.get('application_difficulty', 3)
                        st.metric("Application Difficulty", difficulty_map.get(difficulty, "Medium"))
                    
                    # Detailed breakdown
                    st.subheader("Detailed Score Breakdown")
                    
                    breakdown_col1, breakdown_col2 = st.columns(2)
                    
                    with breakdown_col1:
                        st.write("**Compatibility Scores:**")
                        st.progress(analysis.get('demographic_match', 0) / 100, text=f"Demographic Match: {analysis.get('demographic_match', 0)}%")
                        st.progress(analysis.get('academic_match', 0) / 100, text=f"Academic Fit: {analysis.get('academic_match', 0)}%")
                        st.progress(analysis.get('field_relevance', 0) / 100, text=f"Field Relevance: {analysis.get('field_relevance', 0)}%")
                        st.progress(analysis.get('financial_alignment', 0) / 100, text=f"Financial Alignment: {analysis.get('financial_alignment', 0)}%")
                    
                    with breakdown_col2:
                        st.write("**Your Strengths:**")
                        for strength in analysis.get('strengths', []):
                            st.write(f"✅ {strength}")
                        
                        if analysis.get('missing_requirements'):
                            st.write("**Areas to Address:**")
                            for req in analysis.get('missing_requirements', []):
                                st.write(f"❌ {req}")
                    
                    # Recommendations
                    if analysis.get('recommendations'):
                        st.subheader("AI Recommendations")
                        for i, rec in enumerate(analysis.get('recommendations', []), 1):
                            st.write(f"{i}. {rec}")
                    
                except Exception as e:
                    st.error(f"Error during analysis: {str(e)}")
    
    with tab2:
        st.header("AI-Powered Essay Assistant")
        
        # Essay prompt input
        essay_prompt = st.text_area(
            "Essay Prompt (optional):",
            placeholder="Paste the scholarship essay prompt here for personalized guidance...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Get Essay Tips", type="primary", key="essay_tips"):
                with st.spinner("Generating personalized essay tips..."):
                    try:
                        tips = ai_enhancer.generate_essay_tips(scholarship_dict, user_profile)
                        
                        st.subheader("Personalized Essay Writing Tips")
                        for i, tip in enumerate(tips, 1):
                            st.write(f"**{i}.** {tip}")
                            
                    except Exception as e:
                        st.error(f"Error generating essay tips: {str(e)}")
        
        with col2:
            if st.button("Generate Essay Outline", key="essay_outline"):
                with st.spinner("Creating essay outline..."):
                    try:
                        if ai_matcher.is_available():
                            # Generate detailed essay strategy
                            eligibility_analysis = ai_matcher.calculate_comprehensive_eligibility_score(
                                scholarship_dict, user_profile
                            )
                            strategy = ai_matcher.generate_personalized_application_strategy(
                                scholarship_dict, user_profile, eligibility_analysis
                            )
                            
                            essay_strategy = strategy.get('essay_strategy', {})
                            
                            st.subheader("Essay Strategy & Outline")
                            
                            st.write("**Recommended Themes:**")
                            for theme in essay_strategy.get('main_themes', []):
                                st.write(f"• {theme}")
                            
                            st.write("**Key Points to Include:**")
                            for point in essay_strategy.get('key_points', []):
                                st.write(f"• {point}")
                            
                            st.write(f"**Recommended Tone:** {essay_strategy.get('tone', 'Professional')}")
                            st.write(f"**Suggested Word Count:** {essay_strategy.get('word_count_suggestion', 500)} words")
                        else:
                            st.warning("Essay outline generation requires AI features.")
                            
                    except Exception as e:
                        st.error(f"Error generating essay outline: {str(e)}")
        
        # Essay improvement tool
        st.subheader("Essay Review & Improvement")
        user_essay = st.text_area(
            "Paste your essay draft for AI feedback:",
            placeholder="Paste your essay draft here to get AI-powered feedback and suggestions...",
            height=200
        )
        
        if st.button("Review My Essay", key="review_essay") and user_essay:
            if ai_matcher.is_available():
                with st.spinner("Analyzing your essay..."):
                    try:
                        # Create essay review prompt
                        prompt = f"""
                        Review this scholarship essay and provide constructive feedback.
                        
                        Scholarship: {scholarship_dict.get('title', 'N/A')}
                        Target Demographics: {scholarship_dict.get('target_demographics', [])}
                        
                        Student Essay:
                        {user_essay}
                        
                        Provide feedback on:
                        1. Clarity and coherence
                        2. Relevance to scholarship goals
                        3. Personal story effectiveness
                        4. Grammar and style
                        5. Specific improvement suggestions
                        """
                        
                        response = ai_matcher.client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "You are an expert essay reviewer who helps students improve their scholarship applications. Provide constructive, encouraging feedback."
                                },
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=500,
                            temperature=0.3
                        )
                        
                        feedback = response.choices[0].message.content.strip()
                        
                        st.subheader("AI Essay Feedback")
                        st.write(feedback)
                        
                    except Exception as e:
                        st.error(f"Error reviewing essay: {str(e)}")
            else:
                st.warning("Essay review requires AI features.")
    
    with tab3:
        st.header("Personalized Application Strategy")
        
        if st.button("Generate Strategy", type="primary", key="generate_strategy"):
            with st.spinner("Creating your personalized application strategy..."):
                try:
                    # Get eligibility analysis first
                    eligibility_analysis = ai_matcher.calculate_comprehensive_eligibility_score(
                        scholarship_dict, user_profile
                    )
                    
                    # Generate strategy
                    strategy = ai_matcher.generate_personalized_application_strategy(
                        scholarship_dict, user_profile, eligibility_analysis
                    )
                    
                    # Display timeline
                    st.subheader("📅 Application Timeline")
                    timeline_df = pd.DataFrame(strategy.get('timeline', []))
                    if not timeline_df.empty:
                        for _, task in timeline_df.iterrows():
                            priority_emoji = "🔴" if task['priority'] >= 4 else "🟡" if task['priority'] >= 3 else "🟢"
                            st.write(f"**Week {task['week']}:** {priority_emoji} {task['task']}")
                    
                    # Competitive advantages
                    advantages = strategy.get('competitive_advantages', [])
                    if advantages:
                        st.subheader("🏆 Your Competitive Advantages")
                        for advantage in advantages:
                            st.write(f"✨ {advantage}")
                    
                    # Improvement areas
                    improvements = strategy.get('improvement_areas', [])
                    if improvements:
                        st.subheader("📈 Areas for Improvement")
                        for improvement in improvements:
                            st.write(f"🎯 {improvement}")
                    
                    # Networking suggestions
                    networking = strategy.get('networking_suggestions', [])
                    if networking:
                        st.subheader("🤝 Networking Opportunities")
                        for suggestion in networking:
                            st.write(f"👥 {suggestion}")
                    
                except Exception as e:
                    st.error(f"Error generating strategy: {str(e)}")
    
    with tab4:
        st.header("Application Requirements Guide")
        
        # Display scholarship requirements
        st.subheader("📋 Required Documents")
        
        requirements = scholarship_dict.get('application_requirements', 'Not specified')
        if requirements and requirements != 'Not specified':
            st.write(requirements)
        else:
            # Default requirements
            default_reqs = [
                "Personal Statement/Essay",
                "Official Transcripts",
                "Letters of Recommendation (usually 2-3)",
                "Completed Application Form",
                "Proof of Enrollment",
                "Financial Aid Information (if applicable)"
            ]
            for req in default_reqs:
                st.write(f"• {req}")
        
        # Eligibility criteria
        st.subheader("✅ Eligibility Criteria")
        eligibility = scholarship_dict.get('eligibility_criteria', 'Not specified')
        if eligibility and eligibility != 'Not specified':
            st.write(eligibility)
        else:
            st.write("Eligibility criteria not specified for this scholarship.")
        
        # Important dates
        st.subheader("📅 Important Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Deadline:** {scholarship_dict.get('deadline', 'Not specified')}")
            st.write(f"**Award Amount:** ${scholarship_dict.get('amount', 0):,}")
        
        with col2:
            st.write(f"**GPA Requirement:** {scholarship_dict.get('gpa_requirement', 'Not specified')}")
            st.write(f"**Category:** {scholarship_dict.get('category', 'Not specified')}")
        
        # Contact information
        if scholarship_dict.get('website') or scholarship_dict.get('contact_info'):
            st.subheader("📞 Contact Information")
            if scholarship_dict.get('website'):
                st.write(f"**Website:** {scholarship_dict.get('website')}")
            if scholarship_dict.get('contact_info'):
                st.write(f"**Contact:** {scholarship_dict.get('contact_info')}")
    
    with tab5:
        st.header("AI Success Tips & Insights")
        
        if st.button("Get Success Tips", type="primary", key="success_tips"):
            with st.spinner("Generating personalized success tips..."):
                try:
                    if ai_matcher.is_available():
                        # Generate insights
                        recent_analyses = [ai_matcher.calculate_comprehensive_eligibility_score(
                            scholarship_dict, user_profile
                        )]
                        
                        insights = ai_matcher.generate_ai_insights_dashboard(
                            user_profile, recent_analyses
                        )
                        
                        # Display insights
                        st.subheader("🎯 Key Insights")
                        for insight in insights.get('key_insights', []):
                            st.info(insight)
                        
                        st.subheader("📈 Success Predictors")
                        for predictor in insights.get('success_predictors', []):
                            st.write(f"✅ {predictor}")
                        
                        st.subheader("🚀 Next Actions")
                        for i, action in enumerate(insights.get('next_actions', []), 1):
                            st.write(f"{i}. {action}")
                        
                        st.subheader("🔍 Opportunity Alerts")
                        for alert in insights.get('opportunity_alerts', []):
                            st.warning(alert)
                    else:
                        # Basic tips without AI
                        st.subheader("General Success Tips")
                        basic_tips = [
                            "Start your application early to avoid rushing",
                            "Tailor your essay to each specific scholarship",
                            "Highlight your unique experiences and perspectives",
                            "Proofread everything multiple times",
                            "Get strong letters of recommendation from people who know you well",
                            "Follow all instructions carefully",
                            "Submit before the deadline"
                        ]
                        for tip in basic_tips:
                            st.write(f"• {tip}")
                
                except Exception as e:
                    st.error(f"Error generating success tips: {str(e)}")
        
        # Additional resources
        st.subheader("📚 Additional Resources")
        st.write("""
        **General Application Tips:**
        - Research the organization offering the scholarship
        - Use specific examples in your essays
        - Show, don't just tell about your accomplishments
        - Be authentic and genuine in your writing
        - Demonstrate financial need if applicable
        
        **Common Mistakes to Avoid:**
        - Generic essays that could apply to any scholarship
        - Missing deadlines or requirements
        - Poor grammar and spelling
        - Not answering the essay prompt directly
        - Failing to follow formatting guidelines
        """)

if __name__ == "__main__":
    main()