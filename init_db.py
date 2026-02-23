from database import SessionLocal, engine, Base
from database import DRGItem

# 删除所有表并重新创建（方便反复测试）
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# 创建会话
db = SessionLocal()

# 准备测试数据
drg1 = DRGItem(
    group_code="RA23",
    group_name="急性阑尾炎手术，无并发症",
    weight=1.2,
    base_price=5000,
    avg_cost=6000
)

drg2 = DRGItem(
    group_code="RB14",
    group_name="剖宫产，无并发症",
    weight=1.5,
    base_price=6000,
    avg_cost=7500
)

drg3 = DRGItem(
    group_code="FC09",
    group_name="肺炎，年龄>65岁",
    weight=1.1,
    base_price=4000,
    avg_cost=4300
)

# 添加到会话并提交
db.add_all([drg1, drg2, drg3])
db.commit()

print("✅ 测试数据插入成功！")

# 验证一下
count = db.query(DRGItem).count()
print(f"当前 drg_dict 表中共有 {count} 条记录")

db.close()