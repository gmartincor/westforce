const ExpenseDistributionFilter = (() => {
    const fetchData = async (startDate, endDate) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        const url = `/dashboard/api/expense-distribution/?${params.toString()}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching expense distribution data:', error);
            return [];
        }
    };

    const init = (filterSelector) => {
        const filter = TimeRangeFilter.init(filterSelector, async ({ startDate, endDate }) => {
            const data = await fetchData(startDate, endDate);
            DashboardCharts.renderExpenseDistribution(data);
        });

        return filter;
    };

    return { init };
})();

window.ExpenseDistributionFilter = ExpenseDistributionFilter;
