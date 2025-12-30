"""
语音合成API适配器
支持将诗歌转换为带情感的语音朗读
"""

import requests
import base64
from typing import Dict, Any
from config import APIConfig


class TTSGenerator:
    """TTS生成器基类"""

    def __init__(self):
        self.config = APIConfig

    def generate(self, text: str, emotion: str) -> Dict[str, Any]:
        """生成语音"""
        raise NotImplementedError


class OpenAITTSGenerator(TTSGenerator):
    """OpenAI TTS 语音生成器"""

    def __init__(self):
        super().__init__()
        self.api_key = self.config.OPENAI_API_KEY
        base_url = getattr(self.config, 'OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.api_url = f"{base_url.rstrip('/')}/audio/speech"

    def generate(self, text: str, emotion: str) -> Dict[str, Any]:
        """使用OpenAI TTS生成语音"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 根据情绪选择声音和语速
            voice_settings = self._get_voice_settings(emotion)

            data = {
                "model": "tts-1",  # 或 tts-1-hd 获得更高质量
                "input": text,
                "voice": voice_settings['voice'],
                "speed": voice_settings['speed']
            }

            print(f"[OpenAI TTS] Generating speech for emotion: {emotion}")
            print(f"[OpenAI TTS] Voice: {voice_settings['voice']}, Speed: {voice_settings['speed']}")

            response = requests.post(
                self.api_url,
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()

            # OpenAI TTS返回音频二进制数据
            audio_data = response.content

            # 转换为base64以便传输
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            print(f"[OpenAI TTS] ✓ Speech generated successfully ({len(audio_data)} bytes)")

            return {
                'status': 'success',
                'audio_base64': audio_base64,
                'audio_format': 'mp3',
                'voice': voice_settings['voice'],
                'emotion': emotion,
                'service': 'openai-tts'
            }

        except requests.exceptions.RequestException as e:
            print(f"[OpenAI TTS] ✗ Error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'service': 'openai-tts'
            }

    def _get_voice_settings(self, emotion: str) -> Dict[str, Any]:
        """根据情绪选择声音和语速"""
        # OpenAI TTS支持的声音: alloy, echo, fable, onyx, nova, shimmer
        settings = {
            'positive': {
                'voice': 'nova',      # 温暖、充满活力的女声
                'speed': 1.0          # 正常语速
            },
            'negative': {
                'voice': 'onyx',      # 沉稳、温和的男声
                'speed': 0.9          # 稍慢，更有思考感
            },
            'neutral': {
                'voice': 'shimmer',   # 柔和、平静的女声
                'speed': 0.95         # 稍慢
            }
        }

        return settings.get(emotion, settings['neutral'])


class EdgeTTSGenerator(TTSGenerator):
    """Microsoft Edge TTS 语音生成器（免费备选方案）"""

    def generate(self, text: str, emotion: str) -> Dict[str, Any]:
        """使用Edge TTS生成语音"""
        try:
            import edge_tts
            import asyncio

            # 根据情绪选择声音
            voice_map = {
                'positive': 'zh-CN-XiaoyiNeural',    # 活泼的女声
                'negative': 'zh-CN-YunxiNeural',     # 沉稳的男声
                'neutral': 'zh-CN-XiaoxiaoNeural'    # 温柔的女声
            }

            voice = voice_map.get(emotion, 'zh-CN-XiaoxiaoNeural')

            print(f"[Edge TTS] Generating speech with voice: {voice}")

            # 创建临时文件保存音频
            import tempfile
            import os

            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_path = temp_file.name
            temp_file.close()

            # 异步生成语音
            async def generate_speech():
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(temp_path)

            asyncio.run(generate_speech())

            # 读取音频文件
            with open(temp_path, 'rb') as f:
                audio_data = f.read()

            # 删除临时文件
            os.unlink(temp_path)

            # 转换为base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            print(f"[Edge TTS] ✓ Speech generated successfully")

            return {
                'status': 'success',
                'audio_base64': audio_base64,
                'audio_format': 'mp3',
                'voice': voice,
                'emotion': emotion,
                'service': 'edge-tts'
            }

        except ImportError:
            print("[Edge TTS] ✗ edge-tts library not installed. Install with: pip install edge-tts")
            return {
                'status': 'error',
                'message': 'edge-tts library not installed',
                'service': 'edge-tts'
            }
        except Exception as e:
            print(f"[Edge TTS] ✗ Error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'service': 'edge-tts'
            }


def get_tts_generator(service: str = None) -> TTSGenerator:
    """获取TTS生成器实例"""
    if service is None:
        service = getattr(APIConfig, 'TTS_SERVICE', 'openai')

    generators = {
        'openai': OpenAITTSGenerator,
        'edge': EdgeTTSGenerator
    }

    generator_class = generators.get(service, OpenAITTSGenerator)
    return generator_class()
