# Layout Generator 合并分析

## 🔍 关键差异发现

### 1. 字段名差异

#### 28nm格式（当前项目）
```json
{
    "name": "VCM",
    "device": "PDB3AC_H_G",        // 使用 "device"
    "position": "left_0",
    "type": "pad",
    "pin_connection": {            // 使用 "pin_connection"
        "AIO": {"label": "VCM"}
    }
}
```

#### 180nm格式（目标项目）
```json
{
    "name": "VIOLA",
    "device_type": "PVDD1CDG",     // 使用 "device_type"
    "view_name": "layout",
    "domain": "analog",
    "pad_width": 80,
    "pad_height": 120,
    "position": "top_0",
    "type": "pad",
    "pin_config": {                 // 使用 "pin_config"
        "VDD": {"label": "VIOLA"}
    }
}
```

### 2. ring_config差异

#### 28nm格式
```json
{
    "ring_config": {
        "width": 3,
        "height": 3,
        "placement_order": "counterclockwise"
    }
}
```

#### 180nm格式
```json
{
    "ring_config": {
        "chip_width": 2250,
        "chip_height": 2160,
        "pad_spacing": 90,
        "pad_width": 80,
        "pad_height": 120,
        "corner_size": 130,
        "top_count": 3,
        "bottom_count": 3,
        "left_count": 3,
        "right_count": 3,
        "placement_order": "clockwise"
    }
}
```

### 3. 代码差异

#### 当前项目（28nm）
- 使用 `instance.get("device", "")`
- 使用 `instance.get("pin_connection", {})`
- 组件中使用 `component["device"]`

#### 目标项目（180nm）
- 使用 `instance.get("device_type", "")`
- 使用 `instance.get("pin_config", {})`
- 组件中使用 `component["device_type"]`
- 支持 `view_name`, `domain`, `pad_width`, `pad_height` 等字段

## 🎯 合并策略

需要创建一个兼容层，自动识别并转换两种格式。

