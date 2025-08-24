import os
import json
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional
import streamlit as st
from openai import OpenAI
from utils.ai_enhancer import AIEnhancer

class AdvancedAIMatchingEngine:
    """Advanced AI-powered eligibility matching and application assistance"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        self.ai_enhancer = AIEnhancer()
    
    def is_available(self) -> bool:
        """Check if AI matching is available"""
        return self.client is not None
    
    def calculate_comprehensive_eligibility_score(self, scholarship: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive eligibility score using AI and rule-based matching"""
        if not self.is_available():
            return self._basic_eligibility_score(scholarship, user_profile)
        
        try:
            prompt = f"""
            Analyze this scholarship against the student's profile and provide a comprehensive eligibility assessment.
            
            Return a JSON response with:
            - overall_score: number 0-100 (likelihood of eligibility)
            - demographic_match: number 0-100 (how well demographics align)
            - academic_match: number 0-100 (academic requirements fit)
            - field_relevance: number 0-100 (field of study relevance)
            - financial_alignment: number 0-100 (financial need alignment)
            - application_difficulty: number 1-5 (1=easy, 5=very difficult)
            - success_probability: number 0-100 (estimated chance of winning)
            - missing_requirements: array of strings (what student lacks)
            - strengths: array of strings (student's advantages)
            - recommendations: array of strings (actionable advice)
            
            Scholarship:
            Title: {scholarship.get('title', 'N/A')}
            Amount: ${scholarship.get('amount', 0):,}
            Category: {scholarship.get('category', 'N/A')}
            Target Demographics: {scholarship.get('target_demographics', [])}
            Eligibility: {scholarship.get('eligibility_criteria', 'N/A')}
            GPA Requirement: {scholarship.get('gpa_requirement', 0.0)}
            Application Difficulty: {scholarship.get('application_difficulty', 'Medium')}
            Estimated Applicants: {scholarship.get('estimated_applicants', 'Unknown')}
            
            Student Profile:
            Demographics: {user_profile.get('demographics', [])}
            Field of Study: {user_profile.get('field_of_study', 'N/A')}
            Academic Level: {user_profile.get('academic_level', 'N/A')}
            GPA: {user_profile.get('gpa', 'N/A')}
            Financial Need: {user_profile.get('financial_need', 'N/A')}
            Location: {user_profile.get('location', 'N/A')}
            Interests: {user_profile.get('interests', [])}
            Extracurriculars: {user_profile.get('extracurriculars', [])}
            Career Goals: {user_profile.get('career_goals', 'N/A')}
            Graduation Year: {user_profile.get('graduation_year', 'N/A')}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert scholarship advisor with deep knowledge of eligibility requirements and application success factors. Provide detailed, accurate assessments."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=600,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            result = json.loads(content) if content else {}
            
            # Add calculated fields
            result['scholarship_id'] = scholarship.get('id')
            result['scholarship_title'] = scholarship.get('title', '')
            result['award_amount'] = scholarship.get('amount', 0)
            
            return result
            
        except Exception as e:
            st.error(f"AI eligibility analysis failed: {str(e)}")
            return self._basic_eligibility_score(scholarship, user_profile)
    
    def _basic_eligibility_score(self, scholarship: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based eligibility scoring"""
        score = 0
        missing_requirements = []
        strengths = []
        
        # GPA check
        required_gpa = scholarship.get('gpa_requirement', 0.0)
        user_gpa = user_profile.get('gpa', 0.0)
        if required_gpa > 0:
            if user_gpa >= required_gpa:
                score += 25
                strengths.append(f"Meets GPA requirement ({user_gpa} >= {required_gpa})")
            else:
                missing_requirements.append(f"GPA requirement not met ({user_gpa} < {required_gpa})")
        else:
            score += 15
        
        # Demographics match
        scholarship_demos = scholarship.get('target_demographics', [])
        user_demos = user_profile.get('demographics', [])
        demo_match = len(set(scholarship_demos) & set(user_demos))
        if demo_match > 0:
            score += min(30, demo_match * 15)
            strengths.append(f"Matches {demo_match} demographic criteria")
        
        # Field relevance
        scholarship_category = scholarship.get('category', '').lower()
        user_field = user_profile.get('field_of_study', '').lower()
        if scholarship_category in user_field or user_field in scholarship_category:
            score += 20
            strengths.append("Field of study aligns with scholarship category")
        
        # Academic level
        user_level = user_profile.get('academic_level', '')
        if user_level:
            score += 15
            strengths.append(f"Clear academic level: {user_level}")
        
        return {
            'overall_score': min(100, score),
            'demographic_match': min(100, demo_match * 25) if demo_match > 0 else 0,
            'academic_match': 75 if user_gpa >= required_gpa else 25,
            'field_relevance': 80 if scholarship_category in user_field else 20,
            'financial_alignment': 50,  # Default moderate alignment
            'application_difficulty': 3,  # Default medium difficulty
            'success_probability': min(100, score * 0.8),
            'missing_requirements': missing_requirements,
            'strengths': strengths,
            'recommendations': ["Complete your profile for better matching"],
            'scholarship_id': scholarship.get('id'),
            'scholarship_title': scholarship.get('title'),
            'award_amount': scholarship.get('amount', 0)
        }
    
    def generate_personalized_application_strategy(self, scholarship: Dict[str, Any], user_profile: Dict[str, Any], eligibility_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive application strategy using AI"""
        if not self.is_available():
            return self._basic_application_strategy(scholarship, user_profile)
        
        try:
            prompt = f"""
            Create a personalized application strategy for this student applying to this scholarship.
            
            Based on the eligibility analysis and profiles, provide a JSON response with:
            - timeline: array of objects with "week", "task", "priority" (priority: 1-5)
            - essay_strategy: object with "main_themes", "key_points", "tone", "word_count_suggestion"
            - document_checklist: array of strings (required documents)
            - competitive_advantages: array of strings (student's unique selling points)
            - improvement_areas: array of strings (areas to strengthen before applying)
            - networking_suggestions: array of strings (people/organizations to connect with)
            - deadline_alerts: array of objects with "task", "days_before_deadline"
            
            Scholarship:
            Title: {scholarship.get('title', 'N/A')}
            Amount: ${scholarship.get('amount', 0):,}
            Requirements: {scholarship.get('application_requirements', 'N/A')}
            Deadline: {scholarship.get('deadline', 'N/A')}
            
            Student Profile:
            Demographics: {user_profile.get('demographics', [])}
            Field: {user_profile.get('field_of_study', 'N/A')}
            Level: {user_profile.get('academic_level', 'N/A')}
            GPA: {user_profile.get('gpa', 'N/A')}
            Interests: {user_profile.get('interests', [])}
            Extracurriculars: {user_profile.get('extracurriculars', [])}
            Career Goals: {user_profile.get('career_goals', 'N/A')}
            
            Eligibility Analysis:
            Overall Score: {eligibility_analysis.get('overall_score', 0)}
            Strengths: {eligibility_analysis.get('strengths', [])}
            Missing Requirements: {eligibility_analysis.get('missing_requirements', [])}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert application strategist who helps students create winning scholarship applications. Provide detailed, actionable strategies."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=800,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            strategy = json.loads(content) if content else {}
            return strategy
            
        except Exception as e:
            st.error(f"Failed to generate application strategy: {str(e)}")
            return self._basic_application_strategy(scholarship, user_profile)
    
    def _basic_application_strategy(self, scholarship: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback basic application strategy"""
        return {
            'timeline': [
                {"week": 1, "task": "Gather required documents", "priority": 5},
                {"week": 2, "task": "Write first draft of essay", "priority": 4},
                {"week": 3, "task": "Request recommendation letters", "priority": 5},
                {"week": 4, "task": "Revise and finalize application", "priority": 5}
            ],
            'essay_strategy': {
                'main_themes': ['Academic achievement', 'Personal growth', 'Future goals'],
                'key_points': ['Highlight relevant experiences', 'Show passion for field'],
                'tone': 'Professional but personal',
                'word_count_suggestion': 500
            },
            'document_checklist': ['Personal statement', 'Transcripts', 'Recommendation letters'],
            'competitive_advantages': ['Strong academic record'],
            'improvement_areas': ['Complete profile information'],
            'networking_suggestions': ['Connect with alumni', 'Join professional organizations'],
            'deadline_alerts': [
                {"task": "Submit application", "days_before_deadline": 7}
            ]
        }
    
    def batch_analyze_scholarships(self, scholarships: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze multiple scholarships efficiently and rank by compatibility"""
        results = []
        
        for scholarship in scholarships:
            try:
                analysis = self.calculate_comprehensive_eligibility_score(scholarship, user_profile)
                results.append(analysis)
            except Exception as e:
                # Create basic result for failed analysis
                basic_result = self._basic_eligibility_score(scholarship, user_profile)
                results.append(basic_result)
        
        # Sort by overall score (descending)
        results.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        return results
    
    def generate_ai_insights_dashboard(self, user_profile: Dict[str, Any], recent_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate personalized insights for the dashboard"""
        if not self.is_available() or not recent_analyses:
            return self._basic_insights(user_profile, recent_analyses)
        
        try:
            # Prepare analysis summary
            avg_score = np.mean([a.get('overall_score', 0) for a in recent_analyses[:10]])
            top_categories = {}
            common_missing = {}
            
            for analysis in recent_analyses[:10]:
                # Track categories
                category = analysis.get('scholarship_category', 'General')
                top_categories[category] = top_categories.get(category, 0) + 1
                
                # Track missing requirements
                for req in analysis.get('missing_requirements', []):
                    common_missing[req] = common_missing.get(req, 0) + 1
            
            prompt = f"""
            Generate personalized insights for this student's scholarship journey.
            
            Provide JSON response with:
            - profile_strength_score: number 0-100
            - key_insights: array of strings (3-5 key observations)
            - improvement_recommendations: array of strings (actionable steps)
            - opportunity_alerts: array of strings (specific opportunities to pursue)
            - success_predictors: array of strings (factors that increase success)
            - next_actions: array of strings (immediate steps to take)
            
            Student Profile:
            Demographics: {user_profile.get('demographics', [])}
            Field: {user_profile.get('field_of_study', 'N/A')}
            Level: {user_profile.get('academic_level', 'N/A')}
            GPA: {user_profile.get('gpa', 'N/A')}
            Interests: {user_profile.get('interests', [])}
            Career Goals: {user_profile.get('career_goals', 'N/A')}
            
            Recent Analysis Summary:
            Average Eligibility Score: {avg_score:.1f}/100
            Top Categories: {dict(list(top_categories.items())[:3])}
            Common Missing Requirements: {dict(list(common_missing.items())[:3])}
            Total Scholarships Analyzed: {len(recent_analyses)}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a scholarship success coach. Provide encouraging but realistic insights to help students succeed."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.4
            )
            
            content = response.choices[0].message.content
            insights = json.loads(content) if content else {}
            return insights
            
        except Exception as e:
            st.error(f"Failed to generate AI insights: {str(e)}")
            return self._basic_insights(user_profile, recent_analyses)
    
    def _basic_insights(self, user_profile: Dict[str, Any], recent_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback basic insights"""
        profile_completeness = sum([
            1 for field in ['demographics', 'field_of_study', 'academic_level', 'gpa', 'interests', 'career_goals']
            if user_profile.get(field)
        ]) / 6 * 100
        
        return {
            'profile_strength_score': int(profile_completeness),
            'key_insights': [
                f"Your profile is {profile_completeness:.0f}% complete",
                f"You've analyzed {len(recent_analyses)} scholarships recently"
            ],
            'improvement_recommendations': [
                "Complete all profile fields for better matching",
                "Add more extracurricular activities",
                "Update your career goals"
            ],
            'opportunity_alerts': [
                "Look for scholarships in your field of study",
                "Consider scholarships for your demographic groups"
            ],
            'success_predictors': [
                "Strong academic performance",
                "Clear career goals",
                "Diverse experiences"
            ],
            'next_actions': [
                "Update your profile",
                "Apply to high-match scholarships",
                "Prepare application materials"
            ]
        }