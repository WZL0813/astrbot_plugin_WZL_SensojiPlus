# astrbot_plugin_WZL_SensojiPlus
# 浅草寺抽签插件版本说明

## v1.2.4
**发布日期**: 2025-03-20  
**更新内容**:
- 一些小优化。

---

## v1.2.3
**发布日期**: 2025-03-19    
**更新内容**:
- 将输出文字更改为输出图片，缓解了消息过长导致刷屏的问题。

---

## v1.2.2
**发布日期**: 2025-03-18    
**更新内容**:
- 优化了代码逻辑，修复了在没有LLM对话时调用解签功能报错的问题。

---

## v1.2.1
**发布日期**: 2025-03-18    
**更新内容**:  
- 新增了解签指令，避免了在特定大模型下自然语言解签无法触发解签函数导致解签功能失效的问题。
- 优化了代码逻辑，避免了在特定情况下解签对象不对的问题。

---

## v1.2.0
**发布日期**: 2025-03-17    
**更新内容**:  
- 新增了转运和LLM解签功能。用户可通过`转运`指令进行转运操作，并在发送`解签`或`解释一下抽的签`等指令时，系统将自动调用LLM进行解签。
- 优化了代码逻辑

---

## v1.1.2
**发布日期**: 2025-03-17    
**更新内容**:  
- 修改签文，使用日本浅草寺观音签，总数达到100种。
- 增加了诗文解释和运势细节。

---

## v1.1.1
**发布日期**: 2025-03-16    
**更新内容**:  
- 新增 JSON 文件存储功能：将用户抽签结果持久化存储到 JSON 文件中，避免重启后数据丢失。文件路径：插件目录下的 user_daily_results.json。
- 优化数据清理逻辑：在加载数据时自动清理过期的抽签记录，确保数据时效性。
- 提升代码可维护性：将数据加载和保存逻辑封装为独立函数（load_data 和 save_data），便于后续扩展和维护。

---

## v1.1.0
**发布日期**: 2025-03-16    
**更新内容**:  
- 新增每日抽签限制功能，用户每天只能抽取一次签文，当天后续抽签会返回第一次的结果。
- 自动清理过期数据，日期更新后用户可重新抽签。
- 优化代码逻辑，使用字典存储用户抽签结果，提升运行效率。

---

## v1.0.2
**发布日期**: 2025-03-16    
**更新内容**:  
- 优化了代码结构，将签文数据单独拆分为 sensoji_data.py 文件，便于维护和扩展。

---

## v1.0.1
**发布日期**: 2025-03-16    
**更新内容**:  
- 新增签文，总数达到 15 种，增加更多吉凶等级（如“半吉”、“末凶”等）。  
- 优化签文输出格式，增加诗句和建议部分，提升用户体验。  
- 修复了部分签文描述不准确的问题。  

---

## v1.0.0
**发布日期**: 2025-03-16  
**更新内容**:  
- 实现浅草寺抽签功能，用户可以通过 `/抽签` 命令随机抽取签文。  
- 内置 7 种签文，包含吉凶等级、运势描述。  
- 支持 AstrBot 框架，插件安装简单，使用方便。

---