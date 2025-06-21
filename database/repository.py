from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from database.models import Scholarship, UserProfile, Application, SavedScholarship, SearchHistory, get_session
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime

class ScholarshipRepository:
    """Repository for scholarship database operations"""
    
    def __init__(self):
        self.session = get_session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    def create_scholarship(self, scholarship_data: Dict[str, Any]) -> Scholarship:
        """Create a new scholarship in the database"""
        scholarship = Scholarship(**scholarship_data)
        self.session.add(scholarship)
        self.session.commit()
        self.session.refresh(scholarship)
        return scholarship
    
    def bulk_create_scholarships(self, scholarships_data: List[Dict[str, Any]]) -> List[Scholarship]:
        """Bulk create scholarships for efficient data loading"""
        scholarships = [Scholarship(**data) for data in scholarships_data]
        self.session.add_all(scholarships)
        self.session.commit()
        return scholarships
    
    def get_scholarship_by_id(self, scholarship_id: int) -> Optional[Scholarship]:
        """Get scholarship by ID"""
        return self.session.query(Scholarship).filter(Scholarship.id == scholarship_id).first()
    
    def get_all_scholarships(self) -> List[Scholarship]:
        """Get all scholarships"""
        return self.session.query(Scholarship).all()
    
    def search_scholarships(self, 
                          query: Optional[str] = None,
                          categories: Optional[List[str]] = None,
                          demographics: Optional[List[str]] = None,
                          min_amount: Optional[float] = None,
                          max_amount: Optional[float] = None,
                          max_gpa: Optional[float] = None,
                          sources: Optional[List[str]] = None,
                          limit: int = 100,
                          offset: int = 0) -> List[Scholarship]:
        """Advanced scholarship search with filters"""
        
        query_obj = self.session.query(Scholarship)
        
        # Text search
        if query:
            query_obj = query_obj.filter(
                or_(
                    Scholarship.title.ilike(f'%{query}%'),
                    Scholarship.description.ilike(f'%{query}%'),
                    Scholarship.category.ilike(f'%{query}%'),
                    Scholarship.eligibility_criteria.ilike(f'%{query}%')
                )
            )
        
        # Category filter
        if categories:
            query_obj = query_obj.filter(Scholarship.category.in_(categories))
        
        # Demographics filter
        if demographics:
            for demo in demographics:
                query_obj = query_obj.filter(
                    Scholarship.target_demographics.op('?')(demo)
                )
        
        # Amount range
        if min_amount is not None:
            query_obj = query_obj.filter(Scholarship.amount >= min_amount)
        if max_amount is not None:
            query_obj = query_obj.filter(Scholarship.amount <= max_amount)
        
        # GPA requirement
        if max_gpa is not None:
            query_obj = query_obj.filter(Scholarship.gpa_requirement <= max_gpa)
        
        # Source filter
        if sources:
            query_obj = query_obj.filter(Scholarship.source.in_(sources))
        
        return query_obj.offset(offset).limit(limit).all()
    
    def get_scholarships_by_category(self, category: str) -> List[Scholarship]:
        """Get scholarships by category"""
        return self.session.query(Scholarship).filter(Scholarship.category == category).all()
    
    def get_scholarships_by_demographics(self, demographics: List[str]) -> List[Scholarship]:
        """Get scholarships targeting specific demographics"""
        query_obj = self.session.query(Scholarship)
        for demo in demographics:
            query_obj = query_obj.filter(
                Scholarship.target_demographics.op('?')(demo)
            )
        return query_obj.all()
    
    def get_scholarship_statistics(self) -> Dict[str, Any]:
        """Get comprehensive scholarship statistics"""
        total_count = self.session.query(Scholarship).count()
        total_value = self.session.query(func.sum(Scholarship.amount)).scalar() or 0
        avg_amount = self.session.query(func.avg(Scholarship.amount)).scalar() or 0
        min_amount = self.session.query(func.min(Scholarship.amount)).scalar() or 0
        max_amount = self.session.query(func.max(Scholarship.amount)).scalar() or 0
        
        # Category distribution
        category_stats = self.session.query(
            Scholarship.category, 
            func.count(Scholarship.id)
        ).group_by(Scholarship.category).all()
        
        # Source distribution
        source_stats = self.session.query(
            Scholarship.source, 
            func.count(Scholarship.id)
        ).group_by(Scholarship.source).all()
        
        return {
            'total_scholarships': total_count,
            'total_value': total_value,
            'average_amount': avg_amount,
            'min_amount': min_amount,
            'max_amount': max_amount,
            'category_distribution': dict(category_stats),
            'source_distribution': dict(source_stats)
        }
    
    def update_scholarship(self, scholarship_id: int, update_data: Dict[str, Any]) -> Optional[Scholarship]:
        """Update scholarship information"""
        scholarship = self.get_scholarship_by_id(scholarship_id)
        if scholarship:
            for key, value in update_data.items():
                setattr(scholarship, key, value)
            scholarship.last_updated = datetime.utcnow()
            self.session.commit()
            self.session.refresh(scholarship)
        return scholarship

class UserRepository:
    """Repository for user profile operations"""
    
    def __init__(self):
        self.session = get_session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    def create_or_update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> UserProfile:
        """Create or update user profile"""
        profile = self.session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if profile:
            # Update existing profile
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.updated_at = datetime.utcnow()
        else:
            # Create new profile
            profile_data['user_id'] = user_id
            profile = UserProfile(**profile_data)
            self.session.add(profile)
        
        self.session.commit()
        self.session.refresh(profile)
        return profile
    
    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        return self.session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        profile = self.get_profile(user_id)
        if profile:
            self.session.delete(profile)
            self.session.commit()
            return True
        return False

class ApplicationRepository:
    """Repository for application tracking operations"""
    
    def __init__(self):
        self.session = get_session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    def create_application(self, application_data: Dict[str, Any]) -> Application:
        """Create new application"""
        application = Application(**application_data)
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        return application
    
    def get_user_applications(self, user_id: str) -> List[Application]:
        """Get all applications for a user"""
        return self.session.query(Application).filter(Application.user_id == user_id).all()
    
    def get_application_by_id(self, app_id: int) -> Optional[Application]:
        """Get application by ID"""
        return self.session.query(Application).filter(Application.id == app_id).first()
    
    def update_application(self, app_id: int, update_data: Dict[str, Any]) -> Optional[Application]:
        """Update application"""
        application = self.get_application_by_id(app_id)
        if application:
            for key, value in update_data.items():
                setattr(application, key, value)
            application.last_updated = datetime.utcnow()
            self.session.commit()
            self.session.refresh(application)
        return application
    
    def get_applications_by_status(self, user_id: str, status: str) -> List[Application]:
        """Get applications by status"""
        return self.session.query(Application).filter(
            and_(Application.user_id == user_id, Application.status == status)
        ).all()
    
    def get_upcoming_deadlines(self, user_id: str, days_ahead: int = 30) -> List[Application]:
        """Get applications with upcoming deadlines"""
        cutoff_date = datetime.utcnow().date()
        return self.session.query(Application).filter(
            and_(
                Application.user_id == user_id,
                Application.deadline >= cutoff_date,
                Application.status.notin_(['Submitted', 'Accepted', 'Rejected'])
            )
        ).order_by(Application.deadline).all()
    
    def get_application_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get application statistics for user"""
        total_apps = self.session.query(Application).filter(Application.user_id == user_id).count()
        
        status_counts = self.session.query(
            Application.status,
            func.count(Application.id)
        ).filter(Application.user_id == user_id).group_by(Application.status).all()
        
        avg_completion = self.session.query(
            func.avg(Application.completion_percentage)
        ).filter(Application.user_id == user_id).scalar() or 0
        
        return {
            'total_applications': total_apps,
            'status_breakdown': dict(status_counts),
            'average_completion': avg_completion
        }
    
    def delete_application(self, app_id: int) -> bool:
        """Delete application"""
        application = self.get_application_by_id(app_id)
        if application:
            self.session.delete(application)
            self.session.commit()
            return True
        return False

class SavedScholarshipRepository:
    """Repository for saved scholarship operations"""
    
    def __init__(self):
        self.session = get_session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    def save_scholarship(self, user_id: str, scholarship_id: int, notes: str = "") -> SavedScholarship:
        """Save scholarship for user"""
        # Check if already saved
        existing = self.session.query(SavedScholarship).filter(
            and_(SavedScholarship.user_id == user_id, SavedScholarship.scholarship_id == scholarship_id)
        ).first()
        
        if existing:
            return existing
        
        saved = SavedScholarship(
            user_id=user_id,
            scholarship_id=scholarship_id,
            notes=notes
        )
        self.session.add(saved)
        self.session.commit()
        self.session.refresh(saved)
        return saved
    
    def get_saved_scholarships(self, user_id: str) -> List[SavedScholarship]:
        """Get all saved scholarships for user"""
        return self.session.query(SavedScholarship).filter(SavedScholarship.user_id == user_id).all()
    
    def unsave_scholarship(self, user_id: str, scholarship_id: int) -> bool:
        """Remove scholarship from saved list"""
        saved = self.session.query(SavedScholarship).filter(
            and_(SavedScholarship.user_id == user_id, SavedScholarship.scholarship_id == scholarship_id)
        ).first()
        
        if saved:
            self.session.delete(saved)
            self.session.commit()
            return True
        return False

class SearchHistoryRepository:
    """Repository for search history operations"""
    
    def __init__(self):
        self.session = get_session()
    
    def close(self):
        """Close database session"""
        self.session.close()
    
    def record_search(self, user_id: str, query: str, filters: Dict[str, Any], results_count: int) -> SearchHistory:
        """Record a search in history"""
        search = SearchHistory(
            user_id=user_id,
            search_query=query,
            filters_applied=filters,
            results_count=results_count
        )
        self.session.add(search)
        self.session.commit()
        self.session.refresh(search)
        return search
    
    def get_search_history(self, user_id: str, limit: int = 50) -> List[SearchHistory]:
        """Get search history for user"""
        return self.session.query(SearchHistory).filter(
            SearchHistory.user_id == user_id
        ).order_by(SearchHistory.searched_at.desc()).limit(limit).all()
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular search terms"""
        popular = self.session.query(
            SearchHistory.search_query,
            func.count(SearchHistory.id).label('search_count')
        ).group_by(SearchHistory.search_query).order_by(
            func.count(SearchHistory.id).desc()
        ).limit(limit).all()
        
        return [{'query': query, 'count': count} for query, count in popular]