import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from typing import Dict, List, Tuple, Any

try:
    from xgboost import XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    XGBClassifier = None
from sample_data import (
    BUSINESS_BENCHMARKS, 
    LAND_RATES_BY_REGION,
    calculate_expected_metrics,
    generate_sample_dataset,
    FRAUD_TYPES,
    MAJOR_INDIAN_FRAUD_CASES,
    get_similar_fraud_cases,
    SMALL_VENDOR_TYPES,
    SMALL_VENDOR_FRAUD_PATTERNS
)


class FraudDetectionEngine:
    def __init__(self):
        self.sample_data = generate_sample_dataset(500)
        self.scaler = StandardScaler()
        self.isolation_forest = None
        self.random_forest = None
        self.xgboost_model = None
        self._train_models()
    
    def _train_models(self):
        features = self._extract_features(self.sample_data)
        labels = self.sample_data['is_fraudulent'].astype(int).values
        
        self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)
        
        self.isolation_forest = IsolationForest(
            contamination=0.15,
            random_state=42,
            n_estimators=100
        )
        self.isolation_forest.fit(scaled_features)
        
        X_train, X_test, y_train, y_test = train_test_split(
            scaled_features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        self.random_forest = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        )
        self.random_forest.fit(X_train, y_train)
        
        if XGBOOST_AVAILABLE and XGBClassifier is not None:
            self.xgboost_model = XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                scale_pos_weight=len(y_train[y_train==0]) / max(len(y_train[y_train==1]), 1),
                eval_metric='logloss'
            )
            self.xgboost_model.fit(X_train, y_train)
        else:
            self.xgboost_model = None
    
    def _extract_features(self, df: pd.DataFrame) -> np.ndarray:
        features = []
        
        for _, row in df.iterrows():
            benchmarks = BUSINESS_BENCHMARKS.get(
                row["business_type"], 
                BUSINESS_BENCHMARKS["Small Shop"]
            )
            
            expected_elec_mid = row["total_land_sqft"] * np.mean(benchmarks["electricity_kwh_per_sqft"])
            elec_ratio = row["electricity_consumption_kwh"] / max(expected_elec_mid, 1)
            
            expected_rev_mid = row["total_land_sqft"] * np.mean(benchmarks["revenue_per_sqft"])
            rev_ratio = row["declared_revenue"] / max(expected_rev_mid, 1)
            
            expected_emp_mid = row["num_outlets"] * np.mean(benchmarks["employees_per_outlet"])
            emp_ratio = row["num_employees"] / max(expected_emp_mid, 1)
            
            tax_rate = row["declared_tax_paid"] / max(row["declared_revenue"], 1)
            expected_tax_mid = np.mean(benchmarks["expected_tax_rate"])
            tax_ratio = tax_rate / max(expected_tax_mid, 0.01)
            
            land_rate_range = LAND_RATES_BY_REGION.get(row["region"], (1000, 10000))
            land_rate_normalized = (row["land_rate_per_sqft"] - land_rate_range[0]) / max(land_rate_range[1] - land_rate_range[0], 1)
            
            tycoon_score = {
                "None": 0,
                "Distant/Indirect": 0.25,
                "Business Associate": 0.5,
                "Close Business Partner": 0.75,
                "Family/Direct Relationship": 1.0
            }.get(row["tycoon_connection_level"], 0)
            
            revenue_per_employee = row["declared_revenue"] / max(row["num_employees"], 1)
            revenue_per_outlet = row["declared_revenue"] / max(row["num_outlets"], 1)
            land_per_outlet = row["total_land_sqft"] / max(row["num_outlets"], 1)
            
            features.append([
                elec_ratio,
                rev_ratio,
                emp_ratio,
                tax_ratio,
                land_rate_normalized,
                tycoon_score,
                revenue_per_employee / 100000,
                revenue_per_outlet / 1000000,
                land_per_outlet / 10000,
                1 if row["is_stock_listed"] else 0,
                row["years_in_operation"] / 30
            ])
        
        return np.array(features)
    
    def detect_shell_company(self, business_data: Dict) -> Dict:
        indicators = []
        shell_score = 0
        
        benchmarks = BUSINESS_BENCHMARKS.get(business_data["business_type"], BUSINESS_BENCHMARKS["Small Shop"])
        expected_elec = business_data["total_land_sqft"] * np.mean(benchmarks["electricity_kwh_per_sqft"])
        actual_elec = business_data["electricity_consumption_kwh"]
        
        if actual_elec < expected_elec * 0.2:
            indicators.append("Extremely low electricity consumption - possible ghost office")
            shell_score += 30
        
        expected_emp = business_data["num_outlets"] * np.mean(benchmarks["employees_per_outlet"])
        actual_emp = business_data["num_employees"]
        
        if actual_emp < max(expected_emp * 0.1, 3):
            indicators.append("Minimal employee count - paper company indicator")
            shell_score += 25
        
        expected_rev = business_data["total_land_sqft"] * np.mean(benchmarks["revenue_per_sqft"])
        actual_rev = business_data["declared_revenue"]
        
        if actual_rev > expected_rev * 3 and actual_elec < expected_elec * 0.3:
            indicators.append("High revenue with low operational footprint")
            shell_score += 35
        
        if business_data.get("years_in_operation", 5) <= 2 and actual_rev > 10000000:
            indicators.append("New company with unusually high revenue")
            shell_score += 20
        
        return {
            "is_likely_shell": shell_score >= 50,
            "shell_score": min(100, shell_score),
            "indicators": indicators,
            "fraud_type": "shell_company"
        }
    
    def detect_money_laundering(self, business_data: Dict) -> Dict:
        indicators = []
        ml_score = 0
        
        benchmarks = BUSINESS_BENCHMARKS.get(business_data["business_type"], BUSINESS_BENCHMARKS["Small Shop"])
        expected_rev = business_data["total_land_sqft"] * np.mean(benchmarks["revenue_per_sqft"])
        actual_rev = business_data["declared_revenue"]
        
        if actual_rev > expected_rev * 4:
            indicators.append("Revenue significantly exceeds business capacity - possible money integration")
            ml_score += 30
        
        cash_intensive_types = ["Restaurant/Food Service", "Jewelry/Gold Business", "Small Shop", "Real Estate Developer"]
        cash_intensive_types.extend(SMALL_VENDOR_TYPES)
        
        if business_data["business_type"] in cash_intensive_types and actual_rev > expected_rev * 2:
            indicators.append("Cash-intensive business with unusually high revenue")
            ml_score += 25
        
        tycoon_level = business_data.get("tycoon_connection_level", "None")
        if tycoon_level in ["Close Business Partner", "Family/Direct Relationship"]:
            if actual_rev > expected_rev * 1.5:
                indicators.append("High-risk connections with inflated revenue")
                ml_score += 30
        
        return {
            "is_likely_laundering": ml_score >= 50,
            "laundering_score": min(100, ml_score),
            "indicators": indicators,
            "fraud_type": "money_laundering"
        }
    
    def detect_black_money(self, business_data: Dict) -> Dict:
        indicators = []
        bm_score = 0
        
        benchmarks = BUSINESS_BENCHMARKS.get(business_data["business_type"], BUSINESS_BENCHMARKS["Small Shop"])
        expected_rev = business_data["total_land_sqft"] * np.mean(benchmarks["revenue_per_sqft"])
        actual_rev = business_data["declared_revenue"]
        
        if actual_rev < expected_rev * 0.4:
            indicators.append("Significantly under-reported revenue - likely cash hoarding")
            bm_score += 35
        
        actual_tax_rate = business_data["declared_tax_paid"] / max(actual_rev, 1)
        expected_tax = np.mean(benchmarks["expected_tax_rate"])
        if actual_tax_rate < expected_tax * 0.3:
            indicators.append("Extremely low effective tax rate")
            bm_score += 25
        
        total_land_value = business_data["total_land_sqft"] * business_data["land_rate_per_sqft"]
        if total_land_value > actual_rev * 10:
            indicators.append("Asset value far exceeds declared income capacity")
            bm_score += 30
        
        land_rate_range = LAND_RATES_BY_REGION.get(business_data["region"], (1000, 10000))
        if business_data["land_rate_per_sqft"] < land_rate_range[0] * 0.4:
            indicators.append("Severely undervalued land - possible benami property")
            bm_score += 25
        
        return {
            "is_likely_black_money": bm_score >= 50,
            "black_money_score": min(100, bm_score),
            "indicators": indicators,
            "fraud_type": "black_money"
        }
    
    def detect_circular_trading(self, business_data: Dict) -> Dict:
        indicators = []
        ct_score = 0
        
        benchmarks = BUSINESS_BENCHMARKS.get(business_data["business_type"], BUSINESS_BENCHMARKS["Small Shop"])
        expected_rev = business_data["total_land_sqft"] * np.mean(benchmarks["revenue_per_sqft"])
        actual_rev = business_data["declared_revenue"]
        
        if actual_rev > expected_rev * 5:
            indicators.append("Revenue massively exceeds operational capacity - possible fake invoices")
            ct_score += 35
        
        if business_data["business_type"] == "Import/Export Trading":
            if actual_rev > expected_rev * 3:
                indicators.append("Trading business with inflated transactions")
                ct_score += 30
        
        if business_data.get("years_in_operation", 5) <= 3 and actual_rev > 50000000:
            indicators.append("New entity with massive transaction volume")
            ct_score += 25
        
        return {
            "is_likely_circular": ct_score >= 50,
            "circular_score": min(100, ct_score),
            "indicators": indicators,
            "fraud_type": "circular_trading"
        }
    
    def detect_benami_property(self, business_data: Dict) -> Dict:
        indicators = []
        bp_score = 0
        
        actual_rev = business_data["declared_revenue"]
        land_value = business_data["total_land_sqft"] * business_data["land_rate_per_sqft"]
        
        if land_value > actual_rev * 15:
            indicators.append("Property value grossly disproportionate to income")
            bp_score += 35
        
        land_rate_range = LAND_RATES_BY_REGION.get(business_data["region"], (1000, 10000))
        if business_data["land_rate_per_sqft"] < land_rate_range[0] * 0.3:
            indicators.append("Land significantly undervalued vs market rates")
            bp_score += 30
        
        if business_data.get("tycoon_connection_level") in ["Close Business Partner", "Family/Direct Relationship"]:
            indicators.append("High-risk political/tycoon connections with property")
            bp_score += 25
        
        return {
            "is_likely_benami": bp_score >= 50,
            "benami_score": min(100, bp_score),
            "indicators": indicators,
            "fraud_type": "benami_property"
        }
    
    def detect_front_operation(self, business_data: Dict, lifestyle_data: Dict = None) -> Dict:
        indicators = []
        front_score = 0
        
        if business_data["business_type"] not in SMALL_VENDOR_TYPES:
            return {"is_likely_front": False, "front_score": 0, "indicators": [], "fraud_type": "front_operation"}
        
        benchmarks = BUSINESS_BENCHMARKS.get(business_data["business_type"], BUSINESS_BENCHMARKS["Street Vendor - Food"])
        
        if "daily_revenue_range" in benchmarks:
            expected_daily_high = benchmarks["daily_revenue_range"][1]
            expected_annual_high = expected_daily_high * 300
            actual_rev = business_data["declared_revenue"]
            
            if actual_rev > expected_annual_high * 2:
                indicators.append(f"Revenue (₹{actual_rev:,.0f}) far exceeds expected for vendor type")
                front_score += 35
        
        if lifestyle_data:
            vehicle = lifestyle_data.get("vehicle", "None")
            if vehicle in ["Four-wheeler (Mid-range)", "Four-wheeler (Luxury)", "Multiple Vehicles"]:
                indicators.append(f"Luxury vehicle ({vehicle}) inconsistent with small vendor income")
                front_score += 25
            
            property_type = lifestyle_data.get("property", "Rented (Basic)")
            if property_type in ["Owned (Multiple Properties)", "Owned (Premium/Luxury)"]:
                indicators.append(f"Premium property ownership inconsistent with vendor income")
                front_score += 25
            
            education = lifestyle_data.get("education", "Government School")
            if education in ["International School", "Abroad Education"]:
                indicators.append("High-cost education for children inconsistent with vendor income")
                front_score += 15
        
        if business_data.get("num_bank_accounts", 1) > 3:
            indicators.append("Multiple bank accounts unusual for small vendor")
            front_score += 20
        
        if business_data.get("upi_transaction_volume", 0) > 1000000:
            indicators.append("High UPI transaction volume unusual for vendor type")
            front_score += 20
        
        return {
            "is_likely_front": front_score >= 50,
            "front_score": min(100, front_score),
            "indicators": indicators,
            "fraud_type": "front_operation"
        }
    
    def detect_cash_layering(self, business_data: Dict, transaction_data: Dict = None) -> Dict:
        indicators = []
        layering_score = 0
        
        if business_data["business_type"] not in SMALL_VENDOR_TYPES:
            return {"is_likely_layering": False, "layering_score": 0, "indicators": [], "fraud_type": "cash_layering"}
        
        if transaction_data:
            cash_deposits = transaction_data.get("cash_deposit_total", 0)
            declared_rev = business_data["declared_revenue"]
            
            if cash_deposits > declared_rev * 0.5:
                indicators.append(f"Cash deposits (₹{cash_deposits:,.0f}) exceed 50% of declared revenue")
                layering_score += 30
            
            threshold_txns = transaction_data.get("threshold_transaction_count", 0)
            if threshold_txns >= 3:
                indicators.append(f"{threshold_txns} transactions just below ₹50,000 threshold - structuring suspected")
                layering_score += 35
            
            round_txns = transaction_data.get("round_transaction_count", 0)
            total_txns = transaction_data.get("transaction_count", 1)
            if round_txns > total_txns * 0.4:
                indicators.append("High proportion of round figure transactions")
                layering_score += 20
        
        if business_data.get("connected_to_high_value", False):
            indicators.append("Connections to high-value businesses - potential layering point")
            layering_score += 25
        
        return {
            "is_likely_layering": layering_score >= 50,
            "layering_score": min(100, layering_score),
            "indicators": indicators,
            "fraud_type": "cash_layering"
        }
    
    def detect_vendor_network_fraud(self, business_data: Dict, network_data: Dict = None) -> Dict:
        indicators = []
        network_score = 0
        
        if network_data:
            connected_vendors = network_data.get("connected_vendor_count", 0)
            if connected_vendors >= 5:
                indicators.append(f"Connected to {connected_vendors} other vendors - potential network")
                network_score += 25
            
            common_supplier = network_data.get("common_supplier_connections", 0)
            if common_supplier >= 3:
                indicators.append("Multiple vendors with common supplier - circular arrangement possible")
                network_score += 30
            
            shared_address = network_data.get("shared_address_count", 0)
            if shared_address >= 2:
                indicators.append(f"{shared_address} entities at same address - shell network indicator")
                network_score += 35
            
            family_connections = network_data.get("family_business_count", 0)
            if family_connections >= 3:
                indicators.append(f"{family_connections} family-connected businesses - benami network possible")
                network_score += 25
        
        return {
            "is_likely_network_fraud": network_score >= 50,
            "network_score": min(100, network_score),
            "indicators": indicators,
            "fraud_type": "vendor_network"
        }
    
    def run_all_fraud_checks(self, business_data: Dict, lifestyle_data: Dict = None, 
                             transaction_data: Dict = None, network_data: Dict = None) -> Dict:
        checks = {}
        
        checks["shell_company"] = self.detect_shell_company(business_data)
        checks["money_laundering"] = self.detect_money_laundering(business_data)
        checks["black_money"] = self.detect_black_money(business_data)
        checks["circular_trading"] = self.detect_circular_trading(business_data)
        checks["benami_property"] = self.detect_benami_property(business_data)
        
        if business_data["business_type"] in SMALL_VENDOR_TYPES:
            checks["front_operation"] = self.detect_front_operation(business_data, lifestyle_data)
            checks["cash_layering"] = self.detect_cash_layering(business_data, transaction_data)
            checks["vendor_network"] = self.detect_vendor_network_fraud(business_data, network_data)
        
        return checks
    
    def analyze_business(self, business_data: Dict, lifestyle_data: Dict = None,
                        transaction_data: Dict = None, network_data: Dict = None) -> Dict[str, Any]:
        anomaly_scores = {}
        risk_factors = []
        detailed_analysis = {}
        matched_patterns = []
        
        benchmarks = BUSINESS_BENCHMARKS.get(
            business_data["business_type"],
            BUSINESS_BENCHMARKS["Small Shop"]
        )
        
        expected = calculate_expected_metrics(
            business_data["business_type"],
            business_data["num_outlets"],
            business_data["total_land_sqft"]
        )
        
        all_fraud_checks = self.run_all_fraud_checks(
            business_data, lifestyle_data, transaction_data, network_data
        )
        
        for check_name, check_result in all_fraud_checks.items():
            score_key = f"{check_name}_score"
            if score_key.replace("_score", "_score") in str(check_result):
                for key, value in check_result.items():
                    if "score" in key and isinstance(value, (int, float)):
                        anomaly_scores[check_name] = value
            
            is_flagged_key = [k for k in check_result.keys() if k.startswith("is_likely")]
            if is_flagged_key and check_result.get(is_flagged_key[0], False):
                score_val = check_result.get(list(check_result.keys())[1], 50)
                matched_patterns.append({
                    "type": check_result.get("fraud_type", check_name).replace("_", " ").title(),
                    "score": score_val,
                    "indicators": check_result.get("indicators", [])
                })
                
                for indicator in check_result.get("indicators", []):
                    risk_factors.append({
                        "factor": f"{check_name.replace('_', ' ').title()} Indicator",
                        "severity": "HIGH",
                        "description": indicator,
                        "score": score_val
                    })
        
        expected_elec = expected["electricity_range"]
        actual_elec = business_data["electricity_consumption_kwh"]
        if actual_elec < expected_elec[0] * 0.5 or actual_elec > expected_elec[1] * 2:
            anomaly_scores["electricity_anomaly"] = min(100, abs(actual_elec - np.mean(expected_elec)) / max(np.mean(expected_elec), 1) * 50)
            risk_factors.append({
                "factor": "Electricity Consumption Anomaly",
                "severity": "MEDIUM" if anomaly_scores["electricity_anomaly"] < 50 else "HIGH",
                "description": f"Consumption {actual_elec} kWh outside expected range {expected_elec[0]:.0f}-{expected_elec[1]:.0f} kWh",
                "score": anomaly_scores["electricity_anomaly"]
            })
        
        expected_rev = expected["revenue_range"]
        actual_rev = business_data["declared_revenue"]
        if actual_rev < expected_rev[0] * 0.5 or actual_rev > expected_rev[1] * 2:
            anomaly_scores["revenue_anomaly"] = min(100, abs(actual_rev - np.mean(expected_rev)) / max(np.mean(expected_rev), 1) * 50)
            risk_factors.append({
                "factor": "Revenue Anomaly",
                "severity": "MEDIUM" if anomaly_scores["revenue_anomaly"] < 50 else "HIGH",
                "description": f"Revenue ₹{actual_rev:,.0f} outside expected range ₹{expected_rev[0]:,.0f}-₹{expected_rev[1]:,.0f}",
                "score": anomaly_scores["revenue_anomaly"]
            })
        
        expected_emp = expected["employees_range"]
        actual_emp = business_data["num_employees"]
        if actual_emp < expected_emp[0] * 0.5 or actual_emp > expected_emp[1] * 2:
            anomaly_scores["employee_anomaly"] = min(100, abs(actual_emp - np.mean(expected_emp)) / max(np.mean(expected_emp), 1) * 50)
            risk_factors.append({
                "factor": "Employee Count Anomaly",
                "severity": "MEDIUM",
                "description": f"{actual_emp} employees outside expected range {expected_emp[0]:.0f}-{expected_emp[1]:.0f}",
                "score": anomaly_scores["employee_anomaly"]
            })
        
        input_df = pd.DataFrame([{
            "business_type": business_data["business_type"],
            "num_outlets": business_data["num_outlets"],
            "total_land_sqft": business_data["total_land_sqft"],
            "region": business_data["region"],
            "land_rate_per_sqft": business_data["land_rate_per_sqft"],
            "electricity_consumption_kwh": business_data["electricity_consumption_kwh"],
            "declared_revenue": business_data["declared_revenue"],
            "declared_tax_paid": business_data["declared_tax_paid"],
            "num_employees": business_data["num_employees"],
            "is_stock_listed": business_data.get("is_stock_listed", False),
            "tycoon_connection_level": business_data.get("tycoon_connection_level", "None"),
            "years_in_operation": business_data.get("years_in_operation", 5)
        }])
        
        features = self._extract_features(input_df)
        scaled_features = self.scaler.transform(features)
        
        if_score = self.isolation_forest.decision_function(scaled_features)[0]
        if_normalized = (1 - (if_score + 0.5)) * 100
        if_normalized = max(0, min(100, if_normalized))
        
        rf_proba = self.random_forest.predict_proba(scaled_features)[0][1] * 100
        
        if self.xgboost_model is not None:
            xgb_proba = self.xgboost_model.predict_proba(scaled_features)[0][1] * 100
            ml_ensemble = (if_normalized * 0.3 + rf_proba * 0.35 + xgb_proba * 0.35)
        else:
            xgb_proba = rf_proba
            ml_ensemble = (if_normalized * 0.4 + rf_proba * 0.6)
        
        ml_scores_detail = {
            "isolation_forest_score": if_normalized,
            "random_forest_score": rf_proba,
            "xgboost_score": xgb_proba,
            "ensemble_score": ml_ensemble
        }
        
        pattern_score = sum(p["score"] for p in matched_patterns) / max(len(matched_patterns), 1) if matched_patterns else 0
        anomaly_avg = np.mean(list(anomaly_scores.values())) if anomaly_scores else 0
        
        fraud_probability = (ml_ensemble * 0.4 + pattern_score * 0.35 + anomaly_avg * 0.25)
        fraud_probability = min(100, max(0, fraud_probability))
        
        if fraud_probability >= 80:
            risk_level = "CRITICAL"
        elif fraud_probability >= 60:
            risk_level = "VERY HIGH"
        elif fraud_probability >= 40:
            risk_level = "HIGH"
        elif fraud_probability >= 25:
            risk_level = "MODERATE"
        else:
            risk_level = "LOW"
        
        recommendations = {
            "LOW": "Standard periodic monitoring. No immediate action required.",
            "MODERATE": "Enhanced scrutiny recommended. Request additional documentation within 30 days.",
            "HIGH": "Initiate preliminary investigation under Section 131. Request comprehensive records.",
            "VERY HIGH": "Urgent detailed audit required. Consider Section 142(2A) special audit.",
            "CRITICAL": "Immediate multi-agency investigation. Consider search under Section 132."
        }
        
        similar_cases = []
        if matched_patterns:
            fraud_indicators = []
            for pattern in matched_patterns:
                fraud_indicators.extend(pattern.get("indicators", []))
            similar_cases = get_similar_fraud_cases(fraud_indicators)
        
        return {
            "fraud_probability": round(fraud_probability, 1),
            "risk_level": risk_level,
            "ml_score": round(ml_ensemble, 1),
            "ml_scores_detail": ml_scores_detail,
            "anomaly_scores": anomaly_scores,
            "risk_factors": sorted(risk_factors, key=lambda x: x["score"], reverse=True),
            "matched_fraud_patterns": matched_patterns,
            "detailed_analysis": detailed_analysis,
            "similar_cases": similar_cases,
            "recommendation": recommendations[risk_level],
            "all_fraud_checks": all_fraud_checks,
            "is_small_vendor": business_data["business_type"] in SMALL_VENDOR_TYPES
        }


fraud_engine = FraudDetectionEngine()
