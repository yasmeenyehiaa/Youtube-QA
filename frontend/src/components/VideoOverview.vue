<script setup>
import { ref, watch } from "vue";
import { getVideoOverview } from "../api";
import { mmss } from "../utils";

const props = defineProps({ videoId: { type: String, required: true }, overview: Object });
const emit = defineEmits(["seek", "changed"]);

const data = ref(props.overview || null);
const busy = ref(false);
const error = ref("");

watch(
  () => props.videoId,
  () => {
    data.value = props.overview || null;
    error.value = "";
  },
);

async function loadOverview() {
  busy.value = true;
  error.value = "";
  try {
    data.value = await getVideoOverview(props.videoId);
    emit("changed");
  } catch (e) {
    error.value = e.message;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <section class="overview">
    <header class="overview-header">
      <div>
        <h2>Video overview</h2>
        <p>Get the key ideas and jump to a chapter.</p>
      </div>
      <button class="overview-generate" :disabled="busy" @click="loadOverview">
        {{ busy ? "Generating…" : data ? "Refresh overview" : "Generate overview" }}
      </button>
    </header>
    <p v-if="error" class="error overview-error" role="alert">{{ error }}</p>
    <p v-if="busy" class="overview-loading" role="status">Reading transcript and creating chapters…</p>
    <template v-if="data">
      <p class="overview-summary">{{ data.summary }}</p>
      <div v-if="data.topics?.length" class="topic-tags">
        <span v-for="topic in data.topics" :key="topic" class="topic-tag">{{ topic }}</span>
      </div>
      <h3 class="chapter-heading">Chapters</h3>
      <ol class="chapter-list">
        <li v-for="chapter in data.chapters" :key="`${chapter.start_seconds}-${chapter.title}`">
          <button
            class="chapter-link"
            :aria-label="`Jump to ${chapter.title} at ${mmss(chapter.start_seconds)}`"
            @click="emit('seek', { videoId, t: chapter.start_seconds })"
          >
            <span class="chapter-time">{{ mmss(chapter.start_seconds) }}</span>
            <span class="chapter-content">
              <strong>{{ chapter.title }}</strong>
              <span>{{ chapter.summary }}</span>
            </span>
          </button>
        </li>
      </ol>
    </template>
  </section>
</template>
