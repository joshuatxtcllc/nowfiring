/**
 * Houston Jobs Hub - Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile menu toggle
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const mainNav = document.querySelector('.main-nav');
  const authButtons = document.querySelector('.auth-buttons');
  
  if (mobileMenuToggle) {
    mobileMenuToggle.addEventListener('click', () => {
      mobileMenuToggle.classList.toggle('active');
      
      // If mobile nav is not displayed yet, create and show it
      if (!document.querySelector('.mobile-nav')) {
        const mobileNav = document.createElement('div');
        mobileNav.className = 'mobile-nav';
        
        // Clone the navigation and auth buttons
        const navClone = mainNav.cloneNode(true);
        const authClone = authButtons.cloneNode(true);
        
        mobileNav.appendChild(navClone);
        mobileNav.appendChild(authClone);
        
        // Insert after header
        const header = document.querySelector('.header');
        header.parentNode.insertBefore(mobileNav, header.nextSibling);
        
        // Add animation
        setTimeout(() => {
          mobileNav.style.height = mobileNav.scrollHeight + 'px';
        }, 10);
      } else {
        // Toggle existing mobile nav
        const mobileNav = document.querySelector('.mobile-nav');
        if (mobileNav.style.height) {
          mobileNav.style.height = null;
          setTimeout(() => {
            mobileNav.remove();
          }, 300); // match transition time
        } else {
          mobileNav.style.height = mobileNav.scrollHeight + 'px';
        }
      }
    });
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth'
        });
      }
    });
  });

  // Form validation
  const forms = document.querySelectorAll('form');
  forms.forEach(form => {
    form.addEventListener('submit', function(event) {
      let isValid = true;
      
      // Validate required fields
      const requiredFields = form.querySelectorAll('[required]');
      requiredFields.forEach(field => {
        if (!field.value.trim()) {
          isValid = false;
          highlightInvalidField(field);
        } else {
          removeInvalidHighlight(field);
        }
      });
      
      // Validate email fields
      const emailFields = form.querySelectorAll('input[type="email"]');
      emailFields.forEach(field => {
        if (field.value.trim() && !isValidEmail(field.value)) {
          isValid = false;
          highlightInvalidField(field);
        }
      });
      
      if (!isValid) {
        event.preventDefault();
        // Scroll to the first invalid field
        const firstInvalidField = form.querySelector('.invalid');
        if (firstInvalidField) {
          firstInvalidField.focus();
        }
      }
    });
  });

  // Function to validate email format
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  // Function to highlight invalid field
  function highlightInvalidField(field) {
    field.classList.add('invalid');
    
    // Add error message if not already present
    let errorMessage = field.nextElementSibling;
    if (!errorMessage || !errorMessage.classList.contains('error-message')) {
      errorMessage = document.createElement('div');
      errorMessage.className = 'error-message';
      errorMessage.textContent = field.dataset.errorMessage || 'This field is required';
      field.parentNode.insertBefore(errorMessage, field.nextSibling);
    }
  }

  // Function to remove invalid highlight
  function removeInvalidHighlight(field) {
    field.classList.remove('invalid');
    
    // Remove error message if present
    const errorMessage = field.nextElementSibling;
    if (errorMessage && errorMessage.classList.contains('error-message')) {
      errorMessage.remove();
    }
  }

  // Remove invalid highlights on input
  document.addEventListener('input', function(event) {
    if (event.target.classList.contains('invalid')) {
      if (event.target.value.trim()) {
        removeInvalidHighlight(event.target);
      }
    }
  });

  // Initialize any sliders/carousels
  initializeTestimonialCarousel();
});

/**
 * Initialize the testimonials carousel using simple auto-scrolling
 */
function initializeTestimonialCarousel() {
  const carousel = document.querySelector('.testimonials-carousel');
  if (!carousel || carousel.children.length <= 1) return;

  let currentIndex = 0;
  const testimonials = Array.from(carousel.children);
  const totalTestimonials = testimonials.length;
  
  // Hide all except the first one
  testimonials.forEach((testimonial, index) => {
    if (index > 0) {
      testimonial.style.display = 'none';
    }
  });
  
  // Create navigation dots
  const dotsContainer = document.createElement('div');
  dotsContainer.className = 'carousel-dots';
  
  testimonials.forEach((_, index) => {
    const dot = document.createElement('button');
    dot.className = 'carousel-dot';
    dot.setAttribute('aria-label', `Go to testimonial ${index + 1}`);
    if (index === 0) {
      dot.classList.add('active');
    }
    
    dot.addEventListener('click', () => {
      goToTestimonial(index);
    });
    
    dotsContainer.appendChild(dot);
  });
  
  carousel.parentNode.appendChild(dotsContainer);
  
  // Auto-rotate every 5 seconds
  const autoRotate = setInterval(() => {
    goToTestimonial((currentIndex + 1) % totalTestimonials);
  }, 5000);
  
  // Stop rotation on mouse hover
  carousel.addEventListener('mouseenter', () => {
    clearInterval(autoRotate);
  });
  
  // Resume rotation on mouse leave
  carousel.addEventListener('mouseleave', () => {
    clearInterval(autoRotate);
    autoRotate = setInterval(() => {
      goToTestimonial((currentIndex + 1) % totalTestimonials);
    }, 5000);
  });
  
  // Function to transition to specific testimonial
  function goToTestimonial(index) {
    testimonials[currentIndex].style.display = 'none';
    testimonials[index].style.display = 'block';
    
    // Update active dot
    const dots = dotsContainer.querySelectorAll('.carousel-dot');
    dots[currentIndex].classList.remove('active');
    dots[index].classList.add('active');
    
    currentIndex = index;
  }
}

/**
 * Directory submission functionality
 * This will need to be expanded with proper API calls
 */
class DirectorySubmitter {
  constructor() {
    this.businessData = {};
    this.directories = [];
    this.results = {
      successful: [],
      failed: []
    };
  }
  
  /**
   * Initialize the submitter with business data
   * @param {Object} businessData - The business information to submit
   */
  init(businessData) {
    this.businessData = businessData;
    
    // In a real implementation, you would fetch the directory list from an API
    this.directories = [
      {
        name: 'Houston Business Directory',
        url: 'https://houstonbiz.com/submit-listing',
        apiEndpoint: '/api/submit/houstonbiz'
      },
      {
        name: 'TX Local',
        url: 'https://txlocal.com/add-business',
        apiEndpoint: '/api/submit/txlocal'
      },
      // Additional directories would be loaded here
    ];
    
    return this;
  }
  
  /**
   * Submit the business to all directories
   * @returns {Promise} A promise that resolves with the results
   */
  async submitToAll() {
    const submissionPromises = this.directories.map(directory => 
      this.submitToDirectory(directory)
    );
    
    await Promise.allSettled(submissionPromises);
    
    return this.results;
  }
  
  /**
   * Submit to a specific directory
   * @param {Object} directory - The directory to submit to
   * @returns {Promise} A promise that resolves on completion
   */
  async submitToDirectory(directory) {
    try {
      console.log(`Submitting to ${directory.name}...`);
      
      // In a real implementation, this would be an actual API call
      // using fetch or axios
      const response = await this.mockApiCall(directory.apiEndpoint, this.businessData);
      
      if (response.success) {
        this.results.successful.push({
          name: directory.name,
          message: response.message
        });
      } else {
        this.results.failed.push({
          name: directory.name,
          error: response.message
        });
      }
      
      return response;
    } catch (error) {
      this.results.failed.push({
        name: directory.name,
        error: error.message
      });
      
      return {
        success: false,
        message: error.message
      };
    }
  }
  
  /**
   * Mock API call for demonstration purposes
   * @param {string} endpoint - The API endpoint
   * @param {Object} data - The data to send
   * @returns {Promise} A promise that resolves with the mock response
   */
  mockApiCall(endpoint, data) {
    return new Promise((resolve) => {
      // Simulate network delay
      setTimeout(() => {
        // 80% success rate for demonstration
        const success = Math.random() > 0.2;
        
        if (success) {
          resolve({
            success: true,
            message: 'Business successfully submitted'
          });
        } else {
          resolve({
            success: false,
            message: 'Error submitting business: Form validation failed'
          });
        }
      }, 1000);
    });
  }
  
  /**
   * Generate a report of the submission results
   * @returns {Object} The submission results
   */
  generateReport() {
    return {
      total: this.directories.length,
      successful: this.results.successful.length,
      failed: this.results.failed.length,
      successDetails: this.results.successful,
      failureDetails: this.results.failed
    };
  }
}

// Global instance for use in HTML event handlers
window.directorySubmitter = new DirectorySubmitter();
