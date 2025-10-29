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
        return `${parseFloat(value || 0).toFixed(1)}%`;
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

    const getScaleConfig = (axis, showGrid = true) => ({
        beginAtZero: true,
        grid: showGrid ? { color: CONFIG.gridColor } : { display: false }
    });

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
                        y: getScaleConfig('y'),
                        x: getScaleConfig('x')
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
                        x: getScaleConfig('x'),
                        y: getScaleConfig('y', false)
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
        if (!ctx) return null;

        destroyChart(elementId);

        const config = getBaseConfig(type, data, options);
        instances[elementId] = new Chart(ctx, config);
        
        return instances[elementId];
    };

    const createLineDataset = (label, data, color, fill = false) => ({
        label,
        data,
        borderColor: color,
        backgroundColor: color + '20',
        tension: 0.4,
        fill,
        borderWidth: 2
    });

    const renderCashFlow = (data) => {
        if (!data?.length) return;

        createChart('line', 'cashFlowChart', {
            labels: data.map(d => d.month),
            datasets: [
                createLineDataset('Income', data.map(d => parseFloatSafe(d.income)), CONFIG.colors.success),
                createLineDataset('Expenses', data.map(d => parseFloatSafe(d.expenses)), CONFIG.colors.danger),
                createLineDataset('Cash Flow', data.map(d => parseFloatSafe(d.cash_flow)), CONFIG.colors.primary, true)
            ]
        }, {
            tooltip: {
                callbacks: {
                    label: (ctx) => `${ctx.dataset.label}: ${formatCurrency(ctx.parsed.y)}`
                }
            }
        });
    };

    const renderExpenseDistribution = (data) => {
        const chartId = 'expenseDistributionChart';
        const ctx = document.getElementById(chartId);
        
        if (!ctx) return;

        if (!data?.length) {
            destroyChart(chartId);
            ctx.getContext('2d').clearRect(0, 0, ctx.width, ctx.height);
            return;
        }

        createChart('doughnut', chartId, {
            labels: data.map(d => d.name),
            datasets: [{
                data: data.map(d => parseFloatSafe(d.total)),
                backgroundColor: getColors(data.length),
                borderWidth: 0
            }]
        }, {
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const item = data[ctx.dataIndex];
                        return `${ctx.label}: ${formatCurrency(ctx.parsed)} (${formatPercentage(item.percentage)})`;
                    }
                }
            }
        });
    };

    const renderServiceRevenue = (data) => {
        if (!data?.length) return;

        createChart('bar', 'serviceRevenueChart', {
            labels: data.map(d => d.name),
            datasets: [{
                label: 'Revenue',
                data: data.map(d => parseFloatSafe(d.revenue)),
                backgroundColor: CONFIG.colors.primary,
                borderRadius: 8,
                borderWidth: 0
            }]
        }, {
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const item = data[ctx.dataIndex];
                        return [
                            `Revenue: ${formatCurrency(ctx.parsed.x)} (${formatPercentage(item.percentage)})`,
                            `Jobs: ${item.count}`,
                            `Average: ${formatCurrency(item.avg_revenue)}`
                        ];
                    }
                }
            }
        });
    };

    const renderExpenseTrends = (data) => {
        if (!data?.categories?.length || !data?.monthly_trends?.length) return;

        const colors = getColors(data.categories.length);

        createChart('line', 'expenseTrendsChart', {
            labels: data.monthly_trends.map(d => d.month),
            datasets: data.categories.map((cat, index) => 
                createLineDataset(
                    cat.name,
                    data.monthly_trends.map(month => parseFloatSafe(month.categories[cat.id])),
                    colors[index]
                )
            )
        }, {
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

        renderCashFlow(data.cashflow_data);
        renderExpenseDistribution(data.expense_distribution);
        renderServiceRevenue(data.service_revenue);
        renderExpenseTrends(data.expense_trends);
    };

    return {
        init,
        destroy: destroyAll,
        renderExpenseDistribution,
        renderServiceRevenue
    };
})();

window.DashboardCharts = DashboardCharts;
