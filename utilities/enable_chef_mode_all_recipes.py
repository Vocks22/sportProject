#!/usr/bin/env python3
"""
Script pour activer le mode chef sur toutes les recettes dans Recipes.jsx
"""

import re

# Lire le fichier
with open('src/frontend/components/Recipes.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fonction pour déterminer la difficulté selon le temps
def get_difficulty(time_str):
    try:
        minutes = int(re.search(r'\d+', time_str).group())
        if minutes <= 10:
            return "beginner"
        elif minutes <= 20:
            return "intermediate"
        else:
            return "advanced"
    except:
        return "intermediate"

# Trouver toutes les recettes
lines = content.split('\n')
modified_lines = []
i = 0

while i < len(lines):
    line = lines[i]
    modified_lines.append(line)
    
    # Détecter le début d'un objet recette
    if 'id:' in line and '{' in lines[i-1] if i > 0 else False:
        # Chercher si has_chef_mode existe déjà dans cette recette
        has_chef_mode_found = False
        time_value = "15 min"  # valeur par défaut
        
        # Parcourir les lignes de la recette
        j = i
        brace_count = 1
        recipe_end = i
        
        while j < len(lines) and brace_count > 0:
            j += 1
            if j < len(lines):
                if '{' in lines[j]:
                    brace_count += 1
                if '}' in lines[j]:
                    brace_count -= 1
                    if brace_count == 0:
                        recipe_end = j
                if 'has_chef_mode' in lines[j]:
                    has_chef_mode_found = True
                if 'time:' in lines[j]:
                    time_match = re.search(r'"([^"]+)"', lines[j])
                    if time_match:
                        time_value = time_match.group(1)
        
        # Si has_chef_mode n'est pas trouvé, on l'ajoute
        if not has_chef_mode_found and recipe_end > i:
            # Continuer à ajouter les lignes jusqu'à la fin de la recette
            while i < recipe_end - 1:
                i += 1
                modified_lines.append(lines[i])
            
            # Ajouter has_chef_mode et difficulty_level avant la fermeture
            difficulty = get_difficulty(time_value)
            modified_lines.append(f'      has_chef_mode: true,')
            modified_lines.append(f'      difficulty_level: "{difficulty}"')
            
    i += 1

# Rejoindre les lignes modifiées
modified_content = '\n'.join(modified_lines)

# Écrire le fichier modifié
with open('src/frontend/components/Recipes.jsx', 'w', encoding='utf-8') as f:
    f.write(modified_content)

print("✅ Mode chef activé sur toutes les recettes!")
print("Les recettes ont été mises à jour avec:")
print("  - has_chef_mode: true")
print("  - difficulty_level basé sur le temps de préparation")
print("    • ≤10 min = beginner")
print("    • 11-20 min = intermediate") 
print("    • >20 min = advanced")