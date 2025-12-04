# 工艺节点解耦计划

## 🎯 目标

将不同工艺节点的代码解耦，避免在一个类中通过 `if process_node == "180nm"` 来判断，每个工艺节点有自己独立的实现。

## 📋 设计方案

### 1. 基类（Base Class）
- `SchematicGeneratorBase` - 包含所有工艺节点通用的方法
  - `get_outer_pad_positions()`
  - `rotate_point()`
  - `get_pin_side_from_center()`
  - `generate_pin_commands()`
  - `sanitize_skill_instance_name()`
  - `format_skill_net_label()`
  - `generate_schematic()` - 通用实现

### 2. 工艺节点特定类
- `SchematicGenerator28nm` - 28nm特定实现
  - `normalize_device_config()` - 28nm设备配置标准化
  - `get_device_offset()` - 28nm设备偏移
  - `calculate_position_from_description()` - 28nm位置计算
  
- `SchematicGenerator180nm` - 180nm特定实现
  - `normalize_device_config()` - 180nm设备配置标准化
  - `get_device_offset()` - 180nm设备偏移
  - `calculate_position_from_description()` - 180nm位置计算

### 3. 工厂模式
- `create_schematic_generator()` - 根据工艺节点创建对应的生成器

## ✅ 已完成

1. ✅ 创建 `SchematicGeneratorBase` 基类
2. ✅ 创建 `SchematicGenerator28nm` 类
3. ✅ 创建 `SchematicGenerator180nm` 类
4. ✅ 创建 `schematic_generator_factory.py` 工厂

## 🔄 待完成

1. ⏳ 将 `generate_schematic()` 方法移到基类（需要处理工艺节点特定的差异）
2. ⏳ 迁移 `calculate_position_from_description()` 到各自类中
3. ⏳ 更新所有调用点使用工厂模式
4. ⏳ 移除原 `SchematicGenerator` 类中的工艺节点判断逻辑

## 📝 注意事项

- `generate_schematic()` 方法中有一些工艺节点特定的逻辑需要处理：
  - `pin_connection` vs `pin_config`（已统一为 `pin_connection`）
  - `direction` vs `io_type`（需要根据工艺节点选择）
  
- 位置计算逻辑可能不同，需要分别实现

