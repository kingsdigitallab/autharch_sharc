<template>
  <main class="about">
    <div class="container">
      <the-breadcrumbs :breadcrumbs="breadcrumbs"/>
      <about-page/>
    </div>
  </main>
</template>

<script>
import AboutPage from '../components/additional-modules/AboutPage.vue'
import TheBreadcrumbs from "@/components/TheBreadcrumbs";

export default {
  name: 'About',
  components: {
    AboutPage,
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