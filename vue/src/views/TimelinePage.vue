<template>
  <main class="secondary">
    <div class="container">
      <the-breadcrumbs :breadcrumbs="breadcrumbs"/>
      <timeline/>
    </div>
  </main>
</template>

<script>
import TheBreadcrumbs from '../components/TheBreadcrumbs.vue'
import Timeline from "@/components/additional-modules/Timeline";

export default {
  name: 'TimelinePage',
  components: {
    TheBreadcrumbs,
    Timeline
  },
  data: function () {
    return {
      breadcrumbs: []
    }
  },
  methods: {
    updatePage() {
      this.breadcrumbs = [
        {text: 'Home', url: '/'},
      ];
      if (this.$route.meta.breadcrumb) {
        this.breadcrumbs.push({
          text: this.$route.meta.breadcrumb,
          url: '/' + this.$route.meta.breadcrumb.toLowerCase()
        });
      }
    }
  },
  created() {
    this.updatePage();
  },
  watch: {
    $route() {
      this.updatePage();
    }
  }
}
</script>