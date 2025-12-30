"""
音频混合模块 - 将TTS朗读与背景音乐混合
"""

import os
import io
import base64
from typing import Dict, Any, Optional


class AudioMixer:
    """音频混合器"""

    def __init__(self):
        self.background_music_dir = os.path.join('static', 'audio', 'background')

        # 背景音乐库（基于情绪）
        self.music_library = {
            'positive': {
                'file': 'happy_background.mp3',
                'url': '/static/audio/background/happy_background.mp3',
                'fallback': 'https://cdn.pixabay.com/download/audio/2022/03/10/audio_d1718ab41b.mp3'
            },
            'negative': {
                'file': 'calm_background.mp3',
                'url': '/static/audio/background/calm_background.mp3',
                'fallback': 'https://cdn.pixabay.com/download/audio/2021/08/04/audio_0625c1539c.mp3'
            },
            'neutral': {
                'file': 'peaceful_background.mp3',
                'url': '/static/audio/background/peaceful_background.mp3',
                'fallback': 'https://cdn.pixabay.com/download/audio/2022/05/27/audio_1808fbf07a.mp3'
            }
        }

    def mix_with_pydub(self, narration_audio: bytes, emotion: str) -> Optional[bytes]:
        """使用pydub混合音频（需要ffmpeg）"""
        try:
            from pydub import AudioSegment
            from pydub.playback import play
            import requests

            print("[AudioMixer] Using pydub for audio mixing...")

            # 加载朗读音频
            narration = AudioSegment.from_mp3(io.BytesIO(narration_audio))

            # 获取背景音乐
            music_info = self.music_library.get(emotion, self.music_library['neutral'])

            # 尝试加载本地文件，失败则下载
            try:
                music_path = os.path.join(self.background_music_dir, music_info['file'])
                background = AudioSegment.from_mp3(music_path)
                print(f"[AudioMixer] Loaded local music: {music_path}")
            except:
                # 下载背景音乐
                print(f"[AudioMixer] Downloading background music from {music_info['fallback']}")
                response = requests.get(music_info['fallback'], timeout=30)
                background = AudioSegment.from_mp3(io.BytesIO(response.content))

            # 调整背景音乐长度匹配朗读
            if len(background) < len(narration):
                # 如果背景音乐太短，循环播放
                loops_needed = (len(narration) // len(background)) + 1
                background = background * loops_needed

            # 裁剪背景音乐到朗读长度
            background = background[:len(narration)]

            # 降低背景音乐音量（-15dB，让朗读更清晰）
            background = background - 15

            # 混合音频
            mixed = narration.overlay(background)

            # 淡入淡出效果
            mixed = mixed.fade_in(1000).fade_out(2000)

            # 导出为MP3
            output = io.BytesIO()
            mixed.export(output, format='mp3', bitrate='128k')
            output.seek(0)

            print("[AudioMixer] ✓ Audio mixed successfully with pydub")
            return output.read()

        except ImportError:
            print("[AudioMixer] ✗ pydub not installed")
            return None
        except Exception as e:
            print(f"[AudioMixer] ✗ Error in pydub mixing: {str(e)}")
            return None

    def mix_with_web_audio(self, narration_audio_base64: str, emotion: str) -> Dict[str, Any]:
        """使用Web Audio API混合（客户端混合）"""
        print("[AudioMixer] Preparing for Web Audio API mixing...")

        music_info = self.music_library.get(emotion, self.music_library['neutral'])

        return {
            'method': 'web_audio',
            'narration_base64': narration_audio_base64,
            'background_music_url': music_info['fallback'],
            'background_volume': 0.3,  # 30%音量
            'narration_volume': 1.0    # 100%音量
        }

    def mix(self, narration_audio_base64: str, emotion: str) -> Dict[str, Any]:
        """
        混合音频的主方法
        优先使用pydub，失败则返回Web Audio方案
        """
        # 解码base64
        narration_bytes = base64.b64decode(narration_audio_base64)

        # 尝试使用pydub混合
        mixed_audio = self.mix_with_pydub(narration_bytes, emotion)

        if mixed_audio:
            # 成功混合，返回混合后的音频
            mixed_base64 = base64.b64encode(mixed_audio).decode('utf-8')
            return {
                'status': 'success',
                'method': 'pydub',
                'audio_base64': mixed_base64,
                'audio_format': 'mp3',
                'mixed': True,
                'emotion': emotion
            }
        else:
            # pydub失败，返回Web Audio方案
            print("[AudioMixer] Falling back to Web Audio API mixing")
            web_audio_data = self.mix_with_web_audio(narration_audio_base64, emotion)
            return {
                'status': 'success',
                'method': 'web_audio',
                'narration_base64': web_audio_data['narration_base64'],
                'background_music_url': web_audio_data['background_music_url'],
                'background_volume': web_audio_data['background_volume'],
                'narration_volume': web_audio_data['narration_volume'],
                'mixed': False,
                'emotion': emotion,
                'note': 'Using client-side Web Audio API mixing. Install pydub and ffmpeg for server-side mixing.'
            }


def get_audio_mixer() -> AudioMixer:
    """获取音频混合器实例"""
    return AudioMixer()
