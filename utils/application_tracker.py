import pandas as pd
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import streamlit as st

class ApplicationTracker:
    """Real-time application tracking system"""
    
    def __init__(self):
        self.applications = []
        self.status_options = [
            "Not Started", "In Progress", "Submitted", "Under Review", 
            "Awaiting Decision", "Accepted", "Rejected", "Waitlisted"
        ]
    
    def add_application(self, scholarship_id: str, scholarship_title: str, 
                       user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new scholarship application"""
        application = {
            'id': f"app_{len(self.applications) + 1}",
            'scholarship_id': scholarship_id,
            'scholarship_title': scholarship_title,
            'status': 'Not Started',
            'date_added': datetime.now().isoformat(),
            'deadline': None,
            'priority': self._calculate_priority(scholarship_title, user_profile),
            'completion_percentage': 0,
            'required_documents': self._get_required_documents(scholarship_title),
            'submitted_documents': [],
            'notes': '',
            'reminders': [],
            'last_updated': datetime.now().isoformat()
        }
        
        self.applications.append(application)
        return application
    
    def update_application_status(self, app_id: str, new_status: str, 
                                 notes: Optional[str] = "") -> bool:
        """Update application status"""
        for app in self.applications:
            if app['id'] == app_id:
                app['status'] = new_status
                app['last_updated'] = datetime.now().isoformat()
                if notes:
                    app['notes'] = notes
                
                # Update completion percentage based on status
                app['completion_percentage'] = self._calculate_completion(new_status)
                return True
        return False
    
    def add_document(self, app_id: str, document_name: str, 
                    document_type: str = "general") -> bool:
        """Add a submitted document to an application"""
        for app in self.applications:
            if app['id'] == app_id:
                document = {
                    'name': document_name,
                    'type': document_type,
                    'date_added': datetime.now().isoformat()
                }
                app['submitted_documents'].append(document)
                app['last_updated'] = datetime.now().isoformat()
                
                # Recalculate completion percentage
                app['completion_percentage'] = self._calculate_document_completion(app)
                return True
        return False
    
    def get_applications_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get applications filtered by status"""
        return [app for app in self.applications if app['status'] == status]
    
    def get_upcoming_deadlines(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get applications with upcoming deadlines"""
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        upcoming = []
        
        for app in self.applications:
            if app['deadline']:
                try:
                    deadline_date = datetime.fromisoformat(app['deadline'])
                    if deadline_date <= cutoff_date and app['status'] not in ['Submitted', 'Accepted', 'Rejected']:
                        days_remaining = (deadline_date - datetime.now()).days
                        app['days_remaining'] = max(0, days_remaining)
                        upcoming.append(app)
                except ValueError:
                    continue
        
        return sorted(upcoming, key=lambda x: x['days_remaining'])
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get statistics for dashboard"""
        total_apps = len(self.applications)
        if total_apps == 0:
            return {
                'total_applications': 0,
                'submitted': 0,
                'in_progress': 0,
                'acceptance_rate': 0,
                'avg_completion': 0,
                'urgent_deadlines': 0
            }
        
        status_counts = {}
        for status in self.status_options:
            status_counts[status] = len(self.get_applications_by_status(status))
        
        accepted = status_counts.get('Accepted', 0)
        submitted = status_counts.get('Submitted', 0)
        acceptance_rate = (accepted / max(submitted, 1)) * 100
        
        avg_completion = sum(app['completion_percentage'] for app in self.applications) / total_apps
        
        urgent_deadlines = len(self.get_upcoming_deadlines(7))  # Next 7 days
        
        return {
            'total_applications': total_apps,
            'submitted': submitted,
            'in_progress': status_counts.get('In Progress', 0),
            'acceptance_rate': acceptance_rate,
            'avg_completion': avg_completion,
            'urgent_deadlines': urgent_deadlines,
            'status_breakdown': status_counts
        }
    
    def _calculate_priority(self, scholarship_title: str, user_profile: Dict[str, Any]) -> str:
        """Calculate application priority based on match and deadlines"""
        # This would integrate with the match scoring system
        # For now, return a simple priority
        return "Medium"
    
    def _calculate_completion(self, status: str) -> int:
        """Calculate completion percentage based on status"""
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
        return completion_map.get(status, 0)
    
    def _calculate_document_completion(self, application: Dict[str, Any]) -> int:
        """Calculate completion based on submitted documents"""
        required_docs = len(application['required_documents'])
        submitted_docs = len(application['submitted_documents'])
        
        if required_docs == 0:
            return 50  # Base completion if no specific requirements
        
        doc_completion = (submitted_docs / required_docs) * 80  # 80% for documents
        status_bonus = 20 if application['status'] == 'Submitted' else 0
        
        return min(100, int(doc_completion + status_bonus))
    
    def _get_required_documents(self, scholarship_title: str) -> List[str]:
        """Get typical required documents for a scholarship"""
        base_docs = ["Personal Statement", "Transcripts", "Letters of Recommendation"]
        
        # Add specific documents based on scholarship type
        if "STEM" in scholarship_title or "Engineering" in scholarship_title:
            base_docs.extend(["Portfolio", "Research Summary"])
        
        if "Leadership" in scholarship_title:
            base_docs.append("Leadership Examples")
        
        if "Need-based" in scholarship_title:
            base_docs.append("Financial Aid Documentation")
        
        return base_docs
    
    def export_applications(self) -> str:
        """Export applications to JSON format"""
        return json.dumps(self.applications, indent=2, default=str)
    
    def import_applications(self, data: str) -> bool:
        """Import applications from JSON format"""
        try:
            imported_apps = json.loads(data)
            if isinstance(imported_apps, list):
                self.applications = imported_apps
                return True
            return False
        except Exception:
            return False
    
    def get_application_timeline(self, app_id: str) -> List[Dict[str, Any]]:
        """Get timeline of application activities"""
        for app in self.applications:
            if app['id'] == app_id:
                timeline = [
                    {
                        'date': app['date_added'],
                        'action': 'Application Started',
                        'description': f"Added {app['scholarship_title']} to applications"
                    }
                ]
                
                # Add document submissions
                for doc in app['submitted_documents']:
                    timeline.append({
                        'date': doc['date_added'],
                        'action': 'Document Submitted',
                        'description': f"Submitted {doc['name']}"
                    })
                
                # Add status changes (would need to track these separately in full implementation)
                timeline.append({
                    'date': app['last_updated'],
                    'action': 'Status Update',
                    'description': f"Status changed to {app['status']}"
                })
                
                return sorted(timeline, key=lambda x: x['date'], reverse=True)
        
        return []
    
    def set_reminder(self, app_id: str, reminder_date: str, message: str) -> bool:
        """Set a reminder for an application"""
        for app in self.applications:
            if app['id'] == app_id:
                reminder = {
                    'date': reminder_date,
                    'message': message,
                    'created': datetime.now().isoformat()
                }
                app['reminders'].append(reminder)
                return True
        return False
    
    def get_active_reminders(self) -> List[Dict[str, Any]]:
        """Get all active reminders"""
        active_reminders = []
        current_date = datetime.now()
        
        for app in self.applications:
            for reminder in app['reminders']:
                try:
                    reminder_date = datetime.fromisoformat(reminder['date'])
                    if reminder_date <= current_date:
                        active_reminders.append({
                            'app_id': app['id'],
                            'scholarship_title': app['scholarship_title'],
                            'message': reminder['message'],
                            'date': reminder['date']
                        })
                except ValueError:
                    continue
        
        return active_reminders