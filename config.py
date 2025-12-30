"""
API配置文件 - MOMO多智能体系统
支持多种图片生成和音乐生成API
"""

import os


class APIConfig:
    """API配置类"""

    # ============ 基础配置 ============
    DEBUG = True

    # ============ Deepseek API（诗歌生成）============
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', 'sk-3be19817f3ee47849920179aaeb9cc21')

    # ============ 图片生成API配置 ============
    # 可选服务：'dalle', 'stability', 'replicate', 'tongyi', 'unsplash'
    IMAGE_SERVICE = os.environ.get('IMAGE_SERVICE', 'dalle')

    # OpenAI DALL-E (使用ChatAnywhere代理)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', 'sk-vWPlVDMJizXLti9l69ah2W5l0bdGKxwh1OnBBRuhwtPJL4ed')
    OPENAI_BASE_URL = os.environ.get('OPENAI_BASE_URL', 'https://api.chatanywhere.tech/v1')
    DALLE_MODEL = 'dall-e-3'  # 或 'dall-e-2'
    DALLE_SIZE = '1024x1024'  # 1024x1024, 1792x1024, 1024x1792
    DALLE_QUALITY = 'standard'  # 'standard' 或 'hd'

    # Stability AI (Stable Diffusion)
    STABILITY_API_KEY = os.environ.get('STABILITY_API_KEY', '')
    STABILITY_ENGINE = 'stable-diffusion-xl-1024-v1-0'

    # Replicate (开源模型)
    REPLICATE_API_KEY = os.environ.get('REPLICATE_API_KEY', '')

    # 通义万相（阿里云）
    TONGYI_API_KEY = os.environ.get('TONGYI_API_KEY', '')
    TONGYI_APP_KEY = os.environ.get('TONGYI_APP_KEY', '')

    # ============ TTS语音合成API配置 ============
    # 可选服务：'openai', 'edge'
    TTS_SERVICE = os.environ.get('TTS_SERVICE', 'openai')

    # ============ 音乐生成API配置 ============
    # 可选服务：'suno', 'stable-audio', 'musicgen', 'library'
    MUSIC_SERVICE = os.environ.get('MUSIC_SERVICE', 'stable-audio')

    # Suno AI
    SUNO_API_KEY = os.environ.get('SUNO_API_KEY', '')

    # Stability AI (Stable Audio)
    STABLE_AUDIO_API_KEY = os.environ.get('STABLE_AUDIO_API_KEY', '')

    # Replicate MusicGen
    MUSICGEN_USE_REPLICATE = True

    # 音乐生成参数
    MUSIC_DURATION = 30  # 秒
    MUSIC_STYLE_MAPPING = {
        'positive': 'uplifting, cheerful, acoustic, piano, optimistic, major key',
        'negative': 'melancholic, reflective, emotional, piano, strings, minor key transitioning to hopeful',
        'neutral': 'ambient, calm, peaceful, soft piano, meditative, relaxing'
    }

    # ============ 本地音乐库（备用方案）============
    MUSIC_LIBRARY = {
        "positive": [
            {
                "title": "Morning Light",
                "url": "https://www.bensound.com/bensound-music/bensound-ukulele.mp3",
                "description": "Uplifting acoustic melody with gentle piano"
            },
            {
                "title": "Sunny Days",
                "url": "https://www.bensound.com/bensound-music/bensound-happyrock.mp3",
                "description": "Cheerful and optimistic tune"
            }
        ],
        "negative": [
            {
                "title": "Reflection",
                "url": "https://www.bensound.com/bensound-music/bensound-slowmotion.mp3",
                "description": "Contemplative piano with emotional depth"
            },
            {
                "title": "New Dawn",
                "url": "https://www.bensound.com/bensound-music/bensound-epic.mp3",
                "description": "From melancholic to hopeful journey"
            }
        ],
        "neutral": [
            {
                "title": "Peaceful Mind",
                "url": "https://www.bensound.com/bensound-music/bensound-relaxing.mp3",
                "description": "Calm and soothing ambient music"
            },
            {
                "title": "Gentle Thoughts",
                "url": "https://www.bensound.com/bensound-music/bensound-piano.mp3",
                "description": "Soft piano meditation"
            }
        ]
    }

    # ============ 日志配置 ============
    LOG_LEVEL = 'INFO'

    @classmethod
    def validate(cls):
        """验证必要的API密钥是否配置"""
        issues = []

        # 检查诗歌生成
        if not cls.DEEPSEEK_API_KEY or cls.DEEPSEEK_API_KEY == '':
            issues.append("DEEPSEEK_API_KEY not configured")

        # 检查图片生成
        if cls.IMAGE_SERVICE == 'dalle' and not cls.OPENAI_API_KEY:
            issues.append("OPENAI_API_KEY not configured for DALL-E")
        elif cls.IMAGE_SERVICE == 'stability' and not cls.STABILITY_API_KEY:
            issues.append("STABILITY_API_KEY not configured")
        elif cls.IMAGE_SERVICE == 'tongyi' and not cls.TONGYI_API_KEY:
            issues.append("TONGYI_API_KEY not configured")

        # 检查音乐生成
        if cls.MUSIC_SERVICE == 'suno' and not cls.SUNO_API_KEY:
            issues.append("SUNO_API_KEY not configured")
        elif cls.MUSIC_SERVICE == 'stable-audio' and not cls.STABLE_AUDIO_API_KEY:
            issues.append("STABLE_AUDIO_API_KEY not configured")
        elif cls.MUSIC_SERVICE == 'musicgen' and not cls.REPLICATE_API_KEY:
            issues.append("REPLICATE_API_KEY not configured for MusicGen")

        return issues

    @classmethod
    def print_status(cls):
        """打印配置状态"""
        print("\n" + "="*60)
        print("API Configuration Status")
        print("="*60)
        print(f"Deepseek (Poem):  {'✓' if cls.DEEPSEEK_API_KEY else '✗'}")
        print(f"Image Service:    {cls.IMAGE_SERVICE}")
        print(f"Music Service:    {cls.MUSIC_SERVICE}")
        print("="*60 + "\n")
