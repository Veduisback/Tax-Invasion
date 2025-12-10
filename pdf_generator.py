import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from typing import Dict, Any, List


def generate_fraud_report_pdf(business_data: Dict, result: Dict, business_name: str = None) -> bytes:
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E3A5F'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1E3A5F'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    elements = []
    
    elements.append(Paragraph("INCOME TAX DEPARTMENT", subtitle_style))
    elements.append(Paragraph("Tax Fraud Detection Report", title_style))
    elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    elements.append(Paragraph("CONFIDENTIAL - FOR OFFICIAL USE ONLY", 
                             ParagraphStyle('Confidential', parent=normal_style, textColor=colors.red, alignment=TA_CENTER)))
    
    if business_name:
        elements.append(Paragraph(f"<b>Business Under Investigation:</b> {business_name}", normal_style))
    
    is_small_vendor = result.get('is_small_vendor', False)
    if is_small_vendor:
        elements.append(Paragraph("<b>Analysis Type:</b> Small Vendor / Street Vendor Investigation", normal_style))
    
    elements.append(Spacer(1, 20))
    
    risk_colors = {
        "LOW": colors.HexColor('#28a745'),
        "MODERATE": colors.HexColor('#ffc107'),
        "HIGH": colors.HexColor('#fd7e14'),
        "VERY HIGH": colors.HexColor('#dc3545'),
        "CRITICAL": colors.HexColor('#721c24')
    }
    
    risk_color = risk_colors.get(result['risk_level'], colors.grey)
    
    summary_data = [
        ['Fraud Probability', 'Risk Level', 'ML Ensemble Score'],
        [f"{result['fraud_probability']}%", result['risk_level'], f"{result['ml_score']:.1f}%"]
    ]
    
    summary_table = Table(summary_data, colWidths=[150, 150, 150])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A5F')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (1, 1), (1, 1), risk_color),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, 1), 14),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('TOPPADDING', (0, 1), (-1, 1), 15),
        ('BOTTOMPADDING', (0, 1), (-1, 1), 15),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Recommendation", heading_style))
    elements.append(Paragraph(result['recommendation'], normal_style))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Business Information", heading_style))
    
    business_info = [
        ['Property', 'Value'],
        ['Business Type', business_data.get('business_type', 'N/A')],
        ['Number of Outlets', str(business_data.get('num_outlets', 'N/A'))],
        ['Region', business_data.get('region', 'N/A')],
        ['State', business_data.get('state', 'N/A')],
        ['Total Land Area', f"{business_data.get('total_land_sqft', 0):,.0f} sq ft"],
        ['Declared Revenue', f"Rs.{business_data.get('declared_revenue', 0):,.0f}"],
        ['Declared Tax Paid', f"Rs.{business_data.get('declared_tax_paid', 0):,.0f}"],
        ['Number of Employees', str(business_data.get('num_employees', 'N/A'))],
        ['Years in Operation', str(business_data.get('years_in_operation', 'N/A'))],
        ['Tycoon Connection', business_data.get('tycoon_connection_level', 'None')],
    ]
    
    if business_data.get('satellite_measured_area'):
        business_info.append(['Satellite Measured Area', f"{business_data.get('satellite_measured_area', 0):,.0f} sq ft"])
        business_info.append(['Area Discrepancy', f"{business_data.get('area_discrepancy_percent', 0):.1f}%"])
    
    business_table = Table(business_info, colWidths=[200, 250])
    business_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    elements.append(business_table)
    elements.append(Spacer(1, 20))
    
    matched_patterns = result.get('matched_fraud_patterns', [])
    if matched_patterns:
        elements.append(Paragraph("Matched Fraud Patterns", heading_style))
        
        pattern_data = [['Pattern Type', 'Confidence', 'Key Indicators']]
        for p in matched_patterns:
            indicators = ', '.join(p.get('indicators', [])[:2])
            if len(p.get('indicators', [])) > 2:
                indicators += '...'
            pattern_data.append([p['type'], f"{p['score']}%", indicators[:50] + ('...' if len(indicators) > 50 else '')])
        
        pattern_table = Table(pattern_data, colWidths=[120, 80, 250])
        pattern_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(pattern_table)
        elements.append(Spacer(1, 15))
    
    if result.get('risk_factors'):
        elements.append(Paragraph("Identified Risk Factors", heading_style))
        
        risk_data = [['Risk Factor', 'Severity', 'Score']]
        for rf in result['risk_factors'][:10]:
            risk_data.append([
                rf['factor'][:40] + ('...' if len(rf['factor']) > 40 else ''),
                rf['severity'],
                f"{rf['score']:.1f}"
            ])
        
        risk_table = Table(risk_data, colWidths=[250, 100, 80])
        
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]
        
        for i, rf in enumerate(result['risk_factors'][:10], 1):
            severity = rf['severity']
            if severity == 'HIGH':
                table_style.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#dc3545')))
                table_style.append(('TEXTCOLOR', (1, i), (1, i), colors.white))
            elif severity == 'MEDIUM':
                table_style.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#ffc107')))
            else:
                table_style.append(('BACKGROUND', (1, i), (1, i), colors.HexColor('#28a745')))
                table_style.append(('TEXTCOLOR', (1, i), (1, i), colors.white))
        
        risk_table.setStyle(TableStyle(table_style))
        elements.append(risk_table)
        elements.append(Spacer(1, 20))
    
    similar_cases = result.get('similar_cases', [])
    if similar_cases:
        elements.append(Paragraph("Similar Historical Fraud Cases", heading_style))
        
        case_data = [['Case Name', 'Year', 'Amount (Cr)', 'Fraud Type']]
        for c in similar_cases[:5]:
            case_data.append([
                c['name'][:30] + ('...' if len(c['name']) > 30 else ''),
                str(c['year']),
                f"Rs.{c['amount_crore']:,}",
                c['fraud_type']
            ])
        
        case_table = Table(case_data, colWidths=[150, 60, 100, 140])
        case_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(case_table)
        elements.append(Spacer(1, 15))
    
    if result.get('ml_scores_detail'):
        elements.append(Paragraph("Machine Learning Model Scores", heading_style))
        
        ml_data = [
            ['Model', 'Score'],
            ['Isolation Forest', f"{result['ml_scores_detail']['isolation_forest_score']:.1f}%"],
            ['Random Forest', f"{result['ml_scores_detail']['random_forest_score']:.1f}%"],
            ['XGBoost', f"{result['ml_scores_detail']['xgboost_score']:.1f}%"],
            ['Ensemble (Weighted)', f"{result['ml_scores_detail']['ensemble_score']:.1f}%"],
        ]
        
        ml_table = Table(ml_data, colWidths=[200, 100])
        ml_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(ml_table)
        elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("Disclaimer", heading_style))
    disclaimer_text = """This report is generated by an automated fraud detection system developed for the Income Tax Department. 
    It should be used as a preliminary screening tool to prioritize investigations, not as definitive proof of any wrongdoing. 
    All findings require verification through proper investigative procedures as per the Income Tax Act, 1961. 
    This assessment is based on statistical analysis, machine learning models, and pattern matching against benchmark data and historical fraud cases.
    The system learns from publicly available news sources and official case records to improve detection accuracy."""
    elements.append(Paragraph(disclaimer_text, normal_style))
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph("_" * 40, normal_style))
    elements.append(Paragraph("Authorized Signature", normal_style))
    elements.append(Paragraph(f"Report ID: FD-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                             ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
    
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.getvalue()


def generate_vendor_report_pdf(vendor_data: Dict, analysis_result: Dict, visual_analysis: Dict = None, 
                               lifestyle_analysis: Dict = None, network_analysis: Dict = None) -> bytes:
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=22, 
                                  textColor=colors.HexColor('#1E3A5F'), alignment=TA_CENTER, spaceAfter=20)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Normal'], fontSize=11, 
                                     textColor=colors.grey, alignment=TA_CENTER, spaceAfter=25)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=13, 
                                    textColor=colors.HexColor('#1E3A5F'), spaceBefore=12, spaceAfter=8)
    normal_style = ParagraphStyle('CustomNormal', parent=styles['Normal'], fontSize=10, spaceAfter=5)
    
    elements = []
    
    elements.append(Paragraph("INCOME TAX DEPARTMENT", subtitle_style))
    elements.append(Paragraph("Small Vendor Fraud Assessment Report", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", subtitle_style))
    elements.append(Paragraph("CONFIDENTIAL - FIELD INVESTIGATION DOCUMENT", 
                             ParagraphStyle('Conf', parent=normal_style, textColor=colors.red, alignment=TA_CENTER)))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Vendor Profile", heading_style))
    
    vendor_info = [
        ['Field', 'Value'],
        ['Vendor Name', vendor_data.get('vendor_name', 'N/A')],
        ['Vendor Type', vendor_data.get('business_type', 'N/A')],
        ['Location', vendor_data.get('location_description', vendor_data.get('region', 'N/A'))],
        ['Declared Monthly Revenue', f"Rs.{vendor_data.get('declared_revenue', 0)/12:,.0f}"],
        ['Years in Operation', str(vendor_data.get('years_in_operation', 'N/A'))],
    ]
    
    vendor_table = Table(vendor_info, colWidths=[180, 270])
    vendor_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(vendor_table)
    elements.append(Spacer(1, 15))
    
    if visual_analysis:
        elements.append(Paragraph("Visual Intelligence Analysis", heading_style))
        
        visual_info = [
            ['Assessment', 'Finding'],
            ['Stall Size Estimate', f"{visual_analysis.get('stall_size_estimate', 'N/A')} sq ft"],
            ['Stock Value Estimate', f"Rs.{visual_analysis.get('stock_value_estimate', 0):,.0f}"],
            ['Equipment Value', f"Rs.{visual_analysis.get('equipment_value', 0):,.0f}"],
            ['Quality Tier', visual_analysis.get('quality_tier', 'N/A').title()],
            ['Customer Capacity/Hr', str(visual_analysis.get('customer_capacity', 'N/A'))],
            ['Legitimacy Score', f"{visual_analysis.get('legitimacy_score', 'N/A')}/100"],
        ]
        
        visual_table = Table(visual_info, colWidths=[180, 270])
        visual_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(visual_table)
        
        red_flags = visual_analysis.get('red_flags', [])
        if red_flags:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("<b>Visual Red Flags:</b>", normal_style))
            for flag in red_flags[:5]:
                elements.append(Paragraph(f"  - {flag}", normal_style))
        
        elements.append(Spacer(1, 15))
    
    if lifestyle_analysis:
        elements.append(Paragraph("Lifestyle vs Income Analysis", heading_style))
        
        lifestyle_info = [
            ['Metric', 'Value'],
            ['Declared Annual Income', f"Rs.{lifestyle_analysis.get('declared_income', 0):,.0f}"],
            ['Estimated Annual Expense', f"Rs.{lifestyle_analysis.get('estimated_annual_expense', 0):,.0f}"],
            ['Estimated Asset Value', f"Rs.{lifestyle_analysis.get('estimated_asset_value', 0):,.0f}"],
            ['Expense Ratio', f"{lifestyle_analysis.get('expense_ratio', 0):.2f}x"],
            ['Income Gap', f"Rs.{lifestyle_analysis.get('income_gap', 0):,.0f}"],
            ['Lifestyle Risk Score', f"{lifestyle_analysis.get('risk_score', 0)}/100"],
        ]
        
        lifestyle_table = Table(lifestyle_info, colWidths=[180, 270])
        lifestyle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fd7e14')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(lifestyle_table)
        elements.append(Spacer(1, 15))
    
    if network_analysis:
        elements.append(Paragraph("Network Analysis", heading_style))
        
        network_info = [
            ['Metric', 'Value'],
            ['Total Connected Entities', str(network_analysis.get('total_entities', 0))],
            ['Total Connections', str(network_analysis.get('total_connections', 0))],
            ['Suspicious Connections', str(len(network_analysis.get('suspicious_connections', [])))],
            ['Network Risk Score', f"{network_analysis.get('network_risk_score', 0)}/100"],
        ]
        
        network_table = Table(network_info, colWidths=[180, 270])
        network_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(network_table)
        elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Overall Assessment", heading_style))
    
    overall_score = analysis_result.get('fraud_probability', 0)
    risk_level = analysis_result.get('risk_level', 'LOW')
    
    assessment_info = [
        ['Overall Fraud Score', f"{overall_score:.1f}%"],
        ['Risk Level', risk_level],
        ['Recommendation', analysis_result.get('recommendation', 'N/A')[:100]],
    ]
    
    risk_colors = {
        "LOW": colors.HexColor('#28a745'),
        "MODERATE": colors.HexColor('#ffc107'),
        "HIGH": colors.HexColor('#fd7e14'),
        "VERY HIGH": colors.HexColor('#dc3545'),
        "CRITICAL": colors.HexColor('#721c24')
    }
    
    assessment_table = Table(assessment_info, colWidths=[180, 270])
    assessment_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (1, 1), (1, 1), risk_colors.get(risk_level, colors.grey)),
        ('TEXTCOLOR', (1, 1), (1, 1), colors.white),
    ]))
    elements.append(assessment_table)
    
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("_" * 40, normal_style))
    elements.append(Paragraph("Field Officer Signature", normal_style))
    elements.append(Paragraph(f"Report ID: SV-{datetime.now().strftime('%Y%m%d%H%M%S')}", 
                             ParagraphStyle('Footer', parent=normal_style, fontSize=8, textColor=colors.grey)))
    
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.getvalue()
