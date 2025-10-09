// State management
const state = {
    projectFile: null,
    transcriptFile: null,
    folderId: null,
    results: null
};

// DOM Elements
const projectFileInput = document.getElementById('project-file');
const transcriptFileInput = document.getElementById('transcript-file');
const generateBtn = document.getElementById('generate-btn');
const uploadSection = document.getElementById('upload-section');
const resultsSection = document.getElementById('results-section');
const loadingOverlay = document.getElementById('loading-overlay');
const errorMessage = document.getElementById('error-message');
const errorText = document.getElementById('error-text');

// File upload handlers
projectFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        if (!file.name.toLowerCase().endsWith('.zip')) {
            showError('Please select a ZIP file for the project');
            projectFileInput.value = '';
            return;
        }
        state.projectFile = file;
        document.getElementById('project-filename').textContent = `✓ ${file.name}`;
        checkFilesReady();
    }
});

transcriptFileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        state.transcriptFile = file;
        document.getElementById('transcript-filename').textContent = `✓ ${file.name}`;
        checkFilesReady();
    }
});

// Check if both files are uploaded
function checkFilesReady() {
    if (state.projectFile && state.transcriptFile) {
        generateBtn.disabled = false;
    }
}

// Generate button handler
generateBtn.addEventListener('click', async () => {
    try {
        showLoading(true);
        
        // Generate unique folder ID
        state.folderId = `session_${Date.now()}`;
        
        // Step 1: Upload project
        await uploadProject();
        
        // Step 2: Upload transcript
        const transcriptContent = await readTranscriptFile();
        
        // Step 3: Parse project using the parser API
        const parsedProject = await parseProject();
        
        // Step 4: Generate todo list
        await generateTodoList(parsedProject, transcriptContent);
        
        showLoading(false);
        showResults();
        
    } catch (error) {
        console.error('Error:', error);
        showLoading(false);
        showError(error.message || 'An error occurred during processing');
    }
});

// Upload project to server
async function uploadProject() {
    const formData = new FormData();
    formData.append('file', state.projectFile);
    
    const response = await fetch(`/api/import-project/${state.folderId}`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload project');
    }
    
    return await response.json();
}

// Read transcript file content
async function readTranscriptFile() {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(new Error('Failed to read transcript file'));
        reader.readAsText(state.transcriptFile);
    });
}

async function parseProject() {
    const projectPath = `/tmp/${state.folderId}`;
    
    const response = await fetch('/api/parse-project', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            project_path: projectPath
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to parse project. Make sure the zip file contains PHP or JavaScript files.');
    }
    
    const result = await response.json();
    return result.parsed_project;
}

// Generate todo list via API
async function generateTodoList(parsedProject, transcript) {
    const response = await fetch('/api/generate-todolist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            parsed_project: parsedProject,
            transcript: transcript
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate todo list');
    }
    
    state.results = await response.json();
    
    // Store the results via build-output API
    await buildOutput();
}

// Store results via build-output API
async function buildOutput() {
    const response = await fetch('/api/build-output', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            context: state.results.context,
            technical_todo: state.results.technical_todolist,
            clarifications: state.results.clarifications
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to save results');
    }
    
    const buildData = await response.json();
    state.outputPath = buildData.path;
}

// Show results section
function showResults() {
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Populate results
    document.getElementById('context-content').textContent = 
        formatContent(state.results.context);
    document.getElementById('todo-content').textContent = 
        formatContent(state.results.technical_todolist);
    document.getElementById('clarifications-content').textContent = 
        formatContent(state.results.clarifications);
}

// Format content for display
function formatContent(content) {
    if (typeof content === 'object') {
        return JSON.stringify(content, null, 2);
    }
    return content || 'No data available';
}

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update active states
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Download results
document.getElementById('download-btn').addEventListener('click', async () => {
    try {
        // Create a downloadable file with all results
        const content = `REUNION TO CODE - GENERATED RESULTS
${'='.repeat(50)}

PROJECT CONTEXT
${'-'.repeat(50)}
${formatContent(state.results.context)}

TECHNICAL TODO LIST
${'-'.repeat(50)}
${formatContent(state.results.technical_todolist)}

CLARIFICATIONS REQUIRED
${'-'.repeat(50)}
${formatContent(state.results.clarifications)}

${'='.repeat(50)}
Generated on: ${new Date().toLocaleString()}
Output path: ${state.outputPath || 'N/A'}
`;
        
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `reunion-to-code-results-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showSuccess('Results downloaded successfully!');
    } catch (error) {
        showError('Failed to download results');
    }
});

// New analysis button
document.getElementById('new-analysis-btn').addEventListener('click', () => {
    // Reset state
    state.projectFile = null;
    state.transcriptFile = null;
    state.folderId = null;
    state.results = null;
    
    // Reset UI
    projectFileInput.value = '';
    transcriptFileInput.value = '';
    document.getElementById('project-filename').textContent = '';
    document.getElementById('transcript-filename').textContent = '';
    generateBtn.disabled = true;
    
    // Show upload section
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';
});

// Utility functions
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function showSuccess(message) {
    // Reuse error box for success messages
    errorMessage.style.borderLeftColor = '#10b981';
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    setTimeout(() => {
        errorMessage.style.borderLeftColor = '#ef4444';
        errorMessage.style.display = 'none';
    }, 3000);
}

// Drag and drop support
['project-file', 'transcript-file'].forEach(id => {
    const input = document.getElementById(id);
    const label = input.parentElement;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        label.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        label.addEventListener(eventName, () => {
            label.querySelector('.upload-box').style.borderColor = '#4f46e5';
            label.querySelector('.upload-box').style.background = '#eef2ff';
        });
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        label.addEventListener(eventName, () => {
            label.querySelector('.upload-box').style.borderColor = '#e2e8f0';
            label.querySelector('.upload-box').style.background = '#f8fafc';
        });
    });
    
    label.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            input.dispatchEvent(new Event('change'));
        }
    });
});

console.log('Reunion to Code UI initialized ✓');


