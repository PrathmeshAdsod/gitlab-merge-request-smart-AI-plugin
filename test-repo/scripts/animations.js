// Enhanced animations for the test page
document.addEventListener('DOMContentLoaded', function() {
    // Create floating bubbles
    function createBubble() {
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.style.left = Math.random() * 100 + 'vw';
        bubble.style.animationDuration = (Math.random() * 3 + 2) + 's';
        bubble.style.opacity = Math.random() * 0.5 + 0.3;
        document.body.appendChild(bubble);
        
        setTimeout(() => {
            document.body.removeChild(bubble);
        }, 5000);
    }
    
    // Create bubbles periodically
    setInterval(createBubble, 800);
    
    // Add ripple effect to clickable elements
    document.addEventListener('click', function(e) {
        const ripple = document.createElement('div');
        ripple.className = 'ripple';
        document.body.appendChild(ripple);
        
        ripple.style.left = e.clientX + 'px';
        ripple.style.top = e.clientY + 'px';
        
        setTimeout(() => {
            document.body.removeChild(ripple);
        }, 600);
    });
    
    // Animate table rows on hover
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8f9fa';
            this.style.transform = 'scale(1.02)';
            this.style.transition = 'all 0.2s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.transform = '';
        });
    });
    
    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add typewriter effect to the main heading
    const heading = document.querySelector('h1');
    if (heading) {
        const text = heading.textContent;
        heading.textContent = '';
        let i = 0;
        
        const typeWriter = () => {
            if (i < text.length) {
                heading.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            }
        };
        
        setTimeout(typeWriter, 500);
    }
});

// Progressive loading simulation
window.addEventListener('load', function() {
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(20px)';
        section.style.transition = 'all 0.6s ease';
        
        setTimeout(() => {
            section.style.opacity = '1';
            section.style.transform = 'translateY(0)';
        }, index * 200 + 1000);
    });
});