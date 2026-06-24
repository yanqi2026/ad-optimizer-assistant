"""
优化工作台 - 一站式投放优化
流程：数据输入 → AI对话分析（多轮交互）

架构：Streamlit前端 → Coze API → Bot后端
模式：🤖 真实AI对话 / 🎮 模拟演示（侧边栏切换）

v3.0 更新：
- 聊天式架构，重构叙事逻辑
- 移动端适配优化
- 性能优化，减少不必要的重渲染
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
from pathlib import Path
import requests as http_requests

# 添加项目根目录到路径，以便导入demo_data和coze_api
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from demo_data import demo_datasets, generate_csv_template, csv_template_columns, csv_template_labels
from coze_api import CozeAPI, build_diagnosis_prompt, build_strategy_prompt, build_material_prompt

# ========== 页面配置 ==========
st.set_page_config(
    page_title="优化工作台 | 优化师分身",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"  # 默认折叠侧边栏，移动端友好
)

# ========== 样式 ==========
st.markdown("""
<style>
    /* 全局字体优化 */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    }
    
    /* 数据卡片 */
    .data-card {
        background: white;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #4ECDC4;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
        font-size: 0.9rem;
    }
    .data-card-label { color: #999; font-size: 0.8rem; }
    .data-card-value { color: #333; font-weight: 600; }
    
    /* 聊天消息优化 */
    [data-testid="stChatMessageContent"] {
        padding: 0.8rem;
        border-radius: 12px;
    }
    
    /* 快捷操作按钮 - 紧凑胶囊样式 */
    .quick-btn-row {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        padding: 8px 0;
    }
    
    /* 移动端适配 */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.5rem !important;
        }
        .stFormSubmitButton > button {
            width: 100%;
        }
        [data-testid="stHorizontalBlock"] {
            flex-direction: column;
        }
    }
    
    /* 输入框优化 */
    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea {
        border-radius: 8px;
    }
    
    /* 下拉框优化 */
    [data-testid="stSelectbox"] {
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== 出价模式选项 ==========
BID_MODE_OPTIONS = ["oCPM", "oCPC", "自动出价", "ROI出价", "深度转化出价", "净成交ROI出价", "CPM", "CPC"]

# ========== 默认测试数据（模块级定义，供回调使用） ==========
_DEFAULT_TEST_DATA = {
    "account_name": "小赢卡贷",
    "industry": "金融借贷",
    "platform": "腾讯广告MP",
    "bid_mode": "oCPM",
    "optimization": "平衡",
    "ctr": 1.50,
    "cvr": 6.00,
    "cpc": 12.00,
    "spend": 35000.0,
    "conversions": 25,
    "target_cpa": 1100,
    "daily_budget": 100000,
    "product_type": "信用贷",
    "avg_loan": 20000,
    "user_problem": "近期CPA上涨，量级不够稳定，想优化成本同时保量，客户要求投放时段必须在7-18点内",
}

def _load_test_data_callback():
    """on_click回调：直接写入控件session_state，比删key更可靠"""
    for k, v in _DEFAULT_TEST_DATA.items():
        st.session_state[f"form_{k}"] = v
    st.session_state.demo_data = _DEFAULT_TEST_DATA

# ========== Session State 初始化 ==========
def init_session_state():
    """初始化会话状态"""
    defaults = {
        'input_data': None,
        'chat_messages': [],
        'use_api': True,
        'conversation_id': None,
        'api_error': None,
        'feedback_records': [],
        '_msg_queue': [],       # 消息队列，支持多条排队
        'demo_data': None,
        'workbench_step': 0
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ========== 工具函数 ==========
@st.cache_data(ttl=300)
def get_api_client():
    """获取CozeAPI客户端（带缓存）"""
    token = ""
    try:
        token = st.secrets.get("COZE_PAT_TOKEN", "")
    except Exception:
        pass
    if not token:
        import os
        token = os.environ.get("COZE_PAT_TOKEN", "")
    if not token:
        raise ValueError("未找到PAT Token，请在 .streamlit/secrets.toml 中配置 COZE_PAT_TOKEN")
    return CozeAPI(token)

def api_chat(user_message):
    """调用Bot API，返回助手回复文本"""
    api = get_api_client()
    if not st.session_state.conversation_id:
        st.session_state.conversation_id = api.create_conversation()
    
    full_text = ""
    for chunk in api.stream_chat(user_message, st.session_state.conversation_id):
        full_text += chunk
    return full_text

def render_bot_text(text):
    """渲染Bot回复：URL分隔 + 标题级别统一，避免字号不稳定"""
    import re
    # 在URL后面如果紧跟中文标点或文字，插入空格分隔
    fixed = re.sub(r'(https?://[^\s<>"\'）】}]+)([，。、！？~～；：''…—\u4e00-\u9fff])', r'\1 \2', text)
    # 统一标题级别：降2级，最低到####，避免Bot用#或##导致字号过大
    lines = fixed.split('\n')
    normalized = []
    for line in lines:
        m = re.match(r'^(#{1,6})\s', line)
        if m:
            level = len(m.group(1))
            new_level = min(level + 2, 4)
            line = '#' * new_level + line[level:]
        normalized.append(line)
    fixed = '\n'.join(normalized)
    st.markdown(fixed)

# ========== 飞书反馈写入 ==========
FEISHU_BASE_TOKEN = "Qt8SbZrqyanv80sBTHYcnZexnAc"
FEISHU_TABLE_ID = "tbl1WnihCvScVVKK"

@st.cache_data(ttl=3600)
def _get_feishu_token():
    """获取飞书tenant_access_token（缓存1小时）"""
    try:
        app_id = st.secrets.get("FEISHU_APP_ID", "")
        app_secret = st.secrets.get("FEISHU_APP_SECRET", "")
    except Exception:
        import os
        app_id = os.environ.get("FEISHU_APP_ID", "")
        app_secret = os.environ.get("FEISHU_APP_SECRET", "")
    if not app_id or not app_secret:
        return None
    resp = http_requests.post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=10
    )
    data = resp.json()
    return data.get("tenant_access_token")

def submit_feedback_to_feishu(rating, question=""):
    """静默写入反馈到飞书多维表格，不弹任何提示"""
    try:
        token = _get_feishu_token()
        if not token:
            return False
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 只写核心4个字段，避免必填字段问题
        body = {
            "fields": ["回答是否有帮助", "你问了什么", "日期", "具体问题或建议"],
            "rows": [[rating, question[:200], now_str, f"Streamlit前端自动反馈-{rating}"]]
        }
        resp = http_requests.post(
            f"https://open.feishu.cn/open-apis/base/v3/bases/{FEISHU_BASE_TOKEN}/tables/{FEISHU_TABLE_ID}/records/batch_create",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=body,
            timeout=10
        )
        return resp.json().get("code", -1) == 0
    except Exception:
        return False

def build_data_summary(data):
    """构建精简数据摘要，用于追问时注入上下文（控制token量减少等待）"""
    problem = data.get('user_problem', '')
    p = f"，问题:{problem}" if problem else ""
    return f"[{data.get('industry','金融借贷')}·{data.get('platform','腾讯广告MP')} CTR:{data.get('ctr','N/A')}% CVR:{data.get('cvr','N/A')}% CPA:{data.get('cpa','N/A')}元 日耗:{data.get('spend','N/A')}元 目标CPA:{data.get('target_cpa','N/A')}元 出价:{data.get('bid_mode','oCPM')}{p}]"

def build_initial_message(data):
    """根据表单数据组装自然语言的首条消息"""
    avg_loan_info = f"、件均{data.get('avg_loan', 0)}元" if data.get('avg_loan', 0) > 0 else ""
    problem = data.get('user_problem', '')
    problem_line = f"\n\n我遇到的问题是：{problem}" if problem else ""
    
    return f"""请帮我分析以下账户数据：
- 行业：{data.get('industry', '金融借贷')} · 平台：{data.get('platform', '腾讯广告MP')}
- CTR：{data.get('ctr', 'N/A')}% · CVR：{data.get('cvr', 'N/A')}% · CPA：{data.get('cpa', 'N/A')}元 · CPC：{data.get('cpc', 'N/A')}元
- 日消耗：{data.get('spend', 'N/A')}元 · 日转化：{data.get('conversions', 'N/A')}
- 产品：{data.get('product_type', '信用贷')}{avg_loan_info} · 目标CPA：{data.get('target_cpa', 'N/A')}元
- 出价模式：{data.get('bid_mode', 'oCPM')} · 优化方向：{data.get('optimization', '平衡')} · 日预算：{data.get('daily_budget', 'N/A')}元{problem_line}

请先理解我的核心诉求，然后给出诊断分析和策略建议。"""

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("### 🔧 数据来源")
    mode_options = ["🤖 真实AI对话", "🎮 模拟演示"]
    mode_idx = 0 if st.session_state.use_api else 1
    data_mode = st.radio(
        "选择模式",
        mode_options,
        index=mode_idx,
        horizontal=True,
        label_visibility="collapsed"
    )
    new_use_api = (data_mode == "🤖 真实AI对话")
    
    if new_use_api != st.session_state.use_api:
        st.session_state.use_api = new_use_api
        st.session_state.chat_messages = []
        st.session_state.conversation_id = None
        st.rerun()
    
    if st.session_state.use_api:
        st.caption("🤖 由优化师分身Bot驱动")
        if st.button("🔄 新对话", use_container_width=True):
            st.session_state.conversation_id = None
            st.session_state.chat_messages = []
            st.session_state._msg_queue = []
            st.rerun()
    else:
        st.caption("🎮 使用模拟数据演示")
    
    st.markdown("---")
    
    # 数据概览（确认数据后显示）
    if st.session_state.input_data:
        d = st.session_state.input_data
        st.markdown("### 📊 当前数据")
        st.markdown(f"""
        <div class="data-card">
            <span class="data-card-label">账户</span><br>
            <span class="data-card-value">{d.get('account_name', '未命名') or '未命名'}</span><br>
            <span style="font-size:0.75rem;color:#999;">{d.get('platform', '')} · {d.get('industry', '')}</span>
        </div>
        <div class="data-card">
            <span class="data-card-label">核心指标</span><br>
            <span class="data-card-value">CTR {d.get('ctr', 0)}% · CVR {d.get('cvr', 0)}% · CPA {d.get('cpa', 0):.0f}元</span>
        </div>
        <div class="data-card">
            <span class="data-card-label">目标</span><br>
            <span class="data-card-value">CPA {d.get('target_cpa', 0):.0f}元 · 日预算 {d.get('daily_budget', 0):.0f}元</span>
        </div>
        """, unsafe_allow_html=True)
        prob = d.get('user_problem', '')
        if prob:
            st.markdown(f"""
            <div class="data-card" style="border-left-color:#FF9800;">
                <span class="data-card-label">🔍 问题描述</span><br>
                <span class="data-card-value" style="font-size:0.85rem;">{prob[:80]}{'...' if len(prob)>80 else ''}</span>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("✏️ 修改数据", use_container_width=True):
            st.session_state.input_data = None
            st.session_state.chat_messages = []
            st.session_state.conversation_id = None
            st.session_state._msg_queue = []
            st.rerun()
    
    st.markdown("---")
    st.markdown("### 💡 使用提示")
    st.markdown("""
1. 填写账户数据并确认
2. 自动进入AI对话分析
3. 可随时追问、调整方向
4. 如"给我策略方案""素材方向呢"
""")

# ========== 处理消息队列 ==========
# 从队列中取出一条消息发送（每次rerun只处理一条，保证Bot逐一回复）
if st.session_state._msg_queue:
    msg = st.session_state._msg_queue.pop(0)
    st.session_state.chat_messages.append({"role": "user", "content": msg})
    st.rerun()

# ========== 页面主体 ==========
st.markdown('<p style="font-size:1.5rem;font-weight:700;margin:0;">🎯 优化工作台</p>', unsafe_allow_html=True)
st.caption("数据输入 → AI多轮对话分析")

# ========================================================================
# 数据输入区（未确认数据时显示）
# ========================================================================
if not st.session_state.input_data:
    # 快捷操作
    quick_col1, quick_col2 = st.columns(2)
    with quick_col1:
        st.button("📋 加载测试数据", use_container_width=True, help="一键填充默认测试数据", on_click=_load_test_data_callback)
    with quick_col2:
        uploaded_csv = st.file_uploader("上传辅助分析的数据", type=["csv"], key="csv_upload")
        if uploaded_csv:
            try:
                df_csv = pd.read_csv(uploaded_csv)
                if len(df_csv) > 0:
                    row = df_csv.iloc[0]
                    csv_data = {}
                    for col in df_csv.columns:
                        csv_data[col] = row[col]
                    st.session_state.demo_data = csv_data
                    # 直接写入控件session_state
                    for k, v in csv_data.items():
                        st.session_state[f"form_{k}"] = v
                    st.session_state.workbench_step = 0
                    st.rerun()
            except Exception as e:
                st.error(f"CSV解析失败：{e}")

    # 获取预填充数据
    prefill = st.session_state.get("demo_data", None)

    def pf(key, default=""):
        if prefill and key in prefill:
            return prefill[key]
        return default

    with st.form(key="workbench_input"):
        # 行1：基本信息
        col1, col2, col3 = st.columns(3)
        with col1:
            account_name = st.text_input("账户名称", value=pf("account_name", ""),
                                          placeholder="选填，如小赢卡贷-6月", key="form_account_name")
        with col2:
            industry_opts = ["金融借贷", "教育", "电商", "游戏", "其他"]
            default_industry = pf("industry", "金融借贷")
            industry_idx = industry_opts.index(default_industry) if default_industry in industry_opts else 0
            industry = st.selectbox("行业", industry_opts, index=industry_idx, key="form_industry")
        with col3:
            platform_opts = ["腾讯广告MP", "巨量引擎"]
            default_platform = pf("platform", "腾讯广告MP")
            platform_idx = platform_opts.index(default_platform) if default_platform in platform_opts else 0
            platform = st.selectbox("平台", platform_opts, index=platform_idx, key="form_platform")
        
        # 行2：核心指标
        col1, col2, col3 = st.columns(3)
        with col1:
            ctr = st.number_input("CTR(%)", min_value=0.0, value=float(pf("ctr", 0.0)), step=0.1, format="%.2f", key="form_ctr")
        with col2:
            cvr = st.number_input("CVR(%)", min_value=0.0, value=float(pf("cvr", 0.0)), step=0.1, format="%.2f", key="form_cvr")
        with col3:
            cpc = st.number_input("CPC(元)", min_value=0.0, value=float(pf("cpc", 0.0)), step=0.1, format="%.2f", key="form_cpc")
        
        col4, col5 = st.columns(2)
        with col4:
            spend = st.number_input("日消耗(元)", min_value=0.0, value=float(pf("spend", 0.0)), step=100.0, format="%.2f", key="form_spend")
        with col5:
            conversions = st.number_input("日转化数", min_value=0, value=int(pf("conversions", 0)), step=1, key="form_conversions")
        
        # CPA自动计算
        cpa = round(spend / conversions, 2) if conversions > 0 else 0.0
        if conversions > 0:
            st.info(f"💰 CPA = {cpa:.2f}元（自动计算）")
        else:
            st.info("💰 填写日消耗和转化数后自动计算CPA")
        
        # 行3：策略相关
        col1, col2 = st.columns(2)
        with col1:
            target_cpa = st.number_input("目标CPA(元)", min_value=0.0, value=float(pf("target_cpa", 0.0)), step=50.0, format="%.2f", key="form_target_cpa")
            bid_mode_idx = BID_MODE_OPTIONS.index(pf("bid_mode", "oCPM")) if pf("bid_mode", "oCPM") in BID_MODE_OPTIONS else 0
            bid_mode = st.selectbox("出价模式", BID_MODE_OPTIONS, index=bid_mode_idx, help="默认oCPM", key="form_bid_mode")
        with col2:
            daily_budget = st.number_input("日预算(元)", min_value=0.0, value=float(pf("daily_budget", 0.0)), step=1000.0, format="%.2f", key="form_daily_budget")
            opt_opts = ["拿量优先", "成本优先", "平衡"]
            default_opt = pf("optimization", "平衡")
            opt_idx = opt_opts.index(default_opt) if default_opt in opt_opts else 2
            optimization = st.selectbox("优化方向", opt_opts, index=opt_idx, key="form_optimization")
        
        col3, col4 = st.columns(2)
        with col3:
            product_type = st.text_input("产品类型", value=pf("product_type", "信用贷"), placeholder="如信用贷、大额贷", key="form_product_type")
        with col4:
            avg_loan = st.number_input("件均(元)", min_value=0.0, value=float(pf("avg_loan", 0.0)), step=1000.0, format="%.2f",
                                        help="选填，影响行业基准判断", key="form_avg_loan")
        
        # 行4：问题描述（醒目样式）
        st.markdown("""<div style="background:linear-gradient(135deg,#FF6F00,#FF9800);border-radius:10px;padding:12px 16px;margin:12px 0 4px 0;box-shadow:0 3px 8px rgba(255,152,0,0.3)">
        <span style="color:#fff;font-weight:800;font-size:1.15rem;letter-spacing:0.5px">⚠️ 描述你遇到的问题</span><br>
        <span style="color:#FFF3E0;font-size:0.9rem">这是AI理解你需求的核心依据，请务必填写！</span>
        </div>""", unsafe_allow_html=True)
        user_problem = st.text_area(
            "⚠️ 描述你遇到的问题",
            value=pf("user_problem", ""),
            placeholder="如：最近3天CPA突然涨了50% / 量级起不来，CTR正常但CVR很低 / 客户只让跑6-18点……",
            height=100,
            label_visibility="collapsed",
            help="描述越具体，AI分析越精准",
            key="form_user_problem"
        )
        
        if "demo_data" in st.session_state:
            del st.session_state.demo_data
        
        submitted = st.form_submit_button("✅ 确认数据，开始分析", type="primary", use_container_width=True)

    if submitted:
        input_data = {
            "account_name": account_name, "industry": industry, "platform": platform,
            "ctr": ctr, "cvr": cvr, "cpa": cpa, "cpc": cpc, "spend": spend,
            "conversions": conversions, "target_cpa": target_cpa,
            "daily_budget": daily_budget, "optimization": optimization,
            "product_type": product_type, "avg_loan": avg_loan,
            "bid_mode": bid_mode, "user_problem": user_problem
        }
        st.session_state.input_data = input_data
        st.session_state.chat_messages = []
        st.session_state.conversation_id = None
        st.session_state._msg_queue = [build_initial_message(input_data)]
        st.rerun()

# ========================================================================
# 对话分析区（确认数据后显示）
# ========================================================================
if st.session_state.input_data:
    
    st.markdown("---")
    st.markdown("### 💬 AI对话分析")
    
    # 展示聊天记录（排除最后一条用户消息，因为Bot需要回复）
    messages_to_show = st.session_state.chat_messages.copy()
    
    # 检查是否需要Bot回复（最后一条是用户消息）
    need_bot_reply = False
    last_user_msg = None
    if messages_to_show and messages_to_show[-1]["role"] == "user":
        need_bot_reply = True
        last_user_msg = messages_to_show[-1]["content"]
    
    # 先展示所有已有的完整对话
    if not need_bot_reply:
        for msg in messages_to_show:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    render_bot_text(msg["content"])
                else:
                    st.markdown(msg["content"])
    
    # Bot回复中
    if need_bot_reply and st.session_state.use_api:
        # 先展示之前的消息
        for msg in messages_to_show[:-1]:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    render_bot_text(msg["content"])
                else:
                    st.markdown(msg["content"])
        # 展示当前用户消息
        with st.chat_message("user"):
            st.markdown(last_user_msg)
        # Bot流式回复
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("🤖 AI正在分析中，请稍候...")
            try:
                full_text = ""
                for chunk in api_chat(last_user_msg):
                    full_text += chunk
                    placeholder.markdown(full_text + "▌")
                placeholder.empty()
                if full_text.strip():
                    st.session_state.chat_messages.append({"role": "assistant", "content": full_text})
                    render_bot_text(full_text)
                else:
                    fallback = "⚠️ Bot返回为空，请重新提问或换个说法试试"
                    st.session_state.chat_messages.append({"role": "assistant", "content": fallback})
                    st.warning(fallback)
            except Exception as e:
                placeholder.empty()
                error_msg = f"❌ API调用失败: {str(e)[:200]}"
                st.error(error_msg)
                st.info("💡 请检查网络和Token配置，或稍后重试")
    
    elif need_bot_reply and not st.session_state.use_api:
        for msg in messages_to_show[:-1]:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    render_bot_text(msg["content"])
                else:
                    st.markdown(msg["content"])
        with st.chat_message("user"):
            st.markdown(last_user_msg)
        sim_reply = """📋 **模拟模式提示**

当前为模拟演示模式，无法调用Bot。

请切换到「🤖 真实AI对话」模式获得完整分析能力。"""
        with st.chat_message("assistant"):
            st.markdown(sim_reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": sim_reply})
    
    # 快捷操作按钮 — 放在聊天区域底部，输入框上方
    st.markdown("""<div style="background:linear-gradient(135deg,#4ECDC4,#44B09E);border-radius:10px;padding:10px 16px;margin:8px 0 4px 0;box-shadow:0 2px 6px rgba(78,205,196,0.3)">
    <span style="color:#fff;font-weight:700;font-size:0.95rem">💬 继续追问</span>
    <span style="color:#E0F7FA;font-size:0.85rem">— 在下方输入框补充信息、调整方向，或点快捷按钮</span>
    </div>""", unsafe_allow_html=True)
    qa_col1, qa_col2, qa_col3, qa_col4 = st.columns(4)
    with qa_col1:
        if st.button("📊 策略方案", use_container_width=True, key="btn_strategy", help="获取完整投放策略"):
            st.session_state._msg_queue.append(f"{build_data_summary(st.session_state.input_data)}\n基于以上分析，请给出完整的投放策略方案（出价、时段分配、预算分配等）")
            st.rerun()
    with qa_col2:
        if st.button("💡 素材灵感", use_container_width=True, key="btn_material", help="获取创意方向"):
            st.session_state._msg_queue.append(f"{build_data_summary(st.session_state.input_data)}\n请给出素材灵感和创意方向，重点是行业实测跑量方向")
            st.rerun()
    with qa_col3:
        if st.button("🔍 深入诊断", use_container_width=True, key="btn_diagnosis", help="更深入分析"):
            st.session_state._msg_queue.append(f"{build_data_summary(st.session_state.input_data)}\n请更深入地诊断一下，每个指标的问题和优化空间分别是什么？")
            st.rerun()
    with qa_col4:
        if st.button("🔄 重新分析", use_container_width=True, key="btn_reset", help="从头开始"):
            st.session_state.chat_messages = []
            st.session_state.conversation_id = None
            st.session_state._msg_queue = [build_initial_message(st.session_state.input_data)]
            st.rerun()
    
    # 聊天输入框
    user_input = st.chat_input("继续追问或调整方向…", key="chat_input_main")
    if user_input and user_input.strip():
        # 追问时自动注入数据摘要，避免Bot遗忘上下文
        context_msg = f"{build_data_summary(st.session_state.input_data)}\n{user_input.strip()}"
        st.session_state.chat_messages.append({"role": "user", "content": context_msg})
        st.rerun()

# ========== 反馈区 ==========
if st.session_state.input_data and st.session_state.chat_messages:
    st.markdown("---")
    fb_col1, fb_col2 = st.columns(2)
    with fb_col1:
        if st.button("👍 本次分析有用", use_container_width=True):
            st.session_state.feedback_records.append({
                "time": datetime.now().strftime("%m-%d %H:%M"),
                "rating": "有用",
                "detail": ""
            })
            # 静默写入飞书表格，不展示飞书链接
            last_question = ""
            for m in reversed(st.session_state.chat_messages):
                if m["role"] == "user":
                    last_question = m["content"][:100]
                    break
            submit_feedback_to_feishu("有用", last_question)
            st.success("感谢反馈！🎉")
    with fb_col2:
        if st.button("👎 还需要改进", use_container_width=True):
            st.session_state.feedback_records.append({
                "time": datetime.now().strftime("%m-%d %H:%M"),
                "rating": "没用",
                "detail": ""
            })
            # 写入飞书表格 + 展示飞书链接让用户详细反馈
            last_question = ""
            for m in reversed(st.session_state.chat_messages):
                if m["role"] == "user":
                    last_question = m["content"][:100]
                    break
            submit_feedback_to_feishu("没用", last_question)
            st.info("已记录，会持续优化～ 🙏")
            st.markdown("📝 **欢迎到反馈表单详细说说**，帮分身变得更聪明～ [点击填写反馈](https://my.feishu.cn/share/base/form/shrcnzsgzjdz3qN1bRkHVeMgTDg)")

# ========== 页脚 ==========
st.divider()
mode_text = "🤖 AI对话模式" if st.session_state.use_api else "🎮 模拟演示模式"
st.caption(f"🔧 优化工作台 v3.0 · {mode_text} · 数据输入 + 多轮对话分析")
