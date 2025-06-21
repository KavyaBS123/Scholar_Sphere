import streamlit as st
import pandas as pd
import plotly.express as px
from utils.ai_enhancer import AIEnhancer

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
    
    # Initialize AI enhancer
    ai_enhancer = AIEnhancer()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Text search
    search_term = st.sidebar.text_input(
        "Search:",
        placeholder="Enter keywords..."
    )
    
    # Amount range
    min_amount, max_amount = st.sidebar.slider(
        "Award Amount",
        min_value=int(scholarships_df['amount'].min()),
        max_value=int(scholarships_df['amount'].max()),
        value=(int(scholarships_df['amount'].min()), int(scholarships_df['amount'].max())),
        step=1000,
        format="$%d"
    )
    
    # Category filter
    categories = sorted(scholarships_df['category'].unique())
    selected_categories = st.sidebar.multiselect(
        "Categories",
        categories,
        default=categories
    )
    
    # Demographics filter
    all_demographics = set()
    for demo_list in scholarships_df['target_demographics']:
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
    
    # Sorting options
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Found {len(filtered_df)} scholarships")
    with col2:
        sort_by = st.selectbox(
            "Sort by:",
            ["Amount (High to Low)", "Amount (Low to High)", "Deadline", "Alphabetical"]
        )
    
    # Apply sorting
    if sort_by == "Amount (High to Low)":
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
    
    # Display scholarships
    for idx, (_, scholarship) in enumerate(page_df.iterrows()):
        with st.expander(f"🎯 {scholarship['title']} - ${scholarship['amount']:,}", expanded=False):
            display_scholarship_details(scholarship, ai_enhancer, idx)
    
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

def display_scholarship_details(scholarship, ai_enhancer, idx):
    """Display detailed scholarship information"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # AI-enhanced description
        with st.spinner("Generating AI summary..."):
            try:
                summary = ai_enhancer.summarize_scholarship(scholarship.to_dict())
                st.markdown(f"**AI Summary:** {summary}")
            except Exception as e:
                st.write(f"**Description:** {scholarship['description']}")
                st.caption(f"AI summary unavailable: {str(e)}")
        
        st.write(f"**Category:** {scholarship['category']}")
        st.write(f"**Target Demographics:** {', '.join(scholarship['target_demographics'])}")
        st.write(f"**Eligibility Criteria:** {scholarship['eligibility_criteria']}")
        st.write(f"**Application Requirements:** {scholarship['application_requirements']}")
        
        if scholarship['website']:
            st.markdown(f"**Website:** [{scholarship['website']}]({scholarship['website']})")
    
    with col2:
        st.metric("Award Amount", f"${scholarship['amount']:,}")
        st.metric("GPA Requirement", f"{scholarship['gpa_requirement']}")
        st.write(f"**Deadline:** {scholarship['deadline']}")
        st.write(f"**Contact:** {scholarship['contact_info']}")
        
        # Action buttons
        if st.button(f"Save to Favorites", key=f"save_{idx}"):
            st.success("Added to favorites!")
        
        if st.button(f"Apply Now", key=f"apply_{idx}"):
            if scholarship['website']:
                st.success(f"Opening application: {scholarship['website']}")
            else:
                st.info("Contact information provided above for application.")
        
        # Match score if user profile exists
        if st.session_state.user_profile['demographics'] or st.session_state.user_profile['field_of_study']:
            from pages import Dashboard
            try:
                match_score = Dashboard.calculate_match_score(scholarship, st.session_state.user_profile)
                st.metric("Match Score", f"{match_score}%")
            except:
                pass

if __name__ == "__main__":
    main()
