<script setup>
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { deleteVideo, ingestVideo, searchVideos } from "../api";
import { mmss } from "../utils";

const props = defineProps({
  videos: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  loaded: { type: Boolean, default: false },
});
const emit = defineEmits(["select", "changed"]);

const url = ref("");
const status = ref("");
const error = ref("");
const busy = ref(false);
const searchQuery = ref("");
const sourceFilter = ref("");
const topicFilter = ref("");
const semanticMatches = ref(new Set());
const searchBusy = ref(false);
let searchTimer;
let searchRequest = 0;

const sources = computed(() => [...new Set(props.videos.map((video) => video.source))].sort());
const topics = computed(() =>
  [...new Set(props.videos.flatMap((video) => video.topics || []))].sort(),
);
const filteredVideos = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  return props.videos.filter((video) => {
    const textMatches =
      !query ||
      [video.title, video.source, ...(video.topics || [])].some((value) =>
        value.toLowerCase().includes(query),
      ) ||
      semanticMatches.value.has(video.video_id);
    const sourceMatches = !sourceFilter.value || video.source === sourceFilter.value;
    const topicMatches = !topicFilter.value || (video.topics || []).includes(topicFilter.value);
    return textMatches && sourceMatches && topicMatches;
  });
});

watch(searchQuery, (query) => {
  clearTimeout(searchTimer);
  const requestId = ++searchRequest;
  if (!query.trim()) {
    semanticMatches.value = new Set();
    searchBusy.value = false;
    return;
  }
  searchTimer = setTimeout(async () => {
    searchBusy.value = true;
    error.value = "";
    try {
      const result = await searchVideos(query.trim());
      if (requestId === searchRequest) semanticMatches.value = new Set(result.video_ids);
    } catch (e) {
      if (requestId === searchRequest) error.value = e.message;
    } finally {
      if (requestId === searchRequest) searchBusy.value = false;
    }
  }, 350);
});

onBeforeUnmount(() => clearTimeout(searchTimer));

async function ingest() {
  const videoUrl = url.value.trim();
  if (!videoUrl || busy.value) return;
  busy.value = true;
  error.value = "";
  status.value = "Adding video…";
  try {
    const video = await ingestVideo(videoUrl);
    url.value = "";
    status.value = `Added "${video.title}".`;
    emit("changed");
    emit("select", video.video_id);
  } catch (e) {
    error.value = e.message;
    status.value = "";
  } finally {
    busy.value = false;
  }
}

async function remove(videoId) {
  error.value = "";
  try {
    await deleteVideo(videoId);
    emit("changed");
  } catch (e) {
    error.value = e.message;
  }
}
</script>

<template>
  <section class="library">
    <h1 class="library-title">Your Video Hub</h1>
    <p class="library-subtitle">Add a YouTube video or choose one to start asking questions.</p>

    <form class="ingest-form" @submit.prevent="ingest">
      <label class="sr-only" for="yt-url">YouTube video URL</label>
      <input
        id="yt-url"
        v-model="url"
        placeholder="Paste a YouTube video link"
        :disabled="busy"
      />
      <button type="submit" :disabled="busy || !url.trim()">
        {{ busy ? "Adding…" : "Add video" }}
      </button>
    </form>
    <p v-if="status" class="status" role="status">{{ status }}</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <div v-if="videos.length" class="library-controls">
      <label class="library-search">
        <span class="sr-only">Search videos by title, source, or topic</span>
        <input v-model="searchQuery" placeholder="Search titles, sources, or topics…" />
        <span v-if="searchBusy" class="search-spinner" aria-label="Searching">…</span>
      </label>
      <label class="filter-label">
        <span>Source</span>
        <select v-model="sourceFilter" aria-label="Filter by transcript source">
          <option value="">All sources</option>
          <option v-for="source in sources" :key="source" :value="source">{{ source }}</option>
        </select>
      </label>
      <label v-if="topics.length" class="filter-label">
        <span>Topic</span>
        <select v-model="topicFilter" aria-label="Filter by topic">
          <option value="">All topics</option>
          <option v-for="topic in topics" :key="topic" :value="topic">{{ topic }}</option>
        </select>
      </label>
    </div>

    <div v-if="filteredVideos.length" class="video-grid">
      <article v-for="video in filteredVideos" :key="video.video_id" class="video-card">
        <button
          class="thumbnail-button"
          :aria-label="`Watch ${video.title}`"
          @click="emit('select', video.video_id)"
        >
          <img
            class="thumbnail"
            :src="`https://i.ytimg.com/vi/${video.video_id}/hqdefault.jpg`"
            :alt="`Thumbnail for ${video.title}`"
            loading="lazy"
          />
          <span class="duration">{{ mmss(video.duration_seconds) }}</span>
        </button>
        <div class="video-card-info">
          <button class="video-card-title" @click="emit('select', video.video_id)">
            {{ video.title }}
          </button>
          <div v-if="video.topics?.length" class="card-topics">
            <span v-for="topic in video.topics.slice(0, 3)" :key="topic" class="topic-tag">{{ topic }}</span>
          </div>
          <button
            class="remove"
            :aria-label="`Remove ${video.title} from library`"
            @click="remove(video.video_id)"
          >
            <span aria-hidden="true">🗑️</span>
            <span>Remove video</span>
          </button>
        </div>
      </article>
    </div>
    <p v-else-if="videos.length" class="empty-library">No videos match those search filters.</p>
    <p v-else-if="loading" class="empty-library library-loading" role="status">
      <span class="library-spinner" aria-hidden="true"></span>
      <span>Loading your library…</span>
    </p>
    <p v-else-if="loaded" class="empty-library">Your library is empty. Add a video to get started.</p>
  </section>
</template>
