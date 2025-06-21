import pandas as pd
import json
from typing import List, Dict, Any, Optional
from io import StringIO
import streamlit as st

class DataManager:
    """Manages scholarship data storage and retrieval"""
    
    def __init__(self):
        self.scholarships = []
        self.scholarships_df = None
    
    def load_scholarships(self, scholarships_data: List[Dict[str, Any]]):
        """Load scholarship data from a list of dictionaries"""
        # Load real scholarship data from authentic sources
        from utils.data_integration import RealScholarshipIntegrator
        
        integrator = RealScholarshipIntegrator()
        real_scholarships = integrator.aggregate_all_real_scholarships()
        enriched_scholarships = integrator.enrich_with_additional_data(real_scholarships)
        
        # Combine with any provided data
        all_scholarships = enriched_scholarships + scholarships_data
        
        self.scholarships = all_scholarships
        self.scholarships_df = pd.DataFrame(all_scholarships)
        
        # Ensure proper data types
        self._clean_and_validate_data()
    
    def _clean_and_validate_data(self):
        """Clean and validate scholarship data"""
        if self.scholarships_df is None or self.scholarships_df.empty:
            return
        
        # Convert amount to numeric
        self.scholarships_df['amount'] = pd.to_numeric(self.scholarships_df['amount'], errors='coerce')
        
        # Convert GPA requirement to numeric
        self.scholarships_df['gpa_requirement'] = pd.to_numeric(self.scholarships_df['gpa_requirement'], errors='coerce')
        
        # Ensure target_demographics is a list
        if 'target_demographics' in self.scholarships_df.columns:
            self.scholarships_df['target_demographics'] = self.scholarships_df['target_demographics'].apply(
                lambda x: x if isinstance(x, list) else [x] if x else []
            )
        
        # Fill missing values
        self.scholarships_df['description'] = self.scholarships_df['description'].fillna('')
        self.scholarships_df['eligibility_criteria'] = self.scholarships_df['eligibility_criteria'].fillna('')
        self.scholarships_df['application_requirements'] = self.scholarships_df['application_requirements'].fillna('')
        self.scholarships_df['website'] = self.scholarships_df['website'].fillna('')
        self.scholarships_df['contact_info'] = self.scholarships_df['contact_info'].fillna('')
        
        # Remove any rows with missing critical data
        critical_columns = ['title', 'amount', 'category', 'deadline']
        self.scholarships_df = self.scholarships_df.dropna(subset=critical_columns)
        
        # Reset index after dropping rows
        self.scholarships_df = self.scholarships_df.reset_index(drop=True)
    
    def get_scholarships_df(self) -> pd.DataFrame:
        """Get the scholarships dataframe"""
        return self.scholarships_df.copy() if self.scholarships_df is not None else pd.DataFrame()
    
    def get_scholarship_by_id(self, scholarship_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific scholarship by its index"""
        if self.scholarships_df is None or scholarship_id >= len(self.scholarships_df):
            return None
        
        return self.scholarships_df.iloc[scholarship_id].to_dict()
    
    def search_scholarships(self, query: str, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Search scholarships based on query and filters"""
        if self.scholarships_df is None or self.scholarships_df.empty:
            return pd.DataFrame()
        
        result_df = self.scholarships_df.copy()
        
        # Text search
        if query:
            search_columns = ['title', 'description', 'category', 'eligibility_criteria']
            search_mask = pd.Series([False] * len(result_df))
            
            for column in search_columns:
                if column in result_df.columns:
                    search_mask |= result_df[column].str.contains(query, case=False, na=False)
            
            result_df = result_df[search_mask]
        
        # Apply filters
        if filters:
            # Amount range filter
            if 'min_amount' in filters and filters['min_amount'] is not None:
                result_df = result_df[result_df['amount'] >= filters['min_amount']]
            
            if 'max_amount' in filters and filters['max_amount'] is not None:
                result_df = result_df[result_df['amount'] <= filters['max_amount']]
            
            # Category filter
            if 'categories' in filters and filters['categories']:
                category_mask = result_df['category'].isin(filters['categories'])
                result_df = result_df[category_mask]
            
            # Demographics filter
            if 'demographics' in filters and filters['demographics']:
                demo_mask = result_df['target_demographics'].apply(
                    lambda x: any(demo in filters['demographics'] for demo in x) if isinstance(x, list) else False
                )
                result_df = result_df[demo_mask]
            
            # GPA filter
            if 'max_gpa_requirement' in filters and filters['max_gpa_requirement'] is not None:
                result_df = result_df[result_df['gpa_requirement'] <= filters['max_gpa_requirement']]
        
        return result_df
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        if self.scholarships_df is None or self.scholarships_df.empty:
            return []
        
        return sorted(self.scholarships_df['category'].unique().tolist())
    
    def get_demographics(self) -> List[str]:
        """Get all unique demographics"""
        if self.scholarships_df is None or self.scholarships_df.empty:
            return []
        
        all_demographics = set()
        for demo_list in self.scholarships_df['target_demographics']:
            if isinstance(demo_list, list):
                all_demographics.update(demo_list)
        
        return sorted(list(all_demographics))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the scholarship data"""
        if self.scholarships_df is None or self.scholarships_df.empty:
            return {
                'total_scholarships': 0,
                'total_value': 0,
                'average_amount': 0,
                'min_amount': 0,
                'max_amount': 0,
                'categories_count': 0,
                'demographics_count': 0
            }
        
        return {
            'total_scholarships': len(self.scholarships_df),
            'total_value': self.scholarships_df['amount'].sum(),
            'average_amount': self.scholarships_df['amount'].mean(),
            'min_amount': self.scholarships_df['amount'].min(),
            'max_amount': self.scholarships_df['amount'].max(),
            'categories_count': self.scholarships_df['category'].nunique(),
            'demographics_count': len(self.get_demographics())
        }
    
    def add_scholarship(self, scholarship_data: Dict[str, Any]):
        """Add a new scholarship to the dataset"""
        self.scholarships.append(scholarship_data)
        
        # Recreate the dataframe
        self.scholarships_df = pd.DataFrame(self.scholarships)
        self._clean_and_validate_data()
    
    def update_scholarship(self, index: int, scholarship_data: Dict[str, Any]):
        """Update an existing scholarship"""
        if 0 <= index < len(self.scholarships):
            self.scholarships[index] = scholarship_data
            
            # Recreate the dataframe
            self.scholarships_df = pd.DataFrame(self.scholarships)
            self._clean_and_validate_data()
    
    def delete_scholarship(self, index: int):
        """Delete a scholarship by index"""
        if 0 <= index < len(self.scholarships):
            del self.scholarships[index]
            
            # Recreate the dataframe
            self.scholarships_df = pd.DataFrame(self.scholarships)
            self._clean_and_validate_data()
    
    def export_data(self, format: str = 'json') -> str:
        """Export scholarship data in specified format"""
        if format.lower() == 'json':
            return json.dumps(self.scholarships, indent=2, default=str)
        elif format.lower() == 'csv':
            if self.scholarships_df is not None:
                return self.scholarships_df.to_csv(index=False)
            else:
                return ""
        else:
            raise ValueError("Unsupported export format. Use 'json' or 'csv'.")
    
    def import_data(self, data: str, format: str = 'json'):
        """Import scholarship data from string"""
        try:
            if format.lower() == 'json':
                imported_data = json.loads(data)
                if isinstance(imported_data, list):
                    self.load_scholarships(imported_data)
                else:
                    raise ValueError("JSON data must be a list of scholarship objects")
            elif format.lower() == 'csv':
                df = pd.read_csv(StringIO(data))
                scholarships_list = df.to_dict('records')
                self.load_scholarships(scholarships_list)
            else:
                raise ValueError("Unsupported import format. Use 'json' or 'csv'.")
        except Exception as e:
            raise ValueError(f"Failed to import data: {str(e)}")
