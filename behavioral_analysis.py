import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import numpy as np

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if OPENAI_AVAILABLE and OPENAI_API_KEY:
    # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
    # do not change this unless explicitly requested by the user
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None


LIFESTYLE_COST_ESTIMATES = {
    "vehicle": {
        "None": {"purchase": 0, "annual_maintenance": 0},
        "Two-wheeler (Basic)": {"purchase": 80000, "annual_maintenance": 15000},
        "Two-wheeler (Premium)": {"purchase": 200000, "annual_maintenance": 25000},
        "Four-wheeler (Economy)": {"purchase": 600000, "annual_maintenance": 60000},
        "Four-wheeler (Mid-range)": {"purchase": 1500000, "annual_maintenance": 100000},
        "Four-wheeler (Luxury)": {"purchase": 4000000, "annual_maintenance": 200000},
        "Multiple Vehicles": {"purchase": 8000000, "annual_maintenance": 400000}
    },
    "property": {
        "Rented (Basic)": {"value": 0, "annual_cost": 120000},
        "Rented (Premium)": {"value": 0, "annual_cost": 360000},
        "Owned (1 Property)": {"value": 3000000, "annual_cost": 60000},
        "Owned (Multiple Properties)": {"value": 15000000, "annual_cost": 200000},
        "Owned (Premium/Luxury)": {"value": 50000000, "annual_cost": 500000}
    },
    "education": {
        "Government School": {"annual": 5000},
        "Private School (Budget)": {"annual": 40000},
        "Private School (Mid-tier)": {"annual": 120000},
        "Private School (Premium)": {"annual": 350000},
        "International School": {"annual": 800000},
        "Abroad Education": {"annual": 2500000}
    },
    "travel": {
        "Local Only": {"annual": 10000},
        "Occasional Domestic": {"annual": 50000},
        "Frequent Domestic": {"annual": 150000},
        "Occasional International": {"annual": 300000},
        "Frequent International": {"annual": 800000},
        "Luxury Travel": {"annual": 2000000}
    },
    "jewelry": {
        "None/Minimal": {"annual": 10000},
        "Occasional (Below 1L)": {"annual": 50000},
        "Regular (1-5L/year)": {"annual": 300000},
        "Frequent (5-20L/year)": {"annual": 1200000},
        "Heavy (Above 20L/year)": {"annual": 3000000}
    },
    "mobile_devices": {
        "Basic Phone": {"value": 5000, "annual": 2000},
        "Budget Smartphone": {"value": 15000, "annual": 5000},
        "Mid-range Smartphone": {"value": 35000, "annual": 10000},
        "Premium Smartphone": {"value": 100000, "annual": 20000},
        "Multiple Premium Devices": {"value": 300000, "annual": 50000}
    }
}


def calculate_lifestyle_expense_profile(lifestyle_data: Dict) -> Dict:
    total_annual_expense = 0
    total_asset_value = 0
    expense_breakdown = {}
    asset_breakdown = {}
    
    vehicle = lifestyle_data.get("vehicle", "None")
    if vehicle in LIFESTYLE_COST_ESTIMATES["vehicle"]:
        vehicle_data = LIFESTYLE_COST_ESTIMATES["vehicle"][vehicle]
        expense_breakdown["vehicle_maintenance"] = vehicle_data["annual_maintenance"]
        asset_breakdown["vehicles"] = vehicle_data["purchase"]
        total_annual_expense += vehicle_data["annual_maintenance"]
        total_asset_value += vehicle_data["purchase"]
    
    property_type = lifestyle_data.get("property", "Rented (Basic)")
    if property_type in LIFESTYLE_COST_ESTIMATES["property"]:
        prop_data = LIFESTYLE_COST_ESTIMATES["property"][property_type]
        expense_breakdown["housing"] = prop_data["annual_cost"]
        asset_breakdown["property"] = prop_data["value"]
        total_annual_expense += prop_data["annual_cost"]
        total_asset_value += prop_data["value"]
    
    education = lifestyle_data.get("education", "Government School")
    if education in LIFESTYLE_COST_ESTIMATES["education"]:
        edu_cost = LIFESTYLE_COST_ESTIMATES["education"][education]["annual"]
        num_children = lifestyle_data.get("num_children", 1)
        expense_breakdown["education"] = edu_cost * num_children
        total_annual_expense += edu_cost * num_children
    
    travel = lifestyle_data.get("travel", "Local Only")
    if travel in LIFESTYLE_COST_ESTIMATES["travel"]:
        travel_cost = LIFESTYLE_COST_ESTIMATES["travel"][travel]["annual"]
        expense_breakdown["travel"] = travel_cost
        total_annual_expense += travel_cost
    
    jewelry = lifestyle_data.get("jewelry", "None/Minimal")
    if jewelry in LIFESTYLE_COST_ESTIMATES["jewelry"]:
        jewelry_cost = LIFESTYLE_COST_ESTIMATES["jewelry"][jewelry]["annual"]
        expense_breakdown["jewelry"] = jewelry_cost
        total_annual_expense += jewelry_cost
    
    devices = lifestyle_data.get("mobile_devices", "Budget Smartphone")
    if devices in LIFESTYLE_COST_ESTIMATES["mobile_devices"]:
        device_data = LIFESTYLE_COST_ESTIMATES["mobile_devices"][devices]
        expense_breakdown["electronics"] = device_data["annual"]
        asset_breakdown["electronics"] = device_data["value"]
        total_annual_expense += device_data["annual"]
        total_asset_value += device_data["value"]
    
    basic_living = 200000
    expense_breakdown["basic_living"] = basic_living
    total_annual_expense += basic_living
    
    return {
        "total_annual_expense": total_annual_expense,
        "total_asset_value": total_asset_value,
        "expense_breakdown": expense_breakdown,
        "asset_breakdown": asset_breakdown,
        "minimum_income_required": total_annual_expense * 1.3
    }


def analyze_income_lifestyle_gap(
    declared_income: float,
    lifestyle_data: Dict
) -> Dict:
    expense_profile = calculate_lifestyle_expense_profile(lifestyle_data)
    
    annual_expense = expense_profile["total_annual_expense"]
    asset_value = expense_profile["total_asset_value"]
    
    if declared_income > 0:
        expense_ratio = annual_expense / declared_income
        asset_income_ratio = asset_value / declared_income
    else:
        expense_ratio = float('inf')
        asset_income_ratio = float('inf')
    
    if expense_ratio > 2 or asset_income_ratio > 20:
        risk_level = "CRITICAL"
        risk_score = 95
        fraud_probability = 90
    elif expense_ratio > 1.5 or asset_income_ratio > 15:
        risk_level = "HIGH"
        risk_score = 75
        fraud_probability = 70
    elif expense_ratio > 1.2 or asset_income_ratio > 10:
        risk_level = "MODERATE"
        risk_score = 50
        fraud_probability = 45
    elif expense_ratio > 1 or asset_income_ratio > 5:
        risk_level = "LOW"
        risk_score = 25
        fraud_probability = 20
    else:
        risk_level = "NORMAL"
        risk_score = 10
        fraud_probability = 5
    
    income_gap = max(0, annual_expense - declared_income)
    unexplained_assets = max(0, asset_value - (declared_income * 5))
    
    indicators = []
    
    if expense_ratio > 1.2:
        indicators.append({
            "type": "expense_exceeds_income",
            "severity": "HIGH" if expense_ratio > 1.5 else "MEDIUM",
            "description": f"Annual expenses (₹{annual_expense:,.0f}) exceed {expense_ratio:.1f}x declared income"
        })
    
    if asset_income_ratio > 5:
        indicators.append({
            "type": "unexplained_assets",
            "severity": "HIGH" if asset_income_ratio > 10 else "MEDIUM",
            "description": f"Assets worth ₹{asset_value:,.0f} are {asset_income_ratio:.1f}x annual income"
        })
    
    if lifestyle_data.get("vehicle") in ["Four-wheeler (Luxury)", "Multiple Vehicles"]:
        if declared_income < 2000000:
            indicators.append({
                "type": "luxury_vehicle_mismatch",
                "severity": "HIGH",
                "description": "Luxury vehicles owned despite modest declared income"
            })
    
    if lifestyle_data.get("property") in ["Owned (Multiple Properties)", "Owned (Premium/Luxury)"]:
        if declared_income < 5000000:
            indicators.append({
                "type": "property_mismatch",
                "severity": "HIGH",
                "description": "Premium/multiple properties inconsistent with income"
            })
    
    if lifestyle_data.get("education") in ["International School", "Abroad Education"]:
        if declared_income < 3000000:
            indicators.append({
                "type": "education_expense_mismatch",
                "severity": "MEDIUM",
                "description": "High-cost education expenses despite moderate income"
            })
    
    return {
        "declared_income": declared_income,
        "estimated_annual_expense": annual_expense,
        "estimated_asset_value": asset_value,
        "expense_ratio": expense_ratio,
        "asset_income_ratio": asset_income_ratio,
        "income_gap": income_gap,
        "unexplained_assets": unexplained_assets,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "fraud_probability": fraud_probability,
        "indicators": indicators,
        "expense_breakdown": expense_profile["expense_breakdown"],
        "asset_breakdown": expense_profile["asset_breakdown"],
        "recommendation": get_lifestyle_recommendation(risk_level, indicators)
    }


def get_lifestyle_recommendation(risk_level: str, indicators: List[Dict]) -> str:
    if risk_level == "CRITICAL":
        return """URGENT ACTION REQUIRED:
1. Initiate detailed investigation under Section 131
2. Issue notice under Section 142(1) for wealth explanation
3. Consider provisional attachment under Section 281B
4. Coordinate with Enforcement Directorate if money laundering suspected
5. Request bank statements for last 5 years
6. Verify all property transactions"""
    
    elif risk_level == "HIGH":
        return """HIGH PRIORITY INVESTIGATION:
1. Issue notice under Section 142(1) requesting source of funds
2. Cross-verify with property registration records
3. Obtain vehicle registration and loan details
4. Request Form 26AS and bank statements
5. Verify GST returns if applicable
6. Consider surprise verification under Section 133A"""
    
    elif risk_level == "MODERATE":
        return """ENHANCED SCRUTINY RECOMMENDED:
1. Request supporting documents for major expenses
2. Cross-verify declared income with TDS records
3. Review bank transaction patterns
4. Check for related party transactions
5. Schedule for regular monitoring"""
    
    elif risk_level == "LOW":
        return """STANDARD VERIFICATION:
1. Routine document verification
2. Cross-check with employer records
3. Standard periodic monitoring
4. Update records if new information emerges"""
    
    else:
        return "No significant discrepancies. Routine monitoring sufficient."


def analyze_transaction_patterns(
    transactions: List[Dict],
    declared_monthly_income: float
) -> Dict:
    if not transactions:
        return {"analysis_available": False, "reason": "No transactions provided"}
    
    total_credits = sum(t.get("amount", 0) for t in transactions if t.get("type") == "credit")
    total_debits = sum(t.get("amount", 0) for t in transactions if t.get("type") == "debit")
    
    cash_deposits = [t for t in transactions if t.get("mode") == "cash" and t.get("type") == "credit"]
    cash_deposit_total = sum(t.get("amount", 0) for t in cash_deposits)
    
    round_transactions = [t for t in transactions if t.get("amount", 0) % 10000 == 0 and t.get("amount", 0) >= 50000]
    
    threshold_transactions = [t for t in transactions if 45000 <= t.get("amount", 0) <= 49999]
    
    just_below_10l = [t for t in transactions if 900000 <= t.get("amount", 0) <= 999999]
    
    red_flags = []
    risk_score = 0
    
    if declared_monthly_income > 0:
        months = max(1, len(set(t.get("date", "")[:7] for t in transactions)))
        monthly_credits = total_credits / months
        
        if monthly_credits > declared_monthly_income * 1.5:
            red_flags.append({
                "type": "excess_credits",
                "severity": "HIGH",
                "description": f"Monthly credits (₹{monthly_credits:,.0f}) exceed declared income by {(monthly_credits/declared_monthly_income - 1)*100:.0f}%"
            })
            risk_score += 30
    
    if cash_deposit_total > declared_monthly_income * 0.5:
        red_flags.append({
            "type": "high_cash_deposits",
            "severity": "HIGH",
            "description": f"High cash deposits (₹{cash_deposit_total:,.0f}) indicate potential unreported income"
        })
        risk_score += 25
    
    if len(threshold_transactions) >= 3:
        red_flags.append({
            "type": "structuring_suspected",
            "severity": "CRITICAL",
            "description": f"{len(threshold_transactions)} transactions just below ₹50,000 reporting threshold - structuring suspected"
        })
        risk_score += 40
    
    if just_below_10l:
        red_flags.append({
            "type": "10l_threshold_avoidance",
            "severity": "CRITICAL",
            "description": f"{len(just_below_10l)} transactions just below ₹10 lakh PAN reporting threshold"
        })
        risk_score += 35
    
    if len(round_transactions) > len(transactions) * 0.3:
        red_flags.append({
            "type": "round_figure_pattern",
            "severity": "MEDIUM",
            "description": "High proportion of round figure transactions may indicate layering"
        })
        risk_score += 15
    
    return {
        "analysis_available": True,
        "total_credits": total_credits,
        "total_debits": total_debits,
        "cash_deposit_total": cash_deposit_total,
        "transaction_count": len(transactions),
        "round_transaction_count": len(round_transactions),
        "threshold_transaction_count": len(threshold_transactions),
        "red_flags": red_flags,
        "risk_score": min(100, risk_score),
        "recommendation": get_transaction_recommendation(risk_score)
    }


def get_transaction_recommendation(risk_score: int) -> str:
    if risk_score >= 70:
        return "URGENT: File STR with FIU-IND. Initiate PMLA investigation. Request complete transaction history."
    elif risk_score >= 50:
        return "HIGH PRIORITY: Request source explanation for suspicious transactions. Cross-verify with ITR."
    elif risk_score >= 30:
        return "MODERATE: Enhanced monitoring. Request supporting documents for large transactions."
    else:
        return "LOW: Standard monitoring. Periodic review recommended."


def generate_behavioral_ai_analysis(
    vendor_data: Dict,
    lifestyle_data: Dict,
    transaction_summary: Optional[Dict] = None
) -> str:
    if not openai_client:
        return generate_fallback_behavioral_analysis(vendor_data, lifestyle_data, transaction_summary)
    
    try:
        prompt = f"""As a senior tax fraud investigator for the Income Tax Department of India, analyze the following case for potential fraud:

BUSINESS/VENDOR DATA:
{json.dumps(vendor_data, indent=2)}

LIFESTYLE INDICATORS:
{json.dumps(lifestyle_data, indent=2)}

{f"TRANSACTION PATTERNS: {json.dumps(transaction_summary, indent=2)}" if transaction_summary else ""}

Provide a comprehensive behavioral analysis including:
1. Income vs Lifestyle Assessment
2. Red Flags and Suspicious Patterns
3. Potential Fraud Schemes (consider front operations, cash layering, benami networks)
4. Recommended Investigation Steps
5. Applicable Legal Provisions under Income Tax Act
6. Risk Level and Priority

Focus on patterns specific to small vendors and street vendors who may be used as fronts for larger fraud operations."""

        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert tax fraud investigator specializing in detecting fraud by small vendors and street vendors in India. You understand how these businesses can be used for money laundering, cash layering, and as fronts for larger criminal operations."
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2048
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Behavioral AI analysis error: {e}")
        return generate_fallback_behavioral_analysis(vendor_data, lifestyle_data, transaction_summary)


def generate_fallback_behavioral_analysis(
    vendor_data: Dict,
    lifestyle_data: Dict,
    transaction_summary: Optional[Dict] = None
) -> str:
    lifestyle_result = analyze_income_lifestyle_gap(
        vendor_data.get("declared_revenue", 0),
        lifestyle_data
    )
    
    report = f"""## Behavioral Pattern Analysis Report

### Business Profile
- Type: {vendor_data.get('business_type', 'Not specified')}
- Declared Annual Income: ₹{vendor_data.get('declared_revenue', 0):,.0f}
- Years in Operation: {vendor_data.get('years_in_operation', 'Unknown')}

### Lifestyle vs Income Analysis
- Estimated Annual Expenses: ₹{lifestyle_result['estimated_annual_expense']:,.0f}
- Estimated Asset Value: ₹{lifestyle_result['estimated_asset_value']:,.0f}
- Expense to Income Ratio: {lifestyle_result['expense_ratio']:.2f}x
- Asset to Income Ratio: {lifestyle_result['asset_income_ratio']:.2f}x

### Risk Assessment
- Risk Level: {lifestyle_result['risk_level']}
- Risk Score: {lifestyle_result['risk_score']}/100
- Fraud Probability: {lifestyle_result['fraud_probability']}%

### Identified Indicators
"""
    
    for indicator in lifestyle_result['indicators']:
        report += f"- [{indicator['severity']}] {indicator['description']}\n"
    
    if not lifestyle_result['indicators']:
        report += "- No significant indicators identified\n"
    
    if transaction_summary and transaction_summary.get('analysis_available'):
        report += f"""
### Transaction Pattern Analysis
- Total Credits: ₹{transaction_summary.get('total_credits', 0):,.0f}
- Cash Deposits: ₹{transaction_summary.get('cash_deposit_total', 0):,.0f}
- Suspicious Transactions: {transaction_summary.get('threshold_transaction_count', 0)}
"""

    report += f"""
### Recommendation
{lifestyle_result['recommendation']}

### Disclaimer
This analysis is based on available behavioral data and should be verified through proper investigation procedures.

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report
