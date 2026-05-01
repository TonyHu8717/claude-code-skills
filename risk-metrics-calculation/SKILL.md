---
name: risk-metrics-calculation
description: 计算投资组合风险指标，包括 VaR、CVaR、Sharpe、Sortino 和回撤分析。在衡量投资组合风险、实施风险限制或构建风险监控系统时使用。
---

# 风险指标计算

投资组合管理的综合风险度量工具包，包括风险价值、预期损失和回撤分析。

## 何时使用此技能

- 衡量投资组合风险
- 实施风险限制
- 构建风险仪表板
- 计算风险调整后收益
- 设置头寸规模
- 监管报告

## 核心概念

### 1. 风险指标类别

| 类别          | 指标         | 用例             |
| ------------- | ------------ | -------------------- |
| **波动率**    | 标准差、Beta   | 一般风险         |
| **尾部风险**     | VaR、CVaR       | 极端损失       |
| **回撤**      | 最大回撤、Calmar  | 资本保全 |
| **风险调整** | Sharpe、Sortino | 绩效          |

### 2. 时间范围

```
日内：   日内交易者的分钟/小时级 VaR
日度：      标准风险报告
周度：     再平衡决策
月度：    绩效归因
年度：     战略配置
```

## 实现

### 模式 1：核心风险指标

```python
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Optional, Tuple

class RiskMetrics:
    """核心风险指标计算。"""

    def __init__(self, returns: pd.Series, rf_rate: float = 0.02):
        """
        参数：
            returns: 周期收益序列
            rf_rate: 年化无风险利率
        """
        self.returns = returns
        self.rf_rate = rf_rate
        self.ann_factor = 252  # 每年交易日

    # 波动率指标
    def volatility(self, annualized: bool = True) -> float:
        """收益的标准差。"""
        vol = self.returns.std()
        if annualized:
            vol *= np.sqrt(self.ann_factor)
        return vol

    def downside_deviation(self, threshold: float = 0, annualized: bool = True) -> float:
        """低于阈值的收益标准差。"""
        downside = self.returns[self.returns < threshold]
        if len(downside) == 0:
            return 0.0
        dd = downside.std()
        if annualized:
            dd *= np.sqrt(self.ann_factor)
        return dd

    def beta(self, market_returns: pd.Series) -> float:
        """相对于市场的 Beta。"""
        aligned = pd.concat([self.returns, market_returns], axis=1).dropna()
        if len(aligned) < 2:
            return np.nan
        cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])
        return cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else 0

    # 风险价值
    def var_historical(self, confidence: float = 0.95) -> float:
        """置信水平下的历史 VaR。"""
        return -np.percentile(self.returns, (1 - confidence) * 100)

    def var_parametric(self, confidence: float = 0.95) -> float:
        """假设正态分布的参数 VaR。"""
        z_score = stats.norm.ppf(confidence)
        return self.returns.mean() - z_score * self.returns.std()

    def var_cornish_fisher(self, confidence: float = 0.95) -> float:
        """使用 Cornish-Fisher 展开处理非正态性的 VaR。"""
        z = stats.norm.ppf(confidence)
        s = stats.skew(self.returns)  # 偏度
        k = stats.kurtosis(self.returns)  # 超额峰度

        # Cornish-Fisher 展开
        z_cf = (z + (z**2 - 1) * s / 6 +
                (z**3 - 3*z) * k / 24 -
                (2*z**3 - 5*z) * s**2 / 36)

        return -(self.returns.mean() + z_cf * self.returns.std())

    # 条件 VaR（预期损失）
    def cvar(self, confidence: float = 0.95) -> float:
        """预期损失 / CVaR / 平均 VaR。"""
        var = self.var_historical(confidence)
        return -self.returns[self.returns <= -var].mean()

    # 回撤分析
    def drawdowns(self) -> pd.Series:
        """计算回撤序列。"""
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.cummax()
        return (cumulative - running_max) / running_max

    def max_drawdown(self) -> float:
        """最大回撤。"""
        return self.drawdowns().min()

    def avg_drawdown(self) -> float:
        """平均回撤。"""
        dd = self.drawdowns()
        return dd[dd < 0].mean() if (dd < 0).any() else 0

    def drawdown_duration(self) -> Dict[str, int]:
        """回撤持续时间统计。"""
        dd = self.drawdowns()
        in_drawdown = dd < 0

        # 查找回撤期间
        drawdown_starts = in_drawdown & ~in_drawdown.shift(1).fillna(False)
        drawdown_ends = ~in_drawdown & in_drawdown.shift(1).fillna(False)

        durations = []
        current_duration = 0

        for i in range(len(dd)):
            if in_drawdown.iloc[i]:
                current_duration += 1
            elif current_duration > 0:
                durations.append(current_duration)
                current_duration = 0

        if current_duration > 0:
            durations.append(current_duration)

        return {
            "max_duration": max(durations) if durations else 0,
            "avg_duration": np.mean(durations) if durations else 0,
            "current_duration": current_duration
        }

    # 风险调整后收益
    def sharpe_ratio(self) -> float:
        """年化 Sharpe 比率。"""
        excess_return = self.returns.mean() * self.ann_factor - self.rf_rate
        vol = self.volatility(annualized=True)
        return excess_return / vol if vol > 0 else 0

    def sortino_ratio(self) -> float:
        """使用下行偏差的 Sortino 比率。"""
        excess_return = self.returns.mean() * self.ann_factor - self.rf_rate
        dd = self.downside_deviation(threshold=0, annualized=True)
        return excess_return / dd if dd > 0 else 0

    def calmar_ratio(self) -> float:
        """Calmar 比率（收益/最大回撤）。"""
        annual_return = (1 + self.returns).prod() ** (self.ann_factor / len(self.returns)) - 1
        max_dd = abs(self.max_drawdown())
        return annual_return / max_dd if max_dd > 0 else 0

    def omega_ratio(self, threshold: float = 0) -> float:
        """Omega 比率。"""
        returns_above = self.returns[self.returns > threshold] - threshold
        returns_below = threshold - self.returns[self.returns <= threshold]

        if returns_below.sum() == 0:
            return np.inf

        return returns_above.sum() / returns_below.sum()

    # 信息比率
    def information_ratio(self, benchmark_returns: pd.Series) -> float:
        """相对于基准的信息比率。"""
        active_returns = self.returns - benchmark_returns
        tracking_error = active_returns.std() * np.sqrt(self.ann_factor)
        active_return = active_returns.mean() * self.ann_factor
        return active_return / tracking_error if tracking_error > 0 else 0

    # 摘要
    def summary(self) -> Dict[str, float]:
        """生成综合风险摘要。"""
        dd_stats = self.drawdown_duration()

        return {
            # 收益
            "total_return": (1 + self.returns).prod() - 1,
            "annual_return": (1 + self.returns).prod() ** (self.ann_factor / len(self.returns)) - 1,

            # 波动率
            "annual_volatility": self.volatility(),
            "downside_deviation": self.downside_deviation(),

            # VaR 和 CVaR
            "var_95_historical": self.var_historical(0.95),
            "var_99_historical": self.var_historical(0.99),
            "cvar_95": self.cvar(0.95),

            # 回撤
            "max_drawdown": self.max_drawdown(),
            "avg_drawdown": self.avg_drawdown(),
            "max_drawdown_duration": dd_stats["max_duration"],

            # 风险调整
            "sharpe_ratio": self.sharpe_ratio(),
            "sortino_ratio": self.sortino_ratio(),
            "calmar_ratio": self.calmar_ratio(),
            "omega_ratio": self.omega_ratio(),

            # 分布
            "skewness": stats.skew(self.returns),
            "kurtosis": stats.kurtosis(self.returns),
        }
```

### 模式 2：投资组合风险

```python
class PortfolioRisk:
    """投资组合层面的风险计算。"""

    def __init__(
        self,
        returns: pd.DataFrame,
        weights: Optional[pd.Series] = None
    ):
        """
        参数：
            returns: 资产收益 DataFrame（列 = 资产）
            weights: 投资组合权重（默认：等权）
        """
        self.returns = returns
        self.weights = weights if weights is not None else \
            pd.Series(1/len(returns.columns), index=returns.columns)
        self.ann_factor = 252

    def portfolio_return(self) -> float:
        """加权投资组合收益。"""
        return (self.returns @ self.weights).mean() * self.ann_factor

    def portfolio_volatility(self) -> float:
        """投资组合波动率。"""
        cov_matrix = self.returns.cov() * self.ann_factor
        port_var = self.weights @ cov_matrix @ self.weights
        return np.sqrt(port_var)

    def marginal_risk_contribution(self) -> pd.Series:
        """各资产的边际风险贡献。"""
        cov_matrix = self.returns.cov() * self.ann_factor
        port_vol = self.portfolio_volatility()

        # 边际贡献
        mrc = (cov_matrix @ self.weights) / port_vol
        return mrc

    def component_risk(self) -> pd.Series:
        """各成分对总风险的贡献。"""
        mrc = self.marginal_risk_contribution()
        return self.weights * mrc

    def risk_parity_weights(self, target_vol: float = None) -> pd.Series:
        """计算风险平价权重。"""
        from scipy.optimize import minimize

        n = len(self.returns.columns)
        cov_matrix = self.returns.cov() * self.ann_factor

        def risk_budget_objective(weights):
            port_vol = np.sqrt(weights @ cov_matrix @ weights)
            mrc = (cov_matrix @ weights) / port_vol
            rc = weights * mrc
            target_rc = port_vol / n  # 等风险贡献
            return np.sum((rc - target_rc) ** 2)

        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},  # 权重之和为 1
        ]
        bounds = [(0.01, 1.0) for _ in range(n)]  # 最小 1%，最大 100%
        x0 = np.array([1/n] * n)

        result = minimize(
            risk_budget_objective,
            x0,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )

        return pd.Series(result.x, index=self.returns.columns)

    def correlation_matrix(self) -> pd.DataFrame:
        """资产相关性矩阵。"""
        return self.returns.corr()

    def diversification_ratio(self) -> float:
        """分散化比率（越高 = 越分散）。"""
        asset_vols = self.returns.std() * np.sqrt(self.ann_factor)
        weighted_vol = (self.weights * asset_vols).sum()
        port_vol = self.portfolio_volatility()
        return weighted_vol / port_vol if port_vol > 0 else 1

    def tracking_error(self, benchmark_returns: pd.Series) -> float:
        """相对于基准的跟踪误差。"""
        port_returns = self.returns @ self.weights
        active_returns = port_returns - benchmark_returns
        return active_returns.std() * np.sqrt(self.ann_factor)

    def conditional_correlation(
        self,
        threshold_percentile: float = 10
    ) -> pd.DataFrame:
        """压力期间的相关性。"""
        port_returns = self.returns @ self.weights
        threshold = np.percentile(port_returns, threshold_percentile)
        stress_mask = port_returns <= threshold
        return self.returns[stress_mask].corr()
```

### 模式 3：滚动风险指标

```python
class RollingRiskMetrics:
    """滚动窗口风险计算。"""

    def __init__(self, returns: pd.Series, window: int = 63):
        """
        参数：
            returns: 收益序列
            window: 滚动窗口大小（默认：63 = 约 3 个月）
        """
        self.returns = returns
        self.window = window

    def rolling_volatility(self, annualized: bool = True) -> pd.Series:
        """滚动波动率。"""
        vol = self.returns.rolling(self.window).std()
        if annualized:
            vol *= np.sqrt(252)
        return vol

    def rolling_sharpe(self, rf_rate: float = 0.02) -> pd.Series:
        """滚动 Sharpe 比率。"""
        rolling_return = self.returns.rolling(self.window).mean() * 252
        rolling_vol = self.rolling_volatility()
        return (rolling_return - rf_rate) / rolling_vol

    def rolling_var(self, confidence: float = 0.95) -> pd.Series:
        """滚动历史 VaR。"""
        return self.returns.rolling(self.window).apply(
            lambda x: -np.percentile(x, (1 - confidence) * 100),
            raw=True
        )

    def rolling_max_drawdown(self) -> pd.Series:
        """滚动最大回撤。"""
        def max_dd(returns):
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.cummax()
            drawdowns = (cumulative - running_max) / running_max
            return drawdowns.min()

        return self.returns.rolling(self.window).apply(max_dd, raw=False)

    def rolling_beta(self, market_returns: pd.Series) -> pd.Series:
        """相对于市场的滚动 Beta。"""
        def calc_beta(window_data):
            port_ret = window_data.iloc[:, 0]
            mkt_ret = window_data.iloc[:, 1]
            cov = np.cov(port_ret, mkt_ret)
            return cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else 0

        combined = pd.concat([self.returns, market_returns], axis=1)
        return combined.rolling(self.window).apply(
            lambda x: calc_beta(x.to_frame()),
            raw=False
        ).iloc[:, 0]

    def volatility_regime(
        self,
        low_threshold: float = 0.10,
        high_threshold: float = 0.20
    ) -> pd.Series:
        """分类波动率状态。"""
        vol = self.rolling_volatility()

        def classify(v):
            if v < low_threshold:
                return "low"
            elif v > high_threshold:
                return "high"
            else:
                return "normal"

        return vol.apply(classify)
```

### 模式 4：压力测试

```python
class StressTester:
    """历史和假设压力测试。"""

    # 历史危机期间
    HISTORICAL_SCENARIOS = {
        "2008_financial_crisis": ("2008-09-01", "2009-03-31"),
        "2020_covid_crash": ("2020-02-19", "2020-03-23"),
        "2022_rate_hikes": ("2022-01-01", "2022-10-31"),
        "dot_com_bust": ("2000-03-01", "2002-10-01"),
        "flash_crash_2010": ("2010-05-06", "2010-05-06"),
    }

    def __init__(self, returns: pd.Series, weights: pd.Series = None):
        self.returns = returns
        self.weights = weights

    def historical_stress_test(
        self,
        scenario_name: str,
        historical_data: pd.DataFrame
    ) -> Dict[str, float]:
        """针对历史危机期间测试投资组合。"""
        if scenario_name not in self.HISTORICAL_SCENARIOS:
            raise ValueError(f"Unknown scenario: {scenario_name}")

        start, end = self.HISTORICAL_SCENARIOS[scenario_name]

        # 获取危机期间的收益
        crisis_returns = historical_data.loc[start:end]

        if self.weights is not None:
            port_returns = (crisis_returns @ self.weights)
        else:
            port_returns = crisis_returns

        total_return = (1 + port_returns).prod() - 1
        max_dd = self._calculate_max_dd(port_returns)
        worst_day = port_returns.min()

        return {
            "scenario": scenario_name,
            "period": f"{start} to {end}",
            "total_return": total_return,
            "max_drawdown": max_dd,
            "worst_day": worst_day,
            "volatility": port_returns.std() * np.sqrt(252)
        }

    def hypothetical_stress_test(
        self,
        shocks: Dict[str, float]
    ) -> float:
        """
        针对假设冲击测试投资组合。

        参数：
            shocks: {资产: 冲击收益} 字典
        """
        if self.weights is None:
            raise ValueError("Weights required for hypothetical stress test")

        total_impact = 0
        for asset, shock in shocks.items():
            if asset in self.weights.index:
                total_impact += self.weights[asset] * shock

        return total_impact

    def monte_carlo_stress(
        self,
        n_simulations: int = 10000,
        horizon_days: int = 21,
        vol_multiplier: float = 2.0
    ) -> Dict[str, float]:
        """蒙特卡洛压力测试，使用提高的波动率。"""
        mean = self.returns.mean()
        vol = self.returns.std() * vol_multiplier

        simulations = np.random.normal(
            mean,
            vol,
            (n_simulations, horizon_days)
        )

        total_returns = (1 + simulations).prod(axis=1) - 1

        return {
            "expected_loss": -total_returns.mean(),
            "var_95": -np.percentile(total_returns, 5),
            "var_99": -np.percentile(total_returns, 1),
            "worst_case": -total_returns.min(),
            "prob_10pct_loss": (total_returns < -0.10).mean()
        }

    def _calculate_max_dd(self, returns: pd.Series) -> float:
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.cummax()
        drawdowns = (cumulative - running_max) / running_max
        return drawdowns.min()
```

## 快速参考

```python
# 日常用法
metrics = RiskMetrics(returns)
print(f"Sharpe: {metrics.sharpe_ratio():.2f}")
print(f"Max DD: {metrics.max_drawdown():.2%}")
print(f"VaR 95%: {metrics.var_historical(0.95):.2%}")

# 完整摘要
summary = metrics.summary()
for metric, value in summary.items():
    print(f"{metric}: {value:.4f}")
```

## 最佳实践

### 应该做的

- **使用多个指标** - 没有单一指标能捕捉所有风险
- **考虑尾部风险** - VaR 不够，使用 CVaR
- **滚动分析** - 风险随时间变化
- **压力测试** - 历史和假设的
- **记录假设** - 分布、回溯期等

### 不应该做的

- **不要仅依赖 VaR** - 低估尾部风险
- **不要假设正态性** - 收益具有厚尾
- **不要忽略相关性** - 压力期间会增加
- **不要使用短回溯期** - 会错过状态变化
- **不要忘记交易成本** - 影响实际风险
