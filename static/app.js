/**
 * PatraBodh Frontend - Camera upload, drag-drop, and result display
 */

(function () {
    'use strict';

    // DOM elements
    const dropZone = document.getElementById('dropZone');
    const cameraInput = document.getElementById('cameraInput');
    const fileInput = document.getElementById('fileInput');
    const uploadSection = document.getElementById('uploadSection');
    const previewSection = document.getElementById('previewSection');
    const previewImage = document.getElementById('previewImage');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const analysisContent = document.getElementById('analysisContent');
    const fieldsCard = document.getElementById('fieldsCard');
    const fieldsContent = document.getElementById('fieldsContent');
    const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const retryBtn = document.getElementById('retryBtn');

    let currentFile = null;

    // --- Event Listeners ---

    cameraInput.addEventListener('change', handleFileSelect);
    fileInput.addEventListener('change', handleFileSelect);
    changeImageBtn.addEventListener('click', resetToUpload);
    analyzeAnotherBtn.addEventListener('click', resetToUpload);
    retryBtn.addEventListener('click', () => {
        if (currentFile) analyzeDocument(currentFile);
        else resetToUpload();
    });

    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) processFile(files[0]);
    });

    // --- File Handling ---

    function handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) processFile(files[0]);
    }

    function processFile(file) {
        // Validate type
        if (!file.type.startsWith('image/')) {
            showError('Please upload an image file (JPEG, PNG, or WebP).');
            return;
        }

        // Validate size (10MB max)
        if (file.size > 10 * 1024 * 1024) {
            showError('Image is too large. Maximum size is 10MB.');
            return;
        }

        currentFile = file;

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            showSection('preview');
        };
        reader.readAsDataURL(file);

        // Auto-analyze after short delay for preview
        setTimeout(() => analyzeDocument(file), 500);
    }

    // --- API Communication ---

    async function analyzeDocument(file) {
        showSection('loading');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(err.detail || `Server error: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);

        } catch (err) {
            showError(err.message || 'Failed to analyze document. Please try again.');
        }
    }

    // --- Display Results ---

    function displayResults(data) {
        // Display analysis
        if (data.analysis && data.analysis.raw) {
            analysisContent.innerHTML = markdownToHtml(data.analysis.raw);
        } else if (data.analysis && data.analysis.sections) {
            let html = '';
            for (const [section, content] of Object.entries(data.analysis.sections)) {
                html += `<h2>${escapeHtml(section)}</h2>`;
                html += markdownToHtml(content);
            }
            analysisContent.innerHTML = html;
        } else {
            analysisContent.innerHTML = '<p>No analysis available.</p>';
        }

        // Display extracted fields
        if (data.extracted_fields && data.extracted_fields.fields && data.extracted_fields.fields.length > 0) {
            fieldsCard.classList.remove('hidden');
            let tableHtml = '<table class="fields-table"><thead><tr><th>Field</th><th>Value</th><th>Required</th></tr></thead><tbody>';
            for (const field of data.extracted_fields.fields) {
                const reqClass = field.required ? 'field-required' : '';
                const reqText = field.required ? '✓ Yes' : '—';
                tableHtml += `<tr>
                    <td>${escapeHtml(field.name)}</td>
                    <td>${escapeHtml(field.value || '—')}</td>
                    <td class="${reqClass}">${reqText}</td>
                </tr>`;
            }
            tableHtml += '</tbody></table>';

            // Add metadata
            if (data.extracted_fields.document_type) {
                tableHtml = `<p><strong>Document Type:</strong> ${escapeHtml(data.extracted_fields.document_type)}</p>` + tableHtml;
            }
            if (data.extracted_fields.deadlines && data.extracted_fields.deadlines.length) {
                tableHtml += `<p><strong>⏰ Deadlines:</strong> ${data.extracted_fields.deadlines.map(escapeHtml).join(', ')}</p>`;
            }
            if (data.extracted_fields.fees && data.extracted_fields.fees.length) {
                tableHtml += `<p><strong>💰 Fees:</strong> ${data.extracted_fields.fees.map(escapeHtml).join(', ')}</p>`;
            }

            fieldsContent.innerHTML = tableHtml;
        } else {
            fieldsCard.classList.add('hidden');
        }

        showSection('results');
    }

    // --- UI Helpers ---

    function showSection(section) {
        uploadSection.classList.add('hidden');
        previewSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');

        switch (section) {
            case 'upload': uploadSection.classList.remove('hidden'); break;
            case 'preview':
                uploadSection.classList.remove('hidden');
                previewSection.classList.remove('hidden');
                break;
            case 'loading':
                previewSection.classList.remove('hidden');
                loadingSection.classList.remove('hidden');
                break;
            case 'results': resultsSection.classList.remove('hidden'); break;
            case 'error': errorSection.classList.remove('hidden'); break;
        }
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        showSection('error');
    }

    function resetToUpload() {
        currentFile = null;
        cameraInput.value = '';
        fileInput.value = '';
        previewImage.src = '';
        analysisContent.innerHTML = '';
        fieldsContent.innerHTML = '';
        fieldsCard.classList.add('hidden');
        showSection('upload');
    }

    // --- Markdown Renderer (lightweight) ---

    function markdownToHtml(md) {
        if (!md) return '';
        let html = escapeHtml(md);

        // Headers
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

        // Bold and italic
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // Lists
        html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');

        // Line breaks to paragraphs
        html = html.replace(/\n\n/g, '</p><p>');
        html = html.replace(/\n/g, '<br>');
        html = '<p>' + html + '</p>';

        // Clean up empty paragraphs
        html = html.replace(/<p>\s*<\/p>/g, '');
        html = html.replace(/<p>(<h[1-3]>)/g, '$1');
        html = html.replace(/(<\/h[1-3]>)<\/p>/g, '$1');
        html = html.replace(/<p>(<ul>)/g, '$1');
        html = html.replace(/(<\/ul>)<\/p>/g, '$1');

        return html;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

})();
