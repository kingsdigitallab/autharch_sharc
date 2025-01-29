<template>

  <main class="object-list">
    <div class="container">
      <the-breadcrumbs :breadcrumbs="breadcrumbs"/>
      <h1 class="page-title">Search</h1>
      <p class="page-description" v-html="pageDescription"></p>
      <archive-list/>
    </div>
  </main>
</template>

<script>
import TheBreadcrumbs from '../components/TheBreadcrumbs.vue'
import { mapGetters, mapActions } from 'vuex';   
import ArchiveList from '../components/archival-records-modules/ArchiveList.vue'

export default {
  name: 'ObjectList',
  computed: mapGetters(['pageDescription',]),
  components: {
    ArchiveList,
    TheBreadcrumbs,
  },
  data: function() {
		return {
			breadcrumbs: []
		}
	},
  methods: {
    updatePage() {
			this.breadcrumbs = [
				{ text: 'Home', url: '/' },
			];
			if (this.$route.meta.breadcrumb) {
				this.breadcrumbs.push( {
					text: this.$route.meta.breadcrumb,
					url: '/'+ this.$route.meta.breadcrumb.toLowerCase()
				});
			}
		},
    ...mapActions(['fetchObjectsPageDescription'])
  },
  async created() {
    await this.fetchObjectsPageDescription();
    this.updatePage();
  }
}
</script>
