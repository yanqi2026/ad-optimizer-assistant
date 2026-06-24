"""
优化师分身 - AI驱动的营销投放策略助手
主页 - 产品介绍 + 场景入口

v3.0 更新：
- 移动端适配优化
- UI统一优化
"""
import streamlit as st
from pathlib import Path

# ========== 页面配置 ==========
st.set_page_config(
    page_title="优化师分身 | AI投放助手",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== 自定义样式 ==========
st.markdown("""
<style>
    /* 全局字体优化 - 跨平台兼容性 */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    }
    
    /* 主标题 */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1A1A2E;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* 场景卡片 */
    .scene-card {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFA 100%);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(78, 205, 196, 0.2);
        transition: all 0.3s ease;
        height: 100%;
    }
    .scene-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(78, 205, 196, 0.2);
    }
    .scene-card h3 {
        color: #1A1A2E;
        font-size: 1.2rem;
        margin: 0.8rem 0 0.5rem;
    }
    .scene-card p {
        color: #666;
        font-size: 0.9rem;
        line-height: 1.6;
        margin: 0;
    }
    
    /* 标签徽章 */
    .badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-diagnosis { background: #FFEBEE; color: #C62828; }
    .badge-strategy { background: #E0F7FA; color: #00838F; }
    .badge-material { background: #FFF8E1; color: #E65100; }
    
    /* 亮点数字 */
    .highlight-num {
        font-size: 1.1rem;
        font-weight: 700;
        color: #4ECDC4;
    }
    
    /* 流程步骤 */
    .flow-step {
        background: #F0FDFA;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        border: 1px solid #B2DFDB;
    }
    .flow-step .step-num {
        font-size: 0.75rem;
        color: #4ECDC4;
        font-weight: 600;
        margin-bottom: 0.3rem;
    }
    .flow-step .step-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #1A1A2E;
        margin-bottom: 0.2rem;
    }
    .flow-step .step-desc {
        font-size: 0.8rem;
        color: #666;
    }
    
    /* CTA按钮 */
    .stButton > button {
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(78, 205, 196, 0.4);
    }
    
    /* 指标卡片 */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .metric-card .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #4ECDC4;
    }
    .metric-card .metric-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.3rem;
    }
    
    /* 使用说明 */
    .info-box {
        background: #FAFAFA;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid #4ECDC4;
    }
    
    /* 底部版权 */
    .footer {
        text-align: center;
        color: #999;
        font-size: 0.8rem;
        padding: 1.5rem 0 1rem;
    }
    
    /* 移动端适配 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem !important;
        }
        .sub-header {
            font-size: 0.95rem !important;
        }
        .metric-card .metric-value {
            font-size: 1.2rem;
        }
        .stButton > button {
            width: 100%;
        }
        .scene-card {
            padding: 1.2rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== 主页面内容 ==========
st.markdown('<h1 class="main-header">🎯 优化师分身</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI驱动的营销投放策略助手 · 腾讯广告 · 金融借贷行业</p>', unsafe_allow_html=True)

# ========== 价值主张 ==========
value_col1, value_col2, value_col3, value_col4 = st.columns(4)

with value_col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">⏱️ 30秒</div>
        <div class="metric-label">完成诊断分析</div>
    </div>
    """, unsafe_allow_html=True)

with value_col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">📈 10年+</div>
        <div class="metric-label">行业经验沉淀</div>
    </div>
    """, unsafe_allow_html=True)

with value_col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">🎯 3大场景</div>
        <div class="metric-label">覆盖核心需求</div>
    </div>
    """, unsafe_allow_html=True)

with value_col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">🔒 数据安全</div>
        <div class="metric-label">本地处理/脱敏</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== 一站式入口 ==========
st.subheader("🚀 一站式投放优化")

workbench_col1, workbench_col2 = st.columns([2, 3], gap="large")

with workbench_col1:
    st.markdown("""
    <div class="scene-card">
        <h3>🎯 优化工作台</h3>
        <p><strong>诊断 → 策略 → 素材</strong>，一站式搞定</p>
        <br>
        <p>• <span class="badge badge-diagnosis">Step1</span> 智能诊断账户健康度</p>
        <p>• <span class="badge badge-strategy">Step2</span> 生成完整投放策略</p>
        <p>• <span class="badge badge-material">Step3</span> 创意素材灵感</p>
        <br>
        <p style="color:#999; font-size:0.85rem;">每步可独立使用，也可跳步选择</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎯 进入优化工作台", key="goto_workbench", use_container_width=True):
        st.switch_page("pages/1_优化工作台.py")

with workbench_col2:
    st.markdown("""
    <div class="info-box">
        <h4>💡 使用流程</h4>
        <p><strong>1️⃣ 填数据</strong> — 输入账户核心指标（CTR/CVR/CPA等）</p>
        <p><strong>2️⃣ 看诊断</strong> — AI自动分析健康度+识别问题+给建议</p>
        <p><strong>3️⃣ 拿策略</strong> — 一键生成出价+时段+人群+执行节奏</p>
        <p><strong>4️⃣ 找灵感</strong> — 5个创意方向+文案模板，直接可用</p>
        <br>
        <p style="color:#999; font-size:0.85rem;">⚠️ 每步结果自动流转到下一步，也可跳过选择只看需要的部分</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== 使用流程 ==========
st.subheader("📋 3步快速上手")

flow_col1, flow_col2, flow_col3 = st.columns(3, gap="medium")

with flow_col1:
    st.markdown("""
    <div class="flow-step">
        <div class="step-num">STEP 1</div>
        <div class="step-title">📝 填写数据</div>
        <div class="step-desc">输入账户核心指标或推广需求</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #4ECDC4; font-size: 1.5rem; margin-top: -0.5rem;">→</div>
    """, unsafe_allow_html=True)

with flow_col2:
    st.markdown("""
    <div class="flow-step">
        <div class="step-num">STEP 2</div>
        <div class="step-title">🤖 AI分析</div>
        <div class="step-desc">基于行业知识库智能分析</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #4ECDC4; font-size: 1.5rem; margin-top: -0.5rem;">→</div>
    """, unsafe_allow_html=True)

with flow_col3:
    st.markdown("""
    <div class="flow-step">
        <div class="step-num">STEP 3</div>
        <div class="step-title">✅ 获取方案</div>
        <div class="step-desc">导出诊断报告/策略方案</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ========== 适用说明 ==========
info_col1, info_col2 = st.columns(2, gap="large")

with info_col1:
    with st.expander("📖 适用平台与行业", expanded=False):
        st.markdown("""
        **适用平台**
        - 腾讯广告（枫页）
        - 腾讯广告MP平台
        
        **适用行业**
        - 金融借贷（主）
        - 其他行业可通用参考
        
        **数据要求**
        - 建议有7天以上投放数据
        - 需核心指标：CTR/CVR/CPA/消耗
        """)
    
    with st.expander("⚠️ 注意事项", expanded=False):
        st.markdown("""
        1. **数据脱敏**：所有输入数据仅本地处理，不会上传
        2. **参考建议**：AI输出为策略建议，实际效果因市场环境而异
        3. **基准对比**：参考行业基准数据，建议结合实际情况调整
        4. **持续优化**：建议每周进行一次账户健康度诊断
        """)

with info_col2:
    with st.expander("💡 常见问题", expanded=False):
        st.markdown("""
        **Q: 需要登录吗？**
        A: 目前为免费体验版本，无需登录即可使用。
        
        **Q: 数据安全吗？**
        A: 所有数据仅在本地处理，不会上传到服务器。
        
        **Q: 诊断结果准确吗？**
        A: 基于10年+行业经验沉淀的知识库，仅供参考，实际决策请结合业务判断。
        
        **Q: 支持其他平台吗？**
        A: 当前版本专注腾讯广告，后续将支持更多平台。
        """)

# ========== 页脚 ==========
st.divider()
st.markdown("""
<div class="footer">
    <p>🎯 优化师分身 v3.0 | AI产品经理转型Demo项目</p>
    <p>基于Coze Bot + Streamlit + 行业知识库构建 | 2026.06</p>
</div>
""", unsafe_allow_html=True)
