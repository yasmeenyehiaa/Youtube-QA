<script setup>
import { ref, computed, onUnmounted, watch } from "vue";
import { clearChat, sendChat, transcribeAudio } from "../api";
import { mmss } from "../utils";
import { getChatDetails, renameChat, saveChat } from "../chatHistory";

const props = defineProps({
  sessionId: String,
  videoId: String,
  videos: Array,
});
const emit = defineEmits(["seek"]);

const messages = ref([]);
const draft = ref("");
const busy = ref(false);
const recording = ref(false);
const error = ref("");
const chatTitle = ref("");
const editingTitle = ref(false);
const titleDraft = ref("");
const copiedMessage = ref(null);

let recorder = null;
let audioChunks = [];
let copyTimer;

onUnmounted(() => clearTimeout(copyTimer));

watch(
  () => props.sessionId,
  () => {
    try {
      const chat = getChatDetails(props.videoId);
      messages.value = chat.messages;
      chatTitle.value = chat.title;
    } catch (e) {
      error.value = `Unable to restore this chat: ${e.message}`;
      messages.value = [];
    }
  },
  { immediate: true },
);

watch(
  messages,
  (value) => {
    try {
      saveChat(props.videoId, value);
    } catch (e) {
      error.value = `Unable to save this chat: ${e.message}`;
    }
  },
  { deep: true },
);

const scopeLabel = computed(() => {
  const v = props.videos?.find((x) => x.video_id === props.videoId);
  return v ? v.title : props.videoId;
});

function beginRename() {
  titleDraft.value = chatTitle.value || `Chat about ${scopeLabel.value}`;
  editingTitle.value = true;
}

function saveTitle() {
  const title = titleDraft.value.trim();
  try {
    renameChat(props.videoId, title);
    chatTitle.value = title;
    editingTitle.value = false;
  } catch (e) {
    error.value = `Unable to rename this chat: ${e.message}`;
  }
}

async function copyAnswer(text, index) {
  error.value = "";
  try {
    if (navigator.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        copyWithFallback(text);
      }
    } else {
      copyWithFallback(text);
    }
    copiedMessage.value = index;
    clearTimeout(copyTimer);
    copyTimer = setTimeout(() => {
      copiedMessage.value = null;
    }, 1800);
  } catch (e) {
    error.value = `Unable to copy answer: ${e.message}`;
  }
}

function copyWithFallback(text) {
  const field = document.createElement("textarea");
  field.value = text;
  field.setAttribute("readonly", "");
  field.style.position = "fixed";
  field.style.opacity = "0";
  document.body.appendChild(field);
  let copied = false;
  try {
    field.select();
    copied = document.execCommand("copy");
  } finally {
    field.remove();
  }
  if (!copied) throw new Error("Clipboard access is unavailable in this browser.");
}

function messageParts(message) {
  const parts = [];
  const boldPattern = /\*\*(.+?)\*\*/g;
  let lastIndex = 0;

  for (const match of message.matchAll(boldPattern)) {
    const start = match.index;
    if (start > lastIndex) parts.push({ text: message.slice(lastIndex, start), bold: false });
    parts.push({ text: match[1], bold: true });
    lastIndex = start + match[0].length;
  }

  if (lastIndex < message.length || parts.length === 0) {
    parts.push({ text: message.slice(lastIndex), bold: false });
  }
  return parts;
}

async function clearHistory() {
  if (busy.value || !window.confirm("Clear this video's chat history?")) return;
  error.value = "";
  try {
    await clearChat(props.sessionId, props.videoId);
    messages.value = [];
    saveChat(props.videoId, messages.value);
  } catch (e) {
    error.value = e.message;
  }
}

async function send() {
  const text = draft.value.trim();
  if (!text || busy.value) return;
  error.value = "";
  messages.value.push({ role: "user", text });
  draft.value = "";
  busy.value = true;
  try {
    const res = await sendChat({
      session_id: props.sessionId,
      message: text,
      video_id: props.videoId,
    });
    messages.value.push({ role: "assistant", text: res.answer, citations: res.citations });
  } catch (e) {
    error.value = e.message;
  } finally {
    busy.value = false;
  }
}

async function toggleRecord() {
  if (recording.value) {
    recorder.stop();
    recording.value = false;
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    audioChunks = [];
    recorder = new MediaRecorder(stream);
    recorder.ondataavailable = (e) => audioChunks.push(e.data);
    recorder.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(audioChunks, { type: recorder.mimeType || "audio/webm" });
      busy.value = true;
      try {
        const { text } = await transcribeAudio(blob);
        draft.value = text;
      } catch (e) {
        error.value = e.message;
      } finally {
        busy.value = false;
      }
    };
    recorder.start();
    recording.value = true;
  } catch (e) {
    error.value = `Microphone unavailable: ${e.message}`;
  }
}
</script>

<template>
  <section class="chat">
    <header class="chat-header">
      <div class="chat-heading">
        <h2>Ask</h2>
        <span class="scope">{{ scopeLabel }}</span>
      </div>
      <div class="chat-actions">
        <button class="chat-action" :disabled="busy" @click="beginRename">Rename</button>
        <button class="chat-action clear-action" :disabled="busy || !messages.length" @click="clearHistory">
          Clear
        </button>
      </div>
    </header>
    <form v-if="editingTitle" class="rename-chat-form" @submit.prevent="saveTitle">
      <input v-model="titleDraft" aria-label="Chat name" maxlength="80" />
      <button type="submit">Save</button>
      <button type="button" @click="editingTitle = false">Cancel</button>
    </form>
    <p v-if="chatTitle" class="chat-title">{{ chatTitle }}</p>

    <div class="messages">
      <p v-if="!messages.length" class="hint">Ask a question about this video.</p>
      <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
        <button
          v-if="m.role === 'assistant'"
          class="copy-answer"
          :aria-label="copiedMessage === i ? 'Answer copied' : 'Copy answer'"
          @click="copyAnswer(m.text, i)"
        >
          <span aria-hidden="true">{{ copiedMessage === i ? "✓" : "▢" }}</span>
          {{ copiedMessage === i ? "Copied" : "Copy answer" }}
        </button>
        <p class="text" dir="auto">
          <template v-if="m.role === 'assistant'">
            <template v-for="(part, partIndex) in messageParts(m.text)" :key="partIndex">
              <strong v-if="part.bold">{{ part.text }}</strong>
              <template v-else>{{ part.text }}</template>
            </template>
          </template>
          <template v-else>{{ m.text }}</template>
        </p>
        <div v-if="m.citations && m.citations.length" class="chips">
          <button
            v-for="c in m.citations"
            :key="c.video_id + c.start"
            class="chip"
            :title="c.text"
            @click="emit('seek', { videoId: c.video_id, t: c.start })"
          >
            {{ mmss(c.start) }} · {{ c.title }}
          </button>
        </div>
      </div>
      <p v-if="busy" class="hint">Thinking…</p>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <form class="composer" @submit.prevent="send">
      <input v-model="draft" placeholder="Ask about this video…" :disabled="busy" />
      <button
        type="button"
        :class="['mic', { recording }]"
        :aria-label="recording ? 'Stop recording' : 'Record a question'"
        @click="toggleRecord"
      >
        {{ recording ? "Stop" : "Mic" }}
      </button>
      <button type="submit" :disabled="busy || !draft.trim()">Send</button>
    </form>
  </section>
</template>
