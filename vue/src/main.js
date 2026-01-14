import Vue from 'vue';
import App from './App.vue';
import linkify from 'vue-linkify';
import router from './router';
import store from './store';
import VueGtag from 'vue-gtag';

Vue.config.productionTip = false;
Vue.directive('linkified', linkify);

var VueTruncate = require('vue-truncate-filter');
Vue.use(VueTruncate);

Vue.use(require('vue-cookies'));

const VUE_APP_GOOGLE_ANALYTICS_ID = process.env.VUE_APP_GOOGLE_ANALYTICS_ID || ''

if (VUE_APP_GOOGLE_ANALYTICS_ID) {
  Vue.use(VueGtag, {
    config: {
      id: VUE_APP_GOOGLE_ANALYTICS_ID
    }
  }, router)
}

// Vue scroll-to
Vue.use(require('vue-scrollto'), {
     container: "body",
     duration: 500,
     easing: "ease",
     offset: 0,
     force: true,
     cancelable: true,
     onStart: false,
     onDone: false,
     onCancel: false,
     x: false,
     y: true
 });

// set secure, only https works
Vue.$cookies.config('30d','','',true)

new Vue({
  store,
  router,
  render: h => h(App)
}).$mount('#app')
