const ExpenseDistributionFilter = (() => {
    const fetchData = async (startDate, endDate) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        try {
            const response = await fetch(`/dashboard/api/expense-distribution/?${params}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching expense distribution:', error);
            return [];
        }
    };

    const init = (filterSelector) => {
        return TimeRangeFilter.init(filterSelector, async ({ startDate, endDate }) => {
            const data = await fetchData(startDate, endDate);
            DashboardCharts.renderExpenseDistribution(data);
        });
    };

    return { init };
})();

window.ExpenseDistributionFilter = ExpenseDistributionFilter;
