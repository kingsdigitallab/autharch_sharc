<template>
    <div class="story">
        <template v-if="!loading">
            <h1 class="page-title">{{getStory.title}}</h1>
            <div class="two-column-70-30">
                <WagtailContent v-bind:api_content="getStory"></WagtailContent>
                <div class="grey-column" v-if="pageType === 'editor.StoryObjectCollection'">
                    <h3>All stories</h3>

                    <router-link v-for="(story, index) in getStoryList" v-bind:key="index" :to="{name: 'story', params: {subpage: story.url_slug}}" v-bind:class="[{active: story.url_slug === $route.params.subpage}]">{{story.title}}</router-link>
                </div>
              <div class="grey-column" v-if="pageType === 'editor.ThemeObjectCollection'">
                    <h3>All themes</h3>
                    <router-link v-for="(story, index) in getThemeList" v-bind:key="index" :to="{name: 'theme', params: {subpage: story.url_slug}}" v-bind:class="[{active: story.url_slug === $route.params.subpage}]">{{story.title}}</router-link>
                </div>

            </div>
            <related-objects-template v-if="getStory.related_documents && getStory.related_documents.length > 0" v-bind:relatedObjects="getStory.related_documents"></related-objects-template>
        </template>
        <div v-else class="loader"></div>
    </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

import RelatedObjectsTemplate from './templates/RelatedObjectsTemplate.vue';
import WagtailContent from "@/components/WagtailContent";

export default {
    name: 'ObjectStorySingle',
    props: {
      'pageType':{
        type:String,
        default: "editor.StoryObjectCollection"
      }
    },
    computed: mapGetters(['getStory', 'getStoryList', 'getThemeList']),
    components: {WagtailContent, RelatedObjectsTemplate},
    data: function() {
        return {
            loading: true
        }
    },
    methods: {
        ...mapActions(['fetchStoryList', 'fetchStory', 'fetchTheme', 'fetchThemeList'])
    },
    async created() {

        if (this.pageType === "editor.StoryObjectCollection"){
          await this.fetchStoryList();
          await this.fetchStory(this.$route.params.subpage);
        } else if (this.pageType === "editor.ThemeObjectCollection"){
          await this.fetchThemeList();
          await this.fetchTheme(this.$route.params.subpage);
        }

        this.loading = false;
    },
    watch: {
        $route(to) {
          this.fetchStory(to.params.subpage);
        }
    }
}
</script>