import { callVisionModel, callBrainModel, buildMacroPrompt } from './ai';
import { MealLog, UserProfile, DailySummary } from './models';

type UserRecord = {
  profile?: UserProfile;
  meals: MealLog[];
  summaries?: DailySummary[];
};

// Simple in-memory store; in production replace with KV or Durable Objects
const db = new Map<string, UserRecord>();

async function handleRequest(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const path = url.pathname;

  if (path === '/health') {
    return new Response('OK', { status: 200 });
  }

  if (path === '/ai/food' && req.method === 'POST') {
    try {
      const form = await req.formData();
      const userId = String(form.get('userId') ?? 'anonymous');
      const imageBlob = form.get('image') as Blob | null;
      if (!imageBlob) return new Response(JSON.stringify({ error: 'image missing' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
      const imgBuf = await imageBlob.arrayBuffer();
      const label = await callVisionModel(imgBuf);

      // Prepare brain prompt
      const record = db.get(userId) ?? { meals: [] };
      const prompt = buildMacroPrompt(record.profile ?? { userId }, record.meals, label);
      const macroPlan = await callBrainModel(prompt, { userId });

      // Persist minimal state
      db.set(userId, record);
      return new Response(JSON.stringify({ userId, label, macroPlan }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (e) {
      return new Response(JSON.stringify({ error: (e as Error).message }), { status: 500, headers: { 'Content-Type': 'application/json' } });
    }
  }

  if (path === '/log/meal' && req.method === 'POST') {
    try {
      const data = await req.json();
      const userId = data.userId ?? 'anonymous';
      const record = db.get(userId) ?? { meals: [] };
      const meal: MealLog = {
        id: String(Date.now()),
        timestamp: new Date().toISOString(),
        calories: data.calories,
        protein: data.protein,
        carbs: data.carbs,
        fats: data.fats,
        text: data.text,
        imageUrl: data.imageUrl
      };
      record.meals.push(meal);
      db.set(userId, record);
      return new Response(JSON.stringify({ ok: true, meal }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    } catch (e) {
      return new Response(JSON.stringify({ error: 'invalid payload' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
    }
  }

  if (path === '/stats' && req.method === 'GET') {
    const userId = url.searchParams.get('userId') ?? 'anonymous';
    const rec = db.get(userId) ?? { meals: [] };
    const totalCalories = rec.meals?.reduce((acc, m) => acc + (m.calories ?? 0), 0) ?? 0;
    const summary = { userId, totalCalories, meals: rec.meals.length };
    return new Response(JSON.stringify(summary), { status: 200, headers: { 'Content-Type': 'application/json' } });
  }

  return new Response('Not Found', { status: 404 });
}

addEventListener('fetch', (event) => {
  event.respondWith(handleRequest(event.request));
});
