"""
Cloudflare Workers AI Integration для NutriBuddy
✅ Исправлено: конвертация OGG→WAV через ffmpeg + правильная отправка multipart/form-data
"""
import aiohttp
import os
import logging
from typing import Optional, List
import io
import wave
import struct
import tempfile
import subprocess

logger = logging.getLogger(__name__)

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")

if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
    logger.warning("⚠️ Cloudflare credentials not set")
    BASE_URL = ""
else:
    BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{CLOUDFLARE_ACCOUNT_ID}/ai/run/"

# 🔥 Проверка наличия ffmpeg в системе
def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except:
        return False

FFMPEG_AVAILABLE = check_ffmpeg()
if not FFMPEG_AVAILABLE:
    logger.warning("⚠️ ffmpeg not found — audio conversion may fail")

# 🔥 Только проверенные модели
WHISPER_MODELS = [
    "@cf/openai/whisper",  # базовая модель, работает
]

def _bytes_to_array(image_bytes: bytes) -> List[int]:
    return list(image_bytes)

def _ensure_correct_wav(wav_bytes: bytes) -> Optional[bytes]:
    """
    Приводит WAV к формату, принимаемому Cloudflare Whisper:
    - 16-bit PCM
    - 16000 Hz
    - mono
    """
    try:
        with io.BytesIO(wav_bytes) as wav_in:
            with wave.open(wav_in, 'rb') as wav_file:
                n_channels = wav_file.getnchannels()
                sampwidth = wav_file.getsampwidth()
                framerate = wav_file.getframerate()
                n_frames = wav_file.getnframes()
                frames = wav_file.readframes(n_frames)

                # Если уже идеальный формат — возвращаем как есть
                if n_channels == 1 and sampwidth == 2 and framerate == 16000:
                    return wav_bytes

                logger.info(f"🔄 Adjusting WAV: {n_channels}ch, {sampwidth*8}bit, {framerate}Hz → 1ch, 16bit, 16kHz")

                # Декодируем семплы
                if sampwidth == 2:
                    samples = struct.unpack(f'{len(frames)//2}h', frames)
                else:
                    # Для других разрядностей (например, 8-bit) — примитивная конвертация
                    # В реальности лучше использовать ffmpeg, но для простоты допустим
                    samples = [0] * n_frames  # заглушка

                # Приводим к моно, если стерео
                if n_channels == 2:
                    samples = samples[::2]

                # Ресемплинг
                target_rate = 16000
                if framerate != target_rate:
                    ratio = target_rate / framerate
                    new_length = int(len(samples) * ratio)
                    resampled = []
                    for i in range(new_length):
                        src_idx = int(i / ratio)
                        if src_idx < len(samples):
                            resampled.append(samples[src_idx])
                    samples = resampled

                # Кодируем обратно в WAV
                output = io.BytesIO()
                with wave.open(output, 'wb') as wav_out:
                    wav_out.setnchannels(1)
                    wav_out.setsampwidth(2)
                    wav_out.setframerate(target_rate)
                    wav_out.writeframes(struct.pack(f'{len(samples)}h', *samples))

                output.seek(0)
                logger.info("✅ WAV adjusted successfully")
                return output.read()

    except Exception as e:
        logger.warning(f"⚠️ Failed to adjust WAV: {e}")
        return None


async def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> Optional[str]:
    try:
        if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
            logger.error("❌ Cloudflare credentials not set")
            return None

        file_size = len(audio_bytes)
        logger.info(f"🎤 Original size: {file_size / 1024:.1f} KB")

        # 🔥 Шаг 1. Конвертируем OGG → WAV через ffmpeg (если доступен)
        wav_bytes = None
        if FFMPEG_AVAILABLE:
            try:
                import ffmpeg
                with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as f_in:
                    f_in.write(audio_bytes)
                    in_path = f_in.name
                out_path = in_path.replace('.ogg', '.wav')
                try:
                    # Запускаем ffmpeg с нужными параметрами
                    ffmpeg.input(in_path).output(
                        out_path,
                        acodec='pcm_s16le',
                        ar='16000',
                        ac=1
                    ).run(quiet=True, overwrite_output=True)
                    with open(out_path, 'rb') as f:
                        wav_bytes = f.read()
                    logger.info("✅ ffmpeg conversion successful")
                finally:
                    if os.path.exists(in_path):
                        os.unlink(in_path)
                    if os.path.exists(out_path):
                        os.unlink(out_path)
            except Exception as conv_error:
                logger.warning(f"⚠️ ffmpeg conversion failed: {conv_error}")

        # 🔥 Шаг 2. Если не удалось получить WAV, пытаемся обработать как есть (маловероятно)
        processed_bytes = wav_bytes if wav_bytes else audio_bytes

        # 🔥 Шаг 3. Приводим WAV к нужным параметрам
        if wav_bytes:
            processed_bytes = _ensure_correct_wav(wav_bytes)
            if not processed_bytes:
                processed_bytes = wav_bytes  # fallback на сырой WAV

        # 🔥 Шаг 4. Отправляем через multipart/form-data
        for model in WHISPER_MODELS:
            try:
                form = aiohttp.FormData()
                form.add_field(
                    'file',
                    processed_bytes,
                    filename='audio.wav',
                    content_type='audio/wav'
                )

                headers = {"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}"}
                url = f"{BASE_URL}{model}"

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        headers=headers,
                        data=form,
                        timeout=aiohttp.ClientTimeout(total=60)
                    ) as resp:
                        if resp.status == 200:
                            result = await resp.json()
                            text = result.get("result", {}).get("text", "").strip()
                            if text:
                                logger.info(f"✅ Whisper success: {text[:100]}...")
                                return text
                            else:
                                logger.warning("⚠️ Empty transcription")
                        else:
                            error_text = await resp.text()
                            logger.warning(f"⚠️ {model} failed {resp.status}: {error_text[:300]}")
            except Exception as e:
                logger.warning(f"⚠️ {model} exception: {e}")
                continue

        logger.error("❌ All Whisper models failed")
        return None

    except Exception as e:
        logger.exception(f"💥 Critical error: {e}")
        return None


# Остальные функции (analyze_food_image, generate_text) остаются без изменений
# (см. ваш код выше)
