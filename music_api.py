"""
音乐生成API适配器
支持多种音乐生成服务：Suno AI, Stable Audio, MusicGen等
"""

import requests
import json
import time
import random
from typing import Dict, Any
from config import APIConfig


class MusicGenerator:
    """音乐生成器基类"""

    def __init__(self):
        self.config = APIConfig

    def generate(self, prompt: str, emotion: str, duration: int = 30) -> Dict[str, Any]:
        """生成音乐"""
        raise NotImplementedError


class StableAudioGenerator(MusicGenerator):
    """Stability AI Stable Audio 音乐生成器"""

    def __init__(self):
        super().__init__()
        self.api_key = self.config.STABLE_AUDIO_API_KEY
        self.api_url = "https://api.stability.ai/v2beta/stable-audio/generate/music"

    def generate(self, prompt: str, emotion: str, duration: int = 30) -> Dict[str, Any]:
        """使用Stable Audio生成音乐"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 构建音乐提示词
            style_prompt = self.config.MUSIC_STYLE_MAPPING.get(emotion, 'calm, peaceful')
            full_prompt = f"{style_prompt}, instrumental, no vocals, suitable for memory reflection"

            data = {
                "prompt": full_prompt,
                "duration": min(duration, 47),  # Stable Audio最长47秒
                "output_format": "mp3"
            }

            print(f"[Stable Audio] Generating music: {full_prompt[:100]}...")

            response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()

            # Stable Audio返回音频文件的base64或URL
            result = response.json()

            # 处理返回的音频数据
            if 'audio' in result:
                audio_base64 = result['audio']
                # 可以保存到服务器或返回data URL
                audio_url = f"data:audio/mp3;base64,{audio_base64}"
            elif 'url' in result:
                audio_url = result['url']
            else:
                raise Exception("No audio data returned")

            print(f"[Stable Audio] ✓ Music generated successfully")

            return {
                'status': 'success',
                'title': f"{emotion.capitalize()} Memory Music",
                'url': audio_url,
                'description': full_prompt,
                'duration': duration,
                'service': 'stable-audio'
            }

        except Exception as e:
            print(f"[Stable Audio] ✗ Error: {str(e)}")
            return self._get_fallback_music(emotion)

    def _get_fallback_music(self, emotion: str) -> Dict[str, Any]:
        """获取备用音乐"""
        return MusicLibraryGenerator().generate("", emotion, 30)


class MusicGenGenerator(MusicGenerator):
    """Meta MusicGen 音乐生成器（通过Replicate）"""

    def __init__(self):
        super().__init__()
        self.api_key = self.config.REPLICATE_API_KEY
        self.api_url = "https://api.replicate.com/v1/predictions"

    def generate(self, prompt: str, emotion: str, duration: int = 30) -> Dict[str, Any]:
        """使用MusicGen生成音乐"""
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }

            # 构建音乐提示词
            style_prompt = self.config.MUSIC_STYLE_MAPPING.get(emotion, 'calm, peaceful')

            data = {
                "version": "b05b1dff1d8c6dc63d14b0cdb42135378dcb87f6373b0d3d341ede46e59e2b38",  # MusicGen
                "input": {
                    "prompt": style_prompt,
                    "duration": duration,
                    "temperature": 1.0,
                    "model_version": "stereo-large"
                }
            }

            print(f"[MusicGen] Generating music: {style_prompt[:100]}...")

            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()

            prediction = response.json()
            prediction_id = prediction['id']

            # 轮询结果
            audio_url = self._wait_for_prediction(prediction_id, headers)

            print(f"[MusicGen] ✓ Music generated successfully")

            return {
                'status': 'success',
                'title': f"{emotion.capitalize()} Memory Music",
                'url': audio_url,
                'description': style_prompt,
                'duration': duration,
                'service': 'musicgen'
            }

        except Exception as e:
            print(f"[MusicGen] ✗ Error: {str(e)}")
            return self._get_fallback_music(emotion)

    def _wait_for_prediction(self, prediction_id: str, headers: dict, max_wait: int = 120) -> str:
        """等待预测完成"""
        start_time = time.time()
        get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"

        while time.time() - start_time < max_wait:
            response = requests.get(get_url, headers=headers)
            prediction = response.json()

            status = prediction['status']

            if status == 'succeeded':
                return prediction['output']  # 返回音频URL
            elif status == 'failed':
                raise Exception("Prediction failed")

            time.sleep(3)

        raise Exception("Prediction timeout")

    def _get_fallback_music(self, emotion: str) -> Dict[str, Any]:
        """获取备用音乐"""
        return MusicLibraryGenerator().generate("", emotion, 30)


class SunoAIGenerator(MusicGenerator):
    """Suno AI 音乐生成器"""

    def __init__(self):
        super().__init__()
        self.api_key = self.config.SUNO_API_KEY
        # Suno AI的非官方API地址（需要根据实际情况调整）
        self.api_url = "https://api.sunoai.com/v1/generate"

    def generate(self, prompt: str, emotion: str, duration: int = 30) -> Dict[str, Any]:
        """使用Suno AI生成音乐"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 构建音乐提示词
            style_prompt = self.config.MUSIC_STYLE_MAPPING.get(emotion, 'calm, peaceful')

            data = {
                "prompt": style_prompt,
                "duration": duration,
                "instrumental": True,  # 纯音乐，无歌词
                "style": "ambient"
            }

            print(f"[Suno AI] Generating music: {style_prompt[:100]}...")

            response = requests.post(self.api_url, headers=headers, json=data, timeout=120)
            response.raise_for_status()

            result = response.json()
            audio_url = result.get('audio_url') or result.get('url')

            print(f"[Suno AI] ✓ Music generated successfully")

            return {
                'status': 'success',
                'title': f"{emotion.capitalize()} Memory Music",
                'url': audio_url,
                'description': style_prompt,
                'duration': duration,
                'service': 'suno-ai'
            }

        except Exception as e:
            print(f"[Suno AI] ✗ Error: {str(e)}")
            return self._get_fallback_music(emotion)

    def _get_fallback_music(self, emotion: str) -> Dict[str, Any]:
        """获取备用音乐"""
        return MusicLibraryGenerator().generate("", emotion, 30)


class MusicLibraryGenerator(MusicGenerator):
    """音乐库生成器（使用预置的音乐库，无需API）"""

    def generate(self, prompt: str, emotion: str, duration: int = 30) -> Dict[str, Any]:
        """从音乐库中选择音乐"""
        music_list = self.config.MUSIC_LIBRARY.get(emotion, self.config.MUSIC_LIBRARY['neutral'])

        # 随机选择一首音乐
        selected = random.choice(music_list) if music_list else {
            'title': 'Default Music',
            'url': 'https://www.bensound.com/bensound-music/bensound-relaxing.mp3',
            'description': 'Calm background music'
        }

        print(f"[Music Library] Selected: {selected['title']}")

        return {
            'status': 'success',
            'title': selected['title'],
            'url': selected['url'],
            'description': selected['description'],
            'service': 'library',
            'note': 'Using pre-selected music. Configure API for custom generation.'
        }


class SmartMusicGenerator(MusicGenerator):
    """智能音乐生成器 - 自动选择最佳服务"""

    def __init__(self):
        super().__init__()
        self.generators = self._init_generators()

    def _init_generators(self) -> Dict[str, MusicGenerator]:
        """初始化所有可用的生成器"""
        generators = {}

        # 根据配置初始化生成器
        if self.config.STABLE_AUDIO_API_KEY:
            generators['stable-audio'] = StableAudioGenerator()

        if self.config.REPLICATE_API_KEY:
            generators['musicgen'] = MusicGenGenerator()

        if self.config.SUNO_API_KEY:
            generators['suno'] = SunoAIGenerator()

        # 音乐库总是可用
        generators['library'] = MusicLibraryGenerator()

        return generators

    def generate(self, prompt: str, emotion: str, duration: int = 30) -> Dict[str, Any]:
        """智能选择生成器并生成音乐"""

        # 优先级顺序
        priority = ['stable-audio', 'musicgen', 'suno', 'library']

        for service in priority:
            if service in self.generators:
                print(f"[Smart Generator] Trying {service}...")
                result = self.generators[service].generate(prompt, emotion, duration)

                if result['status'] == 'success':
                    return result

        # 如果所有服务都失败，使用音乐库
        print(f"[Smart Generator] All services failed, using library")
        return MusicLibraryGenerator().generate(prompt, emotion, duration)


def get_music_generator(service: str = None) -> MusicGenerator:
    """获取音乐生成器实例"""
    if service is None:
        service = APIConfig.MUSIC_SERVICE

    generators = {
        'stable-audio': StableAudioGenerator,
        'musicgen': MusicGenGenerator,
        'suno': SunoAIGenerator,
        'library': MusicLibraryGenerator,
        'smart': SmartMusicGenerator
    }

    generator_class = generators.get(service, MusicLibraryGenerator)
    return generator_class()
