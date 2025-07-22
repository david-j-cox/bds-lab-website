// Cyberpunk 90s Retro Interactive Effects

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all effects
    initPixelAnimations();
    initGlitchEffects();
    initScrollEffects();
    initNavigationEffects();
    initButtonEffects();
});

// Pixel Art Animations
function initPixelAnimations() {
    const pixels = document.querySelectorAll('.pixel');
    
    // Random pixel flicker effect
    setInterval(() => {
        const randomPixel = pixels[Math.floor(Math.random() * pixels.length)];
        if (randomPixel.classList.contains('active')) {
            randomPixel.style.opacity = '0.3';
            setTimeout(() => {
                randomPixel.style.opacity = '1';
            }, 100);
        }
    }, 2000);
    
    // Mouse hover effect on pixel grid
    const pixelGrid = document.querySelector('.pixel-grid');
    if (pixelGrid) {
        pixelGrid.addEventListener('mouseenter', () => {
            pixels.forEach(pixel => {
                if (pixel.classList.contains('active')) {
                    pixel.style.transform = 'scale(1.2)';
                }
            });
        });
        
        pixelGrid.addEventListener('mouseleave', () => {
            pixels.forEach(pixel => {
                pixel.style.transform = 'scale(1)';
            });
        });
    }
}

// Glitch Effects
function initGlitchEffects() {
    const glitchElements = document.querySelectorAll('.glitch');
    
    glitchElements.forEach(element => {
        // Random glitch intensity
        setInterval(() => {
            const intensity = Math.random() * 5;
            element.style.transform = `translate(${intensity}px, ${intensity}px)`;
            setTimeout(() => {
                element.style.transform = 'translate(0, 0)';
            }, 50);
        }, 3000);
    });
}

// Scroll Effects
function initScrollEffects() {
    let ticking = false;
    
    function updateScrollEffects() {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('.cyber-grid');
        
        if (parallax) {
            parallax.style.transform = `translateY(${scrolled * 0.5}px)`;
        }
        
        // Add glow effect to elements as they come into view
        const elements = document.querySelectorAll('.feature-card, .cyber-button');
        elements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const isVisible = rect.top < window.innerHeight && rect.bottom > 0;
            
            if (isVisible) {
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }
        });
        
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateScrollEffects);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick);
    
    // Initial call
    updateScrollEffects();
}

// Navigation Effects
function initNavigationEffects() {
    const navLinks = document.querySelectorAll('.nav-link');
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    
    // Set active state based on current page
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === 'index.html' && href === 'index.html')) {
            link.classList.add('active');
        }
        
        // Add hover sound effect simulation (visual only)
        link.addEventListener('mouseenter', () => {
            link.style.letterSpacing = '3px';
            link.style.transform = 'scale(1.1)';
        });
        
        link.addEventListener('mouseleave', () => {
            link.style.letterSpacing = '1px';
            link.style.transform = 'scale(1)';
        });
    });
}

// Button Effects
function initButtonEffects() {
    const buttons = document.querySelectorAll('.cyber-button');
    
    buttons.forEach(button => {
        // Add click ripple effect
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
        
        // Store original text for restoration
        if (!button.getAttribute('data-original')) {
            button.setAttribute('data-original', button.textContent);
        }
        
        // Add typing effect on hover for regular buttons
        if (!button.classList.contains('small')) {
            button.addEventListener('mouseenter', function() {
                const originalText = this.getAttribute('data-original');
                this.textContent = '';
                let i = 0;
                
                const typeWriter = () => {
                    if (i < originalText.length) {
                        this.textContent += originalText.charAt(i);
                        i++;
                        setTimeout(typeWriter, 50);
                    }
                };
                
                typeWriter();
            });
            
            button.addEventListener('mouseleave', function() {
                const originalText = this.getAttribute('data-original');
                this.textContent = originalText;
            });
                }
    });
}

// Add CSS for ripple effect
const style = document.createElement('style');
style.textContent = `
    .cyber-button {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(0, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .feature-card {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }
    
    .cyber-button {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.6s ease, transform 0.6s ease;
    }
`;
document.head.appendChild(style);

// Terminal-style typing effect for text elements
function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// Add terminal cursor effect to certain elements
function addTerminalCursor(element) {
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    
    const cursor = document.createElement('span');
    cursor.textContent = '|';
    cursor.style.color = 'var(--neon-cyan)';
    cursor.style.animation = 'blink 1s infinite';
    cursor.style.marginLeft = '2px';
    
    element.appendChild(cursor);
}

// Add CSS for blinking cursor
const cursorStyle = document.createElement('style');
cursorStyle.textContent = `
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0; }
    }
`;
document.head.appendChild(cursorStyle);

// Initialize terminal effects on page load
window.addEventListener('load', () => {
    const titleElements = document.querySelectorAll('.cyber-h2, .lab-title');
    titleElements.forEach(element => {
        addTerminalCursor(element);
    });
});

// Add matrix-style rain effect in background
function createMatrixRain() {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '-2';
    canvas.style.opacity = '0.1';
    
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}";
    const matrixArray = matrix.split("");
    
    const fontSize = 10;
    const columns = canvas.width / fontSize;
    const drops = [];
    
    for (let x = 0; x < columns; x++) {
        drops[x] = 1;
    }
    
    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.fillStyle = '#0F0';
        ctx.font = fontSize + 'px monospace';
        
        for (let i = 0; i < drops.length; i++) {
            const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
    }
    
    setInterval(draw, 35);
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Initialize matrix rain effect
createMatrixRain(); 