import pandas as pd
from typing import List, Dict, Any, Optional
import streamlit as st
from database.models import create_tables, get_session
from database.repository import ScholarshipRepository, UserRepository, ApplicationRepository
from utils.data_integration import RealScholarshipIntegrator
import uuid

class DatabaseManager:
    """Enhanced data manager with PostgreSQL backend"""
    
    def __init__(self):
        self.scholarship_repo = ScholarshipRepository()
        self.user_repo = UserRepository()
        self.app_repo = ApplicationRepository()
        self._ensure_tables_exist()
        self._user_id = self._get_or_create_user_id()
    
    def _ensure_tables_exist(self):
        """Ensure database tables are created"""
        try:
            create_tables()
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
    
    def _get_or_create_user_id(self) -> str:
        """Get or create a unique user ID for session"""
        if 'user_id' not in st.session_state:
            st.session_state.user_id = str(uuid.uuid4())
        return st.session_state.user_id
    
    def load_scholarships(self, force_reload: bool = False):
        """Load scholarships from database or refresh from sources"""
        try:
            # Check if we have scholarships in database
            existing_count = len(self.scholarship_repo.get_all_scholarships())
            
            if existing_count == 0 or force_reload:
                # Load from authentic sources
                integrator = RealScholarshipIntegrator()
                real_scholarships = integrator.aggregate_all_real_scholarships()
                enriched_scholarships = integrator.enrich_with_additional_data(real_scholarships)
                
                # Clear existing if force reload
                if force_reload and existing_count > 0:
                    self._clear_scholarships()
                
                # Bulk insert into database
                self.scholarship_repo.bulk_create_scholarships(enriched_scholarships)
                st.success(f"Loaded {len(enriched_scholarships)} scholarships from verified sources")
                
        except Exception as e:
            st.error(f"Error loading scholarships: {str(e)}")
    
    def _clear_scholarships(self):
        """Clear existing scholarships (for reload)"""
        try:
            from database.models import Scholarship, get_session
            session = get_session()
            session.query(Scholarship).delete()
            session.commit()
            session.close()
        except Exception as e:
            st.error(f"Error clearing scholarships: {str(e)}")
    
    def get_scholarships_df(self) -> pd.DataFrame:
        """Get scholarships as DataFrame"""
        try:
            scholarships = self.scholarship_repo.get_all_scholarships()
            
            if not scholarships:
                return pd.DataFrame()
            
            # Convert to DataFrame
            data = []
            for scholarship in scholarships:
                data.append({
                    'id': scholarship.id,
                    'title': scholarship.title,
                    'amount': scholarship.amount,
                    'category': scholarship.category,
                    'target_demographics': scholarship.target_demographics,
                    'description': scholarship.description,
                    'eligibility_criteria': scholarship.eligibility_criteria,
                    'application_requirements': scholarship.application_requirements,
                    'deadline': scholarship.deadline,
                    'gpa_requirement': scholarship.gpa_requirement,
                    'website': scholarship.website,
                    'contact_info': scholarship.contact_info,
                    'source': scholarship.source,
                    'verification_status': scholarship.verification_status,
                    'application_difficulty': scholarship.application_difficulty,
                    'estimated_applicants': scholarship.estimated_applicants,
                    'last_updated': scholarship.last_updated
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error retrieving scholarships: {str(e)}")
            return pd.DataFrame()
    
    def search_scholarships(self, 
                          query: str = "", 
                          filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Search scholarships with filters"""
        try:
            # Prepare search parameters
            search_params = {}
            
            if query:
                search_params['query'] = query
            
            if filters:
                if 'categories' in filters and filters['categories']:
                    search_params['categories'] = filters['categories']
                
                if 'demographics' in filters and filters['demographics']:
                    search_params['demographics'] = filters['demographics']
                
                if 'min_amount' in filters:
                    search_params['min_amount'] = filters['min_amount']
                
                if 'max_amount' in filters:
                    search_params['max_amount'] = filters['max_amount']
                
                if 'max_gpa_requirement' in filters:
                    search_params['max_gpa'] = filters['max_gpa_requirement']
            
            # Perform search
            scholarships = self.scholarship_repo.search_scholarships(**search_params)
            
            # Convert to DataFrame
            if not scholarships:
                return pd.DataFrame()
            
            data = []
            for scholarship in scholarships:
                data.append({
                    'id': scholarship.id,
                    'title': scholarship.title,
                    'amount': scholarship.amount,
                    'category': scholarship.category,
                    'target_demographics': scholarship.target_demographics,
                    'description': scholarship.description,
                    'eligibility_criteria': scholarship.eligibility_criteria,
                    'application_requirements': scholarship.application_requirements,
                    'deadline': scholarship.deadline,
                    'gpa_requirement': scholarship.gpa_requirement,
                    'website': scholarship.website,
                    'contact_info': scholarship.contact_info,
                    'source': scholarship.source
                })
            
            return pd.DataFrame(data)
            
        except Exception as e:
            st.error(f"Error searching scholarships: {str(e)}")
            return pd.DataFrame()
    
    def get_scholarship_by_id(self, scholarship_id: int) -> Optional[Dict[str, Any]]:
        """Get specific scholarship by ID"""
        try:
            scholarship = self.scholarship_repo.get_scholarship_by_id(scholarship_id)
            if scholarship:
                return {
                    'id': scholarship.id,
                    'title': scholarship.title,
                    'amount': scholarship.amount,
                    'category': scholarship.category,
                    'target_demographics': scholarship.target_demographics,
                    'description': scholarship.description,
                    'eligibility_criteria': scholarship.eligibility_criteria,
                    'application_requirements': scholarship.application_requirements,
                    'deadline': scholarship.deadline,
                    'gpa_requirement': scholarship.gpa_requirement,
                    'website': scholarship.website,
                    'contact_info': scholarship.contact_info,
                    'source': scholarship.source
                }
            return None
            
        except Exception as e:
            st.error(f"Error retrieving scholarship: {str(e)}")
            return None
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            df = self.get_scholarships_df()
            if df.empty:
                return []
            return sorted(df['category'].unique().tolist())
        except Exception as e:
            st.error(f"Error getting categories: {str(e)}")
            return []
    
    def get_demographics(self) -> List[str]:
        """Get all unique demographics"""
        try:
            df = self.get_scholarships_df()
            if df.empty:
                return []
            
            all_demographics = set()
            for demo_list in df['target_demographics']:
                if isinstance(demo_list, list):
                    all_demographics.update(demo_list)
            
            return sorted(list(all_demographics))
        except Exception as e:
            st.error(f"Error getting demographics: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get scholarship statistics"""
        try:
            return self.scholarship_repo.get_scholarship_statistics()
        except Exception as e:
            st.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def save_user_profile(self, profile_data: Dict[str, Any]):
        """Save user profile to database"""
        try:
            self.user_repo.create_or_update_profile(self._user_id, profile_data)
        except Exception as e:
            st.error(f"Error saving profile: {str(e)}")
    
    def get_user_profile(self) -> Dict[str, Any]:
        """Get user profile from database"""
        try:
            profile = self.user_repo.get_profile(self._user_id)
            if profile:
                return {
                    'demographics': profile.demographics or [],
                    'field_of_study': profile.field_of_study or '',
                    'academic_level': profile.academic_level or '',
                    'gpa': profile.gpa or 0.0,
                    'financial_need': profile.financial_need or '',
                    'location': profile.location or '',
                    'interests': profile.interests or [],
                    'extracurriculars': profile.extracurriculars or [],
                    'career_goals': profile.career_goals or '',
                    'graduation_year': profile.graduation_year or 2024,
                    'essay_topics_interested': profile.essay_topics_interested or [],
                    'application_preferences': profile.application_preferences or []
                }
            return {
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
        except Exception as e:
            st.error(f"Error getting profile: {str(e)}")
            return {}
    
    def add_application(self, scholarship_id: int, scholarship_title: str) -> Dict[str, Any]:
        """Add application to tracking"""
        try:
            app_data = {
                'user_id': self._user_id,
                'scholarship_id': scholarship_id,
                'scholarship_title': scholarship_title,
                'status': 'Not Started',
                'priority': 'Medium',
                'completion_percentage': 0,
                'required_documents': ['Personal Statement', 'Transcripts', 'Letters of Recommendation'],
                'submitted_documents': [],
                'notes': '',
                'reminders': []
            }
            
            application = self.app_repo.create_application(app_data)
            
            return {
                'id': application.id,
                'scholarship_id': application.scholarship_id,
                'scholarship_title': application.scholarship_title,
                'status': application.status,
                'priority': application.priority,
                'completion_percentage': application.completion_percentage,
                'required_documents': application.required_documents,
                'submitted_documents': application.submitted_documents,
                'notes': application.notes,
                'date_added': application.date_added.isoformat(),
                'last_updated': application.last_updated.isoformat()
            }
            
        except Exception as e:
            st.error(f"Error adding application: {str(e)}")
            return {}
    
    def get_user_applications(self) -> List[Dict[str, Any]]:
        """Get all applications for current user"""
        try:
            applications = self.app_repo.get_user_applications(self._user_id)
            
            result = []
            for app in applications:
                result.append({
                    'id': app.id,
                    'scholarship_id': app.scholarship_id,
                    'scholarship_title': app.scholarship_title,
                    'status': app.status,
                    'priority': app.priority,
                    'completion_percentage': app.completion_percentage,
                    'required_documents': app.required_documents,
                    'submitted_documents': app.submitted_documents,
                    'notes': app.notes,
                    'deadline': app.deadline.isoformat() if app.deadline else None,
                    'date_added': app.date_added.isoformat(),
                    'last_updated': app.last_updated.isoformat()
                })
            
            return result
            
        except Exception as e:
            st.error(f"Error getting applications: {str(e)}")
            return []
    
    def update_application_status(self, app_id: int, new_status: str, notes: str = "") -> bool:
        """Update application status"""
        try:
            update_data = {
                'status': new_status,
                'notes': notes
            }
            
            # Update completion percentage based on status
            completion_map = {
                'Not Started': 0,
                'In Progress': 25,
                'Submitted': 100,
                'Under Review': 100,
                'Awaiting Decision': 100,
                'Accepted': 100,
                'Rejected': 100,
                'Waitlisted': 100
            }
            update_data['completion_percentage'] = completion_map.get(new_status, 0)
            
            application = self.app_repo.update_application(app_id, update_data)
            return application is not None
            
        except Exception as e:
            st.error(f"Error updating application: {str(e)}")
            return False
    
    def close_connections(self):
        """Close database connections"""
        try:
            self.scholarship_repo.close()
            self.user_repo.close()
            self.app_repo.close()
        except Exception as e:
            st.error(f"Error closing connections: {str(e)}")