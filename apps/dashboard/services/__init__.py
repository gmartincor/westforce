from .financial import FinancialMetricsService
from .cashflow import CashFlowService
from .service_revenue import ServiceRevenueService
from .expense_trends import ExpenseTrendService
from .expense_distribution import ExpenseDistributionService


class DashboardOrchestrator:
    
    def __init__(self):
        self.financial_service = FinancialMetricsService()
        self.cashflow_service = CashFlowService()
        self.service_revenue_service = ServiceRevenueService()
        self.expense_trend_service = ExpenseTrendService()
        self.expense_distribution_service = ExpenseDistributionService()
    
    def get_dashboard_data(self, **filters):
        return {
            **self.financial_service.get_data(**filters),
            'cashflow_data': self.cashflow_service.get_data(**filters),
            'service_revenue': self.service_revenue_service.get_data(**filters),
            'expense_trends': self.expense_trend_service.get_data(**filters),
            'expense_distribution': self.expense_distribution_service.get_data(**filters),
        }


__all__ = [
    'DashboardOrchestrator',
    'FinancialMetricsService',
    'CashFlowService',
    'ServiceRevenueService',
    'ExpenseTrendService',
    'ExpenseDistributionService',
]
