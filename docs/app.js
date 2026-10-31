/**
 * PatraBodh Frontend - Demo Mode for GitHub Pages
 * Simulates Gemma 4 document analysis for static hosting.
 */

(function () {
    'use strict';

    const dropZone = document.getElementById('dropZone');
    const cameraInput = document.getElementById('cameraInput');
    const fileInput = document.getElementById('fileInput');
    const uploadSection = document.getElementById('uploadSection');
    const previewSection = document.getElementById('previewSection');
    const previewImage = document.getElementById('previewImage');
    const changeImageBtn = document.getElementById('changeImageBtn');
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    const fieldsCard = document.getElementById('fieldsCard');
    const fieldsContent = document.getElementById('fieldsContent');
    const analysisContent = document.getElementById('analysisContent');
    const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
    const errorSection = document.getElementById('errorSection');
    const errorMessage = document.getElementById('errorMessage');
    const retryBtn = document.getElementById('retryBtn');

    let currentFile = null;

    // Demo analysis response simulating Gemma 4 output
    const DEMO_ANALYSIS = `## 📄 Document Type
This appears to be an **Aadhaar Card Enrollment/Update Form** (आधार नामांकन/अपडेट फॉर्म).

## 📝 What This Document Is About
यह फॉर्म आधार कार्ड के लिए नया नामांकन या मौजूदा आधार में अपडेट करने के लिए है। यह भारत सरकार की UIDAI द्वारा जारी किया जाता है और लगभग सभी सरकारी सेवाओं, बैंक खातों और सब्सिडी के लिए आवश्यक है।

This form is for new Aadhaar enrollment or updating existing Aadhaar details. It is issued by UIDAI (Government of India) and is required for most government services, bank accounts, and subsidy programs.

## 📋 Key Fields Identified
- **पूर्ण नाम / Full Name** → Your complete legal name as per supporting documents
- **जन्म तिथि / Date of Birth** → DD/MM/YYYY format, must match school/birth certificate
- **लिंग / Gender** → Male/Female/Other
- **पता / Address** → Current residential address with PIN code
- **मोबाइल नंबर / Mobile Number** → For OTP verification and updates
- **ईमेल / Email** → Optional, for receiving digital Aadhaar

## ⚠️ Important Things to Note
- Original documents required for verification (not photocopies)
- Biometric capture (fingerprints + iris scan) done at enrollment center
- Processing time: 90 days for new enrollment, 30 days for updates
- No fee for first-time enrollment; ₹50 for updates
- Common mistake: Name spelling mismatch between form and supporting documents

## ✅ Next Steps
1. Fill all fields in BLOCK LETTERS (English) or clearly in Hindi
2. Attach self-attested copies of proof of identity + proof of address
3. Visit nearest Aadhaar Enrollment Center with original documents
4. After submission, track status at https://resident.uidai.gov.in/check-aadhaar

## 🔗 Related Government Schemes
- **Direct Benefit Transfer (DBT)**: Aadhaar-linked bank accounts receive government subsidies directly
- **PM-KISAN**: Requires Aadhaar for farmer benefit transfers
- **Ayushman Bharat**: Aadhaar used as identity proof for health insurance enrollment
- **LPG Subsidy (PAHAL)**: Aadhaar linking mandatory for subsidized gas cylinders`;

    const DEMO_FIELDS = {
        document_type: "Aadhaar Enrollment/Update Form",
        language: "mixed (hi/en)",
        title: "आधार नामांकन/अपडेट फॉर्म",
        issuing_authority: "UIDAI, Government of India",
        fields: [
            { name: "Full Name / पूर्ण नाम", value: "", required: true },
            { name: "Date of Birth / जन्म तिथि", value: "", required: true },
            { name: "Gender / लिंग", value: "", required: true },
            { name: "Address / पता", value: "", required: true },
            { name: "Mobile Number / मोबाइल", value: "", required: true },
            { name: "Email / ईमेल", value: "", required: false }
        ],
        deadlines: ["90 days processing for new enrollment", "30 days for updates"],
        fees: ["Free for first enrollment", "₹50 for updates"],
        required_documents: ["Proof of Identity (POI)", "Proof of Address (POA)", "Proof of Date of Birth"],
        submission_address: "Nearest Aadhaar Enrollment Center",
        contact_info: "UIDAI Helpline: 1947 | help@uidai.gov.in"
    };

    function showSection(section) {
        [uploadSection, previewSection, loadingSection, resultsSection, errorSection]
            .forEach(s => s.classList.add('hidden'));
        section.classList.remove('hidden');
    }

    function handleFile(file) {
        if (!file || !file.type.startsWith('image/')) {
            showError('Please upload a valid image file (JPEG, PNG, or WebP).');
            return;
        }
        currentFile = file;
        const reader = new FileReader();
        reader.onload = function (e) {
            previewImage.src = e.target.result;
            showSection(previewSection);
        };
        reader.readAsDataURL(file);
    }

    function showError(msg) {
        errorMessage.textContent = msg;
        showSection(errorSection);
    }

    function renderFields(fields) {
        let html = '<table class="fields-table">';
        html += '<tr><th>Field</th><th>Required</th></tr>';
        fields.fields.forEach(f => {
            html += `<tr><td>${f.name}</td><td>${f.required ? '✅ Yes' : '❌ No'}</td></tr>`;
        });
        html += '</table>';

        if (fields.fees && fields.fees.length) {
            html += '<div class="field-group"><strong>💰 Fees:</strong> ' + fields.fees.join(', ') + '</div>';
        }
        if (fields.deadlines && fields.deadlines.length) {
            html += '<div class="field-group"><strong>⏰ Deadlines:</strong> ' + fields.deadlines.join(', ') + '</div>';
        }
        if (fields.required_documents && fields.required_documents.length) {
            html += '<div class="field-group"><strong>📎 Required Documents:</strong> ' + fields.required_documents.join(', ') + '</div>';
        }
        if (fields.contact_info) {
            html += '<div class="field-group"><strong>📞 Contact:</strong> ' + fields.contact_info + '</div>';
        }

        fieldsContent.innerHTML = html;
    }

    function simpleMarkdown(text) {
        return text
            .replace(/^## (.+)$/gm, '<h3>$1</h3>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/^- (.+)$/gm, '<li>$1</li>')
            .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
            .replace(/<\/ul>\s*<ul>/g, '')
            .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
            .replace(/\n\n/g, '<br><br>')
            .replace(/https?:\/\/[^\s]+/g, url => `<a href="${url}" target="_blank">${url}</a>`);
    }

    async function analyzeDocument() {
        showSection(loadingSection);

        // Simulate network delay for realistic demo feel
        await new Promise(resolve => setTimeout(resolve, 2500));

        renderFields(DEMO_FIELDS);
        analysisContent.innerHTML = simpleMarkdown(DEMO_ANALYSIS);
        showSection(resultsSection);
    }

    // Event listeners
    fileInput.addEventListener('change', e => handleFile(e.target.files[0]));
    cameraInput.addEventListener('change', e => handleFile(e.target.files[0]));

    changeImageBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        cameraInput.value = '';
        showSection(uploadSection);
    });

    analyzeAnotherBtn.addEventListener('click', () => {
        currentFile = null;
        fileInput.value = '';
        cameraInput.value = '';
        showSection(uploadSection);
    });

    retryBtn.addEventListener('click', () => {
        if (currentFile) analyzeDocument();
        else showSection(uploadSection);
    });

    // Drag and drop
    dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        handleFile(e.dataTransfer.files[0]);
    });

    // Auto-analyze after preview
    previewImage.addEventListener('load', () => {
        if (currentFile) analyzeDocument();
    });

})();
