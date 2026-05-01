---
name: python-configuration
description: 通过环境变量和类型化设置进行 Python 配置管理。在外部化配置、设置 pydantic-settings、管理密钥或实现环境特定行为时使用。
---

# Python 配置管理

使用环境变量和类型化设置从代码中外部化配置。良好管理的配置使相同的代码无需修改即可在任何环境中运行。

## 何时使用此技能

- 设置新项目的配置系统
- 从硬编码值迁移到环境变量
- 实现 pydantic-settings 进行类型化配置
- 管理密钥和敏感值
- 创建环境特定设置（dev/staging/prod）
- 在应用程序启动时验证配置

## 核心概念

### 1. 外部化配置

所有环境特定的值（URL、密钥、功能标志）来自环境变量，而不是代码。

### 2. 类型化设置

在启动时将配置解析和验证为类型化对象，而不是分散在代码中。

### 3. 快速失败

在应用程序启动时验证所有必需的配置。缺失的配置应立即崩溃并显示清晰的消息。

### 4. 合理的默认值

为本地开发提供合理的默认值，同时要求敏感设置使用显式值。

## 快速开始

```python
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    api_key: str = Field(alias="API_KEY")
    debug: bool = Field(default=False, alias="DEBUG")

settings = Settings()  # Loads from environment
```

## 基础模式

### 模式 1：使用 Pydantic 的类型化设置

创建一个中央设置类来加载和验证所有配置。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, ValidationError
import sys

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")
    db_name: str = Field(alias="DB_NAME")
    db_user: str = Field(alias="DB_USER")
    db_password: str = Field(alias="DB_PASSWORD")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    # API Keys
    api_secret_key: str = Field(alias="API_SECRET_KEY")

    # Feature flags
    enable_new_feature: bool = Field(default=False, alias="ENABLE_NEW_FEATURE")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

# Create singleton instance at module load
try:
    settings = Settings()
except ValidationError as e:
    print(f"Configuration error:\n{e}")
    sys.exit(1)
```

在应用程序中导入 `settings`：

```python
from myapp.config import settings

def get_database_connection():
    return connect(
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
```

### 模式 2：缺失配置时快速失败

必需的设置应立即崩溃应用程序并显示清晰的错误。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError
import sys

class Settings(BaseSettings):
    # Required - no default means it must be set
    api_key: str = Field(alias="API_KEY")
    database_url: str = Field(alias="DATABASE_URL")

    # Optional with defaults
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

try:
    settings = Settings()
except ValidationError as e:
    print("=" * 60)
    print("CONFIGURATION ERROR")
    print("=" * 60)
    for error in e.errors():
        field = error["loc"][0]
        print(f"  - {field}: {error['msg']}")
    print("\nPlease set the required environment variables.")
    sys.exit(1)
```

启动时的清晰错误比请求中途出现的神秘 `None` 失败要好。

### 模式 3：本地开发默认值

为本地开发提供合理的默认值，同时要求密钥使用显式值。

```python
class Settings(BaseSettings):
    # Has local default, but prod will override
    db_host: str = Field(default="localhost", alias="DB_HOST")
    db_port: int = Field(default=5432, alias="DB_PORT")

    # Always required - no default for secrets
    db_password: str = Field(alias="DB_PASSWORD")
    api_secret_key: str = Field(alias="API_SECRET_KEY")

    # Development convenience
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = {"env_file": ".env"}
```

为本地开发创建 `.env` 文件（永远不要提交此文件）：

```bash
# .env (add to .gitignore)
DB_PASSWORD=local_dev_password
API_SECRET_KEY=dev-secret-key
DEBUG=true
```

### 模式 4：命名空间环境变量

为相关变量添加前缀以提高清晰度和便于调试。

```bash
# Database configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
DB_USER=admin
DB_PASSWORD=secret

# Redis configuration
REDIS_URL=redis://localhost:6379
REDIS_MAX_CONNECTIONS=10

# Authentication
AUTH_SECRET_KEY=your-secret-key
AUTH_TOKEN_EXPIRY_SECONDS=3600
AUTH_ALGORITHM=HS256

# Feature flags
FEATURE_NEW_CHECKOUT=true
FEATURE_BETA_UI=false
```

使 `env | grep DB_` 在调试时有用。

## 高级模式

### 模式 5：类型强制转换

Pydantic 自动处理常见转换。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

class Settings(BaseSettings):
    # Automatically converts "true", "1", "yes" to True
    debug: bool = False

    # Automatically converts string to int
    max_connections: int = 100

    # Parse comma-separated string to list
    allowed_hosts: list[str] = Field(default_factory=list)

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
```

用法：

```bash
ALLOWED_HOSTS=example.com,api.example.com,localhost
MAX_CONNECTIONS=50
DEBUG=true
```

### 模式 6：环境特定配置

使用环境枚举切换行为。

```python
from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import Field, computed_field

class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    environment: Environment = Field(
        default=Environment.LOCAL,
        alias="ENVIRONMENT",
    )

    # Settings that vary by environment
    log_level: str = Field(default="DEBUG", alias="LOG_LEVEL")

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @computed_field
    @property
    def is_local(self) -> bool:
        return self.environment == Environment.LOCAL

# Usage
if settings.is_production:
    configure_production_logging()
else:
    configure_debug_logging()
```

### 模式 7：嵌套配置组

将相关设置组织成嵌套模型。

```python
from pydantic import BaseModel
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseModel):
    host: str = "localhost"
    port: int = 5432
    name: str
    user: str
    password: str

class RedisSettings(BaseModel):
    url: str = "redis://localhost:6379"
    max_connections: int = 10

class Settings(BaseSettings):
    database: DatabaseSettings
    redis: RedisSettings
    debug: bool = False

    model_config = {
        "env_nested_delimiter": "__",
        "env_file": ".env",
    }
```

环境变量使用双下划线进行嵌套：

```bash
DATABASE__HOST=db.example.com
DATABASE__PORT=5432
DATABASE__NAME=myapp
DATABASE__USER=admin
DATABASE__PASSWORD=secret
REDIS__URL=redis://redis.example.com:6379
```

### 模式 8：从文件读取密钥

对于容器环境，从挂载的文件读取密钥。

```python
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    # Read from environment variable or file
    db_password: str = Field(alias="DB_PASSWORD")

    model_config = {
        "secrets_dir": "/run/secrets",  # Docker secrets location
    }
```

如果环境变量未设置，Pydantic 将查找 `/run/secrets/db_password`。

### 模式 9：配置验证

为复杂需求添加自定义验证。

```python
from pydantic_settings import BaseSettings
from pydantic import Field, model_validator

class Settings(BaseSettings):
    db_host: str = Field(alias="DB_HOST")
    db_port: int = Field(alias="DB_PORT")
    read_replica_host: str | None = Field(default=None, alias="READ_REPLICA_HOST")
    read_replica_port: int = Field(default=5432, alias="READ_REPLICA_PORT")

    @model_validator(mode="after")
    def validate_replica_settings(self):
        if self.read_replica_host and self.read_replica_port == self.db_port:
            if self.read_replica_host == self.db_host:
                raise ValueError(
                    "Read replica cannot be the same as primary database"
                )
        return self
```

## 最佳实践总结

1. **永远不要硬编码配置** - 所有环境特定值来自环境变量
2. **使用类型化设置** - 带验证的 Pydantic-settings
3. **快速失败** - 启动时在缺失必需配置时崩溃
4. **提供开发默认值** - 使本地开发更容易
5. **永远不要提交密钥** - 使用 `.env` 文件（gitignored）或密钥管理器
6. **命名空间变量** - `DB_HOST`、`REDIS_URL` 以提高清晰度
7. **导入设置单例** - 不要在代码中到处调用 `os.getenv()`
8. **记录所有变量** - README 应列出必需的环境变量
9. **尽早验证** - 在启动时检查配置正确性
10. **使用 secrets_dir** - 支持容器中的挂载密钥
