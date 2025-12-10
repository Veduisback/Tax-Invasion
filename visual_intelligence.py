import os
import json
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime

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


def analyze_vendor_stall_photo(image_base64: str, vendor_type: str = "Street Vendor") -> Dict:
    if not openai_client:
        return get_fallback_visual_analysis()
    
    try:
        prompt = f"""You are a tax fraud investigation expert analyzing a photo of a {vendor_type} stall/shop for the Income Tax Department of India.

Analyze this image and provide a detailed assessment in JSON format with the following:

1. "stall_size_estimate": Estimated size in square feet (number)
2. "stock_value_estimate": Estimated value of visible stock/inventory in INR (number)
3. "equipment_value": Estimated value of visible equipment/fixtures in INR (number)
4. "quality_tier": One of "basic", "standard", "premium", "luxury"
5. "customer_capacity": Estimated customers that can be served per hour (number)
6. "operating_indicators": List of visible items indicating operations (refrigerators, display cases, signage, etc.)
7. "hygiene_compliance": "poor", "average", "good", "excellent"
8. "location_type": Type of location (footpath, market, station area, mall, etc.)
9. "visible_employees": Estimated number of workers visible or needed
10. "daily_revenue_estimate": Based on setup and location, estimated daily revenue range in INR (object with "low" and "high")
11. "red_flags": List of any suspicious indicators (luxury items, excessive stock, branded items inconsistent with stall type, etc.)
12. "legitimacy_score": 0-100 score indicating how legitimate the operation appears
13. "notes": Any additional observations relevant to fraud investigation

Be thorough and look for discrepancies between the apparent business type and any visible wealth indicators."""

        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert tax fraud investigator specializing in visual analysis of business premises for the Income Tax Department of India. You can estimate business value, stock levels, and detect anomalies that might indicate tax fraud or money laundering."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                        }
                    ]
                }
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2048
        )
        
        result = json.loads(response.choices[0].message.content)
        result["analysis_timestamp"] = datetime.now().isoformat()
        result["analysis_type"] = "visual_ai"
        return result
        
    except Exception as e:
        print(f"Visual analysis error: {e}")
        return get_fallback_visual_analysis()


def get_fallback_visual_analysis() -> Dict:
    return {
        "stall_size_estimate": 0,
        "stock_value_estimate": 0,
        "equipment_value": 0,
        "quality_tier": "unknown",
        "customer_capacity": 0,
        "operating_indicators": [],
        "hygiene_compliance": "unknown",
        "location_type": "unknown",
        "visible_employees": 0,
        "daily_revenue_estimate": {"low": 0, "high": 0},
        "red_flags": [],
        "legitimacy_score": 50,
        "notes": "Visual analysis unavailable - AI service not configured",
        "analysis_timestamp": datetime.now().isoformat(),
        "analysis_type": "fallback"
    }


def analyze_lifestyle_photos(photos_base64: List[str], context: str = "") -> Dict:
    if not openai_client or not photos_base64:
        return get_fallback_lifestyle_analysis()
    
    try:
        content = [
            {
                "type": "text",
                "text": f"""You are investigating potential tax fraud for the Income Tax Department of India. 
                
Analyze these photos for lifestyle indicators that might not match declared income.
Context: {context if context else "Photos of person/property related to tax investigation"}

Provide analysis in JSON format:
1. "vehicle_assessment": Object with "type", "estimated_value", "count"
2. "property_assessment": Object with "type", "estimated_value", "location_tier"
3. "jewelry_visible": Object with "items_seen", "estimated_value"
4. "luxury_items": List of luxury items visible with estimated values
5. "clothing_brands": Assessment of visible clothing/accessories quality
6. "lifestyle_tier": "modest", "middle_class", "upper_middle", "affluent", "luxury"
7. "estimated_monthly_expense": Based on lifestyle indicators
8. "minimum_income_required": Estimated minimum annual income to support this lifestyle
9. "red_flags": List of items inconsistent with modest income claims
10. "overall_assessment": Summary of findings"""
            }
        ]
        
        for i, photo in enumerate(photos_base64[:5]):
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{photo}"}
            })
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert tax fraud investigator who analyzes lifestyle indicators to detect income discrepancies. You are skilled at estimating property values, vehicle costs, and lifestyle expenses in the Indian context."
                },
                {"role": "user", "content": content}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=2048
        )
        
        result = json.loads(response.choices[0].message.content)
        result["analysis_timestamp"] = datetime.now().isoformat()
        result["photos_analyzed"] = len(photos_base64[:5])
        return result
        
    except Exception as e:
        print(f"Lifestyle analysis error: {e}")
        return get_fallback_lifestyle_analysis()


def get_fallback_lifestyle_analysis() -> Dict:
    return {
        "vehicle_assessment": {"type": "unknown", "estimated_value": 0, "count": 0},
        "property_assessment": {"type": "unknown", "estimated_value": 0, "location_tier": "unknown"},
        "jewelry_visible": {"items_seen": [], "estimated_value": 0},
        "luxury_items": [],
        "clothing_brands": "unknown",
        "lifestyle_tier": "unknown",
        "estimated_monthly_expense": 0,
        "minimum_income_required": 0,
        "red_flags": [],
        "overall_assessment": "Analysis unavailable - AI service not configured",
        "analysis_timestamp": datetime.now().isoformat(),
        "photos_analyzed": 0
    }


def compare_declared_vs_visual(
    declared_data: Dict,
    visual_analysis: Dict
) -> Dict:
    discrepancies = []
    risk_score = 0
    
    if visual_analysis.get("stall_size_estimate", 0) > 0:
        declared_area = declared_data.get("total_land_sqft", 0)
        visual_area = visual_analysis.get("stall_size_estimate", 0)
        
        if declared_area > 0:
            area_diff = abs(visual_area - declared_area) / max(declared_area, 1) * 100
            if area_diff > 50:
                discrepancies.append({
                    "type": "area_mismatch",
                    "declared": declared_area,
                    "visual": visual_area,
                    "difference_percent": area_diff,
                    "severity": "HIGH" if area_diff > 100 else "MEDIUM"
                })
                risk_score += 20 if area_diff > 100 else 10
    
    if visual_analysis.get("stock_value_estimate", 0) > 0:
        declared_revenue = declared_data.get("declared_revenue", 0)
        stock_value = visual_analysis.get("stock_value_estimate", 0)
        
        expected_stock = declared_revenue * 0.1
        if stock_value > expected_stock * 3:
            discrepancies.append({
                "type": "excessive_stock",
                "expected_stock": expected_stock,
                "visual_stock": stock_value,
                "description": "Stock value significantly exceeds what's expected for declared revenue",
                "severity": "HIGH"
            })
            risk_score += 25
        elif stock_value < expected_stock * 0.1 and declared_revenue > 500000:
            discrepancies.append({
                "type": "low_stock",
                "expected_stock": expected_stock,
                "visual_stock": stock_value,
                "description": "Visible stock too low for claimed revenue - possible shell operation",
                "severity": "HIGH"
            })
            risk_score += 30
    
    daily_estimate = visual_analysis.get("daily_revenue_estimate", {})
    if daily_estimate.get("high", 0) > 0:
        visual_annual = daily_estimate.get("high", 0) * 300
        declared_annual = declared_data.get("declared_revenue", 0)
        
        if declared_annual > visual_annual * 3:
            discrepancies.append({
                "type": "inflated_revenue",
                "visual_estimate": visual_annual,
                "declared": declared_annual,
                "description": "Declared revenue seems too high for visible business capacity",
                "severity": "HIGH"
            })
            risk_score += 25
        elif visual_annual > declared_annual * 2 and declared_annual > 0:
            discrepancies.append({
                "type": "under_reported_revenue",
                "visual_estimate": visual_annual,
                "declared": declared_annual,
                "description": "Business appears capable of generating more revenue than declared",
                "severity": "MEDIUM"
            })
            risk_score += 15
    
    red_flags = visual_analysis.get("red_flags", [])
    if red_flags:
        for flag in red_flags:
            discrepancies.append({
                "type": "visual_red_flag",
                "description": flag,
                "severity": "MEDIUM"
            })
            risk_score += 5
    
    if visual_analysis.get("quality_tier") == "luxury" and declared_data.get("declared_revenue", 0) < 2000000:
        discrepancies.append({
            "type": "quality_income_mismatch",
            "description": "Luxury quality setup inconsistent with modest declared income",
            "severity": "HIGH"
        })
        risk_score += 20
    
    legitimacy = visual_analysis.get("legitimacy_score", 50)
    if legitimacy < 40:
        risk_score += 25
    elif legitimacy < 60:
        risk_score += 10
    
    return {
        "discrepancies": discrepancies,
        "risk_score": min(100, risk_score),
        "visual_legitimacy_score": legitimacy,
        "recommendation": get_visual_recommendation(risk_score, discrepancies),
        "analysis_timestamp": datetime.now().isoformat()
    }


def get_visual_recommendation(risk_score: int, discrepancies: List[Dict]) -> str:
    if risk_score >= 70:
        return "URGENT: Major discrepancies detected. Recommend immediate field verification and detailed investigation under Section 133A."
    elif risk_score >= 50:
        return "HIGH PRIORITY: Significant discrepancies found. Schedule detailed physical verification and request supporting documents."
    elif risk_score >= 30:
        return "MODERATE: Some discrepancies noted. Cross-verify with bank statements and GST returns."
    elif risk_score >= 15:
        return "LOW: Minor discrepancies. Standard periodic monitoring recommended."
    else:
        return "MINIMAL: Visual analysis consistent with declarations. Routine verification sufficient."


def analyze_transaction_receipts(receipt_images: List[str]) -> Dict:
    if not openai_client or not receipt_images:
        return {"receipts": [], "total_amount": 0, "analysis_available": False}
    
    try:
        receipts_data = []
        total_amount = 0
        
        for receipt_base64 in receipt_images[:10]:
            response = openai_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "Extract transaction details from receipts. Return JSON with: date, vendor_name, amount, payment_method, items (if visible), any suspicious indicators."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extract transaction details from this receipt:"},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{receipt_base64}"}
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_completion_tokens=1024
            )
            
            receipt_data = json.loads(response.choices[0].message.content)
            receipts_data.append(receipt_data)
            total_amount += receipt_data.get("amount", 0)
        
        return {
            "receipts": receipts_data,
            "total_amount": total_amount,
            "receipt_count": len(receipts_data),
            "analysis_available": True,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Receipt analysis error: {e}")
        return {"receipts": [], "total_amount": 0, "analysis_available": False}


def generate_visual_fraud_report(
    vendor_data: Dict,
    visual_analysis: Dict,
    lifestyle_analysis: Optional[Dict] = None,
    comparison_result: Optional[Dict] = None
) -> str:
    if not openai_client:
        return generate_fallback_visual_report(vendor_data, visual_analysis, comparison_result)
    
    try:
        prompt = f"""Generate a professional fraud investigation report based on visual intelligence analysis.

VENDOR DATA:
{json.dumps(vendor_data, indent=2)}

VISUAL ANALYSIS:
{json.dumps(visual_analysis, indent=2)}

{f"LIFESTYLE ANALYSIS: {json.dumps(lifestyle_analysis, indent=2)}" if lifestyle_analysis else ""}

{f"COMPARISON RESULT: {json.dumps(comparison_result, indent=2)}" if comparison_result else ""}

Generate a professional report including:
1. Executive Summary
2. Visual Evidence Analysis
3. Discrepancy Assessment
4. Risk Indicators
5. Recommended Actions under Income Tax Act
6. Supporting Legal Provisions

Format as a professional document suitable for official use."""

        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior tax fraud investigator preparing official reports for the Income Tax Department of India. Your reports are professional, legally sound, and actionable."
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2048
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Report generation error: {e}")
        return generate_fallback_visual_report(vendor_data, visual_analysis, comparison_result)


def generate_fallback_visual_report(
    vendor_data: Dict,
    visual_analysis: Dict,
    comparison_result: Optional[Dict] = None
) -> str:
    report = f"""## Visual Intelligence Fraud Assessment Report

### Executive Summary
This report presents findings from visual analysis of business premises for potential tax fraud indicators.

### Business Details
- Business Type: {vendor_data.get('business_type', 'Not specified')}
- Declared Revenue: ₹{vendor_data.get('declared_revenue', 0):,.0f}
- Location: {vendor_data.get('region', 'Not specified')}

### Visual Analysis Findings
- Estimated Stall Size: {visual_analysis.get('stall_size_estimate', 'N/A')} sq ft
- Stock Value Estimate: ₹{visual_analysis.get('stock_value_estimate', 0):,.0f}
- Quality Tier: {visual_analysis.get('quality_tier', 'Unknown')}
- Legitimacy Score: {visual_analysis.get('legitimacy_score', 'N/A')}/100

### Red Flags Identified
"""
    
    red_flags = visual_analysis.get('red_flags', [])
    if red_flags:
        for flag in red_flags:
            report += f"- {flag}\n"
    else:
        report += "- No significant red flags identified\n"
    
    if comparison_result:
        report += f"""
### Discrepancy Analysis
- Overall Risk Score: {comparison_result.get('risk_score', 0)}/100
- Number of Discrepancies: {len(comparison_result.get('discrepancies', []))}

### Recommendation
{comparison_result.get('recommendation', 'Standard monitoring recommended')}
"""
    
    report += f"""
### Disclaimer
This report is based on AI-powered visual analysis and should be used as a preliminary screening tool. 
All findings require verification through proper investigative procedures under the Income Tax Act, 1961.

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report
