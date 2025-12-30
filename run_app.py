"""
简单的启动脚本 - 清除缓存并启动应用
"""
import sys
import os

# 清除pycache
if os.path.exists('__pycache__'):
    import shutil
    shutil.rmtree('__pycache__')
    print("✓ 已清除 __pycache__")

# 启动应用
from app import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("MOMO V7 启动中...")
    print("="*60)
    print("主页: http://localhost:5000/")
    print("应用页面: http://localhost:5000/app")
    print("健康检查: http://localhost:5000/health")
    print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
