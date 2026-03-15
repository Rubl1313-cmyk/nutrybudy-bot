export interface MacroTargets {
  calories?: number;
  protein?: number;
  carbs?: number;
  fats?: number;
}

export interface UserProfile {
  userId: string;
  heightCm?: number;
  weightKg?: number;
  age?: number;
  sex?: 'male' | 'female' | 'other';
  goal?: 'lose' | 'maintain' | 'gain';
  activityLevel?: 'sedentary' | 'light' | 'moderate' | 'high';
  bmr?: number;
  tdee?: number;
  macroTargets?: MacroTargets;
  hydrationMl?: number;
}

export interface MealLog {
  id: string;
  timestamp: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fats?: number;
  text?: string;
  imageUrl?: string;
}

export interface DailySummary {
  date: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fats?: number;
  waterMl?: number;
  steps?: number;
  activeMinutes?: number;
}
