window.dashboardCharts = {
    data: null,

    init: function(dashboardData) {
        this.data = dashboardData;
        this.createTemporalChart();
        this.createExpensesChart();
        this.createMarginChart();
        this.createBusinessLinesChart();
        this.setupEventListeners();
    },

    createTemporalChart: function() {
        const ctx = document.getElementById('temporalChart');
        if (!ctx) return;

        window.dashboardUtils.destroyChart('temporal');

        const data = this.data.temporal_data;
        
        window.chartInstances.temporal = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [
                    {
                        label: 'Revenue',
                        data: data.map(d => window.dashboardUtils.parseFloatSafe(d.revenue)),
                        borderColor: window.dashboardConfig.colors.success,
                        backgroundColor: window.dashboardConfig.colors.success + '20',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Expenses',
                        data: data.map(d => window.dashboardUtils.parseFloatSafe(d.expenses)),
                        borderColor: window.dashboardConfig.colors.danger,
                        backgroundColor: window.dashboardConfig.colors.danger + '20',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Profit',
                        data: data.map(d => window.dashboardUtils.parseFloatSafe(d.profit)),
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
                            title: function(context) {
                                return context[0].label;
                            },
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

    createExpensesChart: function() {
        const ctx = document.getElementById('expensesChart');
        if (!ctx) return;

        window.dashboardUtils.destroyChart('expenses');

        const data = this.data.expenses_data;
        if (!data || data.length === 0) return;

        window.chartInstances.expenses = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.categoria),
                datasets: [{
                    data: data.map(d => window.dashboardUtils.parseFloatSafe(d.total)),
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
                                const percentage = data[context.dataIndex].porcentaje;
                                return context.label + ': ' + value + 
                                       ' (' + window.dashboardUtils.formatPercentage(percentage) + ')';
                            }
                        }
                    }
                }
            }
        });
    },

    createMarginChart: function() {
        const ctx = document.getElementById('marginChart');
        if (!ctx) return;

        window.dashboardUtils.destroyChart('margin');

        const data = this.data.temporal_data;
        
        window.chartInstances.margin = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Margin (%)',
                    data: data.map(d => {
                        const revenue = window.dashboardUtils.parseFloatSafe(d.revenue);
                        const profit = window.dashboardUtils.parseFloatSafe(d.profit);
                        return revenue > 0 ? ((profit / revenue) * 100) : 0;
                    }),
                    backgroundColor: data.map(d => {
                        const profit = window.dashboardUtils.parseFloatSafe(d.profit);
                        return profit >= 0 ? window.dashboardConfig.colors.success : window.dashboardConfig.colors.danger;
                    })
                }]
            },
            options: {
                ...window.dashboardConfig.chartDefaults,
                plugins: {
                    ...window.dashboardConfig.chartDefaults.plugins,
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return 'Margin: ' + window.dashboardUtils.formatPercentage(context.parsed.y);
                            }
                        }
                    }
                }
            }
        });
    },

    createBusinessLinesChart: function() {
        const ctx = document.getElementById('businessLinesChart');
        if (!ctx) return;

        window.dashboardUtils.destroyChart('businessLines');

        const data = this.data.business_lines_data;
        if (!data || data.length === 0) return;

        window.chartInstances.businessLines = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.map(d => d.name),
                datasets: [{
                    data: data.map(d => window.dashboardUtils.parseFloatSafe(d.revenue)),
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
                                const percentage = data[context.dataIndex].percentage;
                                return context.label + ': ' + value + 
                                       ' (' + window.dashboardUtils.formatPercentage(percentage) + ')';
                            }
                        }
                    }
                }
            }
        });
    },

    setupEventListeners: function() {
        window.dashboardUtils.setupFilterButtons('expenses', (period) => {
            console.log('Filtering expenses by period:', period);
        });

        window.dashboardUtils.setupFilterButtons('business-lines', (period, level) => {
            this.fetchBusinessLinesData(period, level);
        });
        
        const levelFilter = document.getElementById('business-lines-level-filter');
        if (levelFilter && !levelFilter.hasAttribute('data-initialized')) {
            levelFilter.setAttribute('data-initialized', 'true');
            levelFilter.addEventListener('change', () => {
                const activeButton = document.querySelector('[data-chart="business-lines"].bg-blue-500');
                const period = activeButton ? activeButton.dataset.period : '30';
                this.fetchBusinessLinesData(period, levelFilter.value || null);
            });
        }
    },

    fetchBusinessLinesData: function(period, level) {
        const params = new URLSearchParams();
        if (period && period !== 'all') {
            const days = { '30': 30, '90': 90, '365': 365 }[period];
            if (days) {
                const endDate = new Date();
                const startDate = new Date();
                startDate.setDate(endDate.getDate() - days);
                params.append('start_date', startDate.toISOString().split('T')[0]);
                params.append('end_date', endDate.toISOString().split('T')[0]);
            }
        }
        if (level) {
            params.append('level', level);
        }

        fetch(`/dashboard/api/business-lines/?${params.toString()}`)
            .then(response => response.json())
            .then(data => {
                this.data.business_lines_data = data.business_lines_data;
                this.createBusinessLinesChart();
            })
            .catch(error => console.error('Error fetching business lines data:', error));
    }
};
