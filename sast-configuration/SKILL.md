---
name: sast-configuration
description: 配置静态应用安全测试（SAST）工具以自动检测应用代码中的漏洞。在设置安全扫描、实施 DevSecOps 实践或自动化代码漏洞检测时使用。
---

# SAST 配置

静态应用安全测试（SAST）工具的设置、配置和自定义规则创建，用于跨多种编程语言的综合安全扫描。

## 概述

此技能提供设置和配置 SAST 工具的全面指导，包括 Semgrep、SonarQube 和 CodeQL。在以下情况下使用此技能：

- 在 CI/CD 管道中设置 SAST 扫描
- 为代码库创建自定义安全规则
- 配置质量门控和合规策略
- 优化扫描性能并减少误报
- 集成多个 SAST 工具实现纵深防御

## 核心能力

### 1. Semgrep 配置

- 使用模式匹配创建自定义规则
- 特定语言的安全规则（Python、JavaScript、Go、Java 等）
- CI/CD 集成（GitHub Actions、GitLab CI、Jenkins）
- 误报调优和规则优化
- 组织策略执行

### 2. SonarQube 设置

- 质量门控配置
- 安全热点分析
- 代码覆盖率和技术债务跟踪
- 针对语言的自定义质量配置文件
- 与 LDAP/SAML 的企业集成

### 3. CodeQL 分析

- GitHub 高级安全集成
- 自定义查询开发
- 漏洞变体分析
- 安全研究工作流
- SARIF 结果处理

## 快速开始

### 初始评估

1. 识别代码库中的主要编程语言
2. 确定合规要求（PCI-DSS、SOC 2 等）
3. 根据语言支持和集成需求选择 SAST 工具
4. 审查基线扫描以了解当前安全状况

### 基本设置

```bash
# Semgrep 快速开始
pip install semgrep
semgrep --config=auto --error

# 使用 Docker 运行 SonarQube
docker run -d --name sonarqube -p 9000:9000 sonarqube:10.8-community

# CodeQL CLI 设置
gh extension install github/gh-codeql
codeql database create mydb --language=python
```

## 参考文档

- [Semgrep 规则创建](references/semgrep-rules.md) — 基于模式的安全规则开发
- [SonarQube 配置](references/sonarqube-config.md) — 质量门控和配置文件
- [CodeQL 设置指南](references/codeql-setup.md) — 查询开发和工作流

## 模板和资产

- [semgrep-config.yml](assets/semgrep-config.yml) — 生产就绪的 Semgrep 配置
- [sonarqube-settings.xml](assets/sonarqube-settings.xml) — SonarQube 质量配置文件模板
- [run-sast.sh](scripts/run-sast.sh) — 自动化 SAST 执行脚本

## 集成模式

### CI/CD 管道集成

```yaml
# GitHub Actions 示例
- name: Run Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/security-audit
      p/owasp-top-ten
```

### 预提交钩子

```bash
# .pre-commit-config.yaml
- repo: https://github.com/returntocorp/semgrep
  rev: v1.45.0
  hooks:
    - id: semgrep
      args: ['--config=auto', '--error']
```

## 最佳实践

1. **从基线开始**
   - 运行初始扫描以建立安全基线
   - 优先处理严重和高危发现
   - 创建修复路线图

2. **渐进式采用**
   - 从安全聚焦的规则开始
   - 逐步添加代码质量规则
   - 仅对严重问题实施阻断

3. **误报管理**
   - 记录合法的抑制
   - 为已知安全模式创建允许列表
   - 定期审查被抑制的发现

4. **性能优化**
   - 排除测试文件和生成的代码
   - 对大型代码库使用增量扫描
   - 在 CI/CD 中缓存扫描结果

5. **团队赋能**
   - 为开发者提供安全培训
   - 为常见模式创建内部文档
   - 建立安全冠军计划

## 常见用例

### 新项目设置

```bash
./scripts/run-sast.sh --setup --language python --tools semgrep,sonarqube
```

### 自定义规则开发

```yaml
# 详细示例请参见 references/semgrep-rules.md
rules:
  - id: hardcoded-jwt-secret
    pattern: jwt.encode($DATA, "...", ...)
    message: JWT secret should not be hardcoded
    severity: ERROR
```

### 合规扫描

```bash
# PCI-DSS 聚焦扫描
semgrep --config p/pci-dss --json -o pci-scan-results.json
```

## 故障排除

### 高误报率

- 审查并调优规则灵敏度
- 添加路径过滤器以排除测试文件
- 对嘈杂模式使用 nostmt 元数据
- 创建组织特定的规则例外

### 性能问题

- 启用增量扫描
- 跨模块并行化扫描
- 优化规则模式以提高效率
- 缓存依赖和扫描结果

### 集成失败

- 验证 API 令牌和凭据
- 检查网络连接和代理设置
- 审查 SARIF 输出格式兼容性
- 验证 CI/CD 运行器权限

## 相关技能

- [OWASP Top 10 检查清单](../owasp-top10-checklist/SKILL.md)
- [容器安全](../container-security/SKILL.md)
- [依赖扫描](../dependency-scanning/SKILL.md)

## 工具比较

| 工具      | 最适用于                 | 语言支持     | 成本            | 集成       |
| --------- | ------------------------ | ------------ | --------------- | ---------- |
| Semgrep   | 自定义规则、快速扫描     | 30+ 种语言   | 免费/企业版     | 优秀       |
| SonarQube | 代码质量 + 安全          | 25+ 种语言   | 免费/商业版     | 良好       |
| CodeQL    | 深度分析、研究           | 10+ 种语言   | 免费（开源）    | GitHub 原生 |

## 后续步骤

1. 完成初始 SAST 工具设置
2. 运行基线安全扫描
3. 为组织特定模式创建自定义规则
4. 集成到 CI/CD 管道
5. 建立安全门控策略
6. 培训开发团队关于发现和修复
