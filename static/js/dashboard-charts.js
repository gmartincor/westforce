const DashboardCharts = (() => {
    const CONFIG = {
        colors: {
            primary: '#3B82F6',
            success: '#10B981',
            danger: '#EF4444',
            warning: '#F59E0B',
            info: '#06B6D4',
            purple: '#8B5CF6',
            pink: '#EC4899',
            lime: '#84CC16',
            orange: '#F97316',
            teal: '#14B8A6',
            indigo: '#6366F1',
            rose: '#F43F5E'
        },
        gridColor: '#E5E7EB'
    };

    const instances = {};

    const formatCurrency = (value) => {
        return new Intl.NumberFormat('en-AU', {
            style: 'currency',
            currency: 'AUD'
        }).format(parseFloat(value) || 0);
    };

    const formatPercentage = (value) => {
        return parseFloat(value || 0).toFixed(1) + '%';
    };

    const parseFloatSafe = (value) => {
        const parsed = parseFloat(value);
        return isNaN(parsed) ? 0 : parsed;
    };

    const getColors = (count) => {
        const palette = Object.values(CONFIG.colors);
        return palette.slice(0, Math.min(count, palette.length));
    };

    const destroyChart = (id) => {
        if (instances[id]) {
            instances[id].destroy();
            delete instances[id];
        }
    };

    const destroyAll = () => {
        Object.keys(instances).forEach(destroyChart);
    };

    const getBaseConfig = (type, data, customOptions = {}) => {
        const baseConfigs = {
            line: {
                type: 'line',
                data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {
                        mode: 'index',
                        intersect: false
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: { color: CONFIG.gridColor }
                        },
                        x: {
                            grid: { color: CONFIG.gridColor }
                        }
                    }
                }
            },
            bar: {
                type: 'bar',
                data,
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        x: {
                            beginAtZero: true,
                            grid: { color: CONFIG.gridColor }
                        },
                        y: {
                            grid: { display: false }
                        }
                    }
                }
            },
            doughnut: {
                type: 'doughnut',
                data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom'
                        }
                    }
                }
            }
        };

        const config = baseConfigs[type];
        if (customOptions.tooltip) {
            config.options.plugins.tooltip = customOptions.tooltip;
        }
        
        return config;
    };

    const createChart = (type, elementId, data, options = {}) => {
        const ctx = document.getElementById(elementId);
        if (!ctx || !data) return null;

        destroyChart(elementId);

        const config = getBaseConfig(type, data, options);
        instances[elementId] = new Chart(ctx, config);
        
        return instances[elementId];
    };

    const renderCashFlow = (data) => {
        if (!data || data.length === 0) return;

        const chartData = {
            labels: data.map(d => d.month),
            datasets: [{
                label: 'Cash Flow',
                data: data.map(d => parseFloatSafe(d.cash_flow)),
                borderColor: CONFIG.colors.primary,
                backgroundColor: CONFIG.colors.primary + '20',
                tension: 0.4,
                fill: true,
                borderWidth: 2
            }]
        };

        createChart('line', 'cashFlowChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (ctx) => 'Cash Flow: ' + formatCurrency(ctx.parsed.y)
                }
            }
        });
    };

    const renderExpenseDistribution = (data) => {
        if (!data || data.length === 0) return;

        const chartData = {
            labels: data.map(d => d.name),
            datasets: [{
                data: data.map(d => parseFloatSafe(d.total)),
                backgroundColor: getColors(data.length),
                borderWidth: 0
            }]
        };

        createChart('doughnut', 'expenseDistributionChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const item = data[ctx.dataIndex];
                        const value = formatCurrency(ctx.parsed);
                        const percentage = formatPercentage(item.percentage);
                        return `${ctx.label}: ${value} (${percentage})`;
                    }
                }
            }
        });
    };

    const renderServiceProfitability = (data) => {
        if (!data || data.length === 0) return;

        const chartData = {
            labels: data.map(d => d.name),
            datasets: [{
                label: 'Profit Margin (%)',
                data: data.map(d => parseFloatSafe(d.profit_margin)),
                backgroundColor: CONFIG.colors.success,
                borderRadius: 8,
                borderWidth: 0
            }]
        };

        createChart('bar', 'serviceProfitabilityChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const item = data[ctx.dataIndex];
                        const margin = formatPercentage(ctx.parsed.x);
                        const revenue = formatCurrency(item.revenue);
                        return `${margin} margin (${revenue} revenue)`;
                    }
                }
            }
        });
    };

    const renderExpenseTrends = (data) => {
        if (!data || !data.categories || !data.monthly_trends) return;

        const colors = getColors(data.categories.length);

        const datasets = data.categories.map((cat, index) => ({
            label: cat.name,
            data: data.monthly_trends.map(month => 
                parseFloatSafe(month.categories[cat.id])
            ),
            borderColor: colors[index],
            backgroundColor: colors[index] + '30',
            tension: 0.4,
            fill: false,
            borderWidth: 2
        }));

        const chartData = {
            labels: data.monthly_trends.map(d => d.month),
            datasets
        };

        createChart('line', 'expenseTrendsChart', chartData, {
            tooltip: {
                callbacks: {
                    label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`
                }
            }
        });
    };

    const init = (data) => {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not loaded');
            return;
        }

        try {
            renderCashFlow(data.cashflow_data);
            renderExpenseDistribution(data.expense_distribution);
            renderServiceProfitability(data.service_profitability);
            renderExpenseTrends(data.expense_trends);
        } catch (error) {
            console.error('Error initializing charts:', error);
        }
    };

    return {
        init,
        destroy: destroyAll
    };
})();

window.DashboardCharts = DashboardCharts;
