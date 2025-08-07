/**
 * Utilitaires de validation côté frontend - US1.7
 * Validations en temps réel pour l'interface utilisateur
 */

// Configuration des contraintes
export const VALIDATION_CONSTRAINTS = {
  weight: { min: 20, max: 500, step: 0.1 },
  height: { min: 50, max: 300, step: 1 },
  age: { min: 10, max: 120 },
  bodyFat: { min: 0, max: 100, step: 0.1 },
  calories: { min: 800, max: 5000 },
  protein: { min: 10, max: 300 },
  carbs: { min: 20, max: 500 },
  fat: { min: 10, max: 200 },
  fiber: { min: 5, max: 100 },
  water: { min: 1000, max: 5000 }
};

// Types d'erreurs
export const ERROR_TYPES = {
  REQUIRED: 'required',
  MIN_VALUE: 'min_value',
  MAX_VALUE: 'max_value',
  INVALID_FORMAT: 'invalid_format',
  INVALID_DATE: 'invalid_date',
  FUTURE_DATE: 'future_date',
  INCONSISTENT: 'inconsistent',
  UNUSUAL: 'unusual'
};

// Messages d'erreur localisés
export const ERROR_MESSAGES = {
  [ERROR_TYPES.REQUIRED]: 'Ce champ est requis',
  [ERROR_TYPES.MIN_VALUE]: (field, min) => `${field} doit être supérieur à ${min}`,
  [ERROR_TYPES.MAX_VALUE]: (field, max) => `${field} doit être inférieur à ${max}`,
  [ERROR_TYPES.INVALID_FORMAT]: (field) => `Format ${field} invalide`,
  [ERROR_TYPES.INVALID_DATE]: 'Format de date invalide',
  [ERROR_TYPES.FUTURE_DATE]: 'La date ne peut pas être dans le futur',
  [ERROR_TYPES.INCONSISTENT]: 'Valeurs incohérentes',
  [ERROR_TYPES.UNUSUAL]: 'Valeur inhabituelle'
};

/**
 * Classe de résultat de validation
 */
export class ValidationResult {
  constructor() {
    this.isValid = true;
    this.errors = [];
    this.warnings = [];
    this.fieldErrors = {};
  }

  addError(field, message, type = ERROR_TYPES.INVALID_FORMAT, value = null) {
    this.errors.push({ field, message, type, value });
    this.fieldErrors[field] = this.fieldErrors[field] || [];
    this.fieldErrors[field].push({ message, type, value });
    this.isValid = false;
  }

  addWarning(field, message, type = ERROR_TYPES.UNUSUAL, value = null) {
    this.warnings.push({ field, message, type, value });
  }

  hasFieldError(field) {
    return !!this.fieldErrors[field];
  }

  getFieldError(field) {
    return this.fieldErrors[field]?.[0]?.message || null;
  }

  getAllErrors() {
    return this.errors.map(error => error.message);
  }

  getAllWarnings() {
    return this.warnings.map(warning => warning.message);
  }
}

/**
 * Validateur pour les nombres
 */
export const NumberValidator = {
  validate(value, constraints, fieldName) {
    const result = new ValidationResult();

    if (value === null || value === undefined || value === '') {
      return result; // Null/undefined est acceptable pour les champs optionnels
    }

    const numValue = parseFloat(value);
    
    if (isNaN(numValue)) {
      result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.INVALID_FORMAT](fieldName), ERROR_TYPES.INVALID_FORMAT, value);
      return result;
    }

    if (constraints.min !== undefined && numValue < constraints.min) {
      result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.MIN_VALUE](fieldName, constraints.min), ERROR_TYPES.MIN_VALUE, numValue);
    }

    if (constraints.max !== undefined && numValue > constraints.max) {
      result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.MAX_VALUE](fieldName, constraints.max), ERROR_TYPES.MAX_VALUE, numValue);
    }

    return result;
  }
};

/**
 * Validateur pour les dates
 */
export const DateValidator = {
  validate(dateString, fieldName, allowFuture = false) {
    const result = new ValidationResult();

    if (!dateString) {
      return result; // Date vide acceptable pour champs optionnels
    }

    try {
      const date = new Date(dateString);
      
      if (isNaN(date.getTime())) {
        result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.INVALID_DATE], ERROR_TYPES.INVALID_DATE, dateString);
        return result;
      }

      if (!allowFuture && date > new Date()) {
        result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.FUTURE_DATE], ERROR_TYPES.FUTURE_DATE, dateString);
      }

      // Vérifier que l'âge calculé est raisonnable pour les dates de naissance
      if (fieldName === 'birth_date' || fieldName === 'birthDate') {
        const today = new Date();
        const age = Math.floor((today - date) / (365.25 * 24 * 60 * 60 * 1000));
        
        if (age < VALIDATION_CONSTRAINTS.age.min) {
          result.addError(fieldName, `Âge trop faible (${age} ans)`, ERROR_TYPES.MIN_VALUE, age);
        } else if (age > VALIDATION_CONSTRAINTS.age.max) {
          result.addError(fieldName, `Âge trop élevé (${age} ans)`, ERROR_TYPES.MAX_VALUE, age);
        }
      }

    } catch (error) {
      result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.INVALID_DATE], ERROR_TYPES.INVALID_DATE, dateString);
    }

    return result;
  }
};

/**
 * Validateur pour l'email
 */
export const EmailValidator = {
  validate(email, fieldName = 'email') {
    const result = new ValidationResult();

    if (!email) {
      return result; // Email vide acceptable si pas requis
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
      result.addError(fieldName, 'Format d\'email invalide', ERROR_TYPES.INVALID_FORMAT, email);
    }

    return result;
  }
};

/**
 * Validateur pour les profils utilisateur
 */
export class ProfileValidator {
  static validateWeight(weight, fieldName = 'weight', required = false) {
    const result = new ValidationResult();

    if (required && (!weight && weight !== 0)) {
      result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.REQUIRED], ERROR_TYPES.REQUIRED);
      return result;
    }

    if (!weight && weight !== 0) return result;

    const numberResult = NumberValidator.validate(weight, VALIDATION_CONSTRAINTS.weight, fieldName);
    result.errors.push(...numberResult.errors);
    result.warnings.push(...numberResult.warnings);
    result.fieldErrors = { ...result.fieldErrors, ...numberResult.fieldErrors };
    result.isValid = result.isValid && numberResult.isValid;

    // Avertissements pour valeurs inhabituelles
    const numWeight = parseFloat(weight);
    if (!isNaN(numWeight)) {
      if (numWeight < 40 || numWeight > 200) {
        result.addWarning(fieldName, 'Poids inhabituel - vérifiez la valeur', ERROR_TYPES.UNUSUAL, numWeight);
      }
    }

    return result;
  }

  static validateHeight(height, fieldName = 'height', required = false) {
    const result = new ValidationResult();

    if (required && (!height && height !== 0)) {
      result.addError(fieldName, ERROR_MESSAGES[ERROR_TYPES.REQUIRED], ERROR_TYPES.REQUIRED);
      return result;
    }

    if (!height && height !== 0) return result;

    const numberResult = NumberValidator.validate(height, VALIDATION_CONSTRAINTS.height, fieldName);
    result.errors.push(...numberResult.errors);
    result.warnings.push(...numberResult.warnings);
    result.fieldErrors = { ...result.fieldErrors, ...numberResult.fieldErrors };
    result.isValid = result.isValid && numberResult.isValid;

    // Avertissements pour valeurs inhabituelles
    const numHeight = parseFloat(height);
    if (!isNaN(numHeight)) {
      if (numHeight < 120 || numHeight > 220) {
        result.addWarning(fieldName, 'Taille inhabituelle - vérifiez la valeur', ERROR_TYPES.UNUSUAL, numHeight);
      }
    }

    return result;
  }

  static validateAge(age, fieldName = 'age') {
    const result = new ValidationResult();

    if (!age && age !== 0) return result;

    const numberResult = NumberValidator.validate(age, VALIDATION_CONSTRAINTS.age, fieldName);
    result.errors.push(...numberResult.errors);
    result.warnings.push(...numberResult.warnings);
    result.fieldErrors = { ...result.fieldErrors, ...numberResult.fieldErrors };
    result.isValid = result.isValid && numberResult.isValid;

    return result;
  }

  static validateBodyFatPercentage(bodyFat, fieldName = 'bodyFatPercentage') {
    const result = new ValidationResult();

    if (!bodyFat && bodyFat !== 0) return result;

    const numberResult = NumberValidator.validate(bodyFat, VALIDATION_CONSTRAINTS.bodyFat, fieldName);
    result.errors.push(...numberResult.errors);
    result.warnings.push(...numberResult.warnings);
    result.fieldErrors = { ...result.fieldErrors, ...numberResult.fieldErrors };
    result.isValid = result.isValid && numberResult.isValid;

    return result;
  }

  static validateGender(gender, fieldName = 'gender') {
    const result = new ValidationResult();

    if (!gender) return result;

    const validGenders = ['male', 'female', 'other', 'prefer_not_to_say'];
    if (!validGenders.includes(gender)) {
      result.addError(fieldName, 'Genre invalide', ERROR_TYPES.INVALID_FORMAT, gender);
    }

    return result;
  }

  static validateActivityLevel(activityLevel, fieldName = 'activityLevel') {
    const result = new ValidationResult();

    if (!activityLevel) return result;

    const validLevels = [
      'sedentary', 'lightly_active', 'moderately_active', 
      'very_active', 'extremely_active'
    ];

    if (!validLevels.includes(activityLevel)) {
      result.addError(fieldName, 'Niveau d\'activité invalide', ERROR_TYPES.INVALID_FORMAT, activityLevel);
    }

    return result;
  }

  static validateWeightGoals(currentWeight, targetWeight) {
    const result = new ValidationResult();

    if (!currentWeight || !targetWeight) return result;

    const current = parseFloat(currentWeight);
    const target = parseFloat(targetWeight);

    if (isNaN(current) || isNaN(target)) return result;

    const difference = Math.abs(current - target);

    // Avertir si l'objectif est trop extrême
    if (difference > 50) {
      result.addWarning('targetWeight', 
        `Différence importante entre poids actuel et objectif (${difference.toFixed(1)} kg)`, 
        ERROR_TYPES.UNUSUAL, 
        difference);
    }

    // Avertir si l'objectif semble peu réaliste
    if (target < 40 || target > 200) {
      result.addWarning('targetWeight', 'Poids objectif inhabituel', ERROR_TYPES.UNUSUAL, target);
    }

    return result;
  }

  static validateCompleteProfile(profileData) {
    const result = new ValidationResult();

    // Validation des champs individuels
    const validations = [
      this.validateWeight(profileData.currentWeight, 'currentWeight', true),
      this.validateWeight(profileData.targetWeight, 'targetWeight', true),
      this.validateHeight(profileData.height, 'height', true),
      this.validateAge(profileData.age, 'age'),
      DateValidator.validate(profileData.birthDate, 'birthDate'),
      this.validateGender(profileData.gender, 'gender'),
      this.validateActivityLevel(profileData.activityLevel, 'activityLevel'),
      EmailValidator.validate(profileData.email, 'email'),
      this.validateBodyFatPercentage(profileData.bodyFatPercentage, 'bodyFatPercentage')
    ];

    // Consolider tous les résultats
    for (const validation of validations) {
      result.errors.push(...validation.errors);
      result.warnings.push(...validation.warnings);
      Object.assign(result.fieldErrors, validation.fieldErrors);
      result.isValid = result.isValid && validation.isValid;
    }

    // Validation de la cohérence des objectifs
    const goalValidation = this.validateWeightGoals(profileData.currentWeight, profileData.targetWeight);
    result.warnings.push(...goalValidation.warnings);

    return result;
  }
}

/**
 * Validateur pour les pesées
 */
export class WeightEntryValidator {
  static validate(weightData) {
    const result = new ValidationResult();

    // Poids obligatoire
    const weightResult = ProfileValidator.validateWeight(weightData.weight, 'weight', true);
    result.errors.push(...weightResult.errors);
    result.warnings.push(...weightResult.warnings);
    Object.assign(result.fieldErrors, weightResult.fieldErrors);
    result.isValid = result.isValid && weightResult.isValid;

    // Date optionnelle mais si présente doit être valide
    if (weightData.recordedDate) {
      const dateResult = DateValidator.validate(weightData.recordedDate, 'recordedDate');
      result.errors.push(...dateResult.errors);
      result.warnings.push(...dateResult.warnings);
      Object.assign(result.fieldErrors, dateResult.fieldErrors);
      result.isValid = result.isValid && dateResult.isValid;
    }

    // Métriques corporelles optionnelles
    if (weightData.bodyFatPercentage) {
      const bodyFatResult = ProfileValidator.validateBodyFatPercentage(weightData.bodyFatPercentage, 'bodyFatPercentage');
      result.errors.push(...bodyFatResult.errors);
      result.warnings.push(...bodyFatResult.warnings);
      Object.assign(result.fieldErrors, bodyFatResult.fieldErrors);
      result.isValid = result.isValid && bodyFatResult.isValid;
    }

    // Validation des notes (longueur max)
    if (weightData.notes && weightData.notes.length > 500) {
      result.addError('notes', 'Les notes ne peuvent pas dépasser 500 caractères', ERROR_TYPES.MAX_VALUE, weightData.notes.length);
    }

    return result;
  }
}

/**
 * Validateur pour les objectifs nutritionnels
 */
export class NutritionTargetValidator {
  static validate(nutritionData) {
    const result = new ValidationResult();

    const fields = [
      { key: 'calories', constraint: VALIDATION_CONSTRAINTS.calories, label: 'Calories' },
      { key: 'protein', constraint: VALIDATION_CONSTRAINTS.protein, label: 'Protéines' },
      { key: 'carbs', constraint: VALIDATION_CONSTRAINTS.carbs, label: 'Glucides' },
      { key: 'fat', constraint: VALIDATION_CONSTRAINTS.fat, label: 'Lipides' },
      { key: 'fiber', constraint: VALIDATION_CONSTRAINTS.fiber, label: 'Fibres' },
      { key: 'water', constraint: VALIDATION_CONSTRAINTS.water, label: 'Eau' }
    ];

    for (const field of fields) {
      if (nutritionData[field.key] !== undefined && nutritionData[field.key] !== null) {
        const fieldResult = NumberValidator.validate(nutritionData[field.key], field.constraint, field.label);
        result.errors.push(...fieldResult.errors);
        result.warnings.push(...fieldResult.warnings);
        Object.assign(result.fieldErrors, fieldResult.fieldErrors);
        result.isValid = result.isValid && fieldResult.isValid;

        // Avertissements pour valeurs inhabituelles
        const value = parseFloat(nutritionData[field.key]);
        if (!isNaN(value)) {
          const isUnusual = this.checkUnusualValue(field.key, value);
          if (isUnusual) {
            result.addWarning(field.key, `${field.label} inhabituelle (${value})`, ERROR_TYPES.UNUSUAL, value);
          }
        }
      }
    }

    return result;
  }

  static checkUnusualValue(field, value) {
    const unusualRanges = {
      calories: { low: 1000, high: 4000 },
      protein: { low: 30, high: 250 },
      carbs: { low: 50, high: 400 },
      fat: { low: 20, high: 150 },
      fiber: { low: 15, high: 60 },
      water: { low: 1500, high: 4000 }
    };

    const range = unusualRanges[field];
    return range && (value < range.low || value > range.high);
  }

  static validateMacroConsistency(calories, protein, carbs, fat) {
    const result = new ValidationResult();

    if (!calories || !protein || !carbs || !fat) return result;

    const calculatedCalories = (protein * 4) + (carbs * 4) + (fat * 9);
    const difference = Math.abs(calories - calculatedCalories);
    const tolerancePercent = 10; // 10% de tolérance
    const tolerance = calories * (tolerancePercent / 100);

    if (difference > tolerance) {
      result.addWarning('macros', 
        `Incohérence entre calories (${calories}) et macronutriments (${Math.round(calculatedCalories)} calculées)`, 
        ERROR_TYPES.INCONSISTENT, 
        { calories, calculatedCalories });
    }

    return result;
  }
}

/**
 * Utilitaires pour la validation en temps réel
 */
export const ValidationUtils = {
  /**
   * Débounce pour la validation en temps réel
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  /**
   * Valide un champ spécifique selon son type
   */
  validateField(fieldName, value, constraints = {}) {
    switch (fieldName) {
      case 'weight':
      case 'currentWeight':
      case 'targetWeight':
        return ProfileValidator.validateWeight(value, fieldName, constraints.required);
      
      case 'height':
        return ProfileValidator.validateHeight(value, fieldName, constraints.required);
      
      case 'age':
        return ProfileValidator.validateAge(value, fieldName);
      
      case 'birthDate':
        return DateValidator.validate(value, fieldName);
      
      case 'email':
        return EmailValidator.validate(value, fieldName);
      
      case 'gender':
        return ProfileValidator.validateGender(value, fieldName);
      
      case 'activityLevel':
        return ProfileValidator.validateActivityLevel(value, fieldName);
      
      case 'bodyFatPercentage':
        return ProfileValidator.validateBodyFatPercentage(value, fieldName);
      
      default:
        return new ValidationResult(); // Pas d'erreur pour champs non reconnus
    }
  },

  /**
   * Formate les erreurs pour l'affichage
   */
  formatErrorsForDisplay(validationResult) {
    return {
      hasErrors: !validationResult.isValid,
      hasWarnings: validationResult.warnings.length > 0,
      fieldErrors: validationResult.fieldErrors,
      allErrors: validationResult.getAllErrors(),
      allWarnings: validationResult.getAllWarnings()
    };
  },

  /**
   * Validation progressive pour un formulaire
   */
  validateFormProgressive(formData, fieldsToValidate = null) {
    const result = new ValidationResult();
    const fields = fieldsToValidate || Object.keys(formData);

    for (const fieldName of fields) {
      const fieldResult = this.validateField(fieldName, formData[fieldName]);
      result.errors.push(...fieldResult.errors);
      result.warnings.push(...fieldResult.warnings);
      Object.assign(result.fieldErrors, fieldResult.fieldErrors);
      result.isValid = result.isValid && fieldResult.isValid;
    }

    return result;
  }
};

export default {
  ProfileValidator,
  WeightEntryValidator,
  NutritionTargetValidator,
  ValidationUtils,
  VALIDATION_CONSTRAINTS,
  ERROR_TYPES,
  ERROR_MESSAGES
};