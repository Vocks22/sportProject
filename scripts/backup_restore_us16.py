#!/usr/bin/env python3
"""
Scripts de Backup et Rollback pour US1.6 - Semaines ISO 8601

Ce module fournit des outils robustes pour la sauvegarde et restauration 
des données avant et après la migration US1.6.

Usage:
    python scripts/backup_restore_us16.py backup [--name custom_name]
    python scripts/backup_restore_us16.py restore --backup-name backup_name
    python scripts/backup_restore_us16.py list-backups
    python scripts/backup_restore_us16.py cleanup [--older-than 7]
"""

import sys
import os
import argparse
import json
import shutil
from datetime import datetime, timedelta, date
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ajouter le répertoire backend au path
backend_path = Path(__file__).resolve().parent.parent / 'src' / 'backend'
sys.path.append(str(backend_path))

from database.config import get_config
from database import db
from models.meal_plan import MealPlan, ShoppingList
from models.shopping_history import ShoppingListHistory, StoreCategory
from flask import Flask


class US16BackupManager:
    """Gestionnaire de backup/restore pour la migration US1.6"""
    
    def __init__(self, config_name: str = 'development', verbose: bool = False):
        self.config_name = config_name
        self.verbose = verbose
        
        # Répertoire de backup
        self.backup_dir = Path(__file__).resolve().parent.parent / 'backups' / 'us16_migration'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Tables à sauvegarder
        self.tables_to_backup = [
            'meal_plans',
            'shopping_lists',
            'shopping_list_history',
            'store_categories'
        ]
        
        # Initialiser Flask app
        self.app = Flask(__name__)
        config_class = get_config(config_name)
        self.app.config.from_object(config_class)
        db.init_app(self.app)
        
        if verbose:
            print(f"🔧 Configuration: {config_name}")
            print(f"📁 Répertoire de backup: {self.backup_dir}")
    
    def log(self, message: str, level: str = 'INFO'):
        """Log avec timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if self.verbose or level in ['ERROR', 'WARNING']:
            print(f"[{timestamp}] [{level}] {message}")
    
    def generate_backup_name(self, custom_name: Optional[str] = None) -> str:
        """Génère un nom de backup unique"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if custom_name:
            return f"us16_{custom_name}_{timestamp}"
        else:
            return f"us16_auto_{timestamp}"
    
    def create_full_backup(self, backup_name: Optional[str] = None) -> Tuple[bool, str, Dict]:
        """
        Crée un backup complet des tables concernées par US1.6
        
        Returns:
            (success, backup_path, metadata)
        """
        if not backup_name:
            backup_name = self.generate_backup_name()
        
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        metadata = {
            'backup_name': backup_name,
            'created_at': datetime.now().isoformat(),
            'config': self.config_name,
            'database_uri': self.app.config['SQLALCHEMY_DATABASE_URI'],
            'tables': {},
            'total_records': 0
        }
        
        self.log(f"🔄 Création du backup: {backup_name}")
        
        try:
            with self.app.app_context():
                for table_name in self.tables_to_backup:
                    self.log(f"  📦 Backup table: {table_name}")
                    
                    # Récupérer les données
                    if table_name == 'meal_plans':
                        data = [mp.to_dict() for mp in MealPlan.query.all()]
                    elif table_name == 'shopping_lists':
                        data = [sl.to_dict() for sl in ShoppingList.query.all()]
                    elif table_name == 'shopping_list_history':
                        data = [slh.to_dict() for slh in ShoppingListHistory.query.all()]
                    elif table_name == 'store_categories':
                        data = [sc.to_dict() for sc in StoreCategory.query.all()]
                    else:
                        self.log(f"⚠️ Table non reconnue: {table_name}", 'WARNING')
                        continue
                    
                    # Sauvegarder en JSON
                    table_file = backup_path / f"{table_name}.json"
                    with open(table_file, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
                    
                    # Métadonnées
                    metadata['tables'][table_name] = {
                        'record_count': len(data),
                        'file_size': table_file.stat().st_size,
                        'file_path': str(table_file)
                    }
                    metadata['total_records'] += len(data)
                    
                    self.log(f"    ✅ {len(data)} enregistrements sauvés")
                
                # Sauvegarder les métadonnées
                metadata_file = backup_path / 'metadata.json'
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                
                # Backup SQL brut (pour rollback d'urgence)
                self._create_sql_dump(backup_path)
                
                self.log(f"✅ Backup créé avec succès: {backup_path}")
                self.log(f"📊 Total: {metadata['total_records']} enregistrements")
                
                return True, str(backup_path), metadata
                
        except Exception as e:
            self.log(f"❌ Erreur lors du backup: {e}", 'ERROR')
            # Nettoyer le répertoire en cas d'erreur
            if backup_path.exists():
                shutil.rmtree(backup_path, ignore_errors=True)
            return False, "", {}
    
    def _create_sql_dump(self, backup_path: Path):
        """Crée un dump SQL des tables"""
        try:
            with self.app.app_context():
                sql_dump_file = backup_path / 'sql_dump.sql'
                
                with open(sql_dump_file, 'w', encoding='utf-8') as f:
                    f.write(f"-- Backup SQL US1.6 - {datetime.now().isoformat()}\\n")
                    f.write(f"-- Configuration: {self.config_name}\\n\\n")
                    
                    for table_name in self.tables_to_backup:
                        f.write(f"-- Backup table: {table_name}\\n")
                        f.write(f"DROP TABLE IF EXISTS {table_name}_backup_us16;\\n")
                        f.write(f"CREATE TABLE {table_name}_backup_us16 AS SELECT * FROM {table_name};\\n\\n")
                
                self.log(f"  📄 Dump SQL créé: {sql_dump_file}")
                
        except Exception as e:
            self.log(f"⚠️ Erreur lors de la création du dump SQL: {e}", 'WARNING')
    
    def list_backups(self) -> List[Dict]:
        """Liste tous les backups disponibles"""
        backups = []
        
        if not self.backup_dir.exists():
            return backups
        
        for backup_path in self.backup_dir.iterdir():
            if backup_path.is_dir() and backup_path.name.startswith('us16_'):
                metadata_file = backup_path / 'metadata.json'
                
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        metadata['path'] = str(backup_path)
                        metadata['size_mb'] = round(self._get_folder_size(backup_path) / 1024 / 1024, 2)
                        backups.append(metadata)
                        
                    except Exception as e:
                        self.log(f"⚠️ Erreur lecture backup {backup_path.name}: {e}", 'WARNING')
                        
                        # Backup corrompu - informations basiques
                        backups.append({
                            'backup_name': backup_path.name,
                            'path': str(backup_path),
                            'created_at': datetime.fromtimestamp(backup_path.stat().st_mtime).isoformat(),
                            'status': 'corrupted',
                            'size_mb': round(self._get_folder_size(backup_path) / 1024 / 1024, 2)
                        })
        
        # Trier par date de création (plus récent en premier)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return backups
    
    def _get_folder_size(self, folder_path: Path) -> int:
        """Calcule la taille d'un dossier en bytes"""
        return sum(f.stat().st_size for f in folder_path.rglob('*') if f.is_file())
    
    def restore_from_backup(self, backup_name: str, confirm: bool = False) -> bool:
        """
        Restaure les données depuis un backup
        
        ATTENTION: Cette opération supprime toutes les données actuelles !
        """
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            self.log(f"❌ Backup introuvable: {backup_name}", 'ERROR')
            return False
        
        metadata_file = backup_path / 'metadata.json'
        if not metadata_file.exists():
            self.log(f"❌ Métadonnées du backup introuvables: {backup_name}", 'ERROR')
            return False
        
        # Charger les métadonnées
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        except Exception as e:
            self.log(f"❌ Erreur lecture métadonnées: {e}", 'ERROR')
            return False
        
        if not confirm:
            self.log("⚠️ ATTENTION: La restauration va supprimer toutes les données actuelles!", 'WARNING')
            self.log(f"Backup à restaurer: {backup_name}")
            self.log(f"Date de création: {metadata.get('created_at', 'Unknown')}")
            self.log(f"Total d'enregistrements: {metadata.get('total_records', 0)}")
            self.log("Utilisez --confirm pour procéder à la restauration")
            return False
        
        self.log(f"🔄 Début de la restauration: {backup_name}")
        
        try:
            with self.app.app_context():
                # Créer un backup de sécurité avant restauration
                safety_backup_name = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                self.log(f"🔒 Backup de sécurité: {safety_backup_name}")
                self.create_full_backup(safety_backup_name)
                
                # Restaurer chaque table
                for table_name in self.tables_to_backup:
                    table_file = backup_path / f"{table_name}.json"
                    
                    if not table_file.exists():
                        self.log(f"⚠️ Fichier manquant: {table_file}", 'WARNING')
                        continue
                    
                    self.log(f"  🔄 Restauration table: {table_name}")
                    
                    # Charger les données
                    with open(table_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Vider la table actuelle
                    if table_name == 'meal_plans':
                        MealPlan.query.delete()
                        # Recréer les enregistrements
                        for item_data in data:
                            mp = MealPlan.create_from_dict(item_data)
                            db.session.add(mp)
                    
                    elif table_name == 'shopping_lists':
                        ShoppingList.query.delete()
                        for item_data in data:
                            sl = ShoppingList.create_from_dict(item_data)
                            db.session.add(sl)
                    
                    elif table_name == 'shopping_list_history':
                        ShoppingListHistory.query.delete()
                        for item_data in data:
                            slh = ShoppingListHistory.create_from_dict(item_data)
                            db.session.add(slh)
                    
                    elif table_name == 'store_categories':
                        StoreCategory.query.delete()
                        for item_data in data:
                            sc = StoreCategory(**item_data)
                            db.session.add(sc)
                    
                    db.session.commit()
                    self.log(f"    ✅ {len(data)} enregistrements restaurés")
                
                self.log(f"✅ Restauration terminée avec succès")
                self.log(f"🔒 Backup de sécurité disponible: {safety_backup_name}")
                
                return True
                
        except Exception as e:
            db.session.rollback()
            self.log(f"❌ Erreur lors de la restauration: {e}", 'ERROR')
            return False
    
    def cleanup_old_backups(self, older_than_days: int = 30) -> int:
        """Supprime les backups plus anciens que X jours"""
        if older_than_days <= 0:
            self.log("⚠️ Paramètre older_than_days doit être > 0", 'WARNING')
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        backups = self.list_backups()
        
        deleted_count = 0
        for backup in backups:
            try:
                backup_date = datetime.fromisoformat(backup.get('created_at', ''))
                if backup_date < cutoff_date:
                    backup_path = Path(backup['path'])
                    
                    self.log(f"🗑️ Suppression backup ancien: {backup['backup_name']}")
                    shutil.rmtree(backup_path, ignore_errors=True)
                    deleted_count += 1
                    
            except Exception as e:
                self.log(f"⚠️ Erreur suppression {backup.get('backup_name', 'unknown')}: {e}", 'WARNING')
        
        self.log(f"✅ {deleted_count} backups supprimés (> {older_than_days} jours)")
        return deleted_count
    
    def verify_backup_integrity(self, backup_name: str) -> bool:
        """Vérifie l'intégrité d'un backup"""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            self.log(f"❌ Backup introuvable: {backup_name}", 'ERROR')
            return False
        
        metadata_file = backup_path / 'metadata.json'
        if not metadata_file.exists():
            self.log(f"❌ Métadonnées manquantes: {backup_name}", 'ERROR')
            return False
        
        try:
            # Vérifier les métadonnées
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Vérifier chaque fichier de table
            for table_name, table_info in metadata.get('tables', {}).items():
                table_file = backup_path / f"{table_name}.json"
                
                if not table_file.exists():
                    self.log(f"❌ Fichier manquant: {table_file}", 'ERROR')
                    return False
                
                # Vérifier la taille du fichier
                actual_size = table_file.stat().st_size
                expected_size = table_info.get('file_size', 0)
                
                if actual_size != expected_size:
                    self.log(f"⚠️ Taille fichier incorrecte {table_name}: {actual_size} != {expected_size}", 'WARNING')
                
                # Vérifier que le JSON est valide
                try:
                    with open(table_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    actual_count = len(data)
                    expected_count = table_info.get('record_count', 0)
                    
                    if actual_count != expected_count:
                        self.log(f"⚠️ Nombre d'enregistrements incorrect {table_name}: {actual_count} != {expected_count}", 'WARNING')
                
                except json.JSONDecodeError as e:
                    self.log(f"❌ JSON invalide {table_name}: {e}", 'ERROR')
                    return False
            
            self.log(f"✅ Backup vérifié: {backup_name}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur vérification: {e}", 'ERROR')
            return False


def main():
    """Point d'entrée principal"""
    parser = argparse.ArgumentParser(
        description='Gestionnaire de backup/restore US1.6',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')
    
    # Commande backup
    backup_parser = subparsers.add_parser('backup', help='Créer un backup')
    backup_parser.add_argument('--name', help='Nom personnalisé du backup')
    
    # Commande restore
    restore_parser = subparsers.add_parser('restore', help='Restaurer depuis un backup')
    restore_parser.add_argument('--backup-name', required=True, help='Nom du backup à restaurer')
    restore_parser.add_argument('--confirm', action='store_true', help='Confirmer la restauration')
    
    # Commande list-backups
    list_parser = subparsers.add_parser('list-backups', help='Lister les backups')
    
    # Commande cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Nettoyer les anciens backups')
    cleanup_parser.add_argument('--older-than', type=int, default=30,
                               help='Supprimer les backups plus anciens que X jours (défaut: 30)')
    
    # Commande verify
    verify_parser = subparsers.add_parser('verify', help='Vérifier l\'intégrité d\'un backup')
    verify_parser.add_argument('--backup-name', required=True, help='Nom du backup à vérifier')
    
    # Options globales
    parser.add_argument('--config', default='development',
                       choices=['development', 'testing', 'production'],
                       help='Configuration à utiliser')
    parser.add_argument('--verbose', action='store_true', help='Affichage détaillé')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialiser le gestionnaire
    manager = US16BackupManager(
        config_name=args.config,
        verbose=args.verbose
    )
    
    try:
        if args.command == 'backup':
            success, backup_path, metadata = manager.create_full_backup(args.name)
            sys.exit(0 if success else 1)
        
        elif args.command == 'restore':
            success = manager.restore_from_backup(args.backup_name, args.confirm)
            sys.exit(0 if success else 1)
        
        elif args.command == 'list-backups':
            backups = manager.list_backups()
            
            if not backups:
                print("Aucun backup trouvé")
                sys.exit(0)
            
            print(f"{'Nom':<30} {'Date':<20} {'Taille (MB)':<12} {'Enregistrements':<15} {'Status'}")
            print("-" * 85)
            
            for backup in backups:
                name = backup.get('backup_name', 'Unknown')[:28]
                date = backup.get('created_at', 'Unknown')[:19].replace('T', ' ')
                size = backup.get('size_mb', 0)
                records = backup.get('total_records', 0)
                status = backup.get('status', 'OK')
                
                print(f"{name:<30} {date:<20} {size:<12} {records:<15} {status}")
            
            sys.exit(0)
        
        elif args.command == 'cleanup':
            deleted = manager.cleanup_old_backups(args.older_than)
            sys.exit(0)
        
        elif args.command == 'verify':
            success = manager.verify_backup_integrity(args.backup_name)
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        manager.log("⏹️ Opération interrompue par l'utilisateur", 'WARNING')
        sys.exit(1)
    except Exception as e:
        manager.log(f"💥 Erreur inattendue: {e}", 'ERROR')
        sys.exit(1)


if __name__ == '__main__':
    main()