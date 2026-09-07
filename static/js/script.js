document.addEventListener("DOMContentLoaded", () => {
    const startBtn = document.getElementById("startBtn");
    const stopBtn = document.getElementById("stopBtn");
    const liveText = document.getElementById("liveText");
    const recordIndicator = document.getElementById("recordIndicator");
    const liveSummary = document.getElementById("liveSummary");
    const uploadLiveBtn = document.getElementById("uploadLive");
    const saveLectureBtn = document.getElementById("saveLectureBtn");
    const cancelLectureBtn = document.getElementById("cancelLectureBtn");
    const lectureModal = document.getElementById("lectureModal");

    let recognition;
    let finalTranscript = "";

    if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";

        recognition.onresult = (event) => {
            let interim = "";
            for (let i = event.resultIndex; i < event.results.length; i++) {
                let text = event.results[i][0].transcript;
                if (event.results[i].isFinal) finalTranscript += text + " ";
                else interim += text;
            }
            liveText.value = finalTranscript + interim;
            liveText.scrollTop = liveText.scrollHeight;
        };

        recognition.onend = () => {
            if (!stopBtn.disabled) recognition.start();
        };
    }

    // START
    if (startBtn) {
        startBtn.onclick = () => {
            finalTranscript = "";
            liveText.value = "";
            liveSummary.value = "";
            uploadLiveBtn.classList.add("hidden"); // hide upload until new summary is ready

            recognition.start();
            startBtn.disabled = true;
            stopBtn.disabled = false;
            recordIndicator.classList.remove("hidden");
        };
    }

    // STOP
    if (stopBtn) {
        stopBtn.onclick = async () => {
            recognition.stop();
            startBtn.disabled = false;
            stopBtn.disabled = true;
            recordIndicator.classList.add("hidden");

            // Summarize transcript
            const res = await fetch("/summarize_text", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: finalTranscript })
            });
            const data = await res.json();
            liveSummary.value = data.summary;

            // Show upload button
            uploadLiveBtn.classList.remove("hidden");
        };
    }

    // UPLOAD LECTURE
    if (uploadLiveBtn) {
        uploadLiveBtn.onclick = async () => {
            document.getElementById("lectureModal").style.display = "block";
    };
}

if (saveLectureBtn) {
    saveLectureBtn.onclick = async () => {
            const title = document.getElementById("lectureTitle").value;
            const subject = document.getElementById("lectureSubject").value;
            const payload = {
                title: title,
                subject: subject,
                transcript: liveText.value,
                summary: liveSummary.value
            };

            const res = await fetch("/save_live_lecture", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await res.json();
            if (data.success) {
                alert("✅ Live lecture saved to teacher profile!");
                uploadLiveBtn.classList.add("hidden"); // hide after saving
                lectureModal.style.display = "none";  // close modal
            } else {
                alert("❌ Error saving lecture: " + data.error);
            }
        };
    }
    if (cancelLectureBtn) {
        cancelLectureBtn.onclick = () => {
        lectureModal.style.display = "none";  // close modal on cancel
     };
    }
});
