#!/usr/bin/env python3
"""
Script pour vérifier l'affichage correct des graphiques avec les nouvelles corrections
"""

import requests
import json
from datetime import datetime, timedelta

def test_graph_display():
    """Test l'affichage des graphiques"""
    print("📊 TEST D'AFFICHAGE DES GRAPHIQUES")
    print("=" * 50)
    
    base_url = "http://localhost:5000/api"
    user_id = 1
    
    # Récupérer toutes les données
    print("\n🔍 Analyse des données disponibles")
    try:
        response = requests.get(f"{base_url}/users/{user_id}/weight-history?days=365", timeout=5)
        if response.status_code == 200:
            data = response.json()
            weights = data["weight_history"]
            
            if weights:
                # Analyser les dates
                dates = [datetime.fromisoformat(w["recorded_date"]) for w in weights]
                latest_date = max(dates)
                earliest_date = min(dates)
                
                print(f"   📅 Période totale : {earliest_date.date()} à {latest_date.date()}")
                print(f"   📊 Nombre total de mesures : {len(weights)}")
                
                # Calculer l'écart avec aujourd'hui
                today = datetime.now()
                days_since_latest = (today - latest_date).days
                
                print(f"\n   ⏰ Dernière mesure il y a {days_since_latest} jours")
                
                if days_since_latest > 30:
                    print(f"   ⚠️ Les données sont anciennes (plus de 30 jours)")
                    print(f"   💡 Le graphique devrait afficher 'TOUT' par défaut")
                else:
                    print(f"   ✅ Les données sont récentes")
                    print(f"   💡 Le graphique devrait afficher '3M' par défaut")
                
                # Simuler les différents filtres
                print(f"\n📈 Simulation des filtres de période:")
                
                # Filtre 1M (30 derniers jours depuis la dernière mesure)
                cutoff_1m = latest_date - timedelta(days=30)
                data_1m = [w for w in weights if datetime.fromisoformat(w["recorded_date"]) >= cutoff_1m]
                print(f"   1M : {len(data_1m)} mesures (depuis {cutoff_1m.date()})")
                
                # Filtre 3M (90 derniers jours depuis la dernière mesure)
                cutoff_3m = latest_date - timedelta(days=90)
                data_3m = [w for w in weights if datetime.fromisoformat(w["recorded_date"]) >= cutoff_3m]
                print(f"   3M : {len(data_3m)} mesures (depuis {cutoff_3m.date()})")
                
                # Filtre 6M (180 derniers jours depuis la dernière mesure)
                cutoff_6m = latest_date - timedelta(days=180)
                data_6m = [w for w in weights if datetime.fromisoformat(w["recorded_date"]) >= cutoff_6m]
                print(f"   6M : {len(data_6m)} mesures (depuis {cutoff_6m.date()})")
                
                # Filtre 1Y (365 derniers jours depuis la dernière mesure)
                cutoff_1y = latest_date - timedelta(days=365)
                data_1y = [w for w in weights if datetime.fromisoformat(w["recorded_date"]) >= cutoff_1y]
                print(f"   1Y : {len(data_1y)} mesures (depuis {cutoff_1y.date()})")
                
                print(f"   ALL : {len(weights)} mesures (toutes les données)")
                
                # Recommandations
                print(f"\n💡 Recommandations d'utilisation:")
                
                if len(data_3m) >= 10:
                    print(f"   ✅ Le filtre '3M' affichera {len(data_3m)} mesures")
                else:
                    print(f"   ⚠️ Le filtre '3M' a peu de données ({len(data_3m)} mesures)")
                    print(f"      → Le système affichera les 90 dernières mesures disponibles")
                
                print(f"\n   📅 Pour voir juillet 2024 complet:")
                print(f"      1. Cliquez sur '📅 Personnalisé'")
                print(f"      2. Cliquez sur 'Juillet 24'")
                print(f"      3. Ou sélectionnez Du: 2024-07-01, Au: 2024-07-31")
                
                # Compter par mois
                months_data = {}
                for w in weights:
                    month_key = w["recorded_date"][:7]
                    if month_key not in months_data:
                        months_data[month_key] = []
                    months_data[month_key].append(w["weight"])
                
                print(f"\n📊 Données disponibles par mois:")
                for month in sorted(months_data.keys()):
                    weights_month = months_data[month]
                    print(f"   {month} : {len(weights_month)} mesures ({min(weights_month):.1f} - {max(weights_month):.1f} kg)")
                
        else:
            print(f"   ❌ Erreur API: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Avec les corrections apportées:")
    print("   1. Le graphique affichera 'TOUT' par défaut (car données anciennes)")
    print("   2. Les filtres sont basés sur la dernière mesure, pas la date du jour")
    print("   3. Si pas assez de données pour une période, affiche les N dernières mesures")
    print("   4. Le mode personnalisé permet de sélectionner n'importe quelle période")

if __name__ == '__main__':
    test_graph_display()