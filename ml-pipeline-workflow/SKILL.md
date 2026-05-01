---
name: ml-pipeline-workflow
description: 构建从数据准备到模型训练、验证和生产部署的端到端 MLOps 管道。当创建 ML 管道、实现 MLOps 实践或自动化模型训练和部署工作流时使用。
---

# ML 管道工作流

从数据准备到模型部署的完整端到端 MLOps 管道编排。

## 概述

本技能提供构建生产级 ML 管道的全面指导，涵盖完整生命周期：数据摄入 → 准备 → 训练 → 验证 → 部署 → 监控。

## 何时使用此技能

- 从零构建新的 ML 管道
- 为 ML 系统设计工作流编排
- 实现数据 → 模型 → 部署自动化
- 设置可复现的训练工作流
- 创建基于 DAG 的 ML 编排
- 将 ML 组件集成到生产系统

## 本技能提供的内容

### 核心能力

1. **管道架构**
   - 端到端工作流设计
   - DAG 编排模式（Airflow、Dagster、Kubeflow）
   - 组件依赖和数据流
   - 错误处理和重试策略

2. **数据准备**
   - 数据验证和质量检查
   - 特征工程管道
   - 数据版本控制和溯源
   - 训练/验证/测试集拆分策略

3. **模型训练**
   - 训练任务编排
   - 超参数管理
   - 实验跟踪集成
   - 分布式训练模式

4. **模型验证**
   - 验证框架和指标
   - A/B 测试基础设施
   - 性能回归检测
   - 模型比较工作流

5. **部署自动化**
   - 模型服务模式
   - 金丝雀部署
   - 蓝绿部署策略
   - 回滚机制

### 参考文档

详见 `references/` 目录中的指南：

- **data-preparation.md** — 数据清洗、验证和特征工程
- **model-training.md** — 训练工作流和最佳实践
- **model-validation.md** — 验证策略和指标
- **model-deployment.md** — 部署模式和服务架构

### 资源和模板

`assets/` 目录包含：

- **pipeline-dag.yaml.template** — 工作流编排的 DAG 模板
- **training-config.yaml** — 训练配置模板
- **validation-checklist.md** — 部署前验证清单

## 使用模式

### 基本管道设置

```python
# 1. 定义管道阶段
stages = [
    "data_ingestion",
    "data_validation",
    "feature_engineering",
    "model_training",
    "model_validation",
    "model_deployment"
]

# 2. 配置依赖
# 完整示例参见 assets/pipeline-dag.yaml.template
```

### 生产工作流

1. **数据准备阶段**
   - 从数据源摄入原始数据
   - 运行数据质量检查
   - 应用特征转换
   - 对处理后的数据集进行版本控制

2. **训练阶段**
   - 加载版本化的训练数据
   - 执行训练任务
   - 跟踪实验和指标
   - 保存训练好的模型

3. **验证阶段**
   - 运行验证测试套件
   - 与基线对比
   - 生成性能报告
   - 批准部署

4. **部署阶段**
   - 打包模型工件
   - 部署到服务基础设施
   - 配置监控
   - 验证生产流量

## 最佳实践

### 管道设计

- **模块化**：每个阶段应可独立测试
- **幂等性**：重新运行阶段应是安全的
- **可观测性**：在每个阶段记录指标
- **版本控制**：跟踪数据、代码和模型版本
- **故障处理**：实现重试逻辑和告警

### 数据管理

- 使用数据验证库（Great Expectations、TFX）
- 使用 DVC 或类似工具对数据集进行版本控制
- 记录特征工程转换
- 维护数据溯源跟踪

### 模型运维

- 分离训练和服务基础设施
- 使用模型注册表（MLflow、Weights & Biases）
- 为新模型实现渐进式发布
- 监控模型性能漂移
- 维护回滚能力

### 部署策略

- 从影子部署开始
- 使用金丝雀发布进行验证
- 实现 A/B 测试基础设施
- 设置自动回滚触发器
- 监控延迟和吞吐量

## 集成点

### 编排工具

- **Apache Airflow**：基于 DAG 的工作流编排
- **Dagster**：基于资产的管道编排
- **Kubeflow Pipelines**：Kubernetes 原生 ML 工作流
- **Prefect**：现代数据流自动化

### 实验跟踪

- MLflow 用于实验跟踪和模型注册表
- Weights & Biases 用于可视化和协作
- TensorBoard 用于训练指标

### 部署平台

- AWS SageMaker 用于托管 ML 基础设施
- Google Vertex AI 用于 GCP 部署
- Azure ML 用于 Azure 云
- OCI Data Science 用于 Oracle Cloud Infrastructure 部署
- Kubernetes + KServe 用于云无关的服务

## 渐进式披露

从基础开始，逐步增加复杂性：

1. **第 1 级**：简单线性管道（数据 → 训练 → 部署）
2. **第 2 级**：添加验证和监控阶段
3. **第 3 级**：实现超参数调优
4. **第 4 级**：添加 A/B 测试和渐进式发布
5. **第 5 级**：带集成策略的多模型管道

## 常见模式

### 批量训练管道

```yaml
# 参见 assets/pipeline-dag.yaml.template
stages:
  - name: data_preparation
    dependencies: []
  - name: model_training
    dependencies: [data_preparation]
  - name: model_evaluation
    dependencies: [model_training]
  - name: model_deployment
    dependencies: [model_evaluation]
```

### 实时特征管道

```python
# 实时特征的流处理
# 结合批量训练
# 参见 references/data-preparation.md
```

### 持续训练

```python
# 按计划自动重训练
# 由数据漂移检测触发
# 参见 references/model-training.md
```

## 故障排除

### 常见问题

- **管道失败**：检查依赖和数据可用性
- **训练不稳定**：审查超参数和数据质量
- **部署问题**：验证模型工件和服务配置
- **性能下降**：监控数据漂移和模型指标

### 调试步骤

1. 检查每个阶段的管道日志
2. 在边界处验证输入/输出数据
3. 隔离测试组件
4. 审查实验跟踪指标
5. 检查模型工件和元数据

## 后续步骤

设置管道后：

1. 探索 **hyperparameter-tuning** 技能进行优化
2. 学习 **experiment-tracking-setup** 了解 MLflow/W&B
3. 审查 **model-deployment-patterns** 了解服务策略
4. 使用可观测工具实现监控

## 相关技能

- **experiment-tracking-setup**：MLflow 和 Weights & Biases 集成
- **hyperparameter-tuning**：自动化超参数优化
- **model-deployment-patterns**：高级部署策略
