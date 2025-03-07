document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('summary-form');
    const urlInput = document.getElementById('hn-url');
    const submitButton = document.getElementById('submit-btn');
    const downloadButton = document.getElementById('download-btn');
    const loadingSection = document.getElementById('loading');
    const resultSection = document.getElementById('result');
    const summaryContent = document.getElementById('summary-content');
    const errorSection = document.getElementById('error');
    const errorMessage = document.getElementById('error-message');
    
    // Check if download button exists
    console.log('Download button element:', downloadButton);
    
    // Store the raw markdown summary
    let currentSummaryMarkdown = '';

    // Configure marked.js
    marked.setOptions({
        breaks: true,        // Convert \n to <br>
        gfm: true,           // GitHub Flavored Markdown
        headerIds: true,     // Add id attributes to headings
        sanitize: false      // Allow HTML in markdown
    });

    // Handle form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = urlInput.value.trim();
        if (!url) return;

        // Show loading, hide other sections
        showSection(loadingSection);
        submitButton.disabled = true;

        try {
            const summary = await fetchSummary(url);
            displaySummary(summary);
        } catch (error) {
            displayError(error.message || 'An unexpected error occurred.');
        } finally {
            submitButton.disabled = false;
        }
    });

    // Fetch summary from the backend API
    async function fetchSummary(url) {
        // Use relative path when in production (Docker), fallback to localhost for development
        const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? 'http://localhost:8000/summarize'
            : 'http://backend:8000/summarize';
            
        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Failed to generate summary');
        }
        
        return data.summary;
    }

    // Display the summary
    function displaySummary(summary) {
        console.log('Displaying summary:', summary);
        
        // Store the raw markdown for download
        currentSummaryMarkdown = summary;
        console.log('Stored currentSummaryMarkdown:', currentSummaryMarkdown);
        
        // Convert markdown to HTML
        summaryContent.innerHTML = marked.parse(summary);
        
        // Show result section, hide others
        showSection(resultSection);
        
        // Scroll to result
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Display error message
    function displayError(message) {
        errorMessage.textContent = message;
        showSection(errorSection);
    }

    // Helper to show one section and hide others
    function showSection(sectionToShow) {
        // Hide all sections
        loadingSection.classList.add('hidden');
        resultSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        
        // Show the requested section
        sectionToShow.classList.remove('hidden');
    }
    
    // Simplify the download function
    function downloadSummary() {
        if (!currentSummaryMarkdown) {
            console.log('No summary content to download');
            return;
        }

        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `hn-summary-${timestamp}.md`;

        const blob = new Blob([currentSummaryMarkdown], { type: 'text/markdown;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        
        // Trigger download
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Remove multiple event handlers and just use a single one
    if (downloadButton) {
        downloadButton.addEventListener('click', downloadSummary);
    }
});
