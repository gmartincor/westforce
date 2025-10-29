from .financial import FinancialMetricsService
from .cashflow import CashFlowService
from .profitability import ServiceProfitabilityService
from .expense_trends import ExpenseTrendService
from .expense_distribution import ExpenseDistributionService


class DashboardOrchestrator:
    
    def __init__(self):
        self.financial_service = FinancialMetricsService()
        self.cashflow_service = CashFlowService()
        self.profitability_service = ServiceProfitabilityService()
        self.expense_trend_service = ExpenseTrendService()
        self.expense_distribution_service = ExpenseDistributionService()
    
    def get_dashboard_data(self, **filters):
        return {
            **self.financial_service.get_data(**filters),
            'cashflow_data': self.cashflow_service.get_data(**filters),
            'service_profitability': self.profitability_service.get_data(**filters),
            'expense_trends': self.expense_trend_service.get_data(**filters),
            'expense_distribution': self.expense_distribution_service.get_data(**filters),
        }


__all__ = [
    'DashboardOrchestrator',
    'FinancialMetricsService',
    'CashFlowService',
    'ServiceProfitabilityService',
    'ExpenseTrendService',
    'ExpenseDistributionService',
]
