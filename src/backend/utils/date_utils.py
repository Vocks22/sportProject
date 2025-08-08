"""
Utilitaires de gestion des dates pour US1.6 - Standard ISO 8601
Module contenant les fonctions de calcul et validation des semaines lundi-dimanche
"""

from datetime import datetime, date, timedelta
from typing import Tuple, Optional


def parse_date(date_string: str) -> date:
    """
    Parse a date string in various formats to a date object
    
    Args:
        date_string: Date string in format YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY
        
    Returns:
        Date object
        
    Raises:
        ValueError: If date string format is invalid
    """
    # Try different formats
    formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt).date()
        except ValueError:
            continue
    
    raise ValueError(f"Invalid date format: {date_string}. Expected YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY")


def get_week_dates(week_start: date) -> list:
    """
    Get all dates in a week starting from Monday
    
    Args:
        week_start: Monday date of the week
        
    Returns:
        List of all 7 dates in the week
    """
    validate_week_start_iso8601(week_start)
    return [week_start + timedelta(days=i) for i in range(7)]


def get_monday_of_week(input_date: date) -> date:
    """
    Calcule le lundi de la semaine pour une date donnée selon ISO 8601
    
    La norme ISO 8601 définit la semaine comme débutant le lundi (1) et finissant le dimanche (7).
    
    Args:
        input_date: Date dont on veut le lundi de la semaine
        
    Returns:
        Date du lundi de la semaine correspondante
        
    Example:
        >>> get_monday_of_week(date(2025, 8, 7))  # Jeudi
        date(2025, 8, 4)  # Lundi de cette semaine
    """
    # weekday(): 0=lundi, 1=mardi, 2=mercredi, 3=jeudi, 4=vendredi, 5=samedi, 6=dimanche
    days_since_monday = input_date.weekday()
    monday_date = input_date - timedelta(days=days_since_monday)
    return monday_date


def get_sunday_of_week(input_date: date) -> date:
    """
    Calcule le dimanche de la semaine pour une date donnée selon ISO 8601
    
    Args:
        input_date: Date dont on veut le dimanche de la semaine
        
    Returns:
        Date du dimanche de la semaine correspondante
        
    Example:
        >>> get_sunday_of_week(date(2025, 8, 7))  # Jeudi
        date(2025, 8, 10)  # Dimanche de cette semaine
    """
    monday = get_monday_of_week(input_date)
    sunday = monday + timedelta(days=6)
    return sunday


def get_week_range_iso8601(input_date: date) -> Tuple[date, date]:
    """
    Retourne le lundi et dimanche de la semaine ISO 8601 pour une date donnée
    
    Args:
        input_date: Date de référence
        
    Returns:
        Tuple (monday, sunday) de la semaine
        
    Example:
        >>> get_week_range_iso8601(date(2025, 8, 7))  # Jeudi
        (date(2025, 8, 4), date(2025, 8, 10))  # (Lundi, Dimanche)
    """
    monday = get_monday_of_week(input_date)
    sunday = get_sunday_of_week(input_date)
    return (monday, sunday)


def is_monday(input_date: date) -> bool:
    """
    Vérifie si une date donnée est un lundi
    
    Args:
        input_date: Date à vérifier
        
    Returns:
        True si c'est un lundi, False sinon
        
    Example:
        >>> is_monday(date(2025, 8, 4))  # Lundi
        True
        >>> is_monday(date(2025, 8, 7))  # Jeudi  
        False
    """
    return input_date.weekday() == 0


def validate_week_start_iso8601(week_start: date) -> bool:
    """
    Valide qu'une date week_start respecte la norme ISO 8601 (doit être un lundi)
    
    Args:
        week_start: Date week_start à valider
        
    Returns:
        True si valide (lundi), False sinon
        
    Raises:
        ValueError: Si week_start n'est pas un lundi avec message explicatif
    """
    if not is_monday(week_start):
        weekday_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        current_weekday = weekday_names[week_start.weekday()]
        correct_monday = get_monday_of_week(week_start)
        
        raise ValueError(
            f"week_start doit être un lundi selon ISO 8601. "
            f"Date fournie: {week_start} ({current_weekday}). "
            f"Lundi correct: {correct_monday}"
        )
    
    return True


def convert_week_start_to_iso8601(old_week_start: date) -> date:
    """
    Convertit une ancienne date week_start vers le format ISO 8601 (lundi)
    
    Utilisé pendant la migration pour convertir les dates existantes.
    
    Args:
        old_week_start: Ancienne date week_start (peut être n'importe quel jour)
        
    Returns:
        Date du lundi correspondant selon ISO 8601
        
    Example:
        >>> convert_week_start_to_iso8601(date(2025, 8, 6))  # Mercredi
        date(2025, 8, 4)  # Lundi de cette semaine
    """
    return get_monday_of_week(old_week_start)


def get_week_number_iso8601(input_date: date) -> int:
    """
    Retourne le numéro de semaine selon ISO 8601
    
    Args:
        input_date: Date de référence
        
    Returns:
        Numéro de semaine (1-53)
        
    Example:
        >>> get_week_number_iso8601(date(2025, 8, 7))
        32
    """
    return input_date.isocalendar()[1]


def get_week_year_iso8601(input_date: date) -> int:
    """
    Retourne l'année de la semaine selon ISO 8601
    
    Attention: L'année ISO peut différer de l'année calendaire 
    pour les premières/dernières semaines de l'année.
    
    Args:
        input_date: Date de référence
        
    Returns:
        Année ISO de la semaine
        
    Example:
        >>> get_week_year_iso8601(date(2025, 1, 1))  # Peut être 2024 si semaine chevauche
        2025
    """
    return input_date.isocalendar()[0]


def format_week_display(week_start: date, locale: str = 'fr') -> str:
    """
    Formate une semaine pour l'affichage utilisateur
    
    Args:
        week_start: Date du lundi (début de semaine)
        locale: Locale pour le formatage ('fr' ou 'en')
        
    Returns:
        Chaîne formatée représentant la semaine
        
    Example:
        >>> format_week_display(date(2025, 8, 4), 'fr')
        'Semaine du 4 au 10 août 2025'
    """
    validate_week_start_iso8601(week_start)  # S'assurer que c'est un lundi
    
    sunday = get_sunday_of_week(week_start)
    
    if locale == 'fr':
        month_names_fr = [
            '', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'
        ]
        
        if week_start.month == sunday.month:
            # Même mois
            return f"Semaine du {week_start.day} au {sunday.day} {month_names_fr[week_start.month]} {week_start.year}"
        else:
            # Mois différents
            return f"Semaine du {week_start.day} {month_names_fr[week_start.month]} au {sunday.day} {month_names_fr[sunday.month]} {sunday.year}"
    
    else:  # English
        if week_start.month == sunday.month:
            return f"Week of {week_start.strftime('%B %d')} to {sunday.day}, {week_start.year}"
        else:
            return f"Week of {week_start.strftime('%B %d')} to {sunday.strftime('%B %d, %Y')}"


def next_monday(current_date: date) -> date:
    """
    Retourne le prochain lundi après la date donnée
    
    Args:
        current_date: Date de référence
        
    Returns:
        Date du prochain lundi
        
    Example:
        >>> next_monday(date(2025, 8, 7))  # Jeudi
        date(2025, 8, 11)  # Lundi suivant
    """
    days_until_next_monday = (7 - current_date.weekday()) % 7
    if days_until_next_monday == 0:  # Si on est lundi, prendre le lundi suivant
        days_until_next_monday = 7
    
    return current_date + timedelta(days=days_until_next_monday)


def previous_monday(current_date: date) -> date:
    """
    Retourne le lundi précédent avant la date donnée
    
    Si la date donnée est un lundi, retourne le lundi de la semaine précédente.
    Sinon, retourne le lundi de la semaine courante.
    
    Args:
        current_date: Date de référence
        
    Returns:
        Date du lundi précédent
        
    Example:
        >>> previous_monday(date(2025, 8, 7))  # Jeudi  
        date(2025, 8, 4)  # Lundi de cette semaine
        >>> previous_monday(date(2025, 8, 4))  # Lundi
        date(2025, 7, 28)  # Lundi précédent
    """
    if current_date.weekday() == 0:  # Si on est lundi
        return current_date - timedelta(days=7)
    else:
        return get_monday_of_week(current_date)


def get_current_week_monday() -> date:
    """
    Retourne le lundi de la semaine courante
    
    Returns:
        Date du lundi de la semaine actuelle
    """
    return get_monday_of_week(date.today())


# Fonctions de migration et validation


def batch_convert_week_starts(date_list: list[date]) -> list[Tuple[date, date]]:
    """
    Convertit une liste de dates vers leurs lundis correspondants (batch)
    
    Utilisé pour les migrations de données en lot.
    
    Args:
        date_list: Liste des dates à convertir
        
    Returns:
        Liste de tuples (date_originale, nouveau_lundi)
    """
    return [(original_date, get_monday_of_week(original_date)) for original_date in date_list]


def validate_database_week_starts(week_start_dates: list[date]) -> Tuple[bool, list[str]]:
    """
    Valide une liste de dates week_start de la base de données
    
    Args:
        week_start_dates: Liste des dates week_start à valider
        
    Returns:
        Tuple (is_valid, list_of_error_messages)
    """
    errors = []
    weekday_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    
    for i, week_start in enumerate(week_start_dates):
        if not is_monday(week_start):
            current_weekday = weekday_names[week_start.weekday()]
            correct_monday = get_monday_of_week(week_start)
            errors.append(
                f"Enregistrement {i+1}: {week_start} est un {current_weekday}, "
                f"devrait être {correct_monday} (lundi)"
            )
    
    return len(errors) == 0, errors


# Tests et exemples d'utilisation
if __name__ == "__main__":
    print("🧪 Tests des utilitaires de date ISO 8601")
    print("=" * 50)
    
    # Test avec différents jours de la semaine
    test_dates = [
        date(2025, 8, 4),   # Lundi
        date(2025, 8, 5),   # Mardi  
        date(2025, 8, 6),   # Mercredi
        date(2025, 8, 7),   # Jeudi
        date(2025, 8, 8),   # Vendredi
        date(2025, 8, 9),   # Samedi
        date(2025, 8, 10),  # Dimanche
    ]
    
    weekday_names = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
    
    for test_date in test_dates:
        monday = get_monday_of_week(test_date)
        sunday = get_sunday_of_week(test_date)
        weekday_name = weekday_names[test_date.weekday()]
        
        print(f"{test_date} ({weekday_name:>8}) → Semaine {monday} - {sunday}")
        print(f"  Format affiché: {format_week_display(monday, 'fr')}")
        print()
    
    # Test de validation
    print("🔍 Tests de validation:")
    try:
        validate_week_start_iso8601(date(2025, 8, 4))  # Lundi - OK
        print("✅ Lundi validé correctement")
    except ValueError as e:
        print(f"❌ Erreur inattendue: {e}")
    
    try:
        validate_week_start_iso8601(date(2025, 8, 6))  # Mercredi - KO
        print("❌ Validation incorrecte")
    except ValueError as e:
        print(f"✅ Mercredi rejeté correctement: {e}")