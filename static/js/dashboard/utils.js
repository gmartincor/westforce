const DashboardUtils = {
    formatCurrency(value) {
        return new Intl.NumberFormat('en-AU', {
            style: 'currency',
            currency: 'AUD'
        }).format(parseFloat(value) || 0);
    },

    formatPercentage(value) {
        return parseFloat(value || 0).toFixed(1) + '%';
    },

    formatNumber(value) {
        return new Intl.NumberFormat('en-AU').format(parseFloat(value) || 0);
    },

    generateColors(count) {
        const palette = [
            '#3B82F6', '#10B981', '#EF4444', '#F59E0B', 
            '#06B6D4', '#8B5CF6', '#EC4899', '#84CC16',
            '#F97316', '#14B8A6', '#6366F1', '#F43F5E'
        ];
        return palette.slice(0, Math.min(count, palette.length));
    },

    createGradient(ctx, color) {
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, color + '40');
        gradient.addColorStop(1, color + '10');
        return gradient;
    },

    parseFloatSafe(value) {
        const parsed = parseFloat(value);
        return isNaN(parsed) ? 0 : parsed;
    }
};

window.DashboardUtils = DashboardUtils;
