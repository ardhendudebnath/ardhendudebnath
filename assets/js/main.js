// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Mobile menu toggle
const menuBtn = document.querySelector('.menu-btn');
const navLinks = document.querySelector('.nav-links');
const body = document.querySelector('body');

menuBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    navLinks.classList.toggle('active');
    menuBtn.classList.toggle('active');
    body.classList.toggle('no-scroll');
});

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (navLinks.classList.contains('active') && !navLinks.contains(e.target) && !menuBtn.contains(e.target)) {
        navLinks.classList.remove('active');
        menuBtn.classList.remove('active');
        body.classList.remove('no-scroll');
    }
});

// Prevent scrolling when menu is open
document.addEventListener('scroll', () => {
    if (navLinks.classList.contains('active')) {
        window.scrollTo(0, 0);
    }
});

// Smooth scrolling for mobile menu links
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        if (navLinks.classList.contains('active')) {
            navLinks.classList.remove('active');
            menuBtn.classList.remove('active');
            body.classList.remove('no-scroll');
        }
    });
});

// Intersection Observer for scroll animations
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, {
    threshold: 0.1
});

document.querySelectorAll('.project-card, .section-title').forEach((el) => {
    observer.observe(el);
});

document.addEventListener('DOMContentLoaded', function() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progress = entry.target.querySelector('.skill-progress');
                const level = entry.target.dataset.level;
                progress.style.width = `${level}%`;
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.skill-item').forEach(item => {
        observer.observe(item);
    });
});

// Initialize EmailJS with your User ID
emailjs.init('YOUR_USER_ID'); // Replace with your actual User ID

document.querySelector('.contact-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Show loading state
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Sending...';

    const formData = new FormData(this);
    const data = {
        name: formData.get('name'),
        email: formData.get('email'),
        message: formData.get('message')
    };

    // Send email using EmailJS
    emailjs.send('YOUR_SERVICE_ID', 'YOUR_TEMPLATE_ID', data)
        .then(function(response) {
            alert('Message sent successfully!');
            e.target.reset();
        }, function(error) {
            console.error('EmailJS Error:', error);
            alert('Error sending message. Please try again.');
        })
        .finally(() => {
            // Reset button state
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Send Message';
        });
}); 