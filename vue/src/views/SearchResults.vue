<template>
	<main class="search-results">
        <search-results-page/>
	</main>
</template>

<script>
import SearchResultsPage from '../components/search-modules/SearchResultsPage.vue'

export default {
	name: 'SearchResults',
	components: {
        SearchResultsPage
	}
}
</script>