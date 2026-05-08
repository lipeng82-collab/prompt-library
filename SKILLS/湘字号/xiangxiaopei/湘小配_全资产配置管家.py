#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
湘小配 · 全资产配置管家 Agent
湘江研究院研究中心 · 2026-04-02

功能：全品类资产组合管理、配置分析、风险评估、动态再平衡
覆盖：不动产/有价证券/贵金属/期货/数字货币/现金等价物
"""

import json
import os
import sys
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("=" * 60)
    print("缺少依赖库，请执行：pip install pandas numpy")
    print("=" * 60)
    sys.exit(1)

# ============================================================
# 全局配置
# ============================================================

PORTFOLIO_DIR = os.path.dirname(os.path.abspath(__file__))
PORTFOLIO_FILE = os.path.join(PORTFOLIO_DIR, "portfolio.json")

# 品类中英文映射
CATEGORY_MAP = {
    "real_estate": "不动产",
    "equities_a": "A股",
    "equities_hk": "港股",
    "equities_us": "美股",
    "funds": "基金",
    "equities": "有价证券",
    "fixed_income": "固收/债券",
    "precious_metals": "贵金属",
    "futures": "期货",
    "crypto": "数字货币",
    "cash_equivalents": "现金/货基",
    "cash": "现金",
    "other": "其他",
}

# 品类默认目标配置（均衡型）
DEFAULT_TARGETS = {
    "real_estate": 30,
    "equities": 25,       # equities_a + equities_hk + equities_us + funds
    "fixed_income": 15,
    "precious_metals": 10,
    "crypto": 5,
    "cash_equivalents": 10,
    "other": 5,
}

# 品类间相关性矩阵（中国市场经验值）
CORR_MATRIX = {
    "real_estate":      {"real_estate": 1.00, "equities": 0.30, "fixed_income": -0.10, "precious_metals": 0.05, "crypto": 0.10, "cash": 0.00},
    "equities":         {"real_estate": 0.30, "equities": 1.00, "fixed_income": -0.30, "precious_metals": 0.10, "crypto": 0.45, "cash": 0.05},
    "fixed_income":     {"real_estate": -0.10, "equities": -0.30, "fixed_income": 1.00, "precious_metals": 0.15, "crypto": -0.20, "cash": 0.10},
    "precious_metals":  {"real_estate": 0.05, "equities": 0.10, "fixed_income": 0.15, "precious_metals": 1.00, "crypto": 0.35, "cash": 0.05},
    "crypto":           {"real_estate": 0.10, "equities": 0.45, "fixed_income": -0.20, "precious_metals": 0.35, "crypto": 1.00, "cash": -0.05},
    "cash":             {"real_estate": 0.00, "equities": 0.05, "fixed_income": 0.10, "precious_metals": 0.05, "crypto": -0.05, "cash": 1.00},
}

# 品类预期年化波动率（中国市场经验值）
VOLATILITY = {
    "real_estate": 0.08,
    "equities": 0.25,
    "fixed_income": 0.04,
    "precious_metals": 0.18,
    "crypto": 0.80,
    "cash": 0.01,
    "futures": 0.35,
    "other": 0.15,
}

# 品类预期年化收益率（中国市场经验值）
EXPECTED_RETURN = {
    "real_estate": 0.05,
    "equities": 0.08,
    "fixed_income": 0.035,
    "precious_metals": 0.06,
    "crypto": 0.15,
    "cash": 0.02,
    "futures": 0.05,
    "other": 0.06,
}

# 六大压力测试场景
STRESS_SCENARIOS = [
    {"name": "2008全球金融危机", "impacts": {"real_estate": -0.20, "equities": -0.40, "fixed_income": 0.05, "precious_metals": 0.05, "crypto": 0, "cash": 0.01}},
    {"name": "2020新冠疫情冲击", "impacts": {"real_estate": -0.05, "equities": -0.30, "fixed_income": 0.03, "precious_metals": 0.15, "crypto": -0.50, "cash": 0.01}},
    {"name": "2022加息周期", "impacts": {"real_estate": -0.10, "equities": -0.20, "fixed_income": -0.15, "precious_metals": -0.10, "crypto": -0.65, "cash": 0.02}},
    {"name": "人民币贬值10%", "impacts": {"real_estate": -0.05, "equities": -0.08, "fixed_income": -0.02, "precious_metals": 0.10, "crypto": 0.20, "cash": -0.10}},
    {"name": "房产市场下行20%", "impacts": {"real_estate": -0.20, "equities": -0.15, "fixed_income": 0.02, "precious_metals": 0.05, "crypto": -0.10, "cash": 0.01}},
    {"name": "币圈极端崩盘", "impacts": {"real_estate": -0.02, "equities": -0.05, "fixed_income": 0.01, "precious_metals": 0.03, "crypto": -0.80, "cash": 0.01}},
]

# 流动性评分
LIQUIDITY_SCORE = {
    "real_estate": 1,    # 低流动性
    "equities": 5,       # 高流动性
    "fixed_income": 4,   # 较高流动性
    "precious_metals": 3, # 中等流动性
    "crypto": 4,         # 较高流动性（场内）
    "cash": 5,           # 最高流动性
    "futures": 4,        # 较高（但有合约限制）
    "other": 2,          # 视具体资产
}


# ============================================================
# 数据管理
# ============================================================

def create_sample_portfolio() -> Dict:
    """创建示例资产组合"""
    return {
        "owner": "示例用户",
        "currency": "CNY",
        "base_date": datetime.now().strftime("%Y-%m-%d"),
        "risk_profile": "moderate",
        "assets": {
            "real_estate": [
                {"name": "深圳市南山区XX小区", "type": "住宅", "purchase_price": 3500000,
                 "current_value": 4200000, "mortgage": 1500000, "liquidity": "low"}
            ],
            "equities_a": [
                {"name": "贵州茅台", "code": "600519.SH", "shares": 10, "cost_basis": 160000,
                 "current_price": "auto", "sector": "消费"},
                {"name": "招商银行", "code": "600036.SH", "shares": 1000, "cost_basis": 35000,
                 "current_price": "auto", "sector": "金融"},
            ],
            "funds": [
                {"name": "沪深300ETF", "code": "510300.SH", "shares": 5000, "cost_basis": 18000,
                 "current_price": "auto", "type": "指数基金"},
            ],
            "fixed_income": [
                {"name": "大额存单", "type": "银行存款", "principal": 200000, "rate": 2.5},
            ],
            "precious_metals": [
                {"name": "黄金", "type": "现货", "quantity_gram": 200, "avg_cost_per_gram": 480,
                 "current_price": "auto"},
            ],
            "crypto": [
                {"name": "Bitcoin", "symbol": "BTC", "quantity": 0.5, "avg_cost": 480000,
                 "current_price": "auto"},
            ],
            "cash_equivalents": [
                {"name": "活期存款", "amount": 50000, "type": "活期"},
                {"name": "余额宝", "amount": 100000, "type": "货币基金", "yield": 1.8},
            ],
        },
        "allocation_targets": {
            "real_estate": 30, "equities": 25, "fixed_income": 15,
            "precious_metals": 10, "crypto": 5, "cash_equivalents": 10, "other": 5,
        },
        "rebalance": {
            "threshold": 5,
            "frequency": "quarterly",
        }
    }


def load_portfolio(filepath: str = PORTFOLIO_FILE) -> Dict:
    """加载资产组合配置文件"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        print(f"[INFO] 未找到配置文件 {filepath}，已创建示例组合。")
        portfolio = create_sample_portfolio()
        save_portfolio(portfolio, filepath)
        return portfolio


def save_portfolio(portfolio: Dict, filepath: str = PORTFOLIO_FILE):
    """保存资产组合配置文件"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)
    print(f"[OK] 资产组合已保存至 {filepath}")


# ============================================================
# 核心分析引擎
# ============================================================

class PortfolioEngine:
    """资产组合分析引擎"""

    def __init__(self, portfolio: Dict):
        self.portfolio = portfolio
        self.category_values = {}  # 各品类市值
        self.total_value = 0       # 总资产
        self.category_pcts = {}    # 各品类占比

    def get_category_market_value(self, category: str) -> float:
        """
        计算指定品类的总市值（净额，扣除负债）
        """
        assets = self.portfolio.get("assets", {}).get(category, [])
        total = 0

        if category == "real_estate":
            for a in assets:
                net = a.get("current_value", 0) - a.get("mortgage", 0)
                total += max(0, net)

        elif category in ("equities_a", "equities_hk", "equities_us"):
            for a in assets:
                price = a.get("current_price", 0)
                if price == "auto":
                    # 实际使用时应调用湘小A/湘小美获取实时价格
                    # 此处用成本价近似（标记为待更新）
                    price = a.get("cost_basis", 0) / max(1, a.get("shares", 1))
                total += price * a.get("shares", 1)

        elif category == "funds":
            for a in assets:
                price = a.get("current_price", 0)
                if price == "auto":
                    price = a.get("cost_basis", 0) / max(1, a.get("shares", 1))
                total += price * a.get("shares", 1)

        elif category == "fixed_income":
            for a in assets:
                total += a.get("principal", a.get("face_value", 0))

        elif category == "precious_metals":
            for a in assets:
                price = a.get("current_price", 0)
                if price == "auto":
                    # 应调用湘小金获取
                    price = 680  # 示例价格
                if "quantity_gram" in a:
                    total += a["quantity_gram"] * price
                elif "shares" in a:
                    total += a["shares"] * price

        elif category == "futures":
            for a in assets:
                # 期货记录浮动盈亏（简化处理）
                margin = a.get("margin", 0)
                total += margin  # 以保证金为参考

        elif category == "crypto":
            for a in assets:
                price = a.get("current_price", 0)
                if price == "auto":
                    # 应调用湘小币获取
                    if a.get("symbol") == "BTC":
                        price = 580000
                    elif a.get("symbol") == "ETH":
                        price = 22000
                    else:
                        price = 0
                total += a.get("quantity", 0) * price

        elif category == "cash_equivalents":
            for a in assets:
                total += a.get("amount", 0)

        else:
            for a in assets:
                total += a.get("current_value", a.get("amount", a.get("principal", 0)))

        return total

    def compute_all(self):
        """计算所有品类市值和占比"""
        assets_data = self.portfolio.get("assets", {})
        self.category_values = {}

        for category in CATEGORY_MAP:
            if category in assets_data:
                val = self.get_category_market_value(category)
                if val > 0:
                    self.category_values[category] = val

        self.total_value = sum(self.category_values.values())

        for cat, val in self.category_values.items():
            self.category_pcts[cat] = (val / self.total_value * 100) if self.total_value > 0 else 0

    def get_aggregated_categories(self) -> Dict[str, Tuple[float, float]]:
        """
        将细分品类聚合为配置目标中的大类
        返回: {大类名: (市值, 占比%)}
        """
        aggregated = {}
        mapping = {
            "real_estate": ["real_estate"],
            "equities": ["equities_a", "equities_hk", "equities_us", "funds"],
            "fixed_income": ["fixed_income"],
            "precious_metals": ["precious_metals"],
            "futures": ["futures"],
            "crypto": ["crypto"],
            "cash_equivalents": ["cash_equivalents"],
            "other": ["other"],
        }

        for agg_name, sub_cats in mapping.items():
            total = sum(self.category_values.get(sc, 0) for sc in sub_cats)
            pct = (total / self.total_value * 100) if self.total_value > 0 else 0
            if total > 0:
                aggregated[agg_name] = (total, pct)

        return aggregated

    def calc_hhi(self) -> float:
        """计算赫芬达尔-赫希曼指数（HHI），评估集中度"""
        # 使用聚合后的大类占比
        agg = self.get_aggregated_categories()
        shares = [pct for _, (_, pct) in agg.items()]
        return sum(s ** 2 for s in shares)

    def calc_effective_diversification(self) -> float:
        """
        计算有效分散化比率
        >1.5 表示分散化效果良好
        """
        agg = self.get_aggregated_categories()
        weights = {name: pct / 100 for name, (_, pct) in agg.items()}

        # 组合加权波动率
        portfolio_vol = 0
        categories = list(weights.keys())
        for i, cat_i in enumerate(categories):
            for j, cat_j in enumerate(categories):
                corr = CORR_MATRIX.get(cat_i, {}).get(cat_j, 0)
                vol_i = VOLATILITY.get(cat_i, 0.15)
                vol_j = VOLATILITY.get(cat_j, 0.15)
                portfolio_vol += weights[cat_i] * weights[cat_j] * corr * vol_i * vol_j

        portfolio_vol = math.sqrt(max(0, portfolio_vol))

        # 加权平均波动率
        avg_vol = sum(weights[cat] * VOLATILITY.get(cat, 0.15) for cat in categories)

        if avg_vol > 0:
            return avg_vol / portfolio_vol if portfolio_vol > 0 else 1.0
        return 1.0

    def calc_var(self, confidence: float = 0.95, horizon_days: int = 30) -> Tuple[float, float]:
        """
        计算组合VaR和CVaR（历史模拟法简化版）

        返回: (VaR金额, CVaR金额)
        """
        agg = self.get_aggregated_categories()
        weights = {name: pct / 100 for name, (_, pct) in agg.items()}

        # 组合加权日波动率
        portfolio_var = 0
        categories = list(weights.keys())
        for i, cat_i in enumerate(categories):
            for j, cat_j in enumerate(categories):
                corr = CORR_MATRIX.get(cat_i, {}).get(cat_j, 0)
                vol_i = VOLATILITY.get(cat_i, 0.15)
                vol_j = VOLATILITY.get(cat_j, 0.15)
                portfolio_var += weights[cat_i] * weights[cat_j] * corr * vol_i * vol_j

        daily_vol = math.sqrt(max(0, portfolio_var)) / math.sqrt(252)
        horizon_vol = daily_vol * math.sqrt(horizon_days)

        # 正态分布近似
        from math import erf, sqrt
        if confidence == 0.95:
            z = 1.645
        elif confidence == 0.99:
            z = 2.326
        else:
            z = 1.645

        var_pct = z * horizon_vol
        cvar_pct = var_pct * 1.2  # 简化：CVaR约为VaR的1.2倍

        var_amount = self.total_value * var_pct
        cvar_amount = self.total_value * cvar_pct

        return var_amount, cvar_amount

    def run_stress_tests(self) -> List[Dict]:
        """运行六大压力测试场景"""
        agg = self.get_aggregated_categories()
        results = []

        for scenario in STRESS_SCENARIOS:
            total_loss = 0
            details = []
            for cat_name, (value, pct) in agg.items():
                impact = scenario["impacts"].get(cat_name, 0)
                loss = value * impact
                total_loss += loss
                if abs(loss) > 100:  # 忽略极小金额
                    details.append({
                        "category": cat_name,
                        "value": value,
                        "impact_pct": impact * 100,
                        "loss": loss,
                    })

            loss_pct = (total_loss / self.total_value * 100) if self.total_value > 0 else 0

            # 评级
            if loss_pct > -5:
                rating = "可承受"
            elif loss_pct > -15:
                rating = "需关注"
            elif loss_pct > -25:
                rating = "较高风险"
            else:
                rating = "高危"

            results.append({
                "scenario": scenario["name"],
                "total_loss": total_loss,
                "loss_pct": loss_pct,
                "rating": rating,
                "details": details,
            })

        return results

    def calc_rebalance_needs(self) -> List[Dict]:
        """计算再平衡需求"""
        targets = self.portfolio.get("allocation_targets", DEFAULT_TARGETS)
        threshold = self.portfolio.get("rebalance", {}).get("threshold", 5)
        agg = self.get_aggregated_categories()

        rebalance_list = []
        for cat_name, target_pct in targets.items():
            if cat_name in agg:
                _, current_pct = agg[cat_name]
                deviation = current_pct - target_pct

                need_rebalance = abs(deviation) >= threshold

                if deviation > 0:
                    action = "减仓"
                    priority = "高" if deviation > threshold * 2 else "中"
                elif deviation < 0:
                    action = "加仓"
                    priority = "高" if abs(deviation) > threshold * 2 else "中"
                else:
                    action = "维持"
                    priority = "低"

                rebalance_list.append({
                    "category": cat_name,
                    "category_cn": CATEGORY_MAP.get(cat_name, cat_name),
                    "current_pct": round(current_pct, 1),
                    "target_pct": target_pct,
                    "deviation": round(deviation, 1),
                    "need_rebalance": need_rebalance,
                    "action": action,
                    "priority": priority,
                    "adjust_amount": round(self.total_value * deviation / 100, 0),
                })

        return sorted(rebalance_list, key=lambda x: abs(x["deviation"]), reverse=True)

    def calc_liquidity_score(self) -> Tuple[float, Dict]:
        """计算组合流动性评分"""
        agg = self.get_aggregated_categories()
        weighted_score = 0
        details = {}

        for cat_name, (value, pct) in agg.items():
            score = LIQUIDITY_SCORE.get(cat_name, 3)
            weighted_score += (pct / 100) * score
            details[cat_name] = {
                "score": score,
                "weight": round(pct, 1),
                "weighted": round((pct / 100) * score, 2),
                "label": {1: "低", 2: "较低", 3: "中", 4: "较高", 5: "高"}.get(score, "未知")
            }

        return round(weighted_score, 2), details

    def calc_expected_return(self) -> Tuple[float, Dict]:
        """计算组合预期年化收益率"""
        agg = self.get_aggregated_categories()
        weighted_return = 0
        details = {}

        for cat_name, (value, pct) in agg.items():
            exp_ret = EXPECTED_RETURN.get(cat_name, 0.06)
            weighted_return += (pct / 100) * exp_ret
            details[cat_name] = {
                "expected_return": exp_ret * 100,
                "weight": round(pct, 1),
                "contribution": round((pct / 100) * exp_ret * 100, 2),
            }

        return round(weighted_return * 100, 2), details


# ============================================================
# 报告生成
# ============================================================

def format_wan(value: float) -> str:
    """格式化为万元"""
    if abs(value) >= 100000000:  # >= 1亿
        return f"{value / 100000000:.2f}亿"
    else:
        return f"{value / 10000:.2f}万"


def generate_full_report(engine: PortfolioEngine) -> str:
    """生成完整资产配置报告"""
    engine.compute_all()
    lines = []
    lines.append("=" * 70)
    lines.append("          湘小配 · 全资产配置报告")
    lines.append(f"          报告日期：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)
    lines.append("")

    # === 一、资产全景 ===
    lines.append("=" * 70)
    lines.append("一、资产全景概览")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  总资产：{format_wan(engine.total_value)}")
    lines.append(f"  资产品类数：{len(engine.category_values)}")
    lines.append("")

    lines.append("  【各品类明细】")
    lines.append(f"  {'品类':<14} {'市值':>12} {'占比':>8} {'流动性':>6}")
    lines.append(f"  {'-' * 14} {'-' * 12} {'-' * 8} {'-' * 6}")

    for cat, val in sorted(engine.category_values.items(), key=lambda x: -x[1]):
        pct = engine.category_pcts.get(cat, 0)
        liq = {1: "低", 2: "较低", 3: "中", 4: "较高", 5: "高"}.get(
            LIQUIDITY_SCORE.get(cat, 3), "?")
        cn = CATEGORY_MAP.get(cat, cat)
        lines.append(f"  {cn:<12} {format_wan(val):>14} {pct:>7.1f}% {liq:>6}")

    lines.append(f"  {'合计':<14} {format_wan(engine.total_value):>14} {'100.0%':>8}")
    lines.append("")

    # === 二、配置结构分析 ===
    lines.append("=" * 70)
    lines.append("二、配置结构分析")
    lines.append("=" * 70)
    lines.append("")
    agg = engine.get_aggregated_categories()
    targets = engine.portfolio.get("allocation_targets", DEFAULT_TARGETS)

    lines.append(f"  {'大类':<14} {'市值':>12} {'实际':>7} {'目标':>7} {'偏离':>8} {'状态':>6}")
    lines.append(f"  {'-' * 14} {'-' * 12} {'-' * 7} {'-' * 7} {'-' * 8} {'-' * 6}")

    for agg_name, (value, pct) in sorted(agg.items(), key=lambda x: -x[1][0]):
        target = targets.get(agg_name, 0)
        dev = pct - target
        status = "[OK]" if abs(dev) < 3 else ("[!]" if abs(dev) < 5 else "[X]")
        cn = CATEGORY_MAP.get(agg_name, agg_name)
        lines.append(f"  {cn:<12} {format_wan(value):>14} {pct:>6.1f}% {target:>6}% {dev:>+7.1f}% {status:>6}")

    lines.append("")

    # === 三、风险诊断 ===
    lines.append("=" * 70)
    lines.append("三、风险诊断")
    lines.append("=" * 70)
    lines.append("")

    # 集中度
    hhi = engine.calc_hhi()
    lines.append(f"  【集中度风险】")
    lines.append(f"  HHI指数：{hhi:,.0f}", )
    if hhi < 1800:
        lines.append(f"  评级：[OK] 分散良好")
    elif hhi < 3000:
        lines.append(f"  评级：[!] 适度集中，建议优化")
    else:
        lines.append(f"  评级：[X] 过度集中，强烈建议分散")
    lines.append("")

    # 有效分散化
    ed = engine.calc_effective_diversification()
    lines.append(f"  【有效分散化比率】")
    lines.append(f"  比率：{ed:.2f}")
    if ed > 1.5:
        lines.append(f"  评价：[OK] 分散化效果良好")
    elif ed > 1.2:
        lines.append(f"  评价：[!] 分散化效果一般")
    else:
        lines.append(f"  评价：[X] 分散化效果差，品类间相关性过高")
    lines.append("")

    # VaR
    var_95, cvar_95 = engine.calc_var(0.95, 30)
    var_99, cvar_99 = engine.calc_var(0.99, 30)
    lines.append(f"  【下行风险（30天）】")
    lines.append(f"  {'置信度':>8} {'VaR':>14} {'CVaR':>14}")
    lines.append(f"  {'-' * 8} {'-' * 14} {'-' * 14}")
    lines.append(f"  {'95%':>8} {format_wan(var_95):>14} {format_wan(cvar_95):>14}")
    lines.append(f"  {'99%':>8} {format_wan(var_99):>14} {format_wan(cvar_99):>14}")
    lines.append(f"  （VaR：正常情况下最大可能损失 | CVaR：极端情况下的平均损失）")
    lines.append("")

    # 流动性
    liq_score, liq_details = engine.calc_liquidity_score()
    lines.append(f"  【流动性评分】")
    lines.append(f"  加权流动性评分：{liq_score}/5.00")
    for cat, d in liq_details.items():
        cn = CATEGORY_MAP.get(cat, cat)
        lines.append(f"    {cn:<12} 评分:{d['score']} 权重:{d['weight']}% → {d['label']}")
    lines.append("")

    # === 四、压力测试 ===
    lines.append("=" * 70)
    lines.append("四、压力测试（六大极端场景）")
    lines.append("=" * 70)
    lines.append("")
    stress_results = engine.run_stress_tests()
    lines.append(f"  {'场景':<20} {'预估损失':>14} {'占比':>8} {'评级':>8}")
    lines.append(f"  {'-' * 20} {'-' * 14} {'-' * 8} {'-' * 8}")

    for r in stress_results:
        lines.append(f"  {r['scenario']:<18} {format_wan(r['total_loss']):>14} {r['loss_pct']:>+7.1f}% {r['rating']:>8}")

    lines.append("")

    # 最严重场景详情
    worst = min(stress_results, key=lambda x: x["loss_pct"])
    if worst["loss_pct"] < -10:
        lines.append(f"  [!] 最严重场景：{worst['scenario']}（损失{worst['loss_pct']:+.1f}%）")
        lines.append(f"    主要受损品类：")
        for d in sorted(worst["details"], key=lambda x: x["loss"])[:5]:
            cn = CATEGORY_MAP.get(d["category"], d["category"])
            lines.append(f"      {cn}: {format_wan(abs(d['loss']))} ({d['impact_pct']:+.0f}%)")
        lines.append("")

    # === 五、再平衡建议 ===
    lines.append("=" * 70)
    lines.append("五、再平衡建议")
    lines.append("=" * 70)
    lines.append("")
    rebalance = engine.calc_rebalance_needs()
    threshold = engine.portfolio.get("rebalance", {}).get("threshold", 5)

    needs_rebalance = [r for r in rebalance if r["need_rebalance"]]

    if needs_rebalance:
        lines.append(f"  再平衡触发阈值：±{threshold}个百分点")
        lines.append(f"  以下品类偏离目标配置，建议调整：")
        lines.append("")
        lines.append(f"  {'品类':<12} {'实际':>7} {'目标':>7} {'偏离':>8} {'操作':>6} {'调整额':>12} {'优先级':>6}")
        lines.append(f"  {'-' * 12} {'-' * 7} {'-' * 7} {'-' * 8} {'-' * 6} {'-' * 12} {'-' * 6}")

        for r in needs_rebalance:
            lines.append(
                f"  {r['category_cn']:<10} {r['current_pct']:>6.1f}% {r['target_pct']:>6}% "
                f"{r['deviation']:>+7.1f}% {r['action']:>6} {format_wan(r['adjust_amount']):>12} {r['priority']:>6}"
            )
    else:
        lines.append(f"  [OK] 当前配置偏离度在阈值（±{threshold}%）以内，暂无需再平衡。")

    lines.append("")

    # === 六、收益预期 ===
    lines.append("=" * 70)
    lines.append("六、组合收益预期")
    lines.append("=" * 70)
    lines.append("")
    exp_ret, ret_details = engine.calc_expected_return()
    lines.append(f"  组合预期年化收益率：{exp_ret:.2f}%")
    lines.append("")
    lines.append(f"  {'品类':<14} {'预期收益':>10} {'权重':>8} {'贡献':>8}")
    lines.append(f"  {'-' * 14} {'-' * 10} {'-' * 8} {'-' * 8}")
    for cat, d in ret_details.items():
        cn = CATEGORY_MAP.get(cat, cat)
        lines.append(f"  {cn:<12} {d['expected_return']:>9.1f}% {d['weight']:>7.1f}% {d['contribution']:>7.2f}%")
    lines.append("")

    # === 七、相关性矩阵 ===
    lines.append("=" * 70)
    lines.append("七、跨品类相关性矩阵")
    lines.append("=" * 70)
    lines.append("")
    cats = list(CORR_MATRIX.keys())
    cn_names = [CATEGORY_MAP.get(c, c) for c in cats]

    # 表头
    header = f"  {'':>10}"
    for name in cn_names:
        header += f" {name:>8}"
    lines.append(header)
    lines.append(f"  {'-' * (10 + 9 * len(cats))}")

    for i, cat_i in enumerate(cats):
        row = f"  {cn_names[i]:>10}"
        for j, cat_j in enumerate(cats):
            val = CORR_MATRIX[cat_i][cat_j]
            color = " " if val >= 0 else ""
            row += f" {color}{val:>+7.2f}"
        lines.append(row)

    lines.append("")

    # === 尾部 ===
    lines.append("=" * 70)
    lines.append("")
    lines.append("  [!] 重要声明：本报告仅供内部研究参考，不构成任何投资建议。")
    lines.append("  [!] 投资有风险，决策需谨慎。")
    lines.append("")
    lines.append("  湘小配 · 湘江研究院全资产配置管家")
    lines.append(f"  生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)

    return "\n".join(lines)


def generate_quick_view(engine: PortfolioEngine) -> str:
    """生成快速概览（简版）"""
    engine.compute_all()
    agg = engine.get_aggregated_categories()
    lines = []
    lines.append(f"\n{'='*50}")
    lines.append(f"  湘小配 · 资产快速概览  {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"{'='*50}")
    lines.append(f"  总资产：{format_wan(engine.total_value)}")
    lines.append(f"  品类数：{len(engine.category_values)}")
    lines.append(f"")

    for agg_name, (value, pct) in sorted(agg.items(), key=lambda x: -x[1][0]):
        cn = CATEGORY_MAP.get(agg_name, agg_name)
        bar_len = int(pct / 2)
        bar = "#" * bar_len + "." * (25 - bar_len)
        lines.append(f"  {cn:<10} {bar} {pct:>5.1f}%  {format_wan(value)}")

    hhi = engine.calc_hhi()
    lines.append(f"")
    if hhi < 1800:
        lines.append(f"  HHI指数: {hhi:,.0f}  |  分散良好 [OK]")
    elif hhi < 3000:
        lines.append(f"  HHI指数: {hhi:,.0f}  |  适度集中 [!]")
    else:
        lines.append(f"  HHI指数: {hhi:,.0f}  |  过度集中 [X]")

    return "\n".join(lines)


# ============================================================
# 交互式菜单
# ============================================================

def main_menu():
    """主菜单"""
    portfolio = load_portfolio()
    engine = PortfolioEngine(portfolio)

    while True:
        print("\n" + "=" * 50)
        print("    湘小配 · 全资产配置管家")
        print("=" * 50)
        print("")
        print("  1  资产快速概览")
        print("  2  完整配置报告")
        print("  3  压力测试")
        print("  4  再平衡建议")
        print("  5  风险诊断")
        print("  6  导出组合数据")
        print("  7  编辑资产组合（打开JSON）")
        print("  0  退出")
        print("")

        choice = input("  请选择操作 [0-7]: ").strip()

        if choice == "1":
            report = generate_quick_view(engine)
            print(report)

        elif choice == "2":
            report = generate_full_report(engine)
            print(report)
            # 保存报告
            report_file = os.path.join(PORTFOLIO_DIR, f"资产配置报告_{datetime.now().strftime('%Y%m%d_%H%M')}.txt")
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n  [OK] 报告已保存至：{report_file}")

        elif choice == "3":
            engine.compute_all()
            results = engine.run_stress_tests()
            print("\n  == 压力测试结果 ==")
            for r in results:
                icon = "[OK]" if r["loss_pct"] > -10 else ("[!]" if r["loss_pct"] > -25 else "[X]")
                print(f"  {icon} {r['scenario']:<20} 损失{r['loss_pct']:+.1f}% ({format_wan(r['total_loss'])}) [{r['rating']}]")

        elif choice == "4":
            engine.compute_all()
            rebalance = engine.calc_rebalance_needs()
            threshold = portfolio.get("rebalance", {}).get("threshold", 5)
            needs = [r for r in rebalance if r["need_rebalance"]]

            print(f"\n  == 再平衡建议（阈值±{threshold}%）==")
            if needs:
                for r in needs:
                    print(f"  {r['action']}{r['category_cn']}：当前{r['current_pct']:.1f}% → 目标{r['target_pct']}%（偏离{r['deviation']:+.1f}%）调整{format_wan(r['adjust_amount'])}")
            else:
                print(f"  [OK] 当前配置在阈值范围内，暂无需调整。")

        elif choice == "5":
            engine.compute_all()
            print("\n  == 风险诊断 ==")

            hhi = engine.calc_hhi()
            hhi_label = "分散良好" if hhi < 1800 else ("适度集中" if hhi < 3000 else "过度集中")
            print(f"  HHI指数: {hhi:,.0f} ({hhi_label})")

            ed = engine.calc_effective_diversification()
            ed_label = "良好" if ed > 1.5 else ("一般" if ed > 1.2 else "差")
            print(f"  分散化比率: {ed:.2f} ({ed_label})")

            var_95, cvar_95 = engine.calc_var(0.95, 30)
            print(f"  30天VaR(95%): {format_wan(var_95)}")
            print(f"  30天CVaR(95%): {format_wan(cvar_95)}")

            liq, _ = engine.calc_liquidity_score()
            print(f"  流动性评分: {liq:.2f}/5.00")

        elif choice == "6":
            # 导出组合数据
            export_file = os.path.join(PORTFOLIO_DIR, f"portfolio_export_{datetime.now().strftime('%Y%m%d')}.json")
            save_portfolio(portfolio, export_file)
            print(f"\n  [OK] 组合数据已导出至：{export_file}")

        elif choice == "7":
            print(f"\n  配置文件路径：{PORTFOLIO_FILE}")
            print(f"  请用文本编辑器打开编辑，保存后重新运行即可。")
            try:
                os.startfile(PORTFOLIO_FILE)
            except:
                print(f"  无法自动打开，请手动打开上述路径。")

        elif choice == "0":
            print("\n  再见！投资有风险，决策需谨慎。")
            break

        else:
            print("\n  无效选择，请重新输入。")


if __name__ == "__main__":
    main_menu()
