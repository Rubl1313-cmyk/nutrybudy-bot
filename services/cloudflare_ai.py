import aiohttp
import os
import base64
from typing import Optional

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

async def analyze_food_image(image_bytes: bytes, prompt: str = "What food is in this image? Describe briefly in Russian.") -> Optional[str]:
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    payload = {
        "image": image_base64,
        "prompt": prompt,
        "max_tokens": 200
    }
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BASE_URL + "@cf/unum/uform-gen2-qwen-500m", 
                                   headers=headers, json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result", {}).get("description", "")
                else:
                    error_text = await resp.text()
                    print(f"Cloudflare Vision API error {resp.status}: {error_text}")
                    return None
        except Exception as e:
            print(f"Cloudflare Vision exception: {e}")
            return None

async def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    from aiohttp import FormData
    data = FormData()
    data.add_field('audio', audio_bytes, filename='voice.ogg', content_type='audio/ogg')
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BASE_URL + "@openai/whisper", 
                                   headers=headers, data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result", {}).get("text", "")
                else:
                    error_text = await resp.text()
                    print(f"Cloudflare Whisper error {resp.status}: {error_text}")
                    return None
        except Exception as e:
            print(f"Cloudflare Whisper exception: {e}")
            return None

async def generate_recipe(ingredients: str) -> Optional[str]:
    prompt = f"Составь подробный рецепт блюда на русском языке, используя следующие ингредиенты: {ingredients}. Укажи: 1) Название блюда 2) Ингредиенты с количеством 3) Пошаговое приготовление 4) Время приготовления 5) КБЖУ на порцию. Форматируй красиво."
    payload = {
        "prompt": prompt,
        "max_tokens": 800
    }
    headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(BASE_URL + "@cf/meta/llama-3-8b-instruct", 
                                   headers=headers, json=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result", {}).get("response", "")
                else:
                    error_text = await resp.text()
                    print(f"Cloudflare LLM error {resp.status}: {error_text}")
                    return None
        except Exception as e:
            print(f"Cloudflare LLM exception: {e}")
            return None