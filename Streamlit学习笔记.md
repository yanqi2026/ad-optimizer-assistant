# Streamlit 入门学习笔记
> Day 10 - 2026.06.11

## 核心概念速查

### 1. 页面配置 set_page_config
```python
st.set_page_config(
    page_title="优化师分身",
    page_icon="🎯",
    layout="wide",  # "centered" 或 "wide"
    initial_sidebar_state="collapsed"
)
```
⚠️ 必须放在脚本最开头，第一个st命令之前

### 2. 布局容器

#### st.sidebar - 侧边栏
```python
# 方式1：上下文管理器
with st.sidebar:
    st.selectbox("选择", options)
    st.slider("滑块", 0, 100)

# 方式2：方法调用
sidebar = st.sidebar
sidebar.selectbox("选择", options)
```

#### st.columns - 分栏
```python
# 等宽分栏
col1, col2, col3 = st.columns(3)

# 不等宽分栏 [比例]
left, right = st.columns([2, 1])

# 带间距
col1, col2 = st.columns(2, gap="large")
```

#### st.tabs - 标签页
```python
tab1, tab2, tab3 = st.tabs(["主页", "数据", "设置"])
with tab1:
    st.write("Tab 1 内容")
```

#### st.expander - 可折叠
```python
with st.expander("详细设置"):
    st.write("折叠内容")
```

#### st.container - 容器
```python
# 普通容器
with st.container():
    st.write("内容")

# 带边框
with st.container(border=True):
    st.write("带边框内容")
```

#### st.empty - 占位符
```python
placeholder = st.empty()
# 后续可以替换内容
placeholder.write("新内容")
placeholder.empty()  # 清空
```

### 3. Widget 组件

#### 输入类
```python
st.text_input("提示文字", placeholder="占位符", value="默认值")
st.number_input("数字", min_value=0, max_value=100, value=50, step=10)
st.text_area("多行文本")
st.selectbox("下拉选择", ["选项1", "选项2"])
st.multiselect("多选", ["A", "B", "C"], default=["A"])
st.slider("滑块", 0, 100, 50)
```

#### 按钮类
```python
# 普通按钮
if st.button("提交"):
    st.write("点击了")

# 表单提交（推荐用于批量输入）
with st.form():
    st.text_input("姓名")
    submitted = st.form_submit_button("提交")

# 带回调
def on_click():
    st.session_state.count += 1
st.button("增加", on_click=on_click)
```

#### 展示类
```python
st.metric("标题", "数值", "变化")
st.progress(0.5)  # 进度条
st.spinner("加载中...")  # 配合with使用
```

### 4. Session State 状态管理
```python
# 初始化
if 'count' not in st.session_state:
    st.session_state.count = 0

# 读取
st.write(st.session_state.count)

# 更新
st.session_state.count += 1

# 与Widget关联（用key）
if 'slider_val' not in st.session_state:
    st.session_state.slider_val = 50
st.slider("滑块", 0, 100, key="slider_val")
st.write(st.session_state.slider_val)  # 自动同步
```

### 5. 回调函数 Callbacks
```python
def increment():
    st.session_state.count += 1

# 基础用法
st.button("+1", on_click=increment)

# 传参数
def add_value(val):
    st.session_state.count += val

st.button("+5", on_click=add_value, kwargs={"val": 5})

# 表单回调
def submit_form():
    # 处理表单数据
    pass

with st.form(key="my_form"):
    st.text_input("姓名")
    st.form_submit_button("提交", on_click=submit_form)
```

### 6. 多页面应用
```
项目/
├── app.py              # 主入口
└── pages/
    ├── 0_Home.py        # 主页（0_控制排序）
    ├── 1_页面1.py
    └── 2_页面2.py
```
- 自动生成侧边栏导航
- 文件名前缀数字控制排序

### 7. 主题配置 .streamlit/config.toml
```toml
[theme]
primaryColor = "#4ECDC4"
backgroundColor = "#F7F7F7"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#262730"
font = "sans serif"
```

### 8. 常用技巧

#### 隐藏元素重新显示
```python
# 侧边栏导航
# 在 config.toml 设置
[client]
showSidebarNavigation = false
```

#### 成功/失败提示
```python
st.success("操作成功！")
st.error("出错了！")
st.warning("注意！")
st.info("提示信息")
```

#### 页面跳转
```python
st.switch_page("pages/1_页面.py")
```

## 学习资源
- 官方文档：https://docs.streamlit.io/
- API参考：https://docs.streamlit.io/develop/api-reference
- 官方教程：https://docs.streamlit.io/get-started
