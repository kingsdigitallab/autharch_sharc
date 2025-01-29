<template>
	<main class="secondary">
		<div class="container">
			<the-breadcrumbs :breadcrumbs="breadcrumbs"/>
			<secondary-page/>
		</div>
	</main>
</template>

<script>
import TheBreadcrumbs from '../components/TheBreadcrumbs.vue'
import SecondaryPage from '../components/additional-modules/SecondaryPage.vue'

export default {
	name: 'Secondary',
	components: {
		TheBreadcrumbs,
        SecondaryPage
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