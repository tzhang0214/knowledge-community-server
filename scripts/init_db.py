"""
数据库初始化脚本
"""
import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, SessionLocal
from src.models import User, KnowledgeCategory, KnowledgeItem, KnowledgeDetail
from src.auth import get_password_hash


def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())


def create_sample_data():
    """创建示例数据"""
    db = SessionLocal()
    
    try:
        # 检查是否已存在数据
        existing_user = db.query(User).first()
        if existing_user:
            print("数据库中已存在数据，跳过示例数据创建")
            return
        
        # 创建管理员用户
        admin_user = User(
            id="ADMIN001",
            username="admin",
            email="admin@example.com",
            password_hash=get_password_hash("admin123"),
            role="admin"
        )
        db.add(admin_user)
        
        # 创建测试用户
        test_user = User(
            id="USER001",
            username="testuser",
            email="test@example.com",
            password_hash=get_password_hash("test123"),
            role="user"
        )
        db.add(test_user)
        
        # 创建知识分类
        categories = [
            KnowledgeCategory(
                id=generate_uuid(),
                category_id="camera-imaging",
                title="📷 相机成像原理",
                icon="📷",
                description="相机成像的基本原理和光学系统",
                sort_order=1
            ),
            KnowledgeCategory(
                id=generate_uuid(),
                category_id="isp-algorithms",
                title="🔬 ISP处理算法",
                icon="🔬",
                description="图像信号处理算法详解",
                sort_order=2
            ),
            KnowledgeCategory(
                id=generate_uuid(),
                category_id="hardware-design",
                title="⚡ 硬件设计",
                icon="⚡",
                description="ISP硬件设计和实现",
                sort_order=3
            ),
            KnowledgeCategory(
                id=generate_uuid(),
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
                id=generate_uuid(),
                category_id="basic-concepts",
                title="ISP基础概念",
                description="图像信号处理器(ISP)的基本概念和作用",
                status="completed",
                content="ISP（Image Signal Processor）是图像信号处理器，负责将传感器采集的原始图像数据转换为高质量的图像。",
                sort_order=1
            ),
            KnowledgeItem(
                id=generate_uuid(),
                category_id="camera-imaging",
                title="光学系统",
                description="镜头组、光圈、焦距等光学元件组成成像系统",
                status="completed",
                content="光学系统是相机成像的核心，包括镜头组、光圈、焦距等元件。",
                sort_order=1
            ),
            KnowledgeItem(
                id=generate_uuid(),
                category_id="isp-algorithms",
                title="去马赛克",
                description="Demosaic算法从Bayer阵列重建全彩图像",
                status="completed",
                content="去马赛克算法将Bayer阵列的单色像素重建为全彩图像。",
                sort_order=1
            ),
            KnowledgeItem(
                id=generate_uuid(),
                category_id="isp-algorithms",
                title="降噪算法",
                description="各种降噪算法及其实现原理",
                status="completed",
                content="降噪算法用于减少图像中的噪声，提高图像质量。",
                sort_order=2
            ),
            KnowledgeItem(
                id=generate_uuid(),
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
        
        # 提交知识项数据
        db.commit()
        
        # 创建知识项详情
        knowledge_details = [
            # ISP基础概念的详情
            KnowledgeDetail(
                id=f"detail-{knowledge_items[0].id}-001",
                knowledge_id=knowledge_items[0].id,
                title="ISP定义",
                description="图像信号处理器(Image Signal Processor)的定义和作用",
                external_link="https://en.wikipedia.org/wiki/Image_signal_processor",
                sort_order=1
            ),
            KnowledgeDetail(
                id=f"detail-{knowledge_items[0].id}-002",
                knowledge_id=knowledge_items[0].id,
                title="ISP功能",
                description="ISP的主要功能包括去马赛克、降噪、色彩校正等",
                external_link="https://www.sony-semicon.com/en/products/isp/",
                sort_order=2
            ),
            
            # 光学系统的详情
            KnowledgeDetail(
                id=f"detail-{knowledge_items[1].id}-001",
                knowledge_id=knowledge_items[1].id,
                title="镜头组",
                description="由多个透镜组成的光学系统，用于聚焦光线到传感器上",
                external_link="https://en.wikipedia.org/wiki/Camera_lens",
                sort_order=1
            ),
            KnowledgeDetail(
                id=f"detail-{knowledge_items[1].id}-002",
                knowledge_id=knowledge_items[1].id,
                title="光圈",
                description="控制光线进入量的机械装置，影响景深和曝光",
                external_link="https://en.wikipedia.org/wiki/Aperture",
                sort_order=2
            ),
            KnowledgeDetail(
                id=f"detail-{knowledge_items[1].id}-003",
                knowledge_id=knowledge_items[1].id,
                title="焦距",
                description="镜头到成像平面的距离，决定视角和放大倍数",
                external_link="https://en.wikipedia.org/wiki/Focal_length",
                sort_order=3
            ),
            
            # 去马赛克的详情
            KnowledgeDetail(
                id=f"detail-{knowledge_items[2].id}-001",
                knowledge_id=knowledge_items[2].id,
                title="Bayer阵列",
                description="RGB颜色滤镜阵列，每个像素只记录一种颜色信息",
                external_link="https://en.wikipedia.org/wiki/Bayer_filter",
                sort_order=1
            ),
            KnowledgeDetail(
                id=f"detail-{knowledge_items[2].id}-002",
                knowledge_id=knowledge_items[2].id,
                title="Demosaic算法",
                description="从Bayer阵列重建全彩图像的算法",
                external_link="https://en.wikipedia.org/wiki/Demosaicing",
                sort_order=2
            ),
            
            # 降噪算法的详情
            KnowledgeDetail(
                id=f"detail-{knowledge_items[3].id}-001",
                knowledge_id=knowledge_items[3].id,
                title="空间域降噪",
                description="在空间域内进行噪声抑制的算法",
                external_link="https://en.wikipedia.org/wiki/Noise_reduction",
                sort_order=1
            ),
            KnowledgeDetail(
                id=f"detail-{knowledge_items[3].id}-002",
                knowledge_id=knowledge_items[3].id,
                title="频域降噪",
                description="在频域内进行噪声抑制的算法",
                external_link="https://en.wikipedia.org/wiki/Frequency_domain",
                sort_order=2
            ),
            
            # ISP芯片设计的详情
            KnowledgeDetail(
                id=f"detail-{knowledge_items[4].id}-001",
                knowledge_id=knowledge_items[4].id,
                title="硬件架构",
                description="ISP芯片的硬件架构设计考虑",
                external_link="https://www.qualcomm.com/products/integrated-circuits/computer-vision",
                sort_order=1
            ),
            KnowledgeDetail(
                id=f"detail-{knowledge_items[4].id}-002",
                knowledge_id=knowledge_items[4].id,
                title="性能优化",
                description="ISP芯片性能优化的方法和策略",
                external_link="https://www.intel.com/content/www/us/en/products/network-io/programmable/ethernet.html",
                sort_order=2
            )
        ]
        
        for detail in knowledge_details:
            db.add(detail)
        
        # 提交所有更改
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
    
    # 初始化数据库表结构
    init_db()
    print("数据库表结构创建完成！")
    
    # 创建示例数据
    create_sample_data()
    
    print("数据库初始化完成！")


if __name__ == "__main__":
    main()
