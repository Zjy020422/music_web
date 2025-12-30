from flask import Flask, render_template, request, jsonify, send_file
import random
import time
import requests  # 用于调用Deepseek API
import os
import base64
import io
from multi_agent_system import CoordinatorAgent
from tts_api import get_tts_generator
from audio_mixer import get_audio_mixer

app = Flask(__name__)

# 初始化多智能体协调器
DEEPSEEK_API_KEY = 'sk-3be19817f3ee47849920179aaeb9cc21'
coordinator = CoordinatorAgent(DEEPSEEK_API_KEY)

# 情绪库：三种情绪及其对应的提示词部分
emotion_library = {
    "positive": "loyally showcase my emotions as if \
    you are me and have been through the events I described. \
    Emphasize the positive emotions I am feeling in a tangible and relatable way.",
    "negative": "for the first half of the poem, loyally showcase my emotions \
    as if you are me and have been through the events I described. \
    For the second half of the poem, revisit the events with a more positive mindset, \
    for example think about how everything has a value and \
    you can find beauty in small things in life. \
    Do not write 'first half' or 'second half' directly in your poem. Include only the poem itself\
    and nothing more.",
    "neutral": "for the first half of the poem, loyally showcase my emotions \
    as if you are me and have been through the events I described. \
    For the second half of the poem, revisit the events with a more positive mindset, \
    for example think about how everything has a value and \
    you can find beauty in small things in life. \
    Do not write 'first half' or 'second half' directly in your poem. Include only the poem itself\
    and nothing more."

}

# 模拟已训练好的情绪分类模型
class MockEmotionModel:
    def __init__(self):
        # 模拟模型加载
        print("Loading emotion classification model...")
        time.sleep(1)  # 模拟加载延迟
        print("Model loaded successfully")
        
    def predict(self, eeg_data):
        # 模拟预测过程
        time.sleep(2)  # 模拟预测延迟
        
        # 随机返回三种情绪之一（实际应用中应基于真实模型预测）
        emotions = ["positive", "negative", "neutral"]
        return random.choice(emotions)

# 初始化模型
emotion_model = MockEmotionModel()

# 模拟接收脑电信号并进行情绪分类
@app.route('/classify_emotion', methods=['POST'])
def classify_emotion():
    # 在实际应用中，这里会接收来自头套的脑电信号
    # 这里使用模拟数据
    eeg_data = request.json.get('eeg_data', [])
    
    # 使用模型进行情绪分类
    emotion = emotion_model.predict(eeg_data)
    
    # 返回分类结果
    return jsonify({
        'status': 'success',
        'emotion': emotion
    })

# 生成提示词并调用Deepseek API生成诗歌
@app.route('/generate_poem', methods=['POST'])
def generate_poem():
    # 获取用户属性、情绪和事件相关信息
    user_data = request.json
    emotion = user_data.get('emotion')
    gender = user_data.get('gender')
    age = user_data.get('age')
    occupation = user_data.get('occupation')
    
    # 新增的必填项
    relationship = user_data.get('relationship_with_person')
    referral = user_data.get('how_you_refer_to_person')
    event = user_data.get('event_involving_person')
    place = user_data.get('place_where_event_occured')
    
    # 新增的非必填项
    visual = user_data.get('visual_detail', '')
    auditory = user_data.get('auditory_detail', '')
    tactile = user_data.get('tactile_detail', '')

    # 根据情绪获取对应的提示词部分
    emotion_prompt = emotion_library.get(emotion, "cheer me up")
    
    # 构建细节描述字符串（处理非必填项）
    details = []
    if visual:
        details.append(f"I saw {visual}")
    if auditory:
        details.append(f"I heard {auditory}")
    if tactile:
        details.append(f"I touched {tactile}")
    details_str = ". ".join(details) + "." if details else ""
    
    # 构建英文提示词（聚焦具体事件）
    # prompt = f"I am a {gender}, {age} years old, working as a {occupation}. I am feeling {emotion}. The person I want to write about is my {relationship}, whom I call {referral}. A meaningful event with them was: {event}, which happened at {place}. {details_str} Please generate a modern poem about this event to {emotion_prompt}."
    prompt = f"I am a {gender}, {age} years old, and my occupation is or was: {occupation}.\
    I have a {relationship} whom I refer to as {referral}.\
    I experienced the following event:{event}.\
    This event occured at this place: {place} and I remember these details:\
    {details_str}.If one or more of these details say '0', it means\
    that I do not remember this detail.\
    I am feeling {emotion} right now. Please generate a modern poem to: {emotion_prompt}.\
    You should reference poets with simple language such as George Orwell, but do not use vocabulary\
    that is too archaic. Do not quote George Orwell in any way and do not use the word'Orwell' in the poem.\
    In other words, write in such a way that resonates with me,\
    who is actually an Alzheimer patient, but be congruous and clear. Do not make up details, sensory or otherwise,\
    that are not provided by me. Avoiding using the phrase 'But wait', and use italics instead of asterisks to emphasize \
    a word or phrase. Do not give the poem a title."
   
    # 调用Deepseek API生成诗歌
    try:
        deepseek_api_key = 'sk-3be19817f3ee47849920179aaeb9cc21'
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {deepseek_api_key}"
            }
        data = {
        "model": "deepseek-reasoner",  # 指定使用的模型
        "messages": [
        {"role": "system", "content": "You are a modern poet who knows how to create poetry based on specific events and personal relationships"},
        {"role": "user", "content": prompt}
        ],
        "stream": False  # 关闭流式传输
        }

        poem_llm = requests.post(url, headers=headers, json=data)
        poem = poem_llm.json()['choices'][0]['message']['content']
        
        # 模拟API调用延迟
        time.sleep(1)
         
        return jsonify({
            'status': 'success',
            'prompt': prompt,
            'poem': poem
        })
    except Exception as e:
        poem = "Sorry, I cannot generate a poem right now. Please try again later."
        return jsonify({
            'status': 'success',
            'prompt': prompt,
            'poem': poem
        })

# 首页路由（使用dopetrope模板）
@app.route('/')
def home():
    return render_template('home.html')

# 应用页面路由
@app.route('/app')
def app_page():
    return render_template('index.html')


# ============ 多智能体新增接口 ============

@app.route('/generate_complete_memory', methods=['POST'])
def generate_complete_memory():
    """
    完整记忆生成接口 - 使用多智能体系统生成诗歌、音乐和图片
    """
    try:
        request_data = request.json
        user_data = request_data.get('user_data', {})
        eeg_data = request_data.get('eeg_data', [])

        print("\n" + "="*60)
        print("Processing memory generation with multi-agent system...")
        print("="*60)

        # 使用协调器处理整个流程
        result = coordinator.process({
            'eeg_data': eeg_data,
            'user_data': user_data
        })

        # 构建响应
        response = {
            'status': result['status'],
            'emotion': result.get('emotion', 'neutral'),
            'poem': result.get('poem', ''),
            'music': result.get('music', {}),
            'image': result.get('image', {}),
            'processing_steps': len(result.get('steps', []))
        }

        print(f"✓ Generation completed: Emotion={response['emotion']}")
        print("="*60 + "\n")

        return jsonify(response)

    except Exception as e:
        print(f"Error in generate_complete_memory: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/recommend_music', methods=['POST'])
def recommend_music():
    """音乐推荐接口"""
    data = request.json
    emotion = data.get('emotion', 'neutral')
    poem = data.get('poem', '')

    result = coordinator.music_agent.process({
        'emotion': emotion,
        'poem': poem
    })

    return jsonify(result)


@app.route('/generate_image', methods=['POST'])
def generate_image():
    """图片生成接口"""
    data = request.json
    emotion = data.get('emotion', 'neutral')
    user_data = data.get('user_data', {})

    result = coordinator.image_agent.process({
        'emotion': emotion,
        'user_data': user_data
    })

    return jsonify(result)


@app.route('/generate_narration', methods=['POST'])
def generate_narration():
    """诗歌语音朗读生成接口（含背景音乐混合）"""
    try:
        data = request.json
        poem = data.get('poem', '')
        emotion = data.get('emotion', 'neutral')

        if not poem:
            return jsonify({
                'status': 'error',
                'message': 'No poem provided'
            }), 400

        print(f"\n[TTS+Music] Generating narration with background music for emotion: {emotion}")

        # 步骤1: 生成TTS语音
        tts_gen = get_tts_generator()
        tts_result = tts_gen.generate(poem, emotion)

        if tts_result['status'] != 'success':
            print(f"[TTS] ✗ Narration generation failed")
            return jsonify(tts_result), 500

        print(f"[TTS] ✓ Narration generated successfully")

        # 步骤2: 混合背景音乐
        audio_mixer = get_audio_mixer()
        mixed_result = audio_mixer.mix(tts_result['audio_base64'], emotion)

        if mixed_result['status'] == 'success':
            if mixed_result['mixed']:
                print(f"[AudioMixer] ✓ Audio mixed successfully using {mixed_result['method']}")
            else:
                print(f"[AudioMixer] Using client-side mixing with Web Audio API")

            return jsonify(mixed_result)
        else:
            # 如果混合失败，返回原始朗读
            print(f"[AudioMixer] ✗ Mixing failed, returning narration only")
            return jsonify(tts_result)

    except Exception as e:
        print(f"[TTS+Music] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/audio/<audio_id>')
def serve_audio(audio_id):
    """提供音频文件服务"""
    # 这个端点用于提供生成的音频文件
    # 在实际应用中，你需要实现音频文件的存储和检索逻辑
    pass


@app.route('/health')
def health():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'version': 'v7-multi-agent-tts',
        'agents': {
            'coordinator': coordinator.name,
            'emotion_analysis': coordinator.emotion_agent.name,
            'poem_generation': coordinator.poem_agent.name,
            'music_recommendation': coordinator.music_agent.name,
            'image_generation': coordinator.image_agent.name
        },
        'features': {
            'tts': True,
            'photorealistic_images': True
        }
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("MOMO V7 - Multi-Agent Memory System Starting...")
    print("="*60)
    print(f"Coordinator: {coordinator.name}")
    print(f"  ├── {coordinator.emotion_agent.name}")
    print(f"  ├── {coordinator.poem_agent.name}")
    print(f"  ├── {coordinator.music_agent.name}")
    print(f"  └── {coordinator.image_agent.name}")
    print("="*60 + "\n")

    # 启动应用，开启调试模式
    app.run(debug=True)