#!/usr/bin/env python3
"""
Script de migration US1.6 - Conversion vers semaines ISO 8601 (lundi-dimanche)

Ce script effectue la migration des données existantes vers le nouveau format de semaine ISO 8601.
Il peut être utilisé indépendamment ou en complément de la migration Alembic.

Usage:
    python scripts/migrate_to_iso8601_weeks.py [--dry-run] [--backup] [--validate-only]
    
Options:
    --dry-run       : Simulation sans modifications réelles
    --backup        : Force la création d'un backup avant migration
    --validate-only : Valide seulement les données sans migrer
    --verbose       : Affichage détaillé
"""

import sys
import os
import argparse
import json
from datetime import datetime, date
from pathlib import Path

# Ajouter le répertoire backend au path
backend_path = Path(__file__).resolve().parent.parent / 'src' / 'backend'
sys.path.append(str(backend_path))

from database.config import get_config
from database import db
from models.meal_plan import MealPlan, ShoppingList
from utils.date_utils import (
    get_monday_of_week, 
    validate_week_start_iso8601,
    batch_convert_week_starts,
    validate_database_week_starts,
    format_week_display
)
from flask import Flask


class ISO8601MigrationTool:
    """Outil de migration vers les semaines ISO 8601"""
    
    def __init__(self, config_name: str = 'development', verbose: bool = False):
        self.config_name = config_name
        self.verbose = verbose
        self.stats = {
            'meal_plans_processed': 0,
            'meal_plans_converted': 0,
            'shopping_lists_processed': 0,
            'shopping_lists_converted': 0,
            'errors': []
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
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
    
    def create_backup(self) -> bool:
        """Crée un backup complet des tables affectées"""
        try:
            with self.app.app_context():
                backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                
                # Backup meal_plans
                backup_meal_plans = f"meal_plans_backup_{backup_timestamp}"
                db.session.execute(f"DROP TABLE IF EXISTS {backup_meal_plans}")
                db.session.execute(f"CREATE TABLE {backup_meal_plans} AS SELECT * FROM meal_plans")
                
                # Backup shopping_lists  
                backup_shopping_lists = f"shopping_lists_backup_{backup_timestamp}"
                db.session.execute(f"DROP TABLE IF EXISTS {backup_shopping_lists}")
                db.session.execute(f"CREATE TABLE {backup_shopping_lists} AS SELECT * FROM shopping_lists")
                
                db.session.commit()
                
                # Vérifier les backups
                meal_plans_count = db.session.execute(f"SELECT COUNT(*) FROM {backup_meal_plans}").scalar()
                shopping_lists_count = db.session.execute(f"SELECT COUNT(*) FROM {backup_shopping_lists}").scalar()
                
                self.log(f"✅ Backup créé: {backup_meal_plans} ({meal_plans_count} enregistrements)")
                self.log(f"✅ Backup créé: {backup_shopping_lists} ({shopping_lists_count} enregistrements)")
                
                return True
                
        except Exception as e:
            self.log(f"❌ Erreur lors du backup: {e}", 'ERROR')
            return False
    
    def validate_current_data(self) -> dict:
        """Valide les données actuelles et identifie les problèmes"""
        validation_report = {
            'total_meal_plans': 0,
            'total_shopping_lists': 0,
            'invalid_meal_plans': [],
            'invalid_shopping_lists': [],
            'is_valid': True
        }
        
        try:
            with self.app.app_context():
                # Valider meal_plans
                meal_plans = MealPlan.query.all()
                validation_report['total_meal_plans'] = len(meal_plans)
                
                for mp in meal_plans:
                    if not mp.week_start:
                        validation_report['invalid_meal_plans'].append({
                            'id': mp.id,
                            'issue': 'week_start est NULL',
                            'current_value': None
                        })
                    elif mp.week_start.weekday() != 0:  # Pas un lundi
                        validation_report['invalid_meal_plans'].append({
                            'id': mp.id,
                            'issue': f'week_start n\'est pas un lundi',
                            'current_value': mp.week_start,
                            'current_weekday': ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][mp.week_start.weekday()],
                            'correct_monday': get_monday_of_week(mp.week_start)
                        })
                
                # Valider shopping_lists
                shopping_lists = ShoppingList.query.all()
                validation_report['total_shopping_lists'] = len(shopping_lists)
                
                for sl in shopping_lists:
                    if not sl.week_start:
                        validation_report['invalid_shopping_lists'].append({
                            'id': sl.id,
                            'issue': 'week_start est NULL',
                            'current_value': None
                        })
                    elif sl.week_start.weekday() != 0:  # Pas un lundi
                        validation_report['invalid_shopping_lists'].append({
                            'id': sl.id,
                            'issue': f'week_start n\'est pas un lundi',
                            'current_value': sl.week_start,
                            'current_weekday': ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][sl.week_start.weekday()],
                            'correct_monday': get_monday_of_week(sl.week_start)
                        })
                
                # Déterminer si la validation est OK
                validation_report['is_valid'] = (
                    len(validation_report['invalid_meal_plans']) == 0 and 
                    len(validation_report['invalid_shopping_lists']) == 0
                )
                
                return validation_report
                
        except Exception as e:
            self.log(f"❌ Erreur lors de la validation: {e}", 'ERROR')
            validation_report['error'] = str(e)
            validation_report['is_valid'] = False
            return validation_report
    
    def migrate_meal_plans(self, dry_run: bool = False) -> bool:
        """Migre les meal_plans vers ISO 8601"""
        try:
            with self.app.app_context():
                meal_plans = MealPlan.query.all()
                self.stats['meal_plans_processed'] = len(meal_plans)
                
                updates = []
                for mp in meal_plans:
                    if mp.week_start and mp.week_start.weekday() != 0:
                        old_date = mp.week_start
                        new_date = get_monday_of_week(old_date)
                        
                        updates.append({
                            'id': mp.id,
                            'old_date': old_date,
                            'new_date': new_date,
                            'object': mp
                        })
                
                self.stats['meal_plans_converted'] = len(updates)
                
                if updates:
                    self.log(f"📋 {len(updates)} meal_plans à convertir:")
                    
                    for update in updates:
                        old_weekday = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][update['old_date'].weekday()]
                        self.log(f"  ID {update['id']}: {update['old_date']} ({old_weekday}) → {update['new_date']} (lundi)")
                        
                        if not dry_run:
                            update['object'].week_start = update['new_date']
                    
                    if not dry_run:
                        db.session.commit()
                        self.log(f"✅ {len(updates)} meal_plans mis à jour")
                    else:
                        self.log(f"🔍 Mode dry-run: {len(updates)} meal_plans seraient mis à jour")
                else:
                    self.log("✅ Aucun meal_plan à convertir (déjà conforme ISO 8601)")
                
                return True
                
        except Exception as e:
            if not dry_run:
                db.session.rollback()
            self.log(f"❌ Erreur lors de la migration des meal_plans: {e}", 'ERROR')
            self.stats['errors'].append(f"Migration meal_plans: {e}")
            return False
    
    def migrate_shopping_lists(self, dry_run: bool = False) -> bool:
        """Migre les shopping_lists vers ISO 8601"""
        try:
            with self.app.app_context():
                shopping_lists = ShoppingList.query.all()
                self.stats['shopping_lists_processed'] = len(shopping_lists)
                
                updates = []
                for sl in shopping_lists:
                    if sl.week_start and sl.week_start.weekday() != 0:
                        old_date = sl.week_start
                        new_date = get_monday_of_week(old_date)
                        
                        updates.append({
                            'id': sl.id,
                            'old_date': old_date,
                            'new_date': new_date,
                            'object': sl
                        })
                
                self.stats['shopping_lists_converted'] = len(updates)
                
                if updates:
                    self.log(f"🛒 {len(updates)} shopping_lists à convertir:")
                    
                    for update in updates:
                        old_weekday = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][update['old_date'].weekday()]
                        self.log(f"  ID {update['id']}: {update['old_date']} ({old_weekday}) → {update['new_date']} (lundi)")
                        
                        if not dry_run:
                            update['object'].week_start = update['new_date']
                    
                    if not dry_run:
                        db.session.commit()
                        self.log(f"✅ {len(updates)} shopping_lists mis à jour")
                    else:
                        self.log(f"🔍 Mode dry-run: {len(updates)} shopping_lists seraient mis à jour")
                else:
                    self.log("✅ Aucune shopping_list à convertir (déjà conforme ISO 8601)")
                
                return True
                
        except Exception as e:
            if not dry_run:
                db.session.rollback()
            self.log(f"❌ Erreur lors de la migration des shopping_lists: {e}", 'ERROR')
            self.stats['errors'].append(f"Migration shopping_lists: {e}")
            return False
    
    def post_migration_validation(self) -> bool:
        """Valide les données après migration"""
        self.log("🔍 Validation post-migration...")
        
        validation_report = self.validate_current_data()
        
        if validation_report['is_valid']:
            self.log(f"✅ Validation réussie:")
            self.log(f"  📋 {validation_report['total_meal_plans']} meal_plans validés")
            self.log(f"  🛒 {validation_report['total_shopping_lists']} shopping_lists validés")
            return True
        else:
            self.log("❌ Validation échouée:", 'ERROR')
            
            if validation_report['invalid_meal_plans']:
                self.log(f"  📋 {len(validation_report['invalid_meal_plans'])} meal_plans invalides")
                for invalid in validation_report['invalid_meal_plans'][:5]:  # Max 5 exemples
                    self.log(f"    ID {invalid['id']}: {invalid['issue']}")
            
            if validation_report['invalid_shopping_lists']:
                self.log(f"  🛒 {len(validation_report['invalid_shopping_lists'])} shopping_lists invalides")
                for invalid in validation_report['invalid_shopping_lists'][:5]:  # Max 5 exemples
                    self.log(f"    ID {invalid['id']}: {invalid['issue']}")
            
            return False
    
    def run_migration(self, dry_run: bool = False, create_backup: bool = True) -> bool:
        """Exécute la migration complète"""
        self.log("🚀 Début de la migration US1.6 - Semaines ISO 8601")
        self.log(f"Mode: {'DRY-RUN' if dry_run else 'PRODUCTION'}")
        
        # 1. Validation pré-migration
        self.log("1️⃣ Validation des données actuelles...")
        validation_report = self.validate_current_data()
        
        if validation_report.get('error'):
            self.log(f"❌ Erreur de validation: {validation_report['error']}", 'ERROR')
            return False
        
        if validation_report['is_valid']:
            self.log("✅ Données déjà conformes ISO 8601 - Aucune migration nécessaire")
            return True
        
        self.log(f"📊 Données à migrer:")
        self.log(f"  📋 Meal plans invalides: {len(validation_report['invalid_meal_plans'])}")
        self.log(f"  🛒 Shopping lists invalides: {len(validation_report['invalid_shopping_lists'])}")
        
        # 2. Backup (seulement en mode production)
        if create_backup and not dry_run:
            self.log("2️⃣ Création du backup...")
            if not self.create_backup():
                self.log("❌ Backup échoué - Arrêt de la migration", 'ERROR')
                return False
        
        # 3. Migration meal_plans
        self.log("3️⃣ Migration des meal_plans...")
        if not self.migrate_meal_plans(dry_run):
            return False
        
        # 4. Migration shopping_lists
        self.log("4️⃣ Migration des shopping_lists...")
        if not self.migrate_shopping_lists(dry_run):
            return False
        
        # 5. Validation post-migration (seulement en mode production)
        if not dry_run:
            self.log("5️⃣ Validation post-migration...")
            if not self.post_migration_validation():
                self.log("❌ Validation post-migration échouée", 'ERROR')
                return False
        
        # 6. Rapport final
        self.log("6️⃣ Rapport de migration:")
        self.log(f"  📋 Meal plans traités: {self.stats['meal_plans_processed']}")
        self.log(f"  📋 Meal plans convertis: {self.stats['meal_plans_converted']}")
        self.log(f"  🛒 Shopping lists traitées: {self.stats['shopping_lists_processed']}")
        self.log(f"  🛒 Shopping lists converties: {self.stats['shopping_lists_converted']}")
        
        if self.stats['errors']:
            self.log(f"  ⚠️ Erreurs: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                self.log(f"    - {error}")
        
        if dry_run:
            self.log("🔍 Migration simulée avec succès (dry-run)")
        else:
            self.log("✅ Migration US1.6 terminée avec succès")
        
        return len(self.stats['errors']) == 0


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Migration US1.6 - Semaines ISO 8601 (lundi-dimanche)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'usage:
  python scripts/migrate_to_iso8601_weeks.py --dry-run --verbose
  python scripts/migrate_to_iso8601_weeks.py --validate-only
  python scripts/migrate_to_iso8601_weeks.py --backup
        """
    )
    
    parser.add_argument('--dry-run', action='store_true', 
                       help='Simulation sans modifications réelles')
    parser.add_argument('--backup', action='store_true',
                       help='Force la création d\'un backup avant migration')
    parser.add_argument('--validate-only', action='store_true',
                       help='Valide seulement les données sans migrer') 
    parser.add_argument('--verbose', action='store_true',
                       help='Affichage détaillé')
    parser.add_argument('--config', default='development',
                       choices=['development', 'testing', 'production'],
                       help='Configuration à utiliser')
    
    args = parser.parse_args()
    
    # Initialiser l'outil de migration
    migrator = ISO8601MigrationTool(
        config_name=args.config,
        verbose=args.verbose
    )
    
    try:
        if args.validate_only:
            # Mode validation seulement
            migrator.log("🔍 Mode validation seulement")
            validation_report = migrator.validate_current_data()
            
            if validation_report['is_valid']:
                migrator.log("✅ Toutes les données sont conformes ISO 8601")
                sys.exit(0)
            else:
                migrator.log("❌ Données non conformes détectées:")
                
                # Afficher les détails
                if validation_report['invalid_meal_plans']:
                    migrator.log(f"📋 {len(validation_report['invalid_meal_plans'])} meal_plans invalides")
                    
                if validation_report['invalid_shopping_lists']:
                    migrator.log(f"🛒 {len(validation_report['invalid_shopping_lists'])} shopping_lists invalides")
                
                # Sauvegarder le rapport détaillé
                report_file = f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(validation_report, f, indent=2, default=str)
                
                migrator.log(f"📄 Rapport détaillé sauvé: {report_file}")
                sys.exit(1)
        
        else:
            # Mode migration
            success = migrator.run_migration(
                dry_run=args.dry_run,
                create_backup=args.backup or not args.dry_run
            )
            
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        migrator.log("⏹️ Migration interrompue par l'utilisateur", 'WARNING')
        sys.exit(1)
    except Exception as e:
        migrator.log(f"💥 Erreur inattendue: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()