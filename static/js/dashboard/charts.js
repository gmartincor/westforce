class DashboardCharts {
    constructor() {
        this.factory = new ChartFactory();
        this.utils = window.DashboardUtils;
        this.config = window.DashboardConfig;
    }

    init(data) {
        this.renderCashFlowChart(data.cashflow_data);
        this.renderExpenseDistributionChart(data.expense_distribution);
        this.renderServiceProfitabilityChart(data.service_profitability);
        this.renderExpenseTrendsChart(data.expense_trends);
    }

    destroy() {
        this.factory.destroyAll();
    }

    renderCashFlowChart(data) {
        if (!data || data.length === 0) return;

        const chartData = {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Cash Flow',
                data: data.map(d => this.utils.parseFloatSafe(d.cash_flow)),
                borderColor: this.config.colors.primary,
                backgroundColor: this.config.colors.primary + '20',
                tension: 0.4,
                fill: true,
                borderWidth: 2,
            }]
        };

        this.factory.create('line', 'cashFlowChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (context) => 'Cash Flow: ' + this.utils.formatCurrency(context.parsed.y)
                }
            }
        });
    }

    renderExpenseDistributionChart(data) {
        if (!data || data.length === 0) return;

        const chartData = {
            labels: data.map(d => d.name),
            datasets: [{
                data: data.map(d => this.utils.parseFloatSafe(d.total)),
                backgroundColor: this.utils.generateColors(data.length),
                borderWidth: 0,
            }]
        };

        this.factory.create('doughnut', 'expenseDistributionChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const item = data[context.dataIndex];
                        const value = this.utils.formatCurrency(context.parsed);
                        const percentage = this.utils.formatPercentage(item.percentage);
                        return `${context.label}: ${value} (${percentage})`;
                    }
                }
            }
        });
    }

    renderServiceProfitabilityChart(data) {
        if (!data || data.length === 0) return;

        const chartData = {
            labels: data.map(d => d.name),
            datasets: [{
                label: 'Profit Margin (%)',
                data: data.map(d => this.utils.parseFloatSafe(d.profit_margin)),
                backgroundColor: this.config.colors.success,
                borderRadius: 8,
                borderWidth: 0,
            }]
        };

        this.factory.create('horizontalBar', 'serviceProfitabilityChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (context) => {
                        const item = data[context.dataIndex];
                        const margin = this.utils.formatPercentage(context.parsed.x);
                        const revenue = this.utils.formatCurrency(item.revenue);
                        return `${margin} margin (${revenue} revenue)`;
                    }
                }
            }
        });
    }

    renderExpenseTrendsChart(data) {
        if (!data || !data.categories || !data.monthly_trends) return;

        const categories = data.categories;
        const colors = this.utils.generateColors(categories.length);

        const datasets = categories.map((cat, index) => ({
            label: cat.name,
            data: data.monthly_trends.map(month => 
                this.utils.parseFloatSafe(month.categories[cat.id])
            ),
            borderColor: colors[index],
            backgroundColor: colors[index] + '30',
            tension: 0.4,
            fill: false,
            borderWidth: 2,
        }));

        const chartData = {
            labels: data.monthly_trends.map(d => d.month),
            datasets: datasets
        };

        this.factory.create('line', 'expenseTrendsChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (context) => {
                        return `${context.dataset.label}: ${this.utils.formatCurrency(context.parsed.y)}`;
                    }
                }
            }
        });
    }
}

window.DashboardCharts = DashboardCharts;
