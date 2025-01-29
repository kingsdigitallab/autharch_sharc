<template>
  <footer>

    <div class="image-credit">
      <p>
        Image credits: Royal Collection Trust and Royal Archives / © Her Majesty Queen Elizabeth II 2019-{{ new Date().getFullYear() }}
      </p>
    </div>
    <div class="footer-logos">
      <a href="https://kcl.ac.uk" title="KCL link">
        <img src="@/assets/images/KCL_box_red_485_rgb.jpg" alt="KCL logo">
      </a>
      <a href="https://www.rct.uk/" title="RCT link">
        <img src="@/assets/images/RCTLogo.jpg" alt="RCT logo">
      </a>
      <a href="http://ahrc.ukri.org" title="AHRC link">
        <img class="footer__img" src="@/assets/images/ahrc-2018-landscape-logo-1200px.png" alt="AHRC logo">
      </a>
      <a href="http://bbk.ac.uk" title="Birkbeck University of London link">
        <img src="@/assets/images/bbk-logo-black-digi.jpg" alt="Birbeck University of London logo">
      </a>
    </div>
    <a href="https://twitter.com/sharc_project"><i class="fab fa-twitter" aria-hidden="true"></i> @sharc_project</a>
    
    <span class="delimiter">|</span>

    <router-link to="/accessibility">Accessibility</router-link>
    <p>
      © 2019-{{ new Date().getFullYear() }} Designed, developed and maintained by 
      <a href="https://kdl.kcl.ac.uk" title="King's Digital Lab">King's
      Digital Lab
      </a>
    </p>
    <div class="cookies-box hide" id="cookie-disclaimer" v-if="this.cookie_accepted == false">
      <p>We use cookies to track usage and preferences in accordance with our <a href="/privacy-policy/" class="button cookie">Privacy & Cookie Policy</a></p>
      <p>
        <button v-on:click="set_cookie_accepted()" class="button success closeme" aria-label="Dismiss alert"
                type="button">I understand
        </button>
      </p>
    </div>
  </footer>
</template>

<script>
let cookie_name = 'cookie_accepted';

export default {
  name: 'Footer',
  components: {},
  data: function() {
		return {
			cookie_accepted: false
		}
	},
  methods: {
    set_cookie_accepted() {
      this.$cookies.set(cookie_name, 'True');
      this.cookie_accepted = true;
    }
  },
  created() {
      if (this.$cookies.isKey(cookie_name)) {
        if (this.$cookies.get(cookie_name) == 'True') {
          this.cookie_accepted = true;
        }
      }
    }
}
</script>

