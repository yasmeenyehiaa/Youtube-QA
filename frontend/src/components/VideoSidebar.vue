<script setup>
import { ref } from "vue";
import { ingestVideo, deleteVideo } from "../api";
import { mmss } from "../utils";

const props = defineProps({ videos: Array, selectedId: String });
const emit = defineEmits(["select", "changed"]);

const url = ref("");
const status = ref("");
const error = ref("");
const busy = ref(false);

async function ingest() {
  if (!url.value.trim() || busy.value) return;
  busy.value = true;
  error.value = "";
  status.value = "Indexing. Captions are used when available, otherwise the audio is transcribed.";
  try {
    const rec = await ingestVideo(url.value.trim());
    status.value = `Indexed "${rec.title}" (${rec.chunks} chunks, from ${rec.source}).`;
    url.value = "";
    emit("changed");
    emit("select", rec.video_id);
  } catch (e) {
    error.value = e.message;
    status.value = "";
  } finally {
    busy.value = false;
  }
}

async function remove(videoId) {
  try {
    await deleteVideo(videoId);
    emit("changed");
    if (videoId === props.selectedId) emit("select", null);
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <aside class="sidebar">
    <h1 class="brand">Ask the video</h1>

    <form class="ingest" @submit.prevent="ingest">
      <label for="yt-url">YouTube URL</label>
      <input id="yt-url" v-model="url" placeholder="https://www.youtube.com/watch?v=..." :disabled="busy" />
      <button type="submit" :disabled="busy || !url.trim()">
        {{ busy ? "Indexing…" : "Add video" }}
      </button>
    </form>
    <p v-if="status" class="status">{{ status }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <h2 class="section-title">Library</h2>
    <p v-if="!videos.length" class="hint">No videos yet.</p>
    <ul class="video-list">
      <li v-for="v in videos" :key="v.video_id" :class="{ active: v.video_id === selectedId }">
        <button class="video-item" @click="emit('select', v.video_id)">
          <span class="title">{{ v.title }}</span>
          <span class="meta">{{ mmss(v.duration_seconds) }} · {{ v.source }}</span>
        </button>
        <button class="remove" :aria-label="`Remove ${v.title}`" @click="remove(v.video_id)">×</button>
      </li>
    </ul>
  </aside>
</template>
