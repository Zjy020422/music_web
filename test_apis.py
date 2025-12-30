"""
API测试脚本 - 验证所有API配置是否正常工作
"""

from config import APIConfig
from image_api import get_image_generator
from music_api import get_music_generator

def print_header(title):
    print("\n" + "="*70)
    print(title.center(70))
    print("="*70)

def print_section(title):
    print(f"\n{'─'*70}")
    print(f"  {title}")
    print(f"{'─'*70}")

def check_api_keys():
    """检查API密钥配置"""
    print_section("1. API密钥配置检查")

    configs = [
        ("Deepseek (诗歌)", APIConfig.DEEPSEEK_API_KEY, "✓ 已配置", "✗ 未配置"),
        ("OpenAI (图片)", APIConfig.OPENAI_API_KEY, "✓ 已配置", "✗ 未配置"),
        ("Replicate (可选)", APIConfig.REPLICATE_API_KEY, "✓ 已配置", "✗ 未配置"),
    ]

    for name, key, yes_msg, no_msg in configs:
        status = yes_msg if key and key != '' else no_msg
        print(f"   {name:25} {status}")

    print(f"\n   OpenAI Base URL:       {APIConfig.OPENAI_BASE_URL}")
    print(f"   图片服务:               {APIConfig.IMAGE_SERVICE}")
    print(f"   音乐服务:               {APIConfig.MUSIC_SERVICE}")

def test_image_generation():
    """测试图片生成"""
    print_section("2. 测试图片生成API")

    try:
        print("   正在生成测试图片...")
        img_gen = get_image_generator()

        test_prompt = "A peaceful garden with flowers, warm colors, nostalgic atmosphere"
        result = img_gen.generate(test_prompt, "positive")

        if result['status'] == 'success':
            print(f"   ✓ 图片生成成功！")
            print(f"   服务: {result.get('service', 'unknown')}")
            print(f"   URL: {result['image_url'][:80]}...")
            if 'note' in result:
                print(f"   备注: {result['note']}")
            return True
        else:
            print(f"   ✗ 图片生成失败")
            print(f"   错误: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"   ✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_music_generation():
    """测试音乐生成"""
    print_section("3. 测试音乐生成API")

    try:
        print("   正在生成测试音乐...")
        music_gen = get_music_generator()

        result = music_gen.generate(
            prompt="calm peaceful piano",
            emotion="neutral",
            duration=30
        )

        if result['status'] == 'success':
            print(f"   ✓ 音乐生成成功！")
            print(f"   服务: {result.get('service', 'unknown')}")
            print(f"   标题: {result['title']}")
            print(f"   描述: {result['description']}")
            if 'note' in result:
                print(f"   备注: {result['note']}")
            return True
        else:
            print(f"   ✗ 音乐生成失败")
            print(f"   错误: {result.get('message', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"   ✗ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_recommendations():
    """打印推荐配置"""
    print_section("4. 配置建议")

    current_service = APIConfig.IMAGE_SERVICE
    music_service = APIConfig.MUSIC_SERVICE

    if current_service == 'dalle' and APIConfig.OPENAI_API_KEY:
        print("   ✓ 图片生成：使用DALL-E（已配置）")
    else:
        print("   ⚠ 图片生成：使用备用方案")
        print("      建议：配置OpenAI API以获得最佳图片质量")

    if music_service == 'library':
        print("   ℹ 音乐生成：使用免费音乐库")
        print("      建议：配置Replicate API以获得定制音乐")
        print("      步骤：")
        print("        1. 访问 https://replicate.com/")
        print("        2. 获取API Token")
        print("        3. 在config.py中设置 REPLICATE_API_KEY")
        print("        4. 设置 MUSIC_SERVICE = 'musicgen'")
    elif music_service == 'musicgen' and APIConfig.REPLICATE_API_KEY:
        print("   ✓ 音乐生成：使用MusicGen（已配置）")
    else:
        print("   ⚠ 音乐生成：配置不完整")

def print_cost_estimate():
    """打印成本估算"""
    print_section("5. 成本估算")

    image_cost = 0.04 if APIConfig.IMAGE_SERVICE == 'dalle' else 0
    music_cost = 0.069 if APIConfig.MUSIC_SERVICE == 'musicgen' else 0
    poem_cost = 0.01

    total_per_generation = image_cost + music_cost + poem_cost
    daily_cost = total_per_generation * 10  # 假设每天10次
    monthly_cost = daily_cost * 30

    print(f"   每次生成成本:")
    print(f"      图片: ${image_cost:.3f}")
    print(f"      音乐: ${music_cost:.3f}")
    print(f"      诗歌: ${poem_cost:.3f}")
    print(f"      总计: ${total_per_generation:.3f}")

    print(f"\n   月度估算（每天10次）:")
    print(f"      ${monthly_cost:.2f}/月")

def main():
    """主测试函数"""
    print_header("MOMO V7 - API配置测试")

    # 检查API密钥
    check_api_keys()

    # 测试图片生成
    image_ok = test_image_generation()

    # 测试音乐生成
    music_ok = test_music_generation()

    # 打印建议
    print_recommendations()

    # 打印成本估算
    print_cost_estimate()

    # 总结
    print_section("测试总结")
    print(f"   图片生成: {'✓ 通过' if image_ok else '✗ 失败'}")
    print(f"   音乐生成: {'✓ 通过' if music_ok else '✗ 失败'}")

    if image_ok and music_ok:
        print("\n   🎉 所有测试通过！系统已准备就绪。")
        print("   运行 'python app.py' 启动应用")
    else:
        print("\n   ⚠️  部分测试失败，请检查配置")
        print("   查看 API_SETUP_GUIDE.md 获取详细帮助")

    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
