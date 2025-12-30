"""
图片生成API适配器
支持多种图片生成服务：DALL-E, Stable Diffusion, Replicate等
"""

import requests
import json
import time
from typing import Dict, Any
from config import APIConfig


class ImageGenerator:
    """图片生成器基类"""

    def __init__(self):
        self.config = APIConfig

    def generate(self, prompt: str, emotion: str) -> Dict[str, Any]:
        """生成图片"""
        raise NotImplementedError


class DALLEGenerator(ImageGenerator):
    """OpenAI DALL-E 图片生成器"""

    def __init__(self):
        super().__init__()
        self.api_key = self.config.OPENAI_API_KEY
        # 支持自定义base_url（如使用代理服务）
        base_url = getattr(self.config, 'OPENAI_BASE_URL', 'https://api.openai.com/v1')
        self.api_url = f"{base_url.rstrip('/')}/images/generations"

    def generate(self, prompt: str, emotion: str) -> Dict[str, Any]:
        """使用DALL-E生成图片"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            # 增强提示词以生成照片级真实图片
            photorealistic_prompt = self._enhance_for_photorealism(prompt, emotion)

            data = {
                "model": self.config.DALLE_MODEL,
                "prompt": photorealistic_prompt,
                "n": 1,
                "size": self.config.DALLE_SIZE,
                "quality": self.config.DALLE_QUALITY,
                "style": "natural"  # 使用natural风格获得更真实的照片效果
            }

            print(f"[DALL-E] Generating image with prompt: {photorealistic_prompt[:100]}...")

            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()

            result = response.json()
            image_url = result['data'][0]['url']

            # 可选：revised_prompt 包含DALL-E优化后的提示词
            revised_prompt = result['data'][0].get('revised_prompt', prompt)

            print(f"[DALL-E] ✓ Image generated successfully")

            return {
                'status': 'success',
                'image_url': image_url,
                'prompt': prompt,
                'revised_prompt': revised_prompt,
                'service': 'dall-e'
            }

        except requests.exceptions.RequestException as e:
            print(f"[DALL-E] ✗ Error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'image_url': self._get_fallback_image(emotion),
                'service': 'dall-e'
            }

    def _get_fallback_image(self, emotion: str) -> str:
        """获取备用图片"""
        emotion_keywords = {
            'positive': 'happiness,joy,peace',
            'negative': 'reflection,hope,healing',
            'neutral': 'calm,serenity,peace'
        }
        keywords = emotion_keywords.get(emotion, 'memory,nostalgia')
        return f"https://source.unsplash.com/1024x1024/?{keywords}"

    def _enhance_for_photorealism(self, prompt: str, emotion: str) -> str:
        """增强提示词以生成照片级真实图片"""
        # 照片风格前缀
        photo_prefix = "A highly detailed photorealistic photograph, "

        # 根据情绪调整照片氛围
        emotion_lighting = {
            'positive': 'warm natural lighting, golden hour, soft shadows, vibrant colors',
            'negative': 'gentle diffused lighting, muted tones, contemplative atmosphere, soft focus',
            'neutral': 'balanced natural lighting, realistic colors, clear details'
        }

        lighting = emotion_lighting.get(emotion, 'natural lighting, realistic details')

        # 照片质量后缀
        photo_suffix = f", {lighting}, high resolution, professional photography, 50mm lens, shallow depth of field, captured with DSLR camera"

        # 组合完整提示词
        enhanced_prompt = f"{photo_prefix}{prompt}{photo_suffix}"

        return enhanced_prompt


class StabilityAIGenerator(ImageGenerator):
    """Stability AI (Stable Diffusion) 图片生成器"""

    def __init__(self):
        super().__init__()
        self.api_key = self.config.STABILITY_API_KEY
        self.api_url = f"https://api.stability.ai/v1/generation/{self.config.STABILITY_ENGINE}/text-to-image"

    def generate(self, prompt: str, emotion: str) -> Dict[str, Any]:
        """使用Stable Diffusion生成图片"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            # 根据情绪添加风格提示
            style_suffix = {
                'positive': ', vibrant colors, bright lighting, joyful atmosphere',
                'negative': ', soft colors, gentle lighting, contemplative mood',
                'neutral': ', natural colors, balanced lighting, peaceful scene'
            }
            enhanced_prompt = prompt + style_suffix.get(emotion, '')

            data = {
                "text_prompts": [
                    {
                        "text": enhanced_prompt,
                        "weight": 1
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            }

            print(f"[Stability AI] Generating image with prompt: {prompt[:100]}...")

            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()

            result = response.json()

            # Stability AI返回base64编码的图片
            # 需要转换或上传到服务器
            # 这里简化处理，实际应用中需要保存到服务器
            image_base64 = result['artifacts'][0]['base64']

            # 临时方案：返回data URL
            image_url = f"data:image/png;base64,{image_base64}"

            print(f"[Stability AI] ✓ Image generated successfully")

            return {
                'status': 'success',
                'image_url': image_url,
                'image_base64': image_base64,
                'prompt': enhanced_prompt,
                'service': 'stability-ai'
            }

        except requests.exceptions.RequestException as e:
            print(f"[Stability AI] ✗ Error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'image_url': self._get_fallback_image(emotion),
                'service': 'stability-ai'
            }

    def _get_fallback_image(self, emotion: str) -> str:
        """获取备用图片"""
        emotion_keywords = {
            'positive': 'happiness,joy,peace',
            'negative': 'reflection,hope,healing',
            'neutral': 'calm,serenity,peace'
        }
        keywords = emotion_keywords.get(emotion, 'memory,nostalgia')
        return f"https://source.unsplash.com/1024x1024/?{keywords}"


class ReplicateGenerator(ImageGenerator):
    """Replicate API 图片生成器（支持多种开源模型）"""

    def __init__(self):
        super().__init__()
        self.api_key = self.config.REPLICATE_API_KEY
        self.api_url = "https://api.replicate.com/v1/predictions"

    def generate(self, prompt: str, emotion: str) -> Dict[str, Any]:
        """使用Replicate生成图片"""
        try:
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }

            # 使用SDXL模型
            data = {
                "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",  # SDXL
                "input": {
                    "prompt": prompt,
                    "negative_prompt": "blurry, low quality, distorted, ugly",
                    "width": 1024,
                    "height": 1024
                }
            }

            print(f"[Replicate] Generating image with prompt: {prompt[:100]}...")

            response = requests.post(self.api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()

            prediction = response.json()
            prediction_id = prediction['id']

            # 轮询结果
            image_url = self._wait_for_prediction(prediction_id, headers)

            print(f"[Replicate] ✓ Image generated successfully")

            return {
                'status': 'success',
                'image_url': image_url,
                'prompt': prompt,
                'service': 'replicate'
            }

        except Exception as e:
            print(f"[Replicate] ✗ Error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'image_url': self._get_fallback_image(emotion),
                'service': 'replicate'
            }

    def _wait_for_prediction(self, prediction_id: str, headers: dict, max_wait: int = 60) -> str:
        """等待预测完成"""
        start_time = time.time()
        get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"

        while time.time() - start_time < max_wait:
            response = requests.get(get_url, headers=headers)
            prediction = response.json()

            status = prediction['status']

            if status == 'succeeded':
                return prediction['output'][0]  # 返回图片URL
            elif status == 'failed':
                raise Exception("Prediction failed")

            time.sleep(2)

        raise Exception("Prediction timeout")

    def _get_fallback_image(self, emotion: str) -> str:
        """获取备用图片"""
        emotion_keywords = {
            'positive': 'happiness,joy,peace',
            'negative': 'reflection,hope,healing',
            'neutral': 'calm,serenity,peace'
        }
        keywords = emotion_keywords.get(emotion, 'memory,nostalgia')
        return f"https://source.unsplash.com/1024x1024/?{keywords}"


class UnsplashGenerator(ImageGenerator):
    """Unsplash 占位图片生成器（免费，无需API密钥）"""

    def generate(self, prompt: str, emotion: str) -> Dict[str, Any]:
        """使用Unsplash生成占位图片"""
        # 从提示词中提取关键词
        keywords = self._extract_keywords(prompt, emotion)

        image_url = f"https://source.unsplash.com/1024x1024/?{keywords}"

        print(f"[Unsplash] Using keywords: {keywords}")

        return {
            'status': 'success',
            'image_url': image_url,
            'prompt': prompt,
            'keywords': keywords,
            'service': 'unsplash',
            'note': 'Using Unsplash placeholder. Configure AI service for custom images.'
        }

    def _extract_keywords(self, prompt: str, emotion: str) -> str:
        """从提示词中提取关键词"""
        # 简单的关键词提取
        keywords = []

        # 情绪相关关键词
        emotion_keywords = {
            'positive': 'happiness,joy,peace',
            'negative': 'reflection,contemplation,hope',
            'neutral': 'calm,serenity,peaceful'
        }
        keywords.append(emotion_keywords.get(emotion, 'memory'))

        # 从提示词中提取地点
        place_keywords = ['home', 'kitchen', 'garden', 'park', 'beach', 'mountain', 'room']
        for word in place_keywords:
            if word in prompt.lower():
                keywords.append(word)
                break

        # 添加通用关键词
        keywords.extend(['nostalgia', 'memory'])

        return ','.join(keywords[:4])  # 最多4个关键词


def get_image_generator(service: str = None) -> ImageGenerator:
    """获取图片生成器实例"""
    if service is None:
        service = APIConfig.IMAGE_SERVICE

    generators = {
        'dalle': DALLEGenerator,
        'stability': StabilityAIGenerator,
        'replicate': ReplicateGenerator,
        'unsplash': UnsplashGenerator
    }

    generator_class = generators.get(service, UnsplashGenerator)
    return generator_class()
