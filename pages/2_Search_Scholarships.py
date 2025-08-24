import streamlit as st
import pandas as pd
import plotly.express as px
from utils.ai_enhancer import AIEnhancer
from utils.ai_matching_engine import AdvancedAIMatchingEngine

st.set_page_config(
    page_title="Search Scholarships - ScholarSphere",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("Search Scholarships")
    
    if 'data_manager' not in st.session_state:
        st.error("Please visit the main page first.")
        return
    
    dm = st.session_state.data_manager
    scholarships_df = dm.get_scholarships_df()
    
    # Initialize AI components
    ai_enhancer = AIEnhancer()
    ai_matcher = AdvancedAIMatchingEngine()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # AI-Enhanced Search
    st.sidebar.header("🤖 AI-Enhanced Search")
    
    # Get AI search suggestions
    user_profile = st.session_state.get('user_profile', {})
    if st.sidebar.button("Get AI Search Suggestions") and ai_enhancer.is_available():
        with st.sidebar:
            with st.spinner("Generating suggestions..."):
                try:
                    suggestions = ai_enhancer.generate_search_suggestions(user_profile)
                    st.write("**Suggested Search Terms:**")
                    for suggestion in suggestions:
                        if st.button(suggestion, key=f"suggest_{suggestion}"):
                            st.session_state['search_term'] = suggestion
                            st.rerun()
                except Exception as e:
                    st.error(f"Error generating suggestions: {str(e)}")
    
    # Text search with AI suggestions
    search_term = st.sidebar.text_input(
        "Search:",
        value=st.session_state.get('search_term', ''),
        placeholder="Enter keywords or use AI suggestions above..."
    )
    
    # Save search term to session state
    if search_term:
        st.session_state['search_term'] = search_term
    
    # Amount range
    if not scholarships_df.empty and 'amount' in scholarships_df.columns:
        min_amount, max_amount = st.sidebar.slider(
            "Award Amount",
            min_value=int(scholarships_df['amount'].min()),
            max_value=int(scholarships_df['amount'].max()),
            value=(int(scholarships_df['amount'].min()), int(scholarships_df['amount'].max())),
            step=1000,
            format="$%d"
        )
    else:
        min_amount, max_amount = st.sidebar.slider(
            "Award Amount",
            min_value=0,
            max_value=100000,
            value=(0, 100000),
            step=1000,
            format="$%d"
        )
    
    # Category filter
    if not scholarships_df.empty and 'category' in scholarships_df.columns:
        categories = sorted(scholarships_df['category'].unique())
        selected_categories = st.sidebar.multiselect(
            "Categories",
            categories,
            default=categories
        )
    else:
        categories = []
        selected_categories = st.sidebar.multiselect(
            "Categories",
            categories
        )
    
    # Demographics filter
    all_demographics = set()
    if not scholarships_df.empty and 'target_demographics' in scholarships_df.columns:
        for demo_list in scholarships_df['target_demographics']:
            if isinstance(demo_list, list):
                all_demographics.update(demo_list)
    
    selected_demographics = st.sidebar.multiselect(
        "Demographics",
        sorted(list(all_demographics))
    )
    
    # Academic level filter
    academic_levels = ["High School", "Undergraduate", "Graduate", "Doctoral"]
    selected_academic_levels = st.sidebar.multiselect(
        "Academic Level",
        academic_levels,
        default=academic_levels
    )
    
    # GPA requirement
    max_gpa_requirement = st.sidebar.slider(
        "📊 Maximum GPA Requirement",
        min_value=2.0,
        max_value=4.0,
        value=4.0,
        step=0.1
    )
    
    # Deadline filter
    deadline_filter = st.sidebar.selectbox(
        "⏰ Deadline Filter",
        ["All", "Next 30 days", "Next 90 days", "Next 6 months", "Next year"]
    )
    
    # Apply filters
    filtered_df = apply_filters(
        scholarships_df,
        search_term,
        min_amount,
        max_amount,
        selected_categories,
        selected_demographics,
        selected_academic_levels,
        max_gpa_requirement,
        deadline_filter
    )
    
    # Display results summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Results", len(filtered_df))
    with col2:
        if len(filtered_df) > 0:
            avg_amount = filtered_df['amount'].mean()
            st.metric("Average Award", f"${avg_amount:,.0f}")
        else:
            st.metric("Average Award", "$0")
    with col3:
        if len(filtered_df) > 0:
            total_value = filtered_df['amount'].sum()
            st.metric("Total Value", f"${total_value:,.0f}")
        else:
            st.metric("Total Value", "$0")
    
    if filtered_df.empty:
        st.warning("No scholarships match your current filters. Try adjusting your criteria.")
        return
    
    # AI-Enhanced Sorting and Analysis
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.subheader(f"Found {len(filtered_df)} scholarships")
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["AI Match Score", "Amount (High to Low)", "Amount (Low to High)", "Deadline", "Alphabetical"]
        )
    with col3:
        analyze_with_ai = st.checkbox(
            "AI Analysis",
            value=ai_matcher.is_available(),
            help="Get AI-powered match scores and recommendations"
        )
    
    # AI Analysis and Sorting
    if analyze_with_ai and ai_matcher.is_available() and not filtered_df.empty:
        with st.spinner("AI is analyzing scholarships for optimal matches..."):
            try:
                # Convert to list for AI analysis
                scholarships_list = filtered_df.to_dict('records')
                user_profile = st.session_state.get('user_profile', {})
                
                # Get AI analysis for filtered scholarships
                ai_analyses = ai_matcher.batch_analyze_scholarships(scholarships_list, user_profile)
                
                # Add AI scores to dataframe
                ai_scores_df = pd.DataFrame(ai_analyses)
                if not ai_scores_df.empty:
                    # Merge with filtered_df based on scholarship_id
                    filtered_df = filtered_df.merge(
                        ai_scores_df[['scholarship_id', 'overall_score', 'success_probability', 'application_difficulty']], 
                        left_on='id', 
                        right_on='scholarship_id', 
                        how='left'
                    )
                    
                    # Store analyses for display
                    st.session_state['current_ai_analyses'] = {a['scholarship_id']: a for a in ai_analyses}
                    
                    # Show AI insights summary
                    high_match_count = len([a for a in ai_analyses if a.get('overall_score', 0) >= 70])
                    avg_score = sum([a.get('overall_score', 0) for a in ai_analyses]) / len(ai_analyses)
                    
                    st.info(f"🤖 AI Analysis Complete: {high_match_count} high-match scholarships found (avg. score: {avg_score:.0f}%)")
                    
            except Exception as e:
                st.error(f"AI analysis failed: {str(e)}")
                filtered_df['overall_score'] = 0
    else:
        filtered_df['overall_score'] = 0
    
    # Apply sorting
    if sort_by == "AI Match Score":
        filtered_df = filtered_df.sort_values('overall_score', ascending=False)
    elif sort_by == "Amount (High to Low)":
        filtered_df = filtered_df.sort_values('amount', ascending=False)
    elif sort_by == "Amount (Low to High)":
        filtered_df = filtered_df.sort_values('amount', ascending=True)
    elif sort_by == "Deadline":
        filtered_df['deadline_date'] = pd.to_datetime(filtered_df['deadline'])
        filtered_df = filtered_df.sort_values('deadline_date')
    elif sort_by == "Alphabetical":
        filtered_df = filtered_df.sort_values('title')
    
    # Pagination
    results_per_page = st.selectbox("Results per page:", [10, 25, 50], index=1)
    total_pages = len(filtered_df) // results_per_page + (1 if len(filtered_df) % results_per_page > 0 else 0)
    
    if total_pages > 1:
        page = st.selectbox(f"Page (1-{total_pages}):", range(1, total_pages + 1))
        start_idx = (page - 1) * results_per_page
        end_idx = min(start_idx + results_per_page, len(filtered_df))
        page_df = filtered_df.iloc[start_idx:end_idx]
    else:
        page_df = filtered_df
    
    # Display scholarships with AI enhancements
    for idx, (_, scholarship) in enumerate(page_df.iterrows()):
        # Determine display icon based on AI score
        ai_score = scholarship.get('overall_score', 0)
        if ai_score >= 80:
            icon = "🏆"  # High match
        elif ai_score >= 60:
            icon = "🎯"  # Good match
        elif ai_score >= 40:
            icon = "📋"  # Moderate match
        else:
            icon = "📄"  # Basic match
        
        # Enhanced title with AI score
        title_suffix = f" (AI: {ai_score}%)" if ai_score > 0 else ""
        
        with st.expander(f"{icon} {scholarship['title']} - ${scholarship['amount']:,}{title_suffix}", expanded=False):
            display_scholarship_details_enhanced(scholarship, ai_enhancer, ai_matcher, idx)
    
    # Analytics section
    if len(filtered_df) > 5:
        st.header("📊 Search Results Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Amount distribution
            fig_amounts = px.histogram(
                filtered_df,
                x='amount',
                bins=min(20, len(filtered_df)//2),
                title="Award Amount Distribution",
                labels={'amount': 'Award Amount ($)', 'count': 'Number of Scholarships'}
            )
            st.plotly_chart(fig_amounts, use_container_width=True)
        
        with col2:
            # Category distribution
            category_counts = filtered_df['category'].value_counts()
            fig_categories = px.bar(
                x=category_counts.values,
                y=category_counts.index,
                orientation='h',
                title="Scholarships by Category",
                labels={'x': 'Number of Scholarships', 'y': 'Category'}
            )
            st.plotly_chart(fig_categories, use_container_width=True)

def apply_filters(df, search_term, min_amount, max_amount, categories, demographics, 
                 academic_levels, max_gpa, deadline_filter):
    """Apply all filters to the scholarship dataframe"""
    filtered_df = df.copy()
    
    # Text search
    if search_term:
        search_mask = (
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['description'].str.contains(search_term, case=False, na=False) |
            filtered_df['category'].str.contains(search_term, case=False, na=False) |
            filtered_df['eligibility_criteria'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[search_mask]
    
    # Amount range
    filtered_df = filtered_df[
        (filtered_df['amount'] >= min_amount) & 
        (filtered_df['amount'] <= max_amount)
    ]
    
    # Categories
    if categories:
        filtered_df = filtered_df[filtered_df['category'].isin(categories)]
    
    # Demographics
    if demographics:
        demo_mask = filtered_df['target_demographics'].apply(
            lambda x: any(demo in demographics for demo in x)
        )
        filtered_df = filtered_df[demo_mask]
    
    # Academic levels
    if academic_levels:
        level_mask = filtered_df['eligibility_criteria'].apply(
            lambda x: any(level.lower() in x.lower() for level in academic_levels)
        )
        filtered_df = filtered_df[level_mask]
    
    # GPA requirement
    filtered_df = filtered_df[filtered_df['gpa_requirement'] <= max_gpa]
    
    # Deadline filter
    if deadline_filter != "All":
        filtered_df['deadline_date'] = pd.to_datetime(filtered_df['deadline'])
        now = pd.Timestamp.now()
        
        if deadline_filter == "Next 30 days":
            cutoff = now + pd.Timedelta(days=30)
        elif deadline_filter == "Next 90 days":
            cutoff = now + pd.Timedelta(days=90)
        elif deadline_filter == "Next 6 months":
            cutoff = now + pd.Timedelta(days=180)
        elif deadline_filter == "Next year":
            cutoff = now + pd.Timedelta(days=365)
        
        filtered_df = filtered_df[filtered_df['deadline_date'] <= cutoff]
    
    return filtered_df

def display_scholarship_details_enhanced(scholarship, ai_enhancer, ai_matcher, idx):
    """Display enhanced scholarship information with AI analysis"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Get AI analysis if available
        scholarship_id = scholarship.get('id')
        ai_analysis = st.session_state.get('current_ai_analyses', {}).get(scholarship_id, {})
        
        # AI-enhanced description
        if ai_enhancer.is_available():
            try:
                summary = ai_enhancer.summarize_scholarship(scholarship.to_dict())
                st.markdown(f"**AI Summary:** {summary}")
            except Exception as e:
                st.write(f"**Description:** {scholarship['description'][:300]}...")
        else:
            st.write(f"**Description:** {scholarship['description'][:300]}...")
        
        # AI Insights
        if ai_analysis:
            with st.expander("🤖 AI Insights", expanded=False):
                strengths = ai_analysis.get('strengths', [])
                if strengths:
                    st.write("**Your Advantages:**")
                    for strength in strengths[:3]:
                        st.write(f"✅ {strength}")
                
                recommendations = ai_analysis.get('recommendations', [])
                if recommendations:
                    st.write("**AI Recommendations:**")
                    for rec in recommendations[:3]:
                        st.write(f"💡 {rec}")
                
                missing_reqs = ai_analysis.get('missing_requirements', [])
                if missing_reqs:
                    st.write("**Areas to Address:**")
                    for req in missing_reqs[:3]:
                        st.write(f"⚠️ {req}")
        
        # Basic scholarship info
        st.write(f"**Category:** {scholarship['category']}")
        st.write(f"**Target Demographics:** {', '.join(scholarship['target_demographics'])}")
        st.write(f"**Eligibility:** {scholarship['eligibility_criteria'][:200]}...")
        
        if scholarship.get('website'):
            st.markdown(f"**Website:** [{scholarship['website']}]({scholarship['website']})")
    
    with col2:
        # Metrics with AI enhancements
        st.metric("Award Amount", f"${scholarship['amount']:,}")
        st.metric("GPA Requirement", f"{scholarship['gpa_requirement']}")
        
        # AI-specific metrics
        if ai_analysis:
            ai_score = ai_analysis.get('overall_score', 0)
            score_color = "green" if ai_score >= 70 else "orange" if ai_score >= 50 else "red"
            st.metric("AI Match Score", f"{ai_score}%")
            
            success_prob = ai_analysis.get('success_probability', 0)
            st.metric("Success Probability", f"{success_prob}%")
            
            difficulty = ai_analysis.get('application_difficulty', 3)
            difficulty_map = {1: "Very Easy", 2: "Easy", 3: "Medium", 4: "Hard", 5: "Very Hard"}
            st.metric("Difficulty", difficulty_map.get(difficulty, "Medium"))
        
        st.write(f"**Deadline:** {scholarship['deadline']}")
        if scholarship.get('contact_info'):
            st.write(f"**Contact:** {scholarship['contact_info'][:50]}...")
        
        # Enhanced action buttons
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button(f"Analyze", key=f"analyze_{idx}"):
                # Switch to AI assistant page
                st.info("Redirecting to AI Application Assistant...")
                st.switch_page("pages/8_AI_Application_Assistant.py")
        
        with col_btn2:
            if st.button(f"Track", key=f"track_{idx}"):
                # Add to application tracker
                dm = st.session_state.data_manager
                result = dm.add_application(scholarship['id'], scholarship['title'])
                if result:
                    st.success("Added to tracker!")
                else:
                    st.error("Failed to add")

def display_scholarship_details(scholarship, ai_enhancer, idx):
    """Display basic scholarship information (fallback)"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**Description:** {scholarship['description'][:300]}...")
        st.write(f"**Category:** {scholarship['category']}")
        st.write(f"**Target Demographics:** {', '.join(scholarship['target_demographics'])}")
        st.write(f"**Eligibility:** {scholarship['eligibility_criteria'][:200]}...")
        
        if scholarship.get('website'):
            st.markdown(f"**Website:** [{scholarship['website']}]({scholarship['website']})")
    
    with col2:
        st.metric("Award Amount", f"${scholarship['amount']:,}")
        st.metric("GPA Requirement", f"{scholarship['gpa_requirement']}")
        st.write(f"**Deadline:** {scholarship['deadline']}")
        
        if st.button(f"Apply Now", key=f"apply_{idx}"):
            st.success("Application process initiated!")

if __name__ == "__main__":
    main()
