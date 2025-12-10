import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

BUSINESS_TYPES = [
    "Small Shop",
    "Mega Mart",
    "MNC (Multinational Corporation)",
    "Office/Corporate",
    "Rental Business",
    "Service Provider",
    "Manufacturing",
    "E-commerce",
    "Restaurant/Food Service",
    "Healthcare/Medical",
    "Educational Institution",
    "Real Estate Developer",
    "Import/Export Trading",
    "Jewelry/Gold Business",
    "Construction Company",
    "Street Vendor - Food",
    "Street Vendor - Goods",
    "Small Hawker/Peddler",
    "Roadside Stall",
    "Mobile Vendor",
    "Kiosk/Booth",
    "Small Dhaba",
    "Pan/Cigarette Shop",
    "Fruit/Vegetable Vendor",
    "Tea Stall"
]

SMALL_VENDOR_TYPES = [
    "Street Vendor - Food",
    "Street Vendor - Goods", 
    "Small Hawker/Peddler",
    "Roadside Stall",
    "Mobile Vendor",
    "Kiosk/Booth",
    "Small Dhaba",
    "Pan/Cigarette Shop",
    "Fruit/Vegetable Vendor",
    "Tea Stall"
]

BUSINESS_BENCHMARKS = {
    "Small Shop": {
        "outlets_range": (1, 5),
        "land_sqft_per_outlet": (200, 2000),
        "electricity_kwh_per_sqft": (5, 15),
        "revenue_per_sqft": (500, 3000),
        "employees_per_outlet": (1, 10),
        "expected_tax_rate": (0.15, 0.25)
    },
    "Mega Mart": {
        "outlets_range": (1, 50),
        "land_sqft_per_outlet": (20000, 100000),
        "electricity_kwh_per_sqft": (10, 25),
        "revenue_per_sqft": (1000, 5000),
        "employees_per_outlet": (50, 300),
        "expected_tax_rate": (0.20, 0.30)
    },
    "MNC (Multinational Corporation)": {
        "outlets_range": (5, 100),
        "land_sqft_per_outlet": (5000, 50000),
        "electricity_kwh_per_sqft": (8, 20),
        "revenue_per_sqft": (2000, 10000),
        "employees_per_outlet": (20, 200),
        "expected_tax_rate": (0.22, 0.35)
    },
    "Office/Corporate": {
        "outlets_range": (1, 20),
        "land_sqft_per_outlet": (1000, 20000),
        "electricity_kwh_per_sqft": (6, 15),
        "revenue_per_sqft": (1500, 8000),
        "employees_per_outlet": (10, 100),
        "expected_tax_rate": (0.20, 0.32)
    },
    "Rental Business": {
        "outlets_range": (1, 50),
        "land_sqft_per_outlet": (500, 10000),
        "electricity_kwh_per_sqft": (2, 8),
        "revenue_per_sqft": (200, 1500),
        "employees_per_outlet": (1, 5),
        "expected_tax_rate": (0.15, 0.28)
    },
    "Service Provider": {
        "outlets_range": (1, 30),
        "land_sqft_per_outlet": (500, 5000),
        "electricity_kwh_per_sqft": (5, 12),
        "revenue_per_sqft": (1000, 6000),
        "employees_per_outlet": (5, 50),
        "expected_tax_rate": (0.18, 0.30)
    },
    "Manufacturing": {
        "outlets_range": (1, 20),
        "land_sqft_per_outlet": (10000, 200000),
        "electricity_kwh_per_sqft": (20, 80),
        "revenue_per_sqft": (500, 3000),
        "employees_per_outlet": (50, 500),
        "expected_tax_rate": (0.20, 0.32)
    },
    "E-commerce": {
        "outlets_range": (1, 10),
        "land_sqft_per_outlet": (1000, 50000),
        "electricity_kwh_per_sqft": (15, 40),
        "revenue_per_sqft": (5000, 20000),
        "employees_per_outlet": (10, 200),
        "expected_tax_rate": (0.18, 0.28)
    },
    "Restaurant/Food Service": {
        "outlets_range": (1, 100),
        "land_sqft_per_outlet": (500, 5000),
        "electricity_kwh_per_sqft": (25, 60),
        "revenue_per_sqft": (800, 4000),
        "employees_per_outlet": (5, 30),
        "expected_tax_rate": (0.15, 0.25)
    },
    "Healthcare/Medical": {
        "outlets_range": (1, 50),
        "land_sqft_per_outlet": (1000, 30000),
        "electricity_kwh_per_sqft": (15, 35),
        "revenue_per_sqft": (2000, 15000),
        "employees_per_outlet": (10, 100),
        "expected_tax_rate": (0.18, 0.30)
    },
    "Educational Institution": {
        "outlets_range": (1, 20),
        "land_sqft_per_outlet": (5000, 100000),
        "electricity_kwh_per_sqft": (8, 20),
        "revenue_per_sqft": (500, 2000),
        "employees_per_outlet": (20, 200),
        "expected_tax_rate": (0.0, 0.15)
    },
    "Real Estate Developer": {
        "outlets_range": (1, 10),
        "land_sqft_per_outlet": (50000, 500000),
        "electricity_kwh_per_sqft": (2, 10),
        "revenue_per_sqft": (1000, 5000),
        "employees_per_outlet": (10, 100),
        "expected_tax_rate": (0.20, 0.35)
    },
    "Import/Export Trading": {
        "outlets_range": (1, 5),
        "land_sqft_per_outlet": (2000, 20000),
        "electricity_kwh_per_sqft": (5, 15),
        "revenue_per_sqft": (2000, 15000),
        "employees_per_outlet": (5, 50),
        "expected_tax_rate": (0.18, 0.30)
    },
    "Jewelry/Gold Business": {
        "outlets_range": (1, 20),
        "land_sqft_per_outlet": (500, 5000),
        "electricity_kwh_per_sqft": (8, 20),
        "revenue_per_sqft": (5000, 50000),
        "employees_per_outlet": (3, 20),
        "expected_tax_rate": (0.15, 0.28)
    },
    "Construction Company": {
        "outlets_range": (1, 10),
        "land_sqft_per_outlet": (5000, 50000),
        "electricity_kwh_per_sqft": (10, 30),
        "revenue_per_sqft": (1000, 5000),
        "employees_per_outlet": (20, 200),
        "expected_tax_rate": (0.18, 0.30)
    },
    "Street Vendor - Food": {
        "outlets_range": (1, 3),
        "land_sqft_per_outlet": (20, 100),
        "electricity_kwh_per_sqft": (0, 5),
        "revenue_per_sqft": (5000, 30000),
        "employees_per_outlet": (1, 3),
        "expected_tax_rate": (0.0, 0.10),
        "daily_revenue_range": (500, 5000),
        "typical_stock_value": (2000, 20000),
        "cash_percentage": (90, 100)
    },
    "Street Vendor - Goods": {
        "outlets_range": (1, 5),
        "land_sqft_per_outlet": (30, 200),
        "electricity_kwh_per_sqft": (0, 3),
        "revenue_per_sqft": (3000, 20000),
        "employees_per_outlet": (1, 4),
        "expected_tax_rate": (0.0, 0.10),
        "daily_revenue_range": (1000, 15000),
        "typical_stock_value": (10000, 200000),
        "cash_percentage": (80, 100)
    },
    "Small Hawker/Peddler": {
        "outlets_range": (1, 1),
        "land_sqft_per_outlet": (0, 20),
        "electricity_kwh_per_sqft": (0, 0),
        "revenue_per_sqft": (0, 0),
        "employees_per_outlet": (1, 2),
        "expected_tax_rate": (0.0, 0.05),
        "daily_revenue_range": (200, 2000),
        "typical_stock_value": (500, 10000),
        "cash_percentage": (100, 100)
    },
    "Roadside Stall": {
        "outlets_range": (1, 3),
        "land_sqft_per_outlet": (50, 300),
        "electricity_kwh_per_sqft": (2, 10),
        "revenue_per_sqft": (2000, 15000),
        "employees_per_outlet": (1, 5),
        "expected_tax_rate": (0.0, 0.12),
        "daily_revenue_range": (1000, 10000),
        "typical_stock_value": (5000, 50000),
        "cash_percentage": (85, 100)
    },
    "Mobile Vendor": {
        "outlets_range": (1, 1),
        "land_sqft_per_outlet": (0, 50),
        "electricity_kwh_per_sqft": (0, 0),
        "revenue_per_sqft": (0, 0),
        "employees_per_outlet": (1, 2),
        "expected_tax_rate": (0.0, 0.05),
        "daily_revenue_range": (300, 3000),
        "typical_stock_value": (1000, 15000),
        "cash_percentage": (95, 100)
    },
    "Kiosk/Booth": {
        "outlets_range": (1, 5),
        "land_sqft_per_outlet": (30, 150),
        "electricity_kwh_per_sqft": (5, 20),
        "revenue_per_sqft": (3000, 25000),
        "employees_per_outlet": (1, 3),
        "expected_tax_rate": (0.05, 0.15),
        "daily_revenue_range": (2000, 20000),
        "typical_stock_value": (10000, 100000),
        "cash_percentage": (70, 95)
    },
    "Small Dhaba": {
        "outlets_range": (1, 3),
        "land_sqft_per_outlet": (200, 1000),
        "electricity_kwh_per_sqft": (15, 40),
        "revenue_per_sqft": (1000, 5000),
        "employees_per_outlet": (3, 10),
        "expected_tax_rate": (0.05, 0.15),
        "daily_revenue_range": (3000, 25000),
        "typical_stock_value": (10000, 50000),
        "cash_percentage": (80, 100)
    },
    "Pan/Cigarette Shop": {
        "outlets_range": (1, 5),
        "land_sqft_per_outlet": (20, 100),
        "electricity_kwh_per_sqft": (3, 10),
        "revenue_per_sqft": (8000, 50000),
        "employees_per_outlet": (1, 2),
        "expected_tax_rate": (0.05, 0.15),
        "daily_revenue_range": (2000, 15000),
        "typical_stock_value": (20000, 150000),
        "cash_percentage": (90, 100)
    },
    "Fruit/Vegetable Vendor": {
        "outlets_range": (1, 3),
        "land_sqft_per_outlet": (30, 200),
        "electricity_kwh_per_sqft": (0, 5),
        "revenue_per_sqft": (2000, 15000),
        "employees_per_outlet": (1, 3),
        "expected_tax_rate": (0.0, 0.08),
        "daily_revenue_range": (1000, 8000),
        "typical_stock_value": (5000, 30000),
        "cash_percentage": (95, 100)
    },
    "Tea Stall": {
        "outlets_range": (1, 5),
        "land_sqft_per_outlet": (30, 150),
        "electricity_kwh_per_sqft": (10, 30),
        "revenue_per_sqft": (3000, 20000),
        "employees_per_outlet": (1, 4),
        "expected_tax_rate": (0.0, 0.10),
        "daily_revenue_range": (1000, 8000),
        "typical_stock_value": (3000, 20000),
        "cash_percentage": (90, 100)
    }
}

LAND_RATES_BY_REGION = {
    "Metro City - Prime (Mumbai, Delhi)": (25000, 100000),
    "Metro City - Prime (Bangalore, Chennai)": (15000, 50000),
    "Metro City - Suburban": (8000, 25000),
    "Tier-2 City - Prime": (5000, 15000),
    "Tier-2 City - Suburban": (2000, 8000),
    "Tier-3 City": (1000, 5000),
    "Rural/Industrial Zone": (500, 3000),
    "Special Economic Zone": (3000, 12000),
    "IT Park/Tech Hub": (8000, 25000),
    "Street/Footpath Location": (0, 500),
    "Market Area - Wholesale": (3000, 15000),
    "Railway Station Area": (2000, 10000),
    "Bus Stand Area": (1500, 8000)
}

INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
    "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal",
    "Delhi NCR", "Chandigarh"
]

TYCOON_CONNECTION_LEVELS = [
    "None",
    "Distant/Indirect",
    "Business Associate",
    "Close Business Partner",
    "Family/Direct Relationship"
]

LIFESTYLE_INDICATORS = {
    "vehicle_types": [
        "None",
        "Two-wheeler (Basic)",
        "Two-wheeler (Premium)",
        "Four-wheeler (Economy)",
        "Four-wheeler (Mid-range)",
        "Four-wheeler (Luxury)",
        "Multiple Vehicles"
    ],
    "property_ownership": [
        "Rented (Basic)",
        "Rented (Premium)",
        "Owned (1 Property)",
        "Owned (Multiple Properties)",
        "Owned (Premium/Luxury)"
    ],
    "education_expense": [
        "Government School",
        "Private School (Budget)",
        "Private School (Mid-tier)",
        "Private School (Premium)",
        "International School",
        "Abroad Education"
    ],
    "travel_patterns": [
        "Local Only",
        "Occasional Domestic",
        "Frequent Domestic",
        "Occasional International",
        "Frequent International",
        "Luxury Travel"
    ],
    "jewelry_purchases": [
        "None/Minimal",
        "Occasional (Below 1L)",
        "Regular (1-5L/year)",
        "Frequent (5-20L/year)",
        "Heavy (Above 20L/year)"
    ],
    "mobile_devices": [
        "Basic Phone",
        "Budget Smartphone",
        "Mid-range Smartphone",
        "Premium Smartphone",
        "Multiple Premium Devices"
    ]
}

SMALL_VENDOR_FRAUD_PATTERNS = {
    "front_operation": {
        "name": "Front Operation",
        "description": "Small vendor serving as front for larger cash operations",
        "key_indicators": [
            "High-value transactions relative to visible stock",
            "Frequent large cash exchanges",
            "Connections to larger businesses",
            "Disproportionate lifestyle",
            "Multiple UPI/payment accounts"
        ],
        "risk_weight": 0.9
    },
    "cash_layering": {
        "name": "Cash Layering Point",
        "description": "Using small vendors to layer cash from illegal activities",
        "key_indicators": [
            "Unusual deposit patterns",
            "Multiple bank accounts",
            "Cash deposits in different locations",
            "Connected to known launderers",
            "Round figure transactions"
        ],
        "risk_weight": 0.95
    },
    "turnover_inflation": {
        "name": "Turnover Inflation",
        "description": "Inflating turnover to launder money or get loans",
        "key_indicators": [
            "GST returns higher than visible capacity",
            "Bank deposits exceed stock capacity",
            "Claiming expenses without supporting staff",
            "High-value invoices from unverifiable suppliers"
        ],
        "risk_weight": 0.85
    },
    "benami_network_node": {
        "name": "Benami Network Node",
        "description": "Part of a larger benami property/business network",
        "key_indicators": [
            "Vendor owns properties inconsistent with business",
            "Multiple licenses/registrations in family names",
            "Business location owned by third party",
            "Unexplained asset accumulation"
        ],
        "risk_weight": 0.88
    },
    "gold_hawala": {
        "name": "Gold/Hawala Conduit",
        "description": "Using vendor business for gold or hawala transactions",
        "key_indicators": [
            "Jewelry shop connections",
            "Frequent travel to border regions",
            "Cash-heavy with minimal inventory",
            "International connections in calls/transactions"
        ],
        "risk_weight": 0.92
    }
}

MAJOR_INDIAN_FRAUD_CASES = [
    {
        "name": "Sahara India Pariwar",
        "year": 2014,
        "amount_crore": 24000,
        "fraud_type": "cash_hoarding",
        "detection_method": "IT raids seized cash, jewelry, and incriminating documents",
        "key_indicators": ["massive undisclosed cash", "hidden assets", "multiple shell entities"],
        "description": "Massive undisclosed cash and assets discovered through Income Tax raids"
    },
    {
        "name": "Satyam Balajee Group",
        "year": 2025,
        "amount_crore": 500,
        "fraud_type": "shell_company",
        "detection_method": "Real-time surveillance and financial intelligence tracking",
        "key_indicators": ["shell firms", "fake transactions", "under-reporting"],
        "description": "Shell companies used for fake transactions and under-reporting income"
    },
    {
        "name": "Nationwide Bogus Deductions Scam",
        "year": 2025,
        "amount_crore": 1000,
        "fraud_type": "bogus_deductions",
        "detection_method": "AI-based cross-verification of ITR claims",
        "key_indicators": ["fake HRA claims", "fabricated medical expenses", "inflated refunds"],
        "description": "Organized fake deduction claims across multiple taxpayers"
    },
    {
        "name": "Nirav Modi - PNB Fraud",
        "year": 2018,
        "amount_crore": 14000,
        "fraud_type": "money_laundering",
        "detection_method": "Bank reconciliation and SWIFT message audit",
        "key_indicators": ["unauthorized LoUs", "circular trading", "offshore accounts"],
        "description": "Massive bank fraud through fraudulent Letters of Undertaking"
    },
    {
        "name": "Vijay Mallya - Kingfisher",
        "year": 2016,
        "amount_crore": 9000,
        "fraud_type": "loan_default",
        "detection_method": "Bank NPAs and asset verification",
        "key_indicators": ["loan diversion", "inflated valuations", "asset stripping"],
        "description": "Willful loan default with fund diversion to personal accounts"
    },
    {
        "name": "Kolkata Shell Company Network",
        "year": 2024,
        "amount_crore": 309,
        "fraud_type": "shell_company",
        "detection_method": "Search operations and document verification",
        "key_indicators": ["bogus share capital", "off-book cash", "minimal operations"],
        "description": "Network of shell companies for money laundering"
    },
    {
        "name": "Private Educational Institution Scam",
        "year": 2023,
        "amount_crore": 200,
        "fraud_type": "cash_collection",
        "detection_method": "IT raids on staff bank accounts",
        "key_indicators": ["unreported admission cash", "distributed through staff accounts", "capitation fees"],
        "description": "Cash collections from admissions routed through employee accounts"
    },
    {
        "name": "Real Estate Undervaluation Networks",
        "year": 2024,
        "amount_crore": 500,
        "fraud_type": "undervaluation",
        "detection_method": "Stamp duty mismatch and market rate comparison",
        "key_indicators": ["undervalued properties", "cash components", "benami transactions"],
        "description": "Systematic underreporting of property values"
    },
    {
        "name": "Circular Trading GST Fraud",
        "year": 2024,
        "amount_crore": 1200,
        "fraud_type": "circular_trading",
        "detection_method": "Big data analytics on GST network",
        "key_indicators": ["fake invoices", "no goods movement", "ITC claims"],
        "description": "Fake invoice networks for fraudulent GST input credit"
    },
    {
        "name": "Multi-City Fake Deduction Rackets",
        "year": 2025,
        "amount_crore": 300,
        "fraud_type": "bogus_deductions",
        "detection_method": "AI cross-checks with employer and bank data",
        "key_indicators": ["organized CA networks", "fake rent receipts", "fabricated 80C claims"],
        "description": "Professional networks filing false deductions for multiple clients"
    },
    {
        "name": "Street Vendor Front Operation - Mumbai",
        "year": 2024,
        "amount_crore": 50,
        "fraud_type": "front_operation",
        "detection_method": "Visual surveillance and transaction pattern analysis",
        "key_indicators": ["small stall with luxury lifestyle", "high cash deposits", "connection to real estate"],
        "description": "Network of 50+ street vendors used to layer cash from real estate fraud"
    },
    {
        "name": "Pan Shop Hawala Network - Delhi",
        "year": 2024,
        "amount_crore": 120,
        "fraud_type": "gold_hawala",
        "detection_method": "Mobile number analysis and travel pattern tracking",
        "key_indicators": ["multiple SIM cards", "frequent border travel", "gold purchases"],
        "description": "Pan shops serving as hawala points for cross-border gold smuggling"
    }
]

FRAUD_TYPES = {
    "shell_company": {
        "name": "Shell Company",
        "description": "Paper companies with no real business operations used for money laundering",
        "key_indicators": [
            "Very low electricity consumption relative to revenue",
            "Minimal or no employees",
            "High revenue with low operational footprint",
            "Same directors across multiple entities",
            "Registered at virtual/shared office addresses"
        ],
        "risk_weight": 0.9
    },
    "money_laundering": {
        "name": "Money Laundering",
        "description": "Concealing illegally obtained money through complex transactions",
        "key_indicators": [
            "Unusually high revenue for business type",
            "Cash-intensive operations",
            "Frequent large deposits just under reporting threshold",
            "Circular transactions between related entities",
            "Complex ownership structures"
        ],
        "risk_weight": 0.95
    },
    "under_reporting": {
        "name": "Revenue Under-Reporting",
        "description": "Declaring less revenue than actually earned to evade taxes",
        "key_indicators": [
            "Revenue significantly below industry benchmarks",
            "Mismatch between GST and ITR filings",
            "High electricity/staff but low revenue",
            "Cash-heavy business model"
        ],
        "risk_weight": 0.8
    },
    "bogus_deductions": {
        "name": "Bogus Deductions",
        "description": "Claiming false deductions to reduce taxable income",
        "key_indicators": [
            "Unusually high HRA claims",
            "Fake donation receipts",
            "Inflated medical expenses",
            "False insurance premiums"
        ],
        "risk_weight": 0.7
    },
    "circular_trading": {
        "name": "Circular Trading",
        "description": "Fake invoice networks for GST input credit fraud",
        "key_indicators": [
            "Invoices between related entities",
            "No actual goods movement",
            "High ITC claims",
            "New entities with large transactions"
        ],
        "risk_weight": 0.85
    },
    "black_money": {
        "name": "Black Money/Cash Hoarding",
        "description": "Undisclosed income kept in cash or hidden assets",
        "key_indicators": [
            "Low declared income but high lifestyle",
            "Large cash transactions",
            "Unexplained assets",
            "Gold/jewelry purchases without trail"
        ],
        "risk_weight": 0.9
    },
    "benami_property": {
        "name": "Benami Property",
        "description": "Properties held in others' names to hide ownership",
        "key_indicators": [
            "Properties in family members' names",
            "No income trail for property purchase",
            "Multiple properties under low-income individuals"
        ],
        "risk_weight": 0.85
    },
    "transfer_pricing": {
        "name": "Transfer Pricing Abuse",
        "description": "Manipulating inter-company transactions to shift profits",
        "key_indicators": [
            "Transactions with foreign subsidiaries at non-market rates",
            "Profit shifting to tax havens",
            "Royalty/service fee payments abroad"
        ],
        "risk_weight": 0.8
    },
    "front_operation": {
        "name": "Front Operation",
        "description": "Small vendor serving as front for larger cash operations",
        "key_indicators": [
            "High-value transactions relative to visible stock",
            "Frequent large cash exchanges",
            "Connections to larger businesses",
            "Disproportionate lifestyle"
        ],
        "risk_weight": 0.9
    },
    "cash_layering": {
        "name": "Cash Layering",
        "description": "Using small businesses to layer cash from illegal activities",
        "key_indicators": [
            "Unusual deposit patterns",
            "Multiple bank accounts",
            "Round figure transactions",
            "Connected to known launderers"
        ],
        "risk_weight": 0.92
    }
}


def generate_sample_dataset(n_samples: int = 500) -> pd.DataFrame:
    np.random.seed(42)
    
    data = []
    
    for i in range(n_samples):
        business_type = np.random.choice(BUSINESS_TYPES)
        benchmarks = BUSINESS_BENCHMARKS.get(business_type, BUSINESS_BENCHMARKS["Small Shop"])
        
        is_fraudulent = np.random.random() < 0.15
        
        outlets = np.random.randint(
            benchmarks["outlets_range"][0],
            benchmarks["outlets_range"][1] + 1
        )
        
        land_per_outlet = np.random.uniform(
            benchmarks["land_sqft_per_outlet"][0],
            benchmarks["land_sqft_per_outlet"][1]
        )
        total_land = outlets * land_per_outlet
        
        region = np.random.choice(list(LAND_RATES_BY_REGION.keys()))
        land_rate = np.random.uniform(
            LAND_RATES_BY_REGION[region][0],
            LAND_RATES_BY_REGION[region][1]
        )
        
        state = np.random.choice(INDIAN_STATES)
        
        electricity_per_sqft = np.random.uniform(
            benchmarks["electricity_kwh_per_sqft"][0],
            benchmarks["electricity_kwh_per_sqft"][1]
        )
        total_electricity = total_land * electricity_per_sqft
        
        revenue_per_sqft = np.random.uniform(
            benchmarks["revenue_per_sqft"][0],
            benchmarks["revenue_per_sqft"][1]
        )
        declared_revenue = total_land * revenue_per_sqft
        
        employees_per_outlet = np.random.randint(
            benchmarks["employees_per_outlet"][0],
            benchmarks["employees_per_outlet"][1] + 1
        )
        total_employees = outlets * employees_per_outlet
        
        is_stock_listed = np.random.random() < (0.3 if business_type in ["MNC (Multinational Corporation)", "Mega Mart", "E-commerce"] else 0.05)
        
        tycoon_connection = np.random.choice(
            TYCOON_CONNECTION_LEVELS,
            p=[0.4, 0.25, 0.2, 0.1, 0.05]
        )
        
        fraud_type = None
        if is_fraudulent:
            fraud_type = np.random.choice([
                "under_reported_revenue",
                "inflated_expenses",
                "shell_company",
                "money_laundering",
                "electricity_mismatch",
                "circular_trading",
                "black_money"
            ])
            
            if fraud_type == "under_reported_revenue":
                declared_revenue *= np.random.uniform(0.3, 0.6)
            elif fraud_type == "inflated_expenses":
                total_employees *= np.random.uniform(2.0, 4.0)
            elif fraud_type == "shell_company":
                total_electricity *= np.random.uniform(0.1, 0.3)
                total_employees = np.random.randint(1, 5)
            elif fraud_type == "money_laundering":
                declared_revenue *= np.random.uniform(2.0, 5.0)
                tycoon_connection = np.random.choice(["Close Business Partner", "Family/Direct Relationship"])
            elif fraud_type == "electricity_mismatch":
                total_electricity *= np.random.uniform(0.2, 0.4)
            elif fraud_type == "circular_trading":
                declared_revenue *= np.random.uniform(3.0, 8.0)
            elif fraud_type == "black_money":
                declared_revenue *= np.random.uniform(0.2, 0.5)
        
        tax_rate = np.random.uniform(
            benchmarks["expected_tax_rate"][0],
            benchmarks["expected_tax_rate"][1]
        )
        declared_tax = declared_revenue * tax_rate
        
        data.append({
            "business_id": f"BUS{i+1:04d}",
            "business_type": business_type,
            "num_outlets": outlets,
            "total_land_sqft": round(total_land, 2),
            "region": region,
            "state": state,
            "land_rate_per_sqft": round(land_rate, 2),
            "total_land_value": round(total_land * land_rate, 2),
            "electricity_consumption_kwh": round(total_electricity, 2),
            "declared_revenue": round(declared_revenue, 2),
            "declared_tax_paid": round(declared_tax, 2),
            "num_employees": int(total_employees),
            "is_stock_listed": is_stock_listed,
            "stock_market_cap": round(declared_revenue * np.random.uniform(3, 10), 2) if is_stock_listed else 0,
            "tycoon_connection_level": tycoon_connection,
            "years_in_operation": np.random.randint(1, 30),
            "is_fraudulent": is_fraudulent,
            "fraud_type": fraud_type
        })
    
    return pd.DataFrame(data)


def get_benchmarks_for_type(business_type: str) -> Dict:
    return BUSINESS_BENCHMARKS.get(business_type, BUSINESS_BENCHMARKS["Small Shop"])


def get_land_rate_range(region: str) -> Tuple[float, float]:
    return LAND_RATES_BY_REGION.get(region, (1000, 10000))


def calculate_expected_metrics(
    business_type: str,
    num_outlets: int,
    total_land_sqft: float
) -> Dict:
    benchmarks = get_benchmarks_for_type(business_type)
    
    is_small_vendor = business_type in SMALL_VENDOR_TYPES or "daily_revenue_range" in benchmarks
    
    expected_electricity_low = total_land_sqft * benchmarks["electricity_kwh_per_sqft"][0]
    expected_electricity_high = total_land_sqft * benchmarks["electricity_kwh_per_sqft"][1]
    
    if is_small_vendor and "daily_revenue_range" in benchmarks:
        daily_low, daily_high = benchmarks["daily_revenue_range"]
        working_days_per_year = 300
        expected_revenue_low = daily_low * working_days_per_year * num_outlets
        expected_revenue_high = daily_high * working_days_per_year * num_outlets
    else:
        expected_revenue_low = total_land_sqft * benchmarks["revenue_per_sqft"][0]
        expected_revenue_high = total_land_sqft * benchmarks["revenue_per_sqft"][1]
    
    expected_employees_low = num_outlets * benchmarks["employees_per_outlet"][0]
    expected_employees_high = num_outlets * benchmarks["employees_per_outlet"][1]
    
    return {
        "electricity_range": (expected_electricity_low, expected_electricity_high),
        "revenue_range": (expected_revenue_low, expected_revenue_high),
        "employees_range": (expected_employees_low, expected_employees_high),
        "expected_tax_rate_range": benchmarks["expected_tax_rate"],
        "is_small_vendor": is_small_vendor,
        "daily_revenue_range": benchmarks.get("daily_revenue_range", None),
        "typical_stock_value": benchmarks.get("typical_stock_value", None),
        "cash_percentage": benchmarks.get("cash_percentage", None)
    }


def get_similar_fraud_cases(fraud_indicators: List[str]) -> List[Dict]:
    similar_cases = []
    
    for case in MAJOR_INDIAN_FRAUD_CASES:
        match_score = 0
        for indicator in fraud_indicators:
            indicator_lower = indicator.lower()
            for key_indicator in case["key_indicators"]:
                if any(word in indicator_lower for word in key_indicator.lower().split()):
                    match_score += 1
                    break
        
        if match_score > 0:
            similar_cases.append({
                **case,
                "match_score": match_score
            })
    
    return sorted(similar_cases, key=lambda x: x["match_score"], reverse=True)[:5]


def estimate_daily_revenue_from_visual(
    business_type: str,
    estimated_customers_per_hour: int,
    avg_transaction_value: float,
    operating_hours: int = 10
) -> Dict:
    benchmarks = BUSINESS_BENCHMARKS.get(business_type, BUSINESS_BENCHMARKS["Street Vendor - Food"])
    
    estimated_daily = estimated_customers_per_hour * avg_transaction_value * operating_hours
    
    if "daily_revenue_range" in benchmarks:
        expected_low, expected_high = benchmarks["daily_revenue_range"]
        
        if estimated_daily > expected_high * 1.5:
            status = "ANOMALY_HIGH"
            deviation = ((estimated_daily - expected_high) / expected_high) * 100
        elif estimated_daily < expected_low * 0.5:
            status = "ANOMALY_LOW"
            deviation = ((expected_low - estimated_daily) / expected_low) * 100
        else:
            status = "NORMAL"
            deviation = 0
    else:
        status = "UNKNOWN"
        deviation = 0
    
    return {
        "estimated_daily_revenue": estimated_daily,
        "estimated_monthly_revenue": estimated_daily * 26,
        "estimated_annual_revenue": estimated_daily * 300,
        "status": status,
        "deviation_percent": deviation,
        "benchmark_range": benchmarks.get("daily_revenue_range", (0, 0))
    }


def calculate_lifestyle_income_gap(
    declared_annual_income: float,
    lifestyle_data: Dict
) -> Dict:
    lifestyle_costs = {
        "vehicle_types": {
            "None": 0,
            "Two-wheeler (Basic)": 60000,
            "Two-wheeler (Premium)": 150000,
            "Four-wheeler (Economy)": 500000,
            "Four-wheeler (Mid-range)": 1200000,
            "Four-wheeler (Luxury)": 3000000,
            "Multiple Vehicles": 5000000
        },
        "property_ownership": {
            "Rented (Basic)": 0,
            "Rented (Premium)": 0,
            "Owned (1 Property)": 2000000,
            "Owned (Multiple Properties)": 8000000,
            "Owned (Premium/Luxury)": 20000000
        },
        "education_expense": {
            "Government School": 10000,
            "Private School (Budget)": 50000,
            "Private School (Mid-tier)": 150000,
            "Private School (Premium)": 400000,
            "International School": 1000000,
            "Abroad Education": 3000000
        },
        "travel_patterns": {
            "Local Only": 5000,
            "Occasional Domestic": 30000,
            "Frequent Domestic": 100000,
            "Occasional International": 200000,
            "Frequent International": 500000,
            "Luxury Travel": 1500000
        }
    }
    
    total_estimated_expenses = 0
    expense_breakdown = {}
    
    for category, value in lifestyle_data.items():
        if category in lifestyle_costs and value in lifestyle_costs[category]:
            expense = lifestyle_costs[category][value]
            expense_breakdown[category] = expense
            total_estimated_expenses += expense
    
    basic_living = 300000
    total_estimated_expenses += basic_living
    expense_breakdown["basic_living"] = basic_living
    
    if declared_annual_income > 0:
        gap_ratio = total_estimated_expenses / declared_annual_income
    else:
        gap_ratio = float('inf')
    
    if gap_ratio > 3:
        risk_level = "CRITICAL"
        risk_score = 95
    elif gap_ratio > 2:
        risk_level = "HIGH"
        risk_score = 75
    elif gap_ratio > 1.5:
        risk_level = "MODERATE"
        risk_score = 50
    elif gap_ratio > 1:
        risk_level = "LOW"
        risk_score = 25
    else:
        risk_level = "NORMAL"
        risk_score = 10
    
    return {
        "declared_income": declared_annual_income,
        "estimated_expenses": total_estimated_expenses,
        "expense_breakdown": expense_breakdown,
        "income_gap": max(0, total_estimated_expenses - declared_annual_income),
        "gap_ratio": gap_ratio,
        "risk_level": risk_level,
        "risk_score": risk_score
    }
