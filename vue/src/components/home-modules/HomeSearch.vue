<template>
    <div class="home-search">
        <h1 class="page-title">Search the collection</h1>
        <div>
            <form @submit.prevent="searchRecords" class="search-field">
              <input type="search" v-model="searchTerm" aria-label="Search our collection by name, date, category, creator" placeholder="Search our collection by name, date, category, creator" onfocus="this.placeholder=''" onblur="this.placeholder='Search our collection by name, date, category, creator'"/>
                <input type="submit" class="search-button" aria-label="Search button" value=""/>
            </form>
        </div>
        <br>
        <div v-if="!loading">
            <span :key="i" v-for="(tag, i) in featuredTags">
                <router-link  class="link-button-primary small" :to="{name: 'objects', query: {category: [tag]}}">{{tag}}</router-link>
            </span>
        </div>
        <div v-else class="loader"></div>
    </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'
export default {
    name: 'HomeSearch',
    computed: mapGetters(['featuredTags']),
    data () {
        return {
            loading: true,
            searchTerm: ''
        }
    },
    methods: {
        searchRecords() {
            this.$router.push("/objects?q="+this.searchTerm);
        },
        ...mapActions(['fetchTags']),
    },
    async created() {
        await this.fetchTags();
        this.loading = false;
    },
}
</script>