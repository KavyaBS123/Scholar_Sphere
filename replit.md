# ScholarSphere - Scholarship Discovery Platform

## Overview

ScholarSphere is a comprehensive scholarship discovery and application management platform that leverages AI-powered matching and data analytics to help students find and apply for scholarships. The platform features a Streamlit-based web interface with multiple modules including scholarship search, AI-driven recommendations, application tracking, and data visualization through clustering analysis.

The system integrates real scholarship data from verified sources like government databases, university systems, and established scholarship providers. It provides personalized recommendations based on user profiles, AI-powered application assistance, and comprehensive tracking tools to manage the entire scholarship application lifecycle.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit multi-page application with responsive layout
- **Page Structure**: Modular design with 8 distinct pages (Dashboard, Search, Clusters, Profile Setup, Application Tracker, Data Sources, Database Management, AI Assistant)
- **State Management**: Streamlit session state for user profiles, data managers, and application tracking
- **UI Components**: Plotly for data visualization, interactive forms for user input, and sidebar navigation

### Backend Architecture
- **Database Layer**: SQLAlchemy ORM with PostgreSQL backend
- **Repository Pattern**: Separate repositories for scholarships, users, and applications (ScholarshipRepository, UserRepository, ApplicationRepository)
- **Data Models**: Scholarship, UserProfile, Application, SavedScholarship, SearchHistory models
- **Business Logic**: Utility classes for data management, AI integration, clustering, and application tracking

### AI Integration
- **AI Matching Engine**: OpenAI GPT-4o integration for eligibility scoring, application assistance, and personalized recommendations
- **AI Enhancer**: Scholarship summarization and search suggestions
- **Matching Algorithm**: Hybrid approach combining rule-based matching with AI analysis for comprehensive eligibility scoring

### Data Processing
- **Clustering Engine**: K-means, hierarchical, and DBSCAN clustering using scikit-learn for scholarship categorization
- **Data Integration**: Real-time integration with government databases, university systems, and scholarship providers
- **Data Validation**: Automated cleaning and validation of scholarship data with type conversion and missing value handling

### Application Management
- **Tracking System**: Real-time application status tracking with completion percentages and deadline management
- **Document Management**: Required document tracking and submission status monitoring
- **Analytics**: Dashboard with application statistics, success rates, and deadline alerts

## External Dependencies

### AI Services
- **OpenAI API**: GPT-4o model for scholarship analysis, eligibility matching, and application assistance
- **API Configuration**: Environment variable-based API key management with graceful degradation

### Database
- **PostgreSQL**: Primary data storage for scholarships, user profiles, applications, and search history
- **SQLAlchemy**: ORM layer with declarative base models and session management

### Data Sources
- **Government APIs**: Federal and state scholarship databases
- **Educational Institutions**: University scholarship systems and databases
- **Scholarship Providers**: Integration with major scholarship platforms (Fastweb, Scholarships.com, etc.)
- **Verification Systems**: Data validation and authenticity checking for scholarship information

### Python Libraries
- **Web Framework**: Streamlit for the user interface
- **Data Processing**: Pandas for data manipulation, NumPy for numerical operations
- **Visualization**: Plotly Express and Plotly Graph Objects for interactive charts
- **Machine Learning**: Scikit-learn for clustering and data preprocessing
- **HTTP Client**: Requests for external API integration
- **Database**: SQLAlchemy for ORM functionality

### Development Tools
- **Environment Management**: Python environment variables for configuration
- **Session Management**: Streamlit session state for user data persistence
- **Error Handling**: Comprehensive exception handling with user-friendly error messages