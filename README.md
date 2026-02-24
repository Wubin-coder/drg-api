本地进行测试
ip:127.0.0.1
端口：8000

POSTMAN测试工具
GET方法：http://127.0.0.1:8000
返回结果：
{
    "message": "DRG API 已启动"
}

GET方法：http://127.0.0.1:8000
返回结果（数据库中存储的表是 DRG 分组的核心基础数据，包括编码、名称、权重和价格信息。这些数据是 DRG 审核计费的基础，也是该项目中“智能审核”功能的计算依据。）：
[
    {
       "base_price": 5000.0,
        "weight": 1.2,
        "group_code": "RA23",
        "group_name": "急性阑尾炎手术，无并发症",
        "id": 1,
        "avg_cost": 6000.0
    },
    {
        "base_price": 6000.0,
        "weight": 1.5,
        "group_code": "RB14",
        "group_name": "剖宫产，无并发症",
        "id": 2,
        "avg_cost": 7500.0
    },
    {
        "base_price": 4000.0,
        "weight": 1.1,
        "group_code": "FC09",
        "group_name": "肺炎，年龄>65岁",
        "id": 3,
        "avg_cost": 4300.0
    }
]

POST方法：http://127.0.0.1:8000/review_case
传入参数：{
    "case_id": "C001",
    "diagnosis_code": "急性阑尾炎",
    "procedure_code": "阑尾切除术",
    "age": 30,
    "complications": "",
    "total_cost": 7200
}
返回结果(该结果为DRG计算后的评估结果)：
{
    "case_id": "C001",
    "drg_group_code": "RA23",
    "drg_group_name": "急性阑尾炎手术，无并发症",
    "standard_cost": 6000.0,
    "actual_cost": 7200.0,
    "difference": 1200.0,
    "review_result": "偏高"
}
