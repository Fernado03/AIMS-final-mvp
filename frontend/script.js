// Dialog Manager - Global for all pages
const dialogManager = {
    overlay: document.getElementById('customDialog'),
    title: document.getElementById('dialogTitle'),
    message: document.getElementById('dialogMessage'),
    okBtn: document.getElementById('dialogOkBtn'),
    cancelBtn: document.getElementById('dialogCancelBtn'),
    isOpen: false,

    // Show a confirmation dialog
    confirm: function (message, title = "Confirmation") {
        return new Promise((resolve) => {
            this.title.textContent = title;
            this.message.textContent = message;

            // Show cancel button
            this.cancelBtn.style.display = 'block';

            // Set up button handlers
            const handleOk = () => {
                this.close();
                this.okBtn.removeEventListener('click', handleOk);
                resolve(true);
            };

            const handleCancel = () => {
                this.close();
                this.cancelBtn.removeEventListener('click', handleCancel);
                resolve(false);
            };

            // Remove existing listeners and add new ones
            this.okBtn.replaceWith(this.okBtn.cloneNode(true));
            this.cancelBtn.replaceWith(this.cancelBtn.cloneNode(true));

            this.okBtn = document.getElementById('dialogOkBtn');
            this.cancelBtn = document.getElementById('dialogCancelBtn');

            this.okBtn.addEventListener('click', handleOk);
            this.cancelBtn.addEventListener('click', handleCancel);

            this.open();
        });
    },

    // Show an alert dialog
    alert: function (message, title = "Alert") {
        return new Promise((resolve) => {
            this.title.textContent = title;
            this.message.textContent = message;

            // Hide cancel button for alerts
            this.cancelBtn.style.display = 'none';

            // Set up button handler
            const handleOk = () => {
                this.close();
                this.okBtn.removeEventListener('click', handleOk);
                resolve(true);
            };

            // Remove existing listener and add new one
            this.okBtn.replaceWith(this.okBtn.cloneNode(true));
            this.okBtn = document.getElementById('dialogOkBtn');
            this.okBtn.addEventListener('click', handleOk);

            this.open();
        });
    },

    // Open the dialog
    open: function () {
        this.overlay.style.display = 'flex';
        this.isOpen = true;
    },

    // Close the dialog
    close: function () {
        this.overlay.style.display = 'none';
        this.isOpen = false;
    }
};

// Close dialog when clicking outside
if (dialogManager.overlay) {
    dialogManager.overlay.addEventListener('click', function (e) {
        if (e.target === dialogManager.overlay) {
            dialogManager.close();
        }
    });
}

// Close dialog with Escape key
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && dialogManager.isOpen) {
        dialogManager.close();
    }
});

// Make dialog accessible globally
window.dialogManager = dialogManager;

document.addEventListener('DOMContentLoaded', function () {
    // UI Elements - General
    const statusElement = document.getElementById('recordingStatus'); // Primarily for transcript1
    let currentNoteId = null;

    // --- Page Specific Elements & Logic ---
    const pathname = window.location.pathname;
    const API_BASE_URL = window.APP_CONFIG ? window.APP_CONFIG.API_BASE_URL : "http://127.0.0.1:5000";
    console.log('Current window.location.pathname:', pathname);
    console.log('Using API Base URL:', API_BASE_URL);

    // Function to get note_id from URL
    function getNoteIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('note_id');
    }

    // Function to fetch existing note data
    async function fetchNoteData(noteId) {
        if (!noteId) {
            console.warn("fetchNoteData called without noteId");
            return;
        }
        try {
            const response = await fetch(`${API_BASE_URL}/get_note_data/${noteId}`);
            if (!response.ok) {
                // If note not found (404), it might be a new note flow starting not from subjective.html
                // or an invalid ID. For now, just log and let specific page handlers decide.
                if (response.status === 404) {
                    console.warn(`Note ID ${noteId} not found in DB.`);
                    // If on objective, assessment, or plan page and note doesn't exist, redirect to subjective.html
                    if (!pathname.includes('subjective.html')) {
                        console.log("Redirecting to subjective.html as note was not found.");
                        window.location.href = 'subjective.html';
                    }
                    return null;
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log("Fetched note data:", data);

            // Populate fields based on current page
            if (pathname.includes('subjective.html')) {
                const transcriptTextarea = document.getElementById('transcript');
                if (transcriptTextarea) {
                    transcriptTextarea.value = data.subjective_text || "";
                    transcriptTextarea.readOnly = false; // Allow editing after loading
                }
            } else if (pathname.includes('objective.html')) {
                const objectiveTextarea = document.getElementById('objectiveText');
                if (objectiveTextarea) objectiveTextarea.value = data.objective_text || "";
            } else if (pathname.includes('assessment.html')) {
                const assessmentTextarea = document.getElementById('assessmentText');
                if (assessmentTextarea) assessmentTextarea.value = data.assessment_text || "";
            } else if (pathname.includes('plan.html')) {
                const planTextarea = document.getElementById('planText');
                if (planTextarea) planTextarea.value = data.plan_text || "";
            } else if (pathname.includes('summary.html')) {
                const summaryDisplayArea = document.getElementById('summaryDisplayArea');
                if (summaryDisplayArea) {
                    if (data.summary_text && data.summary_text.trim() !== "") {
                        summaryDisplayArea.textContent = data.summary_text;
                    } else {
                        summaryDisplayArea.textContent = "Summary not available yet or not generated. Click 'Generate Summary' to create one.";
                    }
                }
            }
            return data;
        } catch (error) {
            console.error("Error fetching note data:", error);
            alert("Error loading existing note data. Please check console.");
            if (!pathname.includes('subjective.html') && getNoteIdFromUrl()) { // If expecting a note and it fails to load
                console.log("Failed to load note, redirecting to subjective.html");
                window.location.href = 'subjective.html'; // Start fresh
            }
            return null;
        }
    }

    async function initializeNote() {
        let noteIdFromUrl = getNoteIdFromUrl();
        if (noteIdFromUrl) {
            currentNoteId = noteIdFromUrl;
            console.log("Existing note_id from URL:", currentNoteId);
            await fetchNoteData(currentNoteId);
        } else {
            if (pathname.includes('subjective.html')) {
                try {
                    const response = await fetch(`${API_BASE_URL}/create_note_session`, { method: 'POST' });
                    if (!response.ok) {
                        const errData = await response.json();
                        throw new Error(errData.error || 'Failed to create note session');
                    }
                    const data = await response.json();
                    currentNoteId = data.note_id;
                    console.log("New note session created, ID:", currentNoteId);
                    const newUrl = `${window.location.pathname}?note_id=${currentNoteId}`;
                    window.history.replaceState({ path: newUrl }, '', newUrl);
                    // After creating a new session, data might be empty, so no explicit fetchNoteData here unless needed.
                } catch (error) {
                    console.error("Error creating note session:", error);
                    alert(`Could not start a new note session: ${error.message}. Please try again or refresh.`);
                }
            } else {
                // For objective, assessment, plan pages, if no note_id, redirect to subjective.
                console.warn("No note_id found on a page that expects one. Redirecting to subjective.html.");
                window.location.href = 'subjective.html';
                return;
            }
        }
        if (currentNoteId) {
            updateBackButtonLinks(); // Ensure back buttons are updated after ID is confirmed/set
        }
    }

    function updateBackButtonLinks() {
        if (!currentNoteId) return; // Don't update if no ID

        // For subjective.html, back button is static to index.html, no note_id needed.
        // const backButtonSubjective = document.querySelector('a.page-back-button[href="index.html"]');

        // For objective.html
        const backButtonObjective = document.querySelector('a.page-back-button[href^="subjective.html"]'); // Selects if href starts with subjective.html
        if (backButtonObjective && pathname.includes('objective.html')) {
            backButtonObjective.href = `subjective.html?note_id=${currentNoteId}`;
        }

        // For assessment.html
        const backButtonAssessment = document.querySelector('a.page-back-button[href^="objective.html"]');
        if (backButtonAssessment && pathname.includes('assessment.html')) {
            backButtonAssessment.href = `objective.html?note_id=${currentNoteId}`;
        }

        // For plan.html
        const backButtonPlan = document.querySelector('a.page-back-button[href^="assessment.html"]');
        if (backButtonPlan && pathname.includes('plan.html')) {
            backButtonPlan.href = `assessment.html?note_id=${currentNoteId}`;
        }
    }

    initializeNote(); // Call after defining all functions it might use.

    // --- Subjective Page Specific Logic (includes Audio Recording) ---
    if (pathname.includes('subjective.html')) {
        const startButton = document.getElementById('startButton');
        const stopButton = document.getElementById('stopButton');
        const transcriptTextarea = document.getElementById('transcript');
        const audioFileInput = document.getElementById('audioFile');
        const transcribeFileButton = document.getElementById('transcribeFileButton');
        let mediaRecorder;
        let audioChunks = [];

        // Auto-hide status message after delay
        let statusTimeout;
        function setStatus(message, autoHide = false) {
            if (!statusElement) return;
            statusElement.textContent = message;

            // Clear any existing timeout
            if (statusTimeout) clearTimeout(statusTimeout);

            // Auto-hide after 3 seconds if requested
            if (autoHide && message) {
                statusTimeout = setTimeout(() => {
                    statusElement.textContent = '';
                }, 3000);
            }
        }

        // Initialize transcribeFileButton state
        if (transcribeFileButton) {
            transcribeFileButton.style.display = 'none'; // Hidden initially
        }

        // Add Event Listener to audioFileInput
        if (audioFileInput && transcribeFileButton) {
            audioFileInput.addEventListener('change', function () {
                if (audioFileInput.files.length > 0) {
                    transcribeFileButton.style.display = 'inline-flex';
                    transcribeFileButton.disabled = false; // ensure enabled and visible
                    setStatus && setStatus('File selected. Click "Transcribe File" to proceed.', true);
                } else {
                    transcribeFileButton.style.display = 'none';
                    transcribeFileButton.disabled = true;
                    setStatus && setStatus('');
                }
            });
        }

        // **D. Refactor Transcription Logic: New function handleAudioTranscription**
        async function handleAudioTranscription(audioData, fileNameForFormData) {
            console.log('🎙️ [TRANSCRIPTION START] Audio data size:', audioData.size, 'bytes; Name:', fileNameForFormData);
            const formData = new FormData();
            formData.append('file', audioData, fileNameForFormData);

            // Get overlay elements
            const overlay = document.getElementById('transcriptionOverlay');
            const overlayMessage = document.getElementById('transcriptionMessage');

            console.log('💻 [DEBUG] Overlay element found:', !!overlay);
            console.log('💻 [DEBUG] Overlay message element found:', !!overlayMessage);

            setStatus('Processing audio...');

            // Show loading overlay
            if (overlay) {
                console.log('✅ [OVERLAY] Showing loading overlay...');
                overlay.classList.add('active');
                const fileSizeMB = audioData.size / (1024 * 1024);
                console.log('📁 [FILE SIZE]', fileSizeMB.toFixed(2), 'MB');
                if (overlayMessage) {
                    if (fileSizeMB > 3) {
                        const msg = `Processing large file (${fileSizeMB.toFixed(1)}MB) - This may take up to a minute`;
                        overlayMessage.textContent = msg;
                        console.log('📢 [MESSAGE]', msg);
                    } else {
                        overlayMessage.textContent = 'Processing your audio file';
                        console.log('📢 [MESSAGE] Processing your audio file');
                    }
                }
            } else {
                console.error('❌ [ERROR] Overlay element not found!');
            }

            try {
                console.log('🚀 [FETCH] Sending request to /transcribe endpoint...');
                const startTime = Date.now();

                const response = await fetch(`${API_BASE_URL}/transcribe`, {
                    method: 'POST',
                    body: formData
                });

                const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
                console.log(`⏱️ [TIMING] Request completed in ${elapsed} seconds`);

                if (!response.ok) {
                    const errorText = await response.text();
                    console.error('❌ [ERROR] HTTP error:', response.status, errorText);
                    throw new Error(`HTTP error! ${response.status} ${errorText}`);
                }

                const data = await response.json();
                console.log('📝 [RESPONSE] Transcription data:', data);

                if (transcriptTextarea) {
                    if (data && data.text) {
                        // Append new transcript with space separator
                        const existingText = transcriptTextarea.value.trim();
                        transcriptTextarea.value = existingText ? existingText + ' ' + data.text : data.text;
                        setStatus('Transcription complete. You can edit.', true);
                    } else {
                        transcriptTextarea.value = `[Transcription error: ${data.error || 'No text'}]`;
                        setStatus('Transcription failed. You can type manually.', true);
                    }
                }
            } catch (error) {
                console.error("Error during transcription:", error);
                if (transcriptTextarea) transcriptTextarea.value = "[Transcription fetch error. Check console or type manually.]";
                setStatus('Transcription error.', true);
            } finally {
                // Hide loading overlay
                console.log('🚫 [OVERLAY] Hiding loading overlay...');
                if (overlay) {
                    overlay.classList.remove('active');
                    console.log('✅ [OVERLAY] Hidden successfully');
                } else {
                    console.error('❌ [ERROR] Overlay element not found when trying to hide!');
                }

                // Re-enable buttons
                if (startButton) startButton.disabled = false;
                if (stopButton) stopButton.disabled = true; // Stop should be disabled after processing
                if (transcribeFileButton && audioFileInput) {
                    const hasFile = audioFileInput.files.length > 0;
                    transcribeFileButton.style.display = hasFile ? 'inline-flex' : 'none';
                    transcribeFileButton.disabled = !hasFile; // re-enable when done
                }
                if (audioFileInput) audioFileInput.disabled = false; // Re-enable file input
            }
        }

        // Audio recording functions
        function coreStartRecording() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                console.error("getUserMedia not supported!");
                setStatus('getUserMedia not supported.');
                if (startButton) startButton.disabled = false;
                if (stopButton) stopButton.disabled = true;
                if (audioFileInput) audioFileInput.disabled = false; // Ensure file input enabled if start fails
                if (transcribeFileButton && audioFileInput) transcribeFileButton.style.display = (audioFileInput.files.length > 0) ? 'block' : 'none';
                return;
            }
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.start();
                    audioChunks = [];
                    mediaRecorder.ondataavailable = event => { audioChunks.push(event.data); };

                    // **E. Update mediaRecorder.onstop**
                    mediaRecorder.onstop = () => {
                        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        console.log('Live recording blob size:', audioBlob.size, 'bytes'); // Log blob size
                        audioChunks = []; // Clear chunks after creating blob
                        handleAudioTranscription(audioBlob, 'live_recording.webm');
                    };
                })
                .catch(err => {
                    console.error("Error setting up recording:", err);
                    setStatus('Mic permission error. Please allow microphone access.');
                    if (startButton) startButton.disabled = false;
                    if (stopButton) stopButton.disabled = true;
                    if (audioFileInput) audioFileInput.disabled = false; // Re-enable file input on error
                    if (transcribeFileButton && audioFileInput) transcribeFileButton.style.display = (audioFileInput.files.length > 0) ? 'block' : 'none';
                });
        }

        function coreStopRecording() {
            if (mediaRecorder && mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
            }
        }

        // **G. UI State Management for Start Recording Button**
        if (startButton) {
            startButton.onclick = function () {
                startButton.disabled = true;
                if (stopButton) stopButton.disabled = false;
                setStatus('Recording...');
                // Don't clear transcript - append mode

                // Disable file upload elements
                if (audioFileInput) {
                    audioFileInput.value = ''; // Clear selected file
                    audioFileInput.disabled = true;
                }
                if (transcribeFileButton) transcribeFileButton.style.display = 'none'; // Hide button

                coreStartRecording();
            };
        }

        if (stopButton) {
            stopButton.onclick = function () {
                // startButton will be re-enabled in handleAudioTranscription's finally block
                // stopButton will be re-enabled in handleAudioTranscription's finally block
                // File inputs will be re-enabled in handleAudioTranscription's finally block
                coreStopRecording();
            };
        }

        // **H. Add Keyboard Shortcuts**
        document.addEventListener('keydown', function (event) {
            // Ctrl+R or Cmd+R to start recording
            if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
                event.preventDefault(); // Prevent browser reload
                if (startButton && !startButton.disabled) {
                    startButton.click();
                    console.log('🎤 Keyboard shortcut: Started recording (Ctrl+R)');
                }
            }
            // Ctrl+S or Cmd+S to stop recording
            if ((event.ctrlKey || event.metaKey) && event.key === 's') {
                event.preventDefault(); // Prevent browser save dialog
                if (stopButton && !stopButton.disabled) {
                    stopButton.click();
                    console.log('⏹️ Keyboard shortcut: Stopped recording (Ctrl+S)');
                }
            }
        });

        // **F. Add Click Handler for transcribeFileButton**
        console.log('💻 [DEBUG] Checking transcribe button elements:', {
            transcribeFileButton: !!transcribeFileButton,
            audioFileInput: !!audioFileInput,
            statusElement: !!statusElement,
            transcriptTextarea: !!transcriptTextarea,
            startButton: !!startButton,
            stopButton: !!stopButton
        });

        if (transcribeFileButton && audioFileInput) {
            console.log('✅ [SETUP] Attaching click handler to Transcribe File button');
            transcribeFileButton.onclick = async function () {
                transcribeFileButton.disabled = true; // immediately disable to prevent double clicks
                console.log('👆 [CLICK] Transcribe File button clicked!');
                console.log('📁 [FILES] Files selected:', audioFileInput.files.length);
                if (!audioFileInput.files || audioFileInput.files.length === 0) {
                    alert('Please select an audio file first.');
                    setStatus('Please select an audio file first.', true);
                    return;
                }

                const file = audioFileInput.files[0];

                // Check file size and warn user about processing time
                const fileSizeMB = file.size / (1024 * 1024);
                console.log(`📁 File size: ${fileSizeMB.toFixed(2)} MB`);

                if (fileSizeMB > 3) {
                    transcribeFileButton.disabled = false; // allow interaction during confirm
                    // Estimate duration (rough: 1MB ≈ 1 minute for compressed audio)
                    const estimatedMinutes = Math.ceil(fileSizeMB);
                    const warningMsg = `This is a large file (${fileSizeMB.toFixed(1)}MB, ~${estimatedMinutes} min audio).\n\nTranscription may take 30-60 seconds.\n\nContinue?`;
                    const confirmed = await window.dialogManager.confirm(warningMsg, "Large File Warning");
                    if (!confirmed) {
                        return; // User cancelled
                    }
                }

                transcribeFileButton.disabled = true;
                if (startButton) startButton.disabled = true;
                if (stopButton) stopButton.disabled = true;
                // Don't clear transcript - keep previous content

                // Show different message for large vs small files
                const statusMsg = fileSizeMB > 3
                    ? `Transcribing large file... This may take up to a minute. Please wait.`
                    : "Uploading and transcribing file...";
                if (statusElement) statusElement.textContent = statusMsg;

                console.log('🚀 [ACTION] Calling handleAudioTranscription...');
                handleAudioTranscription(file, file.name);
            };
        } else {
            console.error('❌ [ERROR] Could not attach click handler! Missing elements:', {
                transcribeFileButton: !!transcribeFileButton,
                audioFileInput: !!audioFileInput
            });
        }

        // **G. UI State Management for File Input Change (complementary to start recording)**
        if (audioFileInput) {
            audioFileInput.addEventListener('change', function () {
                if (audioFileInput.files.length > 0) {
                    // If a file is selected, we might want to disable recording buttons
                    // or ensure recording is stopped if it was active.
                    // For now, enabling transcribe button is handled by its own listener.
                    // This part ensures that if a recording was active, selecting a file
                    // might implicitly stop it (though not explicitly implemented here yet)
                    // or at least the UI should reflect a shift in focus to file upload.
                    if (mediaRecorder && mediaRecorder.state === "recording") {
                        // console.warn("File selected while recording was active. Consider stopping recording.");
                        // coreStopRecording(); // Optionally stop recording
                        // Or alert the user:
                        // alert("Selecting a file will stop the current recording if active.");
                    }
                    if (startButton) startButton.disabled = true; // Disable start if a file is chosen
                    if (stopButton) stopButton.disabled = true; // Disable stop as well
                } else {
                    // No file selected, re-enable recording buttons if not already managed elsewhere
                    if (startButton) startButton.disabled = false;
                }
            });
        }

        // Remove old transcribeFileButton.onclick and related UI management logic
        // as it's now integrated into handleAudioTranscription and new event listeners.
        // The old logic from lines 239-298 and 300-336 is superseded.




        const nextButtonSubjective = document.getElementById('nextButtonSubjective');
        if (nextButtonSubjective) {
            // If the button is inside an <a> tag, prevent default navigation
            if (nextButtonSubjective.closest('a')) {
                nextButtonSubjective.closest('a').addEventListener('click', function (event) {
                    event.preventDefault();
                });
            }
            nextButtonSubjective.onclick = async function () { // Removed event param as it's not used if not preventing default on <a>
                if (!currentNoteId) {
                    alert("Error: Note session not initialized. Please refresh the page.");
                    return;
                }
                const subjectiveText = transcriptTextarea ? transcriptTextarea.value : "";
                const confirmed = await window.dialogManager.confirm("Save Subjective data and proceed to Objective page?", "Save and Continue");
                if (confirmed) {
                    try {
                        const response = await fetch(`${API_BASE_URL}/update_note_subjective`, {
                            method: 'POST', headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ note_id: currentNoteId, subjective_text: subjectiveText })
                        });
                        if (!response.ok) {
                            const errText = await response.text();
                            try {
                                const err = JSON.parse(errText);
                                throw new Error(err.error || `Save failed: ${response.status}`);
                            } catch (e) {
                                throw new Error(`Save failed: ${response.status} - ${errText}`);
                            }
                        }
                        // const result = await response.json(); // Assuming success returns some JSON
                        // console.log("Subjective save result:", result);
                        window.location.href = `objective.html?note_id=${currentNoteId}`;
                    } catch (error) {
                        console.error("Error saving subjective data:", error);
                        alert(`Error saving subjective data: ${error.message}`);
                    }
                }
            };
        }
    }

    // --- Objective Page Specific Logic ---
    if (pathname.includes('objective.html')) {
        const objectiveTextarea = document.getElementById('objectiveText');
        // const assessmentTextarea = document.getElementById('assessmentText'); // This will be on assessment.html
        const nextButtonObjective = document.getElementById('nextButtonObjective'); // Assuming an ID like 'nextButtonObjective'

        if (nextButtonObjective) {
            if (nextButtonObjective.closest('a')) {
                nextButtonObjective.closest('a').addEventListener('click', function (event) {
                    event.preventDefault();
                });
            }
            nextButtonObjective.onclick = async function () {
                const objectiveLoadingIndicator = document.getElementById('objectiveLoadingIndicator'); // Get ref

                if (!currentNoteId) { alert("Error: Note ID missing. Please navigate from the start."); return; }
                const objectiveText = objectiveTextarea ? objectiveTextarea.value : "";

                const confirmed = await window.dialogManager.confirm("Save Objective data and proceed to Assessment page?", "Save and Continue");
                if (confirmed) {
                    if (objectiveLoadingIndicator) objectiveLoadingIndicator.style.display = 'block'; // Show indicator
                    nextButtonObjective.disabled = true; // Disable button

                    try {
                        const response = await fetch(`${API_BASE_URL}/update_note_objective`, { // Changed endpoint
                            method: 'POST', headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                note_id: currentNoteId,
                                objective_text: objectiveText
                                // assessment_text: assessmentText // Removed, will be separate
                            })
                        });
                        if (!response.ok) {
                            const errText = await response.text();
                            try { const err = JSON.parse(errText); throw new Error(err.error || `Save failed: ${response.status}`); }
                            catch (e) { throw new Error(`Save failed: ${response.status} - ${errText}`); }
                        }
                        // await response.json();
                        window.location.href = `assessment.html?note_id=${currentNoteId}`; // Navigate to assessment
                    } catch (error) {
                        console.error("Error saving objective data:", error);
                        alert(`Error saving Objective data: ${error.message}`);
                        if (objectiveLoadingIndicator) objectiveLoadingIndicator.style.display = 'none'; // Hide on error
                        nextButtonObjective.disabled = false; // Re-enable on error
                    }
                } else {
                    // User cancelled confirm
                    if (objectiveLoadingIndicator) objectiveLoadingIndicator.style.display = 'none'; // Ensure hidden
                    nextButtonObjective.disabled = false;
                }
            };
        }
    }

    // --- Assessment Page Specific Logic ---
    if (pathname.includes('assessment.html')) {
        const assessmentTextarea = document.getElementById('assessmentText');
        const nextButtonAssessment = document.getElementById('nextButtonAssessment');
        const generateAssessmentButton = document.getElementById('generateAssessmentButton');
        const assessmentPageLoadingIndicator = document.getElementById('assessmentPageLoadingIndicator'); // Renamed/confirmed ID

        if (generateAssessmentButton && assessmentTextarea) {
            generateAssessmentButton.onclick = async function () {
                if (!currentNoteId) {
                    alert("Error: Note ID missing. Please refresh or navigate from the start.");
                    return;
                }

                // First, check if we have the required S/O data
                try {
                    const checkResponse = await fetch(`http://127.0.0.1:5000/get_note_data/${currentNoteId}`);
                    if (checkResponse.ok) {
                        const noteData = await checkResponse.json();
                        const hasSubjective = noteData.subjective_text && noteData.subjective_text.trim().length > 0;
                        const hasObjective = noteData.objective_text && noteData.objective_text.trim().length > 0;

                        if (!hasSubjective || !hasObjective) {
                            let missingSteps = [];
                            if (!hasSubjective) missingSteps.push('Subjective');
                            if (!hasObjective) missingSteps.push('Objective');

                            const message = `Cannot generate Assessment. Missing required data:\n\n${missingSteps.join(' and ')} section(s) need to be completed first.\n\nWould you like to go back and complete them?`;

                            if (await window.dialogManager.confirm(message, "Missing Data")) {
                                // Navigate to the first missing section
                                if (!hasSubjective) {
                                    window.location.href = `subjective.html?note_id=${currentNoteId}`;
                                } else if (!hasObjective) {
                                    window.location.href = `objective.html?note_id=${currentNoteId}`;
                                }
                            }
                            return;
                        }
                    }
                } catch (error) {
                    console.error("Error checking note data:", error);
                    // Continue anyway, let the backend handle it
                }

                // Show inline loading state on the button (no spinner next to it)
                const originalTextGA = generateAssessmentButton.textContent;
                generateAssessmentButton.textContent = 'Generating...';
                generateAssessmentButton.disabled = true;

                try {
                    const response = await fetch(`${API_BASE_URL}/api/generate_assessment/${currentNoteId}`, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const response_data = await response.json(); // Try to parse JSON regardless of response.ok for error messages

                    if (!response.ok) {
                        throw new Error(response_data.error || `Failed to generate assessment. Status: ${response.status}`);
                    }

                    if (response_data.assessment_text) {
                        assessmentTextarea.value = response_data.assessment_text;
                        await window.dialogManager.alert("Assessment generated successfully!", "Success");
                    } else if (response_data.error) {
                        await window.dialogManager.alert(`Error: ${response_data.error}`, "Generation Failed");
                    } else {
                        await window.dialogManager.alert("Received an unexpected response from the server.", "Error");
                    }
                } catch (error) {
                    console.error("Error generating assessment:", error);
                    await window.dialogManager.alert(`Failed to generate assessment.\n\nError: ${error.message}`, "Generation Failed");
                } finally {
                    generateAssessmentButton.textContent = originalTextGA;
                    generateAssessmentButton.disabled = false;
                }
            };
        }

        if (nextButtonAssessment) {
            if (nextButtonAssessment.closest('a')) {
                nextButtonAssessment.closest('a').addEventListener('click', function (event) {
                    event.preventDefault();
                });
            }
            nextButtonAssessment.onclick = async function () {
                if (!currentNoteId) {
                    alert("Error: Note ID missing. Please navigate from the start.");
                    return;
                }
                const assessmentText = assessmentTextarea ? assessmentTextarea.value : "";

                const confirmed = await window.dialogManager.confirm("Save Assessment data and proceed to Plan page?", "Save and Continue");
                if (confirmed) {
                    // Removed loading indicator display for this button as per instructions
                    nextButtonAssessment.disabled = true; // Disable button

                    try {
                        const response = await fetch(`${API_BASE_URL}/update_note_assessment`, {
                            method: 'POST', headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                note_id: currentNoteId,
                                assessment_text: assessmentText
                            })
                        });
                        if (!response.ok) {
                            const errText = await response.text();
                            try { const err = JSON.parse(errText); throw new Error(err.error || `Save failed: ${response.status}`); }
                            catch (e) { throw new Error(`Save failed: ${response.status} - ${errText}`); }
                        }
                        window.location.href = `plan.html?note_id=${currentNoteId}`; // Navigate to plan
                    } catch (error) {
                        console.error("Error saving assessment data:", error);
                        alert(`Error saving Assessment data: ${error.message}`);
                        // Removed loading indicator hide on error
                        nextButtonAssessment.disabled = false; // Re-enable on error
                    }
                } else {
                    // User cancelled confirm
                    // Removed loading indicator hide
                    nextButtonAssessment.disabled = false; // Re-enable button
                }
            };
        }
    }

    // --- Plan Page Specific Logic ---
    if (pathname.includes('plan.html')) {
        const planTextarea = document.getElementById('planText');
        const summarizeButtonPlan = document.getElementById('summarizeButtonPlan');
        const planLoadingIndicator = document.getElementById('planLoadingIndicator');
        const generatePlanButton = document.getElementById('generatePlanButton'); // New button

        if (generatePlanButton && planTextarea) {
            generatePlanButton.onclick = async function () {
                if (!currentNoteId) {
                    alert("Error: Note ID missing. Please refresh or navigate from the start.");
                    return;
                }

                // First, check if we have the required S/O/A data
                try {
                    const checkResponse = await fetch(`${API_BASE_URL}/get_note_data/${currentNoteId}`);
                    if (checkResponse.ok) {
                        const noteData = await checkResponse.json();
                        const hasSubjective = noteData.subjective_text && noteData.subjective_text.trim().length > 0;
                        const hasObjective = noteData.objective_text && noteData.objective_text.trim().length > 0;
                        const hasAssessment = noteData.assessment_text && noteData.assessment_text.trim().length > 0;

                        if (!hasSubjective || !hasObjective || !hasAssessment) {
                            let missingSteps = [];
                            if (!hasSubjective) missingSteps.push('Subjective');
                            if (!hasObjective) missingSteps.push('Objective');
                            if (!hasAssessment) missingSteps.push('Assessment');

                            const message = `Cannot generate Plan. Missing required data:\n\n${missingSteps.join(', ')} section(s) need to be completed first.\n\nWould you like to go back and complete them?`;

                            if (await window.dialogManager.confirm(message, "Missing Data")) {
                                // Navigate to the first missing section
                                if (!hasSubjective) {
                                    window.location.href = `subjective.html?note_id=${currentNoteId}`;
                                } else if (!hasObjective) {
                                    window.location.href = `objective.html?note_id=${currentNoteId}`;
                                } else if (!hasAssessment) {
                                    window.location.href = `assessment.html?note_id=${currentNoteId}`;
                                }
                            }
                            return;
                        }
                    }
                } catch (error) {
                    console.error("Error checking note data:", error);
                    // Continue anyway, let the backend handle it
                }

                // Show inline loading state on the button (no spinner next to it)
                const originalTextGP = generatePlanButton.textContent;
                generatePlanButton.textContent = 'Generating...';
                generatePlanButton.disabled = true;
                if (summarizeButtonPlan) summarizeButtonPlan.disabled = true; // Disable next button too

                try {
                    const response = await fetch(`${API_BASE_URL}/api/generate_plan/${currentNoteId}`, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const response_data = await response.json();

                    if (!response.ok) {
                        throw new Error(response_data.error || `Failed to generate plan. Status: ${response.status}`);
                    }

                    if (response_data.plan_text) {
                        planTextarea.value = response_data.plan_text;
                        await window.dialogManager.alert("Plan generated successfully!", "Success");
                    } else if (response_data.error) {
                        await window.dialogManager.alert(`Error: ${response_data.error}`, "Generation Failed");
                    } else {
                        await window.dialogManager.alert("Received an unexpected response from the server.", "Error");
                    }
                } catch (error) {
                    console.error("Error generating plan:", error);
                    await window.dialogManager.alert(`Failed to generate plan.\n\nError: ${error.message}`, "Generation Failed");
                } finally {
                    generatePlanButton.textContent = originalTextGP;
                    generatePlanButton.disabled = false;
                    if (summarizeButtonPlan) summarizeButtonPlan.disabled = false;
                }
            };
        }

        if (summarizeButtonPlan) {
            if (summarizeButtonPlan.closest('a')) {
                summarizeButtonPlan.closest('a').addEventListener('click', function (event) {
                    event.preventDefault();
                });
            }
            summarizeButtonPlan.onclick = async function () {
                if (!currentNoteId) {
                    alert("Error: Note ID missing. Please navigate from the start.");
                    return;
                }
                const planText = planTextarea ? planTextarea.value : "";

                // Confirmation message changed slightly as plan generation is now separate
                const confirmed = await window.dialogManager.confirm("Save this Plan and proceed to Summary?", "Save and Continue");
                if (confirmed) {
                    // No loading indicator display here for THIS button as per instructions
                    // (it was for summary generation, which is now implicitly on the backend after plan save)
                    summarizeButtonPlan.disabled = true;
                    if (generatePlanButton) generatePlanButton.disabled = true; // Disable generate button too

                    try {
                        const response = await fetch(`${API_BASE_URL}/update_note_plan`, {
                            method: 'POST', headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                note_id: currentNoteId,
                                plan_text: planText
                            })
                        });
                        if (!response.ok) {
                            const errText = await response.text();
                            let errorMsg;
                            try {
                                const err = JSON.parse(errText);
                                errorMsg = err.error || `Save failed: ${response.status}`;
                            } catch (e) {
                                errorMsg = `Save failed: ${response.status} - ${errText}`;
                            }
                            throw new Error(errorMsg);
                        }
                        console.log("Plan saved. Backend will attempt summary generation if applicable.");
                        window.location.href = `summary.html?note_id=${currentNoteId}`;
                    } catch (error) {
                        console.error("Error saving plan data:", error);
                        alert(`Error saving Plan data: ${error.message}`);
                        // No loading indicator to hide here for this button
                        summarizeButtonPlan.disabled = false;
                        if (generatePlanButton) generatePlanButton.disabled = false;
                    }
                } else {
                    // User cancelled confirm
                    // No loading indicator to hide
                    summarizeButtonPlan.disabled = false;
                    if (generatePlanButton) generatePlanButton.disabled = false;
                }
            };
        }
    }

    // --- Summary Page Specific Logic ---
    if (pathname.includes('summary.html')) {
        const summaryLoadingIndicator = document.getElementById('summaryLoadingIndicator');
        const summaryDisplayArea = document.getElementById('summaryDisplayArea');
        const exportContainer = document.getElementById('exportContainer');

        console.log('Summary page loaded. Checking for note ID...');

        // Auto-generate summary function
        async function autoGenerateSummary() {
            if (!summaryLoadingIndicator || !summaryDisplayArea) {
                console.error('Summary page elements not found');
                return;
            }

            // Wait for currentNoteId to be set by initializeNote()
            let attempts = 0;
            while (!currentNoteId && attempts < 10) {
                await new Promise(resolve => setTimeout(resolve, 100));
                attempts++;
            }

            if (!currentNoteId) {
                console.log('Auto-generating summary for note ID:', currentNoteId);
                await window.dialogManager.alert("Note ID is not available. Please navigate from the Plan page.", "Error");
                window.location.href = 'plan.html';
                return;
            }

            // First, check if we have ALL required SOAP data
            try {
                const checkResponse = await fetch(`${API_BASE_URL}/get_note_data/${currentNoteId}`);
                if (checkResponse.ok) {
                    const noteData = await checkResponse.json();
                    const hasSubjective = noteData.subjective_text && noteData.subjective_text.trim().length > 0;
                    const hasObjective = noteData.objective_text && noteData.objective_text.trim().length > 0;
                    const hasAssessment = noteData.assessment_text && noteData.assessment_text.trim().length > 0;
                    const hasPlan = noteData.plan_text && noteData.plan_text.trim().length > 0;

                    if (!hasSubjective || !hasObjective || !hasAssessment || !hasPlan) {
                        let missingSteps = [];
                        if (!hasSubjective) missingSteps.push('Subjective');
                        if (!hasObjective) missingSteps.push('Objective');
                        if (!hasAssessment) missingSteps.push('Assessment');
                        if (!hasPlan) missingSteps.push('Plan');

                        const message = `Cannot generate Summary. Missing required data:\n\n${missingSteps.join(', ')} section(s) need to be completed first.\n\nWould you like to go back and complete them?`;

                        summaryLoadingIndicator.style.display = 'none';
                        if (await window.dialogManager.confirm(message, "Missing Data")) {
                            // Navigate to the first missing section
                            if (!hasSubjective) {
                                window.location.href = `subjective.html?note_id=${currentNoteId}`;
                            } else if (!hasObjective) {
                                window.location.href = `objective.html?note_id=${currentNoteId}`;
                            } else if (!hasAssessment) {
                                window.location.href = `assessment.html?note_id=${currentNoteId}`;
                            } else if (!hasPlan) {
                                window.location.href = `plan.html?note_id=${currentNoteId}`;
                            }
                        }
                        return;
                    }
                }
            } catch (error) {
                console.error("Error checking note data:", error);
                // Continue anyway, let the backend handle it
            }

            summaryLoadingIndicator.style.display = 'flex';
            summaryDisplayArea.style.display = 'none';

            try {
                console.log(`Auto-fetching summary from: http://127.0.0.1:5000/api/generate_summary/${currentNoteId}`);
                const response = await fetch(`${API_BASE_URL}/api/generate_summary/${currentNoteId}`, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' }
                });

                const response_data = await response.json();
                console.log('Response from /api/generate_summary:', response_data);

                if (!response.ok) {
                    throw new Error(response_data.error || `Failed to generate summary. Status: ${response.status}`);
                }

                if (response_data.summary_text) {
                    summaryDisplayArea.textContent = response_data.summary_text;
                    summaryDisplayArea.style.display = 'block';
                    if (exportContainer) exportContainer.style.display = 'flex';
                } else {
                    summaryDisplayArea.textContent = "Failed to generate summary. No text returned.";
                    summaryDisplayArea.style.display = 'block';
                }
            } catch (error) {
                console.error("Error in auto-generate summary:", error);
                summaryDisplayArea.textContent = `Error generating summary: ${error.message}`;
                summaryDisplayArea.style.display = 'block';
                await window.dialogManager.alert(`Error generating summary: ${error.message}`, "Generation Failed");
            } finally {
                summaryLoadingIndicator.style.display = 'none';
            }
        }

        // Trigger auto-generation
        autoGenerateSummary();
    }

    // Back button for summary page (if one exists and needs dynamic note_id)
    const backButtonSummary = document.querySelector('a.page-back-button[href^="plan.html"]');
    if (backButtonSummary) {
        const noteId = getNoteIdFromUrl() || currentNoteId;
        if (noteId) backButtonSummary.href = `plan.html?note_id=${noteId}`;
    }
});

// Export functionality for summary page
document.addEventListener('DOMContentLoaded', function () {
    const exportButton = document.getElementById('exportButton');
    const exportOptions = document.getElementById('exportOptions');
    const summaryDisplayArea = document.getElementById('summaryDisplayArea');

    if (exportButton && exportOptions && summaryDisplayArea) {
        // Toggle export options dropdown
        exportButton.addEventListener('click', function (e) {
            e.stopPropagation();
            exportOptions.style.display = exportOptions.style.display === 'block' ? 'none' : 'block';
        });

        // Close dropdown when clicking elsewhere
        document.addEventListener('click', function () {
            exportOptions.style.display = 'none';
        });

        // Handle export option clicks
        exportOptions.addEventListener('click', function (e) {
            e.stopPropagation();
            const format = e.target.getAttribute('data-format');
            if (!format) return;

            const content = summaryDisplayArea.textContent;
            if (!content || content.trim() === '') {
                alert('No content to export. Please generate a summary first.');
                return;
            }

            if (format === 'txt') {
                exportAsTxt(content);
            } else if (format === 'pdf') {
                exportAsPdf(content);
            }
        });
    }

    function exportAsTxt(content) {
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'summary.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    function exportAsPdf(content) {
        // Use browser's print functionality for simple PDF export
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Summary</title>
                    <style>
                        body { font-family: Arial, sans-serif; padding: 20px; }
                        pre { white-space: pre-wrap; font-family: inherit; }
                    </style>
                </head>
                <body>
                    <pre>${content}</pre>
                    <script>
                        window.onload = function() {
                            setTimeout(function() {
                                window.print();
                                window.close();
                            }, 200);
                        };
                    </script>
                </body>
            </html>
        `);
        printWindow.document.close();
    }
});