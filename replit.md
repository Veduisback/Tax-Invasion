# Tax Fraud Detection System

## Overview
A comprehensive Tax Fraud Detection System for the Income Tax Department of India featuring multi-AI ensemble analysis, machine learning models, and specialized small vendor fraud detection.

## Current State
**Status**: Fully operational with multi-AI integration

## Key Features

### 1. Multi-AI Ensemble Analysis
- **OpenAI GPT-5**: Primary AI model (confidence weight: 0.9)
- **Anthropic Claude Sonnet-4**: Secondary AI model (confidence weight: 0.85)
- **Google Gemini 2.5**: Tertiary AI model (confidence weight: 0.8)
- AI consensus scoring combines insights from all available models using weighted averaging

### 2. Machine Learning Models
- **Isolation Forest**: Anomaly detection
- **Random Forest**: Classification
- **XGBoost**: Gradient boosting classification
- Ensemble scoring combines all ML models with weighted averaging

### 3. Small Vendor Detection
- Daily revenue range calculations (500-15,000 INR typical)
- Uses daily_revenue_range * 300 working days * num_outlets for annual expectations
- Visual intelligence for stall photo analysis
- Lifestyle vs income gap analysis
- Network analysis for connection mapping

### 4. Business Types Supported
- Corporate entities (MNC, Mega Mart, Office/Corporate)
- Manufacturing and service businesses
- Small vendors (Street Vendor, Hawker, Roadside Stall, Tea Stall, etc.)

## Project Structure
- `app.py` - Main Streamlit application
- `ai_analysis.py` - Multi-AI ensemble integration (GPT-5, Claude, Gemini)
- `fraud_detection.py` - ML-based fraud detection engine
- `sample_data.py` - Business benchmarks and data generation
- `database.py` - PostgreSQL database operations
- `behavioral_analysis.py` - Behavioral pattern analysis
- `visual_intelligence.py` - Photo/visual analysis
- `network_analysis.py` - Business network mapping
- `pdf_generator.py` - PDF report generation
- `location_service.py` - Location verification services
- `web_scraper.py` - Fraud news scraping

## Environment Variables Required
- `DATABASE_URL` - PostgreSQL connection string (auto-configured)
- `OPENAI_API_KEY` - For GPT-5 analysis
- `ANTHROPIC_API_KEY` - For Claude analysis
- `GEMINI_API_KEY` - For Gemini analysis

## Recent Changes (December 2025)
- Fixed small vendor calculations to use daily_revenue_range instead of revenue_per_sqft
- Implemented multi-AI ensemble with OpenAI, Anthropic, and Gemini integration
- Added weighted consensus scoring mechanism
- All AI providers gracefully fall back if unavailable

## Running the Application
```bash
streamlit run app.py --server.port 5000
```
