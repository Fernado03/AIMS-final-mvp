// Dialog Manager - Global for all pages
const dialogManager = {
    overlay: document.getElementById('customDialog'),
    title: document.getElementById('dialogTitle'),
    message: document.getElementById('dialogMessage'),
    okBtn: document.getElementById('dialogOkBtn'),
    cancelBtn: document.getElementById('dialogCancelBtn'),
    isOpen: false,
    
    // Show a confirmation dialog
    confirm: function(message, title = "Confirmation") {
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
    alert: function(message, title = "Alert") {
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
    open: function() {
        this.overlay.style.display = 'flex';
        this.isOpen = true;
    },
    
    // Close the dialog
    close: function() {
        this.overlay.style.display = 'none';
        this.isOpen = false;
    }
};

// Close dialog when clicking outside
if (dialogManager.overlay) {
    dialogManager.overlay.addEventListener('click', function(e) {
        if (e.target === dialogManager.overlay) {
            dialogManager.close();
        }
    });
}

// Close dialog with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && dialogManager.isOpen) {
        dialogManager.close();
    }
});

// Make dialog accessible globally
window.dialogManager = dialogManager;

document.addEventListener('DOMContentLoaded', function() {
    // UI Elements - General
    const statusElement = document.getElementById('recordingStatus'); // Primarily for transcript1
    let currentNoteId = null;

    // --- Page Specific Elements & Logic ---
    const pathname = window.location.pathname;
    console.log('Current window.location.pathname:', pathname);

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
            const response = await fetch(`http://127.0.0.1:5000/get_note_data/${noteId}`);
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
                    const response = await fetch('http://127.0.0.1:5000/create_note_session', { method: 'POST' });
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
        const audioFileInput = document.getElementById('audioFile'); // Existing
        const transcribeFileButton = document.getElementById('transcribeFileButton'); // Existing
        const selectedFileNameElement = document.getElementById('selectedFileName'); // **A. Get new element**
        let mediaRecorder;
        let audioChunks = [];

        // **B. Initialize transcribeFileButton state**
        if (transcribeFileButton) {
            transcribeFileButton.disabled = true;
        }

        // **C. Add Event Listener to audioFileInput**
        if (audioFileInput && transcribeFileButton && selectedFileNameElement && statusElement) {
            audioFileInput.addEventListener('change', function() {
                if (audioFileInput.files.length > 0) {
                    transcribeFileButton.disabled = false;
                    selectedFileNameElement.textContent = `Selected: ${audioFileInput.files[0].name}`;
                    statusElement.textContent = 'File selected. Click "Transcribe File" to proceed.';
                } else {
                    transcribeFileButton.disabled = true;
                    selectedFileNameElement.textContent = '';
                    statusElement.textContent = '';
                }
            });
        }

        // **D. Refactor Transcription Logic: New function handleAudioTranscription**
        async function handleAudioTranscription(audioData, fileNameForFormData) {
            console.log('Audio data size being processed:', audioData.size, 'bytes; Name:', fileNameForFormData); // Log audio data size
            const formData = new FormData();
            formData.append('file', audioData, fileNameForFormData);

            if(statusElement) statusElement.textContent = 'Processing audio...';
            if(transcriptTextarea) transcriptTextarea.value = ''; // Clear previous transcript

            try {
                const response = await fetch('http://127.0.0.1:5000/transcribe', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP error! ${response.status} ${errorText}`);
                }

                const data = await response.json();

                if (transcriptTextarea) {
                    if (data && data.text) {
                        transcriptTextarea.value = data.text;
                        if(statusElement) statusElement.textContent = 'Transcription complete. You can edit.';
                    } else {
                        transcriptTextarea.value = `[Transcription error: ${data.error || 'No text'}]`;
                        if(statusElement) statusElement.textContent = 'Transcription failed. You can type manually.';
                    }
                }
            } catch (error) {
                console.error("Error during transcription:", error);
                if (transcriptTextarea) transcriptTextarea.value = "[Transcription fetch error. Check console or type manually.]";
                if(statusElement) statusElement.textContent = 'Transcription error.';
            } finally {
                // Re-enable buttons
                if(startButton) startButton.disabled = false;
                if(stopButton) stopButton.disabled = true; // Stop should be disabled after processing
                if(transcribeFileButton) transcribeFileButton.disabled = (audioFileInput && audioFileInput.files.length === 0); // Re-enable if a file is still selected
                if(audioFileInput) audioFileInput.disabled = false; // Re-enable file input
            }
        }

        // Audio recording functions
        function coreStartRecording() {
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                console.error("getUserMedia not supported!");
                if(statusElement) statusElement.textContent = 'getUserMedia not supported.';
                if(startButton) startButton.disabled = false;
                if(stopButton) stopButton.disabled = true;
                if(audioFileInput) audioFileInput.disabled = false; // Ensure file input enabled if start fails
                if(transcribeFileButton) transcribeFileButton.disabled = (audioFileInput && audioFileInput.files.length === 0);
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
                    if(statusElement) statusElement.textContent = 'Mic permission error. Please allow microphone access.';
                    if(startButton) startButton.disabled = false;
                    if(stopButton) stopButton.disabled = true;
                    if(audioFileInput) audioFileInput.disabled = false; // Re-enable file input on error
                    if(transcribeFileButton) transcribeFileButton.disabled = (audioFileInput && audioFileInput.files.length === 0);
                });
        }

        function coreStopRecording() {
            if (mediaRecorder && mediaRecorder.state !== "inactive") {
                mediaRecorder.stop();
            }
        }

        // **G. UI State Management for Start Recording Button**
        if (startButton) {
            startButton.onclick = function() {
                startButton.disabled = true;
                if(stopButton) stopButton.disabled = false;
                if(statusElement) statusElement.textContent = 'Recording...';
                if(transcriptTextarea) transcriptTextarea.value = ''; // Clear transcript

                // Disable file upload elements
                if(audioFileInput) {
                    audioFileInput.value = ''; // Clear selected file
                    audioFileInput.disabled = true;
                }
                if(selectedFileNameElement) selectedFileNameElement.textContent = '';
                if(transcribeFileButton) transcribeFileButton.disabled = true;

                coreStartRecording();
            };
        }

        if (stopButton) {
            stopButton.onclick = function() {
                // startButton will be re-enabled in handleAudioTranscription's finally block
                // stopButton will be re-enabled in handleAudioTranscription's finally block
                // File inputs will be re-enabled in handleAudioTranscription's finally block
                coreStopRecording();
            };
        }

        // **F. Add Click Handler for transcribeFileButton**
        if (transcribeFileButton && audioFileInput && statusElement && transcriptTextarea && startButton && stopButton) {
            transcribeFileButton.onclick = function() {
                if (!audioFileInput.files || audioFileInput.files.length === 0) {
                    alert('Please select an audio file first.');
                    if(statusElement) statusElement.textContent = 'Please select an audio file first.';
                    return;
                }

                const file = audioFileInput.files[0];
                // Basic type check (can be enhanced)
                // const acceptedTypes = ['audio/mpeg', 'audio/wav', 'audio/wave', 'audio/x-wav', 'audio/m4a', 'audio/x-m4a', 'audio/mp4', 'audio/webm', 'audio/ogg'];
                // if (!acceptedTypes.includes(file.type)) {
                //     alert('Invalid file type. Please upload a common audio file (MP3, WAV, M4A, WebM, OGG).');
                //     if(statusElement) statusElement.textContent = 'Invalid file type.';
                //     audioFileInput.value = ''; // Clear the input
                //     if(selectedFileNameElement) selectedFileNameElement.textContent = '';
                //     transcribeFileButton.disabled = true;
                //     return;
                // }

                transcribeFileButton.disabled = true;
                if(startButton) startButton.disabled = true;
                if(stopButton) stopButton.disabled = true;
                if(transcriptTextarea) transcriptTextarea.value = ''; // Clear previous transcript
                if(statusElement) statusElement.textContent = "Uploading and transcribing file...";

                handleAudioTranscription(file, file.name);
            };
        }
        
        // **G. UI State Management for File Input Change (complementary to start recording)**
        if (audioFileInput) {
            audioFileInput.addEventListener('change', function() {
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
                    if(startButton) startButton.disabled = true; // Disable start if a file is chosen
                    if(stopButton) stopButton.disabled = true; // Disable stop as well
                } else {
                    // No file selected, re-enable recording buttons if not already managed elsewhere
                    if(startButton) startButton.disabled = false;
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
                nextButtonSubjective.closest('a').addEventListener('click', function(event) {
                    event.preventDefault();
                });
            }
            nextButtonSubjective.onclick = async function() { // Removed event param as it's not used if not preventing default on <a>
                if (!currentNoteId) {
                    alert("Error: Note session not initialized. Please refresh the page.");
                    return;
                }
                const subjectiveText = transcriptTextarea ? transcriptTextarea.value : "";
                const confirmed = await window.dialogManager.confirm("Save Subjective data and proceed to Objective page?", "Save and Continue");
                if (confirmed) {
                    try {
                        const response = await fetch('http://127.0.0.1:5000/update_note_subjective', {
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
                nextButtonObjective.closest('a').addEventListener('click', function(event) {
                    event.preventDefault();
                });
            }
            nextButtonObjective.onclick = async function() {
                const objectiveLoadingIndicator = document.getElementById('objectiveLoadingIndicator'); // Get ref

                if (!currentNoteId) { alert("Error: Note ID missing. Please navigate from the start."); return; }
                const objectiveText = objectiveTextarea ? objectiveTextarea.value : "";

                const confirmed = await window.dialogManager.confirm("Save Objective data and proceed to Assessment page?", "Save and Continue");
                if (confirmed) {
                    if (objectiveLoadingIndicator) objectiveLoadingIndicator.style.display = 'block'; // Show indicator
                    nextButtonObjective.disabled = true; // Disable button

                    try {
                        const response = await fetch('http://127.0.0.1:5000/update_note_objective', { // Changed endpoint
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
                            catch (e) { throw new Error(`Save failed: ${response.status} - ${errText}`);}
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

        if (generateAssessmentButton && assessmentPageLoadingIndicator && assessmentTextarea) {
            generateAssessmentButton.onclick = async function() {
                if (!currentNoteId) {
                    alert("Error: Note ID missing. Please refresh or navigate from the start.");
                    return;
                }

                assessmentPageLoadingIndicator.style.display = 'block';
                generateAssessmentButton.disabled = true;

                try {
                    const response = await fetch(`http://127.0.0.1:5000/api/generate_assessment/${currentNoteId}`, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const response_data = await response.json(); // Try to parse JSON regardless of response.ok for error messages

                    if (!response.ok) {
                        throw new Error(response_data.error || `Failed to generate assessment. Status: ${response.status}`);
                    }
                    
                    if (response_data.assessment_text) {
                        assessmentTextarea.value = response_data.assessment_text;
                        // alert("Assessment generated successfully and populated."); // Optional: user feedback
                    } else if (response_data.error) {
                        alert(`Error generating assessment: ${response_data.error}`);
                    } else {
                        alert("Received an unexpected response from the server.");
                    }
                } catch (error) {
                    console.error("Error generating assessment:", error);
                    alert(`Failed to generate assessment. Please try again. Error: ${error.message}`);
                } finally {
                    assessmentPageLoadingIndicator.style.display = 'none';
                    generateAssessmentButton.disabled = false;
                }
            };
        }

        if (nextButtonAssessment) {
             if (nextButtonAssessment.closest('a')) {
                nextButtonAssessment.closest('a').addEventListener('click', function(event) {
                    event.preventDefault();
                });
            }
            nextButtonAssessment.onclick = async function() {
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
                        const response = await fetch('http://127.0.0.1:5000/update_note_assessment', {
                            method: 'POST', headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                note_id: currentNoteId,
                                assessment_text: assessmentText
                            })
                        });
                        if (!response.ok) {
                            const errText = await response.text();
                            try { const err = JSON.parse(errText); throw new Error(err.error || `Save failed: ${response.status}`); }
                            catch (e) { throw new Error(`Save failed: ${response.status} - ${errText}`);}
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

        if (generatePlanButton && planTextarea && planLoadingIndicator) {
            generatePlanButton.onclick = async function() {
                if (!currentNoteId) {
                    alert("Error: Note ID missing. Please refresh or navigate from the start.");
                    return;
                }

                planLoadingIndicator.style.display = 'block';
                generatePlanButton.disabled = true;
                if (summarizeButtonPlan) summarizeButtonPlan.disabled = true; // Disable next button too

                try {
                    const response = await fetch(`http://127.0.0.1:5000/api/generate_plan/${currentNoteId}`, {
                        method: 'GET',
                        headers: { 'Content-Type': 'application/json' }
                    });

                    const response_data = await response.json();

                    if (!response.ok) {
                        throw new Error(response_data.error || `Failed to generate plan. Status: ${response.status}`);
                    }
                    
                    if (response_data.plan_text) {
                        planTextarea.value = response_data.plan_text;
                        // alert("Plan generated successfully and populated."); // Optional
                    } else if (response_data.error) {
                        alert(`Error generating plan: ${response_data.error}`);
                    } else {
                        alert("Received an unexpected response from the server when generating plan.");
                    }
                } catch (error) {
                    console.error("Error generating plan:", error);
                    alert(`Failed to generate plan. Please try again. Error: ${error.message}`);
                } finally {
                    planLoadingIndicator.style.display = 'none';
                    generatePlanButton.disabled = false;
                    if (summarizeButtonPlan) summarizeButtonPlan.disabled = false;
                }
            };
        }

        if (summarizeButtonPlan) {
             if (summarizeButtonPlan.closest('a')) {
                summarizeButtonPlan.closest('a').addEventListener('click', function(event) {
                    event.preventDefault();
                });
            }
            summarizeButtonPlan.onclick = async function() {
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
                        const response = await fetch('http://127.0.0.1:5000/update_note_plan', {
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
        const generateSummaryButton = document.getElementById('generateSummaryButton');
        const summaryLoadingIndicator = document.getElementById('summaryLoadingIndicator');
        const summaryDisplayArea = document.getElementById('summaryDisplayArea');

        // initializeNote() is already called globally and will trigger fetchNoteData.
        // fetchNoteData has been updated to populate the summaryDisplayArea on page load if data exists.
        console.log("On Summary page, note data should be fetched and displayed by initializeNote/fetchNoteData.");

            console.log('Attempting to get Summary page elements...');
            console.log('Summary Button Elements Check:', { generateSummaryButton, summaryLoadingIndicator, summaryDisplayArea, currentNoteId });
        if (generateSummaryButton && summaryLoadingIndicator && summaryDisplayArea) {
            generateSummaryButton.addEventListener('click', async function() {
                console.log('Generate Summary button clicked. Current Note ID for Summary:', currentNoteId);
                if (!currentNoteId) {
                    alert("Error: Note ID is not available. Please ensure you have navigated correctly or refresh the page.");
                    return;
                }

                summaryLoadingIndicator.style.display = 'block';
                generateSummaryButton.disabled = true;
                summaryDisplayArea.textContent = ''; // Clear previous summary

                try {
                    console.log(`Fetching summary from: http://127.0.0.1:5000/api/generate_summary/${currentNoteId}`);
                    const response = await fetch(`http://127.0.0.1:5000/api/generate_summary/${currentNoteId}`, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });

                    const response_data = await response.json();
                    console.log('Response from /api/generate_summary:', response_data);

                    if (!response.ok) {
                        throw new Error(response_data.error || `Failed to generate summary. Status: ${response.status}`);
                    }

                    if (response_data.summary_text) {
                        summaryDisplayArea.textContent = response_data.summary_text;
                    } else {
                        summaryDisplayArea.textContent = "Failed to generate summary. No text returned.";
                    }
                } catch (error) {
                    console.error("Error in Generate Summary fetch operation:", error, error.message, error.stack);
                    summaryDisplayArea.textContent = `Error generating summary: ${error.message}`;
                    alert(`Error generating summary: ${error.message}`);
                } finally {
                    summaryLoadingIndicator.style.display = 'none';
                    generateSummaryButton.disabled = false;
                }
            });
        }

        // Back button for summary page (if one exists and needs dynamic note_id)
        const backButtonSummary = document.querySelector('a.page-back-button[href^="plan.html"]'); // Example selector
        if (backButtonSummary && currentNoteId) { // Check currentNoteId before setting
            backButtonSummary.href = `plan.html?note_id=${currentNoteId}`;
        } else if (backButtonSummary && !currentNoteId) {
            // Fallback if currentNoteId isn't set yet, try to get from URL again or set a default
             const noteIdFromUrl = getNoteIdFromUrl();
             if (noteIdFromUrl) {
                 backButtonSummary.href = `plan.html?note_id=${noteIdFromUrl}`;
             } else {
                 // console.warn("Could not set back button URL for summary page: currentNoteId is null and not in URL.");
                 // backButtonSummary.href = 'plan.html'; // Or some other default
             }
        }
    }
});

// Export functionality for summary page
document.addEventListener('DOMContentLoaded', function() {
    const exportButton = document.getElementById('exportButton');
    const exportOptions = document.getElementById('exportOptions');
    const summaryDisplayArea = document.getElementById('summaryDisplayArea');

    if (exportButton && exportOptions && summaryDisplayArea) {
        // Toggle export options dropdown
        exportButton.addEventListener('click', function(e) {
            e.stopPropagation();
            exportOptions.style.display = exportOptions.style.display === 'block' ? 'none' : 'block';
        });

        // Close dropdown when clicking elsewhere
        document.addEventListener('click', function() {
            exportOptions.style.display = 'none';
        });

        // Handle export option clicks
        exportOptions.addEventListener('click', function(e) {
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