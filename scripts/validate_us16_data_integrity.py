#!/usr/bin/env python3
"""
Validation de l'intégrité des données US1.6 - Semaines ISO 8601

Ce script effectue une validation complète de l'intégrité des données
après la migration vers les semaines ISO 8601 (lundi-dimanche).

Il vérifie:
- Conformité ISO 8601 des dates week_start
- Cohérence des relations entre tables
- Intégrité référentielle
- Validation des contraintes métier
- Détection d'anomalies

Usage:
    python scripts/validate_us16_data_integrity.py [--fix-issues] [--detailed-report]
"""

import sys
import os
import argparse
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict

# Ajouter le répertoire backend au path
backend_path = Path(__file__).resolve().parent.parent / 'src' / 'backend'
sys.path.append(str(backend_path))

from database.config import get_config
from database import db
from models.meal_plan import MealPlan, ShoppingList
from models.shopping_history import ShoppingListHistory, StoreCategory
from utils.date_utils import (
    validate_week_start_iso8601,
    get_monday_of_week,
    format_week_display,
    is_monday
)
from flask import Flask


class DataIntegrityValidator:
    """Validateur d'intégrité des données US1.6"""
    
    def __init__(self, config_name: str = 'development', verbose: bool = False):
        self.config_name = config_name
        self.verbose = verbose
        
        # Rapport de validation
        self.validation_report = {
            'timestamp': datetime.now().isoformat(),
            'config': config_name,
            'summary': {
                'total_issues': 0,
                'critical_issues': 0,
                'warning_issues': 0,
                'info_issues': 0
            },
            'categories': {},
            'fixed_issues': [],
            'recommendations': []
        }
        
        # Compteurs
        self.stats = {
            'meal_plans_checked': 0,
            'shopping_lists_checked': 0,
            'history_entries_checked': 0,
            'categories_checked': 0
        }
        
        # Initialiser Flask app
        self.app = Flask(__name__)
        config_class = get_config(config_name)
        self.app.config.from_object(config_class)
        db.init_app(self.app)
        
        if verbose:
            print(f"🔧 Configuration: {config_name}")
            print(f"🔧 Database: {self.app.config['SQLALCHEMY_DATABASE_URI']}")
    
    def log(self, message: str, level: str = 'INFO'):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        if self.verbose or level in ['ERROR', 'WARNING']:
            print(f"[{timestamp}] [{level}] {message}")
    
    def add_issue(self, category: str, severity: str, title: str, description: str, 
                  record_id: Optional[int] = None, table: Optional[str] = None, 
                  fix_sql: Optional[str] = None, metadata: Optional[Dict] = None):
        """Ajoute un problème au rapport"""
        
        if category not in self.validation_report['categories']:
            self.validation_report['categories'][category] = []
        
        issue = {
            'severity': severity,
            'title': title,
            'description': description,
            'timestamp': datetime.now().isoformat(),
        }
        
        if record_id:
            issue['record_id'] = record_id
        if table:
            issue['table'] = table
        if fix_sql:
            issue['fix_sql'] = fix_sql
        if metadata:
            issue['metadata'] = metadata
        
        self.validation_report['categories'][category].append(issue)
        self.validation_report['summary']['total_issues'] += 1
        
        if severity == 'CRITICAL':
            self.validation_report['summary']['critical_issues'] += 1
        elif severity == 'WARNING':
            self.validation_report['summary']['warning_issues'] += 1
        else:
            self.validation_report['summary']['info_issues'] += 1
    
    def validate_week_start_iso8601_compliance(self) -> bool:
        """Valide la conformité ISO 8601 des dates week_start"""
        self.log("🔍 Validation conformité ISO 8601...")
        
        all_valid = True
        
        with self.app.app_context():
            # Valider meal_plans
            meal_plans = MealPlan.query.all()
            self.stats['meal_plans_checked'] = len(meal_plans)
            
            for mp in meal_plans:
                if not mp.week_start:
                    self.add_issue(
                        'iso8601_compliance', 'CRITICAL',
                        f'Meal Plan {mp.id}: week_start NULL',
                        'La date week_start ne peut pas être NULL',
                        record_id=mp.id, table='meal_plans',
                        fix_sql=f"DELETE FROM meal_plans WHERE id = {mp.id}"
                    )
                    all_valid = False
                    
                elif not is_monday(mp.week_start):
                    correct_monday = get_monday_of_week(mp.week_start)
                    weekday_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
                    current_weekday = weekday_names[mp.week_start.weekday()]
                    
                    self.add_issue(
                        'iso8601_compliance', 'CRITICAL',
                        f'Meal Plan {mp.id}: week_start n\'est pas un lundi',
                        f'Date actuelle: {mp.week_start} ({current_weekday}). Devrait être: {correct_monday} (lundi)',
                        record_id=mp.id, table='meal_plans',
                        fix_sql=f"UPDATE meal_plans SET week_start = '{correct_monday}' WHERE id = {mp.id}",
                        metadata={
                            'current_date': mp.week_start.isoformat(),
                            'current_weekday': current_weekday,
                            'correct_date': correct_monday.isoformat()
                        }
                    )
                    all_valid = False
            
            # Valider shopping_lists
            shopping_lists = ShoppingList.query.all()
            self.stats['shopping_lists_checked'] = len(shopping_lists)
            
            for sl in shopping_lists:
                if not sl.week_start:
                    self.add_issue(
                        'iso8601_compliance', 'CRITICAL',
                        f'Shopping List {sl.id}: week_start NULL',
                        'La date week_start ne peut pas être NULL',
                        record_id=sl.id, table='shopping_lists',
                        fix_sql=f"DELETE FROM shopping_lists WHERE id = {sl.id}"
                    )
                    all_valid = False
                    
                elif not is_monday(sl.week_start):
                    correct_monday = get_monday_of_week(sl.week_start)
                    weekday_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
                    current_weekday = weekday_names[sl.week_start.weekday()]
                    
                    self.add_issue(
                        'iso8601_compliance', 'CRITICAL',
                        f'Shopping List {sl.id}: week_start n\'est pas un lundi',
                        f'Date actuelle: {sl.week_start} ({current_weekday}). Devrait être: {correct_monday} (lundi)',
                        record_id=sl.id, table='shopping_lists',
                        fix_sql=f"UPDATE shopping_lists SET week_start = '{correct_monday}' WHERE id = {sl.id}",
                        metadata={
                            'current_date': sl.week_start.isoformat(),
                            'current_weekday': current_weekday,
                            'correct_date': correct_monday.isoformat()
                        }
                    )
                    all_valid = False
        
        if all_valid:
            self.log("✅ Toutes les dates week_start sont conformes ISO 8601")
        else:
            self.log("❌ Dates week_start non conformes détectées", 'ERROR')
        
        return all_valid
    
    def validate_referential_integrity(self) -> bool:
        """Valide l'intégrité référentielle entre les tables"""
        self.log("🔍 Validation intégrité référentielle...")
        
        all_valid = True
        
        with self.app.app_context():
            # Vérifier shopping_lists -> meal_plans
            shopping_lists = ShoppingList.query.all()
            
            for sl in shopping_lists:
                meal_plan = MealPlan.query.get(sl.meal_plan_id)
                
                if not meal_plan:
                    self.add_issue(
                        'referential_integrity', 'CRITICAL',
                        f'Shopping List {sl.id}: meal_plan orphelin',
                        f'Référence vers meal_plan_id {sl.meal_plan_id} qui n\'existe pas',
                        record_id=sl.id, table='shopping_lists',
                        fix_sql=f"DELETE FROM shopping_lists WHERE id = {sl.id}"
                    )
                    all_valid = False
                
                # Vérifier cohérence des dates week_start
                elif sl.week_start != meal_plan.week_start:
                    self.add_issue(
                        'referential_integrity', 'WARNING',
                        f'Shopping List {sl.id}: incohérence date week_start',
                        f'Shopping list week_start: {sl.week_start}, Meal plan week_start: {meal_plan.week_start}',
                        record_id=sl.id, table='shopping_lists',
                        fix_sql=f"UPDATE shopping_lists SET week_start = '{meal_plan.week_start}' WHERE id = {sl.id}",
                        metadata={
                            'shopping_list_date': sl.week_start.isoformat(),
                            'meal_plan_date': meal_plan.week_start.isoformat()
                        }
                    )
                    all_valid = False
            
            # Vérifier shopping_list_history -> shopping_lists
            history_entries = ShoppingListHistory.query.all()
            self.stats['history_entries_checked'] = len(history_entries)
            
            for history in history_entries:
                shopping_list = ShoppingList.query.get(history.shopping_list_id)
                
                if not shopping_list:
                    self.add_issue(
                        'referential_integrity', 'WARNING',
                        f'History {history.id}: shopping_list orphelin',
                        f'Référence vers shopping_list_id {history.shopping_list_id} qui n\'existe pas',
                        record_id=history.id, table='shopping_list_history',
                        fix_sql=f"DELETE FROM shopping_list_history WHERE id = {history.id}"
                    )
                    all_valid = False
        
        if all_valid:
            self.log("✅ Intégrité référentielle validée")
        else:
            self.log("❌ Problèmes d'intégrité référentielle détectés", 'ERROR')
        
        return all_valid
    
    def validate_business_constraints(self) -> bool:
        """Valide les contraintes métier"""
        self.log("🔍 Validation contraintes métier...")
        
        all_valid = True
        
        with self.app.app_context():
            # Vérifier les doublons de meal_plans (user_id + week_start uniques)
            meal_plans_by_user_week = defaultdict(list)
            
            for mp in MealPlan.query.all():
                key = (mp.user_id, mp.week_start)
                meal_plans_by_user_week[key].append(mp)
            
            for (user_id, week_start), meal_plans in meal_plans_by_user_week.items():
                if len(meal_plans) > 1:
                    ids = [str(mp.id) for mp in meal_plans]
                    self.add_issue(
                        'business_constraints', 'WARNING',
                        f'Doublons meal_plans: utilisateur {user_id}, semaine {week_start}',
                        f'Plusieurs meal_plans trouvés: IDs {", ".join(ids)}',
                        metadata={
                            'user_id': user_id,
                            'week_start': week_start.isoformat() if week_start else None,
                            'duplicate_ids': ids
                        }
                    )
                    all_valid = False
            
            # Vérifier les meal_plans dans le futur (plus de 4 semaines)
            max_future_date = date.today() + timedelta(weeks=4)
            future_meal_plans = MealPlan.query.filter(MealPlan.week_start > max_future_date).all()
            
            for mp in future_meal_plans:
                self.add_issue(
                    'business_constraints', 'INFO',
                    f'Meal Plan {mp.id}: planification très future',
                    f'Meal plan programmé pour {mp.week_start} (> 4 semaines)',
                    record_id=mp.id, table='meal_plans',
                    metadata={'week_start': mp.week_start.isoformat()}
                )
            
            # Vérifier les shopping_lists sans items
            empty_shopping_lists = ShoppingList.query.filter(
                (ShoppingList.items_json == '[]') | 
                (ShoppingList.items_json == None) |
                (ShoppingList.items_json == '')
            ).all()
            
            for sl in empty_shopping_lists:
                self.add_issue(
                    'business_constraints', 'WARNING',
                    f'Shopping List {sl.id}: liste vide',
                    'Liste de courses sans articles',
                    record_id=sl.id, table='shopping_lists'
                )
            
            # Vérifier les valeurs nutritionnelles aberrantes
            for mp in MealPlan.query.all():
                if mp.daily_calories and (mp.daily_calories < 500 or mp.daily_calories > 5000):
                    self.add_issue(
                        'business_constraints', 'WARNING',
                        f'Meal Plan {mp.id}: calories aberrantes',
                        f'Calories quotidiennes: {mp.daily_calories} (normale: 1200-3000)',
                        record_id=mp.id, table='meal_plans',
                        metadata={'daily_calories': mp.daily_calories}
                    )
                
                if mp.daily_protein and (mp.daily_protein < 20 or mp.daily_protein > 300):
                    self.add_issue(
                        'business_constraints', 'WARNING',
                        f'Meal Plan {mp.id}: protéines aberrantes',
                        f'Protéines quotidiennes: {mp.daily_protein}g (normale: 50-200g)',
                        record_id=mp.id, table='meal_plans',
                        metadata={'daily_protein': mp.daily_protein}
                    )
        
        if all_valid:
            self.log("✅ Contraintes métier respectées")
        else:
            self.log("⚠️ Violations de contraintes métier détectées", 'WARNING')
        
        return all_valid
    
    def validate_data_consistency(self) -> bool:
        """Valide la cohérence des données"""
        self.log("🔍 Validation cohérence des données...")
        
        all_valid = True
        
        with self.app.app_context():
            # Vérifier la cohérence des timestamps
            for mp in MealPlan.query.all():
                if mp.created_at and mp.updated_at and mp.created_at > mp.updated_at:
                    self.add_issue(
                        'data_consistency', 'WARNING',
                        f'Meal Plan {mp.id}: timestamps incohérents',
                        f'created_at ({mp.created_at}) > updated_at ({mp.updated_at})',
                        record_id=mp.id, table='meal_plans'
                    )
                    all_valid = False
            
            # Vérifier la cohérence des dates de shopping_lists
            for sl in ShoppingList.query.all():
                if sl.generated_date and sl.last_updated and sl.generated_date > sl.last_updated:
                    self.add_issue(
                        'data_consistency', 'WARNING',
                        f'Shopping List {sl.id}: dates incohérentes',
                        f'generated_date ({sl.generated_date}) > last_updated ({sl.last_updated})',
                        record_id=sl.id, table='shopping_lists'
                    )
                    all_valid = False
                
                # Vérifier la cohérence des dates de completion
                if sl.is_completed and not sl.completion_date:
                    self.add_issue(
                        'data_consistency', 'WARNING',
                        f'Shopping List {sl.id}: completion_date manquante',
                        'Liste marquée comme terminée mais sans date de completion',
                        record_id=sl.id, table='shopping_lists',
                        fix_sql=f"UPDATE shopping_lists SET completion_date = last_updated WHERE id = {sl.id}"
                    )
                    all_valid = False
        
        if all_valid:
            self.log("✅ Cohérence des données validée")
        else:
            self.log("⚠️ Problèmes de cohérence détectés", 'WARNING')
        
        return all_valid
    
    def auto_fix_issues(self, dry_run: bool = True) -> int:
        """Corrige automatiquement les problèmes réparables"""
        if not dry_run:
            self.log("🔧 Correction automatique des problèmes...")
        else:
            self.log("🔍 Simulation de correction (dry-run)...")
        
        fixes_applied = 0
        
        with self.app.app_context():
            for category, issues in self.validation_report['categories'].items():
                for issue in issues:
                    if 'fix_sql' in issue and issue['severity'] in ['CRITICAL', 'WARNING']:
                        try:
                            if not dry_run:
                                db.session.execute(issue['fix_sql'])
                                db.session.commit()
                                
                                self.validation_report['fixed_issues'].append({
                                    'issue': issue,
                                    'fixed_at': datetime.now().isoformat()
                                })
                            
                            fixes_applied += 1
                            self.log(f"  ✅ {'Simulé' if dry_run else 'Appliqué'}: {issue['title']}")
                            
                        except Exception as e:
                            self.log(f"  ❌ Erreur correction {issue['title']}: {e}", 'ERROR')
                            if not dry_run:
                                db.session.rollback()
        
        self.log(f"🔧 {fixes_applied} corrections {'simulées' if dry_run else 'appliquées'}")
        return fixes_applied
    
    def generate_recommendations(self):
        """Génère des recommandations basées sur les problèmes détectés"""
        
        recommendations = []
        
        # Analyser les catégories de problèmes
        for category, issues in self.validation_report['categories'].items():
            critical_count = sum(1 for issue in issues if issue['severity'] == 'CRITICAL')
            warning_count = sum(1 for issue in issues if issue['severity'] == 'WARNING')
            
            if category == 'iso8601_compliance' and critical_count > 0:
                recommendations.append({
                    'priority': 'HIGH',
                    'title': 'Corriger les dates week_start non conformes ISO 8601',
                    'description': f'{critical_count} dates week_start ne sont pas des lundis. Utiliser le script de migration ou les requêtes de correction automatique.',
                    'action': 'Exécuter: python scripts/migrate_to_iso8601_weeks.py --dry-run'
                })
            
            if category == 'referential_integrity' and critical_count > 0:
                recommendations.append({
                    'priority': 'HIGH',
                    'title': 'Nettoyer les références orphelines',
                    'description': f'{critical_count} enregistrements avec des références invalides détectés.',
                    'action': 'Utiliser l\'option --fix-issues pour supprimer les enregistrements orphelins'
                })
            
            if category == 'business_constraints' and warning_count > 5:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'title': 'Réviser les contraintes métier',
                    'description': f'{warning_count} violations de contraintes détectées. Réviser les règles de validation.',
                    'action': 'Analyser le rapport détaillé et mettre à jour les validations applicatives'
                })
        
        # Recommandations générales
        if self.validation_report['summary']['total_issues'] > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'title': 'Mettre en place une validation automatique',
                'description': 'Intégrer ce script de validation dans les tests automatisés.',
                'action': 'Ajouter validate_us16_data_integrity.py aux scripts de CI/CD'
            })
        
        self.validation_report['recommendations'] = recommendations
    
    def run_full_validation(self, fix_issues: bool = False, dry_run: bool = True) -> bool:
        """Exécute la validation complète"""
        self.log("🚀 Début de la validation complète US1.6")
        
        # 1. Validation ISO 8601
        iso8601_valid = self.validate_week_start_iso8601_compliance()
        
        # 2. Validation intégrité référentielle
        integrity_valid = self.validate_referential_integrity()
        
        # 3. Validation contraintes métier
        business_valid = self.validate_business_constraints()
        
        # 4. Validation cohérence des données
        consistency_valid = self.validate_data_consistency()
        
        # 5. Corrections automatiques si demandées
        fixes_applied = 0
        if fix_issues:
            fixes_applied = self.auto_fix_issues(dry_run=dry_run)
        
        # 6. Générer des recommandations
        self.generate_recommendations()
        
        # 7. Rapport final
        all_valid = iso8601_valid and integrity_valid and business_valid and consistency_valid
        
        self.log("📊 Résumé de la validation:")
        self.log(f"  📋 Meal plans vérifiés: {self.stats['meal_plans_checked']}")
        self.log(f"  🛒 Shopping lists vérifiées: {self.stats['shopping_lists_checked']}")
        self.log(f"  📝 Entrées historique vérifiées: {self.stats['history_entries_checked']}")
        self.log(f"  🏪 Catégories vérifiées: {self.stats['categories_checked']}")
        self.log("")
        self.log(f"  ❌ Problèmes critiques: {self.validation_report['summary']['critical_issues']}")
        self.log(f"  ⚠️ Avertissements: {self.validation_report['summary']['warning_issues']}")
        self.log(f"  ℹ️ Informations: {self.validation_report['summary']['info_issues']}")
        
        if fixes_applied > 0:
            self.log(f"  🔧 Corrections appliquées: {fixes_applied}")
        
        if all_valid:
            self.log("✅ Validation complète réussie - Aucun problème critique")
        else:
            self.log("❌ Problèmes détectés - Consulter le rapport détaillé", 'WARNING')
        
        return all_valid
    
    def save_report(self, output_file: Optional[str] = None) -> str:
        """Sauvegarde le rapport de validation"""
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"us16_validation_report_{timestamp}.json"
        
        # Ajouter les statistiques au rapport
        self.validation_report['stats'] = self.stats
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_report, f, indent=2, ensure_ascii=False, default=str)
        
        self.log(f"📄 Rapport sauvé: {output_file}")
        return output_file


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Validation intégrité données US1.6',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--fix-issues', action='store_true',
                       help='Corriger automatiquement les problèmes réparables')
    parser.add_argument('--dry-run', action='store_true', default=True,
                       help='Mode simulation pour les corrections (défaut: activé)')
    parser.add_argument('--no-dry-run', action='store_true',
                       help='Désactiver le mode simulation (corrections réelles)')
    parser.add_argument('--detailed-report', action='store_true',
                       help='Générer un rapport détaillé')
    parser.add_argument('--output-file',
                       help='Fichier de sortie pour le rapport JSON')
    parser.add_argument('--config', default='development',
                       choices=['development', 'testing', 'production'],
                       help='Configuration à utiliser')
    parser.add_argument('--verbose', action='store_true',
                       help='Affichage détaillé')
    
    args = parser.parse_args()
    
    # Gérer les options dry-run
    if args.no_dry_run:
        dry_run = False
    else:
        dry_run = args.dry_run
    
    # Initialiser le validateur
    validator = DataIntegrityValidator(
        config_name=args.config,
        verbose=args.verbose
    )
    
    try:
        # Exécuter la validation
        success = validator.run_full_validation(
            fix_issues=args.fix_issues,
            dry_run=dry_run
        )
        
        # Sauvegarder le rapport si demandé
        if args.detailed_report:
            report_file = validator.save_report(args.output_file)
            
            # Afficher quelques détails du rapport
            if validator.validation_report['summary']['total_issues'] > 0:
                print("\n📋 Détails des problèmes:")
                for category, issues in validator.validation_report['categories'].items():
                    if issues:
                        print(f"\n  📂 {category.replace('_', ' ').title()}:")
                        for issue in issues[:3]:  # Max 3 exemples
                            print(f"    • {issue['title']}")
                        if len(issues) > 3:
                            print(f"    ... et {len(issues) - 3} autres")
            
            # Afficher les recommandations
            if validator.validation_report['recommendations']:
                print("\n💡 Recommandations:")
                for rec in validator.validation_report['recommendations']:
                    priority_icon = '🔥' if rec['priority'] == 'HIGH' else '⚠️'
                    print(f"  {priority_icon} {rec['title']}")
                    print(f"     {rec['description']}")
                    if 'action' in rec:
                        print(f"     Action: {rec['action']}")
                    print()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        validator.log("⏹️ Validation interrompue par l'utilisateur", 'WARNING')
        sys.exit(1)
    except Exception as e:
        validator.log(f"💥 Erreur inattendue: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()