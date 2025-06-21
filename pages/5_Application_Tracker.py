import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.application_tracker import ApplicationTracker

st.set_page_config(
    page_title="Application Tracker - ScholarSphere",
    page_icon="📋",
    layout="wide"
)

def main():
    st.title("📋 Application Tracker")
    st.markdown("Track your scholarship applications, monitor deadlines, and manage your progress.")
    
    # Initialize application tracker
    if 'app_tracker' not in st.session_state:
        st.session_state.app_tracker = ApplicationTracker()
    
    if 'data_manager' not in st.session_state:
        st.error("Please visit the main page first to initialize the application.")
        return
    
    tracker = st.session_state.app_tracker
    dm = st.session_state.data_manager
    
    # Get dashboard statistics
    stats = tracker.get_dashboard_stats()
    
    # Dashboard overview
    st.header("📊 Application Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Applications", stats['total_applications'])
    
    with col2:
        st.metric("Submitted", stats['submitted'])
    
    with col3:
        completion_pct = f"{stats['avg_completion']:.0f}%"
        st.metric("Avg Completion", completion_pct)
    
    with col4:
        st.metric("Urgent Deadlines", stats['urgent_deadlines'])
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Active Applications", "➕ Add Application", "⏰ Deadlines", "📈 Analytics"])
    
    with tab1:
        st.subheader("Your Active Applications")
        
        if stats['total_applications'] == 0:
            st.info("No applications tracked yet. Use the 'Add Application' tab to start tracking your scholarship applications.")
        else:
            # Filter options
            col1, col2 = st.columns([2, 1])
            
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status:",
                    ["All"] + tracker.status_options
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort by:",
                    ["Last Updated", "Priority", "Completion %", "Deadline"]
                )
            
            # Get applications
            applications = tracker.applications
            
            if status_filter != "All":
                applications = [app for app in applications if app['status'] == status_filter]
            
            # Display applications
            for app in applications:
                with st.expander(f"🎯 {app['scholarship_title']} - {app['status']}", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Status:** {app['status']}")
                        st.write(f"**Priority:** {app['priority']}")
                        st.write(f"**Date Added:** {datetime.fromisoformat(app['date_added']).strftime('%m/%d/%Y')}")
                        
                        if app['deadline']:
                            deadline_date = datetime.fromisoformat(app['deadline'])
                            days_remaining = (deadline_date - datetime.now()).days
                            if days_remaining < 0:
                                st.error(f"**Deadline:** Overdue by {abs(days_remaining)} days")
                            elif days_remaining <= 7:
                                st.warning(f"**Deadline:** {days_remaining} days remaining")
                            else:
                                st.write(f"**Deadline:** {days_remaining} days remaining")
                        
                        # Progress bar
                        progress = app['completion_percentage'] / 100
                        st.progress(progress, text=f"Completion: {app['completion_percentage']}%")
                        
                        # Documents section
                        st.write("**Required Documents:**")
                        for doc in app['required_documents']:
                            submitted = any(d['name'] == doc for d in app['submitted_documents'])
                            icon = "✅" if submitted else "⏳"
                            st.write(f"{icon} {doc}")
                        
                        # Notes
                        if app['notes']:
                            st.write(f"**Notes:** {app['notes']}")
                    
                    with col2:
                        # Action buttons
                        new_status = st.selectbox(
                            "Update Status:",
                            tracker.status_options,
                            index=tracker.status_options.index(app['status']),
                            key=f"status_{app['id']}"
                        )
                        
                        notes = st.text_area(
                            "Notes:",
                            value=app['notes'],
                            key=f"notes_{app['id']}"
                        )
                        
                        if st.button("Update", key=f"update_{app['id']}"):
                            tracker.update_application_status(app['id'], new_status, notes or "")
                            st.success("Application updated!")
                            st.rerun()
                        
                        # Add document
                        st.write("**Add Document:**")
                        doc_name = st.text_input("Document Name:", key=f"doc_{app['id']}")
                        if st.button("Add Document", key=f"add_doc_{app['id']}") and doc_name:
                            tracker.add_document(app['id'], doc_name)
                            st.success(f"Added {doc_name}")
                            st.rerun()
    
    with tab2:
        st.subheader("Add New Application")
        
        # Get available scholarships
        scholarships_df = dm.get_scholarships_df()
        
        if scholarships_df.empty:
            st.error("No scholarships available. Please check the main page.")
            return
        
        scholarship_options = [f"{row['title']} - ${row['amount']:,}" for _, row in scholarships_df.iterrows()]
        
        selected_scholarship = st.selectbox(
            "Select Scholarship:",
            scholarship_options
        )
        
        if selected_scholarship:
            # Extract scholarship details
            scholarship_title = selected_scholarship.split(" - $")[0]
            scholarship_row = scholarships_df[scholarships_df['title'] == scholarship_title].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Amount:** ${scholarship_row['amount']:,}")
                st.write(f"**Category:** {scholarship_row['category']}")
                st.write(f"**Deadline:** {scholarship_row['deadline']}")
                st.write(f"**GPA Requirement:** {scholarship_row['gpa_requirement']}")
            
            with col2:
                st.write(f"**Target Demographics:** {', '.join(scholarship_row['target_demographics'])}")
                st.write(f"**Description:** {scholarship_row['description'][:150]}...")
            
            # Add application button
            if st.button("Add to Applications", type="primary"):
                user_profile = st.session_state.user_profile
                new_app = tracker.add_application(
                    scholarship_id=str(scholarship_row.name),
                    scholarship_title=scholarship_title,
                    user_profile=user_profile
                )
                
                # Set deadline if available
                if scholarship_row['deadline']:
                    try:
                        deadline_date = datetime.strptime(scholarship_row['deadline'], '%m/%d/%Y')
                        new_app['deadline'] = deadline_date.isoformat()
                    except ValueError:
                        pass
                
                st.success(f"Added {scholarship_title} to your applications!")
                st.balloons()
                st.rerun()
    
    with tab3:
        st.subheader("Upcoming Deadlines")
        
        # Get upcoming deadlines
        upcoming = tracker.get_upcoming_deadlines(60)  # Next 60 days
        
        if not upcoming:
            st.info("No upcoming deadlines in the next 60 days.")
        else:
            # Create urgency-based sections
            urgent = [app for app in upcoming if app['days_remaining'] <= 7]
            soon = [app for app in upcoming if 7 < app['days_remaining'] <= 30]
            later = [app for app in upcoming if app['days_remaining'] > 30]
            
            if urgent:
                st.error("🚨 URGENT - Due within 7 days")
                for app in urgent:
                    st.write(f"• **{app['scholarship_title']}** - {app['days_remaining']} days remaining")
            
            if soon:
                st.warning("⚠️ DUE SOON - Due within 30 days")
                for app in soon:
                    st.write(f"• **{app['scholarship_title']}** - {app['days_remaining']} days remaining")
            
            if later:
                st.info("📅 UPCOMING - Due within 60 days")
                for app in later:
                    st.write(f"• **{app['scholarship_title']}** - {app['days_remaining']} days remaining")
            
            # Calendar view
            st.subheader("Deadline Calendar")
            
            if upcoming:
                calendar_data = []
                for app in upcoming:
                    try:
                        deadline_date = datetime.fromisoformat(app['deadline'])
                        calendar_data.append({
                            'Date': deadline_date.strftime('%Y-%m-%d'),
                            'Scholarship': app['scholarship_title'],
                            'Days Remaining': app['days_remaining'],
                            'Status': app['status']
                        })
                    except:
                        continue
                
                if calendar_data:
                    calendar_df = pd.DataFrame(calendar_data)
                    st.dataframe(calendar_df, use_container_width=True)
    
    with tab4:
        st.subheader("Application Analytics")
        
        if stats['total_applications'] == 0:
            st.info("No applications to analyze yet.")
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                # Status distribution
                status_data = [(status, count) for status, count in stats['status_breakdown'].items() if count > 0]
                
                if status_data:
                    statuses, counts = zip(*status_data)
                    fig_status = px.pie(
                        values=counts,
                        names=statuses,
                        title="Application Status Distribution"
                    )
                    st.plotly_chart(fig_status, use_container_width=True)
                
                # Completion rates
                completion_data = [app['completion_percentage'] for app in tracker.applications]
                if completion_data:
                    fig_completion = px.histogram(
                        x=completion_data,
                        nbins=10,
                        title="Application Completion Distribution",
                        labels={'x': 'Completion Percentage', 'y': 'Number of Applications'}
                    )
                    st.plotly_chart(fig_completion, use_container_width=True)
            
            with col2:
                # Timeline view
                if tracker.applications:
                    timeline_data = []
                    for app in tracker.applications:
                        date_added = datetime.fromisoformat(app['date_added'])
                        timeline_data.append({
                            'Date': date_added.strftime('%Y-%m-%d'),
                            'Applications': 1
                        })
                    
                    timeline_df = pd.DataFrame(timeline_data)
                    timeline_grouped = timeline_df.groupby('Date').sum().reset_index()
                    
                    fig_timeline = px.line(
                        timeline_grouped,
                        x='Date',
                        y='Applications',
                        title="Applications Added Over Time"
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
                
                # Success metrics
                st.metric("Acceptance Rate", f"{stats['acceptance_rate']:.1f}%")
                
                submitted_apps = stats['submitted']
                if submitted_apps > 0:
                    st.metric("Applications Submitted", submitted_apps)
                    avg_time_to_submit = "7.5 days"  # Would calculate from actual data
                    st.metric("Avg Time to Submit", avg_time_to_submit)

if __name__ == "__main__":
    main()