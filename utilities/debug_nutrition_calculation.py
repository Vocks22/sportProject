#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, 'src/backend')

from main import create_app
from models.meal_tracking import MealTracking, DailyNutritionSummary
from services.meal_tracking_service import MealTrackingService
from datetime import date

# Créer le contexte Flask
app = create_app()

with app.app_context():
    print('🔍 Analyse des calculs nutritionnels')
    print('=' * 40)
    
    # Test avec l'utilisateur 1 et la date d'aujourd'hui
    user_id = 1
    today = date.today()
    
    print(f'Utilisateur: {user_id}')
    print(f'Date: {today}')

    # Récupérer tous les meal trackings d'aujourd'hui
    trackings = MealTracking.query.filter_by(
        user_id=user_id,
        meal_date=today
    ).all()

    print(f'\n📊 Repas trackés pour aujourd\'hui: {len(trackings)}')
    print('-' * 40)

    total_planned_calories = 0
    total_effective_calories = 0
    total_planned_protein = 0
    total_effective_protein = 0
    total_planned_carbs = 0
    total_effective_carbs = 0
    total_planned_fat = 0
    total_effective_fat = 0

    for i, tracking in enumerate(trackings, 1):
        print(f'\n🍽️  Repas #{i}: {tracking.meal_name or "Repas sans nom"} ({tracking.meal_type})')
        print(f'   Status: {tracking.status.value}')
        print(f'   Planifié: {tracking.planned_calories or 0:.1f} kcal, {tracking.planned_protein or 0:.1f}g protéines, {tracking.planned_carbs or 0:.1f}g glucides, {tracking.planned_fat or 0:.1f}g lipides')
        
        if tracking.is_consumed:
            print(f'   Consommé: {tracking.actual_calories or "N/A"} kcal, {tracking.actual_protein or "N/A"}g protéines, {tracking.actual_carbs or "N/A"}g glucides, {tracking.actual_fat or "N/A"}g lipides')
        
        print(f'   EFFECTIF: {tracking.effective_calories:.1f} kcal, {tracking.effective_protein:.1f}g protéines, {tracking.effective_carbs:.1f}g glucides, {tracking.effective_fat:.1f}g lipides')
        
        total_planned_calories += tracking.planned_calories or 0
        total_effective_calories += tracking.effective_calories
        total_planned_protein += tracking.planned_protein or 0
        total_effective_protein += tracking.effective_protein
        total_planned_carbs += tracking.planned_carbs or 0
        total_effective_carbs += tracking.effective_carbs
        total_planned_fat += tracking.planned_fat or 0
        total_effective_fat += tracking.effective_fat

    print(f'\n📈 TOTAUX MANUELS:')
    print(f'   Planifié total: {total_planned_calories:.1f} kcal, {total_planned_protein:.1f}g protéines, {total_planned_carbs:.1f}g glucides, {total_planned_fat:.1f}g lipides')
    print(f'   Effectif total: {total_effective_calories:.1f} kcal, {total_effective_protein:.1f}g protéines, {total_effective_carbs:.1f}g glucides, {total_effective_fat:.1f}g lipides')

    # Calculer le résumé quotidien
    try:
        daily_summary = MealTrackingService.calculate_daily_summary(user_id, today, force_recalculate=True)
        print(f'\n📋 RÉSUMÉ QUOTIDIEN CALCULÉ PAR LE SERVICE:')
        print(f'   Calories planifiées: {daily_summary.planned_calories:.1f}')
        print(f'   Calories effectives: {daily_summary.actual_calories:.1f}')
        print(f'   Protéines planifiées: {daily_summary.planned_protein:.1f}')
        print(f'   Protéines effectives: {daily_summary.actual_protein:.1f}')
        print(f'   Glucides effectifs: {daily_summary.actual_carbs:.1f}')
        print(f'   Lipides effectifs: {daily_summary.actual_fat:.1f}')
        
        # Comparaison
        print(f'\n🔍 VÉRIFICATION:')
        calories_match = abs(total_effective_calories - daily_summary.actual_calories) < 0.1
        protein_match = abs(total_effective_protein - daily_summary.actual_protein) < 0.1
        print(f'   Calories correspondent: {"✅" if calories_match else "❌"} (manuel: {total_effective_calories:.1f}, service: {daily_summary.actual_calories:.1f})')
        print(f'   Protéines correspondent: {"✅" if protein_match else "❌"} (manuel: {total_effective_protein:.1f}, service: {daily_summary.actual_protein:.1f})')
        
    except Exception as e:
        print(f'❌ Erreur calcul résumé: {e}')

    print(f'\n🎯 EXPLICATION DU SYSTÈME:')
    print('1. VALEURS PLANIFIÉES = ce qui était prévu dans le plan de repas')
    print('2. VALEURS EFFECTIVES = ce qui est utilisé pour les calculs finaux')
    print('   - Si repas CONSOMMÉ: utilise actual_* (valeurs réelles consommées)')
    print('   - Si repas PLANIFIÉ: utilise planned_* (valeurs prévues)')
    print('3. Le RÉSUMÉ QUOTIDIEN additionne toutes les valeurs effectives')
    print('4. Les pourcentages dans l\'interface sont calculés par rapport aux objectifs utilisateur')
    
    # Vérifier les valeurs que tu mentionnes
    print(f'\n🤔 ANALYSE DE TES VALEURS MENTIONNÉES:')
    print('Tu mentionnes: "6G de lipides 8G de glucides 20G de protéines Et 100 kilocalories"')
    print('Et aussi "j\'ai déjà 832" (probablement calories?)')
    
    if trackings:
        print(f'Les valeurs actuelles dans la base:')
        print(f'  - Total effectif: {total_effective_calories:.0f} kcal, {total_effective_protein:.0f}g protéines, {total_effective_carbs:.0f}g glucides, {total_effective_fat:.0f}g lipides')
        
        # Chercher le custom protein snack
        custom_snack = None
        for tracking in trackings:
            if 'Custom Protein Snack' in (tracking.meal_name or ''):
                custom_snack = tracking
                break
        
        if custom_snack:
            print(f'\n📝 Custom Protein Snack trouvé:')
            print(f'  - Planifié: {custom_snack.planned_calories:.0f} kcal, {custom_snack.planned_protein:.0f}g prot, {custom_snack.planned_carbs:.0f}g glucides, {custom_snack.planned_fat:.0f}g lipides')
            print(f'  - Status: {custom_snack.status.value}')
    else:
        print('❌ Aucun repas trouvé pour aujourd\'hui')