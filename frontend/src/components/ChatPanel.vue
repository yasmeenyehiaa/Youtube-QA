<script setup>
import { ref, computed } from "vue";
import { sendChat, transcribeAudio } from "../api";
import { mmss } from "../utils";

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

let recorder = null;
let audioChunks = [];

const scopeLabel = computed(() => {
  if (!props.videoId) return "all videos";
  const v = props.videos?.find((x) => x.video_id === props.videoId);
  return v ? v.title : props.videoId;
});

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
      video_id: props.videoId ?? null,
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
      <h2>Ask</h2>
      <span class="scope">{{ scopeLabel }}</span>
    </header>

    <div class="messages">
      <p v-if="!messages.length" class="hint">Ask a question about {{ scopeLabel }}.</p>
      <div v-for="(m, i) in messages" :key="i" :class="['msg', m.role]">
        <p class="text">{{ m.text }}</p>
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
      <input v-model="draft" placeholder="Ask about the video…" :disabled="busy" />
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
