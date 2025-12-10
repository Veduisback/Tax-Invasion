import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if OPENAI_AVAILABLE and OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

if ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
else:
    anthropic_client = None

if GEMINI_AVAILABLE and GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None


def get_ai_status() -> Dict[str, bool]:
    return {
        "openai": openai_client is not None,
        "anthropic": anthropic_client is not None,
        "gemini": gemini_client is not None,
        "any_available": any([openai_client, anthropic_client, gemini_client])
    }


def generate_openai_analysis(prompt: str, system_prompt: str) -> Optional[str]:
    if not openai_client:
        return None
    try:
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI Error: {e}")
        return None


def generate_anthropic_analysis(prompt: str, system_prompt: str) -> Optional[str]:
    if not anthropic_client:
        return None
    try:
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    except Exception as e:
        print(f"Anthropic Error: {e}")
        return None


def generate_gemini_analysis(prompt: str, system_prompt: str) -> Optional[str]:
    if not gemini_client:
        return None
    try:
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=full_prompt
        )
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return None


def generate_multi_ai_ensemble_analysis(
    business_data: Dict,
    detection_result: Dict
) -> Dict[str, Any]:
    matched_patterns = detection_result.get('matched_fraud_patterns', [])
    pattern_str = ""
    if matched_patterns:
        pattern_str = "\n\nMATCHED FRAUD PATTERNS:\n"
        for p in matched_patterns:
            pattern_str += f"- {p['type']} (Score: {p['score']}%)\n"
            for ind in p.get('indicators', []):
                pattern_str += f"  - {ind}\n"
    
    similar_cases = detection_result.get('similar_cases', [])
    cases_str = ""
    if similar_cases:
        cases_str = "\n\nSIMILAR HISTORICAL FRAUD CASES:\n"
        for c in similar_cases[:3]:
            cases_str += f"- {c['name']} ({c['year']}): Rs.{c['amount_crore']} crore - {c['fraud_type']}\n"
            cases_str += f"  Detection Method: {c['detection_method']}\n"
    
    is_small_vendor = detection_result.get('is_small_vendor', False)
    vendor_context = ""
    if is_small_vendor:
        vendor_context = """
SPECIAL CONTEXT - SMALL VENDOR ANALYSIS:
This is a small vendor/street vendor analysis. Focus on:
- Front operation indicators (small vendor used as cash layering point)
- Lifestyle vs income discrepancies
- Network connections to larger businesses
- Cash transaction patterns
- Visual analysis findings if available
"""
    
    prompt = f"""You are a senior tax fraud investigation expert with the Income Tax Department of India. Analyze the following business data and fraud detection results to provide expert insights.

{vendor_context}

BUSINESS INFORMATION:
- Business Type: {business_data['business_type']}
- Number of Outlets/Offices: {business_data['num_outlets']}
- Total Land Area: {business_data['total_land_sqft']:,.0f} sq ft
- Region: {business_data['region']}
- Land Rate: Rs.{business_data['land_rate_per_sqft']:,.0f}/sq ft
- Total Land Value: Rs.{business_data['total_land_sqft'] * business_data['land_rate_per_sqft']:,.0f}
- Electricity Consumption: {business_data['electricity_consumption_kwh']:,.0f} kWh
- Declared Annual Revenue: Rs.{business_data['declared_revenue']:,.0f}
- Declared Tax Paid: Rs.{business_data['declared_tax_paid']:,.0f}
- Number of Employees: {business_data['num_employees']}
- Stock Market Listed: {'Yes' if business_data['is_stock_listed'] else 'No'}
- Market Cap (if listed): Rs.{business_data.get('stock_market_cap', 0):,.0f}
- Connection with Business Tycoons: {business_data['tycoon_connection_level']}
- Years in Operation: {business_data.get('years_in_operation', 'Unknown')}
- Additional Notes: {business_data.get('additional_notes', 'None provided')}

FRAUD DETECTION RESULTS:
- Fraud Probability: {detection_result['fraud_probability']}%
- Risk Level: {detection_result['risk_level']}
- Number of Risk Factors Identified: {len(detection_result['risk_factors'])}

TOP RISK FACTORS:
{chr(10).join([f"- {rf['factor']} (Severity: {rf['severity']}): {rf['description']}" for rf in detection_result['risk_factors'][:5]])}
{pattern_str}
{cases_str}

Based on your expertise in Indian tax fraud investigations, provide:
1. A concise executive summary of the fraud risk assessment
2. Specific red flags that warrant immediate attention
3. Recommended investigation steps for the Income Tax Department
4. Potential fraud schemes this business pattern might indicate
5. Legal provisions under Income Tax Act that may apply
6. Any mitigating factors that might explain the anomalies legitimately

Keep your analysis professional, actionable, and focused on helping tax investigators prioritize their efforts."""

    system_prompt = """You are an expert tax fraud investigator with the Income Tax Department of India. You have decades of experience in detecting financial crimes, shell companies, money laundering, and black money operations. You are familiar with major Indian fraud cases and use pattern matching to identify similar frauds. Provide detailed, professional analysis with specific legal references to Indian tax law."""
    
    analyses = {}
    confidence_scores = {}
    
    openai_result = generate_openai_analysis(prompt, system_prompt)
    if openai_result:
        analyses["openai"] = openai_result
        confidence_scores["openai"] = 0.9
    
    anthropic_result = generate_anthropic_analysis(prompt, system_prompt)
    if anthropic_result:
        analyses["anthropic"] = anthropic_result
        confidence_scores["anthropic"] = 0.85
    
    gemini_result = generate_gemini_analysis(prompt, system_prompt)
    if gemini_result:
        analyses["gemini"] = gemini_result
        confidence_scores["gemini"] = 0.8
    
    if not analyses:
        return {
            "ensemble_analysis": generate_fallback_analysis(business_data, detection_result),
            "individual_analyses": {},
            "consensus_score": 0,
            "ai_models_used": [],
            "confidence_scores": {}
        }
    
    consensus_score = calculate_consensus_score(analyses, detection_result, confidence_scores)
    
    ensemble_analysis = generate_consensus_summary(analyses, consensus_score, detection_result)
    
    return {
        "ensemble_analysis": ensemble_analysis,
        "individual_analyses": analyses,
        "consensus_score": consensus_score,
        "ai_models_used": list(analyses.keys()),
        "confidence_scores": confidence_scores,
        "analysis_timestamp": datetime.now().isoformat()
    }


def calculate_consensus_score(analyses: Dict[str, str], detection_result: Dict, confidence_scores: Dict[str, float] = None) -> float:
    base_score = detection_result.get('fraud_probability', 50)
    
    if confidence_scores is None:
        confidence_scores = {"openai": 0.9, "anthropic": 0.85, "gemini": 0.8}
    
    high_risk_keywords = ['critical', 'urgent', 'immediate', 'serious', 'high risk', 'very high', 'shell company', 'money laundering', 'fraud', 'investigation required', 'section 132']
    medium_risk_keywords = ['moderate', 'review', 'scrutiny', 'verification', 'anomaly', 'enhanced monitoring']
    low_risk_keywords = ['low risk', 'routine', 'standard', 'normal', 'minimal', 'no immediate', 'standard monitoring']
    
    weighted_risk_scores = []
    total_weight = 0
    
    for model, analysis in analyses.items():
        analysis_lower = analysis.lower()
        model_weight = confidence_scores.get(model, 0.7)
        
        high_count = sum(1 for kw in high_risk_keywords if kw in analysis_lower)
        medium_count = sum(1 for kw in medium_risk_keywords if kw in analysis_lower)
        low_count = sum(1 for kw in low_risk_keywords if kw in analysis_lower)
        
        if high_count > medium_count and high_count > low_count:
            model_risk_assessment = 85
        elif low_count > high_count and low_count > medium_count:
            model_risk_assessment = 25
        elif medium_count > high_count:
            model_risk_assessment = 50
        else:
            model_risk_assessment = base_score
        
        weighted_risk_scores.append(model_risk_assessment * model_weight)
        total_weight += model_weight
    
    if weighted_risk_scores and total_weight > 0:
        weighted_avg = sum(weighted_risk_scores) / total_weight
        consensus_score = (base_score * 0.4) + (weighted_avg * 0.6)
    else:
        consensus_score = base_score
    
    model_count = len(analyses)
    if model_count >= 3:
        agreement_bonus = 5
    elif model_count >= 2:
        agreement_bonus = 3
    else:
        agreement_bonus = 0
    
    consensus_score = min(100, max(0, consensus_score + agreement_bonus))
    
    return round(consensus_score, 1)


def generate_consensus_summary(analyses: Dict[str, str], consensus_score: float, detection_result: Dict) -> str:
    model_count = len(analyses)
    model_names = {
        "openai": "GPT-5",
        "anthropic": "Claude",
        "gemini": "Gemini"
    }
    
    used_models = [model_names.get(m, m) for m in analyses.keys()]
    
    summary = f"""## Multi-AI Ensemble Fraud Analysis Report

### AI Models Used: {', '.join(used_models)}
### Consensus Risk Score: {consensus_score}%
### ML Detection Score: {detection_result.get('fraud_probability', 0)}%

---

"""
    
    if consensus_score >= 80:
        risk_assessment = "CRITICAL - Multiple AI models agree on severe fraud indicators"
    elif consensus_score >= 60:
        risk_assessment = "HIGH - Strong consensus on significant fraud risk"
    elif consensus_score >= 40:
        risk_assessment = "MODERATE - Mixed signals requiring further investigation"
    elif consensus_score >= 20:
        risk_assessment = "LOW - AI models find limited fraud indicators"
    else:
        risk_assessment = "MINIMAL - Consensus suggests legitimate operation"
    
    summary += f"### Risk Assessment: {risk_assessment}\n\n---\n\n"
    
    for model, analysis in analyses.items():
        summary += f"### {model_names.get(model, model)} Analysis\n\n{analysis}\n\n---\n\n"
    
    summary += f"""
### Ensemble Recommendation

Based on consensus analysis from {model_count} AI model(s):

"""
    
    if consensus_score >= 80:
        summary += """- **URGENT ACTION REQUIRED**
- Coordinate multi-agency investigation immediately
- Consider search and seizure under Section 132
- Notify ED/FIU if money laundering suspected
- Engage forensic accountants
"""
    elif consensus_score >= 60:
        summary += """- **PRIORITY INVESTIGATION**
- Initiate detailed audit under Section 142(2A)
- Request comprehensive financial records
- Cross-verify with bank statements and GST returns
- Schedule field verification
"""
    elif consensus_score >= 40:
        summary += """- **ENHANCED SCRUTINY**
- Request additional documentation
- Cross-reference with TDS records
- Monitor for additional red flags
- Schedule periodic review
"""
    else:
        summary += """- **STANDARD MONITORING**
- Routine verification sufficient
- Maintain periodic audit schedule
- Update records if new information emerges
"""
    
    summary += f"""
---

*Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using {model_count} AI model(s)*
"""
    
    return summary


def generate_ai_fraud_analysis(
    business_data: Dict,
    detection_result: Dict
) -> Optional[str]:
    ensemble_result = generate_multi_ai_ensemble_analysis(business_data, detection_result)
    return ensemble_result.get('ensemble_analysis', generate_fallback_analysis(business_data, detection_result))


def generate_fallback_analysis(
    business_data: Dict,
    detection_result: Dict
) -> str:
    risk_level = detection_result['risk_level']
    probability = detection_result['fraud_probability']
    risk_factors = detection_result['risk_factors']
    matched_patterns = detection_result.get('matched_fraud_patterns', [])
    similar_cases = detection_result.get('similar_cases', [])
    
    analysis = f"""## Expert Fraud Risk Assessment

### Executive Summary
This {business_data['business_type']} has been assessed with a **{risk_level}** fraud risk level, with an estimated **{probability}%** probability of tax irregularities based on the submitted data and pattern matching against known fraud cases.

### Key Findings
"""
    
    if len(risk_factors) > 0:
        analysis += "\n**Primary Concerns:**\n"
        for i, rf in enumerate(risk_factors[:5], 1):
            analysis += f"{i}. **{rf['factor']}** ({rf['severity']} Severity)\n   - {rf['description']}\n"
    else:
        analysis += "\nNo significant anomalies detected in the submitted data.\n"
    
    if matched_patterns:
        analysis += "\n### Matched Fraud Patterns\n"
        for p in matched_patterns:
            analysis += f"\n**{p['type']}** (Confidence: {p['score']}%)\n"
            for ind in p.get('indicators', []):
                analysis += f"- {ind}\n"
    
    if similar_cases:
        analysis += "\n### Similar Historical Cases\n"
        analysis += "This case shows patterns similar to these major Indian fraud cases:\n"
        for c in similar_cases[:3]:
            analysis += f"\n**{c['name']}** ({c['year']}) - Rs.{c['amount_crore']:,} Crore\n"
            analysis += f"- Fraud Type: {c['fraud_type']}\n"
            analysis += f"- How it was caught: {c['detection_method']}\n"
    
    analysis += f"""
### Recommended Actions

"""
    
    if probability < 20:
        analysis += """- Standard periodic monitoring is sufficient
- No immediate investigation required
- Maintain regular audit schedule
- File for routine verification under Section 143(1)
"""
    elif probability < 40:
        analysis += """- Request additional documentation for verification
- Cross-verify with GST returns and bank statements
- Schedule enhanced review within 60 days
- Consider issuing notice under Section 142(1)
"""
    elif probability < 60:
        analysis += """- Initiate preliminary investigation under Section 131
- Request comprehensive financial statements (last 3 years)
- Verify all declared assets and liabilities
- Cross-reference with TDS returns and Form 26AS
- Interview key personnel if warranted
"""
    elif probability < 80:
        analysis += """- Immediate detailed audit required under Section 142(2A)
- Request complete bank statements and transaction records
- Coordinate with Financial Intelligence Unit (FIU)
- Consider provisional attachment under Section 281B
- Issue summons to directors/key personnel
"""
    else:
        analysis += """- URGENT: Coordinate multi-agency investigation
- Implement immediate asset freezing under Benami Transactions Act
- Conduct surprise search and seizure under Section 132
- Engage forensic accountants
- Notify ED, CBI, and SFIO as applicable
- Consider prosecution under Section 276C
"""
    
    analysis += """
### Applicable Legal Provisions
- **Section 132**: Search and Seizure
- **Section 133A**: Power to Survey
- **Section 142(2A)**: Special Audit
- **Section 276C**: Willful Tax Evasion (Prosecution)
- **Prevention of Money Laundering Act (PMLA)**: If money laundering suspected
- **Benami Transactions (Prohibition) Act**: For benami property cases

### Disclaimer
This assessment is based on statistical analysis and pattern matching against benchmark data and historical fraud cases. It should be used as a preliminary screening tool to prioritize investigations, not as definitive proof of wrongdoing.
"""
    
    return analysis


def analyze_news_for_fraud_patterns(article_content: str) -> Dict:
    if not openai_client:
        return {"patterns": [], "fraud_types": [], "entities": []}
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at analyzing news articles about tax fraud, money laundering, and financial crimes in India. 
                    Extract key information and return a JSON object with:
                    - patterns: list of fraud detection patterns/methods mentioned
                    - fraud_types: list of fraud types mentioned
                    - entities: list of companies/individuals mentioned
                    - amount: estimated fraud amount in crores (if mentioned)
                    - detection_method: how the fraud was detected
                    - key_indicators: list of red flags mentioned"""
                },
                {"role": "user", "content": f"Analyze this article for fraud patterns:\n\n{article_content[:4000]}"}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=1024
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"News analysis error: {e}")
        return {"patterns": [], "fraud_types": [], "entities": []}


def get_investigation_checklist(risk_level: str, matched_patterns: List[Dict] = None) -> list:
    base_checklist = [
        "Verify business registration (ROC/MCA records)",
        "Cross-check declared revenue with GST returns",
        "Verify employee count with PF/ESI records",
        "Obtain Form 26AS and verify TDS credits"
    ]
    
    if risk_level in ["MODERATE", "HIGH", "VERY HIGH", "CRITICAL"]:
        base_checklist.extend([
            "Request bank statements for last 3 years",
            "Verify land ownership documents with Sub-Registrar",
            "Check for related party transactions",
            "Analyze electricity bills vs production capacity",
            "Verify with local municipal records"
        ])
    
    if risk_level in ["HIGH", "VERY HIGH", "CRITICAL"]:
        base_checklist.extend([
            "Conduct surprise physical verification (Section 133A)",
            "Interview key management personnel",
            "Trace fund flows to related entities",
            "Check for overseas transactions and accounts",
            "Obtain information from FIU-IND",
            "Verify directors' other company associations"
        ])
    
    if risk_level in ["VERY HIGH", "CRITICAL"]:
        base_checklist.extend([
            "Coordinate with Enforcement Directorate",
            "Request international information exchange (DTAA)",
            "Engage forensic accountants",
            "Consider provisional attachment under Section 281B",
            "Prepare case for search under Section 132",
            "Check FATCA/CRS information for foreign assets"
        ])
    
    if matched_patterns:
        pattern_types = [p['type'] for p in matched_patterns]
        
        if "Shell Company" in pattern_types:
            base_checklist.extend([
                "Verify physical existence of business premises",
                "Check if registered address is shared office",
                "Verify genuineness of business transactions",
                "Check for common directors in other shell entities"
            ])
        
        if "Money Laundering" in pattern_types:
            base_checklist.extend([
                "File STR with FIU if not already done",
                "Trace source of funds for large transactions",
                "Check for cash deposits in round figures",
                "Verify KYC of major customers/suppliers"
            ])
        
        if "Circular Trading" in pattern_types:
            base_checklist.extend([
                "Verify physical movement of goods (e-way bills)",
                "Check for circular invoice patterns",
                "Verify ITC claims with supplier returns",
                "Coordinate with GST Intelligence"
            ])
        
        if "Front Operation" in pattern_types:
            base_checklist.extend([
                "Conduct surprise visit to verify operations",
                "Compare visual assessment with declared income",
                "Check for connections to larger businesses",
                "Verify lifestyle indicators against income"
            ])
        
        if "Cash Layering" in pattern_types:
            base_checklist.extend([
                "Analyze all bank accounts for patterns",
                "Check for structured transactions",
                "Verify source of cash deposits",
                "Cross-reference with other vendors in area"
            ])
    
    return base_checklist


def generate_small_vendor_ai_analysis(
    vendor_data: Dict,
    visual_analysis: Dict = None,
    lifestyle_analysis: Dict = None,
    network_analysis: Dict = None
) -> str:
    system_prompt = "You are an expert in detecting fraud through small vendors and street vendors in India. You understand how these businesses are exploited for money laundering, tax evasion, and as fronts for larger criminal operations."
    
    prompt = f"""As a senior tax fraud investigator specializing in small vendor and street vendor fraud in India, analyze the following case:

VENDOR DATA:
{json.dumps(vendor_data, indent=2)}

{f"VISUAL ANALYSIS: {json.dumps(visual_analysis, indent=2)}" if visual_analysis else ""}

{f"LIFESTYLE ANALYSIS: {json.dumps(lifestyle_analysis, indent=2)}" if lifestyle_analysis else ""}

{f"NETWORK ANALYSIS: {json.dumps(network_analysis, indent=2)}" if network_analysis else ""}

Provide comprehensive analysis including:
1. Executive Summary
2. Front Operation Assessment - Is this vendor a front for larger operations?
3. Lifestyle vs Income Gap Analysis
4. Network Risk Assessment
5. Visual Evidence Evaluation
6. Recommended Investigation Steps
7. Legal Provisions Applicable
8. Priority Level and Urgency

Focus on patterns specific to small vendors used for:
- Cash layering from real estate/gold businesses
- Hawala operations
- GST fraud networks
- Benami property connections"""
    
    analyses = []
    
    openai_result = generate_openai_analysis(prompt, system_prompt)
    if openai_result:
        analyses.append(("GPT-5", openai_result))
    
    anthropic_result = generate_anthropic_analysis(prompt, system_prompt)
    if anthropic_result:
        analyses.append(("Claude", anthropic_result))
    
    gemini_result = generate_gemini_analysis(prompt, system_prompt)
    if gemini_result:
        analyses.append(("Gemini", gemini_result))
    
    if not analyses:
        return generate_small_vendor_fallback(vendor_data, visual_analysis, lifestyle_analysis, network_analysis)
    
    combined = f"""## Multi-AI Small Vendor Fraud Analysis

### AI Models Used: {', '.join([a[0] for a in analyses])}

---

"""
    
    for model_name, analysis in analyses:
        combined += f"### {model_name} Analysis\n\n{analysis}\n\n---\n\n"
    
    combined += f"""
*Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} using {len(analyses)} AI model(s)*
"""
    
    return combined


def generate_small_vendor_fallback(
    vendor_data: Dict,
    visual_analysis: Dict = None,
    lifestyle_analysis: Dict = None,
    network_analysis: Dict = None
) -> str:
    report = f"""## Small Vendor Fraud Assessment Report

### Vendor Profile
- Type: {vendor_data.get('business_type', 'Unknown')}
- Name: {vendor_data.get('business_name', 'Not specified')}
- Declared Revenue: Rs.{vendor_data.get('declared_revenue', 0):,.0f}
- Location: {vendor_data.get('region', 'Not specified')}

### Risk Assessment Summary
"""
    
    risk_score = 0
    indicators = []
    
    if visual_analysis:
        legitimacy = visual_analysis.get('legitimacy_score', 50)
        if legitimacy < 50:
            risk_score += 30
            indicators.append(f"Low visual legitimacy score ({legitimacy}/100)")
        report += f"\n**Visual Analysis**: Legitimacy Score {legitimacy}/100\n"
    
    if lifestyle_analysis:
        lifestyle_risk = lifestyle_analysis.get('risk_score', 0)
        risk_score += lifestyle_risk * 0.3
        if lifestyle_risk > 50:
            indicators.append(f"High lifestyle vs income gap (Risk: {lifestyle_risk}%)")
        report += f"\n**Lifestyle Analysis**: Risk Score {lifestyle_risk}/100\n"
    
    if network_analysis:
        network_risk = network_analysis.get('network_risk_score', 0)
        risk_score += network_risk * 0.3
        if network_risk > 50:
            indicators.append(f"Suspicious network connections (Risk: {network_risk}%)")
        report += f"\n**Network Analysis**: Risk Score {network_risk}/100\n"
    
    if risk_score >= 70:
        risk_level = "CRITICAL"
    elif risk_score >= 50:
        risk_level = "HIGH"
    elif risk_score >= 30:
        risk_level = "MODERATE"
    else:
        risk_level = "LOW"
    
    report += f"""
### Overall Risk Level: {risk_level} ({risk_score:.0f}/100)

### Key Indicators
"""
    
    for ind in indicators:
        report += f"- {ind}\n"
    
    if not indicators:
        report += "- No significant fraud indicators detected\n"
    
    report += """
### Recommended Actions
"""
    
    if risk_level == "CRITICAL":
        report += "- Immediate field investigation required\n- Coordinate with ED/FIU\n- Consider search operations\n"
    elif risk_level == "HIGH":
        report += "- Priority field verification\n- Request bank statements\n- Cross-verify with GST\n"
    elif risk_level == "MODERATE":
        report += "- Schedule verification visit\n- Request supporting documents\n"
    else:
        report += "- Standard monitoring\n- Periodic review\n"
    
    return report
