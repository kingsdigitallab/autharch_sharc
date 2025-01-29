<template>
  <main class="single-record container">
    <the-breadcrumbs :breadcrumbs="breadcrumbs"/>
    <archive-single/>
  </main>
</template>

<script>
import ArchiveSingle from '../components/object-single-modules/ArchiveSingle.vue'
import TheBreadcrumbs from '../components/TheBreadcrumbs.vue'

export default {
  name: 'ObjectRecord',
  components: {
    ArchiveSingle,
    TheBreadcrumbs
  },
  data: function() {
    return {
      breadcrumbs: [
        { text: 'Home', url: '/' },
        { text: 'Objects', url: '/objects' }
      ]
    }
  }
}
</script>
