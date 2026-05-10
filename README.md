# 湘字号技能工具 Schema 注册中心

> 版本：v1.0.0 | 创建：2026-05-10 | 维护：湘江研究院研究中心

## 概述

本文档定义了湘字号AI体系中所有技能的标准化工具Schema，基于 JSON Schema Draft-07 规范，用于：
- 工具参数验证与类型安全
- 自动化工具发现与注册
- 跨Agent调用协议标准化
- 微信远程操控的可靠性保障

## 已注册技能 Schema

| 技能 | 文件名 | 版本 | 核心能力 |
|------|--------|------|---------|
| 湘小研 | `xiangxiaoyan.schema.json` | v2.1.0 | 政策检索、RAG查询、报告生成、跨省对比 |
| 湘小印 | `xiangxiaoyin.schema.json` | v1.3.0 | 文档转换、口吻润色、合规检查、质量质检 |
| 湘小法 | `xiangxiaofa.schema.json` | v3.0.0 | 合规审查、风险评估、质量门禁、法规引用 |
| 湘小协 | `xiangxiaoxie.schema.json` | v1.2.1 | GE流水线、IPC路由、白板协作、复杂度评估 |
| 湘小策 | `xiangxiaoche.schema.json` | v1.0.0 | 战略顾问、方法论指导、国资语境、成本控制 |
| 湘小审 | `xiangxiaoshen.schema.json` | v1.0.0 | 风险评估、权限审批、操作审计、安全告警 |

## 快速使用

### 1. 验证工具调用参数

```python
import json
from jsonschema import validate, ValidationError

# 加载Schema
with open('xiangxiaoyan.schema.json', 'r', encoding='utf-8') as f:
    schema = json.load(f)

# 待验证的工具调用
tool_call = {
    "tool_name": "xiangxiaoyan",
    "parameters": {
        "action": "policy_search",
        "query": "低空经济产业政策",
        "policy_brands": ["三高四新"],
        "max_results": 10
    }
}

# 验证
try:
    validate(instance=tool_call, schema=schema)
    print("✅ 参数验证通过")
except ValidationError as e:
    print(f"❌ 验证失败: {e.message}")
```

### 2. 工具发现机制

```python
import os
import json

SCHEMA_DIR = "C:\\Users\\Lee Gilbert\\.qclaw\\workspace\\xiang-tools-schema"

def discover_tools():
    """发现所有已注册的工具Schema"""
    tools = []
    for filename in os.listdir(SCHEMA_DIR):
        if filename.endswith('.schema.json'):
            with open(os.path.join(SCHEMA_DIR, filename), 'r', encoding='utf-8') as f:
                schema = json.load(f)
                tools.append({
                    "tool_name": schema["properties"]["tool_name"]["enum"][0],
                    "title": schema.get("title", ""),
                    "version": schema.get("version", ""),
                    "description": schema.get("description", ""),
                    "actions": schema["properties"]["parameters"]["properties"]["action"]["enum"]
                })
    return tools

# 使用示例
tools = discover_tools()
for tool in tools:
    print(f"📦 {tool['tool_name']} v{tool['version']}: {tool['title']}")
    print(f"   支持操作: {', '.join(tool['actions'])}")
```

### 3. 生成工具描述（用于LLM系统提示词）

```python
def generate_tool_descriptions():
    """生成供LLM使用的工具描述文本"""
    tools = discover_tools()
    descriptions = []
    for tool in tools:
        desc = f"""
### {tool['title']} ({tool['tool_name']})
- 版本: {tool['version']}
- 描述: {tool['description']}
- 支持操作:
"""
        for action in tool['actions']:
            desc += f"  - {action}\n"
        descriptions.append(desc)
    return "\n".join(descriptions)

# 输出可直接插入System Prompt
print(generate_tool_descriptions())
```

## Schema 设计规范

### 通用设计原则

1. **严格类型**：所有字段明确定义类型，禁止隐式转换
2. **必填校验**：`required` 字段必须完整，可选字段省略不传
3. **枚举约束**：状态、类型等字段使用 `enum` 限定取值范围
4. **条件校验**：使用 `allOf` + `if/then` 实现条件必填
5. **默认值**：常用参数提供 `default`，减少调用复杂度
6. **示例代码**：每个Schema包含 `examples` 供参考

### 路径字段规范

所有文件路径字段必须：
- 使用**裸路径格式**：`D:\\Work@湘江研究院\\file.md`
- 禁止使用Markdown链接、反引号、括号说明
- Windows路径使用双反斜杠或原始字符串

### 数组字段规范

- 必须是真实JSON数组：`["a", "b"]`
- 单个元素也要用数组：`["item"]`
- 禁止传 `null`、`""`、`{}`、`[]` 代替省略

## 版本管理

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0.0 | 2026-05-10 | 初始版本，包含6个湘字号技能Schema |

## 集成指南

### 与 OpenClaw 集成

将Schema目录注册到OpenClaw配置中：

```yaml
# openclaw.config.yml
skills:
  schema_registry:
    enabled: true
    path: "C:\\Users\\Lee Gilbert\\.qclaw\\workspace\\xiang-tools-schema"
    auto_discover: true
    validation: strict
```

### 与微信远程操控集成

Schema验证确保微信发来的自然语言指令能准确转换为结构化工具调用：

```
用户微信消息: "帮我查一下低空经济政策"
          ↓
[意图识别] → action="policy_search", query="低空经济政策"
          ↓
[Schema验证] → 检查参数是否符合 xiangxiaoyan.schema.json
          ↓
[工具调用] → 执行湘小研政策检索
          ↓
[结果返回] → 格式化后通过微信回复
```

## 维护说明

- Schema文件统一存放在 `xiang-tools-schema/` 目录
- 文件名格式：`{skill_name}.schema.json`
- 版本号与SKILL.md版本保持一致
- 修改Schema后需更新本README的版本历史

---

*湘江研究院研究中心 · AI体系标准化建设*
