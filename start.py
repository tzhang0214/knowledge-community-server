"""
项目启动脚本
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✓ 核心依赖已安装")
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """检查环境配置文件"""
    print("检查环境配置...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("✗ 未找到 .env 文件")
        print("请复制 env.example 为 .env 并配置相关参数")
        return False
    
    print("✓ 环境配置文件存在")
    return True


def init_database():
    """初始化数据库"""
    print("初始化数据库...")
    
    try:
        result = subprocess.run([
            sys.executable, "scripts/init_db.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ 数据库初始化成功")
            return True
        else:
            print(f"✗ 数据库初始化失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ 数据库初始化异常: {e}")
        return False


def start_server(host="0.0.0.0", port=8000, reload=True):
    """启动服务器"""
    print(f"启动服务器 {host}:{port}...")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"✗ 服务器启动失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="ISP知识库系统启动脚本")
    parser.add_argument("--host", default="0.0.0.0", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8000, help="服务器端口")
    parser.add_argument("--no-reload", action="store_true", help="禁用热重载")
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    parser.add_argument("--check-only", action="store_true", help="仅检查环境")
    
    args = parser.parse_args()
    
    print("ISP知识库系统启动脚本")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查环境配置
    if not check_env_file():
        sys.exit(1)
    
    # 仅检查模式
    if args.check_only:
        print("✓ 环境检查完成")
        return
    
    # 初始化数据库
    if args.init_db:
        if not init_database():
            sys.exit(1)
    
    # 启动服务器
    start_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )


if __name__ == "__main__":
    main()
