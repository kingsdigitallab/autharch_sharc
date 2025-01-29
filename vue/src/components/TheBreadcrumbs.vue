<template>
    <ul class="breadcrumbs">
		<li :key="index" v-for="(link, index) in breadcrumbs">
            <router-link :to="link.url" class="breadcrumbs__link">{{link.text}}</router-link>
        </li>
	</ul>
</template>

<script>
export default {
    name: 'TheBreadcrumbs',
	props: {
        breadcrumbs: {
            type: Array
        }
    }
}
</script>

<style>

</style>
