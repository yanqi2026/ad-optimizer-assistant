"""
Coze API 模块 - 处理与优化师分身Bot的流式对话
支持SSE流式输出，自动管理会话上下文

使用方式：
  from coze_api import CozeAPI, build_diagnosis_prompt, build_strategy_prompt, build_material_prompt
  
  api = CozeAPI(pat_token)
  conv_id = api.create_conversation()
  for chunk in api.stream_chat(prompt, conv_id):
      print(chunk, end="", flush=True)
"""
import json
import re
import requests

# ========== 配置 ==========
COZE_API_BASE = "https://api.coze.cn"
DEFAULT_BOT_ID = "7647840847790293042"
DEFAULT_USER_ID = "streamlit_opt_user"


class CozeAPI:
    """Coze Bot API 客户端，支持流式对话"""
    
    def __init__(self, pat_token, bot_id=DEFAULT_BOT_ID, user_id=DEFAULT_USER_ID):
        self.pat_token = pat_token
        self.bot_id = bot_id
        self.user_id = user_id
    
    @property
    def _headers(self):
        return {
            "Authorization": f"Bearer {self.pat_token}",
            "Content-Type": "application/json"
        }
    
    def create_conversation(self):
        """创建新会话，返回 conversation_id"""
        resp = requests.post(
            f"{COZE_API_BASE}/v1/conversation/create",
            headers=self._headers,
            json={},
            timeout=30
        )
        data = resp.json()
        if data.get("code") != 0:
            raise ConnectionError(
                f"创建会话失败: code={data.get('code')}, msg={data.get('msg', '未知错误')}"
            )
        return data["data"]["id"]
    
    def stream_chat(self, prompt, conversation_id):
        """
        流式对话，yield 增量文本片段。
        需要预先创建 conversation。
        
        用法:
            for chunk in api.stream_chat(prompt, conv_id):
                # chunk 是一小段文本
        """
        payload = {
            "bot_id": self.bot_id,
            "user_id": self.user_id,
            "stream": True,
            "auto_save_history": True,
            "additional_messages": [{
                "role": "user",
                "content": prompt,
                "content_type": "text"
            }]
        }
        
        resp = requests.post(
            f"{COZE_API_BASE}/v3/chat",
            headers=self._headers,
            json=payload,
            stream=True,
            timeout=120
        )
        
        if resp.status_code != 200:
            error_msg = resp.text[:300] if resp.text else f"HTTP {resp.status_code}"
            raise ConnectionError(f"对话请求失败: {error_msg}")
        
        current_event = None
        event_types = []  # 收集所有事件类型用于调试
        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            
            if line.startswith("event:"):
                current_event = line[6:].strip()
                if current_event not in event_types:
                    event_types.append(current_event)
            elif line.startswith("data:"):
                data_str = line[5:].strip()
                
                # 处理增量文本
                if current_event == "conversation.message.delta":
                    try:
                        data = json.loads(data_str)
                        content = data.get("content", "")
                        # 只输出助手文本回复，过滤掉工具调用等
                        if content and data.get("content_type", "text") == "text":
                            yield content
                    except json.JSONDecodeError:
                        continue
                # 检查错误事件
                elif current_event == "conversation.chat.failed":
                    try:
                        data = json.loads(data_str)
                        msg = data.get("msg", data.get("last_error", {}).get("msg", "未知错误"))
                        raise ConnectionError(f"Bot对话失败: {msg}")
                    except (json.JSONDecodeError, ConnectionError):
                        raise
                    except Exception:
                        raise ConnectionError(f"Bot对话失败: {data_str[:200]}")
                elif current_event == "conversation.chat.completed":
                    # 检查completed事件中的状态
                    try:
                        data = json.loads(data_str)
                        status = data.get("status", "")
                        if status == "failed":
                            msg = data.get("last_error", {}).get("msg", "未知错误")
                            raise ConnectionError(f"Bot对话完成但状态为failed: {msg}")
                    except (json.JSONDecodeError, ConnectionError):
                        if isinstance(e, ConnectionError):
                            raise
                    break
    
    def chat(self, prompt, conversation_id):
        """非流式对话，返回完整响应文本"""
        chunks = []
        for chunk in self.stream_chat(prompt, conversation_id):
            chunks.append(chunk)
        return "".join(chunks)
    
    def test_connection(self):
        """
        测试API连接是否正常
        返回 (success: bool, message: str, conversation_id: str|None)
        """
        try:
            conv_id = self.create_conversation()
            # 发一条简短消息测试
            resp_text = self.chat("你好", conv_id)
            if resp_text:
                return True, "连接正常", conv_id
            else:
                return False, "Bot返回为空", conv_id
        except ConnectionError as e:
            return False, str(e), None
        except Exception as e:
            return False, f"未知错误: {str(e)[:200]}", None


# ========== Prompt构建函数 ==========

def build_diagnosis_prompt(data):
    """构建诊断场景Prompt，触发Bot的诊断模式"""
    avg_loan_info = f"\n- 件均：{data.get('avg_loan', 0)}元" if data.get('avg_loan', 0) > 0 else ""
    problem = data.get('user_problem', '')
    
    if problem:
        # 有问题描述时：诉求驱动，数据佐证
        return f"""我要解决的问题是：{problem}

请你：
1. 先分析这个问题本身的成因和关键影响因素（不要一上来就对比数据，先针对我说的具体问题拆解分析）
2. 再结合下面的账户数据，验证你的分析并给出针对性建议

账户数据：
- 行业：{data.get('industry', '金融借贷')}
- 平台：{data.get('platform', '腾讯广告MP')}
- CTR（点击率）：{data.get('ctr', 'N/A')}%
- CVR（转化率）：{data.get('cvr', 'N/A')}%
- CPA（转化成本）：{data.get('cpa', 'N/A')}元
- CPC（点击成本）：{data.get('cpc', 'N/A')}元
- 日消耗：{data.get('spend', 'N/A')}元
- 日转化：{data.get('conversions', 'N/A')}
- 产品类型：{data.get('product_type', '信用贷')}{avg_loan_info}
- 目标CPA：{data.get('target_cpa', 'N/A')}元
- 出价模式：{data.get('bid_mode', 'oCPM')}（默认竞价广告·oCPM，如需其他模式可切换）
- 优化方向：{data.get('optimization', '平衡')}

⚠️ 你的诊断必须以「{problem}」为主线，不要给出与此诉求矛盾的结论。例如：如果我说了只跑6-18点，你就不应该在分析中建议加大夜间投放。"""
    else:
        # 无问题描述时：纯数据分析
        return f"""帮我诊断一下账户数据：
- 行业：{data.get('industry', '金融借贷')}
- 平台：{data.get('platform', '腾讯广告MP')}
- CTR（点击率）：{data.get('ctr', 'N/A')}%
- CVR（转化率）：{data.get('cvr', 'N/A')}%
- CPA（转化成本）：{data.get('cpa', 'N/A')}元
- CPC（点击成本）：{data.get('cpc', 'N/A')}元
- 日消耗：{data.get('spend', 'N/A')}元
- 日转化：{data.get('conversions', 'N/A')}
- 产品类型：{data.get('product_type', '信用贷')}{avg_loan_info}
- 目标CPA：{data.get('target_cpa', 'N/A')}元
- 出价模式：{data.get('bid_mode', 'oCPM')}（默认竞价广告·oCPM，如需其他模式可切换）
- 优化方向：{data.get('optimization', '平衡')}"""


def build_strategy_prompt(data):
    """构建策略场景Prompt，触发Bot的策略模式（基于当前对话上下文）"""
    problem = data.get('user_problem', '')
    
    if problem and problem != '无':
        # 有问题描述时：诉求驱动策略
        return f"""我的核心诉求是：{problem}

请基于以上诊断结果，围绕我的核心诉求制定投放策略（默认竞价广告·oCPM出价）：
- 目标CPA：{data.get('target_cpa', 80)}元
- 日预算：{data.get('daily_budget', 10000)}元
- 出价模式：{data.get('bid_mode', 'oCPM')}（如当前模式不合适，请推荐更适合的出价方式并说明理由）
- 优化方向：{data.get('optimization', '平衡')}
- 产品类型：{data.get('product_type', '信贷产品')}
- 平台：{data.get('platform', '腾讯广告MP')}

⚠️ 策略中每个环节都必须满足「{problem}」。例如：如果限定了投放时段，时段分配只能在允许范围内；如果要求保量，不能给出收缩预算的建议。"""
    else:
        return f"""基于以上诊断结果，请给出完整的投放策略方案（默认竞价广告·oCPM出价）：
- 目标CPA：{data.get('target_cpa', 80)}元
- 日预算：{data.get('daily_budget', 10000)}元
- 出价模式：{data.get('bid_mode', 'oCPM')}（如当前模式不合适，请推荐更适合的出价方式并说明理由）
- 优化方向：{data.get('optimization', '平衡')}
- 产品类型：{data.get('product_type', '信贷产品')}
- 平台：{data.get('platform', '腾讯广告MP')}"""


def build_material_prompt(data):
    """构建素材场景Prompt，触发Bot的素材模式（基于当前对话上下文）"""
    problem = data.get('user_problem', '')
    
    if problem:
        # 有问题描述时：诉求驱动素材方向
        return f"""我的核心诉求是：{problem}

请围绕此诉求给出素材灵感和创意方向，重点是行业实测跑量方向和拓展思路，而非通用文案模板。

🚫【金融素材合规红线——绝对禁止出现以下内容，违者审核直接驳回】：
1. 严禁"还信用卡""代还信用卡""以贷还贷"等暗示贷款还信用卡的表述（以贷还贷属违规）
2. 严禁"100%下款""必过""秒批""免息""不用白不用""3分钟到账""帮你度过难关""立即申请"等绝对化/承诺性表述
3. 严禁暗示贷款用于还债、还信用卡、还花呗等场景，可用"资金周转""应急备用"等中性表述替代
4. 所有涉额度、时效、息费的内容必须加合规注释

✅ 合规替代表述：「灵活额度」「了解更多」「线上申请便捷」「最高X万额度」「具体以实际审批为准」
- 产品类型：{data.get('product_type', '信贷产品')}
- 优化方向：{data.get('optimization', '平衡')}
- 目标人群：25-44岁，有资金周转需求

请按以下结构输出：
1. 跑量素材公式：用简洁公式概括该行业跑量素材的核心结构
2. 开场3秒钩子参考：给出3-4个具体可用的开场话术（换人设/换场景=新素材）
3. 拓展方向（5-6个）：每个方向包含——方向名称、核心逻辑、4个具体拓展思路、CTR预期/难度/情绪走向/生命周期
4. 行业素材趋势：4-6条行业最新素材趋势要点
5. 温馨提示：提醒用户如需实时大盘跑量优质素材参考案例，可登录腾讯广告账户前往妙思灵感后台(https://admuse.qq.com/#/idea)，或登录巨量引擎账户前往巨量创意平台(https://cc.oceanengine.com/)。此链接必须输出，不可省略。

⚠️ 素材方向必须紧扣「{problem}」，不要给出与此诉求无关的通用方案。"""
    else:
        return f"""请给出素材灵感和创意方向，重点是行业实测跑量方向和拓展思路，而非通用文案模板。

🚫【金融素材合规红线——绝对禁止出现以下内容，违者审核直接驳回】：
1. 严禁"还信用卡""代还信用卡""以贷还贷"等暗示贷款还信用卡的表述（以贷还贷属违规）
2. 严禁"100%下款""必过""秒批""免息""不用白不用""3分钟到账""帮你度过难关""立即申请"等绝对化/承诺性表述
3. 严禁暗示贷款用于还债、还信用卡、还花呗等场景，可用"资金周转""应急备用"等中性表述替代
4. 所有涉额度、时效、息费的内容必须加合规注释

✅ 合规替代表述：「灵活额度」「了解更多」「线上申请便捷」「最高X万额度」「具体以实际审批为准」
- 产品类型：{data.get('product_type', '信贷产品')}
- 优化方向：{data.get('optimization', '平衡')}
- 目标人群：25-44岁，有资金周转需求

请按以下结构输出：
1. 跑量素材公式：用简洁公式概括该行业跑量素材的核心结构
2. 开场3秒钩子参考：给出3-4个具体可用的开场话术（换人设/换场景=新素材）
3. 拓展方向（5-6个）：每个方向包含——方向名称、核心逻辑、4个具体拓展思路、CTR预期/难度/情绪走向/生命周期
4. 行业素材趋势：4-6条行业最新素材趋势要点
5. 温馨提示：提醒用户如需实时大盘跑量优质素材参考案例，可登录腾讯广告账户前往妙思灵感后台(https://admuse.qq.com/#/idea)，或登录巨量引擎账户前往巨量创意平台(https://cc.oceanengine.com/)。此链接必须输出，不可省略。"""


# ========== JSON解析工具（备用） ==========

def parse_json_from_text(text):
    """
    从文本中提取JSON对象
    依次尝试：直接解析 → 提取代码块 → 提取花括号区间
    返回 dict 或 None
    """
    # 尝试1: 直接解析
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass
    
    # 尝试2: 从markdown代码块提取
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except (json.JSONDecodeError, TypeError):
            pass
    
    # 尝试3: 提取第一个完整的JSON对象（平衡花括号）
    depth = 0
    start = None
    for i, c in enumerate(text):
        if c == '{':
            if depth == 0:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start:i+1])
                except (json.JSONDecodeError, TypeError):
                    start = None
                    continue
    
    return None


# ========== 需求理解Prompt ==========

def build_requirement_prompt(data):
    """构建需求理解Prompt，在诊断之前先明确用户诉求和调整方向"""
    problem = data.get('user_problem', '')
    
    if not problem or problem == '无':
        return None  # 无问题描述时跳过此步骤
    
    avg_loan_info = f"\n- 件均：{data.get('avg_loan', 0)}元" if data.get('avg_loan', 0) > 0 else ""
    
    return f"""请仔细阅读用户的问题描述，然后给出你对需求的理解和后续各步骤的方向侧重。

【用户问题描述】
{problem}

【用户账户背景】
- 行业：{data.get('industry', '金融借贷')}
- 平台：{data.get('platform', '腾讯广告MP')}
- 产品类型：{data.get('product_type', '信用贷')}{avg_loan_info}
- 出价模式：{data.get('bid_mode', 'oCPM')}
- 优化方向：{data.get('optimization', '平衡')}
- 目标CPA：{data.get('target_cpa', 'N/A')}元
- 日预算：{data.get('daily_budget', 'N/A')}元

请按以下结构输出（简洁明确，不要废话）：

📌 需求理解：
用1-2句话概括用户的核心诉求是什么

🎯 关键约束：
列出用户明确提出的限制条件（如时段限制、成本上限、保量要求等），如果没有则写"无特殊约束"

🔄 方向调整：
基于用户诉求，说明后续诊断、策略、素材三个环节分别需要侧重什么、调整什么。例如：
- 诊断环节：应重点分析哪些指标、排查哪些方向
- 策略环节：哪些常规建议不适用、应如何调整
- 素材环节：创意方向应侧重哪些角度

⚠️ 以上理解将作为后续所有分析的前提约束，后续输出不得与此理解矛盾。"""
