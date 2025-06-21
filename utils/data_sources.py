import requests
import json
import pandas as pd
from typing import List, Dict, Any, Optional
import streamlit as st
from datetime import datetime, timedelta
import time

class ScholarshipDataSources:
    """Integrate with real scholarship data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ScholarSphere/1.0 (Educational Platform)'
        })
        
    def fetch_fastweb_scholarships(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch scholarships from Fastweb-style API
        Note: This is a template for integration with real APIs
        """
        # Template for real API integration
        scholarships = []
        
        # In production, this would connect to actual scholarship APIs
        # For now, we'll create a structure that mirrors real data sources
        
        return scholarships
    
    def fetch_college_board_scholarships(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch scholarships from College Board Scholarship Search
        """
        scholarships = []
        
        # Template for College Board API integration
        # Real implementation would use their official API
        
        return scholarships
    
    def fetch_university_scholarships(self, universities: List[str]) -> List[Dict[str, Any]]:
        """
        Fetch scholarships from university databases
        """
        scholarships = []
        
        # Template for university-specific scholarship APIs
        # Would integrate with institution databases
        
        return scholarships
    
    def fetch_government_scholarships(self) -> List[Dict[str, Any]]:
        """
        Fetch government scholarship opportunities
        """
        scholarships = []
        
        # Template for government scholarship APIs
        # Would integrate with federal/state databases
        
        return scholarships
    
    def fetch_foundation_scholarships(self) -> List[Dict[str, Any]]:
        """
        Fetch scholarships from private foundations
        """
        scholarships = []
        
        # Template for foundation APIs
        # Would integrate with foundation databases
        
        return scholarships
    
    def standardize_scholarship_data(self, raw_data: Dict[str, Any], source: str) -> Dict[str, Any]:
        """
        Standardize scholarship data from different sources
        """
        standardized = {
            'title': raw_data.get('title', ''),
            'amount': self._parse_amount(raw_data.get('amount', 0)),
            'category': self._categorize_scholarship(raw_data),
            'target_demographics': self._extract_demographics(raw_data),
            'description': raw_data.get('description', ''),
            'eligibility_criteria': raw_data.get('eligibility', ''),
            'application_requirements': raw_data.get('requirements', ''),
            'deadline': self._parse_deadline(raw_data.get('deadline', '')),
            'gpa_requirement': self._parse_gpa(raw_data.get('gpa', 0)),
            'website': raw_data.get('url', ''),
            'contact_info': raw_data.get('contact', ''),
            'source': source,
            'last_updated': datetime.now().isoformat()
        }
        
        return standardized
    
    def _parse_amount(self, amount_str) -> float:
        """Parse scholarship amount from various formats"""
        if isinstance(amount_str, (int, float)):
            return float(amount_str)
        
        if isinstance(amount_str, str):
            # Remove currency symbols and commas
            amount_str = amount_str.replace('$', '').replace(',', '').strip()
            
            # Handle ranges (take the maximum)
            if '-' in amount_str:
                parts = amount_str.split('-')
                if len(parts) == 2:
                    try:
                        return float(parts[1].strip())
                    except ValueError:
                        pass
            
            # Handle "up to" amounts
            if 'up to' in amount_str.lower():
                amount_str = amount_str.lower().replace('up to', '').strip()
            
            try:
                return float(amount_str)
            except ValueError:
                return 0.0
        
        return 0.0
    
    def _categorize_scholarship(self, raw_data: Dict[str, Any]) -> str:
        """Categorize scholarship based on keywords"""
        text_to_analyze = ' '.join([
            raw_data.get('title', ''),
            raw_data.get('description', ''),
            raw_data.get('field', ''),
            raw_data.get('major', '')
        ]).lower()
        
        # Category mapping
        category_keywords = {
            'STEM': ['stem', 'science', 'technology', 'engineering', 'mathematics', 'computer', 'programming'],
            'Medicine': ['medicine', 'medical', 'health', 'nursing', 'pharmacy', 'dental', 'healthcare'],
            'Business': ['business', 'finance', 'accounting', 'marketing', 'management', 'economics'],
            'Education': ['education', 'teaching', 'teacher', 'educator', 'curriculum'],
            'Arts': ['arts', 'music', 'theater', 'dance', 'creative', 'fine arts', 'visual'],
            'Social Sciences': ['social', 'psychology', 'sociology', 'anthropology', 'political'],
            'Environmental Science': ['environment', 'ecology', 'sustainability', 'conservation'],
            'Engineering': ['engineering', 'mechanical', 'electrical', 'civil', 'chemical'],
            'Computer Science': ['computer science', 'software', 'programming', 'coding', 'it']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                return category
        
        return 'General'
    
    def _extract_demographics(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract target demographics from scholarship data"""
        text_to_analyze = ' '.join([
            raw_data.get('title', ''),
            raw_data.get('description', ''),
            raw_data.get('eligibility', ''),
            raw_data.get('target', '')
        ]).lower()
        
        demographics_keywords = {
            'Women in STEM': ['women', 'female', 'girls in stem', 'women in technology'],
            'LGBTQ+': ['lgbtq', 'lgbt', 'gay', 'lesbian', 'transgender', 'queer'],
            'First-generation college student': ['first generation', 'first-gen', 'first in family'],
            'Underrepresented minority': ['minority', 'underrepresented', 'african american', 'hispanic', 'latino', 'native american'],
            'International student': ['international', 'foreign', 'non-citizen', 'visa'],
            'Veteran': ['veteran', 'military', 'armed forces', 'service member'],
            'Student with disability': ['disability', 'disabled', 'accessibility', 'special needs'],
            'Low-income background': ['low income', 'financial need', 'pell grant', 'need-based'],
            'Rural/Small town background': ['rural', 'small town', 'farming', 'agriculture']
        }
        
        found_demographics = []
        for demographic, keywords in demographics_keywords.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                found_demographics.append(demographic)
        
        return found_demographics if found_demographics else ['General']
    
    def _parse_deadline(self, deadline_str: str) -> str:
        """Parse deadline from various formats"""
        if not deadline_str:
            return (datetime.now() + timedelta(days=180)).strftime('%m/%d/%Y')
        
        # Handle common date formats
        date_formats = [
            '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d',
            '%B %d, %Y', '%b %d, %Y',
            '%m/%d/%y', '%m-%d-%y'
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(deadline_str, fmt)
                return parsed_date.strftime('%m/%d/%Y')
            except ValueError:
                continue
        
        return deadline_str
    
    def _parse_gpa(self, gpa_str) -> float:
        """Parse GPA requirement from various formats"""
        if isinstance(gpa_str, (int, float)):
            return float(gpa_str)
        
        if isinstance(gpa_str, str):
            # Extract numeric value
            import re
            numbers = re.findall(r'\d+\.?\d*', gpa_str)
            if numbers:
                gpa = float(numbers[0])
                return min(gpa, 4.0)  # Cap at 4.0
        
        return 0.0
    
    def aggregate_all_sources(self, limit_per_source: int = 100) -> List[Dict[str, Any]]:
        """
        Aggregate scholarships from all available sources
        """
        all_scholarships = []
        
        # Fetch from different sources
        sources = [
            ('fastweb', self.fetch_fastweb_scholarships),
            ('college_board', self.fetch_college_board_scholarships),
            ('government', self.fetch_government_scholarships),
            ('foundations', self.fetch_foundation_scholarships)
        ]
        
        for source_name, fetch_function in sources:
            try:
                scholarships = fetch_function(limit_per_source)
                for scholarship in scholarships:
                    standardized = self.standardize_scholarship_data(scholarship, source_name)
                    all_scholarships.append(standardized)
            except Exception as e:
                st.warning(f"Could not fetch from {source_name}: {str(e)}")
                continue
        
        return all_scholarships
    
    def get_real_scholarship_feeds(self) -> List[Dict[str, Any]]:
        """
        Get real scholarship data from available public APIs and feeds
        Note: This requires API keys and proper authentication for production use
        """
        
        # For demonstration, return structure that shows integration capability
        # In production, this would connect to real APIs
        
        real_scholarships = []
        
        # Template for real API integration
        # Each source would have its own authentication and data parsing logic
        
        return real_scholarships
    
    def validate_and_enrich_data(self, scholarships: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and enrich scholarship data using AI
        """
        from utils.ai_enhancer import AIEnhancer
        
        ai_enhancer = AIEnhancer()
        enriched_scholarships = []
        
        for scholarship in scholarships:
            try:
                # Validate required fields
                if not scholarship.get('title') or not scholarship.get('amount'):
                    continue
                
                # Enrich with AI if available
                if ai_enhancer.is_available():
                    try:
                        enriched = ai_enhancer.standardize_scholarship_data(scholarship)
                        enriched_scholarships.append(enriched)
                    except Exception:
                        # Fall back to original data if AI enhancement fails
                        enriched_scholarships.append(scholarship)
                else:
                    enriched_scholarships.append(scholarship)
                    
            except Exception as e:
                continue
        
        return enriched_scholarships