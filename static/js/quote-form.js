class QuoteFormManager {
  constructor() {
    this.currentStep = 1;
    this.totalSteps = 6;
    this.formData = {
      bedrooms: '',
      fromSuburb: '',
      toSuburb: '',
      moveDate: '',
      flexibleDates: false,
      startTime: '',
      additionalStop: false,
      largeItems: false,
      packingService: 'not-required',
      storage: false,
      firstName: '',
      lastName: '',
      mobile: '',
      email: '',
      comments: '',
      hearAbout: '',
      newsletter: false
    };
    this.init();
  }

  init() {
    this.bindEvents();
    this.bindInputListeners();
    this.updateProgress();
  }

  bindEvents() {
    document.querySelectorAll('[data-next-step]').forEach(btn => {
      btn.addEventListener('click', () => this.nextStep());
    });

    document.querySelectorAll('[data-prev-step]').forEach(btn => {
      btn.addEventListener('click', () => this.prevStep());
    });

    document.querySelectorAll('[data-bedroom]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const button = e.currentTarget;
        this.selectBedroom(button.dataset.bedroom);
      });
    });

    document.querySelectorAll('[data-packing]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const button = e.currentTarget;
        this.selectPacking(button.dataset.packing);
      });
    });

    const form = document.getElementById('quote-form');
    if (form) {
      form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
  }

  bindInputListeners() {
    const inputMappings = [
      { id: 'from-suburb', key: 'fromSuburb' },
      { id: 'to-suburb', key: 'toSuburb' },
      { id: 'move-date', key: 'moveDate' },
      { id: 'start-time', key: 'startTime' },
      { id: 'first-name', key: 'firstName' },
      { id: 'last-name', key: 'lastName' },
      { id: 'mobile', key: 'mobile' },
      { id: 'email', key: 'email' },
      { id: 'comments', key: 'comments' },
      { id: 'hear-about', key: 'hearAbout' }
    ];

    inputMappings.forEach(({ id, key }) => {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener('input', (e) => {
          this.formData[key] = e.target.value;
        });
      }
    });

    const checkboxMappings = [
      { name: 'flexibleDates', key: 'flexibleDates' },
      { name: 'additionalStop', key: 'additionalStop' },
      { name: 'newsletter', key: 'newsletter' }
    ];

    checkboxMappings.forEach(({ name, key }) => {
      const element = document.querySelector(`input[name="${name}"]`);
      if (element) {
        element.addEventListener('change', (e) => {
          this.formData[key] = e.target.checked;
        });
      }
    });

    const radioGroups = [
      { name: 'largeItems', key: 'largeItems' },
      { name: 'storage', key: 'storage' }
    ];

    radioGroups.forEach(({ name, key }) => {
      document.querySelectorAll(`input[name="${name}"]`).forEach(radio => {
        radio.addEventListener('change', (e) => {
          this.formData[key] = e.target.value === 'yes';
        });
      });
    });
  }

  selectOption(selector, value, dataKey) {
    if (!value) return;
    
    this.formData[dataKey] = value;
    
    const selectedClasses = ['selected', 'bg-primary-600', 'text-white', 'border-primary-600'];
    const defaultClasses = ['bg-white', 'text-gray-700', 'border-gray-300'];
    
    document.querySelectorAll(`[${selector}]`).forEach(btn => {
      btn.classList.remove(...selectedClasses);
      btn.classList.add(...defaultClasses);
    });
    
    const selectedBtn = document.querySelector(`[${selector}="${value}"]`);
    if (selectedBtn) {
      selectedBtn.classList.remove(...defaultClasses);
      selectedBtn.classList.add(...selectedClasses);
    }
  }

  selectBedroom(value) {
    this.selectOption('data-bedroom', value, 'bedrooms');
  }

  selectPacking(value) {
    this.selectOption('data-packing', value, 'packingService');
  }

  validateStep(step) {
    const validations = {
      1: () => this.formData.bedrooms !== '',
      2: () => {
        const fromSuburb = document.getElementById('from-suburb')?.value.trim();
        const toSuburb = document.getElementById('to-suburb')?.value.trim();
        const moveDate = document.getElementById('move-date')?.value;
        const startTime = document.getElementById('start-time')?.value;
        return fromSuburb && toSuburb && moveDate && startTime;
      },
      3: () => true,
      4: () => true,
      5: () => true,
      6: () => {
        const firstName = document.getElementById('first-name')?.value.trim();
        const lastName = document.getElementById('last-name')?.value.trim();
        const mobile = document.getElementById('mobile')?.value.trim();
        const email = document.getElementById('email')?.value.trim();
        return firstName && lastName && mobile && email;
      }
    };

    return validations[step] ? validations[step]() : true;
  }

  nextStep() {
    if (!this.validateStep(this.currentStep)) {
      this.showValidationErrors(this.currentStep);
      return;
    }

    if (this.currentStep < this.totalSteps) {
      this.hideStep(this.currentStep);
      this.currentStep++;
      this.showStep(this.currentStep);
      this.updateProgress();
    }
  }

  showValidationErrors(step) {
    const errorMessages = {
      1: 'Please select the number of bedrooms',
      2: 'Please fill in all move details (suburbs, date, and time)',
      6: 'Please fill in your contact information'
    };

    const message = errorMessages[step] || 'Please fill in all required fields';
    this.showError(message);
  }

  prevStep() {
    if (this.currentStep > 1) {
      this.hideStep(this.currentStep);
      this.currentStep--;
      this.showStep(this.currentStep);
      this.updateProgress();
    }
  }

  showStep(step) {
    const stepElement = document.getElementById(`step-${step}`);
    if (stepElement) {
      stepElement.classList.remove('hidden');
      stepElement.classList.add('animate-fade-in-up');
      this.scrollToTop();
    }
  }

  hideStep(step) {
    const stepElement = document.getElementById(`step-${step}`);
    if (stepElement) {
      stepElement.classList.add('hidden');
    }
  }

  updateProgress() {
    const progress = Math.round((this.currentStep / this.totalSteps) * 100);
    
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
    }

    const progressPercent = document.getElementById('progress-percent');
    if (progressPercent) {
      progressPercent.textContent = progress;
    }

    const stepText = document.getElementById('step-text');
    if (stepText) {
      stepText.textContent = `Step ${this.currentStep} of ${this.totalSteps}`;
    }
  }

  scrollToTop() {
    const formContainer = document.getElementById('quote-form-container');
    if (formContainer) {
      formContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in-up';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);

    setTimeout(() => {
      errorDiv.remove();
    }, 3000);
  }

  showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-accent-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in-up';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);

    setTimeout(() => {
      successDiv.remove();
    }, 3000);
  }

  collectFormData() {
    const fieldMappings = [
      { id: 'from-suburb', key: 'fromSuburb' },
      { id: 'to-suburb', key: 'toSuburb' },
      { id: 'move-date', key: 'moveDate' },
      { id: 'start-time', key: 'startTime' },
      { id: 'first-name', key: 'firstName' },
      { id: 'last-name', key: 'lastName' },
      { id: 'mobile', key: 'mobile' },
      { id: 'email', key: 'email' },
      { id: 'comments', key: 'comments' },
      { id: 'hear-about', key: 'hearAbout' }
    ];

    fieldMappings.forEach(({ id, key }) => {
      const element = document.getElementById(id);
      if (element) {
        this.formData[key] = element.value;
      }
    });

    const checkboxMappings = [
      { name: 'flexibleDates', key: 'flexibleDates' },
      { name: 'additionalStop', key: 'additionalStop' },
      { name: 'newsletter', key: 'newsletter' }
    ];

    checkboxMappings.forEach(({ name, key }) => {
      const element = document.querySelector(`input[name="${name}"]`);
      if (element) {
        this.formData[key] = element.checked;
      }
    });

    const largeItemsRadio = document.querySelector('input[name="largeItems"]:checked');
    if (largeItemsRadio) {
      this.formData.largeItems = largeItemsRadio.value === 'yes';
    }

    const storageRadio = document.querySelector('input[name="storage"]:checked');
    if (storageRadio) {
      this.formData.storage = storageRadio.value === 'yes';
    }
  }

  async handleSubmit(e) {
    e.preventDefault();

    if (!this.validateStep(6)) {
      this.showError('Please fill in all required fields');
      return;
    }

    this.collectFormData();

    const submitBtn = document.getElementById('submit-quote');
    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';

    try {
      const csrfToken = this.getCSRFToken();
      
      if (!csrfToken) {
        throw new Error('CSRF token not found');
      }

      const response = await fetch('/quote/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(this.formData)
      });

      if (response.ok) {
        const estimatedValue = this.calculateEstimatedValue();
        
        if (typeof window.trackQuoteRequest === 'function') {
          window.trackQuoteRequest({
            estimatedValue: estimatedValue,
            transactionId: `QUOTE-${Date.now()}`,
            bedrooms: this.formData.bedrooms,
            serviceType: this.formData.packingService
          });
        }

        this.showSuccess('Quote request sent successfully! We\'ll contact you within 30 minutes.');
        
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        throw new Error('Failed to submit form');
      }
    } catch (error) {
      this.showError('Failed to submit quote request. Please try again.');
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  }

  calculateEstimatedValue() {
    let baseValue = 0;
    
    switch(this.formData.bedrooms) {
      case '1': baseValue = 80; break;
      case '2': baseValue = 120; break;
      case '3': baseValue = 150; break;
      case '4': baseValue = 200; break;
      case '5+': baseValue = 250; break;
      default: baseValue = 100;
    }
    
    if (this.formData.packingService === 'full-pack') baseValue += 50;
    if (this.formData.packingService === 'partial-pack') baseValue += 25;
    if (this.formData.storage) baseValue += 30;
    if (this.formData.largeItems) baseValue += 20;
    
    return baseValue;
  }

  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
      return metaTag.getAttribute('content');
    }
    
    const cookieValue = this.getCookie('csrftoken');
    if (cookieValue) {
      return cookieValue;
    }
    
    const hiddenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (hiddenInput) {
      return hiddenInput.value;
    }
    
    return null;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new QuoteFormManager();
});
