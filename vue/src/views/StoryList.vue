<template>
  <main class="object-story">
    <div class="container">
      <ul class="breadcrumbs">
        <li><a href="/" class="breadcrumbs__link router-link-active">Home</a></li>
      </ul>
      <h1 class="page-title" v-if="pageType === 'editor.StoryObjectCollection'">Stories</h1>
      <h1 class="page-title" v-else-if="pageType === 'editor.ThemeObjectCollection'">Connections</h1>

      <div id="sidebar" role="navigation">
        <input type="checkbox" id="ref">
        <label aria-label="Title Index" class="ref" for="ref">
          <h1>Story Titles</h1>
          <div class="message">
            <ul>
              <li v-for="(story, index) in getStoryList" v-bind:key="index"
                  :to="{name: 'story', params: {subpage: story.url_slug}}"
                  v-bind:class="[{active: story.url_slug === $route.params.subpage}]">
                <a href="#" v-scroll-to="'#title-'+story.id" @click="active = 'title-'+story.id"
                   v-bind:class="{ 'name-active': active === 'title-one' }">
                  <h2>{{ story.title }}</h2>
                </a>
              </li>

            </ul>
          </div>
        </label>
      </div>

      <div>
        <p v-html="getStoryStrap"></p>
      </div>

      <br/>
      <div v-for="(story, index) in getStoryList" class="story" v-bind:key="index">

        <h2 :id="'title-' + story.id">
          {{ story.title }}
        </h2>

        <p v-if="pageType === 'editor.StoryObjectCollection'">
          <template v-for="block in story.body">
            <WagtailBlocks v-bind:block="block"></WagtailBlocks>
          </template>
        </p>

        <related-objects-template v-if="story.related_documents && story.related_documents.length > 0"
                                  v-bind:relatedObjects="story.related_documents"
                                  v-bind:show-title="false"></related-objects-template>

      </div>

    </div>
  </main>
</template>
<script>
import {mapActions, mapGetters} from 'vuex';

import RelatedObjectsTemplate from "@/components/templates/RelatedObjectsTemplate";
import WagtailBlocks from "@/components/WagtailBlocks";
/*
If we decide to use wagtail streamfield content:
import WagtailContent from "@/components/WagtailContent";
components: WagtailContent,
But it might just be a single desc field
 */
export default {
  name: "StoryList",
  computed: mapGetters(['getStory', 'getStoryList', 'getStoryStrap']),
  components: {WagtailBlocks, RelatedObjectsTemplate},
  data() {
    return {
      active: null,
    }
  },
  props: {
    'pageType': {
      type: String,
      default: "editor.StoryObjectCollection"
    }
  },
  methods: {
    ...mapActions(['fetchStoryList', 'fetchThemeList', 'fetchStoryStrap'])
  },
  async created() {

    if (this.pageType === "editor.StoryObjectCollection") {
      await this.fetchStoryList();
      await this.fetchStoryStrap()
    } else if (this.pageType === "editor.ThemeObjectCollection") {
      await this.fetchThemeList();
    }

    this.loading = false;
  },
  watch: {
    $route() {
      if (this.pageType === "editor.ThemeObjectCollection") {
        this.fetchThemeList();
      } else {
        this.fetchStoryList();

      }
    }
  }


}
</script>
<style scoped>
</style>