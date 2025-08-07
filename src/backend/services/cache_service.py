"""
Service de cache Redis pour l'optimisation des performances (US1.5)
Gère la mise en cache des agrégations et des listes de courses
"""

import redis
import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from functools import wraps
import pickle

class CacheService:
    """Service de cache Redis avec stratégies d'invalidation intelligentes"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialise la connexion Redis
        
        Args:
            redis_url: URL de connexion Redis
        """
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=False,  # Pour supporter les objets pickle
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test de connexion
            self.redis_client.ping()
            self.connected = True
        except (redis.RedisError, Exception) as e:
            print(f"Erreur de connexion Redis: {e}")
            self.redis_client = None
            self.connected = False
    
    # Durées de vie des caches (en secondes)
    TTL_SHOPPING_LIST = 3600       # 1 heure
    TTL_AGGREGATION = 1800         # 30 minutes  
    TTL_MEAL_PLAN_INGREDIENTS = 7200  # 2 heures
    TTL_RECIPE_DATA = 86400        # 24 heures
    TTL_USER_PREFERENCES = 3600    # 1 heure
    
    # Préfixes pour les clés
    PREFIX_SHOPPING_LIST = "sl:"
    PREFIX_AGGREGATION = "agg:"
    PREFIX_MEAL_PLAN = "mp:"
    PREFIX_RECIPE = "recipe:"
    PREFIX_USER_PREF = "user_pref:"

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Génère une clé de cache unique basée sur les paramètres
        
        Args:
            prefix: Préfixe de la clé
            *args: Arguments positionnels
            **kwargs: Arguments nommés
        
        Returns:
            str: Clé de cache unique
        """
        # Créer une représentation hashable des arguments
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items()) if kwargs else {}
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()[:16]
        
        return f"{prefix}{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """
        Récupère une valeur depuis le cache
        
        Args:
            key: Clé de cache
        
        Returns:
            Optional[Any]: Valeur cachée ou None
        """
        if not self.connected:
            return None
        
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return pickle.loads(cached_data)
        except (redis.RedisError, pickle.PickleError) as e:
            print(f"Erreur lecture cache {key}: {e}")
        
        return None

    def set(self, key: str, value: Any, ttl: int) -> bool:
        """
        Met en cache une valeur
        
        Args:
            key: Clé de cache
            value: Valeur à cacher
            ttl: Durée de vie en secondes
        
        Returns:
            bool: Succès de l'opération
        """
        if not self.connected:
            return False
        
        try:
            serialized_data = pickle.dumps(value)
            result = self.redis_client.setex(key, ttl, serialized_data)
            return bool(result)
        except (redis.RedisError, pickle.PickleError) as e:
            print(f"Erreur écriture cache {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        Supprime une entrée du cache
        
        Args:
            key: Clé à supprimer
        
        Returns:
            bool: Succès de l'opération
        """
        if not self.connected:
            return False
        
        try:
            result = self.redis_client.delete(key)
            return bool(result)
        except redis.RedisError as e:
            print(f"Erreur suppression cache {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Supprime toutes les entrées correspondant à un pattern
        
        Args:
            pattern: Pattern de clés (ex: "sl:*")
        
        Returns:
            int: Nombre d'entrées supprimées
        """
        if not self.connected:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            print(f"Erreur suppression pattern {pattern}: {e}")
            return 0

    def get_shopping_list_aggregation(
        self, 
        meal_plan_id: int, 
        preferences: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Récupère l'agrégation cachée d'une liste de courses
        
        Args:
            meal_plan_id: ID du plan de repas
            preferences: Préférences d'agrégation
        
        Returns:
            Optional[Dict]: Données d'agrégation ou None
        """
        cache_key = self._generate_cache_key(
            self.PREFIX_AGGREGATION,
            meal_plan_id,
            preferences=preferences
        )
        return self.get(cache_key)

    def cache_shopping_list_aggregation(
        self,
        meal_plan_id: int,
        aggregation_data: Dict,
        preferences: Optional[Dict] = None
    ) -> bool:
        """
        Met en cache l'agrégation d'une liste de courses
        
        Args:
            meal_plan_id: ID du plan de repas
            aggregation_data: Données d'agrégation
            preferences: Préférences d'agrégation
        
        Returns:
            bool: Succès de l'opération
        """
        cache_key = self._generate_cache_key(
            self.PREFIX_AGGREGATION,
            meal_plan_id,
            preferences=preferences
        )
        
        # Ajouter métadonnées de cache
        cached_data = {
            'data': aggregation_data,
            'cached_at': datetime.utcnow().isoformat(),
            'meal_plan_id': meal_plan_id,
            'preferences': preferences
        }
        
        return self.set(cache_key, cached_data, self.TTL_AGGREGATION)

    def get_meal_plan_ingredients(self, meal_plan_id: int) -> Optional[List[Dict]]:
        """
        Récupère les ingrédients cachés d'un plan de repas
        
        Args:
            meal_plan_id: ID du plan de repas
        
        Returns:
            Optional[List[Dict]]: Liste des ingrédients ou None
        """
        cache_key = self._generate_cache_key(
            self.PREFIX_MEAL_PLAN,
            meal_plan_id,
            type="ingredients"
        )
        return self.get(cache_key)

    def cache_meal_plan_ingredients(
        self,
        meal_plan_id: int,
        ingredients: List[Dict]
    ) -> bool:
        """
        Met en cache les ingrédients d'un plan de repas
        
        Args:
            meal_plan_id: ID du plan de repas
            ingredients: Liste des ingrédients
        
        Returns:
            bool: Succès de l'opération
        """
        cache_key = self._generate_cache_key(
            self.PREFIX_MEAL_PLAN,
            meal_plan_id,
            type="ingredients"
        )
        
        cached_data = {
            'ingredients': ingredients,
            'cached_at': datetime.utcnow().isoformat(),
            'meal_plan_id': meal_plan_id
        }
        
        return self.set(cache_key, cached_data, self.TTL_MEAL_PLAN_INGREDIENTS)

    def invalidate_shopping_list_caches(self, meal_plan_id: int) -> int:
        """
        Invalide tous les caches liés à un plan de repas
        
        Args:
            meal_plan_id: ID du plan de repas
        
        Returns:
            int: Nombre de caches invalidés
        """
        patterns_to_clear = [
            f"{self.PREFIX_SHOPPING_LIST}*{meal_plan_id}*",
            f"{self.PREFIX_AGGREGATION}*{meal_plan_id}*",
            f"{self.PREFIX_MEAL_PLAN}*{meal_plan_id}*"
        ]
        
        total_cleared = 0
        for pattern in patterns_to_clear:
            total_cleared += self.delete_pattern(pattern)
        
        return total_cleared

    def get_cache_statistics(self) -> Dict[str, Any]:
        """
        Récupère les statistiques du cache Redis
        
        Returns:
            Dict[str, Any]: Statistiques du cache
        """
        if not self.connected:
            return {'connected': False, 'error': 'Redis non connecté'}
        
        try:
            info = self.redis_client.info()
            
            # Compter les clés par préfixe
            key_counts = {}
            prefixes = [
                self.PREFIX_SHOPPING_LIST,
                self.PREFIX_AGGREGATION,
                self.PREFIX_MEAL_PLAN,
                self.PREFIX_RECIPE,
                self.PREFIX_USER_PREF
            ]
            
            for prefix in prefixes:
                keys = self.redis_client.keys(f"{prefix}*")
                key_counts[prefix.rstrip(':')] = len(keys)
            
            return {
                'connected': True,
                'total_keys': info.get('db0', {}).get('keys', 0),
                'used_memory': info.get('used_memory_human', '0B'),
                'hit_rate': info.get('keyspace_hit_rate', 0),
                'key_counts_by_type': key_counts,
                'uptime_seconds': info.get('uptime_in_seconds', 0)
            }
        except redis.RedisError as e:
            return {
                'connected': False,
                'error': str(e)
            }

# Décorateur pour la mise en cache automatique
def cached_method(cache_service: CacheService, ttl: int, prefix: str = "method:"):
    """
    Décorateur pour mettre en cache automatiquement les résultats de méthodes
    
    Args:
        cache_service: Instance du service de cache
        ttl: Durée de vie en secondes
        prefix: Préfixe des clés de cache
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Générer la clé de cache
            cache_key = cache_service._generate_cache_key(
                prefix,
                func.__name__,
                *args,
                **kwargs
            )
            
            # Essayer de récupérer depuis le cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Exécuter la fonction et cacher le résultat
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Instance globale du service de cache
cache_service = CacheService()

# Configuration de performance par défaut
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'cache_aggregations': True,
    'cache_meal_plan_ingredients': True,
    'batch_size_ingredients': 100,
    'max_concurrent_requests': 10,
    'request_timeout': 30
}

class PerformanceOptimizer:
    """Optimiseur de performance pour les opérations de liste de courses"""
    
    @staticmethod
    def optimize_ingredient_queries(ingredient_ids: List[int]) -> List[Dict]:
        """
        Optimise les requêtes d'ingrédients en utilisant des requêtes par batch
        
        Args:
            ingredient_ids: Liste des IDs d'ingrédients
        
        Returns:
            List[Dict]: Ingrédients optimisés
        """
        from models.ingredient import Ingredient
        
        # Diviser en batches pour éviter les requêtes trop lourdes
        batch_size = PERFORMANCE_CONFIG['batch_size_ingredients']
        ingredients = []
        
        for i in range(0, len(ingredient_ids), batch_size):
            batch_ids = ingredient_ids[i:i + batch_size]
            batch_ingredients = Ingredient.query.filter(
                Ingredient.id.in_(batch_ids)
            ).all()
            ingredients.extend(batch_ingredients)
        
        return ingredients

    @staticmethod
    def preload_related_data(shopping_list_ids: List[int]) -> Dict[int, Dict]:
        """
        Précharge les données liées pour plusieurs listes de courses
        
        Args:
            shopping_list_ids: IDs des listes de courses
        
        Returns:
            Dict[int, Dict]: Données préchargées par ID de liste
        """
        from models.meal_plan import ShoppingList
        from sqlalchemy.orm import joinedload
        
        # Requête optimisée avec jointure
        shopping_lists = ShoppingList.query.filter(
            ShoppingList.id.in_(shopping_list_ids)
        ).options(
            joinedload(ShoppingList.meal_plan)
        ).all()
        
        preloaded_data = {}
        for shopping_list in shopping_lists:
            preloaded_data[shopping_list.id] = {
                'shopping_list': shopping_list,
                'meal_plan': shopping_list.meal_plan,
                'items_count': len(shopping_list.items),
                'checked_count': len([
                    k for k, v in shopping_list.checked_items.items() if v
                ])
            }
        
        return preloaded_data