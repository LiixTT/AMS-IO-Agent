# 基于配置文件的Layout生成器重构方案

## 📋 概述

采用**最小改动 + 提取差异模块**的方案，通过配置文件驱动不同工艺节点的设备列表和参数，避免硬编码，提高可维护性。

## ✅ 已完成的改动

### 1. 配置文件整合
- ✅ 创建 `config/lydevices_28.json` - 28nm工艺设备配置
- ✅ 创建 `config/lydevices_180.json` - 180nm工艺设备配置
- ✅ 修改 `process_node_config.py` - 从JSON文件加载配置并合并到现有配置

### 2. 设备分类器重构
- ✅ 修改 `device_classifier.py` - 从配置文件加载设备列表，支持多工艺节点
- ✅ 所有分类方法现在接受 `process_node` 参数

### 3. Filler生成器重构
- ✅ 修改 `filler_generator.py` - 从配置文件获取filler设备名称
- ✅ 所有方法现在接受 `process_node` 参数

### 4. Layout生成器更新
- ✅ 更新 `layout_generator.py` - 传递 `process_node` 参数给所有设备分类调用
- ✅ 更新 `auto_filler.py` - 传递 `process_node` 参数给所有filler生成调用

## 📁 文件结构

```
config/
├── lydevices_28.json      # 28nm工艺设备配置
└── lydevices_180.json     # 180nm工艺设备配置

src/app/layout/
├── process_node_config.py  # 配置加载器（已增强）
├── device_classifier.py     # 设备分类器（已重构）
├── filler_generator.py      # Filler生成器（已重构）
├── layout_generator.py      # Layout生成器（已更新）
└── auto_filler.py           # 自动Filler生成（已更新）
```

## 🔧 配置文件格式

### lydevices_28.json / lydevices_180.json

```json
{
  "process": "28",
  "layout_params": {
    "pad_width": 20,
    "pad_height": 110,
    "corner_size": 110,
    "pad_spacing": 60
  },
  "digital_devices": [...],
  "analog_devices": [...],
  "digital_io": [...],
  "analog_io": [...],
  "corner_devices": [...],
  "filler_devices": [...],
  "analog_filler": [...],
  "digital_filler": [...],
  "cut_devices": [...],
  "device_masters": {
    "default_library": "...",
    "default_view": "layout"
  }
}
```

## 💡 优势

1. **配置驱动** - 设备列表和参数从JSON文件加载，无需修改代码
2. **向后兼容** - 如果配置文件不存在，使用硬编码的默认值
3. **易于扩展** - 新增工艺节点只需添加新的JSON配置文件
4. **最小改动** - 保持现有代码结构，只添加配置加载逻辑
5. **类型安全** - 所有方法都有默认参数，保持API兼容性

## 🔄 使用方式

### 基本使用（无需改动）

```python
# 自动从配置文件加载
generator = LayoutGenerator(process_node="28nm")
# 或
generator = LayoutGenerator(process_node="180nm")
```

### 配置文件优先级

1. 首先尝试从 `config/lydevices_{process}.json` 加载
2. 如果文件不存在或加载失败，使用硬编码的默认配置
3. JSON配置会合并到基础配置中

## 📝 后续工作（可选）

- [ ] 提取PSUB生成逻辑到独立模块（180nm需要）
- [ ] 将更多工艺特定逻辑移到配置文件
- [ ] 添加配置文件验证和错误处理

## 🎯 设计原则

1. **最小改动** - 保持现有代码结构，只添加必要的配置加载
2. **向后兼容** - 所有改动都有默认值，不影响现有代码
3. **配置优先** - 配置文件优先于硬编码，但提供fallback
4. **易于维护** - 设备列表在JSON中，修改无需改代码

