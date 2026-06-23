const API_BASE = "http://127.0.0.1:8000";
let currentTab = "text"; 
let selectedLevel = "basic";
let selectedFile = null;
let obfuscatedTextResult = "";
let obfuscatedFileBlob = null;
let obfuscatedFileName = "";

const tabText = document.getElementById("tab-text");
const tabFile = document.getElementById("tab-file");
const contentText = document.getElementById("content-text");
const contentFile = document.getElementById("content-file");

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileInfo = document.getElementById("file-info");
const selectedFileName = document.getElementById("selected-file-name");
const btnRemoveFile = document.getElementById("btn-remove-file");

const levelOptions = document.querySelectorAll(".protection-card");

const btnObfuscate = document.getElementById("btn-obfuscate");
const loader = document.getElementById("loader");
const resultPlaceholder = document.getElementById("result-placeholder");
const placeholderMessage = document.getElementById("placeholder-message");
const resultContent = document.getElementById("result-content");
const codeOutput = document.getElementById("code-output");
const resultFileContent = document.getElementById("result-file-content");

const btnCopy = document.getElementById("btn-copy");
const btnDownload = document.getElementById("btn-download");
const btnDownloadFile = document.getElementById("btn-download-file");

const codeInput = document.getElementById("code-input");
const lineNumbers = document.getElementById("line-numbers");
const outputLineNumbers = document.getElementById("output-line-numbers");
const editorLinesCount = document.getElementById("editor-lines-count");

function syncLineNumbers(textarea, sidebar, counterLabel = null) {
    const lines = textarea.value.split("\n");
    const count = lines.length;
    
    let numbersHTML = "";
    for (let i = 1; i <= count; i++) {
        numbersHTML += `<div>${i}</div>`;
    }
    sidebar.innerHTML = numbersHTML;
    
    if (counterLabel) {
        counterLabel.textContent = `${count} ${count > 1 ? 'lignes' : 'ligne'}`;
    }
}

codeInput.addEventListener("scroll", () => {
    lineNumbers.scrollTop = codeInput.scrollTop;
});

codeOutput.addEventListener("scroll", () => {
    outputLineNumbers.scrollTop = codeOutput.scrollTop;
});

codeInput.addEventListener("input", () => {
    syncLineNumbers(codeInput, lineNumbers, editorLinesCount);
});

tabText.addEventListener("click", () => {
    currentTab = "text";
    tabText.classList.add("active");
    tabFile.classList.remove("active");
    contentText.classList.add("active");
    contentFile.classList.remove("active");
    resetResultViews();
});

tabFile.addEventListener("click", () => {
    currentTab = "file";
    tabFile.classList.add("active");
    tabText.classList.remove("active");
    contentFile.classList.add("active");
    contentText.classList.remove("active");
    resetResultViews();
});

levelOptions.forEach(option => {
    option.addEventListener("click", () => {
        levelOptions.forEach(opt => opt.classList.remove("active"));
        option.classList.add("active");
        selectedLevel = option.dataset.level;
    });
});

dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
    handleFileSelection(e.target.files[0]);
});

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    if (e.dataTransfer.files.length > 0) {
        handleFileSelection(e.dataTransfer.files[0]);
    }
});

btnRemoveFile.addEventListener("click", () => {
    selectedFile = null;
    fileInput.value = "";
    fileInfo.style.display = "none";
    dropZone.style.display = "block";
    resetResultViews();
});

function handleFileSelection(file) {
    if (!file) return;
    
    const allowed = [".py", ".zip", ".tar.gz"];
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    const isTarGz = file.name.endsWith(".tar.gz");
    
    if (!allowed.includes(ext) && !isTarGz) {
        showToast("Format de fichier non supporté. (.py, .zip, .tar.gz uniquement)", "error");
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showToast("La taille du fichier dépasse la limite de 10 Mo.", "error");
        return;
    }

    selectedFile = file;
    selectedFileName.textContent = `${file.name} (${formatBytes(file.size)})`;
    
    const iconEl = fileInfo.querySelector(".file-icon i");
    if (ext === ".py") {
        iconEl.className = "fa-solid fa-file-code";
    } else {
        iconEl.className = "fa-solid fa-file-zipper";
    }

    dropZone.style.display = "none";
    fileInfo.style.display = "flex";
    resetResultViews();
}

btnObfuscate.addEventListener("click", async () => {
    if (currentTab === "text") {
        const code = codeInput.value.trim();
        if (!code) {
            showToast("Veuillez saisir du code Python à obfusquer.", "error");
            return;
        }
        await obfuscateText(code);
    } else {
        if (!selectedFile) {
            showToast("Veuillez sélectionner un fichier à obfusquer.", "error");
            return;
        }
        await obfuscateFile(selectedFile);
    }
});

async function obfuscateText(code) {
    showLoading(true);
    try {
        const response = await fetch(`${API_BASE}/obfuscate-text`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                code: code,
                level: selectedLevel
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "Une erreur est survenue lors de l'obfuscation.");
        }

        let result = data.obfuscated_code;
        if (selectedLevel === "hardcore" && result.includes("_environment_scope")) {
            result = "builtins = __import__('builtins')\nsetattr(builtins, '_environment_scope', None)\n" + result;
        }

        obfuscatedTextResult = result;
        codeOutput.value = obfuscatedTextResult;
        syncLineNumbers(codeOutput, outputLineNumbers);
        
        resultPlaceholder.style.display = "none";
        resultFileContent.style.display = "none";
        resultContent.style.display = "flex";
        showToast("Code obfusqué avec succès !", "success");
    } catch (err) {
        showToast(err.message, "error");
        resetResultViews();
    } finally {
        showLoading(false);
    }
}

async function obfuscateFile(file) {
    showLoading(true);
    try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("level", selectedLevel);

        const response = await fetch(`${API_BASE}/obfuscate`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Une erreur est survenue lors du traitement du fichier.");
        }

        obfuscatedFileBlob = await response.blob();
        obfuscatedFileName = `obfuscated_${file.name}`;

        resultPlaceholder.style.display = "none";
        resultContent.style.display = "none";
        resultFileContent.style.display = "flex";
        showToast("Fichier obfusqué avec succès !", "success");
    } catch (err) {
        showToast(err.message, "error");
        resetResultViews();
    } finally {
        showLoading(false);
    }
}

btnCopy.addEventListener("click", () => {
    if (!obfuscatedTextResult) return;
    navigator.clipboard.writeText(obfuscatedTextResult)
        .then(() => showToast("Copié dans le presse-papiers !", "success"))
        .catch(() => showToast("Impossible d'effectuer la copie.", "error"));
});

btnDownload.addEventListener("click", () => {
    if (!obfuscatedTextResult) return;
    const blob = new Blob([obfuscatedTextResult], { type: "text/plain;charset=utf-8" });
    triggerDownload(blob, "obfuscated_script.py");
});

btnDownloadFile.addEventListener("click", () => {
    if (!obfuscatedFileBlob) return;
    triggerDownload(obfuscatedFileBlob, obfuscatedFileName);
});

function triggerDownload(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
}

function showLoading(isLoading) {
    if (isLoading) {
        resultPlaceholder.style.display = "flex";
        placeholderMessage.style.display = "none";
        loader.style.display = "block";
        btnObfuscate.disabled = true;
        btnObfuscate.style.opacity = "0.7";
    } else {
        loader.style.display = "none";
        btnObfuscate.disabled = false;
        btnObfuscate.style.opacity = "1";
    }
}

function resetResultViews() {
    resultPlaceholder.style.display = "flex";
    placeholderMessage.style.display = "flex";
    loader.style.display = "none";
    resultContent.style.display = "none";
    resultFileContent.style.display = "none";
    obfuscatedTextResult = "";
    obfuscatedFileBlob = null;
    obfuscatedFileName = "";
    codeOutput.value = "";
    syncLineNumbers(codeOutput, outputLineNumbers);
}

function showToast(message, type = "success") {
    const container = document.getElementById("notification-container");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    
    const iconClass = type === "success" ? "fa-solid fa-circle-check" : "fa-solid fa-circle-exclamation";
    toast.innerHTML = `<i class="${iconClass}"></i><p>${message}</p>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = "slideIn 0.25s cubic-bezier(0, 0, 0.2, 1) reverse forwards";
        setTimeout(() => toast.remove(), 250);
    }, 4000);
}

function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Octets';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Octets', 'Ko', 'Mo', 'Go'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

syncLineNumbers(codeInput, lineNumbers, editorLinesCount);
syncLineNumbers(codeOutput, outputLineNumbers);