# 设备命名规范指南

## ⚠️ 重要：工艺节点设备命名差异

### 28nm 工艺节点

**设备类型需要后缀**：`_H_G` 或 `_V_G`

- **水平设备**：`PDB3AC_H_G`, `PVDD1AC_H_G`, `PVSS1AC_H_G`
- **垂直设备**：`PDB3AC_V_G`, `PVDD1AC_V_G`, `PVSS1AC_V_G`
- **角点设备**：`PCORNERA_G`（不需要方向后缀）

**示例**：
```json
{
    "name": "VCM",
    "device": "PDB3AC_H_G",  // 完整设备名，包含后缀
    "position": "left_0",
    "type": "pad"
}
```

或者只指定基础设备名，系统会自动添加后缀：
```json
{
    "name": "VCM",
    "device": "PDB3AC",  // 基础设备名，系统会自动添加_H_G或_V_G
    "position": "left_0",
    "type": "pad"
}
```

### 180nm 工艺节点

**设备类型不需要后缀**：设备名已经是完整的

- **电源设备**：`PVDD1CDG`, `PVSS1CDG`, `PVDD2CDG`, `PVSS2CDG`
- **模拟设备**：`PVDD1ANA`, `PVSS1ANA`
- **角点设备**：`PCORNER`

**示例**：
```json
{
    "name": "VIOLA",
    "device": "PVDD1CDG",  // 完整设备名，不需要后缀
    "position": "top_0",
    "type": "pad"
}
```

**⚠️ 注意**：180nm的设备名已经是完整的，**不要**添加 `_H_G` 或 `_V_G` 后缀！

## 🔧 代码处理逻辑

`schematic_generator.py` 中的 `normalize_device_config()` 函数会根据工艺节点自动处理：

1. **28nm**：
   - 如果设备名没有后缀，自动根据位置添加 `_H_G` 或 `_V_G`
   - 如果设备名已有后缀，直接使用

2. **180nm**：
   - 设备名保持原样，**不添加**后缀
   - 只设置 orientation（方向）

## 📋 设备类型对照表

### 28nm 设备类型（需要后缀）

| 基础类型 | 水平设备 | 垂直设备 |
|---------|---------|---------|
| `PDB3AC` | `PDB3AC_H_G` | `PDB3AC_V_G` |
| `PVDD1AC` | `PVDD1AC_H_G` | `PVDD1AC_V_G` |
| `PVSS1AC` | `PVSS1AC_H_G` | `PVSS1AC_V_G` |
| `PDDW16SDGZ` | `PDDW16SDGZ_H_G` | `PDDW16SDGZ_V_G` |

### 180nm 设备类型（不需要后缀）

| 设备类型 | 说明 |
|---------|------|
| `PVDD1CDG` | 数字电源 |
| `PVSS1CDG` | 数字地 |
| `PVDD2CDG` | 数字电源2 |
| `PVSS2CDG` | 数字地2 |
| `PVDD1ANA` | 模拟电源 |
| `PVSS1ANA` | 模拟地 |
| `PCORNER` | 角点 |

## ✅ 正确示例

### 28nm 配置
```json
{
    "instances": [
        {
            "name": "VCM",
            "device": "PDB3AC_H_G",  // ✅ 正确：包含后缀
            "position": "left_0",
            "type": "pad"
        }
    ]
}
```

### 180nm 配置
```json
{
    "instances": [
        {
            "name": "VIOLA",
            "device": "PVDD1CDG",  // ✅ 正确：不包含后缀
            "position": "top_0",
            "type": "pad"
        }
    ]
}
```

## ❌ 错误示例

### 180nm 错误用法
```json
{
    "instances": [
        {
            "name": "VIOLA",
            "device": "PVDD1CDG_H_G",  // ❌ 错误：180nm不需要后缀！
            "position": "top_0",
            "type": "pad"
        }
    ]
}
```

---

**记住**：28nm需要后缀，180nm不需要后缀！ 🎯

