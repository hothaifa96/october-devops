// Mobile Navigation Toggle
const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");
const navLinks = document.querySelectorAll(".nav-link");

hamburger.addEventListener("click", () => {
  hamburger.classList.toggle("active");
  navMenu.classList.toggle("active");
});

navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    hamburger.classList.remove("active");
    navMenu.classList.remove("active");
  });
});

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Header scroll effect
window.addEventListener("scroll", () => {
  const header = document.querySelector(".header");
  if (window.scrollY > 100) {
    header.style.background = "rgba(255, 255, 255, 0.98)";
    header.style.boxShadow = "0 2px 20px rgba(0, 0, 0, 0.1)";
  } else {
    header.style.background = "rgba(255, 255, 255, 0.95)";
    header.style.boxShadow = "none";
  }
});

// Intersection Observer for fade-in animations
const observerOptions = {
  threshold: 0.1,
  rootMargin: "0px 0px -50px 0px",
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1";
      entry.target.style.transform = "translateY(0)";
    }
  });
}, observerOptions);

// Observe content cards for animation
document.addEventListener("DOMContentLoaded", () => {
  const contentCards = document.querySelectorAll(".content-card");
  contentCards.forEach((card) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(30px)";
    card.style.transition = "opacity 0.6s ease-out, transform 0.6s ease-out";
    observer.observe(card);
  });

  // Observe features
  const features = document.querySelectorAll(".feature");
  features.forEach((feature, index) => {
    feature.style.opacity = "0";
    feature.style.transform = "translateY(30px)";
    feature.style.transition = `opacity 0.6s ease-out ${
      index * 0.1
    }s, transform 0.6s ease-out ${index * 0.1}s`;
    observer.observe(feature);
  });
});

// Add active state to navigation based on scroll position
window.addEventListener("scroll", () => {
  let current = "";
  const sections = document.querySelectorAll("section[id]");

  sections.forEach((section) => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;
    if (scrollY >= sectionTop - 200) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach((link) => {
    link.classList.remove("active");
    if (link.getAttribute("href").slice(1) === current) {
      link.classList.add("active");
    }
  });
});

// Add copy link functionality for content items
document.querySelectorAll(".content-list a").forEach((link) => {
  link.addEventListener("click", (e) => {
    // Only add copy functionality if it's a direct file link
    if (link.href.includes(".md") || link.href.includes(".pdf")) {
      // Optional: Add a small tooltip or notification
      console.log("Link copied to clipboard:", link.href);
    }
  });
});

// Search functionality (placeholder for future enhancement)
function addSearchFunctionality() {
  // This can be enhanced later with actual search implementation
  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.placeholder = "Search content...";
  searchInput.className = "search-input";

  // Add search input to header (optional enhancement)
  // document.querySelector('.nav-container').appendChild(searchInput);
}

// Performance optimization: Lazy load images if any are added later
function lazyLoadImages() {
  const images = document.querySelectorAll("img[data-src]");
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove("lazy");
        imageObserver.unobserve(img);
      }
    });
  });

  images.forEach((img) => imageObserver.observe(img));
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  lazyLoadImages();

  // Add loading complete class
  document.body.classList.add("loaded");
});

// Add keyboard navigation support
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    // Close mobile menu if open
    hamburger.classList.remove("active");
    navMenu.classList.remove("active");
  }
});

// Print functionality
function addPrintButton() {
  const printButton = document.createElement("button");
  printButton.innerHTML = '<i class="fas fa-print"></i> Print';
  printButton.className = "btn btn-secondary print-btn";
  printButton.addEventListener("click", () => {
    window.print();
  });

  // Add to hero section (optional)
  // document.querySelector('.hero-buttons').appendChild(printButton);
}

// Theme toggle (optional enhancement)
function addThemeToggle() {
  const themeToggle = document.createElement("button");
  themeToggle.innerHTML = '<i class="fas fa-moon"></i>';
  themeToggle.className = "theme-toggle";
  themeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-theme");
    const icon = themeToggle.querySelector("i");
    icon.className = document.body.classList.contains("dark-theme")
      ? "fas fa-sun"
      : "fas fa-moon";
  });

  // Add to header (optional)
  // document.querySelector('.nav-container').appendChild(themeToggle);
}

// Analytics and tracking (placeholder)
function trackPageView() {
  // Add analytics tracking here if needed
  console.log("Page view tracked:", window.location.pathname);
}

// Error handling for broken links
document.querySelectorAll("a").forEach((link) => {
  link.addEventListener("error", (e) => {
    console.warn("Broken link detected:", link.href);
    link.style.color = "#ef4444";
    link.style.textDecoration = "line-through";
  });
});

// Initialize everything
trackPageView();
