# `create_layout_generator` 的实际操作 vs 直接使用

## 一、`create_layout_generator` 实际做了什么？

### 工厂函数的实现（简化版）

```python
def create_layout_generator(process_node: str = "28nm"):
    """创建布局生成器"""
    # 1. 判断工艺节点
    if process_node == "180nm":
        # 2. 创建并返回 180nm 生成器
        return LayoutGeneratorT180()
    else:
        # 3. 创建并返回 28nm 生成器（默认）
        return LayoutGeneratorT28()
```

### 实际执行的操作步骤

当调用 `create_layout_generator(process_node="28nm")` 时：

1. **接收参数**：`process_node = "28nm"`
2. **判断条件**：检查 `process_node == "180nm"` → False
3. **执行创建**：调用 `LayoutGeneratorT28()`
4. **返回对象**：返回创建好的生成器实例

### 创建生成器时实际发生了什么？

当执行 `LayoutGeneratorT28()` 时，会调用 `__init__` 方法：

```python
class LayoutGeneratorT28:
    def __init__(self):
        # 1. 获取 28nm 工艺节点配置
        node_config = get_process_node_config("28nm")
        
        # 2. 设置默认配置
        self.config = {
            "library_name": node_config["library_name"],  # 例如: "tphn28hpcpgv18"
            "view_name": "layout",
            "pad_width": node_config["pad_width"],        # 例如: 80
            "pad_height": node_config["pad_height"],      # 例如: 80
            "corner_size": node_config["corner_size"],    # 例如: 80
            "pad_spacing": node_config["pad_spacing"],    # 例如: 0
            "placement_order": "counterclockwise",
            "filler_components": node_config["filler_components"],
            "process_node": "28nm"
        }
        
        # 3. 初始化所有子模块
        self.position_calculator = PositionCalculator(self.config)
        self.voltage_domain_handler = VoltageDomainHandler()
        self.filler_generator = FillerGenerator()
        self.layout_validator = LayoutValidator()
        self.inner_pad_handler = InnerPadHandler(self.config)
        self.skill_generator = SkillGeneratorT28(self.config)
        self.auto_filler_generator = AutoFillerGeneratorT28(self.config)
```

**总结**：`create_layout_generator` 实际上就是：
1. 根据 `process_node` 参数判断
2. 调用对应的类构造函数 `LayoutGeneratorT28()` 或 `LayoutGeneratorT180()`
3. 返回创建好的对象

## 二、直接使用布局生成器

### 方式1：直接实例化（不使用工厂）

```python
# 需要手动判断工艺节点
if process_node == "28nm":
    generator = LayoutGeneratorT28()
elif process_node == "180nm":
    generator = LayoutGeneratorT180()
else:
    raise ValueError(f"Unsupported process node: {process_node}")

# 使用生成器
generator.set_config(ring_config)
components = generator.convert_relative_to_absolute(instances, ring_config)
```

### 方式2：使用工厂函数

```python
# 一行代码搞定，工厂自动判断
generator = create_layout_generator(process_node)

# 使用生成器（完全相同）
generator.set_config(ring_config)
components = generator.convert_relative_to_absolute(instances, ring_config)
```

## 三、两者的区别对比

### 功能上的区别

| 方面 | 直接使用 | 使用工厂 |
|------|---------|---------|
| **创建对象** | ✅ 完全相同 | ✅ 完全相同 |
| **初始化过程** | ✅ 完全相同 | ✅ 完全相同 |
| **返回的对象** | ✅ 完全相同 | ✅ 完全相同 |
| **对象的方法** | ✅ 完全相同 | ✅ 完全相同 |

**结论**：在功能上，两者创建的生成器对象**完全一样**！

### 代码上的区别

| 方面 | 直接使用 | 使用工厂 |
|------|---------|---------|
| **代码行数** | 需要 if-elif 判断（3-5行） | 一行代码 |
| **判断逻辑位置** | 分散在各个调用处 | 集中在工厂函数中 |
| **维护性** | 修改时需要改多处 | 只需改工厂函数 |
| **可读性** | 需要理解判断逻辑 | 语义清晰 |

### 实际代码对比

#### 场景1：在工具函数中使用

**直接使用（需要判断）**：
```python
def generate_io_ring_layout(config_file, output_file, process_node="28nm"):
    # ... 其他代码 ...
    
    # 需要在这里判断
    if process_node == "28nm":
        generator = LayoutGeneratorT28()
    elif process_node == "180nm":
        generator = LayoutGeneratorT180()
    else:
        raise ValueError(f"Unsupported process node: {process_node}")
    
    generator.set_config(ring_config)
    # ... 使用生成器 ...
```

**使用工厂（简洁）**：
```python
def generate_io_ring_layout(config_file, output_file, process_node="28nm"):
    # ... 其他代码 ...
    
    # 一行搞定
    generator = create_layout_generator(process_node)
    
    generator.set_config(ring_config)
    # ... 使用生成器 ...
```

#### 场景2：在多个地方使用

**直接使用（重复代码）**：
```python
# 位置1：验证函数
def validate_config(json_file, process_node):
    if process_node == "28nm":
        generator = LayoutGeneratorT28()
    elif process_node == "180nm":
        generator = LayoutGeneratorT180()
    # ... 验证逻辑 ...

# 位置2：转换函数
def convert_positions(instances, process_node):
    if process_node == "28nm":
        generator = LayoutGeneratorT28()
    elif process_node == "180nm":
        generator = LayoutGeneratorT180()
    # ... 转换逻辑 ...

# 位置3：生成函数
def generate_layout(config, process_node):
    if process_node == "28nm":
        generator = LayoutGeneratorT28()
    elif process_node == "180nm":
        generator = LayoutGeneratorT180()
    # ... 生成逻辑 ...
```

**使用工厂（统一接口）**：
```python
# 位置1：验证函数
def validate_config(json_file, process_node):
    generator = create_layout_generator(process_node)
    # ... 验证逻辑 ...

# 位置2：转换函数
def convert_positions(instances, process_node):
    generator = create_layout_generator(process_node)
    # ... 转换逻辑 ...

# 位置3：生成函数
def generate_layout(config, process_node):
    generator = create_layout_generator(process_node)
    # ... 生成逻辑 ...
```

## 四、实际执行流程对比

### 直接使用流程

```
调用代码
  ↓
判断 process_node
  ↓
if "28nm" → LayoutGeneratorT28() → 创建对象 → 返回
if "180nm" → LayoutGeneratorT180() → 创建对象 → 返回
  ↓
使用生成器对象
```

### 使用工厂流程

```
调用代码
  ↓
调用 create_layout_generator(process_node)
  ↓
工厂函数内部判断 process_node
  ↓
if "28nm" → LayoutGeneratorT28() → 创建对象 → 返回
if "180nm" → LayoutGeneratorT180() → 创建对象 → 返回
  ↓
返回生成器对象
  ↓
使用生成器对象
```

**注意**：最终都是调用 `LayoutGeneratorT28()` 或 `LayoutGeneratorT180()`，执行的操作**完全相同**！

## 五、总结

### `create_layout_generator` 实际做了什么？

1. **接收参数**：`process_node`
2. **判断条件**：根据 `process_node` 选择对应的类
3. **创建对象**：调用 `LayoutGeneratorT28()` 或 `LayoutGeneratorT180()`
4. **返回对象**：返回创建好的生成器实例

### 和直接使用的区别

| 特性 | 直接使用 | 使用工厂 |
|------|---------|---------|
| **创建的对象** | 完全相同 | 完全相同 |
| **初始化过程** | 完全相同 | 完全相同 |
| **代码简洁性** | 需要判断逻辑 | 一行代码 |
| **代码维护性** | 分散在多处 | 集中管理 |
| **扩展性** | 需要改多处 | 只需改工厂 |

### 核心区别

**功能上**：没有区别，创建的对象完全相同。

**代码上**：
- 直接使用：需要自己写判断逻辑，代码分散
- 使用工厂：判断逻辑封装在工厂中，调用简洁

**本质上**：工厂模式是一个**代码组织方式**，让代码更简洁、更易维护，但**不改变实际的功能**。

