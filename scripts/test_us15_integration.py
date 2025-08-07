#!/usr/bin/env python3
"""
Script de test d'intégration pour l'US1.5 - Liste de Courses Interactive
Teste le fonctionnement complet de bout en bout
"""

import sys
import os
import requests
import json
from datetime import datetime, date

# Ajouter le chemin du backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

def test_us15_integration():
    """
    Test d'intégration complet de l'US1.5
    """
    print("🧪 Test d'intégration US1.5 - Liste de Courses Interactive")
    print("=" * 60)
    
    # Configuration
    BASE_URL = "http://localhost:5000/api"
    
    try:
        # 1. Vérifier que le serveur est en marche
        print("\n1. 🔍 Vérification du serveur...")
        response = requests.get(f"{BASE_URL}/recipes", timeout=5)
        if response.status_code == 200:
            print("   ✅ Serveur accessible")
        else:
            print(f"   ❌ Serveur non accessible (status: {response.status_code})")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Impossible de contacter le serveur: {e}")
        print("   💡 Assurez-vous que le serveur Flask est démarré")
        return False
    
    # 2. Test de création d'un plan de repas
    print("\n2. 📋 Test de création d'un plan de repas...")
    meal_plan_data = {
        "week_start": date.today().isoformat(),
        "meals": {
            "monday": {
                "repas1": 1,
                "repas2": 2
            },
            "tuesday": {
                "repas1": 3,
                "collation1": 4
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/meal-plans",
            json=meal_plan_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            meal_plan = response.json()
            meal_plan_id = meal_plan['id']
            print(f"   ✅ Plan de repas créé (ID: {meal_plan_id})")
        else:
            print(f"   ❌ Échec de création du plan de repas: {response.status_code}")
            print(f"   📝 Réponse: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la création du plan de repas: {e}")
        return False
    
    # 3. Test de génération de liste de courses optimisée
    print("\n3. 🛒 Test de génération de liste de courses optimisée...")
    try:
        response = requests.post(
            f"{BASE_URL}/meal-plans/{meal_plan_id}/shopping-list",
            json={
                "aggregation_preferences": {
                    "unit_preferences": {
                        "prefer_kg_over_g": True,
                        "prefer_l_over_ml": True
                    }
                }
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            shopping_data = response.json()
            shopping_list = shopping_data['shopping_list']
            shopping_list_id = shopping_list['id']
            print(f"   ✅ Liste de courses générée (ID: {shopping_list_id})")
            print(f"   📊 {len(shopping_list.get('items', []))} articles générés")
            print(f"   💰 Budget estimé: {shopping_list.get('estimated_budget', 'N/A')}")
            
            # Vérifier les fonctionnalités d'agrégation
            generation_info = shopping_data.get('generation_info', {})
            if generation_info:
                print(f"   🔄 Agrégation: {generation_info}")
        else:
            print(f"   ❌ Échec de génération de liste: {response.status_code}")
            print(f"   📝 Réponse: {response.text}")
            return False
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la génération de liste: {e}")
        return False
    
    # 4. Test de mise à jour d'articles (toggle)
    print("\n4. ✅ Test de mise à jour d'articles...")
    try:
        if shopping_list.get('items'):
            first_item_id = shopping_list['items'][0].get('id')
            if first_item_id:
                response = requests.patch(
                    f"{BASE_URL}/shopping-lists/{shopping_list_id}/items/{first_item_id}/toggle",
                    json={
                        "checked": True,
                        "user_id": "test_user"
                    },
                    headers={'Content-Type': 'application/json'}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Article coché avec succès")
                    print(f"   🔄 Version de liste: {result['shopping_list'].get('version', 'N/A')}")
                else:
                    print(f"   ❌ Échec de mise à jour d'article: {response.status_code}")
            else:
                print("   ⚠️ Pas d'articles dans la liste pour tester")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la mise à jour d'article: {e}")
    
    # 5. Test de mise à jour groupée
    print("\n5. 📦 Test de mise à jour groupée...")
    try:
        items_to_toggle = []
        for i, item in enumerate(shopping_list.get('items', [])[:3]):  # Max 3 items
            items_to_toggle.append({
                "item_id": str(item.get('id')),
                "checked": i % 2 == 0  # Alterner true/false
            })
        
        if items_to_toggle:
            response = requests.patch(
                f"{BASE_URL}/shopping-lists/{shopping_list_id}/bulk-toggle",
                json={
                    "items": items_to_toggle,
                    "user_id": "test_user"
                },
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Mise à jour groupée réussie")
                print(f"   📊 {result.get('updated_items')}/{result.get('total_items')} articles mis à jour")
            else:
                print(f"   ❌ Échec de mise à jour groupée: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la mise à jour groupée: {e}")
    
    # 6. Test des statistiques
    print("\n6. 📈 Test des statistiques...")
    try:
        response = requests.get(f"{BASE_URL}/shopping-lists/{shopping_list_id}/statistics")
        
        if response.status_code == 200:
            stats = response.json()
            overview = stats.get('overview', {})
            print(f"   ✅ Statistiques récupérées")
            print(f"   📊 Total articles: {overview.get('total_items', 'N/A')}")
            print(f"   ✅ Articles cochés: {overview.get('completed_items', 'N/A')}")
            print(f"   📈 Pourcentage: {overview.get('completion_percentage', 'N/A')}%")
            print(f"   ⏱️ Temps estimé: {overview.get('estimated_shopping_time_minutes', 'N/A')} min")
        else:
            print(f"   ❌ Échec de récupération des statistiques: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la récupération des statistiques: {e}")
    
    # 7. Test de l'historique
    print("\n7. 📜 Test de l'historique...")
    try:
        response = requests.get(f"{BASE_URL}/shopping-lists/{shopping_list_id}/history")
        
        if response.status_code == 200:
            history = response.json()
            history_entries = history.get('history', [])
            print(f"   ✅ Historique récupéré")
            print(f"   📋 {len(history_entries)} entrées d'historique")
            
            for entry in history_entries[:3]:  # Afficher les 3 premières entrées
                action = entry.get('action', 'N/A')
                timestamp = entry.get('timestamp', 'N/A')
                print(f"   📝 {action} à {timestamp}")
        else:
            print(f"   ❌ Échec de récupération de l'historique: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la récupération de l'historique: {e}")
    
    # 8. Test de l'export
    print("\n8. 📤 Test de l'export...")
    try:
        response = requests.post(
            f"{BASE_URL}/shopping-lists/{shopping_list_id}/export-data",
            json={
                "format": "json",
                "include_metadata": True,
                "include_checked_items": True
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            export_result = response.json()
            if export_result.get('success'):
                download_info = export_result.get('download_info', {})
                print(f"   ✅ Export préparé avec succès")
                print(f"   📄 Fichier: {download_info.get('filename', 'N/A')}")
                print(f"   📊 Taille estimée: {download_info.get('size_estimate', 'N/A')} bytes")
            else:
                print(f"   ❌ Export échoué: {export_result.get('error', 'Erreur inconnue')}")
        else:
            print(f"   ❌ Échec de préparation de l'export: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la préparation de l'export: {e}")
    
    # 9. Test de régénération
    print("\n9. 🔄 Test de régénération de liste...")
    try:
        response = requests.post(
            f"{BASE_URL}/shopping-lists/{shopping_list_id}/regenerate",
            json={
                "preserve_checked_items": True
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"   ✅ Liste régénérée avec succès")
                print(f"   📊 Nouvelles statistiques disponibles")
            else:
                print(f"   ❌ Régénération échouée: {result.get('error', 'Erreur inconnue')}")
        else:
            print(f"   ❌ Échec de régénération: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la régénération: {e}")
    
    # 10. Test des catégories de rayons
    print("\n10. 🏪 Test des catégories de rayons...")
    try:
        response = requests.get(f"{BASE_URL}/shopping-lists/categories")
        
        if response.status_code == 200:
            categories = response.json()
            categories_list = categories.get('categories', [])
            print(f"   ✅ Catégories récupérées")
            print(f"   🏪 {len(categories_list)} catégories disponibles")
            
            for category in categories_list[:5]:  # Afficher les 5 premières
                name = category.get('display_name', 'N/A')
                icon = category.get('icon', '')
                print(f"   📂 {icon} {name}")
        else:
            print(f"   ❌ Échec de récupération des catégories: {response.status_code}")
    
    except Exception as e:
        print(f"   ❌ Erreur lors de la récupération des catégories: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test d'intégration US1.5 terminé !")
    print("💡 Vérifiez les résultats ci-dessus pour détecter d'éventuels problèmes")
    return True

if __name__ == "__main__":
    success = test_us15_integration()
    sys.exit(0 if success else 1)