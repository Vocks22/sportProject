#!/usr/bin/env python3
"""
Test standalone des utilitaires de dates ISO 8601 pour US1.6
Ce script peut être exécuté sans dépendances Flask/SQLAlchemy
"""

import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Ajouter le répertoire backend au path
backend_path = Path(__file__).resolve().parent.parent / 'src' / 'backend'
sys.path.append(str(backend_path))

try:
    from utils.date_utils import (
        get_monday_of_week, get_sunday_of_week, get_week_range_iso8601,
        validate_week_start_iso8601, format_week_display,
        get_current_week_monday, next_monday, previous_monday,
        get_week_number_iso8601, get_week_year_iso8601,
        batch_convert_week_starts, validate_database_week_starts
    )
    
    def test_date_utils():
        """Tests complets des utilitaires de dates ISO 8601"""
        print("🧪 Tests des utilitaires de dates ISO 8601")
        print("=" * 50)
        
        test_cases = [
            # (input_date, expected_monday, expected_sunday, description)
            (date(2025, 8, 7), date(2025, 8, 4), date(2025, 8, 10), "Jeudi 7 août 2025"),
            (date(2025, 8, 4), date(2025, 8, 4), date(2025, 8, 10), "Lundi 4 août 2025"),
            (date(2025, 8, 10), date(2025, 8, 4), date(2025, 8, 10), "Dimanche 10 août 2025"),
            (date(2025, 1, 1), date(2024, 12, 30), date(2025, 1, 5), "Mercredi 1er janvier 2025"),
            (date(2025, 12, 29), date(2025, 12, 29), date(2026, 1, 4), "Lundi 29 décembre 2025"),
        ]
        
        all_passed = True
        
        for i, (input_date, expected_monday, expected_sunday, description) in enumerate(test_cases, 1):
            print(f"\n{i}. Test: {description}")
            print(f"   Date d'entrée: {input_date} ({['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][input_date.weekday()]})")
            
            # Test get_monday_of_week
            actual_monday = get_monday_of_week(input_date)
            monday_ok = actual_monday == expected_monday
            status = "✅" if monday_ok else "❌"
            print(f"   {status} Lundi: {actual_monday} (attendu: {expected_monday})")
            
            # Test get_sunday_of_week  
            actual_sunday = get_sunday_of_week(input_date)
            sunday_ok = actual_sunday == expected_sunday
            status = "✅" if sunday_ok else "❌"
            print(f"   {status} Dimanche: {actual_sunday} (attendu: {expected_sunday})")
            
            # Test get_week_range_iso8601
            monday, sunday = get_week_range_iso8601(input_date)
            range_ok = monday == expected_monday and sunday == expected_sunday
            status = "✅" if range_ok else "❌"
            print(f"   {status} Plage: {monday} - {sunday}")
            
            # Test format_week_display
            try:
                display = format_week_display(actual_monday, 'fr')
                print(f"   📅 Affichage: {display}")
            except Exception as e:
                print(f"   ❌ Erreur formatage: {e}")
                all_passed = False
            
            if not (monday_ok and sunday_ok and range_ok):
                all_passed = False
        
        # Tests de validation
        print(f"\n6. Tests de validation:")
        
        # Test lundi valide
        try:
            validate_week_start_iso8601(date(2025, 8, 4))  # Lundi
            print("   ✅ Validation lundi: OK")
        except ValueError as e:
            print(f"   ❌ Validation lundi échouée: {e}")
            all_passed = False
        
        # Test non-lundi invalide
        try:
            validate_week_start_iso8601(date(2025, 8, 6))  # Mercredi
            print("   ❌ Validation mercredi: devrait échouer mais n'a pas échoué")
            all_passed = False
        except ValueError:
            print("   ✅ Validation mercredi: correctement rejeté")
        
        # Test navigation de semaines
        print(f"\n7. Tests de navigation:")
        current_monday = get_current_week_monday()
        print(f"   📅 Lundi de cette semaine: {current_monday}")
        
        next_mon = next_monday(current_monday)
        expected_next = current_monday + timedelta(days=7)
        next_ok = next_mon == expected_next
        status = "✅" if next_ok else "❌"
        print(f"   {status} Lundi suivant: {next_mon} (attendu: {expected_next})")
        
        prev_mon = previous_monday(current_monday + timedelta(days=1))  # Mardi
        prev_ok = prev_mon == current_monday
        status = "✅" if prev_ok else "❌" 
        print(f"   {status} Lundi précédent: {prev_mon} (attendu: {current_monday})")
        
        if not (next_ok and prev_ok):
            all_passed = False
        
        # Test batch conversion
        print(f"\n8. Test conversion par lot:")
        test_dates = [date(2025, 8, 5), date(2025, 8, 6), date(2025, 8, 7)]  # Mardi, Mercredi, Jeudi
        conversions = batch_convert_week_starts(test_dates)
        
        expected_monday = date(2025, 8, 4)
        batch_ok = all(converted == expected_monday for original, converted in conversions)
        status = "✅" if batch_ok else "❌"
        print(f"   {status} Conversion lot: {len(conversions)} dates converties vers {expected_monday}")
        
        if not batch_ok:
            all_passed = False
        
        # Test validation de liste
        print(f"\n9. Test validation de liste:")
        valid_dates = [date(2025, 8, 4), date(2025, 8, 11)]  # Deux lundis
        invalid_dates = [date(2025, 8, 4), date(2025, 8, 6)]  # Lundi + Mercredi
        
        is_valid, errors = validate_database_week_starts(valid_dates)
        status = "✅" if is_valid else "❌"
        print(f"   {status} Validation liste valide: {is_valid}")
        
        is_valid, errors = validate_database_week_starts(invalid_dates)
        status = "✅" if not is_valid else "❌"
        print(f"   {status} Validation liste invalide: {'rejetée' if not is_valid else 'acceptée (erreur)'}")
        if errors:
            print(f"      Erreurs détectées: {len(errors)}")
            for error in errors[:2]:  # Max 2 exemples
                print(f"        - {error}")
        
        # Résultat final
        print("\n" + "=" * 50)
        if all_passed:
            print("✅ TOUS LES TESTS RÉUSSIS")
            print("🎉 Les utilitaires de dates ISO 8601 fonctionnent correctement!")
            return True
        else:
            print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
            print("⚠️ Vérifiez l'implémentation des utilitaires de dates")
            return False
    
    def test_performance():
        """Test de performance"""
        print(f"\n🚀 Test de performance")
        print("-" * 30)
        
        import time
        
        # 1000 calculs
        test_dates = [date(2025, 1, 1) + timedelta(days=i) for i in range(1000)]
        
        start = time.time()
        for test_date in test_dates:
            monday = get_monday_of_week(test_date)
            sunday = get_sunday_of_week(test_date)
        
        elapsed = time.time() - start
        
        print(f"📊 {len(test_dates)} calculs en {elapsed:.3f} secondes")
        print(f"📊 {len(test_dates)/elapsed:.0f} calculs/seconde")
        
        if elapsed > 1.0:
            print("⚠️ Performance lente (> 1s pour 1000 calculs)")
            return False
        else:
            print("✅ Performance acceptable")
            return True
    
    def main():
        print("🔍 Validation standalone des utilitaires de dates ISO 8601 - US1.6")
        print(f"📅 Date du test: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Test principal
        utils_ok = test_date_utils()
        
        # Test performance
        perf_ok = test_performance()
        
        # Résultat global
        print("\n" + "=" * 70)
        if utils_ok and perf_ok:
            print("🎯 VALIDATION COMPLÈTE RÉUSSIE")
            print("✅ L'implémentation US1.6 est prête pour la production")
            sys.exit(0)
        else:
            print("💥 VALIDATION ÉCHOUÉE")
            print("❌ Des corrections sont nécessaires avant déploiement")
            sys.exit(1)

    if __name__ == '__main__':
        main()

except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("⚠️ Impossible de charger les utilitaires de dates")
    print("Vérifiez que le fichier src/backend/utils/date_utils.py existe")
    sys.exit(1)
except Exception as e:
    print(f"💥 Erreur inattendue: {e}")
    sys.exit(1)