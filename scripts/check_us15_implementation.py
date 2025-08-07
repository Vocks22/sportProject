#!/usr/bin/env python3
"""
Script de vérification de l'implémentation US1.5
Vérifie que tous les fichiers et composants sont en place
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Vérifie qu'un fichier existe"""
    if os.path.exists(file_path):
        print(f"   ✅ {description}")
        return True
    else:
        print(f"   ❌ {description} - MANQUANT")
        return False

def check_directory_exists(dir_path, description):
    """Vérifie qu'un répertoire existe"""
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print(f"   ✅ {description}")
        return True
    else:
        print(f"   ❌ {description} - MANQUANT")
        return False

def check_file_contains(file_path, search_terms, description):
    """Vérifie qu'un fichier contient certains termes"""
    if not os.path.exists(file_path):
        print(f"   ❌ {description} - FICHIER MANQUANT")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        missing_terms = []
        for term in search_terms:
            if term not in content:
                missing_terms.append(term)
        
        if not missing_terms:
            print(f"   ✅ {description}")
            return True
        else:
            print(f"   ⚠️ {description} - Termes manquants: {', '.join(missing_terms)}")
            return False
    
    except Exception as e:
        print(f"   ❌ {description} - Erreur de lecture: {e}")
        return False

def main():
    print("🔍 Vérification de l'implémentation US1.5 - Liste de Courses Interactive")
    print("=" * 80)
    
    base_path = Path(__file__).parent.parent
    
    all_checks_passed = True
    
    # 1. Vérification des modèles backend
    print("\n📦 1. MODÈLES BACKEND")
    checks = [
        (base_path / "src/backend/models/meal_plan.py", "Modèle MealPlan et ShoppingList"),
        (base_path / "src/backend/models/shopping_history.py", "Modèles ShoppingListHistory et StoreCategory"),
        (base_path / "src/backend/models/ingredient.py", "Modèle Ingredient"),
    ]
    
    for file_path, description in checks:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # 2. Vérification des services backend
    print("\n⚙️ 2. SERVICES BACKEND")
    service_file = base_path / "src/backend/services/shopping_service.py"
    if check_file_exists(service_file, "Service ShoppingService"):
        # Vérifier les méthodes clés
        methods_to_check = [
            "generate_optimized_shopping_list",
            "update_item_status",
            "get_shopping_list_statistics",
            "export_shopping_list_data",
            "_group_by_store_categories",
            "_apply_unit_conversion"
        ]
        
        if not check_file_contains(service_file, methods_to_check, "Méthodes du ShoppingService"):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 3. Vérification des schémas
    print("\n📋 3. SCHÉMAS MARSHMALLOW")
    schema_file = base_path / "src/backend/schemas/meal_plan.py"
    if check_file_exists(schema_file, "Schémas Marshmallow"):
        schemas_to_check = [
            "OptimizedShoppingListSchema",
            "ItemToggleSchema",
            "BulkToggleSchema",
            "ShoppingListExportSchema",
            "ShoppingListStatisticsSchema"
        ]
        
        if not check_file_contains(schema_file, schemas_to_check, "Nouveaux schémas US1.5"):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 4. Vérification des routes API
    print("\n🛣️ 4. ROUTES API")
    routes_file = base_path / "src/backend/routes/meal_plans.py"
    if check_file_exists(routes_file, "Routes API"):
        endpoints_to_check = [
            "toggle_shopping_item",
            "bulk_toggle_items",
            "get_shopping_list_statistics",
            "prepare_shopping_list_export",
            "get_shopping_list_history"
        ]
        
        if not check_file_contains(routes_file, endpoints_to_check, "Nouveaux endpoints US1.5"):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 5. Vérification des migrations
    print("\n🗄️ 5. MIGRATIONS BASE DE DONNÉES")
    migration_file = base_path / "src/backend/database/migrations/versions/003_add_shopping_list_enhancements.py"
    if check_file_exists(migration_file, "Migration US1.5"):
        migration_elements = [
            "shopping_list_history",
            "store_categories",
            "checked_items_json",
            "aggregation_rules_json"
        ]
        
        if not check_file_contains(migration_file, migration_elements, "Éléments de migration"):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 6. Vérification des hooks React
    print("\n⚛️ 6. HOOKS REACT")
    hook_file = base_path / "src/frontend/hooks/useShoppingList.js"
    if check_file_exists(hook_file, "Hook useShoppingList"):
        hook_functions = [
            "toggleItemStatus",
            "bulkToggleItems",
            "getListStatistics",
            "exportList",
            "getListHistory",
            "useNetworkStatus"
        ]
        
        if not check_file_contains(hook_file, hook_functions, "Fonctions du hook US1.5"):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 7. Vérification du composant Shopping
    print("\n🖥️ 7. COMPOSANT SHOPPING")
    component_file = base_path / "src/frontend/components/Shopping.jsx"
    if check_file_exists(component_file, "Composant Shopping"):
        component_features = [
            "showStatsModal",
            "showHistoryModal",
            "handleShowStatistics",
            "handleShowHistory",
            "handleExport",
            "BarChart3",
            "History"
        ]
        
        if not check_file_contains(component_file, component_features, "Fonctionnalités US1.5 du composant"):
            all_checks_passed = False
    else:
        all_checks_passed = False
    
    # 8. Vérification des tests
    print("\n🧪 8. TESTS UNITAIRES")
    test_checks = [
        (base_path / "tests/backend/test_shopping_service_us15.py", "Tests service backend"),
        (base_path / "tests/backend/test_shopping_api_us15.py", "Tests API backend"),
        (base_path / "tests/frontend/shopping-us15.test.jsx", "Tests composant React"),
    ]
    
    for file_path, description in test_checks:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # 9. Vérification des scripts d'intégration
    print("\n🔧 9. SCRIPTS D'INTÉGRATION")
    script_checks = [
        (base_path / "scripts/test_us15_integration.py", "Script de test d'intégration"),
        (base_path / "scripts/check_us15_implementation.py", "Script de vérification (actuel)"),
    ]
    
    for file_path, description in script_checks:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # 10. Vérification de la configuration
    print("\n⚙️ 10. CONFIGURATION")
    config_checks = [
        (base_path / "src/backend/main.py", "Configuration principale"),
        (base_path / "package.json", "Configuration npm"),
        (base_path / "requirements.txt", "Dépendances Python"),
    ]
    
    for file_path, description in config_checks:
        if not check_file_exists(file_path, description):
            all_checks_passed = False
    
    # Vérifier que main.py importe les nouveaux modèles
    main_py = base_path / "src/backend/main.py"
    if main_py.exists():
        import_terms = [
            "ShoppingListHistory",
            "StoreCategory"
        ]
        if not check_file_contains(main_py, import_terms, "Imports des nouveaux modèles"):
            all_checks_passed = False
    
    # 11. Résumé final
    print("\n" + "=" * 80)
    if all_checks_passed:
        print("🎉 SUCCÈS: Tous les composants US1.5 sont en place !")
        print("✨ L'implémentation semble complète et prête pour les tests")
        print("\n📋 PROCHAINES ÉTAPES:")
        print("   1. Exécuter les migrations de base de données")
        print("   2. Démarrer le serveur Flask")
        print("   3. Lancer le script de test d'intégration")
        print("   4. Tester l'interface utilisateur")
    else:
        print("⚠️ ATTENTION: Certains composants sont manquants ou incomplets")
        print("🔧 Veuillez corriger les problèmes avant de continuer")
    
    print("\n💡 COMMANDES UTILES:")
    print("   • Tests backend: python -m pytest tests/backend/test_shopping_*")
    print("   • Tests frontend: npm test shopping-us15")
    print("   • Test d'intégration: python scripts/test_us15_integration.py")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)