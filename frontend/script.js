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
        const model = document.getElementById('model-select').value;

        // Show loading, hide other sections
        showSection(loadingSection);
        submitButton.disabled = true;

        try {
            // Clear previous summary and errors
            summaryContent.innerHTML = '';
            currentSummaryMarkdown = '';
            showSection(loadingSection); // Show loading indicator

            await fetchSummaryStream(url, model);
        } catch (error) {
            displayError(error.message || 'An unexpected error occurred.');
        } finally {
            submitButton.disabled = false;
        }
    });

    // Fetch summary from the backend API using streaming
    async function fetchSummaryStream(url, model) {
        const apiUrl = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
            ? 'http://localhost:8000/summarize_stream'
            : '/api/summarize_stream'; // Ensure this matches your backend route for streaming

        console.log('Using streaming API URL:', apiUrl);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, model })
        });

        if (!response.ok) {
            // Attempt to read error message from stream if possible, or use status text
            let errorDetail = `Failed to start stream: ${response.statusText}`;
            try {
                const errorData = await response.json(); // Or .text() if error is not JSON
                errorDetail = errorData.detail || errorDetail;
            } catch (e) {
                // Ignore if error response is not parseable
            }
            throw new Error(errorDetail);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        currentSummaryMarkdown = ''; // Reset for new stream

        showSection(resultSection); // Show result section once stream starts

        while (true) {
            const { value, done } = await reader.read();
            if (done) {
                console.log('Stream finished.');
                // Optional: Add a [DONE] marker or similar if needed, though OpenRouter doesn't send one for content.
                // The backend might send one if we implement it.
                break;
            }

            const chunk = decoder.decode(value, { stream: true });
            currentSummaryMarkdown += chunk;
            summaryContent.innerHTML = marked.parse(currentSummaryMarkdown);
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }

    // Display the summary (now handled by fetchSummaryStream progressively)
    // function displaySummary(summary) { // This function is no longer directly called for streaming
    //     console.log('Displaying summary:', summary);
    //     currentSummaryMarkdown = summary;
    //     summaryContent.innerHTML = marked.parse(summary);
    //     showSection(resultSection);
    //     resultSection.scrollIntoView({ behavior: 'smooth' });
    // }

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
