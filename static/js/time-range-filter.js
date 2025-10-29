const TimeRangeFilter = (() => {
    const PRESETS = {
        all: { months: null },
        month: { months: 1 },
        '3months': { months: 3 },
        '6months': { months: 6 },
        year: { months: 12 }
    };

    const calculateDateRange = (preset) => {
        if (preset === 'all') {
            return { startDate: null, endDate: null };
        }

        const end = new Date();
        const start = new Date();
        start.setMonth(start.getMonth() - PRESETS[preset].months);

        return {
            startDate: start.toISOString().split('T')[0],
            endDate: end.toISOString().split('T')[0]
        };
    };

    const updateButtonStates = (container, activePreset) => {
        container.querySelectorAll('.time-preset-btn').forEach(btn => {
            const isActive = btn.dataset.preset === activePreset;
            btn.classList.toggle('bg-blue-600', isActive);
            btn.classList.toggle('text-white', isActive);
            btn.classList.toggle('border-blue-600', isActive);
            btn.classList.toggle('dark:bg-blue-600', isActive);
            btn.classList.toggle('dark:border-blue-600', isActive);
        });
    };

    const init = (containerSelector, onChange) => {
        const container = document.querySelector(containerSelector);
        if (!container) return null;

        let currentPreset = 'all';

        const handlePresetClick = (preset) => {
            currentPreset = preset;
            const { startDate, endDate } = calculateDateRange(preset);
            
            updateButtonStates(container, preset);
            
            if (onChange) {
                onChange({ startDate, endDate, preset });
            }
        };

        container.querySelectorAll('.time-preset-btn').forEach(btn => {
            btn.addEventListener('click', () => handlePresetClick(btn.dataset.preset));
        });

        handlePresetClick('all');

        return {
            setPreset: handlePresetClick,
            getState: () => ({
                preset: currentPreset,
                ...calculateDateRange(currentPreset)
            })
        };
    };

    return { init };
})();

window.TimeRangeFilter = TimeRangeFilter;
