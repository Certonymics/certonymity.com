(function() {
    function showThankYouMessage() {
        const form = document.getElementById('waiting-list-form');
        const thankYouMessage = document.getElementById('thank-you-message');
        if (form && thankYouMessage) {
            form.style.display = 'none';
            thankYouMessage.style.display = 'block';
            thankYouMessage.focus();
        }
    }

    // Netlify redirects back with ?success=true after form submission
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('success') === 'true') {
        showThankYouMessage();
    }
})();
