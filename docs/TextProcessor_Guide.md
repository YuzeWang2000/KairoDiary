# TextProcessor 使用说明

## 功能概述

TextProcessor 类提供了多种文本处理功能，支持配置化的处理方法选择：
- **大模型方法**：通过 ollama 调用本地部署的大语言模型
- **传统方法**：基于规则和第三方库的传统处理方法
- **灵活配置**：支持在初始化时和运行时配置处理偏好

## 初始化配置

### 构造函数参数

```python
TextProcessor(
    ollama_url: str = "http://localhost:11434",  # Ollama 服务器 URL
    preferred_model: str = "gemma3n:latest",     # 首选的 Ollama 模型
    use_llm_first: bool = True,                  # 是否优先使用大模型
    enable_spell_checker: bool = True,           # 是否启用传统拼写检查器
    enable_translator: bool = True               # 是否启用传统翻译器
)
```

### 配置示例

```python
# 默认配置 - 优先使用大模型
processor = TextProcessor()

# 优先使用传统方法
processor = TextProcessor(use_llm_first=False)

# 自定义模型和服务器
processor = TextProcessor(
    ollama_url="http://192.168.1.100:11434",
    preferred_model="llama2:latest",
    use_llm_first=True
)

# 禁用部分传统工具
processor = TextProcessor(
    enable_spell_checker=False,  # 不使用 spellchecker 库
    enable_translator=False      # 不使用 googletrans 库
)
```

## 运行时配置管理

### 设置方法

```python
# 修改 Ollama 服务器 URL
processor.set_ollama_url("http://localhost:11435")

# 修改首选模型
processor.set_preferred_model("gemma2:latest")

# 切换处理方法偏好
processor.set_use_llm_first(False)  # 改为优先使用传统方法
```

### 查询方法

```python
# 获取可用模型列表
models = processor.get_available_models()
print("可用模型:", models)

# 获取当前设置
settings = processor.get_current_settings()
print("当前配置:", settings)
```

## 支持的功能

### 1. 拼写检查 (spell_check)

```python
# 自动选择方法（根据 use_llm_first 设置）
result, method = processor.spell_check("This is a testt with errrors.")

# 强制使用大模型
result, method = processor.spell_check(text, force_method='llm')

# 强制使用传统方法
result, method = processor.spell_check(text, force_method='traditional')
```

- **大模型方法**：使用 LLM 智能检测和纠正拼写错误
- **传统方法**：基于 spellchecker 库的拼写纠正

### 2. 翻译 (translate)

```python
# 自动选择方法
result, method = processor.translate("Hello world", "中文")

# 强制使用指定方法
result, method = processor.translate(text, "中文", force_method='llm')
```

- **大模型方法**：使用 LLM 进行高质量翻译
- **传统方法**：使用 googletrans 库进行翻译

### 3. 文本润色 (polish)

```python
# 自动选择方法
result, method = processor.polish("this   text needs   polishing.")

# 强制使用指定方法  
result, method = processor.polish(text, force_method='traditional')
```

- **大模型方法**：使用 LLM 优化文本表达
- **传统方法**：基于规则的基础格式化

### 4. 文本总结 (summarize)

```python
# 自动选择方法
result, method = processor.summarize(long_text)

# 强制使用指定方法
result, method = processor.summarize(text, force_method='llm')
```

- **大模型方法**：使用 LLM 生成智能摘要
- **传统方法**：基于规则的简单摘要（取前几句或首末句）

## Ollama 集成

### 自动检测
- 启动时自动检测 ollama 服务（默认端口 11434）
- 获取可用模型列表
- 连接失败时自动降级到传统方法

### 使用要求
1. 安装并启动 ollama 服务
2. 下载至少一个语言模型
3. 确保 ollama 运行在 `http://localhost:11434`

### 示例 ollama 模型安装
```bash
# 安装轻量级模型
ollama pull gemma3n

# 安装代码专用模型
ollama pull codellama:7b

# 查看已安装模型
ollama list
```

## 使用方法

### 在日记编辑器中使用
1. 选中要处理的文本
2. 右键打开上下文菜单
3. 选择"文本处理" → 选择具体功能
4. 系统会自动选择最佳处理方法

### 返回值说明
大部分函数返回元组 `(处理结果, 使用方法)`：
- `处理结果`：处理后的文本
- `使用方法`：说明使用了哪种方法（"大模型 (ollama)" 或 "传统方法"）

## 错误处理

### 网络连接问题
- 自动检测 ollama 服务状态
- 连接失败时降级到传统方法
- 超时设置防止长时间等待

### 模型调用失败
- 自动重试机制
- 降级到传统方法
- 详细错误日志输出

## 扩展性

### 添加新的处理功能
1. 在 `TextProcessor` 类中添加新方法
2. 实现 `_method_with_llm()` 和传统方法
3. 在 `diaryEditor.py` 中添加对应的菜单项

### 支持其他 LLM 服务
可以扩展 `_call_ollama()` 方法来支持其他 API：
- OpenAI API
- Anthropic Claude
- 本地 Hugging Face 模型
- 等等

## 配置选项

可以通过修改 `__init__()` 方法来自定义：
- ollama 服务地址
- 默认使用的模型
- 超时时间
- 重试次数
