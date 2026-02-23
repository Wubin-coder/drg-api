from sqlalchemy.orm import Session
from database import DRGItem, AdmissionRecord

# 获取所有DRG分组
def get_all_drg(db: Session):
    """
    返回所有DRG分组记录
    """
    return db.query(DRGItem).all()

# 根据分组编码查询单个DRG分组
def get_drg_by_code(db: Session, code: str):
    """
    根据 group_code 查询一个DRG分组，返回第一条匹配的记录（或None）
    """
    return db.query(DRGItem).filter(DRGItem.group_code == code).first()

# 新增一条入院记录（暂时预留，后续审核接口可能需要保存记录）
def create_admission_record(db: Session, record_data: dict):
    """
    将一条入院记录存入数据库
    """
    db_record = AdmissionRecord(**record_data)
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record