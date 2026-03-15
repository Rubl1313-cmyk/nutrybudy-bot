// Cloudflare Worker for AI-driven Nutrition Bot
// Uses:
//   - llama-3.2-11b-vision-instruct for food recognition from images
//   - hermes-2-pro-mistral-7b for reasoning and task orchestration

import { getUser, setUser, logMeal, logWater, logActivity, getRecommendations } from './storage.js';
import { recognizeFood } from './vision.js';
import { processTextWithBrain } from './brain.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Health check endpoint
    if (url.pathname === '/' || url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }
    
    // Telegram webhook endpoint
    if (url.pathname === '/webhook' && request.method === 'POST') {
      try {
        const update = await request.json();
        await handleTelegramUpdate(update, env);
        return new Response('OK', { status: 200 });
      } catch (error) {
        console.error('Webhook error:', error);
        return new Response('Internal Server Error', { status: 500 });
      }
    }
    
    // API endpoints for direct calls (if needed)
    if (url.pathname.startsWith('/api/')) {
      return handleApiRequest(request, env);
    }
    
    return new Response('Not Found', { status: 404 });
  }
};

async function handleTelegramUpdate(update, env) {
  // Extract user ID and message details
  const userId = update.message?.from?.id;
  if (!userId) return;
  
  // Get or create user profile
  let user = await getUser(env.NUTRITION_DATA, userId);
  if (!user) {
    user = { id: userId, createdAt: new Date().toISOString() };
    await setUser(env.NUTRITION_DATA, userId, user);
  }
  
  // Handle photo messages (food recognition)
  if (update.message?.photo && update.message.photo.length > 0) {
    const photo = update.message.photo[update.message.photo.length - 1]; // Get highest resolution
    const photoUrl = `https://api.telegram.org/file/bot${env.BOT_TOKEN}/${await getFilePath(photo.file_id, env)}`;
    
    // Recognize food using vision model
    const foodDescription = await recognizeFood(env.AI, photoUrl);
    
    // Process with brain model to get nutrition info
    const nutrition = await processTextWithBrain(
      env.AI,
      `Based on this food description: "${foodDescription}", estimate the calories, protein (g), fat (g), and carbs (g). 
       If the message includes quantity information (like "200g chicken"), incorporate that. 
       Return ONLY a JSON object with keys: calories, protein, fat, carbs (all numbers).`
    );
    
    // Log the meal
    await logMeal(env.NUTRITION_DATA, userId, {
      description: foodDescription,
      ...nutrition,
      timestamp: new Date().toISOString()
    });
    
    // Send confirmation to user (simplified - in real implementation, you'd use Telegram API)
    console.log(`Logged meal for user ${userId}:`, foodDescription, nutrition);
    return;
  }
  
  // Handle text messages
  if (update.message?.text) {
    const text = update.message.text;
    
    // Process with brain model to determine intent and extract parameters
    const result = await processTextWithBrain(
      env.AI,
      `You are a nutrition assistant. Analyze this user message: "${text}"
       Determine the user's intent from these options:
       - log_water: user wants to log water intake (extract amount in ml, default 250ml if not specified)
       - log_food: user wants to log food via text description (extract food description and quantity if possible)
       - log_activity: user wants to log physical activity (extract activity type and duration in minutes)
       - get_recommendations: user wants daily nutrition recommendations
       - set_profile: user wants to set/update their profile (age, weight, height, gender, activity level, goals)
       - unknown: if intent is unclear
       
       Return ONLY a JSON object with:
       {
         "intent": "one of the above intents",
         "parameters": { /* relevant parameters based on intent */ }
       }
       
       For log_water: parameters should include "amount_ml" (number)
       For log_food: parameters should include "description" (string) and optionally "quantity_g" (number)
       For log_activity: parameters should include "type" (string) and "duration_min" (number)
       For get_recommendations: parameters should be empty object {}
       For set_profile: parameters should include any of: age, weight_kg, height_cm, gender, activity_level, goals (strings/numbers)
       `
    );
    
    // Execute the determined action
    switch (result.intent) {
      case 'log_water':
        const amount = result.parameters.amount_ml || 250;
        await logWater(env.NUTRITION_DATA, userId, amount);
        console.log(`Logged ${amount}ml water for user ${userId}`);
        break;
        
      case 'log_food':
        const { description, quantity_g } = result.parameters;
        const foodNutrition = await processTextWithBrain(
          env.AI,
          `Estimate nutrition for: "${description}"${quantity_g ? ` (${quantity_g}g)` : ''}.
           Return ONLY JSON: { calories, protein, fat, carbs } (numbers)`
        );
        await logMeal(env.NUTRITION_DATA, userId, {
          description,
          ...foodNutrition,
          timestamp: new Date().toISOString()
        });
        console.log(`Logged food for user ${userId}:`, description, foodNutrition);
        break;
        
      case 'log_activity':
        const { type, duration_min } = result.parameters;
        await logActivity(env.NUTRITION_DATA, userId, { type, duration_min: duration_min || 30 });
        console.log(`Logged activity for user ${userId}:`, type, duration_min);
        break;
        
      case 'get_recommendations':
        const recommendations = await getRecommendations(env.NUTRITION_DATA, userId, env.AI);
        console.log(`Recommendations for user ${userId}:`, recommendations);
        // In real implementation, send recommendations to user via Telegram
        break;
        
      case 'set_profile':
        await setUser(env.NUTRITION_DATA, userId, { ...user, ...result.parameters, updatedAt: new Date().toISOString() });
        console.log(`Updated profile for user ${userId}:`, result.parameters);
        break;
        
      default:
        console.log(`Unknown intent for user ${userId}:`, text);
        // Could send help message
    }
  }
}

// Helper to get file path from Telegram file ID
async function getFilePath(file_id, env) {
  // In a real implementation, you'd call Telegram's getFile method
  // For now, we'll simulate or use a placeholder
  // This would require making an HTTP request to Telegram API
  // Since we're in a Worker, we can use fetch
  const response = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/getFile?file_id=${file_id}`);
  const data = await response.json();
  return data.result.file_path;
}

async function handleApiRequest(request, env) {
  // Implement API endpoints if needed for frontend or other integrations
  // For example: /api/user/:id, /api/log, etc.
  return new Response('API endpoint not implemented', { status: 501 });
}