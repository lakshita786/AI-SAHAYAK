"""
SabbiAI Schemes Database
Knowledge base for Indian Government Schemes - handles loading, searching,
filtering, and recommendation of government welfare programs for rural users.
"""

import os
import pandas as pd
from typing import List, Optional, Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SCHEMES_CSV = os.path.join(DATA_DIR, "indian_govt_schemes.csv")

_cache = None


HARDCODED_SCHEMES = [
    {
        "scheme_name": "PM-KISAN Samman Nidhi",
        "ministry": "Agriculture",
        "category": "farmer",
        "eligibility": "Small and marginal farmers with less than 2 hectares land",
        "min_age": 18,
        "max_age": 99,
        "max_income": 120000,
        "occupation_type": "farmer",
        "benefits": "Rs 6000 per year in 3 installments of Rs 2000",
        "state_specific": "all",
        "apply_link": "https://pmkisan.gov.in",
    },
    {
        "scheme_name": "MGNREGA",
        "ministry": "Rural Development",
        "category": "employment",
        "eligibility": "Any rural household adult willing to do unskilled manual work",
        "min_age": 18,
        "max_age": 60,
        "max_income": 180000,
        "occupation_type": "all",
        "benefits": "100 days guaranteed wage employment per year",
        "state_specific": "all",
        "apply_link": "https://nrega.nic.in",
    },
    {
        "scheme_name": "PMEGP",
        "ministry": "MSME",
        "category": "finance",
        "eligibility": "Any individual above 18 years, SHGs, institutions",
        "min_age": 18,
        "max_age": 99,
        "max_income": 999999,
        "occupation_type": "artisan,small_trader",
        "benefits": "Subsidy 15-35% on project cost up to Rs 50 lakh",
        "state_specific": "all",
        "apply_link": "https://www.kviconline.gov.in/pmegpeportal",
    },
    {
        "scheme_name": "PM Awas Yojana Gramin",
        "ministry": "Rural Development",
        "category": "housing",
        "eligibility": "Homeless or kutcha house owners in rural areas, BPL families",
        "min_age": 18,
        "max_age": 99,
        "max_income": 120000,
        "occupation_type": "all",
        "benefits": "Rs 1.2 lakh in plains, Rs 1.3 lakh in hilly areas for house",
        "state_specific": "all",
        "apply_link": "https://pmayg.nic.in",
    },
    {
        "scheme_name": "Ayushman Bharat PM-JAY",
        "ministry": "Health",
        "category": "health",
        "eligibility": "Bottom 40% poor and vulnerable families per SECC database",
        "min_age": 0,
        "max_age": 99,
        "max_income": 120000,
        "occupation_type": "all",
        "benefits": "Health cover Rs 5 lakh per family per year for secondary care",
        "state_specific": "all",
        "apply_link": "https://pmjay.gov.in",
    },
    {
        "scheme_name": "MUDRA Loan - Shishu",
        "ministry": "Finance",
        "category": "finance",
        "eligibility": "Small business owners, artisans, shopkeepers",
        "min_age": 18,
        "max_age": 65,
        "max_income": 300000,
        "occupation_type": "artisan,small_trader",
        "benefits": "Loans up to Rs 50000 at low interest, no collateral",
        "state_specific": "all",
        "apply_link": "https://www.mudra.org.in",
    },
    {
        "scheme_name": "DDU-Grameen Kaushalya Yojana",
        "ministry": "Rural Development",
        "category": "skill",
        "eligibility": "Rural youth aged 15-35 from poor families",
        "min_age": 15,
        "max_age": 35,
        "max_income": 120000,
        "occupation_type": "all",
        "benefits": "Free skill training + placement assistance + post-placement support",
        "state_specific": "all",
        "apply_link": "https://ddugky.gov.in",
    },
    {
        "scheme_name": "PM Kaushal Vikas Yojana",
        "ministry": "Skill Development",
        "category": "skill",
        "eligibility": "Indian nationals, school/college dropouts or unemployed youth",
        "min_age": 15,
        "max_age": 45,
        "max_income": 999999,
        "occupation_type": "all",
        "benefits": "Free short-term skill training with Rs 8000 reward on completion",
        "state_specific": "all",
        "apply_link": "https://www.pmkvyofficial.org",
    },
    {
        "scheme_name": "Kisan Credit Card",
        "ministry": "Agriculture",
        "category": "finance",
        "eligibility": "Farmers, sharecroppers, tenant farmers, SHG members",
        "min_age": 18,
        "max_age": 75,
        "max_income": 999999,
        "occupation_type": "farmer",
        "benefits": "Flexible credit for farming needs at 4% interest rate",
        "state_specific": "all",
        "apply_link": "https://www.nabard.org",
    },
    {
        "scheme_name": "PM Fasal Bima Yojana",
        "ministry": "Agriculture",
        "category": "farmer",
        "eligibility": "All farmers including sharecroppers growing notified crops",
        "min_age": 18,
        "max_age": 99,
        "max_income": 999999,
        "occupation_type": "farmer",
        "benefits": "Crop insurance at 2% premium for kharif, 1.5% for rabi crops",
        "state_specific": "all",
        "apply_link": "https://pmfby.gov.in",
    },
    {
        "scheme_name": "National Rural Livelihood Mission",
        "ministry": "Rural Development",
        "category": "livelihood",
        "eligibility": "Rural poor women, preference to SC/ST/BPL families",
        "min_age": 18,
        "max_age": 60,
        "max_income": 120000,
        "occupation_type": "all",
        "benefits": "SHG formation, bank linkage, skill training, revolving fund",
        "state_specific": "all",
        "apply_link": "https://aajeevika.gov.in",
    },
    {
        "scheme_name": "PM SVANidhi",
        "ministry": "Housing and Urban Affairs",
        "category": "finance",
        "eligibility": "Street vendors who were vending before March 24 2020",
        "min_age": 18,
        "max_age": 65,
        "max_income": 200000,
        "occupation_type": "small_trader",
        "benefits": "Working capital loan Rs 10000 then 20000 then 50000 with subsidy",
        "state_specific": "all",
        "apply_link": "https://pmsvanidhi.mohua.gov.in",
    },
    {
        "scheme_name": "Atal Pension Yojana",
        "ministry": "Finance",
        "category": "pension",
        "eligibility": "Unorganised sector workers aged 18-40 with bank account",
        "min_age": 18,
        "max_age": 40,
        "max_income": 999999,
        "occupation_type": "all",
        "benefits": "Guaranteed pension Rs 1000-5000 per month after age 60",
        "state_specific": "all",
        "apply_link": "https://npscra.nsdl.co.in",
    },
    {
        "scheme_name": "Sukanya Samriddhi Yojana",
        "ministry": "Finance",
        "category": "savings",
        "eligibility": "Parents/guardians of girl child below 10 years",
        "min_age": 18,
        "max_age": 99,
        "max_income": 999999,
        "occupation_type": "all",
        "benefits": "High interest savings scheme 8.2% for girl child education/marriage",
        "state_specific": "all",
        "apply_link": "https://www.indiapost.gov.in",
    },
    {
        "scheme_name": "Janani Suraksha Yojana",
        "ministry": "Health",
        "category": "health",
        "eligibility": "Pregnant women from BPL families for institutional delivery",
        "min_age": 19,
        "max_age": 45,
        "max_income": 120000,
        "occupation_type": "all",
        "benefits": "Cash Rs 1400 (rural) Rs 1000 (urban) for hospital delivery",
        "state_specific": "all",
        "apply_link": "https://nhm.gov.in",
    },
    {
        "scheme_name": "PM Ujjwala Yojana",
        "ministry": "Petroleum",
        "category": "livelihood",
        "eligibility": "Women from BPL households without LPG connection",
        "min_age": 18,
        "max_age": 99,
        "max_income": 120000,
        "occupation_type": "all",
        "benefits": "Free LPG connection with first refill and stove free",
        "state_specific": "all",
        "apply_link": "https://www.pmuy.gov.in",
    },
    {
        "scheme_name": "National Scholarship Portal Schemes",
        "ministry": "Education",
        "category": "education",
        "eligibility": "Students from minority/SC/ST/OBC communities with 50%+ marks",
        "min_age": 6,
        "max_age": 30,
        "max_income": 200000,
        "occupation_type": "all",
        "benefits": "Scholarships Rs 1000-25000 per year for education",
        "state_specific": "all",
        "apply_link": "https://scholarships.gov.in",
    },
    {
        "scheme_name": "PMEGP - Women Entrepreneur",
        "ministry": "MSME",
        "category": "finance",
        "eligibility": "Women entrepreneurs starting new enterprise",
        "min_age": 18,
        "max_age": 99,
        "max_income": 999999,
        "occupation_type": "artisan,small_trader",
        "benefits": "Higher subsidy 25-35% on project cost up to Rs 25 lakh",
        "state_specific": "all",
        "apply_link": "https://www.kviconline.gov.in",
    },
    {
        "scheme_name": "Deen Dayal Gram Jyoti Yojana",
        "ministry": "Power",
        "category": "infrastructure",
        "eligibility": "Rural households without electricity connection",
        "min_age": 18,
        "max_age": 99,
        "max_income": 120000,
        "occupation_type": "all",
        "benefits": "Free electricity connection for BPL rural households",
        "state_specific": "all",
        "apply_link": "https://www.ddugjy.gov.in",
    },
    {
        "scheme_name": "PM Gram Sadak Yojana",
        "ministry": "Rural Development",
        "category": "infrastructure",
        "eligibility": "Village communities with population 250+ unconnected by road",
        "min_age": 18,
        "max_age": 99,
        "max_income": 999999,
        "occupation_type": "all",
        "benefits": "All-weather road connectivity to unconnected rural habitations",
        "state_specific": "all",
        "apply_link": "https://pmgsy.nic.in",
    },
]


def load_schemes() -> List[Dict]:
    """
    Load schemes from CSV file with in-memory caching.
    Falls back to HARDCODED_SCHEMES if CSV is missing or empty.
    """
    global _cache

    if _cache is not None:
        return _cache

    try:
        if not os.path.exists(SCHEMES_CSV):
            print(
                f"[schemes_db] CSV not found at {SCHEMES_CSV}, using hardcoded schemes"
            )
            _cache = HARDCODED_SCHEMES
            return _cache

        df = pd.read_csv(SCHEMES_CSV)

        if df.empty or len(df) < 5:
            print("[schemes_db] CSV empty or too few rows, using hardcoded schemes")
            _cache = HARDCODED_SCHEMES
            return _cache

        df.columns = df.columns.str.strip().str.lower()

        column_map = {
            "scheme_name": "scheme_name",
            "name": "scheme_name",
            "shortdescription": "scheme_name",
            "description": "benefits",
            "benefits": "benefits",
            "benefit": "benefits",
            "eligibilitycriteria": "eligibility",
            "eligibility": "eligibility",
            "nodename": "ministry",
            "ministry": "ministry",
            "department": "ministry",
            "category": "category",
            "min_age": "min_age",
            "max_age": "max_age",
            "max_income": "max_income",
            "occupationtype": "occupation_type",
            "occupation_type": "occupation_type",
            "statespecific": "state_specific",
            "state_specific": "state_specific",
        }
        df = df.rename(columns=column_map)

        for col in ["min_age", "max_age", "max_income"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        for col in [
            "scheme_name",
            "eligibility",
            "benefits",
            "category",
            "occupation_type",
            "state_specific",
        ]:
            if col in df.columns:
                df[col] = df[col].fillna("unknown").astype(str).str.strip()

        if "apply_link" not in df.columns:
            df["apply_link"] = "https://pmkisan.gov.in"
        else:
            df["apply_link"] = df["apply_link"].fillna("https://pmkisan.gov.in")

        required = ["scheme_name", "eligibility", "benefits"]
        for col in required:
            if col not in df.columns:
                print(f"[schemes_db] Missing column '{col}', using hardcoded schemes")
                _cache = HARDCODED_SCHEMES
                return _cache

        _cache = df.to_dict("records")
        print(f"[schemes_db] Loaded {len(_cache)} schemes from CSV")
        return _cache

    except Exception as e:
        print(f"[schemes_db] Error loading CSV: {e}, using hardcoded schemes")
        _cache = HARDCODED_SCHEMES
        return _cache


def search_schemes(
    query: str,
    category: Optional[str] = None,
    occupation: Optional[str] = None,
    income: Optional[float] = None,
    state: Optional[str] = None,
) -> List[Dict]:
    """
    Search schemes by natural language query and optional filters.
    Returns top 5 matching schemes.
    """
    try:
        schemes = load_schemes()
        results = schemes

        if category:
            cat_lower = category.lower().strip()
            results = [
                s for s in results if cat_lower in str(s.get("category", "")).lower()
            ]

        if occupation:
            occ_lower = occupation.lower().strip()
            results = [
                s
                for s in results
                if occ_lower in str(s.get("occupation_type", "")).lower()
                or "all" in str(s.get("occupation_type", "")).lower()
            ]

        if income is not None:
            results = [s for s in results if float(s.get("max_income", 0)) >= income]

        if state:
            state_lower = state.lower().strip()
            results = [
                s
                for s in results
                if state_lower in str(s.get("state_specific", "")).lower()
                or "all" in str(s.get("state_specific", "")).lower()
            ]

        if query and len(query.strip()) > 1:
            query_lower = query.lower().strip()
            keywords = query_lower.split()

            scored = []
            for s in results:
                score = 0
                searchable = " ".join(
                    [
                        str(s.get("scheme_name", "")),
                        str(s.get("eligibility", "")),
                        str(s.get("benefits", "")),
                        str(s.get("category", "")),
                        str(s.get("ministry", "")),
                    ]
                ).lower()

                scheme_name_lower = str(s.get("scheme_name", "")).lower()

                for kw in keywords:
                    if kw in searchable:
                        score += 1
                        if kw in scheme_name_lower:
                            score += 5
                        if kw in str(s.get("category", "")).lower():
                            score += 4
                        if kw in str(s.get("occupation_type", "")).lower():
                            score += 4

                if (
                    occupation
                    and occupation.lower() in str(s.get("occupation_type", "")).lower()
                ):
                    score += 10
                if "all" not in str(s.get("occupation_type", "")).lower():
                    if (
                        occupation
                        and occupation.lower()
                        in str(s.get("occupation_type", "")).lower()
                    ):
                        score += 3

                farming_terms = [
                    "farming",
                    "farmer",
                    "agriculture",
                    "kisan",
                    "crop",
                    "land",
                ]
                for term in farming_terms:
                    if term in searchable:
                        score += 2
                        if term in scheme_name_lower:
                            score += 4

                if score > 0:
                    scored.append((score, s))

            scored.sort(key=lambda x: x[0], reverse=True)
            results = [s for _, s in scored]

        if not results:
            fallback = [s for s in HARDCODED_SCHEMES[:3] if s not in results]
            return fallback

        return results[:5]

    except Exception as e:
        print(f"[schemes_db] Search error: {e}")
        return HARDCODED_SCHEMES[:3]


def get_scheme_details(scheme_name: str) -> Optional[Dict]:
    """
    Get full details for a specific scheme by exact name.
    Returns None if not found.
    """
    try:
        schemes = load_schemes()
        name_lower = scheme_name.lower().strip()

        for s in schemes:
            if name_lower in s.get("scheme_name", "").lower():
                return s

        for s in schemes:
            if name_lower in s.get("scheme_name", "").lower():
                return s

        return None

    except Exception as e:
        print(f"[schemes_db] get_scheme_details error: {e}")
        return None


def get_schemes_by_profile(
    age: int, income: float, occupation: str, state: str
) -> List[Dict]:
    """
    Smart recommendation function - finds all schemes matching user profile.
    Applies all eligibility rules: age, income, occupation, state.
    Returns schemes sorted by benefit value (most benefit first).
    """
    try:
        schemes = load_schemes()
        matches = []

        occ_lower = occupation.lower().strip()
        state_lower = state.lower().strip()

        for s in schemes:
            try:
                min_age = int(s.get("min_age", 0) or 0)
                max_age = int(s.get("max_age", 99) or 99)
                max_income = float(s.get("max_income", 999999) or 999999)
                occ_type = str(s.get("occupation_type", "all")).lower()
                state_sp = str(s.get("state_specific", "all")).lower()

                if not (min_age <= age <= max_age):
                    continue
                if income > max_income:
                    continue

                occ_match = (
                    "all" in occ_type
                    or occ_lower in occ_type
                    or occ_lower.replace("_", " ") in occ_type
                    or occ_lower.replace(" ", "_") in occ_type
                )
                if not occ_match:
                    continue

                state_match = (
                    "all" in state_sp or "india" in state_sp or state_lower in state_sp
                )
                if not state_match:
                    continue

                benefit_text = str(s.get("benefits", "")).lower()
                benefit_score = 0

                if any(
                    w in benefit_text
                    for w in ["6000", "12000", "18000", "loan", "subsidy"]
                ):
                    benefit_score += 2
                if any(
                    w in benefit_text
                    for w in ["50000", "1 lakh", "100000", "insurance"]
                ):
                    benefit_score += 3
                if any(
                    w in benefit_text
                    for w in ["5 lakh", "500000", "free", "guaranteed"]
                ):
                    benefit_score += 5
                if "₹" in str(s.get("benefits", "")):
                    benefit_score += 1

                matches.append((benefit_score, s))

            except (ValueError, TypeError):
                continue

        matches.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in matches]

    except Exception as e:
        print(f"[schemes_db] get_schemes_by_profile error: {e}")
        return []


if __name__ == "__main__":
    print("Testing schemes_db.py...")
    schemes = load_schemes()
    print(f"Loaded {len(schemes)} schemes")

    results = search_schemes(
        "farming scheme for poor", occupation="farmer", income=8000
    )
    print(f"Search results: {len(results)} found")
    for s in results:
        print(f"  -> {s['scheme_name']}: {str(s['benefits'])[:50]}...")

    profile_results = get_schemes_by_profile(
        age=35, income=8000, occupation="farmer", state="UP"
    )
    print(f"Profile match: {len(profile_results)} schemes found")
    for s in profile_results[:3]:
        print(f"  -> {s['scheme_name']}")

    print("schemes_db.py working correctly")
