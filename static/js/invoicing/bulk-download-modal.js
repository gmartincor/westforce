class BulkDownloadModal {
    constructor(config) {
        this.modalId = config.modalId;
        this.formId = config.formId;
        this.previewUrl = config.previewUrl;
        this.downloadUrlMonthly = config.downloadUrlMonthly;
        this.downloadUrlQuarterly = config.downloadUrlQuarterly;
        this.currentPeriodType = null;
        
        this.elements = {
            modal: null,
            form: null,
            modalTitle: null,
            monthSelect: null,
            quarterSelect: null,
            previewLoader: null,
            previewContent: null,
            downloadButton: null
        };
        
        this.init();
    }

    init() {
        this.cacheElements();
        this.bindEvents();
    }

    cacheElements() {
        this.elements.modal = document.getElementById(this.modalId);
        this.elements.form = document.getElementById(this.formId);
        this.elements.modalTitle = document.getElementById('modalTitle');
        this.elements.monthSelect = document.getElementById('monthSelect');
        this.elements.quarterSelect = document.getElementById('quarterSelect');
        this.elements.previewLoader = document.getElementById('previewLoader');
        this.elements.previewContent = document.getElementById('previewContent');
        this.elements.downloadButton = document.getElementById('downloadButton');
    }

    bindEvents() {
        if (this.elements.form) {
            this.elements.form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }
    }

    show(periodType) {
        this.currentPeriodType = periodType;
        
        const titleText = periodType === 'monthly' ? 'Monthly Bulk Download' : 'Quarterly Bulk Download';
        this.elements.modalTitle.textContent = titleText;
        
        this.elements.monthSelect.classList.toggle('hidden', periodType !== 'monthly');
        this.elements.quarterSelect.classList.toggle('hidden', periodType !== 'quarterly');
        
        this.elements.modal.classList.remove('hidden');
        this.elements.modal.classList.add('flex');
        
        this.updatePreview();
    }

    close() {
        this.elements.modal.classList.add('hidden');
        this.elements.modal.classList.remove('flex');
        this.resetPreview();
    }

    async updatePreview() {
        const formData = new FormData(this.elements.form);
        const params = new URLSearchParams();
        
        params.append('type', this.currentPeriodType);
        params.append('year', formData.get('year'));
        
        if (this.currentPeriodType === 'monthly') {
            params.append('month', formData.get('month'));
        } else {
            params.append('quarter', formData.get('quarter'));
        }
        
        const status = formData.get('status');
        if (status) {
            params.append('status', status);
        }
        
        this.showLoader();
        
        try {
            const response = await fetch(`${this.previewUrl}?${params.toString()}`);
            const data = await response.json();
            
            if (data.success) {
                this.displayPreview(data);
            } else {
                this.displayError(data.error || 'Failed to load preview');
            }
        } catch (error) {
            this.displayError('Error loading preview: ' + error.message);
        }
    }

    showLoader() {
        this.elements.previewLoader.classList.remove('hidden');
        this.elements.previewContent.classList.add('hidden');
        this.elements.downloadButton.disabled = true;
    }

    displayPreview(data) {
        this.elements.previewLoader.classList.add('hidden');
        this.elements.previewContent.classList.remove('hidden');
        
        const hasInvoices = data.count > 0;
        this.elements.downloadButton.disabled = !hasInvoices;
        
        if (hasInvoices) {
            this.elements.previewContent.innerHTML = `
                <div class="space-y-2">
                    <p class="text-sm font-medium text-gray-900 dark:text-white">
                        ${data.period_name}
                    </p>
                    <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                        <span>Invoices found:</span>
                        <span class="font-semibold text-gray-900 dark:text-white">${data.count}</span>
                    </div>
                    <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400">
                        <span>Total amount:</span>
                        <span class="font-semibold text-gray-900 dark:text-white">$${parseFloat(data.total_amount).toFixed(2)} AUD</span>
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-500 mt-2">
                        ${data.date_range}
                    </div>
                </div>
            `;
        } else {
            this.elements.previewContent.innerHTML = `
                <p class="text-sm text-gray-500 dark:text-gray-400">
                    No invoices found for this period
                </p>
            `;
        }
    }

    displayError(message) {
        this.elements.previewLoader.classList.add('hidden');
        this.elements.previewContent.classList.remove('hidden');
        this.elements.downloadButton.disabled = true;
        
        this.elements.previewContent.innerHTML = `
            <p class="text-sm text-red-600 dark:text-red-400">
                ${message}
            </p>
        `;
    }

    resetPreview() {
        this.elements.previewContent.innerHTML = `
            <p class="text-sm text-gray-600 dark:text-gray-400">
                Select a period to see available invoices
            </p>
        `;
        this.elements.downloadButton.disabled = true;
    }

    handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(this.elements.form);
        const params = new URLSearchParams();
        
        params.append('year', formData.get('year'));
        
        if (this.currentPeriodType === 'monthly') {
            params.append('month', formData.get('month'));
            this.elements.form.action = this.downloadUrlMonthly;
        } else {
            params.append('quarter', formData.get('quarter'));
            this.elements.form.action = this.downloadUrlQuarterly;
        }
        
        const status = formData.get('status');
        if (status) {
            params.append('status', status);
        }
        
        window.location.href = `${this.elements.form.action}?${params.toString()}`;
        
        this.close();
    }
}

let bulkDownloadModalInstance = null;

function initializeBulkDownloadModal(config) {
    bulkDownloadModalInstance = new BulkDownloadModal(config);
}

function showBulkDownloadModal(periodType) {
    if (bulkDownloadModalInstance) {
        bulkDownloadModalInstance.show(periodType);
    }
}

function closeBulkDownloadModal() {
    if (bulkDownloadModalInstance) {
        bulkDownloadModalInstance.close();
    }
}

function updatePreview() {
    if (bulkDownloadModalInstance) {
        bulkDownloadModalInstance.updatePreview();
    }
}
