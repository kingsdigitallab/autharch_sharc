<template>
  <div class="about-page">
    <h1 class="page-title">{{getPage.title}}</h1>
    <template v-if="!loading">
    <WagtailContent v-bind:api_content="getPage"></WagtailContent>
    </template>
  </div>
</template>


<script>
import {mapActions, mapGetters} from 'vuex';
import WagtailContent from "@/components/WagtailContent";

export default {
  name: 'AboutPage',
  components: {WagtailContent},
  computed: mapGetters(['getPage', 'getImageURL']),
  data() {
    return {
      loading: true,
    }
  },
  methods: {
    async updatePage() {
        this.loading = true;
        await this.fetchSecondaryPage(this.$route.name);
        this.loading = false;
    },
    ...mapActions(['fetchSecondaryPage'])
  },
  async created() {
    if (this.$route.name) {
      this.updatePage();
    }
    this.fetchSecondaryPage(this.$route.name);
  },
  watch: {
    $route(to) {
      if(to.name) {
        this.updatePage();
      }
    }
  }
}
</script>
