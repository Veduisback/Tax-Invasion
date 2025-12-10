import os
import json
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime
from collections import defaultdict

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


class FraudNetworkAnalyzer:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.clusters = {}
        
    def add_entity(self, entity_id: str, entity_data: Dict) -> None:
        self.nodes[entity_id] = {
            "id": entity_id,
            "type": entity_data.get("type", "unknown"),
            "name": entity_data.get("name", "Unknown"),
            "risk_score": entity_data.get("risk_score", 0),
            "data": entity_data
        }
    
    def add_connection(
        self, 
        from_id: str, 
        to_id: str, 
        connection_type: str,
        strength: float = 0.5,
        metadata: Optional[Dict] = None
    ) -> None:
        self.edges.append({
            "from": from_id,
            "to": to_id,
            "type": connection_type,
            "strength": strength,
            "metadata": metadata or {}
        })
    
    def analyze_network(self) -> Dict:
        suspicious_connections = []
        high_risk_clusters = []
        network_risk_score = 0
        
        connection_counts = defaultdict(int)
        for edge in self.edges:
            connection_counts[edge["from"]] += 1
            connection_counts[edge["to"]] += 1
        
        hub_entities = [
            entity_id for entity_id, count in connection_counts.items()
            if count > 3
        ]
        
        for entity_id in hub_entities:
            entity = self.nodes.get(entity_id, {})
            if entity.get("risk_score", 0) > 50:
                high_risk_clusters.append({
                    "hub": entity_id,
                    "hub_name": entity.get("name", "Unknown"),
                    "connection_count": connection_counts[entity_id],
                    "risk_score": entity.get("risk_score", 0)
                })
                network_risk_score += 15
        
        for edge in self.edges:
            from_entity = self.nodes.get(edge["from"], {})
            to_entity = self.nodes.get(edge["to"], {})
            
            if edge["type"] == "financial":
                if from_entity.get("type") == "small_vendor" and to_entity.get("type") == "high_value_business":
                    suspicious_connections.append({
                        "from": edge["from"],
                        "from_name": from_entity.get("name"),
                        "to": edge["to"],
                        "to_name": to_entity.get("name"),
                        "type": "vendor_to_business_flow",
                        "risk": "HIGH",
                        "description": "Financial flow from small vendor to high-value business - potential layering"
                    })
                    network_risk_score += 20
            
            if edge["type"] == "family":
                if from_entity.get("risk_score", 0) > 60 or to_entity.get("risk_score", 0) > 60:
                    suspicious_connections.append({
                        "from": edge["from"],
                        "from_name": from_entity.get("name"),
                        "to": edge["to"],
                        "to_name": to_entity.get("name"),
                        "type": "family_connection",
                        "risk": "MEDIUM",
                        "description": "Family connection to high-risk entity - potential benami operation"
                    })
                    network_risk_score += 10
            
            if edge["type"] == "common_address":
                suspicious_connections.append({
                    "from": edge["from"],
                    "from_name": from_entity.get("name"),
                    "to": edge["to"],
                    "to_name": to_entity.get("name"),
                    "type": "shared_location",
                    "risk": "MEDIUM",
                    "description": "Entities sharing same address - possible shell network"
                })
                network_risk_score += 8
        
        return {
            "total_entities": len(self.nodes),
            "total_connections": len(self.edges),
            "hub_entities": hub_entities,
            "high_risk_clusters": high_risk_clusters,
            "suspicious_connections": suspicious_connections,
            "network_risk_score": min(100, network_risk_score),
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def find_connected_entities(self, entity_id: str, max_depth: int = 2) -> List[Dict]:
        visited = set()
        connected = []
        
        def dfs(current_id: str, depth: int, path: List[str]):
            if depth > max_depth or current_id in visited:
                return
            
            visited.add(current_id)
            
            if current_id != entity_id:
                connected.append({
                    "entity_id": current_id,
                    "entity": self.nodes.get(current_id, {}),
                    "distance": depth,
                    "path": path
                })
            
            for edge in self.edges:
                next_id = None
                if edge["from"] == current_id:
                    next_id = edge["to"]
                elif edge["to"] == current_id:
                    next_id = edge["from"]
                
                if next_id and next_id not in visited:
                    dfs(next_id, depth + 1, path + [edge["type"]])
        
        dfs(entity_id, 0, [])
        return connected
    
    def get_network_visualization_data(self) -> Dict:
        nodes_list = []
        for node_id, node_data in self.nodes.items():
            risk = node_data.get("risk_score", 0)
            if risk > 70:
                color = "#dc3545"
            elif risk > 50:
                color = "#fd7e14"
            elif risk > 30:
                color = "#ffc107"
            else:
                color = "#28a745"
            
            nodes_list.append({
                "id": node_id,
                "label": node_data.get("name", node_id)[:20],
                "type": node_data.get("type", "unknown"),
                "risk_score": risk,
                "color": color,
                "size": 10 + (risk / 10)
            })
        
        edges_list = []
        for edge in self.edges:
            edge_color = "#999999"
            if edge["type"] == "financial":
                edge_color = "#dc3545"
            elif edge["type"] == "family":
                edge_color = "#007bff"
            elif edge["type"] == "business":
                edge_color = "#28a745"
            
            edges_list.append({
                "from": edge["from"],
                "to": edge["to"],
                "type": edge["type"],
                "color": edge_color,
                "width": 1 + edge.get("strength", 0.5) * 3
            })
        
        return {
            "nodes": nodes_list,
            "edges": edges_list
        }


def build_vendor_network(
    primary_vendor: Dict,
    related_entities: List[Dict],
    transactions: Optional[List[Dict]] = None
) -> FraudNetworkAnalyzer:
    analyzer = FraudNetworkAnalyzer()
    
    primary_id = primary_vendor.get("id", "primary")
    analyzer.add_entity(primary_id, {
        "type": "small_vendor",
        "name": primary_vendor.get("name", "Primary Vendor"),
        "risk_score": primary_vendor.get("risk_score", 50),
        "business_type": primary_vendor.get("business_type", "Unknown"),
        "declared_revenue": primary_vendor.get("declared_revenue", 0)
    })
    
    for entity in related_entities:
        entity_id = entity.get("id", f"entity_{len(analyzer.nodes)}")
        analyzer.add_entity(entity_id, {
            "type": entity.get("type", "person"),
            "name": entity.get("name", "Unknown"),
            "risk_score": entity.get("risk_score", 0),
            "relationship": entity.get("relationship")
        })
        
        analyzer.add_connection(
            primary_id,
            entity_id,
            entity.get("connection_type", "associated"),
            entity.get("connection_strength", 0.5),
            {"relationship": entity.get("relationship")}
        )
    
    if transactions:
        counterparties = defaultdict(lambda: {"count": 0, "total": 0})
        for txn in transactions:
            counterparty = txn.get("counterparty")
            if counterparty:
                counterparties[counterparty]["count"] += 1
                counterparties[counterparty]["total"] += txn.get("amount", 0)
        
        for counterparty, data in counterparties.items():
            if data["count"] >= 3 or data["total"] >= 100000:
                cp_id = f"cp_{counterparty[:10]}"
                if cp_id not in analyzer.nodes:
                    analyzer.add_entity(cp_id, {
                        "type": "counterparty",
                        "name": counterparty,
                        "risk_score": 30 if data["total"] > 500000 else 15,
                        "transaction_count": data["count"],
                        "total_value": data["total"]
                    })
                    analyzer.add_connection(
                        primary_id,
                        cp_id,
                        "financial",
                        min(1.0, data["total"] / 1000000),
                        {"transaction_count": data["count"], "total_value": data["total"]}
                    )
    
    return analyzer


def detect_shell_network_patterns(network: FraudNetworkAnalyzer) -> Dict:
    patterns = []
    risk_indicators = []
    
    address_groups = defaultdict(list)
    for node_id, node_data in network.nodes.items():
        address = node_data.get("data", {}).get("address")
        if address:
            address_groups[address].append(node_id)
    
    for address, entities in address_groups.items():
        if len(entities) > 2:
            patterns.append({
                "type": "shared_address",
                "entities": entities,
                "count": len(entities),
                "risk": "HIGH" if len(entities) > 5 else "MEDIUM",
                "description": f"{len(entities)} entities registered at same address"
            })
    
    director_groups = defaultdict(list)
    for node_id, node_data in network.nodes.items():
        directors = node_data.get("data", {}).get("directors", [])
        for director in directors:
            director_groups[director].append(node_id)
    
    for director, companies in director_groups.items():
        if len(companies) > 3:
            patterns.append({
                "type": "common_director",
                "director": director,
                "companies": companies,
                "count": len(companies),
                "risk": "HIGH",
                "description": f"Same director in {len(companies)} entities - shell network indicator"
            })
    
    analysis_result = network.analyze_network()
    for cluster in analysis_result.get("high_risk_clusters", []):
        patterns.append({
            "type": "high_risk_hub",
            "hub": cluster["hub"],
            "hub_name": cluster["hub_name"],
            "connections": cluster["connection_count"],
            "risk": "CRITICAL" if cluster["risk_score"] > 70 else "HIGH",
            "description": f"Central hub with {cluster['connection_count']} connections and {cluster['risk_score']}% risk"
        })
    
    for pattern in patterns:
        risk_indicators.append({
            "indicator": pattern["type"],
            "severity": pattern["risk"],
            "description": pattern["description"]
        })
    
    shell_network_score = len([p for p in patterns if p["risk"] in ["HIGH", "CRITICAL"]]) * 20
    shell_network_score += len([p for p in patterns if p["risk"] == "MEDIUM"]) * 10
    
    return {
        "patterns_detected": patterns,
        "risk_indicators": risk_indicators,
        "shell_network_probability": min(100, shell_network_score),
        "is_likely_shell_network": shell_network_score >= 50,
        "recommendation": get_shell_network_recommendation(shell_network_score)
    }


def get_shell_network_recommendation(score: int) -> str:
    if score >= 70:
        return """CRITICAL - SHELL NETWORK DETECTED:
1. Immediately report to Investigation Wing
2. Coordinate with SFIO for company law violations
3. Request forensic audit of all linked entities
4. Consider prosecution under Section 276C
5. File report with FIU-IND for PMLA action"""
    elif score >= 50:
        return """HIGH RISK - LIKELY SHELL NETWORK:
1. Initiate comprehensive investigation
2. Verify physical existence of all linked entities
3. Trace beneficial ownership
4. Request bank statements for all entities
5. Cross-verify with ROC/MCA records"""
    elif score >= 30:
        return """MODERATE RISK:
1. Enhanced due diligence on linked entities
2. Verify legitimacy of business operations
3. Request supporting documents
4. Monitor for additional connections"""
    else:
        return "LOW RISK: Standard monitoring. Keep records updated."


def analyze_vendor_network_ai(
    vendor_data: Dict,
    network_data: Dict
) -> str:
    if not openai_client:
        return generate_fallback_network_analysis(vendor_data, network_data)
    
    try:
        prompt = f"""As a senior tax fraud investigator, analyze this vendor's network connections for potential fraud patterns.

VENDOR DATA:
{json.dumps(vendor_data, indent=2)}

NETWORK ANALYSIS:
{json.dumps(network_data, indent=2)}

Provide analysis including:
1. Network Structure Assessment
2. Suspicious Connection Patterns
3. Shell Network Indicators
4. Potential Fraud Schemes
5. Risk Level for Each Connected Entity
6. Recommended Investigation Actions
7. Legal Provisions Applicable

Focus on patterns like:
- Front operations for larger businesses
- Cash layering networks
- Benami property connections
- Circular trading arrangements
- Common director/address patterns"""

        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in financial network analysis for tax fraud detection in India. You can identify shell company networks, benami arrangements, and money laundering structures."
                },
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=2048
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Network AI analysis error: {e}")
        return generate_fallback_network_analysis(vendor_data, network_data)


def generate_fallback_network_analysis(vendor_data: Dict, network_data: Dict) -> str:
    report = f"""## Network Analysis Report

### Primary Entity
- Name: {vendor_data.get('name', 'Unknown')}
- Type: {vendor_data.get('business_type', 'Unknown')}
- Declared Revenue: ₹{vendor_data.get('declared_revenue', 0):,.0f}

### Network Statistics
- Total Entities: {network_data.get('total_entities', 0)}
- Total Connections: {network_data.get('total_connections', 0)}
- Hub Entities: {len(network_data.get('hub_entities', []))}
- Network Risk Score: {network_data.get('network_risk_score', 0)}/100

### Suspicious Connections
"""
    
    for conn in network_data.get('suspicious_connections', []):
        report += f"- [{conn['risk']}] {conn['from_name']} → {conn['to_name']}: {conn['description']}\n"
    
    if not network_data.get('suspicious_connections'):
        report += "- No suspicious connections identified\n"
    
    report += f"""
### High Risk Clusters
"""
    for cluster in network_data.get('high_risk_clusters', []):
        report += f"- Hub: {cluster['hub_name']} (Risk: {cluster['risk_score']}%, Connections: {cluster['connection_count']})\n"
    
    if not network_data.get('high_risk_clusters'):
        report += "- No high-risk clusters identified\n"
    
    report += f"""
### Recommendation
Based on network analysis, {"ENHANCED INVESTIGATION RECOMMENDED" if network_data.get('network_risk_score', 0) > 50 else "Standard monitoring sufficient"}.

Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return report


def create_network_graph_html(network_data: Dict) -> str:
    nodes_json = json.dumps(network_data.get("nodes", []))
    edges_json = json.dumps(network_data.get("edges", []))
    
    html = f"""
    <div id="network-graph" style="width: 100%; height: 500px; border: 1px solid #ddd; border-radius: 8px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.6/dist/vis-network.min.js"></script>
    <script>
        var nodes = new vis.DataSet({nodes_json});
        var edges = new vis.DataSet({edges_json});
        
        var container = document.getElementById('network-graph');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                shape: 'dot',
                font: {{ size: 12 }}
            }},
            edges: {{
                arrows: 'to',
                smooth: {{ type: 'curvedCW' }}
            }},
            physics: {{
                stabilization: true,
                barnesHut: {{
                    gravitationalConstant: -2000,
                    springLength: 150
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100
            }}
        }};
        
        var network = new vis.Network(container, data, options);
    </script>
    """
    
    return html
