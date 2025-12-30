"""
多智能体系统 - MOMO情绪疗愈系统
包含：情绪分析、诗歌生成、音乐推荐、图片生成四个智能体
"""

import requests
import json
import random
from typing import Dict, List, Any
from abc import ABC, abstractmethod

# 导入API适配器
try:
    from image_api import get_image_generator
    from music_api import get_music_generator
    from config import APIConfig
    USE_ADVANCED_API = True
except ImportError:
    print("Warning: API modules not found. Using fallback implementations.")
    USE_ADVANCED_API = False


class Agent(ABC):
    """智能体基类"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理输入数据并返回结果"""
        pass


class EmotionAnalysisAgent(Agent):
    """情绪分析智能体 - 使用EEG模型分析情绪"""

    def __init__(self):
        super().__init__("EmotionAnalysisAgent")

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析EEG数据，返回情绪分类结果
        input_data: {'eeg_data': [...]}
        """
        # 模拟情绪分类（实际应用中会使用训练好的模型）
        emotions = ["positive", "negative", "neutral"]
        emotion = random.choice(emotions)

        return {
            'status': 'success',
            'emotion': emotion,
            'confidence': random.uniform(0.7, 0.95)
        }


class PoemGenerationAgent(Agent):
    """诗歌生成智能体 - 使用LLM生成个性化诗歌"""

    def __init__(self, api_key: str):
        super().__init__("PoemGenerationAgent")
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/chat/completions"

        # 情绪库：不同情绪对应的提示词策略
        self.emotion_library = {
            "positive": "loyally showcase my emotions as if you are me and have been through the events I described. Emphasize the positive emotions I am feeling in a tangible and relatable way.",
            "negative": "for the first half of the poem, loyally showcase my emotions as if you are me and have been through the events I described. For the second half of the poem, revisit the events with a more positive mindset, for example think about how everything has a value and you can find beauty in small things in life. Do not write 'first half' or 'second half' directly in your poem. Include only the poem itself and nothing more.",
            "neutral": "for the first half of the poem, loyally showcase my emotions as if you are me and have been through the events I described. For the second half of the poem, revisit the events with a more positive mindset, for example think about how everything has a value and you can find beauty in small things in life. Do not write 'first half' or 'second half' directly in your poem. Include only the poem itself and nothing more."
        }

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成个性化诗歌
        input_data: {
            'emotion': str,
            'user_data': {...}
        }
        """
        emotion = input_data.get('emotion')
        user_data = input_data.get('user_data', {})

        # 构建提示词
        emotion_prompt = self.emotion_library.get(emotion, "cheer me up")

        # 提取用户信息
        gender = user_data.get('gender')
        age = user_data.get('age')
        occupation = user_data.get('occupation')
        relationship = user_data.get('relationship_with_person')
        referral = user_data.get('how_you_refer_to_person')
        event = user_data.get('event_involving_person')
        place = user_data.get('place_where_event_occured')

        # 感官细节
        visual = user_data.get('visual_detail', '')
        auditory = user_data.get('auditory_detail', '')
        tactile = user_data.get('tactile_detail', '')

        # 构建细节描述
        details = []
        if visual:
            details.append(f"I saw {visual}")
        if auditory:
            details.append(f"I heard {auditory}")
        if tactile:
            details.append(f"I touched {tactile}")
        details_str = ". ".join(details) + "." if details else ""

        # 完整提示词
        prompt = f"I am a {gender}, {age} years old, and my occupation is or was: {occupation}. I have a {relationship} whom I refer to as {referral}. I experienced the following event:{event}. This event occured at this place: {place} and I remember these details: {details_str}.If one or more of these details say '0', it means that I do not remember this detail. I am feeling {emotion} right now. Please generate a modern poem to: {emotion_prompt}. You should reference poets with simple language such as George Orwell, but do not use vocabulary that is too archaic. Do not quote George Orwell in any way and do not use the word'Orwell' in the poem. In other words, write in such a way that resonates with me, who is actually an Alzheimer patient, but be congruous and clear. Do not make up details, sensory or otherwise, that are not provided by me. Avoiding using the phrase 'But wait', and use italics instead of asterisks to emphasize a word or phrase. Do not give the poem a title."

        # 调用API
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            data = {
                "model": "deepseek-reasoner",
                "messages": [
                    {"role": "system", "content": "You are a modern poet who knows how to create poetry based on specific events and personal relationships"},
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            }

            response = requests.post(self.api_url, headers=headers, json=data)
            poem = response.json()['choices'][0]['message']['content']

            return {
                'status': 'success',
                'poem': poem,
                'prompt': prompt
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'poem': "Sorry, I cannot generate a poem right now. Please try again later."
            }


class MusicRecommendationAgent(Agent):
    """音乐推荐智能体 - 根据情绪和诗歌内容推荐音乐"""

    def __init__(self):
        super().__init__("MusicRecommendationAgent")

        # 情绪到音乐类型的映射
        self.emotion_music_mapping = {
            "positive": {
                "genres": ["uplifting", "peaceful", "hopeful"],
                "tempo": "moderate to fast",
                "mood": "bright and warm",
                "instruments": ["piano", "strings", "light percussion"]
            },
            "negative": {
                "genres": ["reflective", "melancholic turning hopeful"],
                "tempo": "slow to moderate",
                "mood": "somber transitioning to hopeful",
                "instruments": ["piano", "cello", "violin"]
            },
            "neutral": {
                "genres": ["ambient", "contemplative"],
                "tempo": "moderate",
                "mood": "calm and balanced",
                "instruments": ["piano", "soft strings", "ambient pads"]
            }
        }

        # 预定义的音乐库（可以替换为实际的音乐数据库或API）
        self.music_library = {
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

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        推荐/生成背景音乐
        input_data: {
            'emotion': str,
            'poem': str (可选)
        }
        """
        emotion = input_data.get('emotion', 'neutral')
        poem = input_data.get('poem', '')

        # 使用高级音乐生成API
        if USE_ADVANCED_API:
            try:
                # 获取音乐生成器
                music_gen = get_music_generator()

                # 生成音乐
                result = music_gen.generate(
                    prompt=poem[:200] if poem else "",
                    emotion=emotion,
                    duration=30
                )

                if result['status'] == 'success':
                    return {
                        'status': 'success',
                        'music_features': self.emotion_music_mapping.get(emotion, {}),
                        'recommended_music': {
                            'title': result.get('title', 'Generated Music'),
                            'url': result.get('url', ''),
                            'description': result.get('description', '')
                        },
                        'explanation': f"Generated music that matches your {emotion} emotion"
                    }
            except Exception as e:
                print(f"[MusicAgent] API failed: {e}, using fallback")

        # 备用方案：使用预设音乐库
        music_features = self.emotion_music_mapping.get(emotion, self.emotion_music_mapping['neutral'])
        available_music = self.music_library.get(emotion, self.music_library['neutral'])
        selected_music = random.choice(available_music) if available_music else None

        return {
            'status': 'success',
            'music_features': music_features,
            'recommended_music': selected_music,
            'explanation': f"Selected music that matches your {emotion} emotion with {music_features['mood']} mood."
        }


class ImageGenerationAgent(Agent):
    """图片生成智能体 - 根据场景描述生成图片"""

    def __init__(self, api_key: str = None):
        super().__init__("ImageGenerationAgent")
        self.api_key = api_key

        # 可以使用的图片生成API：
        # 1. DALL-E (OpenAI)
        # 2. Stable Diffusion
        # 3. Midjourney API
        # 4. 国内：通义万相、文心一格等

    def _build_prompt(self, user_data: Dict[str, Any], emotion: str) -> str:
        """构建图片生成提示词（包含所有表单内容）"""

        # 提取所有表单信息
        place = user_data.get('place_where_event_occured', 'a peaceful place')
        event = user_data.get('event_involving_person', '')
        relationship = user_data.get('relationship_with_person', '')
        person_name = user_data.get('how_you_refer_to_person', '')
        visual = user_data.get('visual_detail', '')
        auditory = user_data.get('auditory_detail', '')
        tactile = user_data.get('tactile_detail', '')

        # 移除艺术风格映射，改为照片风格（因为已在image_api中处理）
        # 构建详细的场景描述
        prompt_parts = []

        # 基础场景
        prompt_parts.append(f"A memory scene at {place}")

        # 添加事件描述
        if event and event != '0':
            prompt_parts.append(f"showing the event: {event}")

        # 添加人物信息
        if relationship and person_name:
            if relationship != '0' and person_name != '0':
                prompt_parts.append(f"with {person_name} ({relationship})")

        # 添加视觉细节
        if visual and visual != '0':
            prompt_parts.append(f"visual elements: {visual}")

        # 添加听觉细节（转化为视觉描述）
        if auditory and auditory != '0':
            prompt_parts.append(f"capturing the atmosphere of {auditory}")

        # 添加触觉细节（转化为视觉描述）
        if tactile and tactile != '0':
            prompt_parts.append(f"showing textures and materials related to {tactile}")

        # 组合所有部分
        prompt = ", ".join(prompt_parts)

        # 添加照片风格要求（不添加艺术风格，因为image_api会处理）
        prompt += ". A realistic memory photograph suitable for Alzheimer's patients to recall memories, highly detailed, emotionally resonant."

        return prompt

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成场景图片
        input_data: {
            'emotion': str,
            'user_data': {...}
        }
        """
        emotion = input_data.get('emotion', 'neutral')
        user_data = input_data.get('user_data', {})

        # 构建图片生成提示词
        image_prompt = self._build_prompt(user_data, emotion)

        # 使用高级图片生成API
        if USE_ADVANCED_API:
            try:
                # 获取图片生成器
                image_gen = get_image_generator()

                # 生成图片
                result = image_gen.generate(
                    prompt=image_prompt,
                    emotion=emotion
                )

                if result['status'] == 'success':
                    return {
                        'status': 'success',
                        'image_url': result.get('image_url', ''),
                        'image_prompt': image_prompt,
                        'description': f"Generated image based on the scene at {user_data.get('place_where_event_occured', 'the remembered place')}",
                        'service': result.get('service', 'unknown')
                    }
            except Exception as e:
                print(f"[ImageAgent] API failed: {e}, using fallback")

        # 备用方案：使用Unsplash占位图片
        try:
            place = user_data.get('place_where_event_occured', 'nature')
            placeholder_keywords = place.replace(' ', ',')
            image_url = f"https://source.unsplash.com/1024x1024/?{placeholder_keywords},memory,nostalgia"

            return {
                'status': 'success',
                'image_url': image_url,
                'image_prompt': image_prompt,
                'description': f"Memory scene at {user_data.get('place_where_event_occured', 'the remembered place')}",
                'note': 'Using Unsplash placeholder. Configure API for AI-generated images.'
            }

        except Exception as e:
            return {
                'status': 'success',
                'image_url': 'https://source.unsplash.com/1024x1024/?memory,nostalgia,peaceful',
                'image_prompt': image_prompt,
                'description': 'A peaceful memory scene',
                'note': 'Using fallback image'
            }


class CoordinatorAgent(Agent):
    """协调器智能体 - 协调各个智能体的工作流程"""

    def __init__(self, deepseek_api_key: str):
        super().__init__("CoordinatorAgent")

        # 初始化各个智能体
        self.emotion_agent = EmotionAnalysisAgent()
        self.poem_agent = PoemGenerationAgent(deepseek_api_key)
        self.music_agent = MusicRecommendationAgent()
        self.image_agent = ImageGenerationAgent()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        协调整个工作流程
        input_data: {
            'eeg_data': [...],
            'user_data': {...}
        }
        """
        results = {
            'status': 'processing',
            'steps': []
        }

        # 步骤1: 情绪分析
        print(f"[{self.name}] Step 1: Emotion Analysis")
        emotion_result = self.emotion_agent.process({
            'eeg_data': input_data.get('eeg_data', [])
        })
        results['steps'].append({'step': 'emotion_analysis', 'result': emotion_result})

        if emotion_result['status'] != 'success':
            results['status'] = 'error'
            results['error'] = 'Emotion analysis failed'
            return results

        emotion = emotion_result['emotion']
        results['emotion'] = emotion

        # 步骤2: 诗歌生成
        print(f"[{self.name}] Step 2: Poem Generation (Emotion: {emotion})")
        poem_result = self.poem_agent.process({
            'emotion': emotion,
            'user_data': input_data.get('user_data', {})
        })
        results['steps'].append({'step': 'poem_generation', 'result': poem_result})
        results['poem'] = poem_result.get('poem', '')

        # 步骤3: 音乐推荐（并行）
        print(f"[{self.name}] Step 3: Music Recommendation")
        music_result = self.music_agent.process({
            'emotion': emotion,
            'poem': results['poem']
        })
        results['steps'].append({'step': 'music_recommendation', 'result': music_result})
        results['music'] = music_result.get('recommended_music', {})

        # 步骤4: 图片生成（并行）
        print(f"[{self.name}] Step 4: Image Generation")
        image_result = self.image_agent.process({
            'emotion': emotion,
            'user_data': input_data.get('user_data', {})
        })
        results['steps'].append({'step': 'image_generation', 'result': image_result})
        results['image'] = {
            'url': image_result.get('image_url', ''),
            'description': image_result.get('description', ''),
            'prompt': image_result.get('image_prompt', '')
        }

        # 完成
        results['status'] = 'success'
        print(f"[{self.name}] All steps completed successfully!")

        return results
