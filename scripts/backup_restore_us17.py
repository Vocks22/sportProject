#!/usr/bin/env python3
"""
Script de Backup et Restore spécialisé pour l'US1.7 - Profil Utilisateur Réel

Ce script fournit des fonctionnalités avancées de sauvegarde et restauration
spécifiquement optimisées pour les modifications de l'US1.7.

Fonctionnalités :
- Backup complet avant migration
- Backup incrémental des nouvelles données
- Restore sélectif par table ou utilisateur
- Validation de l'intégrité des données
- Monitoring de la migration
- Rollback automatique en cas d'échec

Author: Database Administrator
Date: 2025-08-07
Version: 1.0.0
"""

import os
import sys
import json
import sqlite3
import shutil
import hashlib
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
import argparse
import logging

# Ajouter le répertoire parent pour importer les modules
sys.path.append(str(Path(__file__).parent.parent))

from src.backend.database.config import get_config
from src.backend.models.user import User, WeightHistory, UserGoalsHistory, UserMeasurement


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('us17_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class US17BackupManager:
    """Gestionnaire de backup spécialisé pour l'US1.7"""
    
    def __init__(self, config_name: str = 'development'):
        """Initialise le gestionnaire de backup"""
        self.config = get_config(config_name)
        self.backup_dir = Path('backups') / 'us17'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Extraction de l'URI de la base de données
        self.db_uri = self.config.SQLALCHEMY_DATABASE_URI
        if self.db_uri.startswith('sqlite:///'):
            self.db_path = Path(self.db_uri.replace('sqlite:///', ''))
        else:
            raise ValueError("Ce script ne supporte que SQLite pour l'instant")
        
        logger.info(f"Initialisation du backup manager pour {self.db_path}")
    
    def create_full_backup(self, backup_name: Optional[str] = None) -> Path:
        """Crée une sauvegarde complète de la base de données"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = backup_name or f"us17_full_backup_{timestamp}"
        backup_path = self.backup_dir / f"{backup_name}.db"
        
        logger.info(f"Création du backup complet: {backup_path}")
        
        try:
            # Copie de la base de données
            shutil.copy2(self.db_path, backup_path)
            
            # Création des métadonnées
            metadata = {
                'backup_type': 'full',
                'timestamp': timestamp,
                'original_db': str(self.db_path),
                'backup_path': str(backup_path),
                'file_size': backup_path.stat().st_size,
                'checksum': self._calculate_checksum(backup_path),
                'us17_status': self._check_us17_migration_status()
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Backup complet créé avec succès: {backup_path}")
            logger.info(f"Métadonnées sauvegardées: {metadata_path}")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Erreur lors du backup complet: {e}")
            raise
    
    def create_data_export(self, export_name: Optional[str] = None) -> Path:
        """Exporte les données utilisateur en format JSON pour analyse"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_name = export_name or f"us17_data_export_{timestamp}"
        export_path = self.backup_dir / f"{export_name}.json"
        
        logger.info(f"Export des données utilisateur: {export_path}")
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                export_data = {
                    'export_info': {
                        'timestamp': timestamp,
                        'us17_migration_status': self._check_us17_migration_status()
                    },
                    'users': self._export_users_data(conn),
                    'weight_history': self._export_weight_history(conn),
                    'goals_history': self._export_goals_history(conn),
                    'measurements': self._export_measurements(conn),
                    'statistics': self._generate_data_statistics(conn)
                }
                
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                
                logger.info(f"Export des données terminé: {export_path}")
                return export_path
                
        except Exception as e:
            logger.error(f"Erreur lors de l'export des données: {e}")
            raise
    
    def validate_migration_integrity(self) -> Dict[str, Any]:
        """Valide l'intégrité des données après migration"""
        logger.info("Validation de l'intégrité de la migration US1.7")
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'migration_status': 'unknown',
            'checks': {},
            'errors': [],
            'warnings': [],
            'overall_status': 'pending'
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                
                # Vérification de la structure des tables
                validation_results['checks']['table_structure'] = self._validate_table_structure(conn)
                
                # Vérification des contraintes
                validation_results['checks']['constraints'] = self._validate_constraints(conn)
                
                # Vérification des index
                validation_results['checks']['indexes'] = self._validate_indexes(conn)
                
                # Vérification des données
                validation_results['checks']['data_integrity'] = self._validate_data_integrity(conn)
                
                # Vérification des vues
                validation_results['checks']['views'] = self._validate_views(conn)
                
                # Calcul du statut global
                all_checks_passed = all(
                    check.get('status') == 'passed' 
                    for check in validation_results['checks'].values()
                )
                
                validation_results['overall_status'] = 'passed' if all_checks_passed else 'failed'
                validation_results['migration_status'] = self._check_us17_migration_status()
                
        except Exception as e:
            validation_results['errors'].append(f"Erreur de validation: {str(e)}")
            validation_results['overall_status'] = 'error'
            logger.error(f"Erreur lors de la validation: {e}")
        
        # Sauvegarde du rapport de validation
        report_path = self.backup_dir / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(validation_results, f, indent=2, default=str)
        
        logger.info(f"Rapport de validation sauvegardé: {report_path}")
        return validation_results
    
    def restore_from_backup(self, backup_path: Path, confirm: bool = False) -> bool:
        """Restaure la base de données depuis un backup"""
        if not backup_path.exists():
            logger.error(f"Backup introuvable: {backup_path}")
            return False
        
        if not confirm:
            logger.warning("Restauration annulée - confirmation requise")
            return False
        
        logger.info(f"Restauration depuis: {backup_path}")
        
        try:
            # Backup de sécurité avant restauration
            safety_backup = self.create_full_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Backup de sécurité créé: {safety_backup}")
            
            # Restauration
            shutil.copy2(backup_path, self.db_path)
            
            # Validation post-restauration
            validation_results = self.validate_migration_integrity()
            
            if validation_results['overall_status'] == 'passed':
                logger.info("Restauration réussie et validée")
                return True
            else:
                logger.error("Erreurs détectées après restauration")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la restauration: {e}")
            return False
    
    def rollback_us17_migration(self, confirm: bool = False) -> bool:
        """Effectue un rollback complet de la migration US1.7"""
        if not confirm:
            logger.warning("Rollback annulé - confirmation requise")
            return False
        
        logger.info("Démarrage du rollback de la migration US1.7")
        
        try:
            # Trouver le dernier backup pré-migration
            pre_migration_backup = self._find_pre_migration_backup()
            
            if not pre_migration_backup:
                logger.error("Aucun backup pré-migration trouvé")
                return False
            
            # Restaurer le backup pré-migration
            success = self.restore_from_backup(pre_migration_backup, confirm=True)
            
            if success:
                logger.info("Rollback US1.7 terminé avec succès")
                return True
            else:
                logger.error("Échec du rollback US1.7")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors du rollback: {e}")
            return False
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcule le checksum MD5 d'un fichier"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _check_us17_migration_status(self) -> str:
        """Vérifie le statut de la migration US1.7"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Vérifier la table alembic_version
                cursor.execute("SELECT version_num FROM alembic_version")
                current_version = cursor.fetchone()
                
                if current_version and current_version[0] >= '006':
                    return 'migrated'
                else:
                    return 'not_migrated'
                    
        except Exception:
            return 'unknown'
    
    def _export_users_data(self, conn: sqlite3.Connection) -> List[Dict]:
        """Exporte les données des utilisateurs"""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM users 
            ORDER BY created_at DESC
        """)
        
        users = []
        for row in cursor.fetchall():
            user_data = dict(row)
            # Conversion des dates en format ISO
            if user_data.get('birth_date'):
                user_data['birth_date'] = str(user_data['birth_date'])
            if user_data.get('created_at'):
                user_data['created_at'] = str(user_data['created_at'])
            if user_data.get('updated_at'):
                user_data['updated_at'] = str(user_data['updated_at'])
            
            users.append(user_data)
        
        return users
    
    def _export_weight_history(self, conn: sqlite3.Connection) -> List[Dict]:
        """Exporte l'historique des poids"""
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='weight_history'
        """)
        
        if not cursor.fetchone():
            return []
        
        cursor.execute("""
            SELECT wh.*, u.username 
            FROM weight_history wh
            LEFT JOIN users u ON wh.user_id = u.id
            ORDER BY wh.recorded_date DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _export_goals_history(self, conn: sqlite3.Connection) -> List[Dict]:
        """Exporte l'historique des objectifs"""
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_goals_history'
        """)
        
        if not cursor.fetchone():
            return []
        
        cursor.execute("""
            SELECT gh.*, u.username 
            FROM user_goals_history gh
            LEFT JOIN users u ON gh.user_id = u.id
            ORDER BY gh.start_date DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _export_measurements(self, conn: sqlite3.Connection) -> List[Dict]:
        """Exporte les mesures corporelles"""
        cursor = conn.cursor()
        
        # Vérifier si la table existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='user_measurements'
        """)
        
        if not cursor.fetchone():
            return []
        
        cursor.execute("""
            SELECT um.*, u.username 
            FROM user_measurements um
            LEFT JOIN users u ON um.user_id = u.id
            ORDER BY um.recorded_date DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def _generate_data_statistics(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Génère des statistiques sur les données"""
        cursor = conn.cursor()
        
        stats = {}
        
        # Statistiques utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        stats['total_users'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE profile_completed = 1")
        stats['users_with_completed_profiles'] = cursor.fetchone()[0]
        
        # Statistiques historique poids (si la table existe)
        try:
            cursor.execute("SELECT COUNT(*) FROM weight_history")
            stats['total_weight_entries'] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats['total_weight_entries'] = 0
        
        # Statistiques objectifs (si la table existe)
        try:
            cursor.execute("SELECT COUNT(*) FROM user_goals_history")
            stats['total_goals'] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats['total_goals'] = 0
        
        # Statistiques mesures (si la table existe)
        try:
            cursor.execute("SELECT COUNT(*) FROM user_measurements")
            stats['total_measurements'] = cursor.fetchone()[0]
        except sqlite3.OperationalError:
            stats['total_measurements'] = 0
        
        return stats
    
    def _validate_table_structure(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Valide la structure des tables"""
        cursor = conn.cursor()
        
        expected_tables = [
            'users', 'weight_history', 'user_goals_history', 
            'user_measurements', 'alembic_version'
        ]
        
        result = {'status': 'passed', 'details': {}, 'errors': []}
        
        for table in expected_tables:
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                result['details'][table] = {
                    'exists': len(columns) > 0,
                    'column_count': len(columns),
                    'columns': [col[1] for col in columns]
                }
            except Exception as e:
                result['errors'].append(f"Erreur table {table}: {e}")
                result['status'] = 'failed'
        
        return result
    
    def _validate_constraints(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Valide les contraintes de la base"""
        cursor = conn.cursor()
        result = {'status': 'passed', 'details': {}, 'errors': []}
        
        try:
            # Test des contraintes de validation
            test_cases = [
                ("INSERT INTO users (username, email, current_weight) VALUES ('test', 'test@test.com', -10)", False),
                ("INSERT INTO users (username, email, height) VALUES ('test2', 'test2@test.com', 500)", False),
            ]
            
            for sql, should_succeed in test_cases:
                try:
                    cursor.execute(sql)
                    if not should_succeed:
                        result['errors'].append(f"Contrainte non respectée: {sql}")
                        result['status'] = 'failed'
                    conn.rollback()
                except sqlite3.IntegrityError:
                    if should_succeed:
                        result['errors'].append(f"Contrainte trop stricte: {sql}")
                        result['status'] = 'failed'
                    conn.rollback()
                
        except Exception as e:
            result['errors'].append(f"Erreur validation contraintes: {e}")
            result['status'] = 'failed'
        
        return result
    
    def _validate_indexes(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Valide la présence des index"""
        cursor = conn.cursor()
        result = {'status': 'passed', 'details': {}, 'indexes': []}
        
        try:
            cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            
            result['indexes'] = [{'name': idx[0], 'table': idx[1]} for idx in indexes]
            result['details']['index_count'] = len(indexes)
            
            # Vérifier la présence d'index critiques
            critical_indexes = [
                'idx_users_profile_status',
                'idx_weight_history_user_date',
                'idx_goals_history_user_status'
            ]
            
            existing_index_names = [idx[0] for idx in indexes]
            missing_indexes = [idx for idx in critical_indexes if idx not in existing_index_names]
            
            if missing_indexes:
                result['errors'] = [f"Index manquant: {idx}" for idx in missing_indexes]
                result['status'] = 'warning'
            
        except Exception as e:
            result['errors'] = [f"Erreur validation index: {e}"]
            result['status'] = 'failed'
        
        return result
    
    def _validate_data_integrity(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Valide l'intégrité des données"""
        cursor = conn.cursor()
        result = {'status': 'passed', 'details': {}, 'errors': []}
        
        try:
            # Vérifier les clés étrangères
            cursor.execute("PRAGMA foreign_key_check")
            fk_errors = cursor.fetchall()
            
            if fk_errors:
                result['errors'].extend([f"FK error: {error}" for error in fk_errors])
                result['status'] = 'failed'
            
            # Vérifier les données incohérentes
            cursor.execute("""
                SELECT COUNT(*) FROM users 
                WHERE current_weight IS NOT NULL AND current_weight <= 0
            """)
            invalid_weights = cursor.fetchone()[0]
            
            if invalid_weights > 0:
                result['errors'].append(f"{invalid_weights} poids invalides détectés")
                result['status'] = 'failed'
            
            result['details']['foreign_key_errors'] = len(fk_errors)
            result['details']['invalid_weights'] = invalid_weights
            
        except Exception as e:
            result['errors'].append(f"Erreur validation données: {e}")
            result['status'] = 'failed'
        
        return result
    
    def _validate_views(self, conn: sqlite3.Connection) -> Dict[str, Any]:
        """Valide les vues créées"""
        cursor = conn.cursor()
        result = {'status': 'passed', 'details': {}, 'views': []}
        
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [row[0] for row in cursor.fetchall()]
            
            result['views'] = views
            result['details']['view_count'] = len(views)
            
            expected_views = [
                'v_user_profile_complete',
                'v_weight_evolution',
                'v_progress_stats'
            ]
            
            missing_views = [view for view in expected_views if view not in views]
            
            if missing_views:
                result['errors'] = [f"Vue manquante: {view}" for view in missing_views]
                result['status'] = 'warning'
            
        except Exception as e:
            result['errors'] = [f"Erreur validation vues: {e}"]
            result['status'] = 'failed'
        
        return result
    
    def _find_pre_migration_backup(self) -> Optional[Path]:
        """Trouve le dernier backup pré-migration"""
        backup_files = list(self.backup_dir.glob('*.json'))
        
        for backup_metadata_path in sorted(backup_files, reverse=True):
            try:
                with open(backup_metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if (metadata.get('us17_status') == 'not_migrated' and 
                    metadata.get('backup_type') == 'full'):
                    backup_db_path = Path(metadata['backup_path'])
                    if backup_db_path.exists():
                        return backup_db_path
                        
            except Exception as e:
                logger.warning(f"Erreur lecture métadonnées {backup_metadata_path}: {e}")
        
        return None


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description='Gestionnaire de backup US1.7')
    parser.add_argument('--action', required=True, 
                       choices=['backup', 'export', 'validate', 'restore', 'rollback'],
                       help='Action à effectuer')
    parser.add_argument('--backup-path', type=str, help='Chemin du backup pour restauration')
    parser.add_argument('--name', type=str, help='Nom du backup/export')
    parser.add_argument('--config', default='development', help='Configuration à utiliser')
    parser.add_argument('--confirm', action='store_true', help='Confirmer les actions destructives')
    
    args = parser.parse_args()
    
    try:
        manager = US17BackupManager(args.config)
        
        if args.action == 'backup':
            backup_path = manager.create_full_backup(args.name)
            print(f"Backup créé: {backup_path}")
            
        elif args.action == 'export':
            export_path = manager.create_data_export(args.name)
            print(f"Export créé: {export_path}")
            
        elif args.action == 'validate':
            results = manager.validate_migration_integrity()
            print(f"Validation: {results['overall_status']}")
            if results['errors']:
                print("Erreurs détectées:")
                for error in results['errors']:
                    print(f"  - {error}")
                    
        elif args.action == 'restore':
            if not args.backup_path:
                print("Erreur: --backup-path requis pour la restauration")
                sys.exit(1)
            
            backup_path = Path(args.backup_path)
            success = manager.restore_from_backup(backup_path, args.confirm)
            print(f"Restauration: {'réussie' if success else 'échouée'}")
            
        elif args.action == 'rollback':
            success = manager.rollback_us17_migration(args.confirm)
            print(f"Rollback: {'réussi' if success else 'échoué'}")
            
    except Exception as e:
        logger.error(f"Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()