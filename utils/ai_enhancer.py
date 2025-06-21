import os
import json
from typing import Dict, Any, List
import streamlit as st
from openai import OpenAI

class AIEnhancer:
    """AI-powered scholarship enhancement and summarization"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def is_available(self) -> bool:
        """Check if AI enhancement is available"""
        return self.client is not None
    
    def summarize_scholarship(self, scholarship_data: Dict[str, Any]) -> str:
        """Generate an AI summary of a scholarship"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        try:
            # Create a comprehensive prompt
            prompt = f"""
            Please provide a concise, helpful summary of this scholarship opportunity for a student. 
            Focus on the key benefits, target audience, and what makes this scholarship unique or appealing.
            
            Scholarship Details:
            Title: {scholarship_data.get('title', 'N/A')}
            Amount: ${scholarship_data.get('amount', 0):,}
            Category: {scholarship_data.get('category', 'N/A')}
            Target Demographics: {', '.join(scholarship_data.get('target_demographics', []))}
            Description: {scholarship_data.get('description', 'N/A')}
            Eligibility: {scholarship_data.get('eligibility_criteria', 'N/A')}
            Deadline: {scholarship_data.get('deadline', 'N/A')}
            
            Write a 2-3 sentence summary that would help a student quickly understand if this scholarship is right for them.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Failed to generate AI summary: {str(e)}")
    
    def analyze_scholarship_fit(self, scholarship_data: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well a scholarship fits a user's profile using AI"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        try:
            prompt = f"""
            Analyze how well this scholarship matches the student's profile. Provide a JSON response with:
            - match_score: number from 0-100
            - reasons: list of strings explaining why it's a good or poor match
            - recommendations: list of strings with advice for the student
            
            Scholarship:
            Title: {scholarship_data.get('title', 'N/A')}
            Amount: ${scholarship_data.get('amount', 0):,}
            Category: {scholarship_data.get('category', 'N/A')}
            Target Demographics: {', '.join(scholarship_data.get('target_demographics', []))}
            Eligibility: {scholarship_data.get('eligibility_criteria', 'N/A')}
            
            Student Profile:
            Demographics: {', '.join(user_profile.get('demographics', []))}
            Field of Study: {user_profile.get('field_of_study', 'N/A')}
            Academic Level: {user_profile.get('academic_level', 'N/A')}
            GPA: {user_profile.get('gpa', 'N/A')}
            Financial Need: {user_profile.get('financial_need', 'N/A')}
            Interests: {', '.join(user_profile.get('interests', []))}
            Career Goals: {user_profile.get('career_goals', 'N/A')}
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert scholarship advisor. Analyze scholarship-student matches and provide JSON responses."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            raise Exception(f"Failed to analyze scholarship fit: {str(e)}")
    
    def generate_essay_tips(self, scholarship_data: Dict[str, Any], user_profile: Dict[str, Any]) -> List[str]:
        """Generate essay writing tips for a specific scholarship"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        try:
            prompt = f"""
            Provide 3-5 specific essay writing tips for this scholarship application based on the student's profile.
            
            Scholarship:
            Title: {scholarship_data.get('title', 'N/A')}
            Category: {scholarship_data.get('category', 'N/A')}
            Target Demographics: {', '.join(scholarship_data.get('target_demographics', []))}
            Description: {scholarship_data.get('description', 'N/A')}
            
            Student Profile:
            Demographics: {', '.join(user_profile.get('demographics', []))}
            Field of Study: {user_profile.get('field_of_study', 'N/A')}
            Career Goals: {user_profile.get('career_goals', 'N/A')}
            Interests: {', '.join(user_profile.get('interests', []))}
            Extracurriculars: {', '.join(user_profile.get('extracurriculars', []))}
            
            Provide actionable, specific tips that would help this student write a compelling essay for this scholarship.
            Return as a list of tip strings.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            tips_text = response.choices[0].message.content.strip()
            # Split into individual tips (assuming they're separated by newlines or bullet points)
            tips = [tip.strip('• -').strip() for tip in tips_text.split('\n') if tip.strip()]
            return tips[:5]  # Return max 5 tips
            
        except Exception as e:
            raise Exception(f"Failed to generate essay tips: {str(e)}")
    
    def standardize_scholarship_data(self, raw_scholarship: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to standardize and clean scholarship data"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        try:
            prompt = f"""
            Clean and standardize this scholarship data. Provide a JSON response with these exact fields:
            - title: string (clean, proper case)
            - amount: number (extract numeric value)
            - category: string (standardized category like "STEM", "Business", etc.)
            - target_demographics: array of strings (standardized demographic categories)
            - description: string (clean, concise description)
            - eligibility_criteria: string (clear eligibility requirements)
            - deadline: string (standardized date format MM/DD/YYYY if possible)
            - gpa_requirement: number (extract GPA requirement, use 0.0 if none)
            
            Raw data:
            {json.dumps(raw_scholarship, indent=2)}
            
            Standardize the data to be consistent and clean.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data cleaning expert. Standardize scholarship information and return clean JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=400,
                temperature=0.1
            )
            
            standardized_data = json.loads(response.choices[0].message.content)
            return standardized_data
            
        except Exception as e:
            raise Exception(f"Failed to standardize scholarship data: {str(e)}")
    
    def generate_search_suggestions(self, user_profile: Dict[str, Any]) -> List[str]:
        """Generate search term suggestions based on user profile"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        try:
            prompt = f"""
            Based on this student's profile, suggest 5-7 specific search terms they should use to find relevant scholarships.
            
            Student Profile:
            Demographics: {', '.join(user_profile.get('demographics', []))}
            Field of Study: {user_profile.get('field_of_study', 'N/A')}
            Academic Level: {user_profile.get('academic_level', 'N/A')}
            Interests: {', '.join(user_profile.get('interests', []))}
            Career Goals: {user_profile.get('career_goals', 'N/A')}
            Location: {user_profile.get('location', 'N/A')}
            
            Provide search terms that would help them find scholarships they might not have considered.
            Return as a simple list, one term per line.
            """
            
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            suggestions_text = response.choices[0].message.content.strip()
            suggestions = [term.strip('• -').strip() for term in suggestions_text.split('\n') if term.strip()]
            return suggestions[:7]  # Return max 7 suggestions
            
        except Exception as e:
            raise Exception(f"Failed to generate search suggestions: {str(e)}")
    
    def batch_summarize_scholarships(self, scholarships: List[Dict[str, Any]]) -> Dict[int, str]:
        """Summarize multiple scholarships in a batch (more efficient)"""
        if not self.is_available():
            raise Exception("OpenAI API key not configured")
        
        summaries = {}
        
        # Process in smaller batches to avoid token limits
        batch_size = 5
        for i in range(0, len(scholarships), batch_size):
            batch = scholarships[i:i+batch_size]
            
            try:
                batch_summaries = self._process_scholarship_batch(batch, i)
                summaries.update(batch_summaries)
            except Exception as e:
                # If batch fails, try individual processing
                for j, scholarship in enumerate(batch):
                    try:
                        summary = self.summarize_scholarship(scholarship)
                        summaries[i + j] = summary
                    except:
                        summaries[i + j] = "Summary unavailable"
        
        return summaries
    
    def _process_scholarship_batch(self, scholarships: List[Dict[str, Any]], start_index: int) -> Dict[int, str]:
        """Process a batch of scholarships for summarization"""
        prompt = "Provide concise summaries for these scholarships. For each scholarship, write a 2-3 sentence summary.\n\n"
        
        for i, scholarship in enumerate(scholarships):
            prompt += f"Scholarship {i+1}:\n"
            prompt += f"Title: {scholarship.get('title', 'N/A')}\n"
            prompt += f"Amount: ${scholarship.get('amount', 0):,}\n"
            prompt += f"Category: {scholarship.get('category', 'N/A')}\n"
            prompt += f"Description: {scholarship.get('description', 'N/A')[:200]}...\n\n"
        
        prompt += "Provide summaries in this format:\nScholarship 1: [summary]\nScholarship 2: [summary]\n..."
        
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        response_text = response.choices[0].message.content.strip()
        summaries = {}
        
        # Parse the response
        lines = response_text.split('\n')
        for line in lines:
            if line.startswith('Scholarship '):
                try:
                    # Extract number and summary
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        num_part = parts[0].replace('Scholarship ', '').strip()
                        summary = parts[1].strip()
                        index = int(num_part) - 1 + start_index
                        summaries[index] = summary
                except:
                    continue
        
        return summaries
