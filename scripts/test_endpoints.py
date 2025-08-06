#!/usr/bin/env python3
"""
Script de test des endpoints API DietTracker
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000/api"

def test_endpoint(method, endpoint, data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            return None
        
        return {
            "status": response.status_code,
            "data": response.json() if response.content else None
        }
    except requests.exceptions.ConnectionError:
        return {"status": "error", "data": "Connection refused - is server running?"}
    except Exception as e:
        return {"status": "error", "data": str(e)}

def main():
    """Test all endpoints"""
    print("🔍 Test des endpoints API DietTracker")
    print("=" * 50)
    
    # Test endpoints
    tests = [
        ("GET", "/ingredients", None),
        ("GET", "/recipes", None),
        ("GET", "/users", None),
        ("GET", "/meal-plans", None),
    ]
    
    for method, endpoint, data in tests:
        print(f"\n📍 {method} {endpoint}")
        result = test_endpoint(method, endpoint, data)
        
        if result["status"] == "error":
            print(f"   ❌ Erreur: {result['data']}")
        elif result["status"] == 200:
            if isinstance(result["data"], list):
                print(f"   ✅ OK - {len(result['data'])} éléments")
                if result["data"] and len(result["data"]) > 0:
                    print(f"   Exemple: {result['data'][0].get('name', 'N/A')}")
            else:
                print(f"   ✅ OK")
        else:
            print(f"   ⚠️ Status: {result['status']}")
            if result["data"]:
                print(f"   Réponse: {result['data']}")
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés")

if __name__ == "__main__":
    main()