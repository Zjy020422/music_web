# MOMO V7 新功能更新说明

## 🎉 本次更新内容

### 1. 照片级真实图片生成 📸

**改进内容：**
- 修改DALL-E图片生成为照片级真实风格
- 自动添加专业摄影参数（50mm镜头、浅景深、DSLR相机效果）
- 根据情绪自适应照片氛围：
  - **积极情绪**: 温暖自然光、金色时刻、柔和阴影、鲜艳色彩
  - **消极情绪**: 柔和散射光、柔和色调、沉思氛围、柔焦
  - **中性情绪**: 平衡自然光、真实色彩、清晰细节

**技术实现：** `image_api.py:94-114`
```python
def _enhance_for_photorealism(self, prompt: str, emotion: str) -> str:
    photo_prefix = "A highly detailed photorealistic photograph, "
    # ... 情绪自适应照明设置
    photo_suffix = ", {lighting}, high resolution, professional photography, 50mm lens..."
```

**效果对比：**
- 修改前：艺术化、插画风格的图片
- 修改后：接近真实照片的高质量图像

---

### 2. AI诗歌语音朗读功能 🎙️

**新增功能：**
- 使用OpenAI TTS将生成的诗歌转换为语音朗读
- 根据情绪自动选择合适的声音和语速：
  - **积极情绪**: Nova声音（温暖、充满活力的女声），正常语速
  - **消极情绪**: Onyx声音（沉稳、温和的男声），稍慢语速(0.9x)
  - **中性情绪**: Shimmer声音（柔和、平静的女声），稍慢语速(0.95x)

**新增文件：** `tts_api.py`
- OpenAITTSGenerator：主要TTS实现
- EdgeTTSGenerator：免费备选方案（需安装edge-tts）

**API端点：** `POST /generate_narration`
```json
{
  "poem": "诗歌内容",
  "emotion": "positive/negative/neutral"
}
```

**配置：** `config.py`
```python
TTS_SERVICE = 'openai'  # 或 'edge'
```

---

### 3. 前端语音播放器 🔊

**UI更新：**
- 在诗歌展示区域下方添加了精美的语音朗读播放器
- 渐变背景（紫色到粉色）
- 实时状态显示：正在生成 → 准备就绪
- 完整的音频控制（播放、暂停、进度条、音量）

**用户体验：**
- 诗歌生成后自动生成语音朗读
- 可同时播放朗读和背景音乐
- 建议：先播放朗读，再开启背景音乐营造氛围

**位置：** `templates/index.html:272-287`

---

## 📋 完整工作流程

```
用户填写信息 → 生成诗歌
     ↓
显示诗歌文本（逐行动画）
     ↓
生成语音朗读（TTS）
     ↓
显示背景音乐
     ↓
显示记忆场景图片（照片级真实）
```

---

## 🚀 使用方法

### 启动应用

```bash
cd F:\work\2025work\sure\momo\code\website\codeV7
python app.py
```

或使用新的启动脚本：
```bash
python run_app.py
```

### 访问地址

- **主页**: http://localhost:5000/
- **应用**: http://localhost:5000/app
- **健康检查**: http://localhost:5000/health

### 完整体验流程

1. 在主页了解项目介绍
2. 点击"立即体验"进入应用页面
3. 点击"Analyze Emotion"进行情绪分析
4. 填写完整的记忆信息表单
5. 点击"Generate Poem"生成诗歌
6. 等待系统生成：
   - ✅ 诗歌文本（逐行显示）
   - ✅ 语音朗读（自动生成）
   - ✅ 背景音乐（情绪匹配）
   - ✅ 记忆场景图片（照片级真实）
7. 播放语音朗读，聆听专属诗歌
8. 播放背景音乐，营造沉浸氛围
9. 观看记忆场景图片，回忆珍贵时刻

---

## 🔧 技术细节

### 修改的文件

1. **image_api.py** (新增94-114行)
   - 添加 `_enhance_for_photorealism()` 方法
   - 修改 `DALLEGenerator.generate()` 调用增强提示词

2. **tts_api.py** (新文件，205行)
   - OpenAITTSGenerator类
   - EdgeTTSGenerator类（备选）
   - `get_tts_generator()` 工厂函数

3. **config.py** (新增40-42行)
   - 添加TTS_SERVICE配置

4. **app.py** (新增导入和端点)
   - 导入TTS模块
   - 新增 `/generate_narration` 端点
   - 更新health端点显示新功能

5. **templates/index.html** (多处修改)
   - 添加语音播放器UI (272-287行)
   - 添加 `generateNarration()` 函数 (694-737行)
   - 添加 `base64ToBlob()` 辅助函数 (739-748行)
   - 在诗歌生成成功后调用朗读生成 (553-556行)

---

## 💡 成本估算

### 每次完整生成成本

- 诗歌生成 (Deepseek): ~$0.01
- 图片生成 (DALL-E 3): ~$0.04
- **语音朗读 (OpenAI TTS)**: ~$0.015 (每1000字符)
- 音乐 (免费库): $0

**总计**: ~$0.065/次

### 月度估算（每天10次）

- 图片：$12
- 语音：$4.5
- 诗歌：$3
- **总计：$19.5/月**

---

## 🎯 下一步建议

### 可选增强功能

1. **音频混合**
   - 安装ffmpeg和pydub
   - 实现语音朗读与背景音乐的自动混合
   - 生成单一混合音频文件

2. **语音调节**
   - 添加语速调节滑块
   - 添加音调调节选项
   - 提供多种声音选择

3. **离线TTS**
   - 集成Edge TTS作为免费方案
   - 添加本地TTS引擎支持

4. **音频下载**
   - 添加语音朗读下载功能
   - 支持MP3/WAV格式导出

---

## ⚠️ 注意事项

1. **API配置**
   - 确保 `config.py` 中的 OPENAI_API_KEY 正确
   - TTS使用相同的OpenAI账号和base_url

2. **浏览器兼容性**
   - 确保浏览器支持HTML5 Audio
   - 建议使用Chrome、Firefox或Edge最新版本

3. **音频播放**
   - 语音朗读和背景音乐可同时播放
   - 建议先播放语音，再开启背景音乐
   - 注意调节音量平衡

4. **生成时间**
   - TTS生成需要3-5秒
   - 较长诗歌可能需要更长时间
   - 状态显示会实时更新

---

## ✨ 特色亮点

### 1. 多模态融合体验
文字（诗歌）+ 听觉（朗读+音乐）+ 视觉（照片级图片）

### 2. 情绪自适应
每个模态都根据患者情绪状态动态调整

### 3. 临床优化
- 语音语速针对阿尔茨海默病患者优化
- 图片真实化帮助记忆激活
- 音乐情绪调节功能

### 4. 完整疗愈包
30秒内生成包含诗歌、朗读、音乐、图片的完整疗愈体验

---

## 📞 问题排查

### TTS生成失败

**可能原因：**
- OpenAI API配置错误
- 网络连接问题
- API额度不足

**解决方案：**
1. 检查 `config.py` 中的API配置
2. 查看浏览器控制台错误信息
3. 检查Flask后端日志
4. 尝试切换到Edge TTS: `TTS_SERVICE = 'edge'`

### 音频无法播放

**可能原因：**
- Base64解码失败
- 浏览器不支持音频格式
- CORS问题

**解决方案：**
1. 打开浏览器开发者工具检查错误
2. 确认浏览器支持MP3格式
3. 检查Flask允许的CORS设置

### 图片不够真实

**解决方案：**
- 修改 `config.py`:
  ```python
  DALLE_QUALITY = 'hd'  # 使用HD质量
  ```
- 调整 `image_api.py` 中的照片增强提示词

---

**更新日期**: 2025-11-27
**版本**: V7.1 - Photorealistic + TTS
