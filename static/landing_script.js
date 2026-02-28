const root = document.documentElement;
const panel = document.getElementById('accessibilityPanel');
const panelToggle = document.getElementById('togglePanel');
const closePanel = document.getElementById('closePanel');
const decreaseBtn = document.getElementById('fontDecrease');
const resetBtn = document.getElementById('fontReset');
const increaseBtn = document.getElementById('fontIncrease');

panelToggle.addEventListener('click', () => {
    panel.classList.toggle('hidden');
});

closePanel.addEventListener('click', () => {
    accessibilityPanel.classList.add('hidden');
});

document.addEventListener('click', function (event) {
    const isClickInsidePanel = accessibilityPanel.contains(event.target);
    const isClickToggleButton = togglePanel.contains(event.target);

    if (!isClickInsidePanel && !isClickToggleButton) {
        accessibilityPanel.classList.add('hidden');
    }
});

function setupToggle(buttonId, classTarget, className) {
    const button = document.getElementById(buttonId);
    const thumb = button.querySelector('span');

    button.addEventListener('click', () => {
        const isActive = classTarget.classList.toggle(className);
        button.classList.toggle('bg-blue-600', isActive);
        button.classList.toggle('bg-gray-300', !isActive);
        thumb.classList.toggle('translate-x-6', isActive);
        thumb.classList.toggle('translate-x-1', !isActive);
    });
}

setupToggle('toggleDyslexic', root, 'dyslexic-font');
setupToggle('toggleMonochrome', root, 'monochrome');
// setupToggle('toggleRuler', root, 'reading-ruler');
setupToggle('toggleCursor', root, 'big-cursor');

//ruler
const ruler = document.getElementById('readingRuler');
const rulerToggle = document.getElementById('toggleRuler');
const rulerThumb = rulerToggle.querySelector('span');

let rulerActive = false;

rulerToggle.addEventListener('click', () => {
    rulerActive = !rulerActive;
    ruler.classList.toggle('hidden', !rulerActive);

    rulerToggle.classList.toggle('bg-blue-600', rulerActive);
    rulerToggle.classList.toggle('bg-gray-300', !rulerActive);
    rulerThumb.classList.toggle('translate-x-6', rulerActive);
    rulerThumb.classList.toggle('translate-x-1', !rulerActive);
});

document.addEventListener('mousemove', (e) => {
    if (rulerActive) {
        const height = ruler.offsetHeight;
        ruler.style.top = `${e.clientY - height / 2}px`;
    }
});
//font size
let currentFontSize = 16;
decreaseBtn.addEventListener('click', () => {
    if (currentFontSize > 12) {
        currentFontSize -= 1;
        updateFontSize();
    }
});
resetBtn.addEventListener('click', () => {
    currentFontSize = 16;
    updateFontSize();
});
increaseBtn.addEventListener('click', () => {
    if (currentFontSize < 24) {
        currentFontSize += 1;
        updateFontSize();
    }
});

function updateFontSize() {
    document.documentElement.style.setProperty('--font-size-base', `${currentFontSize}px`);
    document.body.style.fontSize = `${currentFontSize}px`;
    root.style.fontSize = `${currentFontSize}px`;
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Button functionality
const learnMoreBtn = document.getElementById('learnMoreBtn');
if (learnMoreBtn) {
    learnMoreBtn.addEventListener('click', function () {
        window.location.href = '/learn_more';
    });
}

const signupBtn = document.getElementById('signupBtn');
if (signupBtn) {
    signupBtn.addEventListener('click', function () {
        window.location.href = '/signup';
    });
}

const learnMoreFooterBtn = document.getElementById('learnMoreFooterBtn');
if (learnMoreFooterBtn) {
    learnMoreFooterBtn.addEventListener('click', function () {
        window.location.href = '/learn_more';
    });
}





// FAQ Accordion Logic (Moved from learn_more.html)
document.addEventListener("DOMContentLoaded", () => {
    const questions = document.querySelectorAll(".faq-question");

    questions.forEach((question) => {
        question.addEventListener("click", () => {
            const faqItem = question.parentElement;
            const answer = faqItem.querySelector(".faq-answer");
            const iconPath = question.querySelector("svg path");

            const isOpen = answer.classList.contains("active");

            // Optional: Close all others (one open at a time)
            document.querySelectorAll(".faq-answer.active").forEach((openAnswer) => {
                if (openAnswer !== answer) {
                    openAnswer.classList.remove("active");
                    openAnswer.style.maxHeight = null;
                    openAnswer.parentElement.querySelector(".faq-question").classList.remove("open");
                    openAnswer.parentElement.querySelector("svg path").setAttribute(
                        "d",
                        "M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                    );
                }
            });

            if (isOpen) {
                answer.classList.remove("active");
                answer.style.maxHeight = null;
                question.classList.remove("open");
                iconPath.setAttribute(
                    "d",
                    "M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z"
                ); // plus
            } else {
                answer.classList.add("active");
                answer.style.maxHeight = answer.scrollHeight + "px";
                question.classList.add("open");
                iconPath.setAttribute(
                    "d",
                    "M5 10a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1z"
                ); // minus
            }
        });
    });
});
