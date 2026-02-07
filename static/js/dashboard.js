// Simple interaction logic for the Dashboard
document.addEventListener('DOMContentLoaded', () => {
    console.log("Dashboard Hub Initialized");
    
    const cards = document.querySelectorAll('.action-card');
    
    cards.forEach(card => {
        card.addEventListener('click', () => {
            // Optional: Show a loading spinner before navigating
            card.style.opacity = '0.7';
        });
    });
});