import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.clustering import ScholarshipClustering
import numpy as np

st.set_page_config(
    page_title="Scholarship Clusters - ScholarSphere",
    page_icon="🗂️",
    layout="wide"
)

def main():
    st.title("Scholarship Clusters")
    
    if 'data_manager' not in st.session_state:
        st.error("Please visit the main page first.")
        return
    
    dm = st.session_state.data_manager
    scholarships_df = dm.get_scholarships_df()
    
    # Initialize clustering
    clustering = ScholarshipClustering()
    
    # Sidebar for clustering options
    st.sidebar.header("Clustering Options")
    
    # User profile integration
    user_profile = st.session_state.get('user_profile', {})
    
    view_mode = st.sidebar.selectbox(
        "View Mode:",
        ["All Scholarships", "Matching My Profile", "High Award Amount", "Low Competition"]
    )
    
    # Award amount filter
    amount_filter = st.sidebar.selectbox(
        "Award Amount Focus:",
        ["All Amounts", "Under $5,000", "$5,000 - $25,000", "Over $25,000"]
    )
    
    # Competition level
    competition_level = st.sidebar.selectbox(
        "Competition Level:",
        ["All Levels", "Low Competition", "Medium Competition", "High Competition"]
    )
    
    # Number of groups
    n_clusters = st.sidebar.slider(
        "Number of Groups:",
        min_value=3,
        max_value=8,
        value=5
    )
    
    features_to_use = st.sidebar.multiselect(
        "Group By:",
        ["Amount", "Category", "Demographics", "GPA Requirement"],
        default=["Amount", "Category", "Demographics"]
    )
    
    if not features_to_use:
        st.warning("Please select at least one grouping feature.")
        return
    
    # Filter scholarships based on user preferences
    filtered_df = scholarships_df.copy()
    
    # Apply view mode filter
    if view_mode == "Matching My Profile" and user_profile.get('demographics'):
        filtered_df = filtered_df[
            filtered_df['target_demographics'].apply(
                lambda x: any(demo in x for demo in user_profile['demographics'])
            )
        ]
    elif view_mode == "High Award Amount":
        filtered_df = filtered_df[filtered_df['amount'] >= 25000]
    elif view_mode == "Low Competition":
        filtered_df = filtered_df[filtered_df['estimated_applicants'] <= 1000]
    
    # Apply amount filter
    if amount_filter == "Under $5,000":
        filtered_df = filtered_df[filtered_df['amount'] < 5000]
    elif amount_filter == "$5,000 - $25,000":
        filtered_df = filtered_df[(filtered_df['amount'] >= 5000) & (filtered_df['amount'] <= 25000)]
    elif amount_filter == "Over $25,000":
        filtered_df = filtered_df[filtered_df['amount'] > 25000]
    
    # Apply competition filter
    if competition_level == "Low Competition":
        filtered_df = filtered_df[filtered_df['estimated_applicants'] <= 1000]
    elif competition_level == "Medium Competition":
        filtered_df = filtered_df[(filtered_df['estimated_applicants'] > 1000) & (filtered_df['estimated_applicants'] <= 5000)]
    elif competition_level == "High Competition":
        filtered_df = filtered_df[filtered_df['estimated_applicants'] > 5000]
    
    if filtered_df.empty:
        st.warning("No scholarships match your current filters. Try adjusting your criteria.")
        return
    
    # Perform clustering
    with st.spinner("Analyzing scholarship groups..."):
        try:
            clustered_df, cluster_info = clustering.cluster_scholarships(
                filtered_df, 
                method='kmeans',
                n_clusters=n_clusters,
                features=features_to_use
            )
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            return
    
    if clustered_df is None:
        st.error("Clustering could not be performed with the current settings.")
        return
    
    # Display cluster summary
    st.header("📊 Cluster Analysis Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Clusters", clustered_df['cluster'].nunique())
    with col2:
        largest_cluster_size = clustered_df['cluster'].value_counts().max()
        st.metric("Largest Cluster", largest_cluster_size)
    with col3:
        smallest_cluster_size = clustered_df['cluster'].value_counts().min()
        st.metric("Smallest Cluster", smallest_cluster_size)
    
    # Main visualization
    st.header("🎯 Interactive Cluster Visualization")
    
    # Create visualization based on selected features
    if len(features_to_use) >= 2:
        fig = create_cluster_visualization(clustered_df, features_to_use)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select at least 2 features for 2D visualization.")
    
    # Cluster details
    st.header("🔍 Cluster Details")
    
    # Cluster selection
    cluster_ids = sorted(clustered_df['cluster'].unique())
    selected_cluster = st.selectbox(
        "Select a cluster to explore:",
        cluster_ids,
        format_func=lambda x: f"Cluster {x} ({len(clustered_df[clustered_df['cluster'] == x])} scholarships)"
    )
    
    # Display selected cluster information
    cluster_scholarships = clustered_df[clustered_df['cluster'] == selected_cluster]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Cluster {selected_cluster} - Scholarships")
        
        # Display scholarships in the cluster
        for idx, (_, scholarship) in enumerate(cluster_scholarships.iterrows()):
            with st.expander(f"🎯 {scholarship['title']} - ${scholarship['amount']:,}"):
                col_a, col_b = st.columns([3, 1])
                
                with col_a:
                    st.write(f"**Category:** {scholarship['category']}")
                    st.write(f"**Target Demographics:** {', '.join(scholarship['target_demographics'])}")
                    st.write(f"**Description:** {scholarship['description'][:200]}...")
                    st.write(f"**Deadline:** {scholarship['deadline']}")
                
                with col_b:
                    st.metric("Amount", f"${scholarship['amount']:,}")
                    st.metric("GPA Req.", f"{scholarship['gpa_requirement']}")
    
    with col2:
        st.subheader(f"Cluster {selected_cluster} - Analytics")
        
        # Cluster statistics
        cluster_stats = calculate_cluster_statistics(cluster_scholarships)
        
        st.metric("Scholarships", len(cluster_scholarships))
        st.metric("Avg Amount", f"${cluster_stats['avg_amount']:,.0f}")
        st.metric("Total Value", f"${cluster_stats['total_value']:,.0f}")
        st.metric("Avg GPA Req.", f"{cluster_stats['avg_gpa']:.2f}")
        
        # Most common category
        most_common_category = cluster_scholarships['category'].mode().iloc[0] if not cluster_scholarships.empty else "N/A"
        st.write(f"**Most Common Category:** {most_common_category}")
        
        # Most common demographics
        all_demographics = []
        for demo_list in cluster_scholarships['target_demographics']:
            all_demographics.extend(demo_list)
        
        if all_demographics:
            from collections import Counter
            demo_counts = Counter(all_demographics)
            most_common_demo = demo_counts.most_common(1)[0][0]
            st.write(f"**Most Common Demographic:** {most_common_demo}")
    
    # Cluster comparison
    st.header("📈 Cluster Comparison")
    
    # Create comparison charts
    comparison_data = []
    for cluster_id in cluster_ids:
        cluster_data = clustered_df[clustered_df['cluster'] == cluster_id]
        stats = calculate_cluster_statistics(cluster_data)
        comparison_data.append({
            'Cluster': f"Cluster {cluster_id}",
            'Count': len(cluster_data),
            'Avg Amount': stats['avg_amount'],
            'Avg GPA': stats['avg_gpa']
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_amounts = px.bar(
            comparison_df,
            x='Cluster',
            y='Avg Amount',
            title="Average Award Amount by Cluster",
            labels={'Avg Amount': 'Average Amount ($)'}
        )
        st.plotly_chart(fig_amounts, use_container_width=True)
    
    with col2:
        fig_counts = px.bar(
            comparison_df,
            x='Cluster',
            y='Count',
            title="Number of Scholarships by Cluster",
            labels={'Count': 'Number of Scholarships'}
        )
        st.plotly_chart(fig_counts, use_container_width=True)
    
    # Recommendations based on clustering
    st.header("💡 Clustering Insights & Recommendations")
    
    user_profile = st.session_state.user_profile
    if user_profile.get('demographics') or user_profile.get('field_of_study'):
        recommended_clusters = recommend_clusters_for_user(clustered_df, user_profile)
        
        if recommended_clusters:
            st.success("Based on your profile, consider exploring these clusters:")
            for cluster_id, reason in recommended_clusters:
                cluster_size = len(clustered_df[clustered_df['cluster'] == cluster_id])
                st.write(f"• **Cluster {cluster_id}** ({cluster_size} scholarships) - {reason}")
        else:
            st.info("Set up your profile to get personalized cluster recommendations!")
    else:
        st.info("Complete your profile to get personalized cluster recommendations!")
    
    # General insights
    st.subheader("🔍 General Insights")
    insights = generate_clustering_insights(clustered_df, cluster_info)
    for insight in insights:
        st.write(f"• {insight}")

def create_cluster_visualization(clustered_df, features):
    """Create interactive cluster visualization"""
    # Use the first two numerical features for 2D plot
    numerical_features = []
    
    if "Amount" in features:
        numerical_features.append('amount')
    if "GPA Requirement" in features:
        numerical_features.append('gpa_requirement')
    
    # If we don't have enough numerical features, create some
    if len(numerical_features) < 2:
        # Add encoded categorical features
        if "Category" in features:
            clustered_df['category_encoded'] = pd.Categorical(clustered_df['category']).codes
            numerical_features.append('category_encoded')
        
        if "Demographics" in features and len(numerical_features) < 2:
            # Create a demographics diversity score
            clustered_df['demo_diversity'] = clustered_df['target_demographics'].apply(len)
            numerical_features.append('demo_diversity')
    
    if len(numerical_features) >= 2:
        x_feature = numerical_features[0]
        y_feature = numerical_features[1]
        
        fig = px.scatter(
            clustered_df,
            x=x_feature,
            y=y_feature,
            color='cluster',
            hover_data=['title', 'amount', 'category'],
            title=f"Scholarship Clusters: {x_feature.replace('_', ' ').title()} vs {y_feature.replace('_', ' ').title()}",
            labels={
                x_feature: x_feature.replace('_', ' ').title(),
                y_feature: y_feature.replace('_', ' ').title(),
                'cluster': 'Cluster'
            }
        )
        
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(height=600)
        
        return fig
    else:
        # Fallback: create a simple scatter plot with amount vs gpa
        fig = px.scatter(
            clustered_df,
            x='amount',
            y='gpa_requirement',
            color='cluster',
            hover_data=['title', 'category'],
            title="Scholarship Clusters: Amount vs GPA Requirement"
        )
        return fig

def calculate_cluster_statistics(cluster_df):
    """Calculate statistics for a cluster"""
    return {
        'avg_amount': cluster_df['amount'].mean(),
        'total_value': cluster_df['amount'].sum(),
        'avg_gpa': cluster_df['gpa_requirement'].mean(),
        'count': len(cluster_df)
    }

def recommend_clusters_for_user(clustered_df, user_profile):
    """Recommend clusters based on user profile"""
    recommendations = []
    
    for cluster_id in clustered_df['cluster'].unique():
        cluster_data = clustered_df[clustered_df['cluster'] == cluster_id]
        
        # Check demographic alignment
        if user_profile.get('demographics'):
            matching_scholarships = 0
            for _, scholarship in cluster_data.iterrows():
                if any(demo in scholarship.get('target_demographics', []) for demo in user_profile.get('demographics', [])):
                    matching_scholarships += 1
            
            if matching_scholarships > len(cluster_data) * 0.3:  # 30% match threshold
                recommendations.append((cluster_id, f"High demographic alignment ({matching_scholarships}/{len(cluster_data)} scholarships match)"))
        
        # Check field of study alignment
        if user_profile.get('field_of_study'):
            field_matches = cluster_data['category'].str.contains(
                user_profile.get('field_of_study', ''), case=False, na=False
            ).sum()
            
            if field_matches > len(cluster_data) * 0.5:  # 50% match threshold
                recommendations.append((cluster_id, f"Strong field alignment ({field_matches}/{len(cluster_data)} scholarships in your field)"))
    
    return recommendations[:3]  # Return top 3 recommendations

def generate_clustering_insights(clustered_df, cluster_info):
    """Generate insights about the clustering results"""
    insights = []
    
    # Cluster size analysis
    cluster_sizes = clustered_df['cluster'].value_counts()
    insights.append(f"The most popular cluster contains {cluster_sizes.max()} scholarships, while the smallest has {cluster_sizes.min()}")
    
    # Amount analysis by cluster
    cluster_amounts = clustered_df.groupby('cluster')['amount'].mean()
    highest_amount_cluster = cluster_amounts.idxmax()
    insights.append(f"Cluster {highest_amount_cluster} has the highest average award amount (${cluster_amounts.max():,.0f})")
    
    # Category diversity
    total_categories = clustered_df['category'].nunique()
    insights.append(f"Scholarships span {total_categories} different categories, showing diverse opportunities")
    
    # GPA requirements
    avg_gpa = clustered_df['gpa_requirement'].mean()
    insights.append(f"Average GPA requirement across all scholarships is {avg_gpa:.2f}")
    
    return insights

if __name__ == "__main__":
    main()
