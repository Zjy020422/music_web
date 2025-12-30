# MOMO V7 - 多智能体记忆系统

## 🌟 概述

MOMO V7 是一个基于多智能体架构的情绪疗愈系统，专为阿尔茨海默症患者设计。系统通过四个协同工作的智能体，将用户的记忆转化为诗歌、音乐和图像，帮助患者回忆和保存珍贵记忆。

## 🤖 多智能体架构

### 协调器智能体 (CoordinatorAgent)
- **职责**：协调整个工作流程，管理各智能体的执行顺序
- **功能**：接收用户输入，分配任务给各专业智能体，整合返回结果

### 1. 情绪分析智能体 (EmotionAnalysisAgent)
- **职责**：分析EEG脑电信号，识别用户当前情绪状态
- **输入**：脑电信号数据数组
- **输出**：情绪分类（positive/negative/neutral）及置信度

### 2. 诗歌生成智能体 (PoemGenerationAgent)
- **职责**：基于情绪和用户记忆生成个性化诗歌
- **API**：Deepseek Reasoner 模型
- **策略**：
  - **Positive**: 强调积极情感
  - **Negative**: 前半展现情绪，后半转向积极思考
  - **Neutral**: 引导发现生活中的美好

### 3. 音乐推荐智能体 (MusicRecommendationAgent)
- **职责**：根据情绪推荐匹配的背景音乐
- **音乐库映射**：
  - **Positive**: 欢快、明亮的音乐
  - **Negative**: 反思、渐转希望的音乐
  - **Neutral**: 平静、冥想的音乐

### 4. 图片生成智能体 (ImageGenerationAgent)
- **职责**：根据场景描述生成记忆场景图片
- **当前实现**：使用Unsplash占位图片
- **可扩展**：支持DALL-E、Stable Diffusion等API

## 📦 系统架构

```
codeV7/
├── app.py                      # Flask应用主文件
├── multi_agent_system.py       # 多智能体系统核心
├── templates/
│   ├── home.html              # 首页
│   ├── index.html             # 应用主页面（已集成多智能体）
│   └── landing.html
├── static/
│   ├── css/
│   ├── images/
│   └── media/
└── README_MULTI_AGENT.md      # 本文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install flask requests
```

### 2. 启动应用

```bash
cd F:\work\2025work\sure\momo\code\website\codeV7
python app.py
```

启动后你会看到：

```
============================================================
MOMO V7 - Multi-Agent Memory System Starting...
============================================================
Coordinator: CoordinatorAgent
  ├── EmotionAnalysisAgent
  ├── PoemGenerationAgent
  ├── MusicRecommendationAgent
  └── ImageGenerationAgent
============================================================
```

### 3. 访问应用

- **首页**: http://localhost:5000/
- **应用页面**: http://localhost:5000/app
- **健康检查**: http://localhost:5000/health

## 🔌 API 接口

### 1. 完整记忆生成（多智能体）

**端点**: `POST /generate_complete_memory`

**请求体**:
```json
{
  "eeg_data": [/* EEG数据数组 */],
  "user_data": {
    "gender": "male",
    "age": 75,
    "occupation": "teacher",
    "relationship_with_person": "wife",
    "how_you_refer_to_person": "Mary",
    "event_involving_person": "our first dance",
    "place_where_event_occured": "the town hall",
    "visual_detail": "her blue dress",
    "auditory_detail": "the jazz music",
    "tactile_detail": "her warm hand"
  }
}
```

**响应**:
```json
{
  "status": "success",
  "emotion": "positive",
  "poem": "诗歌内容...",
  "music": {
    "title": "Morning Light",
    "url": "https://...",
    "description": "Uplifting acoustic melody"
  },
  "image": {
    "url": "https://...",
    "description": "A memory at the town hall",
    "prompt": "图片生成提示词"
  },
  "processing_steps": 4
}
```

### 2. 传统接口（保持向后兼容）

- `POST /classify_emotion` - 单独情绪分类
- `POST /generate_poem` - 单独诗歌生成
- `POST /recommend_music` - 单独音乐推荐
- `POST /generate_image` - 单独图片生成

## 🎨 前端功能

### 用户流程

1. **情绪检测**
   - 自动分析EEG信号
   - 显示情绪状态（Positive/Negative/Neutral）

2. **填写记忆表单**
   - 基本信息（性别、年龄、职业）
   - 记忆相关人物
   - 事件描述和地点
   - 感官细节（视觉、听觉、触觉）

3. **生成完整记忆包**
   - 点击"Generate Poem"按钮
   - 显示加载动画和引言
   - 逐行展示诗歌
   - 显示记忆场景图片
   - 播放匹配的背景音乐

4. **下载和分享**
   - 下载诗歌Word文档
   - 下载完整记忆包（未来功能）

## 🔧 配置选项

### API密钥配置

在 `app.py` 中修改：

```python
DEEPSEEK_API_KEY = 'your-api-key-here'
```

### 音乐库自定义

在 `multi_agent_system.py` 的 `MusicRecommendationAgent` 类中修改 `music_library`:

```python
self.music_library = {
    "positive": [
        {
            "title": "Your Song Title",
            "url": "https://your-music-url.mp3",
            "description": "Song description"
        }
    ],
    # ... 其他情绪
}
```

### 图片生成服务

要使用真实的AI图片生成服务，修改 `ImageGenerationAgent.process()` 方法：

```python
# 示例：使用DALL-E
import openai
openai.api_key = "your-openai-key"

response = openai.Image.create(
    prompt=image_prompt,
    n=1,
    size="1024x1024"
)
image_url = response['data'][0]['url']
```

## 📊 系统监控

访问 `/health` 端点查看系统状态：

```json
{
  "status": "healthy",
  "version": "v7-multi-agent",
  "agents": {
    "coordinator": "CoordinatorAgent",
    "emotion_analysis": "EmotionAnalysisAgent",
    "poem_generation": "PoemGenerationAgent",
    "music_recommendation": "MusicRecommendationAgent",
    "image_generation": "ImageGenerationAgent"
  }
}
```

## 🎯 下一步开发

### 短期目标

1. **集成真实EEG模型**
   - 加载训练好的CNN/LSTM模型
   - 替换模拟情绪分类

2. **AI图片生成**
   - 集成DALL-E或Stable Diffusion
   - 生成高质量记忆场景图片

3. **音乐生成**
   - 使用MusicGen或Stable Audio
   - 生成定制化背景音乐

### 长期目标

1. **多模态融合**
   - 结合语音输入
   - 支持照片上传辅助回忆

2. **个性化学习**
   - 学习用户偏好
   - 优化推荐算法

3. **社交分享**
   - 生成分享卡片
   - 家庭记忆墙功能

## 🐛 故障排除

### 问题1：诗歌生成失败

- 检查Deepseek API密钥是否正确
- 确认网络连接正常
- 查看控制台错误信息

### 问题2：音乐无法播放

- 确认音乐URL可访问
- 检查浏览器是否支持audio标签
- 查看浏览器控制台CORS错误

### 问题3：图片无法显示

- Unsplash图片需要网络连接
- 检查防火墙设置
- 尝试刷新页面

## 📝 日志

系统会在控制台输出详细日志：

```
============================================================
Processing memory generation with multi-agent system...
============================================================
[CoordinatorAgent] Step 1: Emotion Analysis
[CoordinatorAgent] Step 2: Poem Generation (Emotion: positive)
[CoordinatorAgent] Step 3: Music Recommendation
[CoordinatorAgent] Step 4: Image Generation
[CoordinatorAgent] All steps completed successfully!
✓ Generation completed: Emotion=positive
============================================================
```

## 📄 许可

MOMO V7 - 2025 | 用于阿尔茨海默症患者记忆疗愈的多智能体系统

## 👥 贡献

欢迎提交问题和改进建议！

---

**Made with ❤️ for Alzheimer's patients and their families**
