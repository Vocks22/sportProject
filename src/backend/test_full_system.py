#!/usr/bin/env python3
"""
Script de test complet du système de mesures et graphiques
"""

import requests
import json
from datetime import datetime

def test_full_system():
    """Test complet du système"""
    print("🔧 TEST COMPLET DU SYSTÈME DE MESURES")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api"
    user_id = 1
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: API Weight History
    print("\n📊 Test 1: API Weight History")
    try:
        response = requests.get(f"{base_url}/users/{user_id}/weight-history?days=365&limit=500", timeout=5)
        if response.status_code == 200:
            data = response.json()
            weight_count = data["statistics"]["count"]
            print(f"   ✅ {weight_count} entrées de poids trouvées")
            print(f"   📈 Poids: {data['statistics']['min_weight']}kg - {data['statistics']['max_weight']}kg")
            print(f"   🔄 Changement total: {data['statistics']['weight_change']:.1f}kg")
            
            if weight_count >= 38:
                print(f"   ✅ Les 38 mesures sont bien présentes")
                tests_passed += 1
            else:
                print(f"   ❌ Seulement {weight_count}/38 mesures trouvées")
                tests_failed += 1
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        tests_failed += 1
    
    # Test 2: API Measurements
    print("\n📏 Test 2: API Measurements")
    try:
        response = requests.get(f"{base_url}/users/{user_id}/measurements?days=365&limit=100", timeout=5)
        if response.status_code == 200:
            data = response.json()
            meas_count = len(data)
            with_weight = sum(1 for m in data if m.get('weight'))
            print(f"   ✅ {meas_count} mesures totales trouvées")
            print(f"   ⚖️ {with_weight} mesures avec poids")
            
            # Vérifier les dates
            if data:
                first_date = data[-1]['date']
                last_date = data[0]['date']
                print(f"   📅 Période: {first_date} à {last_date}")
            
            if meas_count >= 38:
                print(f"   ✅ Les 38 mesures sont bien présentes")
                tests_passed += 1
            else:
                print(f"   ❌ Seulement {meas_count}/38 mesures trouvées")
                tests_failed += 1
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        tests_failed += 1
    
    # Test 3: API Profile
    print("\n👤 Test 3: API Profile")
    try:
        response = requests.get(f"{base_url}/users/{user_id}/profile", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Profil récupéré")
            print(f"   📊 Poids actuel: {data.get('current_weight', '--')}kg")
            print(f"   🎯 Objectif: {data.get('target_weight', '--')}kg")
            print(f"   📐 Taille: {data.get('height', '--')}cm")
            tests_passed += 1
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        tests_failed += 1
    
    # Test 4: Vérifier la cohérence des données
    print("\n🔍 Test 4: Cohérence des données")
    try:
        # Récupérer les deux sources
        weight_response = requests.get(f"{base_url}/users/{user_id}/weight-history?days=365", timeout=5)
        meas_response = requests.get(f"{base_url}/users/{user_id}/measurements?days=365", timeout=5)
        
        if weight_response.status_code == 200 and meas_response.status_code == 200:
            weight_data = weight_response.json()
            meas_data = meas_response.json()
            
            weight_count = weight_data["statistics"]["count"]
            meas_with_weight = sum(1 for m in meas_data if m.get('weight'))
            
            if weight_count == meas_with_weight:
                print(f"   ✅ Cohérence parfaite: {weight_count} entrées dans les deux tables")
                tests_passed += 1
            else:
                print(f"   ⚠️ Différence: {weight_count} dans WeightHistory, {meas_with_weight} dans Measurements")
                print(f"   💡 Exécutez sync_weight_data.py pour synchroniser")
                tests_failed += 1
        else:
            print(f"   ❌ Impossible de vérifier la cohérence")
            tests_failed += 1
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        tests_failed += 1
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    print(f"   ✅ Tests réussis: {tests_passed}")
    print(f"   ❌ Tests échoués: {tests_failed}")
    
    if tests_failed == 0:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS!")
        print("Les graphiques devraient maintenant s'afficher correctement.")
        print("\n💡 Actions recommandées:")
        print("   1. Rafraîchir la page du Dashboard")
        print("   2. Vérifier le graphique d'évolution du poids")
        print("   3. Aller sur la page Progress pour voir les stats détaillées")
        print("   4. Vérifier le profil pour l'évolution du poids")
    else:
        print("\n⚠️ Certains tests ont échoué.")
        print("Vérifiez les erreurs ci-dessus et corrigez-les.")
    
    return tests_passed, tests_failed

if __name__ == '__main__':
    test_full_system()