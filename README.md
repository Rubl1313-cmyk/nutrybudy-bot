# AI-Driven Nutrition Bot (Refactor Plan)

This repo proposes a complete rebuild and refactor of your nutrition bot to be fully AI-driven using Cloudflare AI models:
- Vision model: llama-3.2-11b-vision-instruct for food recognition from images
- Brain model: hermes-2-pro-mistral-7b for high-level reasoning and task orchestration

Architecture highlights:
- Cloudflare Workers as the API gateway and orchestrator
- Vision module handles food recognition from photos
- Brain module handles meal planning, macro targets, hydration, activity, climate adaptation
- Persistent user data via KV or Durable Objects (starter uses a simple in-memory store; replace with KV/DO in production)

Key features implemented:
- AI-driven food recognition from images
- AI-driven macro-nutrition calculation (personalized KBJU)
- Hydration tracking, activity monitoring, steps, and climate-adapted recommendations
- User-friendly API endpoints for logging meals, hydration, activity, and obtaining daily recommendations

What you’ll need to do next:
- Replace in-memory store with Cloudflare KV or Durable Objects
- Wire up real authentication to identify users securely
- Add a front-end UI that calls these endpoints and visualizes progress
- Implement proper error handling, rate limits, and retry strategies
- Add tests and CI

How to run locally (rough guide):
- Install wrangler, configure with your Cloudflare account
- wrangler login; wrangler dev
- Ensure your Cloudflare subdomain can access the AI models (model endpoints)

Notes:
- This is a scaffold for rapid rebuilding. It focuses on architecture and integration points rather than a finished product.
