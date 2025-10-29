window.dashboardCharts = {
    instances: {},

    init: function(data) {
        this.createTemporalChart(data.temporal_data);
        this.createExpensesChart(data.expense_categories);
        this.createServiceTypesChart(data.service_types);
        this.createPaymentMethodsChart(data.payment_methods);
    },

    destroy: function(chartId) {
        if (this.instances[chartId]) {
            this.instances[chartId].destroy();
            delete this.instances[chartId];
        }
    },

    createTemporalChart: function(data) {
        const ctx = document.getElementById('temporalChart');
        if (!ctx || !data || data.length === 0) return;

        this.destroy('temporal');

        this.instances.temporal = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.month),
                datasets: [
                    {
                        label: 'Income',
                        data: data.map(d => parseFloat(d.income) || 0),
                        borderColor: window.dashboardConfig.colors.success,
                        backgroundColor: window.dashboardConfig.colors.success + '20',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Expenses',
                        data: data.map(d => parseFloat(d.expenses) || 0),
                        borderColor: window.dashboardConfig.colors.danger,
                        backgroundColor: window.dashboardConfig.colors.danger + '20',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Profit',
                        data: data.map(d => parseFloat(d.profit) || 0),
                        borderColor: window.dashboardConfig.colors.primary,
                        backgroundColor: window.dashboardConfig.colors.primary + '20',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                ...window.dashboardConfig.chartDefaults,
                plugins: {
                    ...window.dashboardConfig.chartDefaults.plugins,
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': ' + 
                                       window.dashboardUtils.formatCurrency(context.parsed.y);
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
    },

    createExpensesChart: function(data) {
        const ctx = document.getElementById('expensesChart');
        if (!ctx || !data || data.length === 0) return;

        this.destroy('expenses');

        this.instances.expenses = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data: data.map(d => parseFloat(d.total) || 0),
                    backgroundColor: window.dashboardUtils.generateColors(data.length)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    ...window.dashboardConfig.chartDefaults.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = window.dashboardUtils.formatCurrency(context.parsed);
                                const percentage = parseFloat(data[context.dataIndex].percentage) || 0;
                                return context.label + ': ' + value + 
                                       ' (' + window.dashboardUtils.formatPercentage(percentage) + ')';
                            }
                        }
                    }
                }
            }
        });
    },

    createServiceTypesChart: function(data) {
        const ctx = document.getElementById('serviceTypesChart');
        if (!ctx || !data || data.length === 0) return;

        this.destroy('serviceTypes');

        this.instances.serviceTypes = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    label: 'Revenue',
                    data: data.map(d => parseFloat(d.total_revenue) || 0),
                    backgroundColor: window.dashboardConfig.colors.primary,
                    borderRadius: 8
                }]
            },
            options: {
                ...window.dashboardConfig.chartDefaults,
                indexAxis: 'y',
                plugins: {
                    ...window.dashboardConfig.chartDefaults.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = window.dashboardUtils.formatCurrency(context.parsed.x);
                                const count = data[context.dataIndex].service_count;
                                return value + ' (' + count + ' services)';
                            }
                        }
                    }
                }
            }
        });
    },

    createPaymentMethodsChart: function(data) {
        const ctx = document.getElementById('paymentMethodsChart');
        if (!ctx || !data || data.length === 0) return;

        this.destroy('paymentMethods');

        this.instances.paymentMethods = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(d => d.method),
                datasets: [{
                    data: data.map(d => parseFloat(d.total) || 0),
                    backgroundColor: window.dashboardUtils.generateColors(data.length)
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    ...window.dashboardConfig.chartDefaults.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = window.dashboardUtils.formatCurrency(context.parsed);
                                const percentage = parseFloat(data[context.dataIndex].percentage) || 0;
                                const count = data[context.dataIndex].count;
                                return context.label + ': ' + value + 
                                       ' (' + window.dashboardUtils.formatPercentage(percentage) + ', ' + count + ' transactions)';
                            }
                        }
                    }
                }
            }
        });
    }
};
