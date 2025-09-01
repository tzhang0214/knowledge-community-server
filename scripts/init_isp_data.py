"""
ISP知识库数据初始化脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from src.database import SessionLocal, engine
from src.models import Base, KnowledgeCategory, KnowledgeItem


def init_isp_knowledge_data():
    """初始化ISP知识库数据"""
    db = SessionLocal()
    
    try:
        # 创建表
        Base.metadata.create_all(bind=engine)
        
        # 清空现有数据
        db.query(KnowledgeItem).delete()
        db.query(KnowledgeCategory).delete()
        db.commit()
        
        # 相机成像原理
        camera_imaging = KnowledgeCategory(
            category_id="camera-imaging",
            title="📷 相机成像原理",
            description="相机成像的基本原理和技术",
            icon="📷",
            sort_order=1,
            is_active=True
        )
        db.add(camera_imaging)
        db.commit()
        
        camera_items = [
            KnowledgeItem(
                category_id="camera-imaging",
                title="光学系统",
                description="镜头组、光圈、焦距等光学元件组成成像系统",
                status="completed",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="camera-imaging",
                title="感光元件",
                description="CMOS/CCD传感器将光信号转换为电信号",
                status="completed",
                sort_order=2
            ),
            KnowledgeItem(
                category_id="camera-imaging",
                title="光电转换",
                description="光子激发电子，产生电荷积累和电压信号",
                status="completed",
                sort_order=3
            ),
            KnowledgeItem(
                category_id="camera-imaging",
                title="采样量化",
                description="空间和时间维度的离散化采样过程",
                status="pending",
                sort_order=4
            ),
            KnowledgeItem(
                category_id="camera-imaging",
                title="色彩滤波",
                description="Bayer阵列等色彩滤镜实现色彩分离",
                status="completed",
                sort_order=5
            ),
            KnowledgeItem(
                category_id="camera-imaging",
                title="噪声来源",
                description="光子噪声、暗电流噪声、读出噪声等",
                status="pending",
                sort_order=6
            )
        ]
        
        for item in camera_items:
            db.add(item)
        
        # ISP处理算法
        isp_algorithms = KnowledgeCategory(
            category_id="isp-algorithms",
            title="🔬 ISP处理算法",
            description="图像信号处理的核心算法",
            icon="🔬",
            sort_order=2,
            is_active=True
        )
        db.add(isp_algorithms)
        db.commit()
        
        isp_items = [
            KnowledgeItem(
                category_id="isp-algorithms",
                title="去马赛克",
                description="Demosaic算法从Bayer阵列重建全彩图像",
                status="completed",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="isp-algorithms",
                title="白平衡",
                description="调整RGB通道比例，校正色温偏差",
                status="completed",
                sort_order=2
            ),
            KnowledgeItem(
                category_id="isp-algorithms",
                title="降噪算法",
                description="双边滤波、非局部均值等降噪技术",
                status="completed",
                sort_order=3
            ),
            KnowledgeItem(
                category_id="isp-algorithms",
                title="色彩校正",
                description="色彩空间转换和色彩增强处理",
                status="completed",
                sort_order=4
            ),
            KnowledgeItem(
                category_id="isp-algorithms",
                title="锐化增强",
                description="拉普拉斯算子、USM等锐化算法",
                status="pending",
                sort_order=5
            ),
            KnowledgeItem(
                category_id="isp-algorithms",
                title="伽马校正",
                description="非线性亮度调整，适应人眼视觉特性",
                status="completed",
                sort_order=6
            )
        ]
        
        for item in isp_items:
            db.add(item)
        
        # ISP处理通路
        isp_pipeline = KnowledgeCategory(
            category_id="isp-pipeline",
            title="🔄 ISP处理通路",
            description="图像信号处理的完整流程",
            icon="🔄",
            sort_order=3,
            is_active=True
        )
        db.add(isp_pipeline)
        db.commit()
        
        pipeline_items = [
            KnowledgeItem(
                category_id="isp-pipeline",
                title="原始数据",
                description="Raw格式图像数据，包含传感器原始信息",
                status="completed",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="isp-pipeline",
                title="预处理",
                description="黑电平校正、坏点检测、镜头阴影校正",
                status="completed",
                sort_order=2
            ),
            KnowledgeItem(
                category_id="isp-pipeline",
                title="去马赛克",
                description="色彩插值，重建完整RGB图像",
                status="completed",
                sort_order=3
            ),
            KnowledgeItem(
                category_id="isp-pipeline",
                title="色彩处理",
                description="白平衡、色彩校正、饱和度调整",
                status="completed",
                sort_order=4
            ),
            KnowledgeItem(
                category_id="isp-pipeline",
                title="图像增强",
                description="降噪、锐化、对比度增强等",
                status="completed",
                sort_order=5
            ),
            KnowledgeItem(
                category_id="isp-pipeline",
                title="后处理",
                description="伽马校正、压缩编码、格式转换",
                status="completed",
                sort_order=6
            ),
            KnowledgeItem(
                category_id="isp-pipeline",
                title="AI处理模块",
                description="深度学习算法进行图像质量增强和智能优化",
                status="future",
                sort_order=7
            )
        ]
        
        for item in pipeline_items:
            db.add(item)
        
        # 软件开发技术栈
        software_stack = KnowledgeCategory(
            category_id="software-stack",
            title="💻 软件开发技术栈",
            description="ISP软件开发的技术栈和工具",
            icon="💻",
            sort_order=4,
            is_active=True
        )
        db.add(software_stack)
        db.commit()
        
        software_items = [
            KnowledgeItem(
                category_id="software-stack",
                title="编程语言",
                description="C/C++、Python、MATLAB等高性能语言",
                status="completed",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="software-stack",
                title="图像处理库",
                description="OpenCV、PIL、scikit-image等",
                status="completed",
                sort_order=2
            ),
            KnowledgeItem(
                category_id="software-stack",
                title="并行计算",
                description="OpenCL、CUDA、SIMD指令集优化",
                status="pending",
                sort_order=3
            ),
            KnowledgeItem(
                category_id="software-stack",
                title="算法优化",
                description="内存管理、缓存优化、算法复杂度",
                status="future",
                sort_order=4
            ),
            KnowledgeItem(
                category_id="software-stack",
                title="硬件加速",
                description="DSP、GPU、FPGA等专用硬件",
                status="completed",
                sort_order=5
            ),
            KnowledgeItem(
                category_id="software-stack",
                title="开发工具",
                description="调试器、性能分析器、代码优化工具",
                status="future",
                sort_order=6
            )
        ]
        
        for item in software_items:
            db.add(item)
        
        # 业务场景应用
        business_scenarios = KnowledgeCategory(
            category_id="business-scenarios",
            title="🎯 业务场景应用",
            description="ISP技术在不同业务场景中的应用",
            icon="🎯",
            sort_order=5,
            is_active=True
        )
        db.add(business_scenarios)
        db.commit()
        
        business_items = [
            KnowledgeItem(
                category_id="business-scenarios",
                title="标准模式",
                description="适合日常拍摄，支持自动优化参数，平衡画质与性能",
                status="completed",
                sort_order=1
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="肖像模式",
                description="利用计算摄影技术实现自然景深效果，突出主体，适合人像拍摄",
                status="completed",
                sort_order=2
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="夜间模式",
                description="在低光环境下自动激活，通过长时间曝光和智能处理捕捉更多细节",
                status="completed",
                sort_order=3
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="全景模式",
                description="移动手机拼接拍摄，适合拍摄广阔场景，支持360度全景",
                status="completed",
                sort_order=4
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="延时摄影",
                description="压缩快播视频，呈现时间流逝效果，如记录日落或云朵移动",
                status="completed",
                sort_order=5
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="慢动作",
                description="将视频放慢播放，突出细节，适合拍摄运动或水流",
                status="completed",
                sort_order=6
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="电影效果",
                description="模拟电影拍摄风格，提供专业级视频录制体验",
                status="completed",
                sort_order=7
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="RAW格式拍摄",
                description="保留更多图像信息，方便后期处理，适合专业摄影",
                status="completed",
                sort_order=8
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="曝光调整",
                description="通过滑动屏幕调整照片亮度，实时预览效果",
                status="completed",
                sort_order=9
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="对焦锁定",
                description="长按对焦框锁定焦点，适合拍摄移动物体",
                status="completed",
                sort_order=10
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="风格滤镜",
                description="提供多种滤镜效果，如黑白、复古等，为照片增添艺术气息",
                status="completed",
                sort_order=11
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="HDR模式",
                description="高动态范围拍摄，自动融合多帧不同曝光图像",
                status="completed",
                sort_order=12
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="专业模式",
                description="手动调节ISO、快门速度、白平衡等参数，满足专业需求",
                status="completed",
                sort_order=13
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="AI场景识别",
                description="智能识别拍摄场景，自动优化参数设置",
                status="future",
                sort_order=14
            ),
            KnowledgeItem(
                category_id="business-scenarios",
                title="AR滤镜",
                description="增强现实滤镜效果，实时叠加虚拟元素",
                status="future",
                sort_order=15
            )
        ]
        
        for item in business_items:
            db.add(item)
        
        db.commit()
        print("✓ ISP知识库数据初始化成功")
        
    except Exception as e:
        db.rollback()
        print(f"✗ ISP知识库数据初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("开始初始化ISP知识库数据...")
    init_isp_knowledge_data()
    print("ISP知识库数据初始化完成！")
