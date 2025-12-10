import trafilatura
import os
from typing import Dict, List, Optional
from datetime import datetime

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_AVAILABLE and OPENAI_API_KEY else None


def get_website_text_content(url: str) -> str:
    try:
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(downloaded)
        return text if text else ""
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return ""


NEWS_SOURCES = [
    {"name": "Economic Times - Tax", "url": "https://economictimes.indiatimes.com/news/economy/policy", "category": "tax_news"},
    {"name": "Business Standard - Tax", "url": "https://www.business-standard.com/economy/news", "category": "tax_news"},
    {"name": "LiveLaw - Tax", "url": "https://www.livelaw.in/tax-cases", "category": "legal_cases"},
    {"name": "Financial Express", "url": "https://www.financialexpress.com/market/", "category": "financial_news"},
    {"name": "Mint - Tax", "url": "https://www.livemint.com/economy", "category": "tax_news"},
    {"name": "Income Tax India", "url": "https://www.incometax.gov.in/iec/foportal/", "category": "official"},
    {"name": "Moneycontrol - Tax", "url": "https://www.moneycontrol.com/news/business/economy/", "category": "financial_news"},
    {"name": "NDTV Profit", "url": "https://www.ndtv.com/business", "category": "financial_news"},
    {"name": "Hindu Business Line", "url": "https://www.thehindubusinessline.com/economy/", "category": "financial_news"},
    {"name": "Times of India - Business", "url": "https://timesofindia.indiatimes.com/business", "category": "financial_news"},
    {"name": "Tax Guru", "url": "https://taxguru.in/", "category": "tax_news"},
    {"name": "CAclubindia", "url": "https://www.caclubindia.com/", "category": "tax_news"}
]

FRAUD_KEYWORDS = [
    "tax fraud", "tax evasion", "black money", "money laundering",
    "shell company", "benami property", "IT raid", "income tax raid",
    "ED raid", "enforcement directorate", "search and seizure",
    "tax default", "GST fraud", "fake invoice", "circular trading",
    "hawala", "undisclosed income", "offshore accounts",
    "PMLA", "FEMA violation", "bogus deductions", "TDS fraud",
    "street vendor", "small vendor", "cash layering"
]


def scrape_news_for_fraud_patterns() -> List[Dict]:
    articles = []
    
    for source in NEWS_SOURCES:
        try:
            content = get_website_text_content(source["url"])
            if content:
                is_relevant = any(keyword.lower() in content.lower() for keyword in FRAUD_KEYWORDS)
                
                if is_relevant:
                    articles.append({
                        "title": f"Content from {source['name']}",
                        "url": source["url"],
                        "source": source["name"],
                        "category": source["category"],
                        "content": content[:5000],
                        "scraped_at": datetime.now().isoformat(),
                        "is_relevant": is_relevant
                    })
        except Exception as e:
            print(f"Error scraping {source['name']}: {e}")
            continue
    
    return articles


def extract_fraud_patterns_from_text(text: str) -> Dict:
    if not openai_client:
        return extract_patterns_rule_based(text)
    
    try:
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at analyzing news articles about tax fraud in India.
                    Extract key information and return a JSON object with:
                    - fraud_types: list of fraud types mentioned
                    - detection_methods: list of how the fraud was detected
                    - key_indicators: list of red flags mentioned
                    - entities: list of companies/individuals mentioned
                    - amount_crore: estimated fraud amount in crores (number or null)
                    - legal_provisions: list of legal sections mentioned"""
                },
                {"role": "user", "content": f"Analyze this text for fraud patterns:\n\n{text[:4000]}"}
            ],
            response_format={"type": "json_object"},
            max_completion_tokens=1024
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"AI extraction error: {e}")
        return extract_patterns_rule_based(text)


def extract_patterns_rule_based(text: str) -> Dict:
    text_lower = text.lower()
    
    fraud_types = []
    if any(word in text_lower for word in ["shell company", "paper company", "dummy company"]):
        fraud_types.append("shell_company")
    if any(word in text_lower for word in ["money laundering", "layering", "pmla"]):
        fraud_types.append("money_laundering")
    if any(word in text_lower for word in ["tax evasion", "tax fraud", "undisclosed income"]):
        fraud_types.append("tax_evasion")
    if any(word in text_lower for word in ["circular trading", "fake invoice", "bogus invoice"]):
        fraud_types.append("circular_trading")
    if any(word in text_lower for word in ["black money", "cash hoarding", "unaccounted cash"]):
        fraud_types.append("black_money")
    if any(word in text_lower for word in ["benami", "benami property", "benami transaction"]):
        fraud_types.append("benami_property")
    if any(word in text_lower for word in ["street vendor", "small vendor", "front operation"]):
        fraud_types.append("front_operation")
    
    detection_methods = []
    if "raid" in text_lower or "search and seizure" in text_lower:
        detection_methods.append("IT Department Raid")
    if "gst" in text_lower and ("mismatch" in text_lower or "analysis" in text_lower):
        detection_methods.append("GST Data Analytics")
    if "bank" in text_lower and ("statement" in text_lower or "transaction" in text_lower):
        detection_methods.append("Bank Transaction Analysis")
    if "whistle" in text_lower or "complaint" in text_lower:
        detection_methods.append("Whistleblower/Complaint")
    
    key_indicators = []
    if "low electricity" in text_lower or "minimal operations" in text_lower:
        key_indicators.append("Low operational footprint")
    if "cash" in text_lower and ("heavy" in text_lower or "intensive" in text_lower):
        key_indicators.append("Cash-intensive operations")
    if "mismatch" in text_lower:
        key_indicators.append("Data mismatch in filings")
    if "related party" in text_lower or "connected entities" in text_lower:
        key_indicators.append("Related party transactions")
    if "lifestyle" in text_lower and "income" in text_lower:
        key_indicators.append("Lifestyle vs income mismatch")
    
    import re
    amount_match = re.search(r'Rs?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:crore|cr)', text_lower)
    amount_crore = None
    if amount_match:
        try:
            amount_crore = float(amount_match.group(1).replace(',', ''))
        except:
            pass
    
    return {
        "fraud_types": fraud_types,
        "detection_methods": detection_methods,
        "key_indicators": key_indicators,
        "entities": [],
        "amount_crore": amount_crore,
        "legal_provisions": []
    }


def learn_from_news() -> Dict:
    articles = scrape_news_for_fraud_patterns()
    
    learned_patterns = []
    total_articles = len(articles)
    relevant_articles = 0
    
    for article in articles:
        if article.get("is_relevant"):
            relevant_articles += 1
            patterns = extract_fraud_patterns_from_text(article["content"])
            
            if patterns.get("fraud_types") or patterns.get("key_indicators"):
                learned_patterns.append({
                    "source": article["source"],
                    "url": article["url"],
                    "extracted_at": datetime.now().isoformat(),
                    **patterns
                })
    
    return {
        "total_sources_checked": len(NEWS_SOURCES),
        "articles_found": total_articles,
        "relevant_articles": relevant_articles,
        "patterns_extracted": len(learned_patterns),
        "learned_patterns": learned_patterns
    }


def get_fraud_news_summary() -> str:
    if not openai_client:
        return "AI summary not available. Please check OPENAI_API_KEY."
    
    all_content = []
    for source in NEWS_SOURCES[:2]:
        content = get_website_text_content(source["url"])
        if content:
            all_content.append(f"From {source['name']}:\n{content[:2000]}")
    
    if not all_content:
        return "Could not fetch news content."
    
    try:
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {
                    "role": "system",
                    "content": "You are a tax fraud analyst. Summarize the key tax fraud and evasion news from the content. Focus on detection methods, fraud amounts, and new patterns discovered."
                },
                {"role": "user", "content": f"Summarize fraud-related news from:\n\n{chr(10).join(all_content[:6000])}"}
            ],
            max_completion_tokens=1024
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {e}"
