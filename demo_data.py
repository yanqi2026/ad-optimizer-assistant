"""
优化师分身 - Demo数据集
3组脱敏典型账户数据，用于新用户快速体验

数据来源：基于行业公开基准数据构造，所有数据已脱敏
创建时间：2026-06-12
"""
import pandas as pd

# ========== 金融借贷 - 账户A（需优化） ==========
finance_account_a = {
    "account_name": "星融信用贷-腾讯MP-6月",
    "industry": "金融借贷",
    "platform": "腾讯广告MP",
    "optimization": "成本优先",
    "bid_mode": "oCPM",
    "ctr": 1.2,
    "cvr": 2.8,
    "cpa": 95.0,
    "cpc": 2.8,
    "spend": 8000.0,
    "conversions": 84,
    "target_cpa": 75,
    "daily_budget": 10000,
    "product_type": "信用贷",
    "avg_loan": 15000,
    # 辅助指标
    "impressions": 666667,
    "clicks": 8000,
    "account_age": "3月以上",
    # 人群画像
    "audience_age": "25-34岁（职场新人）",
    "audience_pain": ["资金周转", "应急备用"],
    "placement": "朋友圈",
    # 预期诊断
    "expected_level": "B",
    "expected_issues": "CTR偏低+CVR偏低+CPA偏高"
}

# ========== 金融借贷 - 账户B（表现优秀） ==========
finance_account_b = {
    "account_name": "快借钱包-巨量-6月",
    "industry": "金融借贷",
    "platform": "巨量引擎",
    "optimization": "平衡",
    "bid_mode": "oCPM",
    "ctr": 2.3,
    "cvr": 4.5,
    "cpa": 62.0,
    "cpc": 1.8,
    "spend": 15000.0,
    "conversions": 242,
    "target_cpa": 65,
    "daily_budget": 15000,
    "product_type": "消费分期",
    "avg_loan": 8000,
    "impressions": 1250000,
    "clicks": 28750,
    "account_age": "3月以上",
    "audience_age": "35-44岁（职场精英）",
    "audience_pain": ["日常消费", "品质生活"],
    "placement": "全渠道",
    "expected_level": "A",
    "expected_issues": "整体稳定"
}

# ========== 教育 - 账户C（新账户冷启动） ==========
education_account_c = {
    "account_name": "启智学堂-腾讯MP-新品",
    "industry": "教育",
    "platform": "腾讯广告MP",
    "optimization": "拿量优先",
    "bid_mode": "oCPM",
    "ctr": 0.8,
    "cvr": 1.5,
    "cpa": 180.0,
    "cpc": 3.5,
    "spend": 3000.0,
    "conversions": 17,
    "target_cpa": 120,
    "daily_budget": 5000,
    "product_type": "其他",
    "avg_loan": 0,
    "impressions": 214286,
    "clicks": 1714,
    "account_age": "<7天",
    "audience_age": "25-34岁（职场新人）",
    "audience_pain": ["创业需求", "品质生活"],
    "placement": "公众号底部",
    "expected_level": "D",
    "expected_issues": "CTR严重偏低+CVR极低+CPA远超目标+冷启动困难"
}

# ========== 数据集列表 ==========
demo_datasets = {
    "金融借贷-需优化（账户A）": {
        "data": finance_account_a,
        "desc": "CTR/CVR偏低，CPA超标，典型需优化场景",
        "tag": "🔴 需优化"
    },
    "金融借贷-表现优秀（账户B）": {
        "data": finance_account_b,
        "desc": "各项指标健康，可作为标杆参考",
        "tag": "🟢 优秀"
    },
    "教育-冷启动（账户C）": {
        "data": education_account_c,
        "desc": "新账户冷启动期，数据不稳定，CTR/CVR极低",
        "tag": "🔴 冷启动"
    }
}

# ========== CSV模板列 ==========
csv_template_columns = [
    "account_name", "industry", "platform", "optimization", "bid_mode",
    "ctr", "cvr", "cpa", "cpc", "spend", "conversions",
    "target_cpa", "daily_budget", "product_type", "avg_loan"
]

csv_template_labels = {
    "account_name": "账户名称",
    "industry": "行业",
    "platform": "平台",
    "optimization": "优化方向",
    "bid_mode": "出价模式",
    "ctr": "CTR(%)",
    "cvr": "CVR(%)",
    "cpa": "CPA(元)",
    "cpc": "CPC(元)",
    "spend": "日消耗(元)",
    "conversions": "日转化数",
    "target_cpa": "目标CPA(元)",
    "daily_budget": "日预算(元)",
    "product_type": "产品类型",
    "avg_loan": "件均(元)"
}


def get_demo_dataframe():
    """生成Demo数据的DataFrame（用于导出参考）"""
    rows = []
    for name, item in demo_datasets.items():
        d = item["data"]
        row = {csv_template_labels.get(k, k): d.get(k, "") for k in csv_template_columns}
        rows.append(row)
    return pd.DataFrame(rows)


def generate_csv_template():
    """生成空CSV模板（供用户下载填写）"""
    df = pd.DataFrame(columns=[csv_template_labels.get(k, k) for k in csv_template_columns])
    # 加一行示例
    example = {csv_template_labels.get(k, k): v for k, v in zip(
        csv_template_columns,
        ["我的账户-腾讯-6月", "金融借贷", "腾讯广告MP", "成本优先", "oCPM",
         1.5, 3.0, 85.0, 2.5, 5000.0, 59, 80, 10000, "信用贷", 15000]
    )}
    df = pd.concat([df, pd.DataFrame([example])], ignore_index=True)
    return df.to_csv(index=False)
