# Layout 目录重构方案

## 当前结构问题

当前所有文件都在 `src/app/layout/` 根目录下，工艺相关文件混杂在一起：
- `layout_generator_T28.py`
- `layout_generator_T180.py`
- `skill_generator_T28.py`
- `skill_generator_T180.py`
- `auto_filler_T28.py`
- `auto_filler_T180.py`
- `layout_visualizer_T28.py`
- `layout_visualizer_T180.py`

**问题**：
- 文件太多，不够清晰
- 工艺相关文件分散，难以区分
- 添加新工艺节点时，文件会更多更乱

## 重构方案

### 新目录结构

```
src/app/layout/
├── __init__.py                    # 保持向后兼容的导入
├── README.md
├── config/                        # 配置文件（已存在）
│
├── T28/                           # 28nm 工艺相关文件
│   ├── __init__.py
│   ├── layout_generator.py       # 原 layout_generator_T28.py
│   ├── skill_generator.py         # 原 skill_generator_T28.py
│   ├── auto_filler.py             # 原 auto_filler_T28.py
│   └── layout_visualizer.py       # 原 layout_visualizer_T28.py
│
├── T180/                          # 180nm 工艺相关文件
│   ├── __init__.py
│   ├── layout_generator.py        # 原 layout_generator_T180.py
│   ├── skill_generator.py         # 原 skill_generator_T180.py
│   ├── auto_filler.py             # 原 auto_filler_T180.py
│   └── layout_visualizer.py        # 原 layout_visualizer_T180.py
│
└── [通用文件]                     # 保留在根目录
    ├── device_classifier.py
    ├── voltage_domain.py
    ├── position_calculator.py
    ├── filler_generator.py
    ├── layout_validator.py
    ├── inner_pad_handler.py
    ├── process_node_config.py
    └── layout_generator_factory.py (如果存在)
```

### 文件重命名规则

为了更清晰，去掉文件名中的工艺后缀：
- `layout_generator_T28.py` → `T28/layout_generator.py`
- `skill_generator_T28.py` → `T28/skill_generator.py`
- `auto_filler_T28.py` → `T28/auto_filler.py`
- `layout_visualizer_T28.py` → `T28/layout_visualizer.py`

同样适用于 T180。

### 向后兼容方案

在 `__init__.py` 中重新导出，保持旧的导入路径可用：

```python
# 向后兼容：保持旧的导入路径
from .T28.layout_generator import LayoutGeneratorT28
from .T28.skill_generator import SkillGeneratorT28
from .T28.auto_filler import AutoFillerGeneratorT28
from .T180.layout_generator import LayoutGeneratorT180
# ... 等等

# 新的推荐导入方式
from .T28 import LayoutGeneratorT28
from .T180 import LayoutGeneratorT180
```

## 优势

1. **结构清晰**：工艺相关文件按工艺节点分组
2. **易于扩展**：添加新工艺节点只需新建文件夹
3. **命名简洁**：文件名不再需要工艺后缀
4. **向后兼容**：保持旧的导入路径可用
5. **易于维护**：相关文件集中在一起

## 需要更新的文件

1. `src/app/layout/__init__.py` - 更新导入路径
2. `src/app/layout/layout_generator_T28.py` - 更新内部导入
3. `src/app/layout/layout_generator_T180.py` - 更新内部导入
4. `src/tools/io_ring_generator_tool.py` - 更新导入路径
5. 其他引用这些文件的地方

## 执行步骤

1. 创建 `T28/` 和 `T180/` 文件夹
2. 移动并重命名文件
3. 更新所有导入路径
4. 更新 `__init__.py` 保持向后兼容
5. 测试确保所有功能正常

