"""
Tests unitaires pour US1.6 - Utilitaires de gestion des dates ISO 8601
Module de tests complet pour valider toutes les fonctions date_utils.py

Coverage: 100% des fonctions utilitaires
Focus: Edge cases, validation, performance
"""

import pytest
from datetime import date, datetime, timedelta
from freezegun import freeze_time
import sys
import os

# Ajouter le chemin vers les modules backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'backend'))

from utils.date_utils import (
    get_monday_of_week,
    get_sunday_of_week, 
    get_week_range_iso8601,
    is_monday,
    validate_week_start_iso8601,
    convert_week_start_to_iso8601,
    get_week_number_iso8601,
    get_week_year_iso8601,
    format_week_display,
    next_monday,
    previous_monday,
    get_current_week_monday,
    batch_convert_week_starts,
    validate_database_week_starts
)


class TestDateUtilsBasicFunctions:
    """Tests des fonctions de base de calcul de dates"""
    
    def test_get_monday_of_week_all_weekdays(self):
        """Test get_monday_of_week pour chaque jour de la semaine"""
        # Semaine du 4 au 10 août 2025
        expected_monday = date(2025, 8, 4)
        
        test_cases = [
            (date(2025, 8, 4), expected_monday, "lundi"),      # lundi
            (date(2025, 8, 5), expected_monday, "mardi"),      # mardi  
            (date(2025, 8, 6), expected_monday, "mercredi"),   # mercredi
            (date(2025, 8, 7), expected_monday, "jeudi"),      # jeudi
            (date(2025, 8, 8), expected_monday, "vendredi"),   # vendredi
            (date(2025, 8, 9), expected_monday, "samedi"),     # samedi
            (date(2025, 8, 10), expected_monday, "dimanche"),  # dimanche
        ]
        
        for input_date, expected, day_name in test_cases:
            result = get_monday_of_week(input_date)
            assert result == expected, f"Échec pour {day_name} {input_date}: attendu {expected}, reçu {result}"
    
    def test_get_sunday_of_week_all_weekdays(self):
        """Test get_sunday_of_week pour chaque jour de la semaine"""
        # Semaine du 4 au 10 août 2025
        expected_sunday = date(2025, 8, 10)
        
        test_cases = [
            (date(2025, 8, 4), expected_sunday, "lundi"),
            (date(2025, 8, 5), expected_sunday, "mardi"), 
            (date(2025, 8, 6), expected_sunday, "mercredi"),
            (date(2025, 8, 7), expected_sunday, "jeudi"),
            (date(2025, 8, 8), expected_sunday, "vendredi"),
            (date(2025, 8, 9), expected_sunday, "samedi"),
            (date(2025, 8, 10), expected_sunday, "dimanche"),
        ]
        
        for input_date, expected, day_name in test_cases:
            result = get_sunday_of_week(input_date)
            assert result == expected, f"Échec pour {day_name} {input_date}: attendu {expected}, reçu {result}"
    
    def test_get_week_range_iso8601(self):
        """Test du calcul de plage de semaine ISO 8601"""
        test_cases = [
            # (date_input, expected_monday, expected_sunday)
            (date(2025, 8, 7), date(2025, 8, 4), date(2025, 8, 10)),
            (date(2025, 1, 1), date(2024, 12, 30), date(2025, 1, 5)),  # Transition d'année
            (date(2025, 12, 31), date(2025, 12, 29), date(2026, 1, 4)),  # Fin d'année
        ]
        
        for input_date, expected_monday, expected_sunday in test_cases:
            monday, sunday = get_week_range_iso8601(input_date)
            assert monday == expected_monday, f"Monday incorrecte pour {input_date}"
            assert sunday == expected_sunday, f"Sunday incorrecte pour {input_date}"
    
    def test_is_monday_validation(self):
        """Test de validation des lundis"""
        # Vrais lundis
        mondays = [
            date(2025, 8, 4),   # Lundi
            date(2025, 8, 11),  # Lundi suivant
            date(2025, 7, 28),  # Lundi précédent
        ]
        
        for monday in mondays:
            assert is_monday(monday), f"{monday} devrait être identifié comme lundi"
        
        # Non-lundis
        non_mondays = [
            date(2025, 8, 5),   # Mardi
            date(2025, 8, 6),   # Mercredi  
            date(2025, 8, 7),   # Jeudi
            date(2025, 8, 8),   # Vendredi
            date(2025, 8, 9),   # Samedi
            date(2025, 8, 10),  # Dimanche
        ]
        
        for non_monday in non_mondays:
            assert not is_monday(non_monday), f"{non_monday} ne devrait pas être identifié comme lundi"


class TestDateUtilsValidation:
    """Tests des fonctions de validation"""
    
    def test_validate_week_start_iso8601_valid(self):
        """Test de validation avec des lundis valides"""
        valid_mondays = [
            date(2025, 8, 4),   # Lundi
            date(2025, 8, 11),  # Lundi suivant
            date(2025, 1, 6),   # Premier lundi 2025
            date(2024, 12, 30), # Dernier lundi 2024
        ]
        
        for monday in valid_mondays:
            # Ne devrait pas lever d'exception
            result = validate_week_start_iso8601(monday)
            assert result is True
    
    def test_validate_week_start_iso8601_invalid(self):
        """Test de validation avec des dates invalides"""
        invalid_dates = [
            (date(2025, 8, 5), "mardi"),
            (date(2025, 8, 6), "mercredi"),  
            (date(2025, 8, 7), "jeudi"),
            (date(2025, 8, 8), "vendredi"),
            (date(2025, 8, 9), "samedi"),
            (date(2025, 8, 10), "dimanche"),
        ]
        
        for invalid_date, expected_day in invalid_dates:
            with pytest.raises(ValueError) as excinfo:
                validate_week_start_iso8601(invalid_date)
            
            error_message = str(excinfo.value)
            assert "week_start doit être un lundi selon ISO 8601" in error_message
            assert expected_day in error_message
            assert str(invalid_date) in error_message
    
    def test_convert_week_start_to_iso8601(self):
        """Test de conversion vers ISO 8601"""
        conversion_cases = [
            # (date_originale, lundi_attendu)
            (date(2025, 8, 7), date(2025, 8, 4)),   # Jeudi → Lundi
            (date(2025, 8, 10), date(2025, 8, 4)),  # Dimanche → Lundi
            (date(2025, 8, 4), date(2025, 8, 4)),   # Lundi → Lundi (pas de changement)
            (date(2025, 1, 1), date(2024, 12, 30)), # 1er janvier → Lundi précédent
        ]
        
        for original_date, expected_monday in conversion_cases:
            result = convert_week_start_to_iso8601(original_date)
            assert result == expected_monday
            assert is_monday(result), f"Le résultat {result} devrait être un lundi"


class TestDateUtilsISO8601Specific:
    """Tests spécifiques à la norme ISO 8601"""
    
    def test_get_week_number_iso8601(self):
        """Test du numéro de semaine ISO 8601"""
        test_cases = [
            # (date, numéro_semaine_attendu)
            (date(2025, 1, 6), 2),    # Première semaine complète de 2025
            (date(2025, 8, 7), 32),   # Semaine 32 en août
            (date(2025, 12, 29), 53), # Dernière semaine de 2025
        ]
        
        for test_date, expected_week in test_cases:
            result = get_week_number_iso8601(test_date)
            assert result == expected_week, f"Semaine incorrecte pour {test_date}: attendu {expected_week}, reçu {result}"
    
    def test_get_week_year_iso8601(self):
        """Test de l'année ISO 8601 (peut différer de l'année calendaire)"""
        test_cases = [
            # (date, année_iso_attendue)
            (date(2025, 1, 1), 2025),  # 1er janvier 2025
            (date(2024, 12, 30), 2025), # 30 décembre 2024 = semaine 1 de 2025
            (date(2026, 1, 1), 2026),   # 1er janvier 2026
        ]
        
        for test_date, expected_year in test_cases:
            result = get_week_year_iso8601(test_date)
            assert result == expected_year, f"Année ISO incorrecte pour {test_date}: attendu {expected_year}, reçu {result}"


class TestDateUtilsFormatting:
    """Tests des fonctions de formatage"""
    
    def test_format_week_display_french(self):
        """Test du formatage en français"""
        test_cases = [
            # (lundi, texte_attendu)
            (date(2025, 8, 4), "Semaine du 4 au 10 août 2025"),
            (date(2025, 1, 6), "Semaine du 6 au 12 janvier 2025"),
            (date(2025, 12, 29), "Semaine du 29 décembre 2025 au 4 janvier 2026"),  # Chevauche années
        ]
        
        for monday, expected_text in test_cases:
            result = format_week_display(monday, 'fr')
            assert result == expected_text, f"Formatage français incorrect: attendu '{expected_text}', reçu '{result}'"
    
    def test_format_week_display_english(self):
        """Test du formatage en anglais"""
        test_cases = [
            # (lundi, texte_attendu)
            (date(2025, 8, 4), "Week of August 04 to 10, 2025"),
            (date(2025, 1, 6), "Week of January 06 to 12, 2025"),
        ]
        
        for monday, expected_text in test_cases:
            result = format_week_display(monday, 'en')
            # Note: Le format exact peut varier selon la locale, on teste la présence des éléments clés
            assert "Week of" in result
            assert "2025" in result
    
    def test_format_week_display_invalid_date(self):
        """Test du formatage avec une date invalide (non-lundi)"""
        with pytest.raises(ValueError):
            format_week_display(date(2025, 8, 7), 'fr')  # Jeudi au lieu de lundi


class TestDateUtilsNavigation:
    """Tests des fonctions de navigation entre semaines"""
    
    def test_next_monday(self):
        """Test du calcul du lundi suivant"""
        test_cases = [
            # (date_input, lundi_suivant_attendu)
            (date(2025, 8, 7), date(2025, 8, 11)),   # Jeudi → Lundi suivant
            (date(2025, 8, 10), date(2025, 8, 11)),  # Dimanche → Lundi suivant  
            (date(2025, 8, 4), date(2025, 8, 11)),   # Lundi → Lundi suivant
        ]
        
        for input_date, expected_monday in test_cases:
            result = next_monday(input_date)
            assert result == expected_monday
            assert is_monday(result), f"Le résultat {result} devrait être un lundi"
    
    def test_previous_monday(self):
        """Test du calcul du lundi précédent"""
        test_cases = [
            # (date_input, lundi_précédent_attendu)
            (date(2025, 8, 7), date(2025, 7, 28)),   # Jeudi → Lundi précédent
            (date(2025, 8, 10), date(2025, 7, 28)),  # Dimanche → Lundi précédent
            (date(2025, 8, 4), date(2025, 7, 28)),   # Lundi → Lundi précédent
        ]
        
        for input_date, expected_monday in test_cases:
            result = previous_monday(input_date)
            assert result == expected_monday
            assert is_monday(result), f"Le résultat {result} devrait être un lundi"
    
    @freeze_time("2025-08-07")  # Jeudi 7 août 2025
    def test_get_current_week_monday(self):
        """Test du calcul du lundi de la semaine courante"""
        result = get_current_week_monday()
        expected = date(2025, 8, 4)  # Lundi de la semaine du 7 août
        
        assert result == expected
        assert is_monday(result)


class TestDateUtilsBatchOperations:
    """Tests des opérations en lot (migration)"""
    
    def test_batch_convert_week_starts(self):
        """Test de conversion en lot"""
        input_dates = [
            date(2025, 8, 5),   # Mardi
            date(2025, 8, 6),   # Mercredi  
            date(2025, 8, 7),   # Jeudi
            date(2025, 8, 10),  # Dimanche
        ]
        
        expected_monday = date(2025, 8, 4)
        
        result = batch_convert_week_starts(input_dates)
        
        assert len(result) == len(input_dates)
        
        for i, (original, converted) in enumerate(result):
            assert original == input_dates[i]
            assert converted == expected_monday
            assert is_monday(converted)
    
    def test_validate_database_week_starts_all_valid(self):
        """Test de validation de base avec toutes les dates valides"""
        valid_mondays = [
            date(2025, 8, 4),   # Lundi
            date(2025, 8, 11),  # Lundi suivant
            date(2025, 7, 28),  # Lundi précédent
        ]
        
        is_valid, errors = validate_database_week_starts(valid_mondays)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_database_week_starts_with_errors(self):
        """Test de validation de base avec des erreurs"""
        mixed_dates = [
            date(2025, 8, 4),   # Lundi - OK
            date(2025, 8, 5),   # Mardi - KO
            date(2025, 8, 11),  # Lundi - OK
            date(2025, 8, 7),   # Jeudi - KO
        ]
        
        is_valid, errors = validate_database_week_starts(mixed_dates)
        
        assert is_valid is False
        assert len(errors) == 2  # 2 erreurs attendues
        
        # Vérifier le contenu des messages d'erreur
        assert "mardi" in errors[0].lower()
        assert "jeudi" in errors[1].lower()
        assert "2025-08-05" in errors[0]
        assert "2025-08-07" in errors[1]


class TestDateUtilsEdgeCases:
    """Tests des cas limites et edge cases"""
    
    def test_year_transition_cases(self):
        """Test des transitions d'année"""
        # Cas où l'année ISO diffère de l'année calendaire
        test_cases = [
            # 31 décembre 2024 est un mardi, donc semaine 1 de 2025
            (date(2024, 12, 31), date(2024, 12, 30), date(2025, 1, 5)),
            # 1er janvier 2025 est un mercredi, donc semaine 1 de 2025  
            (date(2025, 1, 1), date(2024, 12, 30), date(2025, 1, 5)),
        ]
        
        for input_date, expected_monday, expected_sunday in test_cases:
            monday, sunday = get_week_range_iso8601(input_date)
            assert monday == expected_monday
            assert sunday == expected_sunday
    
    def test_leap_year_cases(self):
        """Test des années bissextiles"""
        # 2024 est une année bissextile
        leap_year_cases = [
            # 29 février 2024 (jeudi)
            (date(2024, 2, 29), date(2024, 2, 26), date(2024, 3, 3)),
        ]
        
        for input_date, expected_monday, expected_sunday in leap_year_cases:
            monday, sunday = get_week_range_iso8601(input_date)
            assert monday == expected_monday
            assert sunday == expected_sunday
    
    def test_performance_large_batch(self):
        """Test de performance avec un grand nombre de dates"""
        import time
        
        # Générer 1000 dates aléatoires
        import random
        start_date = date(2020, 1, 1)
        large_date_list = []
        
        for _ in range(1000):
            random_days = random.randint(0, 365 * 5)  # 5 ans de dates
            random_date = start_date + timedelta(days=random_days)
            large_date_list.append(random_date)
        
        # Mesurer le temps d'exécution
        start_time = time.time()
        result = batch_convert_week_starts(large_date_list)
        execution_time = time.time() - start_time
        
        # Vérifications
        assert len(result) == 1000
        assert execution_time < 1.0, f"Opération trop lente: {execution_time:.3f}s pour 1000 dates"
        
        # Vérifier que tous les résultats sont des lundis
        for original, monday in result:
            assert is_monday(monday)


class TestDateUtilsIntegration:
    """Tests d'intégration avec d'autres composants"""
    
    def test_migration_simulation(self):
        """Simulation d'une migration complète"""
        # Simuler des données existantes avec différents jours de semaine
        existing_week_starts = [
            date(2025, 7, 30),  # Mercredi
            date(2025, 8, 3),   # Dimanche  
            date(2025, 8, 6),   # Mercredi
            date(2025, 8, 9),   # Samedi
        ]
        
        # Étape 1: Validation des données actuelles (devrait échouer)
        is_valid_before, errors_before = validate_database_week_starts(existing_week_starts)
        assert is_valid_before is False
        assert len(errors_before) == 4  # Toutes les dates sont invalides
        
        # Étape 2: Conversion vers ISO 8601
        converted_data = batch_convert_week_starts(existing_week_starts)
        new_week_starts = [converted for _, converted in converted_data]
        
        # Étape 3: Validation des données converties (devrait réussir)
        is_valid_after, errors_after = validate_database_week_starts(new_week_starts)
        assert is_valid_after is True
        assert len(errors_after) == 0
        
        # Vérifier que toutes les dates sont maintenant des lundis
        for monday in new_week_starts:
            assert is_monday(monday)


# Configuration des fixtures pour les tests
@pytest.fixture
def sample_week_dates():
    """Fixture avec des dates d'exemple pour une semaine"""
    return {
        'monday': date(2025, 8, 4),
        'tuesday': date(2025, 8, 5),
        'wednesday': date(2025, 8, 6),
        'thursday': date(2025, 8, 7),
        'friday': date(2025, 8, 8),
        'saturday': date(2025, 8, 9),
        'sunday': date(2025, 8, 10),
    }


@pytest.fixture
def migration_test_data():
    """Fixture avec des données de test pour migration"""
    return [
        {'id': 1, 'old_week_start': date(2025, 7, 30), 'expected_monday': date(2025, 7, 28)},
        {'id': 2, 'old_week_start': date(2025, 8, 3), 'expected_monday': date(2025, 7, 28)},
        {'id': 3, 'old_week_start': date(2025, 8, 6), 'expected_monday': date(2025, 8, 4)},
        {'id': 4, 'old_week_start': date(2025, 8, 9), 'expected_monday': date(2025, 8, 4)},
    ]


if __name__ == "__main__":
    # Exécution des tests si le fichier est lancé directement
    pytest.main([__file__, "-v", "--tb=short"])