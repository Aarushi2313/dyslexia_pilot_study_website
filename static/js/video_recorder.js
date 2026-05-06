/**
 * Video Recording Utility
 * Handles camera permissions, recording, uploading, and Google Meet-style controls.
 */

const VideoRecorder = {
    mediaRecorder: null,
    recordedChunks: [],
    stream: null,
    isRecording: false,
    config: {
        audioEnabled: true,
        videoEnabled: true
    },
    uiElements: {
        videoPreview: null,
        micBtn: null,
        camBtn: null
    },

    /**
     * Request camera/microphone permissions and start the stream.
     * @param {string} videoElementId - (Optional) ID of the video element to show preview.
     */
    async init(videoElementId = null) {
        // Safety check for MediaDevices API (requires HTTPS or localhost)
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            console.error("MediaDevices API is not available. Ensure you are using HTTPS or localhost.");
            return false;
        }

        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
            console.log("Camera/Microphone access granted.");

            if (videoElementId) {
                this.attachStreamToVideo(videoElementId);
            }

            return true;
        } catch (err) {
            console.error("Error accessing media devices:", err);
            // alert("Camera and microphone access is required for this task. Please allow access and refresh the page.");
            return false;
        }
    },

    /**
     * Attach the current stream to a video element for preview.
     */
    attachStreamToVideo(elementId) {
        const videoElement = document.getElementById(elementId);
        if (videoElement && this.stream) {
            videoElement.srcObject = this.stream;
            videoElement.muted = true; // Always mute local preview to prevent feedback
            this.uiElements.videoPreview = videoElement;
        }
    },

    /**
     * Toggle Microphone (mute/unmute)
     */
    toggleAudio() {
        if (this.stream) {
            this.config.audioEnabled = !this.config.audioEnabled;
            this.stream.getAudioTracks().forEach(track => {
                track.enabled = this.config.audioEnabled;
            });
            return this.config.audioEnabled;
        }
        return false;
    },

    /**
     * Toggle Camera (enable/disable video track)
     */
    toggleVideo() {
        if (this.stream) {
            this.config.videoEnabled = !this.config.videoEnabled;
            this.stream.getVideoTracks().forEach(track => {
                track.enabled = this.config.videoEnabled;
            });
            return this.config.videoEnabled;
        }
        return false;
    },

    /**
     * Start recording video.
     */
    start() {
        if (!this.stream) {
            console.warn("Stream not initialized. Calling init() first...");
            this.init().then(success => {
                if (success) this.start();
            });
            return;
        }

        this.recordedChunks = [];
        // Use a supported mime type
        const options = { mimeType: 'video/webm;codecs=vp9,opus' };

        try {
            this.mediaRecorder = new MediaRecorder(this.stream, options);
        } catch (e) {
            console.warn("VP9 not supported, trying default.");
            this.mediaRecorder = new MediaRecorder(this.stream);
        }

        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.recordedChunks.push(event.data);
            }
        };

        this.mediaRecorder.start();
        this.isRecording = true;
        console.log("Recording started...");
    },

    /**
     * Stop recording and upload the video.
     * @param {number} taskId - The ID of the task being attempted.
     * @param {string} taskName - (Optional) Name of the task for fallback or logging.
     * @returns {Promise} Resolves when upload is complete.
     */
    async stopAndUpload(taskId, taskName = 'unknown_task') {
        return new Promise((resolve, reject) => {
            if (!this.mediaRecorder || this.mediaRecorder.state === "inactive") {
                console.warn("No active recording to stop.");
                resolve(null); // Resolve anyway to not block submission
                return;
            }

            this.mediaRecorder.onstop = async () => {
                const blob = new Blob(this.recordedChunks, { type: 'video/webm' });
                const formData = new FormData();
                formData.append('video', blob, `recording_${Date.now()}.webm`);
                formData.append('task_id', taskId);
                formData.append('task_name', taskName);

                // Show uploading status (can be customized by UI code)
                const statusDiv = document.getElementById('recordingStatus');
                if (statusDiv) statusDiv.textContent = 'Uploading recording...';

                try {
                    const response = await fetch('/api/upload-video', {
                        method: 'POST',
                        body: formData
                    });
                    const data = await response.json();

                    if (data.success) {
                        console.log("Video uploaded successfully:", data.filename);
                        if (statusDiv) statusDiv.textContent = 'Recording saved.';
                        resolve(data);
                    } else {
                        console.error("Upload failed:", data.message);
                        if (statusDiv) statusDiv.textContent = 'Upload failed, but proceeding.';
                        resolve(null);
                    }
                } catch (error) {
                    console.error("Error uploading video:", error);
                    resolve(null);
                } finally {
                    // Do NOT stop tracks here if we want to keep the preview alive, behavior depends on requirements.
                    // Usually for "stop and upload" implies end of task. 
                    // But if it's just stopping recording, we might want to keep the stream.
                    // However, existing logic stopped it. We'll keep it consistent but careful re: re-recording.
                    // If we want to allow re-recording without page reload, we shouldn't stop tracks?
                    // Let's stop them for now to release the camera light, as typical for "finished" actions.
                    // If the user needs to re-record, they might need to init() again or we handle it.
                    // Actually, let's keep it alive if the user might go to next task? No, tasks are separate pages.
                    this.stopStream(); // Helper to stop everything
                    this.isRecording = false;
                }
            };

            this.mediaRecorder.stop();
            console.log("Recording stopped...");
        });
    },

    stopStream() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }
};
