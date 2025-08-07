#!/usr/bin/env python3
"""
Script pour tester les filtres de dates sur les graphiques
"""

import requests
import json
from datetime import datetime, timedelta

def test_date_filters():
    """Test des filtres de dates sur l'API"""
    print("📅 TEST DES FILTRES DE DATES")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api"
    user_id = 1
    
    # Test 1: Récupérer toutes les données
    print("\n📊 Test 1: Récupération de toutes les données")
    try:
        response = requests.get(f"{base_url}/users/{user_id}/weight-history?days=365", timeout=5)
        if response.status_code == 200:
            data = response.json()
            all_count = data["statistics"]["count"]
            all_weights = data["weight_history"]
            
            print(f"   ✅ {all_count} entrées totales trouvées")
            
            if all_weights:
                first_date = all_weights[-1]["recorded_date"]
                last_date = all_weights[0]["recorded_date"]
                print(f"   📅 Période complète : {first_date} à {last_date}")
                
                # Vérifier les données de juillet 2024
                july_2024 = [w for w in all_weights if w["recorded_date"].startswith("2024-07")]
                print(f"   📅 Juillet 2024 : {len(july_2024)} mesures")
                if july_2024:
                    july_weights = [w["weight"] for w in july_2024]
                    print(f"      Poids : {min(july_weights):.1f}kg - {max(july_weights):.1f}kg")
                
                # Vérifier les données d'août 2024
                aug_2024 = [w for w in all_weights if w["recorded_date"].startswith("2024-08")]
                print(f"   📅 Août 2024 : {len(aug_2024)} mesures")
                if aug_2024:
                    aug_weights = [w["weight"] for w in aug_2024]
                    print(f"      Poids : {min(aug_weights):.1f}kg - {max(aug_weights):.1f}kg")
                
                # Vérifier les données de 2025
                year_2025 = [w for w in all_weights if w["recorded_date"].startswith("2025")]
                print(f"   📅 Année 2025 : {len(year_2025)} mesures")
                if year_2025:
                    weights_2025 = [w["weight"] for w in year_2025]
                    print(f"      Poids : {min(weights_2025):.1f}kg - {max(weights_2025):.1f}kg")
                    
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test 2: Tester différentes périodes
    print("\n🔍 Test 2: Filtrage par période")
    periods = [
        (30, "30 derniers jours"),
        (90, "3 derniers mois"),
        (180, "6 derniers mois"),
        (365, "Année complète")
    ]
    
    for days, label in periods:
        try:
            response = requests.get(f"{base_url}/users/{user_id}/weight-history?days={days}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                count = data["statistics"]["count"]
                print(f"   📊 {label} : {count} mesures")
        except:
            print(f"   ❌ Erreur pour {label}")
    
    # Test 3: Vérifier les mesures
    print("\n📏 Test 3: Cohérence avec les mesures")
    try:
        response = requests.get(f"{base_url}/users/{user_id}/measurements?days=365", timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Compter par mois
            months = {}
            for m in data:
                month_key = m["date"][:7]  # YYYY-MM
                if month_key not in months:
                    months[month_key] = 0
                months[month_key] += 1
            
            print(f"   📅 Distribution par mois:")
            for month in sorted(months.keys()):
                year, m = month.split("-")
                month_name = ["", "Jan", "Fév", "Mar", "Avr", "Mai", "Juin", 
                             "Juil", "Août", "Sep", "Oct", "Nov", "Déc"][int(m)]
                print(f"      {month_name} {year}: {months[month]} mesures")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("💡 Conseils d'utilisation:")
    print("   1. Utilisez le bouton '📅 Personnalisé' pour sélectionner une période")
    print("   2. Cliquez sur 'Juillet 24' pour voir les données de juillet 2024")
    print("   3. Cliquez sur 'Août 24' pour voir les données d'août 2024")
    print("   4. Utilisez les sélecteurs de dates pour choisir n'importe quelle période")

if __name__ == '__main__':
    test_date_filters()