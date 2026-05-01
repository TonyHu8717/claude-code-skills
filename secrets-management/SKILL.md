---
name: secrets-management
description: 使用 Vault、AWS Secrets Manager 或原生平台解决方案为 CI/CD 管道实施安全的密钥管理。在处理敏感凭据、轮换密钥或保护 CI/CD 环境时使用。
---

# 密钥管理

使用 Vault、AWS Secrets Manager 和其他工具为 CI/CD 管道实施安全的密钥管理实践。

## 目的

在 CI/CD 管道中实施安全的密钥管理，避免硬编码敏感信息。

## 何时使用

- 存储 API 密钥和凭据
- 管理数据库密码
- 处理 TLS 证书
- 自动轮换密钥
- 实施最小权限访问

## 密钥管理工具

### HashiCorp Vault

- 集中化密钥管理
- 动态密钥生成
- 密钥轮换
- 审计日志
- 细粒度访问控制

### AWS Secrets Manager

- AWS 原生解决方案
- 自动轮换
- 与 RDS 集成
- CloudFormation 支持

### Azure Key Vault

- Azure 原生解决方案
- HSM 支持的密钥
- 证书管理
- RBAC 集成

### Google Secret Manager

- GCP 原生解决方案
- 版本控制
- IAM 集成

## HashiCorp Vault 集成

### 设置 Vault

```bash
# 启动 Vault 开发服务器
vault server -dev

# 设置环境
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='root'

# 启用密钥引擎
vault secrets enable -path=secret kv-v2

# 存储密钥
vault kv put secret/database/config username=admin password=secret
```

### GitHub Actions 与 Vault

```yaml
name: Deploy with Vault Secrets

on: [push]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Import Secrets from Vault
        uses: hashicorp/vault-action@v2
        with:
          url: https://vault.example.com:8200
          token: ${{ secrets.VAULT_TOKEN }}
          secrets: |
            secret/data/database username | DB_USERNAME ;
            secret/data/database password | DB_PASSWORD ;
            secret/data/api key | API_KEY

      - name: Use secrets
        run: |
          echo "Connecting to database as $DB_USERNAME"
          # Use $DB_PASSWORD, $API_KEY
```

### GitLab CI 与 Vault

```yaml
deploy:
  image: vault:1.17
  before_script:
    - export VAULT_ADDR=https://vault.example.com:8200
    - export VAULT_TOKEN=$VAULT_TOKEN
    - apk add curl jq
  script:
    - |
      DB_PASSWORD=$(vault kv get -field=password secret/database/config)
      API_KEY=$(vault kv get -field=key secret/api/credentials)
      echo "Deploying with secrets..."
      # Use $DB_PASSWORD, $API_KEY
```

**参考：** 参见 `references/vault-setup.md`

## AWS Secrets Manager

### 存储密钥

```bash
aws secretsmanager create-secret \
  --name production/database/password \
  --secret-string "super-secret-password"
```

### 在 GitHub Actions 中检索

```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    aws-region: us-west-2

- name: Get secret from AWS
  run: |
    SECRET=$(aws secretsmanager get-secret-value \
      --secret-id production/database/password \
      --query SecretString \
      --output text)
    echo "::add-mask::$SECRET"
    echo "DB_PASSWORD=$SECRET" >> $GITHUB_ENV

- name: Use secret
  run: |
    # Use $DB_PASSWORD
    ./deploy.sh
```

### Terraform 与 AWS Secrets Manager

```hcl
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "production/database/password"
}

resource "aws_db_instance" "main" {
  allocated_storage    = 100
  engine              = "postgres"
  instance_class      = "db.t3.large"
  username            = "admin"
  password            = jsondecode(data.aws_secretsmanager_secret_version.db_password.secret_string)["password"]
}
```

## GitHub Secrets

### 组织/仓库级密钥

```yaml
- name: Use GitHub secret
  env:
    API_KEY: ${{ secrets.API_KEY }}
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
  run: |
    # 密钥作为环境变量注入 — 永远不要打印到日志
    ./deploy.sh
```

### 环境级密钥

```yaml
deploy:
  runs-on: ubuntu-latest
  environment: production
  steps:
    - name: Deploy
      env:
        PROD_API_KEY: ${{ secrets.PROD_API_KEY }}
      run: |
        # 密钥作为环境变量注入 — 永远不要打印到日志
        ./deploy.sh
```

**参考：** 参见 `references/github-secrets.md`

## GitLab CI/CD 变量

### 项目级变量

```yaml
deploy:
  script:
    - echo "Deploying with $API_KEY"
    - echo "Database: $DATABASE_URL"
```

### 受保护和遮蔽变量

- 受保护：仅在受保护分支中可用
- 遮蔽：在作业日志中隐藏
- 文件类型：作为文件存储

## 最佳实践

1. **永远不要提交密钥** 到 Git
2. **每个环境使用不同的密钥**
3. **定期轮换密钥**
4. **实施最小权限访问**
5. **启用审计日志**
6. **使用密钥扫描**（GitGuardian、TruffleHog）
7. **在日志中遮蔽密钥**
8. **静态加密密钥**
9. **尽可能使用短期令牌**
10. **记录密钥要求**

## 密钥轮换

### 使用 AWS 自动轮换

```python
import boto3
import json

def lambda_handler(event, context):
    client = boto3.client('secretsmanager')

    # 获取当前密钥
    response = client.get_secret_value(SecretId='my-secret')
    current_secret = json.loads(response['SecretString'])

    # 生成新密码
    new_password = generate_strong_password()

    # 更新数据库密码
    update_database_password(new_password)

    # 更新密钥
    client.put_secret_value(
        SecretId='my-secret',
        SecretString=json.dumps({
            'username': current_secret['username'],
            'password': new_password
        })
    )

    return {'statusCode': 200}
```

### 手动轮换流程

1. 生成新密钥
2. 在密钥存储中更新密钥
3. 更新应用以使用新密钥
4. 验证功能
5. 撤销旧密钥

## External Secrets Operator

### Kubernetes 集成

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: production
spec:
  provider:
    vault:
      server: "https://vault.example.com:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "production"

---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: database-credentials
    creationPolicy: Owner
  data:
    - secretKey: username
      remoteRef:
        key: database/config
        property: username
    - secretKey: password
      remoteRef:
        key: database/config
        property: password
```

## 密钥扫描

### 预提交钩子

```bash
#!/bin/bash
# .git/hooks/pre-commit

# 使用 TruffleHog 检查密钥
docker run --rm -v "$(pwd):/repo" \
  trufflesecurity/trufflehog:3.88 \
  filesystem --directory=/repo

if [ $? -ne 0 ]; then
  echo "❌ Secret detected! Commit blocked."
  exit 1
fi
```

### CI/CD 密钥扫描

```yaml
secret-scan:
  stage: security
  image: trufflesecurity/trufflehog:3.88
  script:
    - trufflehog filesystem .
  allow_failure: false
```


## 相关技能

- `github-actions-templates` - GitHub Actions 集成
- `gitlab-ci-patterns` - GitLab CI 集成
- `deployment-pipeline-design` - 管道架构
