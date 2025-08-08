#!/usr/bin/env python3
"""
Script pour peupler la base de données avec les 65 recettes complètes
Incluant les conseils de chef et toutes les informations nutritionnelles
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from database import db
from models.recipe import Recipe
from models.ingredient import Ingredient

def create_recipes_data():
    """Retourne les données des 65 recettes"""
    recipes = []
    
    # REPAS 1 - Petit-déjeuner (15 recettes)
    breakfast_recipes = [
        {
            "name": "Omelette aux Blancs d'Œufs Classique",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Épices", "quantity": 1, "unit": "pincée"}
            ],
            "instructions": ["Séparer les blancs des jaunes", "Battre les blancs légèrement", "Faire chauffer la poêle antiadhésive", "Verser les blancs et cuire à feu moyen", "Ajouter les noix de cajou concassées", "Assaisonner avec les épices", "Plier l'omelette en deux"],
            "prep_time": 5,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 351,
            "total_protein": 28,
            "total_carbs": 15,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Température parfaite: la poêle doit être chaude mais pas fumante", "Les blancs doivent être à température ambiante pour une meilleure texture"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation", "description": "Séparer les blancs et les laisser revenir à température ambiante", "duration_minutes": 2, "temperature": "Ambiante", "technique": "Séparation"},
                {"step": 2, "title": "Cuisson", "description": "Cuire à feu moyen en remuant délicatement", "duration_minutes": 3, "temperature": "Feu moyen", "technique": "Cuisson poêle"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Texture parfaite", "description": "Ne pas trop battre les blancs pour garder une texture moelleuse", "importance": "high"},
                {"type": "tip", "title": "Assaisonnement", "description": "Ajouter les épices en fin de cuisson", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Les bords commencent à prendre", "what_to_look_for": "Bordure blanche qui se forme"}
            ],
            "timing_details": {"total_time": 10, "active_time": 8, "passive_time": 2},
            "media_references": [{"type": "photo", "step_number": 2, "description": "Omelette parfaitement cuite"}]
        },
        {
            "name": "Omelette aux Blancs d'Œufs et Épinards",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Épinards frais", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Laver et égoutter les épinards", "Battre les blancs d'œufs", "Faire revenir les épinards rapidement", "Ajouter les blancs battus", "Incorporer les noix de cajou", "Cuire jusqu'à ce que l'omelette soit prise"],
            "prep_time": 7,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 355,
            "total_protein": 29,
            "total_carbs": 16,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Bien essorer les épinards pour éviter l'excès d'eau", "Faire sauter les épinards rapidement pour garder leur couleur verte"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation épinards", "description": "Laver, égoutter et faire sauter les épinards", "duration_minutes": 3, "temperature": "Feu vif", "technique": "Sauté rapide"},
                {"step": 2, "title": "Cuisson omelette", "description": "Ajouter les blancs et cuire doucement", "duration_minutes": 4, "temperature": "Feu moyen", "technique": "Cuisson douce"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Épinards croquants", "description": "Ne pas trop cuire les épinards pour garder du croquant", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Épinards wilted mais encore verts", "what_to_look_for": "Couleur verte vive maintenue"}
            ],
            "timing_details": {"total_time": 12, "active_time": 10, "passive_time": 2},
            "media_references": []
        },
        {
            "name": "Scrambled aux Blancs d'Œufs et Herbes",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes effilées", "quantity": 40, "unit": "g"},
                {"name": "Herbes de Provence", "quantity": 1, "unit": "c. à café"}
            ],
            "instructions": ["Battre les blancs au fouet", "Ajouter les herbes de Provence", "Cuire à feu doux en remuant constamment", "Incorporer les amandes en fin de cuisson"],
            "prep_time": 3,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 348,
            "total_protein": 28,
            "total_carbs": 14,
            "total_fat": 19,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Remuer constamment pour une texture crémeuse", "Retirer du feu quand encore légèrement humide"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation", "description": "Battre les blancs avec les herbes", "duration_minutes": 2, "temperature": "Ambiante", "technique": "Battage au fouet"},
                {"step": 2, "title": "Cuisson", "description": "Cuire en remuant constamment", "duration_minutes": 3, "temperature": "Feu doux", "technique": "Scrambling"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Texture crémeuse", "description": "Retirer du feu quand encore légèrement humide, la chaleur résiduelle finira la cuisson", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Texture crémeuse avec petits morceaux", "what_to_look_for": "Aspect crémeux mais pas liquide"}
            ],
            "timing_details": {"total_time": 8, "active_time": 8, "passive_time": 0},
            "media_references": []
        },
        {
            "name": "Omelette Roulée aux Blancs d'Œufs",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Paprika", "quantity": 1, "unit": "pincée"}
            ],
            "instructions": ["Battre les blancs avec le paprika", "Verser dans une poêle chaude", "Cuire doucement sans remuer", "Ajouter les noix au centre", "Rouler délicatement l'omelette"],
            "prep_time": 5,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 351,
            "total_protein": 28,
            "total_carbs": 15,
            "total_fat": 18,
            "difficulty_level": "intermediate",
            "has_chef_mode": True,
            "chef_instructions": ["Technique du roulage: commencer par un bord et rouler délicatement", "Utiliser une spatule large pour faciliter le roulage"],
            "cooking_steps": [
                {"step": 1, "title": "Cuisson base", "description": "Cuire l'omelette sans remuer jusqu'à ce qu'elle soit presque prise", "duration_minutes": 5, "temperature": "Feu moyen-doux", "technique": "Cuisson statique"},
                {"step": 2, "title": "Roulage", "description": "Ajouter garniture et rouler délicatement", "duration_minutes": 2, "temperature": "Hors feu", "technique": "Roulage"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Roulage parfait", "description": "L'omelette doit être juste prise mais encore souple pour pouvoir la rouler", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Surface presque sèche mais encore brillante", "what_to_look_for": "Pas de liquide en surface"}
            ],
            "timing_details": {"total_time": 15, "active_time": 10, "passive_time": 5},
            "media_references": []
        },
        {
            "name": "Blancs d'Œufs Brouillés aux Champignons",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Champignons", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Émincer les champignons", "Faire sauter les champignons", "Battre les blancs", "Ajouter aux champignons", "Brouiller doucement", "Garnir d'amandes"],
            "prep_time": 5,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 350,
            "total_protein": 29,
            "total_carbs": 15,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Faire dorer les champignons pour concentrer les saveurs", "Ne pas ajouter de sel aux champignons au début"],
            "cooking_steps": [
                {"step": 1, "title": "Champignons", "description": "Faire sauter jusqu'à évaporation de l'eau", "duration_minutes": 4, "temperature": "Feu vif", "technique": "Sauté"},
                {"step": 2, "title": "Brouillage", "description": "Ajouter les blancs et brouiller doucement", "duration_minutes": 3, "temperature": "Feu doux", "technique": "Scrambling"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Champignons dorés", "description": "Attendre que toute l'eau s'évapore pour avoir des champignons dorés", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Champignons dorés sans eau", "what_to_look_for": "Couleur dorée, pas d'eau dans la poêle"}
            ],
            "timing_details": {"total_time": 12, "active_time": 12, "passive_time": 0},
            "media_references": []
        },
        {
            "name": "Omelette aux Blancs d'Œufs et Tomates Cerises",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Tomates cerises", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Couper les tomates en deux", "Faire revenir les tomates", "Battre les blancs", "Verser sur les tomates", "Ajouter les noix", "Cuire jusqu'à prise complète"],
            "prep_time": 5,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 353,
            "total_protein": 28,
            "total_carbs": 16,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Faire caraméliser légèrement les tomates", "Éviter de trop remuer pour garder les tomates entières"],
            "cooking_steps": [
                {"step": 1, "title": "Tomates", "description": "Faire revenir les tomates coupées", "duration_minutes": 2, "temperature": "Feu moyen", "technique": "Sauté"},
                {"step": 2, "title": "Omelette", "description": "Ajouter les blancs et cuire", "duration_minutes": 3, "temperature": "Feu moyen", "technique": "Cuisson omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Tomates caramélisées", "description": "Laisser les tomates caraméliser sans trop remuer", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Tomates légèrement dorées", "what_to_look_for": "Bords caramélisés"}
            ],
            "timing_details": {"total_time": 10, "active_time": 8, "passive_time": 2},
            "media_references": []
        },
        {
            "name": "Blancs d'Œufs à la Ciboulette",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Ciboulette fraîche", "quantity": 10, "unit": "g"}
            ],
            "instructions": ["Ciseler finement la ciboulette", "Battre les blancs", "Incorporer la ciboulette", "Cuire en omelette", "Parsemer d'amandes"],
            "prep_time": 3,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 348,
            "total_protein": 28,
            "total_carbs": 14,
            "total_fat": 19,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Ajouter la ciboulette en fin de cuisson pour préserver la saveur", "Ciseler finement pour une répartition homogène"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation", "description": "Ciseler la ciboulette et battre les blancs", "duration_minutes": 2, "temperature": "Ambiante", "technique": "Ciselage"},
                {"step": 2, "title": "Cuisson", "description": "Cuire l'omelette et ajouter ciboulette en fin", "duration_minutes": 3, "temperature": "Feu moyen", "technique": "Cuisson omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Ciboulette fraîche", "description": "Ajouter la moitié en fin de cuisson pour garder la fraîcheur", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Omelette dorée parsemée de vert", "what_to_look_for": "Points verts bien répartis"}
            ],
            "timing_details": {"total_time": 8, "active_time": 8, "passive_time": 0},
            "media_references": []
        },
        {
            "name": "Omelette aux Blancs d'Œufs et Courgettes",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Courgettes râpées", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Râper les courgettes", "Faire dégorger et essorer", "Faire revenir les courgettes", "Ajouter les blancs battus", "Incorporer les noix", "Cuire doucement"],
            "prep_time": 7,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 352,
            "total_protein": 28,
            "total_carbs": 15,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Bien essorer les courgettes pour éviter l'excès d'eau", "Faire dorer légèrement les courgettes avant d'ajouter les œufs"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation courgettes", "description": "Râper, saler, essorer les courgettes", "duration_minutes": 5, "temperature": "Ambiante", "technique": "Dégorgeage"},
                {"step": 2, "title": "Cuisson", "description": "Faire revenir puis ajouter les blancs", "duration_minutes": 4, "temperature": "Feu moyen", "technique": "Sauté puis omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Courgettes sans eau", "description": "Presser fortement les courgettes râpées pour extraire toute l'eau", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Courgettes dorées avant ajout des œufs", "what_to_look_for": "Légère coloration dorée"}
            ],
            "timing_details": {"total_time": 12, "active_time": 9, "passive_time": 3},
            "media_references": []
        },
        {
            "name": "Blancs d'Œufs aux Fines Herbes",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Persil, basilic, ciboulette", "quantity": 15, "unit": "g"}
            ],
            "instructions": ["Hacher finement les herbes", "Battre les blancs", "Incorporer les herbes", "Cuire en omelette", "Garnir d'amandes"],
            "prep_time": 5,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 348,
            "total_protein": 28,
            "total_carbs": 14,
            "total_fat": 19,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Mélanger les herbes juste avant la cuisson", "Réserver quelques herbes pour la finition"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation", "description": "Hacher les herbes et battre les blancs", "duration_minutes": 3, "temperature": "Ambiante", "technique": "Hachage"},
                {"step": 2, "title": "Cuisson", "description": "Cuire avec les herbes incorporées", "duration_minutes": 3, "temperature": "Feu moyen", "technique": "Cuisson omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Herbes fraîches", "description": "Ajouter une partie des herbes en fin de cuisson", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Omelette parsemée de points verts", "what_to_look_for": "Herbes bien réparties"}
            ],
            "timing_details": {"total_time": 10, "active_time": 10, "passive_time": 0},
            "media_references": []
        },
        {
            "name": "Omelette aux Blancs d'Œufs et Poivrons",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Poivrons colorés", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Couper les poivrons en dés", "Faire revenir les poivrons", "Battre les blancs", "Verser sur les poivrons", "Ajouter les noix", "Cuire jusqu'à prise"],
            "prep_time": 5,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 354,
            "total_protein": 28,
            "total_carbs": 16,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Faire revenir les poivrons jusqu'à ce qu'ils soient tendres", "Utiliser des poivrons de couleurs différentes pour l'aspect visuel"],
            "cooking_steps": [
                {"step": 1, "title": "Poivrons", "description": "Faire revenir les poivrons en dés", "duration_minutes": 5, "temperature": "Feu moyen", "technique": "Sauté"},
                {"step": 2, "title": "Omelette", "description": "Ajouter les blancs et cuire", "duration_minutes": 3, "temperature": "Feu moyen", "technique": "Cuisson omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Poivrons croquants", "description": "Ne pas trop cuire pour garder du croquant", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Poivrons tendres mais colorés", "what_to_look_for": "Couleurs vives maintenues"}
            ],
            "timing_details": {"total_time": 15, "active_time": 12, "passive_time": 3},
            "media_references": []
        },
        {
            "name": "Blancs d'Œufs Façon Tortilla",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Ail, paprika fumé", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Écraser l'ail", "Battre les blancs avec l'ail et paprika", "Cuire lentement des deux côtés", "Parsemer d'amandes"],
            "prep_time": 5,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 350,
            "total_protein": 28,
            "total_carbs": 14,
            "total_fat": 19,
            "difficulty_level": "intermediate",
            "has_chef_mode": True,
            "chef_instructions": ["Technique espagnole: cuisson lente pour une texture ferme", "Retourner avec une assiette"],
            "cooking_steps": [
                {"step": 1, "title": "Première face", "description": "Cuire lentement le premier côté", "duration_minutes": 4, "temperature": "Feu doux", "technique": "Cuisson lente"},
                {"step": 2, "title": "Retournement", "description": "Retourner et cuire l'autre face", "duration_minutes": 3, "temperature": "Feu doux", "technique": "Retournement à l'assiette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Retournement parfait", "description": "Utiliser une assiette pour retourner la tortilla", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Bords qui se décollent", "what_to_look_for": "Bords fermes et dorés"}
            ],
            "timing_details": {"total_time": 12, "active_time": 10, "passive_time": 2},
            "media_references": []
        },
        {
            "name": "Omelette aux Blancs d'Œufs et Roquette",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Roquette", "quantity": 30, "unit": "g"}
            ],
            "instructions": ["Laver et essorer la roquette", "Battre les blancs", "Cuire l'omelette à moitié", "Ajouter la roquette", "Plier et finir la cuisson", "Garnir de noix"],
            "prep_time": 5,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 352,
            "total_protein": 28,
            "total_carbs": 15,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Ajouter la roquette crue pour garder le piquant", "Ne pas trop cuire pour préserver les nutriments"],
            "cooking_steps": [
                {"step": 1, "title": "Base omelette", "description": "Cuire l'omelette à moitié", "duration_minutes": 3, "temperature": "Feu moyen", "technique": "Cuisson partielle"},
                {"step": 2, "title": "Finition", "description": "Ajouter roquette et plier", "duration_minutes": 2, "temperature": "Feu doux", "technique": "Pliage"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Roquette croquante", "description": "Ajouter la roquette au dernier moment", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Roquette encore verte et croquante", "what_to_look_for": "Feuilles non flétries"}
            ],
            "timing_details": {"total_time": 10, "active_time": 8, "passive_time": 2},
            "media_references": []
        },
        {
            "name": "Blancs d'Œufs aux Épices Orientales",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Cumin, coriandre, paprika", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Mélanger les épices", "Battre les blancs avec les épices", "Cuire en omelette", "Parsemer d'amandes grillées"],
            "prep_time": 5,
            "cook_time": 5,
            "servings": 1,
            "total_calories": 348,
            "total_protein": 28,
            "total_carbs": 14,
            "total_fat": 19,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Faire griller légèrement les épices pour libérer les arômes", "Équilibrer les épices selon le goût"],
            "cooking_steps": [
                {"step": 1, "title": "Épices", "description": "Faire griller les épices à sec", "duration_minutes": 1, "temperature": "Feu moyen", "technique": "Torréfaction"},
                {"step": 2, "title": "Cuisson", "description": "Battre avec blancs et cuire", "duration_minutes": 4, "temperature": "Feu moyen", "technique": "Cuisson omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Épices grillées", "description": "30 secondes à sec pour libérer les arômes", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Épices qui dégagent leur parfum", "what_to_look_for": "Arôme qui se dégage"}
            ],
            "timing_details": {"total_time": 10, "active_time": 10, "passive_time": 0},
            "media_references": []
        },
        {
            "name": "Omelette aux Blancs d'Œufs et Brocolis",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Brocolis vapeur", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Cuire les brocolis à la vapeur", "Battre les blancs", "Faire l'omelette", "Ajouter les brocolis", "Incorporer les noix", "Plier et servir"],
            "prep_time": 8,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 353,
            "total_protein": 29,
            "total_carbs": 15,
            "total_fat": 18,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Brocolis al dente pour garder les nutriments", "Couper en petits bouquets pour une cuisson uniforme"],
            "cooking_steps": [
                {"step": 1, "title": "Brocolis", "description": "Cuire à la vapeur al dente", "duration_minutes": 5, "temperature": "Vapeur", "technique": "Cuisson vapeur"},
                {"step": 2, "title": "Omelette", "description": "Faire l'omelette avec brocolis", "duration_minutes": 4, "temperature": "Feu moyen", "technique": "Cuisson omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Brocolis verts", "description": "Plonger dans l'eau glacée après vapeur pour garder la couleur", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Brocolis vert vif et fermes", "what_to_look_for": "Couleur verte intense"}
            ],
            "timing_details": {"total_time": 15, "active_time": 10, "passive_time": 5},
            "media_references": []
        },
        {
            "name": "Blancs d'Œufs à l'Italienne",
            "category": "breakfast",
            "meal_type": "repas1",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Basilic, origan, ail", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Hacher le basilic et l'ail", "Battre les blancs avec origan", "Cuire l'omelette", "Ajouter basilic frais", "Garnir d'amandes"],
            "prep_time": 5,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 350,
            "total_protein": 28,
            "total_carbs": 14,
            "total_fat": 19,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Basilic frais ajouté en fin de cuisson", "Ail écrasé pour libérer les saveurs"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation", "description": "Préparer les aromates", "duration_minutes": 3, "temperature": "Ambiante", "technique": "Hachage"},
                {"step": 2, "title": "Cuisson", "description": "Cuire avec les aromates", "duration_minutes": 4, "temperature": "Feu moyen", "technique": "Cuisson omelette"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Basilic frais", "description": "Ajouter le basilic après cuisson pour préserver l'arôme", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Omelette dorée parsemée de vert", "what_to_look_for": "Basilic frais non flétri"}
            ],
            "timing_details": {"total_time": 12, "active_time": 10, "passive_time": 2},
            "media_references": []
        }
    ]
    
    # COLLATION 1 - Smoothies (10 recettes)
    smoothie_recipes = [
        {
            "name": "Smoothie Protéiné Classique",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Ananas", "quantity": 50, "unit": "g"},
                {"name": "Chocolat noir", "quantity": 10, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Ajouter des glaçons si désiré", "Servir immédiatement"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 300,
            "total_protein": 12,
            "total_carbs": 45,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Tropical Protéiné",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Ananas", "quantity": 50, "unit": "g"},
                {"name": "Mangue", "quantity": 30, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients jusqu'à consistance lisse", "Servir frais"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 305,
            "total_protein": 12,
            "total_carbs": 48,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Chocolat-Banane",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Banane", "quantity": 50, "unit": "g"},
                {"name": "Chocolat noir", "quantity": 10, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Ajouter de la glace pilée", "Déguster immédiatement"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 310,
            "total_protein": 13,
            "total_carbs": 47,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Vert Protéiné",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Épinards", "quantity": 50, "unit": "g"},
                {"name": "Ananas", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Mixer d'abord les épinards avec le lait", "Ajouter les autres ingrédients", "Mixer jusqu'à consistance lisse"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 298,
            "total_protein": 12,
            "total_carbs": 45,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Fruits Rouges Avoine",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Fruits rouges mélangés", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Servir bien frais"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 295,
            "total_protein": 12,
            "total_carbs": 44,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Vanille-Cannelle",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Ananas", "quantity": 50, "unit": "g"},
                {"name": "Extrait vanille, cannelle", "quantity": 2, "unit": "ml"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Saupoudrer de cannelle", "Servir"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 300,
            "total_protein": 12,
            "total_carbs": 45,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Coco-Ananas",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Ananas", "quantity": 50, "unit": "g"},
                {"name": "Copeaux de coco", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Garnir de copeaux de coco", "Servir frais"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 308,
            "total_protein": 12,
            "total_carbs": 45,
            "total_fat": 9,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Chocolat-Menthe",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Chocolat noir", "quantity": 10, "unit": "g"},
                {"name": "Menthe fraîche", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Décorer avec menthe fraîche", "Servir immédiatement"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 302,
            "total_protein": 12,
            "total_carbs": 44,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Pêche-Avoine",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Pêche", "quantity": 50, "unit": "g"},
                {"name": "Chocolat noir", "quantity": 10, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Servir bien frais"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 305,
            "total_protein": 12,
            "total_carbs": 46,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Smoothie Épicé",
            "category": "snack",
            "meal_type": "collation1",
            "ingredients": [
                {"name": "Lait d'amande", "quantity": 200, "unit": "ml"},
                {"name": "Avoine", "quantity": 60, "unit": "g"},
                {"name": "Ananas", "quantity": 50, "unit": "g"},
                {"name": "Gingembre, curcuma", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Mixer tous les ingrédients", "Ajuster les épices au goût", "Servir"],
            "prep_time": 5,
            "cook_time": 0,
            "servings": 1,
            "total_calories": 300,
            "total_protein": 12,
            "total_carbs": 45,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        }
    ]
    
    # REPAS 2 - Déjeuner (15 recettes)
    lunch_recipes = [
        {
            "name": "Poulet Grillé aux Brocolis Classique",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Brocolis", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Griller le poulet", "Cuire les brocolis à la vapeur", "Assaisonner et servir"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 310,
            "total_protein": 35,
            "total_carbs": 15,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Mariner le poulet 30 min avant cuisson", "Cuisson à cœur 75°C"],
            "cooking_steps": [
                {"step": 1, "title": "Grillade", "description": "Griller le poulet des deux côtés", "duration_minutes": 8, "temperature": "Feu vif", "technique": "Grillade"},
                {"step": 2, "title": "Vapeur", "description": "Cuire les brocolis al dente", "duration_minutes": 5, "temperature": "Vapeur", "technique": "Cuisson vapeur"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Poulet juteux", "description": "Laisser reposer 3 min après cuisson", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 1, "description": "Marques de grill bien visibles", "what_to_look_for": "Quadrillage doré"}
            ],
            "timing_details": {"total_time": 20, "active_time": 15, "passive_time": 5},
            "media_references": []
        },
        {
            "name": "Dinde Sautée aux Épinards",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Escalope de dinde", "quantity": 180, "unit": "g"},
                {"name": "Épinards frais", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Faire sauter la dinde", "Ajouter les épinards", "Assaisonner et servir"],
            "prep_time": 8,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 295,
            "total_protein": 34,
            "total_carbs": 12,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Dinde en lanières pour cuisson rapide", "Épinards ajoutés en fin de cuisson"],
            "cooking_steps": [
                {"step": 1, "title": "Sauté dinde", "description": "Faire sauter la dinde en lanières", "duration_minutes": 5, "temperature": "Feu vif", "technique": "Sauté"},
                {"step": 2, "title": "Épinards", "description": "Ajouter épinards et faire tomber", "duration_minutes": 2, "temperature": "Feu moyen", "technique": "Wilt"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Épinards croquants", "description": "Ne pas trop cuire les épinards", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Épinards tombés mais verts", "what_to_look_for": "Couleur verte maintenue"}
            ],
            "timing_details": {"total_time": 15, "active_time": 15, "passive_time": 0},
            "media_references": []
        },
        {
            "name": "Poulet aux Courgettes Grillées",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Courgettes", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Herbes de Provence", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Trancher les courgettes", "Griller poulet et courgettes", "Assaisonner aux herbes"],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 1,
            "total_calories": 308,
            "total_protein": 35,
            "total_carbs": 14,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Courgettes en tranches de 1cm", "Badigeonner d'huile avant grillage"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation", "description": "Trancher courgettes et préparer poulet", "duration_minutes": 5, "temperature": "Ambiante", "technique": "Découpe"},
                {"step": 2, "title": "Grillage", "description": "Griller poulet et courgettes", "duration_minutes": 10, "temperature": "Feu vif", "technique": "Grillade"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Courgettes grillées", "description": "Marques de grill des deux côtés", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Belles marques de grill", "what_to_look_for": "Lignes dorées"}
            ],
            "timing_details": {"total_time": 25, "active_time": 20, "passive_time": 5},
            "media_references": []
        },
        {
            "name": "Dinde aux Haricots Verts",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Escalope de dinde", "quantity": 180, "unit": "g"},
                {"name": "Haricots verts", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Ail", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Cuire les haricots verts", "Faire sauter la dinde", "Mélanger avec ail", "Servir chaud"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 292,
            "total_protein": 34,
            "total_carbs": 13,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Poulet Mariné aux Légumes Méditerranéens",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Courgettes", "quantity": 75, "unit": "g"},
                {"name": "Aubergines", "quantity": 75, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Mariner le poulet", "Griller les légumes", "Cuire le poulet", "Assembler et servir"],
            "prep_time": 15,
            "cook_time": 15,
            "servings": 1,
            "total_calories": 315,
            "total_protein": 35,
            "total_carbs": 16,
            "total_fat": 8,
            "difficulty_level": "intermediate",
            "has_chef_mode": True,
            "chef_instructions": ["Marinade minimum 1h idéalement", "Légumes en dés réguliers"],
            "cooking_steps": [
                {"step": 1, "title": "Marinade", "description": "Mariner le poulet", "duration_minutes": 30, "temperature": "Frigo", "technique": "Marinade"},
                {"step": 2, "title": "Cuisson", "description": "Griller poulet et légumes", "duration_minutes": 15, "temperature": "Feu moyen", "technique": "Grillade"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Marinade express", "description": "Piquer le poulet pour faire pénétrer la marinade", "importance": "medium"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Légumes dorés et tendres", "what_to_look_for": "Caramélisation légère"}
            ],
            "timing_details": {"total_time": 30, "active_time": 20, "passive_time": 10},
            "media_references": []
        },
        {
            "name": "Dinde au Curry et Brocolis",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Escalope de dinde", "quantity": 180, "unit": "g"},
                {"name": "Brocolis", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Curry", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Faire sauter la dinde au curry", "Cuire les brocolis", "Mélanger et servir"],
            "prep_time": 8,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 298,
            "total_protein": 34,
            "total_carbs": 14,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Poulet aux Champignons et Épinards",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Champignons", "quantity": 75, "unit": "g"},
                {"name": "Épinards", "quantity": 75, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Faire sauter les champignons", "Cuire le poulet", "Ajouter les épinards", "Servir ensemble"],
            "prep_time": 10,
            "cook_time": 12,
            "servings": 1,
            "total_calories": 312,
            "total_protein": 36,
            "total_carbs": 14,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Dinde Grillée aux Asperges",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Escalope de dinde", "quantity": 180, "unit": "g"},
                {"name": "Asperges vertes", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Griller la dinde", "Griller les asperges", "Assaisonner et servir"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 290,
            "total_protein": 34,
            "total_carbs": 12,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Poulet Tandoori aux Légumes Verts",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Mélange légumes verts", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Épices tandoori", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Mariner le poulet au tandoori", "Cuire au four", "Faire sauter les légumes", "Servir ensemble"],
            "prep_time": 15,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 318,
            "total_protein": 35,
            "total_carbs": 16,
            "total_fat": 8,
            "difficulty_level": "intermediate",
            "has_chef_mode": False
        },
        {
            "name": "Dinde aux Poivrons Colorés",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Escalope de dinde", "quantity": 180, "unit": "g"},
                {"name": "Poivrons mélangés", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Couper les poivrons en lanières", "Faire sauter la dinde", "Ajouter les poivrons", "Servir chaud"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 296,
            "total_protein": 34,
            "total_carbs": 14,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Poulet à l'Estragon et Courgettes",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Courgettes", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Estragon", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Cuire le poulet à l'estragon", "Faire sauter les courgettes", "Mélanger et servir"],
            "prep_time": 10,
            "cook_time": 12,
            "servings": 1,
            "total_calories": 308,
            "total_protein": 35,
            "total_carbs": 14,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Dinde aux Brocolis et Ail",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Escalope de dinde", "quantity": 180, "unit": "g"},
                {"name": "Brocolis", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Ail", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Faire sauter la dinde avec l'ail", "Cuire les brocolis", "Assembler et servir"],
            "prep_time": 8,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 295,
            "total_protein": 34,
            "total_carbs": 14,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Poulet Paprika aux Épinards",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Épinards", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Paprika fumé", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Cuire le poulet au paprika", "Faire tomber les épinards", "Servir ensemble"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 310,
            "total_protein": 35,
            "total_carbs": 14,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Dinde aux Légumes Asiatiques",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Escalope de dinde", "quantity": 180, "unit": "g"},
                {"name": "Pak-choï", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Gingembre", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Faire sauter la dinde au gingembre", "Wok les légumes", "Servir chaud"],
            "prep_time": 8,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 293,
            "total_protein": 34,
            "total_carbs": 13,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Poulet aux Herbes de Provence",
            "category": "lunch",
            "meal_type": "repas2",
            "ingredients": [
                {"name": "Blanc de poulet", "quantity": 180, "unit": "g"},
                {"name": "Mélange légumes verts", "quantity": 150, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Herbes de Provence", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Cuire le poulet aux herbes", "Faire sauter les légumes", "Servir ensemble"],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 1,
            "total_calories": 312,
            "total_protein": 35,
            "total_carbs": 15,
            "total_fat": 8,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        }
    ]
    
    # COLLATION 2 - Blancs d'œufs aux oléagineux (10 recettes)
    snack2_recipes = [
        {
            "name": "Blancs d'Œufs aux Amandes Classique",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Fruits rouges", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Cuire les blancs en omelette", "Garnir d'amandes", "Servir avec fruits rouges"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 301,
            "total_protein": 25,
            "total_carbs": 18,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Noix de Cajou et Myrtilles",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de cajou", "quantity": 40, "unit": "g"},
                {"name": "Myrtilles", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Battre et cuire les blancs", "Ajouter noix de cajou", "Servir avec myrtilles"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 305,
            "total_protein": 24,
            "total_carbs": 19,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Amandes et Framboises",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes effilées", "quantity": 40, "unit": "g"},
                {"name": "Framboises", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Cuire les blancs", "Parsemer d'amandes effilées", "Accompagner de framboises"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 299,
            "total_protein": 25,
            "total_carbs": 17,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Noix et Fraises",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Cerneaux de noix", "quantity": 40, "unit": "g"},
                {"name": "Fraises", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Cuire les blancs", "Concasser les noix dessus", "Servir avec fraises coupées"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 308,
            "total_protein": 24,
            "total_carbs": 18,
            "total_fat": 13,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Amandes et Mûres",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Mûres", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Préparer les blancs", "Garnir d'amandes", "Accompagner de mûres"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 301,
            "total_protein": 25,
            "total_carbs": 18,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Noisettes et Fruits Rouges",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noisettes", "quantity": 40, "unit": "g"},
                {"name": "Mélange fruits rouges", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Cuire les blancs", "Parsemer de noisettes", "Servir avec fruits rouges"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 303,
            "total_protein": 24,
            "total_carbs": 18,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Amandes et Cassis",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Cassis", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Préparer les blancs", "Ajouter amandes", "Garnir de cassis"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 298,
            "total_protein": 25,
            "total_carbs": 17,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Pistaches et Fraises",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Pistaches", "quantity": 40, "unit": "g"},
                {"name": "Fraises", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Cuire les blancs", "Parsemer de pistaches", "Servir avec fraises"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 306,
            "total_protein": 25,
            "total_carbs": 18,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Amandes et Groseilles",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Amandes", "quantity": 40, "unit": "g"},
                {"name": "Groseilles", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Préparer les blancs", "Garnir d'amandes", "Accompagner de groseilles"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 300,
            "total_protein": 25,
            "total_carbs": 17,
            "total_fat": 12,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Blancs d'Œufs aux Noix de Pécan et Fruits Rouges",
            "category": "snack",
            "meal_type": "collation2",
            "ingredients": [
                {"name": "Blancs d'œufs", "quantity": 3, "unit": "unités"},
                {"name": "Noix de pécan", "quantity": 40, "unit": "g"},
                {"name": "Fruits rouges", "quantity": 50, "unit": "g"}
            ],
            "instructions": ["Cuire les blancs", "Ajouter noix de pécan", "Servir avec fruits rouges"],
            "prep_time": 5,
            "cook_time": 3,
            "servings": 1,
            "total_calories": 309,
            "total_protein": 24,
            "total_carbs": 18,
            "total_fat": 13,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        }
    ]
    
    # REPAS 3 - Dîner (15 recettes)
    dinner_recipes = [
        {
            "name": "Cabillaud en Papillote Classique",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Salade verte", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Citron", "quantity": 20, "unit": "g"}
            ],
            "instructions": ["Préparer la papillote", "Cuire au four 20 min", "Servir avec salade"],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 1,
            "total_calories": 270,
            "total_protein": 38,
            "total_carbs": 8,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": True,
            "chef_instructions": ["Papier sulfurisé bien fermé", "Four préchauffé à 180°C"],
            "cooking_steps": [
                {"step": 1, "title": "Préparation", "description": "Préparer la papillote avec citron", "duration_minutes": 5, "temperature": "Ambiante", "technique": "Pliage"},
                {"step": 2, "title": "Cuisson", "description": "Cuire au four en papillote", "duration_minutes": 15, "temperature": "180°C", "technique": "Papillote"}
            ],
            "chef_tips": [
                {"type": "tip", "title": "Papillote hermétique", "description": "Bien fermer pour garder la vapeur", "importance": "high"}
            ],
            "visual_cues": [
                {"step_number": 2, "description": "Papillote gonflée", "what_to_look_for": "Papier gonflé par la vapeur"}
            ],
            "timing_details": {"total_time": 25, "active_time": 10, "passive_time": 15},
            "media_references": []
        },
        {
            "name": "Sole Grillée à la Salade Verte",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de sole", "quantity": 200, "unit": "g"},
                {"name": "Salade mélangée", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Herbes", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Griller la sole", "Préparer la salade", "Assaisonner et servir"],
            "prep_time": 8,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 250,
            "total_protein": 36,
            "total_carbs": 6,
            "total_fat": 6,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Cabillaud aux Épinards",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Épinards", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Ail", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Cuire le cabillaud", "Faire tomber les épinards", "Servir ensemble"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 275,
            "total_protein": 39,
            "total_carbs": 8,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Sole aux Courgettes Vapeur",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de sole", "quantity": 200, "unit": "g"},
                {"name": "Courgettes", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Aneth", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Cuire la sole", "Cuire courgettes vapeur", "Assaisonner à l'aneth"],
            "prep_time": 8,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 255,
            "total_protein": 36,
            "total_carbs": 7,
            "total_fat": 6,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Cabillaud au Four aux Tomates Cerises",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Tomates cerises", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Basilic", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Disposer dans un plat", "Cuire au four 25 min", "Garnir de basilic frais"],
            "prep_time": 10,
            "cook_time": 20,
            "servings": 1,
            "total_calories": 278,
            "total_protein": 38,
            "total_carbs": 9,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Sole aux Haricots Verts",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de sole", "quantity": 200, "unit": "g"},
                {"name": "Haricots verts", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Persil", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Cuire la sole", "Cuire haricots verts", "Parsemer de persil"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 252,
            "total_protein": 36,
            "total_carbs": 7,
            "total_fat": 6,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Cabillaud Mariné aux Légumes Grillés",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Légumes grillés", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Thym", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Mariner le cabillaud", "Griller avec légumes", "Servir chaud"],
            "prep_time": 15,
            "cook_time": 20,
            "servings": 1,
            "total_calories": 280,
            "total_protein": 38,
            "total_carbs": 10,
            "total_fat": 7,
            "difficulty_level": "intermediate",
            "has_chef_mode": False
        },
        {
            "name": "Sole à la Provençale",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de sole", "quantity": 200, "unit": "g"},
                {"name": "Ratatouille", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Herbes de Provence", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Cuire la sole", "Réchauffer ratatouille", "Servir ensemble"],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 1,
            "total_calories": 258,
            "total_protein": 36,
            "total_carbs": 8,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Cabillaud aux Brocolis Vapeur",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Brocolis", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Citron", "quantity": 20, "unit": "g"}
            ],
            "instructions": ["Cuire cabillaud vapeur", "Cuire brocolis vapeur", "Arroser de citron"],
            "prep_time": 10,
            "cook_time": 12,
            "servings": 1,
            "total_calories": 272,
            "total_protein": 39,
            "total_carbs": 8,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Sole aux Champignons",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de sole", "quantity": 200, "unit": "g"},
                {"name": "Champignons", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Persil", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Faire sauter champignons", "Cuire la sole", "Garnir de persil"],
            "prep_time": 8,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 254,
            "total_protein": 37,
            "total_carbs": 7,
            "total_fat": 6,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Cabillaud à l'Asiatique",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Pak-choï", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Gingembre, soja", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Cuire cabillaud au gingembre", "Wok le pak-choï", "Arroser de soja"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 276,
            "total_protein": 38,
            "total_carbs": 9,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Sole aux Épinards et Ail",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de sole", "quantity": 200, "unit": "g"},
                {"name": "Épinards", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Ail", "quantity": 3, "unit": "g"}
            ],
            "instructions": ["Cuire la sole", "Faire sauter épinards à l'ail", "Servir ensemble"],
            "prep_time": 8,
            "cook_time": 7,
            "servings": 1,
            "total_calories": 253,
            "total_protein": 36,
            "total_carbs": 7,
            "total_fat": 6,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Cabillaud aux Poivrons",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Poivrons colorés", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Paprika", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Cuire cabillaud", "Faire revenir poivrons", "Saupoudrer de paprika"],
            "prep_time": 10,
            "cook_time": 15,
            "servings": 1,
            "total_calories": 274,
            "total_protein": 38,
            "total_carbs": 9,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        },
        {
            "name": "Sole en Croûte d'Herbes",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de sole", "quantity": 200, "unit": "g"},
                {"name": "Salade verte", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Herbes fraîches", "quantity": 5, "unit": "g"}
            ],
            "instructions": ["Enrober sole d'herbes", "Cuire au four", "Servir avec salade"],
            "prep_time": 10,
            "cook_time": 10,
            "servings": 1,
            "total_calories": 251,
            "total_protein": 36,
            "total_carbs": 6,
            "total_fat": 6,
            "difficulty_level": "intermediate",
            "has_chef_mode": False
        },
        {
            "name": "Cabillaud aux Légumes Méditerranéens",
            "category": "dinner",
            "meal_type": "repas3",
            "ingredients": [
                {"name": "Filet de cabillaud", "quantity": 200, "unit": "g"},
                {"name": "Mélange méditerranéen", "quantity": 100, "unit": "g"},
                {"name": "Huile d'olive", "quantity": 5, "unit": "g"},
                {"name": "Origan", "quantity": 2, "unit": "g"}
            ],
            "instructions": ["Cuire cabillaud au four", "Rôtir légumes", "Parfumer à l'origan"],
            "prep_time": 10,
            "cook_time": 20,
            "servings": 1,
            "total_calories": 279,
            "total_protein": 38,
            "total_carbs": 10,
            "total_fat": 7,
            "difficulty_level": "beginner",
            "has_chef_mode": False
        }
    ]
    
    # Combiner toutes les recettes
    recipes.extend(breakfast_recipes)
    recipes.extend(smoothie_recipes)
    recipes.extend(lunch_recipes)
    recipes.extend(snack2_recipes)
    recipes.extend(dinner_recipes)
    
    return recipes

def seed_recipes():
    """Fonction principale pour peupler la base de données"""
    
    # Configuration Flask
    app = Flask(__name__)
    
    # Déterminer l'environnement
    if os.environ.get('DATABASE_URL'):
        # Production
        os.environ['FLASK_ENV'] = 'production'
        from database.config import ProductionConfig
        app.config.from_object(ProductionConfig)
        print("🌐 Mode: Production")
    else:
        # Development
        from database.config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
        print("💻 Mode: Development")
    
    db.init_app(app)
    
    with app.app_context():
        print("\n🍳 Début du seeding des recettes...")
        
        # Vérifier les recettes existantes
        existing_count = Recipe.query.count()
        print(f"📊 Recettes existantes: {existing_count}")
        
        if existing_count > 2:
            print("⚠️  Il y a déjà plus de 2 recettes dans la base.")
            response = input("Voulez-vous les remplacer par les 65 nouvelles recettes? (oui/non): ")
            if response.lower() != 'oui':
                print("❌ Seeding annulé")
                return
            else:
                print("🗑️  Suppression des recettes existantes...")
                Recipe.query.delete()
                db.session.commit()
        
        # Créer les ingrédients si nécessaire
        print("\n🥗 Vérification des ingrédients...")
        ingredients_needed = [
            "Blancs d'œufs", "Noix de cajou", "Amandes", "Épices", "Épinards frais",
            "Herbes de Provence", "Champignons", "Tomates cerises", "Ciboulette fraîche",
            "Courgettes", "Poivrons", "Ail", "Paprika", "Roquette", "Brocolis",
            "Basilic", "Origan", "Lait d'amande", "Avoine", "Ananas", "Chocolat noir",
            "Mangue", "Banane", "Fruits rouges", "Blanc de poulet", "Escalope de dinde",
            "Haricots verts", "Aubergines", "Curry", "Asperges vertes", "Épices tandoori",
            "Estragon", "Paprika fumé", "Pak-choï", "Gingembre", "Myrtilles", "Framboises",
            "Fraises", "Mûres", "Noisettes", "Cassis", "Pistaches", "Groseilles",
            "Noix de pécan", "Filet de cabillaud", "Filet de sole", "Salade verte",
            "Citron", "Aneth", "Persil", "Thym", "Ratatouille"
        ]
        
        for ing_name in ingredients_needed:
            existing = Ingredient.query.filter_by(name=ing_name).first()
            if not existing:
                ingredient = Ingredient(
                    name=ing_name,
                    category="Divers",
                    calories_per_100g=100,  # Valeurs par défaut
                    protein_per_100g=10,
                    carbs_per_100g=10,
                    fat_per_100g=5
                )
                db.session.add(ingredient)
        
        db.session.commit()
        print(f"✅ {len(ingredients_needed)} ingrédients vérifiés/créés")
        
        # Créer les recettes
        recipes_data = create_recipes_data()
        print(f"\n📝 Création de {len(recipes_data)} recettes...")
        
        created_count = 0
        for recipe_data in recipes_data:
            try:
                # Extraire les données spécifiques au mode chef
                chef_data = {}
                if recipe_data.get('has_chef_mode'):
                    chef_data = {
                        'chef_instructions_json': json.dumps(recipe_data.get('chef_instructions', [])),
                        'cooking_steps_json': json.dumps(recipe_data.get('cooking_steps', [])),
                        'chef_tips_json': json.dumps(recipe_data.get('chef_tips', [])),
                        'visual_cues_json': json.dumps(recipe_data.get('visual_cues', [])),
                        'timing_details_json': json.dumps(recipe_data.get('timing_details', {})),
                        'media_references_json': json.dumps(recipe_data.get('media_references', []))
                    }
                
                # Créer la recette
                recipe = Recipe(
                    name=recipe_data['name'],
                    category=recipe_data['category'],
                    meal_type=recipe_data['meal_type'],
                    ingredients_json=json.dumps(recipe_data.get('ingredients', [])),
                    instructions_json=json.dumps(recipe_data['instructions']),
                    prep_time=recipe_data['prep_time'],
                    cook_time=recipe_data['cook_time'],
                    servings=recipe_data['servings'],
                    total_calories=recipe_data['total_calories'],
                    total_protein=recipe_data['total_protein'],
                    total_carbs=recipe_data['total_carbs'],
                    total_fat=recipe_data['total_fat'],
                    difficulty_level=recipe_data['difficulty_level'],
                    has_chef_mode=recipe_data.get('has_chef_mode', False),
                    **chef_data
                )
                
                db.session.add(recipe)
                created_count += 1
                
                if created_count % 10 == 0:
                    print(f"  📍 {created_count} recettes créées...")
                    
            except Exception as e:
                print(f"❌ Erreur création recette {recipe_data['name']}: {e}")
                continue
        
        # Commit final
        try:
            db.session.commit()
            print(f"\n✅ {created_count} recettes créées avec succès!")
            
            # Statistiques finales
            print("\n📊 Statistiques finales:")
            for meal_type in ['repas1', 'collation1', 'repas2', 'collation2', 'repas3']:
                count = Recipe.query.filter_by(meal_type=meal_type).count()
                print(f"  - {meal_type}: {count} recettes")
            
            chef_count = Recipe.query.filter_by(has_chef_mode=True).count()
            print(f"  - Recettes avec mode chef: {chef_count}")
            
        except Exception as e:
            print(f"❌ Erreur lors du commit: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("=" * 50)
    print("🍽️  SEEDING DES 65 RECETTES DIETTRACKER")
    print("=" * 50)
    
    seed_recipes()
    
    print("\n🎉 Script terminé!")