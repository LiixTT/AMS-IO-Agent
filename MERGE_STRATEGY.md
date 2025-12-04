# 合并策略：支持28nm和180nm双工艺节点

## 💡 核心思路

**完美互补**：
- **当前项目**：硬编码28nm ✅
- **目标项目**：硬编码180nm ✅
- **合并后**：支持两种工艺节点，可动态切换 🎯

## 📋 合并方案

### 方案：创建工艺节点配置层

创建一个统一的工艺节点配置系统，支持28nm和180nm动态切换。

### 1. 创建工艺节点配置模块

**文件**：`src/app/layout/process_node_config.py`

```python
"""
Process Node Configuration - Support multiple process nodes
"""

PROCESS_NODE_CONFIGS = {
    "28nm": {
        "library_name": "tphn28hpcpgv18",
        "pad_width": 20,
        "pad_height": 110,
        "corner_size": 110,
        "pad_spacing": 60,
        "device_offset_rules": {
            "PDB3AC": 1.5 * 0.125,  # Analog signal
            "PDDW16SDGZ": -5.5 * 0.125,  # Digital IO
            "PVDD1DGZ": -8 * 0.125,  # Digital power/ground
            "PVSS1DGZ": -8 * 0.125,
            "PVDD2POC": -8 * 0.125,
            "PVSS2DGZ": -8 * 0.125,
            "default": 1.5 * 0.125
        },
        "template_file": "device_templates.json",  # or IO_device_info_T28.json
        "filler_components": {
            "analog_10": "PFILLER10A_G",
            "analog_20": "PFILLER20A_G",
            "digital_10": "PFILLER10_G",
            "digital_20": "PFILLER20_G",
            "separator": "PRCUTA_G"
        }
    },
    "180nm": {
        "library_name": "tpd018bcdnv5",
        "pad_width": 80,
        "pad_height": 120,
        "corner_size": 130,
        "pad_spacing": 90,
        "device_offset_rules": {
            "PVSS2": 1.5 * 0.125,  # power/ground
            "PVDD2": 1.5 * 0.125,
            "PDDW04": -5.5 * 0.125,  # Digital IO
            "PVDD1": -8 * 0.125,  # Analog I/O
            "PVSS1": -8 * 0.125,
            "default": 1.5 * 0.125
        },
        "template_file": "device_templates_180.json",
        "filler_components": {
            "analog_10": "PFILLER10",
            "analog_20": "PFILLER20",
            "digital_10": "PFILLER10",
            "digital_20": "PFILLER20",
            "separator": "PFILLER10"
        }
    }
}

def get_process_node_config(process_node: str = "28nm"):
    """Get configuration for specified process node"""
    if process_node not in PROCESS_NODE_CONFIGS:
        raise ValueError(f"Unsupported process node: {process_node}. Supported: {list(PROCESS_NODE_CONFIGS.keys())}")
    return PROCESS_NODE_CONFIGS[process_node].copy()

def get_device_offset(process_node: str, device_type: str) -> float:
    """Get device offset based on process node and device type"""
    config = get_process_node_config(process_node)
    rules = config["device_offset_rules"]
    
    # Check for exact match first
    if device_type in rules:
        return rules[device_type]
    
    # Check for prefix match
    for prefix, offset in rules.items():
        if prefix != "default" and device_type.startswith(prefix):
            return offset
    
    # Return default
    return rules.get("default", 1.5 * 0.125)
```

### 2. 修改Layout生成器支持工艺节点

**修改**：`src/app/layout/layout_generator.py`

```python
from .process_node_config import get_process_node_config, get_device_offset

class LayoutGenerator:
    def __init__(self, process_node: str = "28nm"):
        # Get process node configuration
        node_config = get_process_node_config(process_node)
        
        # Default configuration with process node settings
        self.config = {
            "library_name": node_config["library_name"],
            "view_name": "layout",
            "pad_width": node_config["pad_width"],
            "pad_height": node_config["pad_height"],
            "corner_size": node_config["corner_size"],
            "pad_spacing": node_config["pad_spacing"],
            "placement_order": "counterclockwise",
            "filler_components": node_config["filler_components"],
            "process_node": process_node  # Store for reference
        }
        # ... rest of initialization
```

### 3. 修改Schematic生成器支持工艺节点

**修改**：`src/app/schematic/schematic_generator.py`

```python
from src.app.layout.process_node_config import get_device_offset

class SchematicGenerator:
    def __init__(self, template_manager, process_node: str = "28nm"):
        self.template_manager = template_manager
        self.process_node = process_node
    
    def get_device_offset(self, device_type: str) -> float:
        """Get offset based on device type and process node"""
        return get_device_offset(self.process_node, device_type)
```

### 4. 修改IO Ring工具支持工艺节点参数

**修改**：`src/tools/io_ring_generator_tool.py`

```python
@tool
def generate_io_ring_schematic(
    config_file_path: str, 
    output_file_path: Optional[str] = None,
    process_node: str = "28nm"  # Add process node parameter
) -> str:
    """
    Generate IO ring schematic SKILL code from intent graph file
    
    Args:
        config_file_path: Path to intent graph file
        output_file_path: Complete path for output file (optional)
        process_node: Process node to use ("28nm" or "180nm", default: "28nm")
    """
    # Get process node configuration
    from src.app.layout.process_node_config import get_process_node_config
    node_config = get_process_node_config(process_node)
    
    # Use appropriate template file based on process node
    template_file = None
    if process_node == "28nm":
        possible_paths = [
            Path("src/schematic") / "device_templates.json",
            Path("src/scripts/devices") / "IO_device_info_T28.json",
            # ... other paths
        ]
    else:  # 180nm
        possible_paths = [
            Path("src/schematic") / "device_templates_180.json",
            # ... other paths
        ]
    
    # ... rest of the function
```

### 5. 合并180nm的生成器代码

**选项A：创建180nm专用生成器（简单）**
- 复制 `merge_source/src/schematic/schematic_generator180.py` → `src/app/schematic/schematic_generator_180nm.py`
- 更新导入路径
- 在工具中根据process_node选择使用哪个生成器

**选项B：统一生成器（推荐）**
- 修改现有的 `schematic_generator.py` 支持工艺节点参数
- 将180nm的逻辑合并进去
- 使用统一的接口

### 6. 合并工具装饰器

**复制**：`merge_source/src/tools/tool_utils.py` → `src/tools/tool_utils.py`

**应用**：在IO ring工具中使用 `dual_stream_tool` 装饰器

## 📝 实施步骤

### 步骤1：创建工艺节点配置模块

```bash
# 创建配置文件
touch src/app/layout/process_node_config.py
# 添加配置代码（见上面）
```

### 步骤2：合并180nm相关文件

```bash
# 1. 复制180nm schematic生成器（如果需要独立版本）
cp merge_source/src/schematic/schematic_generator180.py \
   src/app/schematic/schematic_generator_180nm.py

# 2. 复制180nm JSON验证器（如果需要）
cp merge_source/src/schematic/json_validator180.py \
   src/app/intent_graph/json_validator_180nm.py

# 3. 复制180nm设备模板（如果还没有）
cp merge_source/src/schematic/device_templates_180.json \
   src/app/schematic/device_templates_180.json
```

### 步骤3：修改现有代码支持工艺节点

1. **Layout生成器**：添加process_node参数
2. **Schematic生成器**：添加process_node参数
3. **IO Ring工具**：添加process_node参数，根据参数选择模板和生成器

### 步骤4：合并工具装饰器

```bash
# 复制工具装饰器
cp merge_source/src/tools/tool_utils.py src/tools/tool_utils.py

# 在io_ring_generator_tool.py中使用
# from src.tools.tool_utils import dual_stream_tool
```

### 步骤5：更新工具配置

在 `config/tools_config.yaml` 中，工具会自动支持process_node参数。

## 🎯 使用方式

### 方式1：通过工具参数指定

```python
# 生成28nm IO ring（默认）
generate_io_ring_schematic("config.json", process_node="28nm")

# 生成180nm IO ring
generate_io_ring_schematic("config.json", process_node="180nm")
```

### 方式2：通过配置文件指定

在JSON配置文件中添加：
```json
{
    "ring_config": {
        "process_node": "180nm",  // or "28nm"
        "chip_width": 2250,
        // ... other config
    }
}
```

### 方式3：通过环境变量

```bash
export PROCESS_NODE=180nm
python main.py
```

## ✅ 优势

1. **向后兼容**：默认28nm，不影响现有代码
2. **灵活切换**：运行时选择工艺节点
3. **代码复用**：共享核心逻辑，只区分工艺特定部分
4. **易于扩展**：未来可以轻松添加其他工艺节点

## 🔄 合并检查清单

- [ ] 创建 `process_node_config.py`
- [ ] 修改 `layout_generator.py` 支持工艺节点
- [ ] 修改 `schematic_generator.py` 支持工艺节点
- [ ] 修改 `io_ring_generator_tool.py` 支持工艺节点参数
- [ ] 复制180nm相关文件
- [ ] 合并工具装饰器
- [ ] 测试28nm功能（确保不破坏现有功能）
- [ ] 测试180nm功能
- [ ] 更新文档

---

**这个方案完美结合了两个项目的优势，实现双工艺节点支持！** 🎉

