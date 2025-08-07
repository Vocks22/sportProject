"""Optimisation des index pour semaines ISO 8601

Revision ID: 005
Revises: 004
Create Date: 2025-08-07

Cette migration optimise les index de performance pour les requêtes hebdomadaires
après la migration vers ISO 8601. Elle ajoute des index composites spécialisés
pour améliorer les performances des requêtes fréquentes.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Optimisation des index pour les performances ISO 8601"""
    
    print("🚀 Optimisation des index pour semaines ISO 8601...")
    
    # 1. Index composites pour meal_plans
    print("📋 Création d'index optimisés pour meal_plans...")
    
    # Index pour recherche par utilisateur et semaine (requête la plus fréquente)
    op.create_index(
        'idx_meal_plans_user_week_composite', 
        'meal_plans', 
        ['user_id', 'week_start'],
        postgresql_concurrently=True if op.get_bind().dialect.name == 'postgresql' else None
    )
    
    # Index pour recherche par semaine et statut actif
    op.create_index(
        'idx_meal_plans_week_active', 
        'meal_plans', 
        ['week_start', 'is_active']
    )
    
    # Index partiel pour meal_plans actifs seulement (optimisation PostgreSQL/SQLite)
    if op.get_bind().dialect.name in ['postgresql', 'sqlite']:
        op.create_index(
            'idx_meal_plans_active_only',
            'meal_plans',
            ['user_id', 'week_start'],
            postgresql_where=sa.text('is_active = true') if op.get_bind().dialect.name == 'postgresql' else None,
            sqlite_where='is_active = 1' if op.get_bind().dialect.name == 'sqlite' else None
        )
    
    # 2. Index composites pour shopping_lists
    print("🛒 Création d'index optimisés pour shopping_lists...")
    
    # Index pour recherche par meal_plan et semaine
    op.create_index(
        'idx_shopping_lists_meal_plan_week', 
        'shopping_lists', 
        ['meal_plan_id', 'week_start']
    )
    
    # Index pour recherche par semaine et statut de completion
    op.create_index(
        'idx_shopping_lists_week_status', 
        'shopping_lists', 
        ['week_start', 'is_completed']
    )
    
    # Index pour les listes non terminées (requête fréquente)
    op.create_index(
        'idx_shopping_lists_incomplete', 
        'shopping_lists', 
        ['week_start', 'last_updated'],
        postgresql_where=sa.text('is_completed = false') if op.get_bind().dialect.name == 'postgresql' else None,
        sqlite_where='is_completed = 0' if op.get_bind().dialect.name == 'sqlite' else None
    )
    
    # 3. Index pour shopping_list_history (traçabilité)
    print("📝 Création d'index pour shopping_list_history...")
    
    # Index pour recherche par liste et timestamp (historique chronologique)
    op.create_index(
        'idx_shopping_history_list_time', 
        'shopping_list_history', 
        ['shopping_list_id', 'timestamp']
    )
    
    # Index pour recherche par action et timestamp (analytics)
    op.create_index(
        'idx_shopping_history_action_time', 
        'shopping_list_history', 
        ['action', 'timestamp']
    )
    
    # 4. Index pour store_categories
    print("🏪 Création d'index pour store_categories...")
    
    # Index pour recherche par utilisateur et activation
    op.create_index(
        'idx_store_categories_user_active', 
        'store_categories', 
        ['user_id', 'is_active', 'sort_order']
    )
    
    # 5. Index sur les colonnes de dates pour requêtes de plage
    print("📅 Création d'index pour requêtes de plage de dates...")
    
    # Index pour requêtes de plage sur meal_plans
    op.create_index(
        'idx_meal_plans_date_range', 
        'meal_plans', 
        ['week_start', 'created_at']
    )
    
    # Index pour requêtes de plage sur shopping_lists
    op.create_index(
        'idx_shopping_lists_date_range', 
        'shopping_lists', 
        ['week_start', 'generated_date']
    )
    
    # 6. Statistiques et analyse des performances
    print("📊 Mise à jour des statistiques de la base de données...")
    
    # Mettre à jour les statistiques pour PostgreSQL
    if op.get_bind().dialect.name == 'postgresql':
        op.execute("ANALYZE meal_plans")
        op.execute("ANALYZE shopping_lists") 
        op.execute("ANALYZE shopping_list_history")
        op.execute("ANALYZE store_categories")
    
    # Optimiser pour SQLite
    elif op.get_bind().dialect.name == 'sqlite':
        op.execute("ANALYZE")
    
    print("✅ Optimisation des index terminée")
    print("""
📈 Index créés pour optimiser les requêtes suivantes:
  • Recherche meal_plans par utilisateur et semaine
  • Filtrage meal_plans actifs
  • Recherche shopping_lists par meal_plan et semaine  
  • Filtrage shopping_lists incomplètes
  • Historique chronologique des modifications
  • Catégories de magasin par utilisateur
  • Requêtes de plage de dates
    """)


def downgrade() -> None:
    """Suppression des index d'optimisation"""
    
    print("⏪ Suppression des index d'optimisation ISO 8601...")
    
    # Supprimer tous les index créés dans upgrade()
    indexes_to_drop = [
        'idx_meal_plans_user_week_composite',
        'idx_meal_plans_week_active', 
        'idx_meal_plans_active_only',
        'idx_shopping_lists_meal_plan_week',
        'idx_shopping_lists_week_status',
        'idx_shopping_lists_incomplete',
        'idx_shopping_history_list_time',
        'idx_shopping_history_action_time', 
        'idx_store_categories_user_active',
        'idx_meal_plans_date_range',
        'idx_shopping_lists_date_range'
    ]
    
    for index_name in indexes_to_drop:
        try:
            # Déterminer la table depuis le nom de l'index
            if 'meal_plans' in index_name:
                table_name = 'meal_plans'
            elif 'shopping_lists' in index_name:
                table_name = 'shopping_lists' 
            elif 'shopping_history' in index_name:
                table_name = 'shopping_list_history'
            elif 'store_categories' in index_name:
                table_name = 'store_categories'
            else:
                continue
                
            op.drop_index(index_name, table_name)
            print(f"  🗑️ Index supprimé: {index_name}")
            
        except Exception as e:
            print(f"  ⚠️ Erreur suppression {index_name}: {e}")
    
    print("✅ Suppression des index terminée")


# Fonctions utilitaires pour l'analyse des performances

def analyze_query_performance():
    """
    Analyse les performances des requêtes principales après optimisation
    Cette fonction peut être appelée manuellement pour le monitoring
    """
    
    common_queries = {
        "meal_plans_by_user_week": """
            SELECT * FROM meal_plans 
            WHERE user_id = ? AND week_start = ?
        """,
        
        "active_meal_plans": """
            SELECT * FROM meal_plans 
            WHERE user_id = ? AND is_active = true
            ORDER BY week_start DESC
        """,
        
        "shopping_lists_by_week": """
            SELECT sl.*, mp.user_id 
            FROM shopping_lists sl
            JOIN meal_plans mp ON sl.meal_plan_id = mp.id
            WHERE sl.week_start = ?
        """,
        
        "incomplete_shopping_lists": """
            SELECT * FROM shopping_lists 
            WHERE is_completed = false 
            ORDER BY week_start DESC, last_updated DESC
        """,
        
        "week_range_meal_plans": """
            SELECT * FROM meal_plans 
            WHERE week_start BETWEEN ? AND ?
            AND user_id = ?
        """
    }
    
    return common_queries


def get_index_usage_stats():
    """
    Retourne des statistiques d'utilisation des index
    Utile pour le monitoring et l'optimisation continue
    """
    
    # Pour PostgreSQL
    postgresql_stats_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes 
        WHERE tablename IN ('meal_plans', 'shopping_lists', 'shopping_list_history', 'store_categories')
        ORDER BY idx_tup_read DESC;
    """
    
    # Pour SQLite (plus limité)
    sqlite_stats_query = """
        SELECT name, sql FROM sqlite_master 
        WHERE type='index' 
        AND tbl_name IN ('meal_plans', 'shopping_lists', 'shopping_list_history', 'store_categories')
        ORDER BY name;
    """
    
    return {
        'postgresql': postgresql_stats_query,
        'sqlite': sqlite_stats_query
    }


if __name__ == "__main__":
    print("🧪 Test des requêtes d'optimisation:")
    
    queries = analyze_query_performance()
    for name, query in queries.items():
        print(f"  📋 {name}")
        print(f"     {query.strip()}")
        print()
    
    print("📊 Statistiques d'index disponibles:")
    stats = get_index_usage_stats()
    for db_type, query in stats.items():
        print(f"  🔍 {db_type.upper()}:")
        print(f"     {query.strip()}")
        print()