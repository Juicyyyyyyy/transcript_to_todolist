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
            showError('Veuillez sélectionner un fichier ZIP pour le projet');
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
        const fileName = file.name.toLowerCase();
        if (!fileName.endsWith('.txt') && !fileName.endsWith('.docx')) {
            showError('Veuillez sélectionner un fichier .txt ou .docx pour la transcription');
            transcriptFileInput.value = '';
            return;
        }
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
        
        state.folderId = `session_${Date.now()}`;
        
        await uploadProject();
        
        const transcriptContent = await uploadTranscript();
        
        const parsedProject = await parseProject();
        
        await generateTodoList(parsedProject, transcriptContent);
        
        showLoading(false);
        showResults();
        
    } catch (error) {
        console.error('Error:', error);
        showLoading(false);
        showError(error.message || 'Une erreur est survenue pendant le traitement');
    }
});

async function uploadProject() {
    const formData = new FormData();
    formData.append('file', state.projectFile);
    
    const response = await fetch(`/api/import-project/${state.folderId}`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        let errorMessage = "Échec de l'import du projet";
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        } catch (e) {
            errorMessage = `Échec de l'import du projet (Statut : ${response.status})`;
        }
        throw new Error(errorMessage);
    }
    
    return await response.json();
}

async function uploadTranscript() {
    const formData = new FormData();
    formData.append('file', state.transcriptFile);
    
    const response = await fetch(`/api/import-transcript/${state.folderId}`, {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        let errorMessage = "Échec de l'import de la transcription";
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        } catch (e) {
            errorMessage = `Échec de l'import de la transcription (Statut : ${response.status})`;
        }
        throw new Error(errorMessage);
    }
    
    const result = await response.json();

    if (!result.content) {
        throw new Error('Aucun contenu extrait du fichier de transcription. Le fichier est peut-être vide ou corrompu.');
    }
    
    return result.content;
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
        let errorMessage = 'Échec de l\'analyse du projet. Assurez-vous que le zip contient des fichiers PHP ou JavaScript.';
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        } catch (e) {
            errorMessage = `Échec de l'analyse du projet (Statut : ${response.status})`;
        }
        throw new Error(errorMessage);
    }
    
    const result = await response.json();
    return result.parsed_project;
}

// Generate todo list via API
async function generateTodoList(parsedProject, transcript) {
    console.log('Generating todo list with:', {
        parsedProjectLength: parsedProject?.length,
        transcriptLength: transcript?.length
    });
    
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
        let errorMessage = 'Échec de la génération de la liste de todos';
        try {
            const errorData = await response.json();
            console.error('Error from API:', errorData);
            errorMessage = errorData.detail || errorMessage;
        } catch (e) {
            console.error('Failed to parse error response:', e);
            errorMessage = `Échec de la génération de la liste de todos (Statut : ${response.status})`;
        }
        throw new Error(errorMessage);
    }
    
    state.results = await response.json();
    
    await buildOutput();
}

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
        let errorMessage = 'Échec de l\'enregistrement des résultats';
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || errorMessage;
        } catch (e) {
            errorMessage = `Échec de l'enregistrement des résultats (Statut : ${response.status})`;
        }
        throw new Error(errorMessage);
    }
    
    const buildData = await response.json();
    state.outputPath = buildData.path;
}

function showResults() {
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    document.getElementById('context-content').innerHTML =
        formatContent(state.results.context);
    document.getElementById('todo-content').innerHTML = 
        formatContent(state.results.technical_todolist);
    document.getElementById('clarifications-content').innerHTML = 
        formatContent(state.results.clarifications);
}

// Format content for display
function formatContent(content) {
    if (typeof content === 'object') {
        content = JSON.stringify(content, null, 2);
        return `<pre><code>${escapeHtml(content)}</code></pre>`;
    }
    if (!content) {
        return '<p class="no-data">Aucune donnée disponible</p>';
    }
    // Parse markdown to HTML
    return marked.parse(content);
}

// Helper function to escape HTML in JSON content
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
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
        const content = `REUNION TO CODE - RÉSULTATS GÉNÉRÉS
${'='.repeat(50)}

CONTEXTE DU PROJET
${'-'.repeat(50)}
${formatContent(state.results.context)}

LISTE DES TODOS TECHNIQUES
${'-'.repeat(50)}
${formatContent(state.results.technical_todolist)}

CLARIFICATIONS REQUISES
${'-'.repeat(50)}
${formatContent(state.results.clarifications)}

${'='.repeat(50)}
Généré le : ${new Date().toLocaleString()}
Chemin de sortie : ${state.outputPath || 'N/A'}
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
        
        showSuccess('Résultats téléchargés avec succès !');
    } catch (error) {
        showError('Échec du téléchargement des résultats');
    }
});

// New analysis button
document.getElementById('new-analysis-btn').addEventListener('click', () => {
    // Reset state
    state.projectFile = null;
    state.transcriptFile = null;
    state.folderId = null;
    state.results = null;
    
    projectFileInput.value = '';
    transcriptFileInput.value = '';
    document.getElementById('project-filename').textContent = '';
    document.getElementById('transcript-filename').textContent = '';
    generateBtn.disabled = true;
    
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';
});

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
    errorMessage.style.borderLeftColor = '#10b981';
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    setTimeout(() => {
        errorMessage.style.borderLeftColor = '#ef4444';
        errorMessage.style.display = 'none';
    }, 3000);
}

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


