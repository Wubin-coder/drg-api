from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 创建数据库连接引擎（使用SQLite，数据库文件将生成在当前目录，名为 drg.db）
SQLALCHEMY_DATABASE_URL = "sqlite:///./drg.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite多线程支持
)

# 2. 创建会话类，用于后续操作数据库
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. 创建基类，后续的模型类都要继承它
Base = declarative_base()


# 4. 定义 DRG 分组字典表
class DRGItem(Base):
    __tablename__ = "drg_dict"

    id = Column(Integer, primary_key=True, index=True)
    group_code = Column(String, unique=True, index=True)  # 分组编码，如 "RA23"
    group_name = Column(String)  # 分组名称
    weight = Column(Float)  # 权重
    base_price = Column(Float)  # 基础付费标准
    avg_cost = Column(Float)  # 参考平均费用


# 5. 定义入院记录表（模拟）
class AdmissionRecord(Base):
    __tablename__ = "admission_record"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String, unique=True)  # 病案号
    diagnosis_code = Column(String)  # 主诊断编码
    procedure_code = Column(String)  # 手术操作编码
    age = Column(Integer)
    complications = Column(String)  # 并发症描述
    total_cost = Column(Float)  # 总费用


# 6. 创建所有表（如果表不存在则创建）
Base.metadata.create_all(bind=engine)

print("✅ 数据库表创建成功！")