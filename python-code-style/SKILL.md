---
name: python-code-style
description: Python 代码风格、代码检查、格式化、命名规范和文档标准。在编写新代码、审查风格、配置代码检查工具、编写文档字符串或制定项目标准时使用。
---

# Python 代码风格与文档

一致的代码风格和清晰的文档使代码库易于维护和协作。此技能涵盖现代 Python 工具、命名规范和文档标准。

## 何时使用此技能

- 为新项目设置代码检查和格式化
- 编写或审查文档字符串
- 制定团队编码标准
- 配置 ruff、mypy 或 pyright
- 审查代码风格一致性
- 创建项目文档

## 核心概念

### 1. 自动化格式化

让工具处理格式化争论。配置一次，自动执行。

### 2. 一致的命名

遵循 PEP 8 规范，使用有意义的描述性名称。

### 3. 文档即代码

文档字符串应与其描述的代码一起维护。

### 4. 类型注解

现代 Python 代码应为所有公共 API 包含类型提示。

## 快速开始

```bash
# Install modern tooling
pip install ruff mypy

# Configure in pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"  # Adjust based on your project's minimum Python version

[tool.mypy]
strict = true
```

## 基础模式

### 模式 1：现代 Python 工具

使用 `ruff` 作为一体化的代码检查和格式化工具。它用一个快速工具取代了 flake8、isort 和 black。

```toml
# pyproject.toml
[tool.ruff]
line-length = 120
target-version = "py312"  # Adjust based on your project's minimum Python version

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
    "SIM",  # flake8-simplify
]
ignore = ["E501"]  # Line length handled by formatter

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

运行命令：

```bash
ruff check --fix .  # Lint and auto-fix
ruff format .       # Format code
```

### 模式 2：类型检查配置

为生产代码配置严格的类型检查。

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

替代方案：使用 `pyright` 进行更快的检查。

```toml
[tool.pyright]
pythonVersion = "3.12"
typeCheckingMode = "strict"
```

### 模式 3：命名规范

遵循 PEP 8，强调清晰性优于简洁性。

**文件和模块：**

```python
# Good: Descriptive snake_case
user_repository.py
order_processing.py
http_client.py

# Avoid: Abbreviations
usr_repo.py
ord_proc.py
http_cli.py
```

**类和函数：**

```python
# Classes: PascalCase
class UserRepository:
    pass

class HTTPClientFactory:  # Acronyms stay uppercase
    pass

# Functions and variables: snake_case
def get_user_by_email(email: str) -> User | None:
    retry_count = 3
    max_connections = 100
```

**常量：**

```python
# Module-level constants: SCREAMING_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
```

### 模式 4：导入组织

按一致的顺序分组导入：标准库、第三方、本地。

```python
# Standard library
import os
from collections.abc import Callable
from typing import Any

# Third-party packages
import httpx
from pydantic import BaseModel
from sqlalchemy import Column

# Local imports
from myproject.models import User
from myproject.services import UserService
```

仅使用绝对导入：

```python
# Preferred
from myproject.utils import retry_decorator

# Avoid relative imports
from ..utils import retry_decorator
```

## 高级模式

### 模式 5：Google 风格文档字符串

为所有公共类、方法和函数编写文档字符串。

**简单函数：**

```python
def get_user(user_id: str) -> User:
    """Retrieve a user by their unique identifier."""
    ...
```

**复杂函数：**

```python
def process_batch(
    items: list[Item],
    max_workers: int = 4,
    on_progress: Callable[[int, int], None] | None = None,
) -> BatchResult:
    """Process items concurrently using a worker pool.

    Processes each item in the batch using the configured number of
    workers. Progress can be monitored via the optional callback.

    Args:
        items: The items to process. Must not be empty.
        max_workers: Maximum concurrent workers. Defaults to 4.
        on_progress: Optional callback receiving (completed, total) counts.

    Returns:
        BatchResult containing succeeded items and any failures with
        their associated exceptions.

    Raises:
        ValueError: If items is empty.
        ProcessingError: If the batch cannot be processed.

    Example:
        >>> result = process_batch(items, max_workers=8)
        >>> print(f"Processed {len(result.succeeded)} items")
    """
    ...
```

**类文档字符串：**

```python
class UserService:
    """Service for managing user operations.

    Provides methods for creating, retrieving, updating, and
    deleting users with proper validation and error handling.

    Attributes:
        repository: The data access layer for user persistence.
        logger: Logger instance for operation tracking.

    Example:
        >>> service = UserService(repository, logger)
        >>> user = service.create_user(CreateUserInput(...))
    """

    def __init__(self, repository: UserRepository, logger: Logger) -> None:
        """Initialize the user service.

        Args:
            repository: Data access layer for users.
            logger: Logger for tracking operations.
        """
        self.repository = repository
        self.logger = logger
```

### 模式 6：行长度和格式化

将行长度设置为 120 个字符以适应现代显示器，同时保持可读性。

```python
# Good: Readable line breaks
def create_user(
    email: str,
    name: str,
    role: UserRole = UserRole.MEMBER,
    notify: bool = True,
) -> User:
    ...

# Good: Chain method calls clearly
result = (
    db.query(User)
    .filter(User.active == True)
    .order_by(User.created_at.desc())
    .limit(10)
    .all()
)

# Good: Format long strings
error_message = (
    f"Failed to process user {user_id}: "
    f"received status {response.status_code} "
    f"with body {response.text[:100]}"
)
```

### 模式 7：项目文档

**README 结构：**

```markdown
# Project Name

Brief description of what the project does.

## Installation

\`\`\`bash
pip install myproject
\`\`\`

## Quick Start

\`\`\`python
from myproject import Client

client = Client(api_key="...")
result = client.process(data)
\`\`\`

## Configuration

Document environment variables and configuration options.

## Development

\`\`\`bash
pip install -e ".[dev]"
pytest
\`\`\`
```

**CHANGELOG 格式（Keep a Changelog）：**

```markdown
# Changelog

## [Unreleased]

### Added
- New feature X

### Changed
- Modified behavior of Y

### Fixed
- Bug in Z
```

## 最佳实践总结

1. **使用 ruff** - 一体化的代码检查和格式化工具
2. **启用严格 mypy** - 在运行前捕获类型错误
3. **120 字符行长度** - 现代可读性标准
4. **描述性名称** - 清晰性优于简洁性
5. **绝对导入** - 比相对导入更易维护
6. **Google 风格文档字符串** - 一致、可读的文档
7. **记录公共 API** - 每个公共函数都需要文档字符串
8. **保持文档更新** - 将文档视为代码
9. **在 CI 中自动化** - 每次提交都运行代码检查工具
10. **目标 Python 3.10+** - 对于新项目，建议使用 Python 3.12+ 以获得现代语言特性
