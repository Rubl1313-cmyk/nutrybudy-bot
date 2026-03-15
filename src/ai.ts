export const VISION_MODEL = 'llama-3.2-11b-vision-instruct';
export const BRAIN_MODEL = 'hermes-2-pro-mistral-7b';

export async function callVisionModel(imageBytes: ArrayBuffer): Promise<string> {
  try {
    const resp = await fetch(`https://api.cloudflare.com/client/v4/workers-ai/models/${VISION_MODEL}/predict`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/octet-stream'
      },
      body: imageBytes
    });
    if (!resp.ok) throw new Error(`Vision model failed: ${resp.status}`);
    const data = await resp.json();
    return data?.prediction ?? data?.label ?? 'unknown';
  } catch (e) {
    console.warn('Vision model error', e);
    return 'unknown';
  }
}

export async function callBrainModel(prompt: string, context?: any): Promise<string> {
  try {
    const body = { prompt, context };
    const resp = await fetch(`https://api.cloudflare.com/client/v4/workers-ai/models/${BRAIN_MODEL}/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!resp.ok) throw new Error(`Brain model failed: ${resp.status}`);
    const data = await resp.json();
    return data?.text ?? '';
  } catch (e) {
    console.warn('Brain model error', e);
    return '';
  }
}

export function buildMacroPrompt(profile: any, meals: any[], foodLabel?: string): string {
  const parts = [
    'You are an AI nutrition coach.',
    'User profile: ' + JSON.stringify(profile),
    'Recent meals: ' + JSON.stringify(meals),
    'Food recognized: ' + (foodLabel ?? 'unknown'),
    'Goal: optimize calories and macros for weight management.',
    'Provide a daily target: calories, protein, carbs, fats, in actionable form.'
  ];
  return parts.join('\n');
}
