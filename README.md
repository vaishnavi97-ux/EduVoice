# 🎙️ EduVoice – AI-Powered Lecture Transcription and Note Taking System

EduVoice is an AI-powered lecture transcription and note-taking system designed to help students convert classroom lectures into useful and organized study notes.

The system records or accepts lecture audio, converts speech into text, summarizes the lecture using AI, and provides structured notes for easy revision.

---

## 🚀 Features

- 🎤 **Live Lecture Recording**
  - Record lectures directly using a microphone.
  - Start and stop recording whenever required.

- 📁 **Audio File Upload**
  - Upload recorded lecture audio files.
  - Supports audio formats such as `.wav` and `.mp3`.

- 📝 **Speech-to-Text Transcription**
  - Converts the lecture audio into text.
  - Helps students avoid manually writing everything during lectures.

- 🤖 **AI-Based Summarization**
  - Converts lengthy lecture transcripts into short and meaningful notes.
  - Important points can be easily revised later.

- 🌐 **Multilingual Support**
  - Supports languages such as English, Telugu, and Hindi.
  - Provides translation between Telugu and English.

- 🔍 **Classroom Control Word Filtering**
  - Removes unnecessary classroom instructions such as:
    - "Pin drop silence"
    - "Don't make noise"
    - Other classroom control words

- 📚 **Structured Notes**
  - Generates organized notes from the lecture transcript.
  - Makes revision easier for students.

- 📄 **Export Notes**
  - Save generated notes as PDF or text files.

---

## 🏗️ System Architecture

EduVoice consists of the following major layers:

```text
              ┌──────────────────────┐
              │      User / Student  │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │     Client Layer     │
              │   React Frontend     │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Voice Processing     │
              │ Speech Recognition   │
              │ Audio Processing     │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │ Application Layer    │
              │ Flask + AI Models    │
              │ Transcription        │
              │ Summarization        │
              │ Translation          │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │    Output Layer      │
              │ Transcript / Notes   │
              │ PDF / TXT Export     │
              └──────────────────────┘
