---
name: backtesting-frameworks
description: 构建稳健的回测系统，正确处理前视偏差、幸存者偏差和交易成本。用于开发交易算法、验证策略或构建回测基础设施时使用。
---

# 回测框架

构建稳健的、生产级的回测系统，避免常见陷阱并产生可靠的策略性能估计。

## 何时使用此技能

- 开发交易策略回测
- 构建回测基础设施
- 验证策略性能
- 避免常见的回测偏差
- 实现前进分析
- 比较策略方案

## 核心概念

### 1. 回测偏差

| 偏差 | 描述 | 缓解措施 |
| ---------------- | ------------------------- | ----------------------- |
| **前视偏差** | 使用未来信息 | 时间点数据 |
| **幸存者偏差** | 仅对幸存者进行测试 | 使用已退市证券 |
| **过拟合** | 对历史数据进行曲线拟合 | 样本外测试 |
| **选择偏差** | 挑选策略 | 预注册 |
| **交易成本偏差** | 忽略交易成本 | 真实成本模型 |

### 2. 正确的回测结构

```
历史数据
      │
      ▼
┌─────────────────────────────────────────┐
│              训练集                       │
│  （策略开发与优化）                        │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│              验证集                       │
│  （参数选择，不可偷看）                     │
└─────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────┐
│              测试集                       │
│  （最终性能评估）                          │
└─────────────────────────────────────────┘
```

### 3. 前进分析

```
窗口 1: [训练──────][测试]
窗口 2:     [训练──────][测试]
窗口 3:         [训练──────][测试]
窗口 4:             [训练──────][测试]
                                     ─────▶ 时间
```

## 实现模式

### 模式 1：事件驱动回测器

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"

@dataclass
class Order:
    symbol: str
    side: OrderSide
    quantity: Decimal
    order_type: OrderType
    limit_price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    timestamp: Optional[datetime] = None

@dataclass
class Fill:
    order: Order
    fill_price: Decimal
    fill_quantity: Decimal
    commission: Decimal
    slippage: Decimal
    timestamp: datetime

@dataclass
class Position:
    symbol: str
    quantity: Decimal = Decimal("0")
    avg_cost: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")

    def update(self, fill: Fill) -> None:
        if fill.order.side == OrderSide.BUY:
            new_quantity = self.quantity + fill.fill_quantity
            if new_quantity != 0:
                self.avg_cost = (
                    (self.quantity * self.avg_cost + fill.fill_quantity * fill.fill_price)
                    / new_quantity
                )
            self.quantity = new_quantity
        else:
            self.realized_pnl += fill.fill_quantity * (fill.fill_price - self.avg_cost)
            self.quantity -= fill.fill_quantity

@dataclass
class Portfolio:
    cash: Decimal
    positions: Dict[str, Position] = field(default_factory=dict)

    def get_position(self, symbol: str) -> Position:
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        return self.positions[symbol]

    def process_fill(self, fill: Fill) -> None:
        position = self.get_position(fill.order.symbol)
        position.update(fill)

        if fill.order.side == OrderSide.BUY:
            self.cash -= fill.fill_price * fill.fill_quantity + fill.commission
        else:
            self.cash += fill.fill_price * fill.fill_quantity - fill.commission

    def get_equity(self, prices: Dict[str, Decimal]) -> Decimal:
        equity = self.cash
        for symbol, position in self.positions.items():
            if position.quantity != 0 and symbol in prices:
                equity += position.quantity * prices[symbol]
        return equity

class Strategy(ABC):
    @abstractmethod
    def on_bar(self, timestamp: datetime, data: pd.DataFrame) -> List[Order]:
        pass

    @abstractmethod
    def on_fill(self, fill: Fill) -> None:
        pass

class ExecutionModel(ABC):
    @abstractmethod
    def execute(self, order: Order, bar: pd.Series) -> Optional[Fill]:
        pass

class SimpleExecutionModel(ExecutionModel):
    def __init__(self, slippage_bps: float = 10, commission_per_share: float = 0.01):
        self.slippage_bps = slippage_bps
        self.commission_per_share = commission_per_share

    def execute(self, order: Order, bar: pd.Series) -> Optional[Fill]:
        if order.order_type == OrderType.MARKET:
            base_price = Decimal(str(bar["open"]))

            # 应用滑点
            slippage_mult = 1 + (self.slippage_bps / 10000)
            if order.side == OrderSide.BUY:
                fill_price = base_price * Decimal(str(slippage_mult))
            else:
                fill_price = base_price / Decimal(str(slippage_mult))

            commission = order.quantity * Decimal(str(self.commission_per_share))
            slippage = abs(fill_price - base_price) * order.quantity

            return Fill(
                order=order,
                fill_price=fill_price,
                fill_quantity=order.quantity,
                commission=commission,
                slippage=slippage,
                timestamp=bar.name
            )
        return None

class Backtester:
    def __init__(
        self,
        strategy: Strategy,
        execution_model: ExecutionModel,
        initial_capital: Decimal = Decimal("100000")
    ):
        self.strategy = strategy
        self.execution_model = execution_model
        self.portfolio = Portfolio(cash=initial_capital)
        self.equity_curve: List[tuple] = []
        self.trades: List[Fill] = []

    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        """在带有 DatetimeIndex 的 OHLCV 数据上运行回测。"""
        pending_orders: List[Order] = []

        for timestamp, bar in data.iterrows():
            # 以今天的价格执行待处理订单
            for order in pending_orders:
                fill = self.execution_model.execute(order, bar)
                if fill:
                    self.portfolio.process_fill(fill)
                    self.strategy.on_fill(fill)
                    self.trades.append(fill)

            pending_orders.clear()

            # 获取当前价格用于权益计算
            prices = {data.index.name or "default": Decimal(str(bar["close"]))}
            equity = self.portfolio.get_equity(prices)
            self.equity_curve.append((timestamp, float(equity)))

            # 为下一个 K 线生成新订单
            new_orders = self.strategy.on_bar(timestamp, data.loc[:timestamp])
            pending_orders.extend(new_orders)

        return self._create_results()

    def _create_results(self) -> pd.DataFrame:
        equity_df = pd.DataFrame(self.equity_curve, columns=["timestamp", "equity"])
        equity_df.set_index("timestamp", inplace=True)
        equity_df["returns"] = equity_df["equity"].pct_change()
        return equity_df
```

### 模式 2：向量化回测器（快速）

```python
import pandas as pd
import numpy as np
from typing import Callable, Dict, Any

class VectorizedBacktester:
    """用于简单策略的快速向量化回测器。"""

    def __init__(
        self,
        initial_capital: float = 100000,
        commission: float = 0.001,  # 0.1%
        slippage: float = 0.0005   # 0.05%
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

    def run(
        self,
        prices: pd.DataFrame,
        signal_func: Callable[[pd.DataFrame], pd.Series]
    ) -> Dict[str, Any]:
        """
        使用信号函数运行回测。

        参数:
            prices: 包含 'close' 列的 DataFrame
            signal_func: 返回持仓信号的函数 (-1, 0, 1)

        返回:
            包含结果的字典
        """
        # 生成信号（移位以避免前视偏差）
        signals = signal_func(prices).shift(1).fillna(0)

        # 计算收益
        returns = prices["close"].pct_change()

        # 计算含成本的策略收益
        position_changes = signals.diff().abs()
        trading_costs = position_changes * (self.commission + self.slippage)

        strategy_returns = signals * returns - trading_costs

        # 构建权益曲线
        equity = (1 + strategy_returns).cumprod() * self.initial_capital

        # 计算指标
        results = {
            "equity": equity,
            "returns": strategy_returns,
            "signals": signals,
            "metrics": self._calculate_metrics(strategy_returns, equity)
        }

        return results

    def _calculate_metrics(
        self,
        returns: pd.Series,
        equity: pd.Series
    ) -> Dict[str, float]:
        """计算性能指标。"""
        total_return = (equity.iloc[-1] / self.initial_capital) - 1
        annual_return = (1 + total_return) ** (252 / len(returns)) - 1
        annual_vol = returns.std() * np.sqrt(252)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0

        # 回撤
        rolling_max = equity.cummax()
        drawdown = (equity - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # 胜率
        winning_days = (returns > 0).sum()
        total_days = (returns != 0).sum()
        win_rate = winning_days / total_days if total_days > 0 else 0

        return {
            "total_return": total_return,
            "annual_return": annual_return,
            "annual_volatility": annual_vol,
            "sharpe_ratio": sharpe,
            "max_drawdown": max_drawdown,
            "win_rate": win_rate,
            "num_trades": int((returns != 0).sum())
        }

# 示例用法
def momentum_signal(prices: pd.DataFrame, lookback: int = 20) -> pd.Series:
    """简单动量策略：价格 > SMA 时做多，否则空仓。"""
    sma = prices["close"].rolling(lookback).mean()
    return (prices["close"] > sma).astype(int)

# 运行回测
# backtester = VectorizedBacktester()
# results = backtester.run(price_data, lambda p: momentum_signal(p, 50))
```

### 模式 3：前进优化

```python
from typing import Callable, Dict, List, Tuple, Any
import pandas as pd
import numpy as np
from itertools import product

class WalkForwardOptimizer:
    """使用锚定或滚动窗口的前进分析。"""

    def __init__(
        self,
        train_period: int,
        test_period: int,
        anchored: bool = False,
        n_splits: int = None
    ):
        """
        参数:
            train_period: 训练窗口中的 K 线数量
            test_period: 测试窗口中的 K 线数量
            anchored: 如果为 True，训练始终从头开始
            n_splits: 训练/测试分割数（如果为 None 则自动计算）
        """
        self.train_period = train_period
        self.test_period = test_period
        self.anchored = anchored
        self.n_splits = n_splits

    def generate_splits(
        self,
        data: pd.DataFrame
    ) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
        """生成训练/测试分割。"""
        splits = []
        n = len(data)

        if self.n_splits:
            step = (n - self.train_period) // self.n_splits
        else:
            step = self.test_period

        start = 0
        while start + self.train_period + self.test_period <= n:
            if self.anchored:
                train_start = 0
            else:
                train_start = start

            train_end = start + self.train_period
            test_end = min(train_end + self.test_period, n)

            train_data = data.iloc[train_start:train_end]
            test_data = data.iloc[train_end:test_end]

            splits.append((train_data, test_data))
            start += step

        return splits

    def optimize(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        param_grid: Dict[str, List],
        metric: str = "sharpe_ratio"
    ) -> Dict[str, Any]:
        """
        运行前进优化。

        参数:
            data: 完整数据集
            strategy_func: 函数(data, **params) -> 结果字典
            param_grid: 要测试的参数组合
            metric: 要优化的指标

        返回:
            所有测试周期的合并结果
        """
        splits = self.generate_splits(data)
        all_results = []
        optimal_params_history = []

        for i, (train_data, test_data) in enumerate(splits):
            # 在训练数据上优化
            best_params, best_metric = self._grid_search(
                train_data, strategy_func, param_grid, metric
            )
            optimal_params_history.append(best_params)

            # 使用最优参数进行测试
            test_results = strategy_func(test_data, **best_params)
            test_results["split"] = i
            test_results["params"] = best_params
            all_results.append(test_results)

            print(f"Split {i+1}/{len(splits)}: "
                  f"Best {metric}={best_metric:.4f}, params={best_params}")

        return {
            "split_results": all_results,
            "param_history": optimal_params_history,
            "combined_equity": self._combine_equity_curves(all_results)
        }

    def _grid_search(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        param_grid: Dict[str, List],
        metric: str
    ) -> Tuple[Dict, float]:
        """网格搜索最优参数。"""
        best_params = None
        best_metric = -np.inf

        # 生成所有参数组合
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())

        for values in product(*param_values):
            params = dict(zip(param_names, values))
            results = strategy_func(data, **params)

            if results["metrics"][metric] > best_metric:
                best_metric = results["metrics"][metric]
                best_params = params

        return best_params, best_metric

    def _combine_equity_curves(
        self,
        results: List[Dict]
    ) -> pd.Series:
        """合并所有测试周期的权益曲线。"""
        combined = pd.concat([r["equity"] for r in results])
        return combined
```

### 模式 4：蒙特卡洛分析

```python
import numpy as np
import pandas as pd
from typing import Dict, List

class MonteCarloAnalyzer:
    """用于策略稳健性的蒙特卡洛模拟。"""

    def __init__(self, n_simulations: int = 1000, confidence: float = 0.95):
        self.n_simulations = n_simulations
        self.confidence = confidence

    def bootstrap_returns(
        self,
        returns: pd.Series,
        n_periods: int = None
    ) -> np.ndarray:
        """
        通过重采样收益进行自举模拟。

        参数:
            returns: 历史收益序列
            n_periods: 每次模拟的长度（默认：与输入相同）

        返回:
            形状为 (n_simulations, n_periods) 的数组
        """
        if n_periods is None:
            n_periods = len(returns)

        simulations = np.zeros((self.n_simulations, n_periods))

        for i in range(self.n_simulations):
            # 有放回重采样
            simulated_returns = np.random.choice(
                returns.values,
                size=n_periods,
                replace=True
            )
            simulations[i] = simulated_returns

        return simulations

    def analyze_drawdowns(
        self,
        returns: pd.Series
    ) -> Dict[str, float]:
        """通过模拟分析回撤分布。"""
        simulations = self.bootstrap_returns(returns)

        max_drawdowns = []
        for sim_returns in simulations:
            equity = (1 + sim_returns).cumprod()
            rolling_max = np.maximum.accumulate(equity)
            drawdowns = (equity - rolling_max) / rolling_max
            max_drawdowns.append(drawdowns.min())

        max_drawdowns = np.array(max_drawdowns)

        return {
            "expected_max_dd": np.mean(max_drawdowns),
            "median_max_dd": np.median(max_drawdowns),
            f"worst_{int(self.confidence*100)}pct": np.percentile(
                max_drawdowns, (1 - self.confidence) * 100
            ),
            "worst_case": max_drawdowns.min()
        }

    def probability_of_loss(
        self,
        returns: pd.Series,
        holding_periods: List[int] = [21, 63, 126, 252]
    ) -> Dict[int, float]:
        """计算不同持有期的亏损概率。"""
        results = {}

        for period in holding_periods:
            if period > len(returns):
                continue

            simulations = self.bootstrap_returns(returns, period)
            total_returns = (1 + simulations).prod(axis=1) - 1
            prob_loss = (total_returns < 0).mean()
            results[period] = prob_loss

        return results

    def confidence_interval(
        self,
        returns: pd.Series,
        periods: int = 252
    ) -> Dict[str, float]:
        """计算未来收益的置信区间。"""
        simulations = self.bootstrap_returns(returns, periods)
        total_returns = (1 + simulations).prod(axis=1) - 1

        lower = (1 - self.confidence) / 2
        upper = 1 - lower

        return {
            "expected": total_returns.mean(),
            "lower_bound": np.percentile(total_returns, lower * 100),
            "upper_bound": np.percentile(total_returns, upper * 100),
            "std": total_returns.std()
        }
```

## 性能指标

```python
def calculate_metrics(returns: pd.Series, rf_rate: float = 0.02) -> Dict[str, float]:
    """计算全面的性能指标。"""
    # 年化因子（假设日收益）
    ann_factor = 252

    # 基本指标
    total_return = (1 + returns).prod() - 1
    annual_return = (1 + total_return) ** (ann_factor / len(returns)) - 1
    annual_vol = returns.std() * np.sqrt(ann_factor)

    # 风险调整收益
    sharpe = (annual_return - rf_rate) / annual_vol if annual_vol > 0 else 0

    # Sortino（下行偏差）
    downside_returns = returns[returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(ann_factor)
    sortino = (annual_return - rf_rate) / downside_vol if downside_vol > 0 else 0

    # Calmar 比率
    equity = (1 + returns).cumprod()
    rolling_max = equity.cummax()
    drawdowns = (equity - rolling_max) / rolling_max
    max_drawdown = drawdowns.min()
    calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0

    # 胜率和盈亏比
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    win_rate = len(wins) / len(returns[returns != 0]) if len(returns[returns != 0]) > 0 else 0
    profit_factor = wins.sum() / abs(losses.sum()) if losses.sum() != 0 else np.inf

    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "calmar_ratio": calmar,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "num_trades": int((returns != 0).sum())
    }
```

## 最佳实践

### 应该做的

- **使用时间点数据** - 避免前视偏差
- **包含交易成本** - 真实估计
- **样本外测试** - 始终保留数据
- **使用前进分析** - 不仅仅是训练/测试
- **蒙特卡洛分析** - 理解不确定性

### 不应该做的

- **不要过拟合** - 限制参数数量
- **不要忽略幸存者偏差** - 包含已退市的证券
- **不要随意使用调整后数据** - 理解调整方式
- **不要在完整历史上优化** - 保留测试集
- **不要忽略容量** - 市场影响很重要
