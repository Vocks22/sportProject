"""Migration US1.6: Semaines Lundi-Dimanche (ISO 8601)

Revision ID: 004
Revises: 003
Create Date: 2025-08-07

Cette migration convertit la logique de semaine vers le standard ISO 8601 (lundi-dimanche)
et met à jour toutes les dates week_start existantes pour qu'elles correspondent au lundi de chaque semaine.

ATTENTION: Cette migration modifie les données existantes de manière irréversible.
Un backup complet est recommandé avant l'exécution.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime, date, timedelta


# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_monday_of_week(input_date: date) -> date:
    """
    Calcule le lundi de la semaine pour une date donnée (ISO 8601)
    
    Args:
        input_date: Date dont on veut le lundi de la semaine
        
    Returns:
        Date du lundi de la semaine (ISO 8601)
    """
    # weekday(): 0=lundi, 1=mardi, ..., 6=dimanche
    days_since_monday = input_date.weekday()
    monday_date = input_date - timedelta(days=days_since_monday)
    return monday_date


def upgrade() -> None:
    """Migration vers semaines ISO 8601 (lundi-dimanche)"""
    
    print("🔄 Début de la migration US1.6: Semaines Lundi-Dimanche (ISO 8601)")
    
    # Créer une connexion pour manipuler les données
    connection = op.get_bind()
    
    # 1. Sauvegarder les données actuelles dans une table temporaire
    print("📦 Création des tables de backup...")
    
    # Backup meal_plans
    op.execute("""
        CREATE TABLE IF NOT EXISTS meal_plans_backup_pre_us16 AS 
        SELECT * FROM meal_plans
    """)
    
    # Backup shopping_lists
    op.execute("""
        CREATE TABLE IF NOT EXISTS shopping_lists_backup_pre_us16 AS 
        SELECT * FROM shopping_lists
    """)
    
    print("✅ Tables de backup créées")
    
    # 2. Mettre à jour les meal_plans
    print("🔄 Conversion des dates week_start dans meal_plans...")
    
    # Récupérer tous les meal_plans existants
    meal_plans_result = connection.execute(sa.text(
        "SELECT id, week_start FROM meal_plans"
    ))
    
    meal_plans_updates = []
    for row in meal_plans_result:
        meal_plan_id = row[0]
        current_week_start = datetime.fromisoformat(row[1]).date()
        
        # Calculer le nouveau week_start (lundi de la semaine)
        new_week_start = get_monday_of_week(current_week_start)
        
        meal_plans_updates.append({
            'id': meal_plan_id,
            'old_date': current_week_start,
            'new_date': new_week_start
        })
    
    # Appliquer les mises à jour
    for update in meal_plans_updates:
        connection.execute(
            sa.text("UPDATE meal_plans SET week_start = :new_date WHERE id = :id"),
            {'new_date': update['new_date'].isoformat(), 'id': update['id']}
        )
        print(f"  📅 Meal Plan {update['id']}: {update['old_date']} → {update['new_date']}")
    
    # 3. Mettre à jour les shopping_lists
    print("🔄 Conversion des dates week_start dans shopping_lists...")
    
    shopping_lists_result = connection.execute(sa.text(
        "SELECT id, week_start FROM shopping_lists"
    ))
    
    shopping_lists_updates = []
    for row in shopping_lists_result:
        shopping_list_id = row[0]
        current_week_start = datetime.fromisoformat(row[1]).date()
        
        # Calculer le nouveau week_start (lundi de la semaine)
        new_week_start = get_monday_of_week(current_week_start)
        
        shopping_lists_updates.append({
            'id': shopping_list_id,
            'old_date': current_week_start,
            'new_date': new_week_start
        })
    
    # Appliquer les mises à jour
    for update in shopping_lists_updates:
        connection.execute(
            sa.text("UPDATE shopping_lists SET week_start = :new_date WHERE id = :id"),
            {'new_date': update['new_date'].isoformat(), 'id': update['id']}
        )
        print(f"  🛒 Shopping List {update['id']}: {update['old_date']} → {update['new_date']}")
    
    # 4. Ajouter des contraintes et commentaires
    print("📝 Ajout des contraintes ISO 8601...")
    
    # Ajouter un trigger pour vérifier que week_start est bien un lundi
    # Note: SQLite ne supporte pas les fonctions personnalisées complexes,
    # la validation sera donc faite au niveau application
    
    # 5. Mettre à jour les métadonnées de migration
    op.execute(f"""
        INSERT OR REPLACE INTO alembic_version (version_num) VALUES ('{revision}')
    """)
    
    # 6. Statistiques de migration
    meal_plan_count = connection.execute(sa.text("SELECT COUNT(*) FROM meal_plans")).scalar()
    shopping_list_count = connection.execute(sa.text("SELECT COUNT(*) FROM shopping_lists")).scalar()
    
    print(f"✅ Migration US1.6 terminée avec succès!")
    print(f"   📊 {meal_plan_count} meal_plans mis à jour")
    print(f"   📊 {shopping_list_count} shopping_lists mis à jour")
    print(f"   🔒 Tables de backup créées: meal_plans_backup_pre_us16, shopping_lists_backup_pre_us16")


def downgrade() -> None:
    """Rollback de la migration US1.6"""
    
    print("⏪ Début du rollback US1.6: Restauration des données pré-ISO 8601")
    
    connection = op.get_bind()
    
    # Vérifier que les tables de backup existent
    backup_tables = connection.execute(sa.text("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND (name='meal_plans_backup_pre_us16' OR name='shopping_lists_backup_pre_us16')
    """)).fetchall()
    
    if len(backup_tables) != 2:
        raise Exception("⚠️ Tables de backup introuvables. Rollback impossible sans risque de perte de données.")
    
    # Restaurer meal_plans
    print("🔄 Restauration des meal_plans...")
    op.execute("DELETE FROM meal_plans")
    op.execute("""
        INSERT INTO meal_plans 
        SELECT * FROM meal_plans_backup_pre_us16
    """)
    
    # Restaurer shopping_lists  
    print("🔄 Restauration des shopping_lists...")
    op.execute("DELETE FROM shopping_lists")
    op.execute("""
        INSERT INTO shopping_lists 
        SELECT * FROM shopping_lists_backup_pre_us16
    """)
    
    # Supprimer les tables de backup
    print("🗑️ Nettoyage des tables de backup...")
    op.execute("DROP TABLE IF EXISTS meal_plans_backup_pre_us16")
    op.execute("DROP TABLE IF EXISTS shopping_lists_backup_pre_us16")
    
    # Statistiques de rollback
    meal_plan_count = connection.execute(sa.text("SELECT COUNT(*) FROM meal_plans")).scalar()
    shopping_list_count = connection.execute(sa.text("SELECT COUNT(*) FROM shopping_lists")).scalar()
    
    print(f"✅ Rollback US1.6 terminé avec succès!")
    print(f"   📊 {meal_plan_count} meal_plans restaurés")
    print(f"   📊 {shopping_list_count} shopping_lists restaurés")


# Fonctions utilitaires pour les tests
def validate_iso8601_week_start(connection, table_name: str) -> bool:
    """Valide que toutes les dates week_start sont bien des lundis"""
    
    result = connection.execute(sa.text(f"""
        SELECT id, week_start FROM {table_name}
    """))
    
    invalid_dates = []
    for row in result:
        week_start = datetime.fromisoformat(row[1]).date()
        if week_start.weekday() != 0:  # 0 = lundi
            invalid_dates.append((row[0], week_start))
    
    if invalid_dates:
        print(f"⚠️ Dates week_start invalides trouvées dans {table_name}:")
        for record_id, invalid_date in invalid_dates:
            weekday_name = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][invalid_date.weekday()]
            print(f"   ID {record_id}: {invalid_date} ({weekday_name})")
        return False
    
    return True


if __name__ == "__main__":
    # Test des fonctions utilitaires
    test_dates = [
        date(2025, 8, 6),   # Mercredi
        date(2025, 8, 7),   # Jeudi  
        date(2025, 8, 10),  # Dimanche
        date(2025, 8, 5),   # Mardi
    ]
    
    print("🧪 Tests des fonctions utilitaires:")
    for test_date in test_dates:
        monday = get_monday_of_week(test_date)
        weekday_name = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'][test_date.weekday()]
        print(f"   {test_date} ({weekday_name}) → lundi {monday}")