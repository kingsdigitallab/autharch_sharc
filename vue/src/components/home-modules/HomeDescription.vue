<template>
    <div class="home-description">
        <h1>{{title}}</h1>
        <p v-html="briefDescription"></p>
        <router-link to="objects" class="link-button-primary large">See all objects</router-link><br>
        <router-link to="groups">Explore object groups</router-link>
    </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex'

export default {
    name: 'HomeDescription',
    computed: mapGetters(['title', 'briefDescription']),
    methods: {
        ...mapActions(['fetchDescription']),
    },
    async created() {
        await this.fetchDescription();
    },

}
</script>