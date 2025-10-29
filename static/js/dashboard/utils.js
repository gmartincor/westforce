window.dashboardUtils = {
    formatCurrency: function(value) {
        return new Intl.NumberFormat('en-AU', {
            style: 'currency',
            currency: 'AUD'
        }).format(parseFloat(value) || 0);
    },

    formatPercentage: function(value) {
        return parseFloat(value || 0).toFixed(1) + '%';
    },

    generateColors: function(count) {
        const baseColors = [
            '#3B82F6', '#10B981', '#EF4444', '#F59E0B', 
            '#06B6D4', '#8B5CF6', '#EC4899', '#84CC16'
        ];
        
        return baseColors.slice(0, Math.min(count, baseColors.length));
    }
};
