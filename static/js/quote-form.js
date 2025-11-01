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
      btn.addEventListener('click', (e) => this.selectBedroom(e.target.dataset.bedroom));
    });

    document.querySelectorAll('[data-packing]').forEach(btn => {
      btn.addEventListener('click', (e) => this.selectPacking(e.target.dataset.packing));
    });

    const form = document.getElementById('quote-form');
    if (form) {
      form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
  }

  selectBedroom(value) {
    this.formData.bedrooms = value;
    document.querySelectorAll('[data-bedroom]').forEach(btn => {
      btn.classList.remove('selected', 'bg-primary-600', 'text-white', 'border-primary-600');
      btn.classList.add('bg-white', 'text-gray-700', 'border-gray-300');
    });
    const selectedBtn = document.querySelector(`[data-bedroom="${value}"]`);
    selectedBtn.classList.remove('bg-white', 'text-gray-700', 'border-gray-300');
    selectedBtn.classList.add('selected', 'bg-primary-600', 'text-white', 'border-primary-600');
  }

  selectPacking(value) {
    this.formData.packingService = value;
    document.querySelectorAll('[data-packing]').forEach(btn => {
      btn.classList.remove('selected', 'bg-primary-600', 'text-white', 'border-primary-600');
      btn.classList.add('bg-white', 'text-gray-700', 'border-gray-300');
    });
    const selectedBtn = document.querySelector(`[data-packing="${value}"]`);
    selectedBtn.classList.remove('bg-white', 'text-gray-700', 'border-gray-300');
    selectedBtn.classList.add('selected', 'bg-primary-600', 'text-white', 'border-primary-600');
  }

  validateStep(step) {
    switch(step) {
      case 1:
        return this.formData.bedrooms !== '';
      case 2:
        return this.formData.fromSuburb && this.formData.toSuburb && this.formData.moveDate && this.formData.startTime;
      case 3:
        return true;
      case 4:
        return true;
      case 5:
        return true;
      case 6:
        return this.formData.firstName && this.formData.lastName && this.formData.mobile && this.formData.email;
      default:
        return true;
    }
  }

  nextStep() {
    if (!this.validateStep(this.currentStep)) {
      this.showError('Please fill in all required fields');
      return;
    }

    if (this.currentStep < this.totalSteps) {
      this.hideStep(this.currentStep);
      this.currentStep++;
      this.showStep(this.currentStep);
      this.updateProgress();
    }
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
    const progress = (this.currentStep / this.totalSteps) * 100;
    const progressBar = document.getElementById('progress-bar');
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
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
    const form = document.getElementById('quote-form');
    const formData = new FormData(form);
    
    for (let [key, value] of formData.entries()) {
      if (key in this.formData) {
        this.formData[key] = value;
      }
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
      const response = await fetch('/quote/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': this.getCookie('csrftoken')
        },
        body: JSON.stringify(this.formData)
      });

      if (response.ok) {
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
}

document.addEventListener('DOMContentLoaded', () => {
  new QuoteFormManager();
});
