# MOMO V7 - API设置指南

## ✅ 已配置的API

### 1. OpenAI (图片生成) - 已配置 ✓
- **服务**: DALL-E 图片生成
- **Base URL**: https://api.chatanywhere.tech/v1
- **API Key**: 已配置
- **状态**: ✅ 可用
- **用途**: 生成记忆场景图片

## 🔧 推荐配置的音乐生成API

由于你已经有OpenAI账号，推荐以下方案：

### 方案1：Replicate (推荐，性价比最高)

**为什么选择Replicate？**
- ✅ 注册简单，提供免费额度
- ✅ 支持MusicGen音乐生成
- ✅ 价格实惠（$0.0023/秒）
- ✅ API易用

**如何获取：**

1. 访问：https://replicate.com/
2. 使用GitHub账号登录
3. 进入：https://replicate.com/account/api-tokens
4. 创建新的API Token
5. 复制token（格式：`r8_xxx...`）

**配置方法：**
```python
# 在 config.py 中修改
REPLICATE_API_KEY = 'r8_你的token'
MUSIC_SERVICE = 'musicgen'  # 使用MusicGen
```

**成本估算：**
- 30秒音乐：约$0.069
- 每天生成10首：$0.69
- 每月成本：约$20

---

### 方案2：继续使用免费音乐库（当前方案）

**优点：**
- ✅ 完全免费
- ✅ 无需配置
- ✅ 即刻可用

**缺点：**
- ❌ 音乐固定，不能定制
- ❌ 选择有限

**当前配置：**
```python
MUSIC_SERVICE = 'library'  # 默认已配置
```

---

## 📋 完整配置步骤

### 步骤1：获取Replicate API（推荐）

1. **注册账号**
   ```
   网址：https://replicate.com/
   使用：GitHub/Google账号登录
   ```

2. **获取API Token**
   ```
   进入：Account → API Tokens
   点击：Create Token
   复制：r8_开头的token
   ```

3. **配置到系统**
   打开 `config.py`，修改：
   ```python
   REPLICATE_API_KEY = 'r8_你的token'
   MUSIC_SERVICE = 'musicgen'
   ```

### 步骤2：测试配置

运行测试脚本：
```bash
cd F:\work\2025work\sure\momo\code\website\codeV7
python test_apis.py
```

---

## 🎯 当前系统功能状态

| 功能 | API服务 | 状态 | 备注 |
|------|---------|------|------|
| 情绪分析 | 模拟/EEG模型 | ✅ 可用 | 使用训练好的模型 |
| 诗歌生成 | Deepseek | ✅ 可用 | 已配置 |
| 图片生成 | OpenAI DALL-E | ✅ 可用 | 已配置（ChatAnywhere） |
| 音乐生成 | 音乐库（免费） | ✅ 可用 | 推荐升级到MusicGen |

---

## 💰 成本分析

### 当前配置（OpenAI图片 + 免费音乐）

**每次生成成本：**
- 图片：约$0.04（DALL-E 3 standard）
- 音乐：$0（使用音乐库）
- 诗歌：约$0.01（Deepseek）
- **总计：约$0.05/次**

**月度成本估算（每天10次使用）：**
- 图片：$12
- 音乐：$0
- 诗歌：$3
- **总计：$15/月**

### 升级方案（OpenAI图片 + MusicGen音乐）

**每次生成成本：**
- 图片：约$0.04
- 音乐：约$0.069（30秒）
- 诗歌：约$0.01
- **总计：约$0.12/次**

**月度成本估算（每天10次使用）：**
- 图片：$12
- 音乐：$21
- 诗歌：$3
- **总计：$36/月**

---

## 🚀 快速开始

### 使用当前配置（无需额外API）

```bash
cd F:\work\2025work\sure\momo\code\website\codeV7
python app.py
```

访问：http://localhost:5000/app

### 升级音乐生成（推荐）

1. 获取Replicate API Token
2. 修改 `config.py`：
   ```python
   REPLICATE_API_KEY = 'r8_你的token'
   MUSIC_SERVICE = 'musicgen'
   ```
3. 重启应用

---

## 🔍 API验证检查

创建测试文件 `test_apis.py`：

```python
from config import APIConfig
from image_api import get_image_generator
from music_api import get_music_generator

print("="*60)
print("API Configuration Check")
print("="*60)

# 检查配置
print(f"\n1. OpenAI (图片生成)")
print(f"   API Key: {'✓ 已配置' if APIConfig.OPENAI_API_KEY else '✗ 未配置'}")
print(f"   Base URL: {APIConfig.OPENAI_BASE_URL}")
print(f"   Service: {APIConfig.IMAGE_SERVICE}")

print(f"\n2. 音乐生成")
print(f"   Service: {APIConfig.MUSIC_SERVICE}")
if APIConfig.MUSIC_SERVICE == 'musicgen':
    print(f"   Replicate Key: {'✓ 已配置' if APIConfig.REPLICATE_API_KEY else '✗ 未配置'}")

print(f"\n3. Deepseek (诗歌生成)")
print(f"   API Key: {'✓ 已配置' if APIConfig.DEEPSEEK_API_KEY else '✗ 未配置'}")

print("\n" + "="*60)
print("Testing APIs...")
print("="*60)

# 测试图片生成
try:
    print("\n[测试] 图片生成...")
    img_gen = get_image_generator()
    result = img_gen.generate("A peaceful garden", "neutral")
    if result['status'] == 'success':
        print(f"✓ 图片生成成功！URL: {result['image_url'][:50]}...")
    else:
        print(f"✗ 图片生成失败")
except Exception as e:
    print(f"✗ 错误: {e}")

# 测试音乐生成
try:
    print("\n[测试] 音乐生成...")
    music_gen = get_music_generator()
    result = music_gen.generate("", "neutral", 30)
    if result['status'] == 'success':
        print(f"✓ 音乐生成成功！标题: {result['title']}")
    else:
        print(f"✗ 音乐生成失败")
except Exception as e:
    print(f"✗ 错误: {e}")

print("\n" + "="*60)
print("检查完成！")
print("="*60)
```

运行测试：
```bash
python test_apis.py
```

---

## 📞 获取帮助

### 常见问题

**Q: OpenAI API调用失败怎么办？**
A: 检查API key是否正确，确认ChatAnywhere服务可用

**Q: 如何切换回Unsplash占位图片？**
A: 修改 `config.py` 中的 `IMAGE_SERVICE = 'unsplash'`

**Q: 音乐库的音乐可以自定义吗？**
A: 可以，编辑 `config.py` 中的 `MUSIC_LIBRARY` 字典

**Q: 成本太高怎么办？**
A:
- 使用DALL-E 2代替DALL-E 3（价格降低75%）
- 图片使用Unsplash（免费）
- 音乐使用音乐库（免费）

---

## ✨ 下一步

1. ✅ **当前可用**：图片生成（DALL-E）+ 音乐库
2. 🎵 **推荐升级**：添加Replicate API，启用MusicGen
3. 🚀 **未来扩展**：集成语音生成、视频生成

---

**配置完成后，运行应用：**
```bash
python app.py
```

访问：http://localhost:5000/app

开始创建你的记忆花园！
