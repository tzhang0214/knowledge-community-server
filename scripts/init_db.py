"""
数据库初始化脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, SessionLocal
from src.models import User, KnowledgeCategory, KnowledgeItem, FlowVersion, FlowModule
from src.auth import get_password_hash


def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()
    
    try:
        # 创建管理员用户
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin_user)
        
        # 创建测试用户
        test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("test123"),
            role="user"
        )
        db.add(test_user)
        
        # 创建知识分类
        categories = [
            KnowledgeCategory(
                category_id="camera-imaging",
                title="📷 相机成像原理",
                icon="📷",
                description="相机成像的基本原理和光学系统",
                sort_order=1
            ),
            KnowledgeCategory(
                category_id="isp-algorithms",
                title="🔬 ISP处理算法",
                icon="🔬",
                description="图像信号处理算法详解",
                sort_order=2
            ),
            KnowledgeCategory(
                category_id="hardware-design",
                title="⚡ 硬件设计",
                icon="⚡",
                description="ISP硬件设计和实现",
                sort_order=3
            ),
            KnowledgeCategory(
                category_id="basic-concepts",
                title="📚 基础知识",
                icon="📚",
                description="ISP基础概念和术语",
                sort_order=0
            )
        ]
        
        for category in categories:
            db.add(category)
        
        # 创建知识项
        knowledge_items = [
            KnowledgeItem(
                category_id="basic-concepts",
                title="ISP基础概念",
                description="图像信号处理器(ISP)的基本概念和作用",
                status="completed",
                content="ISP（Image Signal Processor）是图像信号处理器，负责将传感器采集的原始图像数据转换为高质量的图像。",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="camera-imaging",
                title="光学系统",
                description="镜头组、光圈、焦距等光学元件组成成像系统",
                status="completed",
                content="光学系统是相机成像的核心，包括镜头组、光圈、焦距等元件。",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="isp-algorithms",
                title="去马赛克",
                description="Demosaic算法从Bayer阵列重建全彩图像",
                status="completed",
                content="去马赛克算法将Bayer阵列的单色像素重建为全彩图像。",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="isp-algorithms",
                title="降噪算法",
                description="各种降噪算法及其实现原理",
                status="completed",
                content="降噪算法用于减少图像中的噪声，提高图像质量。",
                sort_order=2
            ),
            KnowledgeItem(
                category_id="hardware-design",
                title="ISP芯片设计",
                description="ISP专用芯片的架构设计",
                status="pending",
                content="ISP芯片设计需要考虑性能、功耗、面积等多个因素。",
                sort_order=1
            )
        ]
        
        for item in knowledge_items:
            db.add(item)
        
        # 创建架构图版本
        flow_versions = [
            FlowVersion(
                version_id="default",
                title="标准版本",
                description="标准ISP架构图",
                is_default=True
            ),
            FlowVersion(
                version_id="advanced",
                title="高级版本",
                description="高级ISP架构图，包含更多模块",
                is_default=False
            )
        ]
        
        for version in flow_versions:
            db.add(version)
        
        # 创建架构图模块
        flow_modules = [
            FlowModule(
                version_id="default",
                module_id="sensor",
                title="图像传感器",
                description="CMOS/CCD图像传感器",
                module_type="sensor",
                introduction="图像传感器负责将光信号转换为电信号",
                principle="光电转换原理",
                position_x=100,
                position_y=100
            ),
            FlowModule(
                version_id="default",
                module_id="mipi-receiver",
                title="MIPI CSI-2接收器",
                description="MIPI接口接收器",
                module_type="interface",
                introduction="MIPI CSI-2接口用于高速数据传输",
                principle="串行数据传输",
                position_x=300,
                position_y=100
            ),
            FlowModule(
                version_id="default",
                module_id="isp-core",
                title="ISP核心处理器",
                description="图像信号处理核心",
                module_type="processing",
                introduction="ISP核心负责图像处理算法",
                principle="并行处理架构",
                position_x=500,
                position_y=100
            ),
            FlowModule(
                version_id="default",
                module_id="memory",
                title="内存控制器",
                description="DDR内存控制器",
                module_type="memory",
                introduction="内存控制器管理图像数据存储",
                principle="DDR接口协议",
                position_x=300,
                position_y=300
            )
        ]
        
        for module in flow_modules:
            db.add(module)
        
        db.commit()
        print("示例数据创建成功！")
        
    except Exception as e:
        db.rollback()
        print(f"创建示例数据失败: {e}")
        raise
    finally:
        db.close()


def main():
    """主函数"""
    print("正在初始化数据库...")
    
    try:
        # 初始化数据库表
        init_db()
        print("数据库表创建成功！")
        
        # 创建示例数据
        create_sample_data()
        
        print("数据库初始化完成！")
        print("\n默认用户:")
        print("管理员: admin / admin123")
        print("测试用户: testuser / test123")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
