const ServiceRevenueFilter = (() => {
    const fetchData = async (startDate, endDate) => {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        try {
            const response = await fetch(`/dashboard/api/service-revenue/?${params}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('Error fetching service revenue:', error);
            return [];
        }
    };

    const init = (filterSelector) => {
        return TimeRangeFilter.init(filterSelector, async ({ startDate, endDate }) => {
            const data = await fetchData(startDate, endDate);
            DashboardCharts.renderServiceRevenue(data);
        });
    };

    return { init };
})();

window.ServiceRevenueFilter = ServiceRevenueFilter;
