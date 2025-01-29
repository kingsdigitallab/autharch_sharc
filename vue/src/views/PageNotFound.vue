<template>
  <main class="not-found">
      <div class="container flex">
        <p class="error">404</p>
        <div>
          <h1 class="page-title">Page not found</h1>
          <p>We can't find the page you are looking for.</p>
          <router-link :to="{name: 'home'}" class="link-button-primary small arrow">Go to home page</router-link>
        </div>
      </div>
  </main>
</template>

<script>

export default {
  name: 'PageNotFound',
  components: {}
}
</script>