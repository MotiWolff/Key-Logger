document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.contact-form');
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault(); // Prevent form from submitting normally
        
        try {
            // Submit form data to Formspree
            const response = await fetch(this.action, {
                method: 'POST',
                body: new FormData(this),
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Success! Clear the form
                this.reset();
                alert('Message sent successfully!');
            } else {
                // Error
                throw new Error(data.error || 'Form submission failed');
            }
        } catch (error) {
            alert('Error sending message: ' + error.message);
        }
    });
}); 