"""
Calorie calculator and nutrition norms for NutriBuddy
✅ Verified by reliable sources:
- Mifflin-St Jeor Equation (1990) - gold standard
- WHO/FAO recommendations
- USDA Dietary Guidelines
"""
from typing import Tuple


def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """
    Calculates basal metabolic rate (BMR) using Mifflin-St Jeor formula.
    
    Formula (Mifflin et al., 1990):
    - Men: BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age(years) + 5
    - Women: BMR = 10 × weight(kg) + 6.25 × height(cm) − 5 × age(years) − 161
    
    Source: 
    Mifflin, M. D., St Jeor, S. T., Hill, L. A., Scott, B. J., Daugherty, S. A., 
    & Koh, Y. O. (1990). A new predictive equation for resting energy expenditure 
    in healthy individuals. The American Journal of Clinical Nutrition, 51(2), 241-247.
    
    Returns:
        float: BMR in kcal/day
    """
    if gender == "male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    return round(bmr, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculates total daily energy expenditure (TDEE) considering activity.
    
    Activity coefficients (Harris-Benedict):
    - low (sedentary): BMR × 1.2
    - medium (moderate): BMR × 1.55
    - high (active): BMR × 1.725
    
    Source:
    Harris, J. A., & Benedict, F. G. (1918). A Biometric Study of Human Basal Metabolism.
    Proceedings of the National Academy of Sciences, 4(12), 370-373.
    
    Returns:
        float: TDEE in kcal/day
    """
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    
    multiplier = activity_multipliers.get(activity_level, 1.55)  # default to moderate
    tdee = bmr * multiplier
    
    return round(tdee, 1)


def calculate_calorie_goal(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str
) -> Tuple[float, float, float, float]:
    """
    Calculates daily calorie and macronutrient goals.
    
    Args:
        weight: Weight in kg
        height: Height in cm
        age: Age in years
        gender: "male" or "female"
        activity_level: "sedentary", "light", "moderate", "active", "very_active"
        goal: "lose_weight", "gain_weight", "maintenance"
    
    Returns:
        Tuple of (calories, protein_g, fat_g, carbs_g)
    """
    # Calculate BMR and TDEE
    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    
    # Adjust calories based on goal
    if goal == "lose_weight":
        # Deficit of 500 kcal/day for ~0.5 kg/week weight loss
        calories = tdee - 500
    elif goal == "gain_weight":
        # Surplus of 300-500 kcal/day for lean mass gain
        calories = tdee + 400
    else:  # maintenance
        calories = tdee
    
    # Ensure minimum safe calorie levels
    if gender == "male":
        calories = max(calories, 1500)  # Minimum for men
    else:
        calories = max(calories, 1200)  # Minimum for women
    
    # Calculate protein based on body weight and goal
    if goal == "gain_weight":
        protein_per_kg = 2.0  # Higher protein for muscle gain
    elif goal == "lose_weight":
        protein_per_kg = 2.2  # Higher protein to preserve muscle during deficit
    else:
        protein_per_kg = 1.6  # Standard recommendation
    
    protein_g = round(weight * protein_per_kg, 1)
    
    # Calculate fat (20-35% of total calories)
    fat_percentage = 0.25  # 25% of calories from fat
    fat_calories = calories * fat_percentage
    fat_g = round(fat_calories / 9, 1)  # 9 kcal per gram of fat
    
    # Calculate carbs (remaining calories)
    protein_calories = protein_g * 4  # 4 kcal per gram of protein
    carbs_calories = calories - protein_calories - fat_calories
    carbs_g = round(carbs_calories / 4, 1)  # 4 kcal per gram of carbs
    
    return round(calories), protein_g, fat_g, carbs_g


def calculate_water_goal(
    weight: float,
    activity_level: str,
    temperature: float = 20.0,
    goal: str = "maintenance",
    gender: str = "male"
) -> int:
    """
    Calculates daily water intake goal.
    
    Args:
        weight: Weight in kg
        activity_level: Activity level
        temperature: Temperature in Celsius
        goal: Fitness goal
        gender: "male" or "female"
    
    Returns:
        int: Water goal in ml
    """
    # Base water requirement: 30-35 ml per kg body weight
    base_water = weight * 33  # ml/kg
    
    # Adjust for activity level
    activity_adjustments = {
        "sedentary": 0.0,
        "light": 500,      # +500ml for light activity
        "moderate": 1000,  # +1000ml for moderate activity
        "active": 1500,    # +1500ml for active lifestyle
        "very_active": 2000  # +2000ml for very active
    }
    
    water_intake = base_water + activity_adjustments.get(activity_level, 0)
    
    # Temperature adjustment (for hot weather)
    if temperature > 25:
        temp_adjustment = (temperature - 25) * 100  # +100ml per degree above 25°C
        water_intake += temp_adjustment
    
    # Goal adjustments
    if goal == "lose_weight":
        water_intake += 500  # Extra water for weight loss
    elif goal == "gain_weight":
        water_intake += 300  # Slightly more for muscle building
    
    # Gender adjustments
    if gender == "male":
        water_intake *= 1.1  # Men typically need more water
    
    # Round to nearest 100ml
    water_goal = int(round(water_intake / 100) * 100)
    
    # Set reasonable limits
    water_goal = max(water_goal, 1500)   # Minimum 1.5L
    water_goal = min(water_goal, 6000)   # Maximum 6L
    
    return water_goal


def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculates Body Mass Index (BMI).
    
    Args:
        weight: Weight in kg
        height: Height in cm
    
    Returns:
        float: BMI value
    """
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    
    return round(bmi, 1)


def get_bmi_category(bmi: float) -> str:
    """
    Gets BMI category according to WHO classification.
    
    Args:
        bmi: BMI value
    
    Returns:
        str: BMI category
    """
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"


def calculate_ideal_weight(height: float, gender: str) -> Tuple[float, float]:
    """
    Calculates ideal weight range using Devine formula.
    
    Args:
        height: Height in cm
        gender: "male" or "female"
    
    Returns:
        Tuple of (min_ideal_weight, max_ideal_weight)
    """
    if gender == "male":
        # Devine formula for men: 50kg + 2.3kg per inch over 5 feet
        base_weight = 50.0
        height_in_inches = (height / 2.54) - 60  # Convert to inches and subtract 5 feet
    else:
        # Devine formula for women: 45.5kg + 2.3kg per inch over 5 feet
        base_weight = 45.5
        height_in_inches = (height / 2.54) - 60
    
    ideal_weight = base_weight + (2.3 * height_in_inches)
    
    # Create range (±10%)
    min_weight = ideal_weight * 0.9
    max_weight = ideal_weight * 1.1
    
    return round(min_weight, 1), round(max_weight, 1)


def calculate_body_fat_percentage(weight: float, height: float, age: int, gender: str) -> float:
    """
    Estimates body fat percentage using BMI method (Deurenberg formula).
    
    Args:
        weight: Weight in kg
        height: Height in cm
        age: Age in years
        gender: "male" or "female"
    
    Returns:
        float: Estimated body fat percentage
    """
    bmi = calculate_bmi(weight, height)
    
    if gender == "male":
        # Deurenberg formula for men
        body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
    else:
        # Deurenberg formula for women
        body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
    
    return max(0, round(body_fat, 1))


def get_body_fat_category(age: int, gender: str, body_fat: float) -> str:
    """
    Gets body fat category based on age and gender.
    
    Args:
        age: Age in years
        gender: "male" or "female"
        body_fat: Body fat percentage
    
    Returns:
        str: Body fat category
    """
    if gender == "male":
        if age < 30:
            if body_fat < 8: return "essential_fat"
            elif body_fat < 15: return "athletic"
            elif body_fat < 20: return "fitness"
            elif body_fat < 25: return "average"
            else: return "obese"
        elif age < 40:
            if body_fat < 11: return "essential_fat"
            elif body_fat < 17: return "athletic"
            elif body_fat < 22: return "fitness"
            elif body_fat < 27: return "average"
            else: return "obese"
        else:
            if body_fat < 13: return "essential_fat"
            elif body_fat < 19: return "athletic"
            elif body_fat < 24: return "fitness"
            elif body_fat < 29: return "average"
            else: return "obese"
    else:  # female
        if age < 30:
            if body_fat < 21: return "essential_fat"
            elif body_fat < 24: return "athletic"
            elif body_fat < 28: return "fitness"
            elif body_fat < 32: return "average"
            else: return "obese"
        elif age < 40:
            if body_fat < 23: return "essential_fat"
            elif body_fat < 26: return "athletic"
            elif body_fat < 30: return "fitness"
            elif body_fat < 34: return "average"
            else: return "obese"
        else:
            if body_fat < 25: return "essential_fat"
            elif body_fat < 28: return "athletic"
            elif body_fat < 32: return "fitness"
            elif body_fat < 36: return "average"
            else: return "obese"


def calculate_lean_body_mass(weight: float, body_fat_percentage: float) -> float:
    """
    Calculates lean body mass.
    
    Args:
        weight: Weight in kg
        body_fat_percentage: Body fat percentage
    
    Returns:
        float: Lean body mass in kg
    """
    fat_mass = weight * (body_fat_percentage / 100)
    lean_mass = weight - fat_mass
    
    return round(lean_mass, 1)


def calculate_calorie_burn_rate(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str
) -> Dict[str, float]:
    """
    Calculates calorie burn rate for different activities.
    
    Args:
        weight: Weight in kg
        height: Height in cm
        age: Age in years
        gender: "male" or "female"
        activity_level: Activity level
    
    Returns:
        Dict with activity burn rates (kcal per hour)
    """
    bmr = calculate_bmr(weight, height, age, gender)
    
    # MET values (Metabolic Equivalent of Task)
    activities = {
        "resting": 1.0,      # Sitting, resting
        "walking": 3.5,      # Moderate walking
        "running": 8.0,      # Running
        "cycling": 6.0,      # Moderate cycling
        "swimming": 7.0,     # Moderate swimming
        "strength": 6.0,     # Weight training
        "yoga": 2.5,         # Yoga
        "dancing": 4.5,      # Social dancing
        "cleaning": 3.0,     # House cleaning
        "gardening": 4.0,    # Gardening
    }
    
    # Calculate calories per hour for each activity
    burn_rates = {}
    for activity, met_value in activities.items():
        # Calories per hour = BMR × MET value ÷ 24
        calories_per_hour = (bmr * met_value) / 24
        burn_rates[activity] = round(calories_per_hour, 1)
    
    return burn_rates


def calculate_weight_change_timeline(
    current_weight: float,
    target_weight: float,
    daily_calorie_difference: int
) -> Dict[str, any]:
    """
    Calculates timeline for weight change.
    
    Args:
        current_weight: Current weight in kg
        target_weight: Target weight in kg
        daily_calorie_difference: Daily calorie difference (+ for surplus, - for deficit)
    
    Returns:
        Dict with timeline information
    """
    weight_difference = target_weight - current_weight
    
    # 7700 kcal = 1 kg of body weight
    total_calorie_difference = abs(weight_difference) * 7700
    
    if daily_calorie_difference == 0:
        return {
            "days_to_goal": float('inf'),
            "weeks_to_goal": float('inf'),
            "months_to_goal": float('inf'),
            "daily_weight_change": 0,
            "weekly_weight_change": 0
        }
    
    days_to_goal = total_calorie_difference / abs(daily_calorie_difference)
    daily_weight_change = daily_calorie_difference / 7700  # kg per day
    
    return {
        "days_to_goal": round(days_to_goal, 1),
        "weeks_to_goal": round(days_to_goal / 7, 1),
        "months_to_goal": round(days_to_goal / 30, 1),
        "daily_weight_change": round(daily_weight_change, 3),
        "weekly_weight_change": round(daily_weight_change * 7, 2)
    }


def get_nutrition_recommendations(
    calories: float,
    protein: float,
    fat: float,
    carbs: float
) -> Dict[str, str]:
    """
    Gets nutrition recommendations based on calculated goals.
    
    Args:
        calories: Daily calorie goal
        protein: Daily protein goal in grams
        fat: Daily fat goal in grams
        carbs: Daily carbs goal in grams
    
    Returns:
        Dict with recommendations
    """
    recommendations = {}
    
    # Protein recommendations
    if protein < 50:
        recommendations["protein"] = "Consider increasing protein intake for better muscle maintenance"
    elif protein > 200:
        recommendations["protein"] = "Very high protein intake - ensure adequate hydration"
    else:
        recommendations["protein"] = "Protein intake is within recommended range"
    
    # Fat recommendations
    fat_percentage = (fat * 9) / calories * 100
    if fat_percentage < 20:
        recommendations["fat"] = "Fat intake is low - consider healthy fats for hormone production"
    elif fat_percentage > 35:
        recommendations["fat"] = "Fat intake is high - consider reducing saturated fats"
    else:
        recommendations["fat"] = "Fat intake is within recommended range"
    
    # Carbs recommendations
    carbs_percentage = (carbs * 4) / calories * 100
    if carbs_percentage < 45:
        recommendations["carbs"] = "Low carb approach - ensure adequate fiber intake"
    elif carbs_percentage > 65:
        recommendations["carbs"] = "High carb intake - focus on complex carbohydrates"
    else:
        recommendations["carbs"] = "Carb intake is within recommended range"
    
    # Overall recommendations
    if calories < 1200:
        recommendations["overall"] = "Very low calorie intake - consult with nutritionist"
    elif calories > 4000:
        recommendations["overall"] = "Very high calorie intake - ensure balanced nutrition"
    else:
        recommendations["overall"] = "Calorie intake is appropriate for weight management"
    
    return recommendations


# =============================================================================
# 🎯 UTILITY FUNCTIONS
# =============================================================================
def format_nutrition_goals(calories: float, protein: float, fat: float, carbs: float) -> str:
    """
    Formats nutrition goals into readable string.
    
    Args:
        calories: Daily calorie goal
        protein: Daily protein goal in grams
        fat: Daily fat goal in grams
        carbs: Daily carbs goal in grams
    
    Returns:
        str: Formatted nutrition goals
    """
    return (
        f"🔥 Calories: {calories:.0f} kcal\n"
        f"🥩 Protein: {protein:.1f} g\n"
        f"🧈 Fat: {fat:.1f} g\n"
        f"🍞 Carbs: {carbs:.1f} g"
    )


def calculate_macronutrient_percentages(protein: float, fat: float, carbs: float) -> Dict[str, float]:
    """
    Calculates macronutrient percentages.
    
    Args:
        protein: Protein in grams
        fat: Fat in grams
        carbs: Carbs in grams
    
    Returns:
        Dict with percentages
    """
    protein_calories = protein * 4
    fat_calories = fat * 9
    carbs_calories = carbs * 4
    total_calories = protein_calories + fat_calories + carbs_calories
    
    if total_calories == 0:
        return {"protein": 0, "fat": 0, "carbs": 0}
    
    return {
        "protein": round((protein_calories / total_calories) * 100, 1),
        "fat": round((fat_calories / total_calories) * 100, 1),
        "carbs": round((carbs_calories / total_calories) * 100, 1)
    }


def validate_nutrition_inputs(
    weight: float,
    height: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str
) -> Dict[str, str]:
    """
    Validates nutrition calculation inputs.
    
    Args:
        weight: Weight in kg
        height: Height in cm
        age: Age in years
        gender: "male" or "female"
        activity_level: Activity level
        goal: Fitness goal
    
    Returns:
        Dict with validation errors
    """
    errors = {}
    
    if weight < 30 or weight > 300:
        errors["weight"] = "Weight must be between 30 and 300 kg"
    
    if height < 100 or height > 250:
        errors["height"] = "Height must be between 100 and 250 cm"
    
    if age < 10 or age > 120:
        errors["age"] = "Age must be between 10 and 120 years"
    
    if gender not in ["male", "female"]:
        errors["gender"] = "Gender must be 'male' or 'female'"
    
    valid_activities = ["sedentary", "light", "moderate", "active", "very_active"]
    if activity_level not in valid_activities:
        errors["activity_level"] = f"Activity level must be one of: {', '.join(valid_activities)}"
    
    valid_goals = ["lose_weight", "gain_weight", "maintenance"]
    if goal not in valid_goals:
        errors["goal"] = f"Goal must be one of: {', '.join(valid_goals)}"
    
    return errors
