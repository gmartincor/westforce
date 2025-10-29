class ChartFactory {
    constructor(config = {}) {
        this.defaultConfig = config;
        this.instances = {};
    }

    create(type, elementId, data, options = {}) {
        const ctx = document.getElementById(elementId);
        if (!ctx || !data) return null;

        this.destroy(elementId);

        const config = this._buildConfig(type, data, options);
        this.instances[elementId] = new Chart(ctx, config);
        
        return this.instances[elementId];
    }

    destroy(elementId) {
        if (this.instances[elementId]) {
            this.instances[elementId].destroy();
            delete this.instances[elementId];
        }
    }

    destroyAll() {
        Object.keys(this.instances).forEach(id => this.destroy(id));
    }

    _buildConfig(type, data, options) {
        const builders = {
            'line': this._buildLineConfig.bind(this),
            'bar': this._buildBarConfig.bind(this),
            'horizontalBar': this._buildHorizontalBarConfig.bind(this),
            'doughnut': this._buildDoughnutConfig.bind(this),
            'pie': this._buildPieConfig.bind(this),
        };

        return builders[type] ? builders[type](data, options) : null;
    }

    _buildLineConfig(data, options) {
        return {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                    },
                    tooltip: options.tooltip || {}
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#E5E7EB'
                        }
                    },
                    x: {
                        grid: {
                            color: '#E5E7EB'
                        }
                    }
                },
                ...options
            }
        };
    }

    _buildBarConfig(data, options) {
        return {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: options.showLegend !== false,
                        position: 'bottom',
                    },
                    tooltip: options.tooltip || {}
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#E5E7EB'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                ...options
            }
        };
    }

    _buildHorizontalBarConfig(data, options) {
        return {
            type: 'bar',
            data: data,
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                    tooltip: options.tooltip || {}
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: {
                            color: '#E5E7EB'
                        }
                    },
                    y: {
                        grid: {
                            display: false
                        }
                    }
                },
                ...options
            }
        };
    }

    _buildDoughnutConfig(data, options) {
        return {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                    },
                    tooltip: options.tooltip || {}
                },
                ...options
            }
        };
    }

    _buildPieConfig(data, options) {
        return {
            type: 'pie',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                    },
                    tooltip: options.tooltip || {}
                },
                ...options
            }
        };
    }
}

window.ChartFactory = ChartFactory;
