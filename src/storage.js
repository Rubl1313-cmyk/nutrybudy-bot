// Storage module for interacting with Cloudflare KV (or Durable Objects in production)
// This is a simplified version using KV. For production, consider Durable Objects for better consistency.

// We assume the KV namespace is bound to the Worker as `NUTRITION_DATA`

export async function getUser(KV, userId) {
  const value = await KV.get(`user:${userId}`);
  return value ? JSON.parse(value) : null;
}

export async function setUser(KV, userId, userData) {
  await KV.put(`user:${userId}`, JSON.stringify(userData));
}

export async function logMeal(KV, userId, mealData) {
  const key = `meal:${userId}:${Date.now()}`;
  await KV.put(key, JSON.stringify({
    ...mealData,
    userId,
    loggedAt: new Date().toISOString()
  }));
}

export async function logWater(KV, userId, amountMl) {
  const key = `water:${userId}:${Date.now()}`;
  await KV.put(key, JSON.stringify({
    amountMl,
    userId,
    loggedAt: new Date().toISOString()
  }));
}

export async function logActivity(KV, userId, activityData) {
  const key = `activity:${userId}:${Date.now()}`;
  await KV.put(key, JSON.stringify({
    ...activityData,
    userId,
    loggedAt: new Date().toISOString()
  }));
}

export async function getUserMeals(KV, userId, limit = 10) {
  // In a real implementation, we would need to scan by prefix or use a sorted set.
  // With KV, we don't have built-in querying. We'll return an empty array for now.
  // For production, consider using Durable Objects or a different storage solution.
  return [];
}

export async function getUserWater(KV, userId, limit = 10) {
  return [];
}

export async function getUserActivity(KV, userId, limit = 10) {
  return [];
}

// Generate recommendations using the brain model based on user data and recent logs
export async function getRecommendations(KV, userId, AI) {
  // Get user profile
  const user = await getUser(KV, userId);
  if (!user) {
    return { error: "User profile not found" };
  }

  // Get recent logs (in a real app, we would fetch from KV or Durable Objects)
  // For now, we'll use placeholder data or empty arrays.
  const meals = await getUserMeals(KV, userId, 5);
  const water = await getUserWater(KV, userId, 5);
  const activity = await getUserActivity(KV, userId, 5);

  // Prepare prompt for the brain model
  const prompt = `
    You are a nutrition and health advisor. Based on the following user data and recent logs, 
    provide personalized recommendations for today's calorie target, macronutrient split, 
    water intake, and activity suggestions.

    User Profile:
    - Age: ${user.age || 'not specified'}
    - Weight: ${user.weight_kg || 'not specified'} kg
    - Height: ${user.height_cm || 'not specified'} cm
    - Gender: ${user.gender || 'not specified'}
    - Activity Level: ${user.activity_level || 'not specified'}
    - Goals: ${user.goals || 'not specified'}

    Recent Meals (last 5):
    ${meals.map(m => `- ${m.description}: ${m.calories} cal, ${m.protein}g protein, ${m.fat}g fat, ${m.carbs}g carbs`).join('\n') || 'None'}

    Recent Water Intake (last 5, in ml):
    ${water.map(w => `- ${w.amountMl} ml`).join('\n') || 'None'}

    Recent Activity (last 5):
    ${activity.map(a => `- ${a.type} for ${a.duration_min} minutes`).join('\n') || 'None'}

    Please provide:
    1. Recommended daily calorie intake
    2. Recommended macronutrient split (protein, fat, carbs in grams)
    3. Recommended water intake (in ml)
    4. Activity suggestions (type and duration)
    5. Any other relevant advice

    Return ONLY a JSON object with the following keys:
    {
      "calories_target": number,
      "protein_target_g": number,
      "fat_target_g": number,
      "carbs_target_g": number,
      "water_target_ml": number,
      "activity_suggestions": [ { "type": string, "duration_min": number } ],
      "advice": string
    }
  `;

  try {
    const response = await AI.run(
      "@cf/hermes-2-pro-mistral-7b",
      {
        prompt: prompt,
        max_tokens: 1000,
        temperature: 0.7
      }
    );

    // Try to parse the response as JSON
    return JSON.parse(response);
  } catch (error) {
    console.error("Error generating recommendations:", error);
    return { error: "Failed to generate recommendations" };
  }
}