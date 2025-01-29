<template>
  <header>
    <div class="container">
      <router-link :to="{name: 'home'}" class="header__logo">
        <img src="@/assets/images/sharc-logo-full.svg" alt="SHARC logo" />
      </router-link>
      <div class="nav-wrapper">
        <nav class="header__nav">
          <ul class="header__nav-list">
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'home'}" class="header__link js-home" exact>Home</router-link>
            </li>
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'exhibition'}" class="header__link js-home" exact>Exhibition</router-link>
            </li>
<!--
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'objects'}" class="header__link js-objects">Objects</router-link>
            </li>
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'timeline'}" class="header__link js-objects">Timeline</router-link>
            </li>
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'stories'}" class="header__link js-objects">Stories</router-link>
            </li>
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'themes'}" class="header__link js-objects">Connections</router-link>
            </li>
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'resources'}" class="header__link js-resources">Resources</router-link>
            </li>-->
            <li class="header__nav-item" v-on:click="toggleMenu">
              <router-link :to="{name: 'about'}" class="header__link js-about">About</router-link>
            </li>
            <li class="header__nav-item" v-on:click="toggleMenu" v-if="getEventsPageStatus">
              <!-- OL: not happy that the Event page id is predetermined, they might accidentally delete this page and we will need to update the id -->
              <router-link to="/events" class="header__link js-events">Events</router-link>
            </li>
          </ul>
        </nav>



        <div class="mobile__nav" role="button" v-on:click="toggleMenu">
          <div class="line1"></div>
          <div class="line2"></div>
          <div class="line3"></div>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';

export default {
  name: 'TheHeader',
  computed: mapGetters(['getEventsPageStatus']),
  data() {
    return {
      searchTerm: '',
    }
  },
  methods: {
    toggleMenu: function() {
      const mobileNav = document.querySelector('.mobile__nav');
      const nav = document.querySelector('.header__nav');
      mobileNav.classList.toggle('toggle');
      nav.classList.toggle('nav-active');
    },
    toggleSearch: function() {
			document.querySelector('.mobile__nav').classList.remove('toggle');
			document.querySelector('.header__nav').classList.remove('nav-active');
		},
    setPage(to) {
      switch(to.name) {
				case 'search-results':
          break;
        case 'not-found':
          break;
        case 'accessibility-statement':
          break;
        case 'acknowledgements':
          this.setActivePage('about');
          break;
        case 'bibliography':
					this.setActivePage('resources');
          break;
        case 'glossary':
					this.setActivePage('resources');
          break;
        case 'object':
					this.setActivePage('objects');
					break;
        default: 
          this.setActivePage(to.name);
			}
    },
    setActivePage(pageName) {
      setTimeout(function() {
        if(document.querySelector('.js-'+pageName)) {
          document.querySelector('.js-'+pageName).classList.add('router-link-exact-active');
        }
      }, 100);
    },
		submit(){
      if (this.searchTerm != '') {
        this.$router.push("/search?q="+this.searchTerm);
      }
    },
    ...mapActions(['fetchEventsPageStatus'])
  },
  async created() {
    this.setPage(this.$route);
    await this.fetchEventsPageStatus();
  },
  watch: {
		$route(to) {
      if (document.querySelectorAll('.router-link-exact-active').length > 0) {
        document.querySelector('.router-link-exact-active').classList.remove('router-link-exact-active');
      }
      this.setPage(to);
		}
	},
}
</script>
