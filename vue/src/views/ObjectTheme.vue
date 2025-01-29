<template>
  <main class="object-story">
    <div class="container">
      <object-story-single v-bind:pageType="'editor.ThemeObjectCollection'"></object-story-single>
    </div>
  </main>
</template>

<script>
import ObjectStorySingle from '../components/ObjectStorySingle.vue'

export default {
  name: 'ObjectTheme',
  components: {
    ObjectStorySingle,
  }
}
</script>

