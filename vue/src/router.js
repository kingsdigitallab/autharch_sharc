import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import ObjectList from './views/ObjectList.vue'
import ObjectSingle from './views/ObjectSingle.vue'
import ObjectStory from './views/ObjectStory.vue'
import ObjectTheme from "./views/ObjectTheme.vue"
import Resources from './views/Resources.vue'
import About from './views/About.vue'
import SearchResults from './views/SearchResults.vue'
import Secondary from './views/Secondary.vue'
import PageNotFound from './views/PageNotFound.vue'
import StoryList from './views/StoryList'
import TimelinePage from "@/views/TimelinePage";
import Privacy from "@/views/PrivacyPolicy";

Vue.use(Router)

export default new Router({
    mode: 'history',
    routes: [
        {
            path: '/',
            name: 'home',
            component: Home
        },
        {
            path: '/search',
            name: 'search-results',
            component: SearchResults
        },
        {
            path: '/objects',
            name: 'objects',
            component: ObjectList
        },
        /*{
            path: '/exhibition',
            name: 'exhibition',
            component: Secondary,
        },
         {
             path: '/assets',
             name: 'exhibition',
             component: Secondary,
             //redirect: 'https://main-bvxea6i-yo3hw5otma6dk.uk-1.platformsh.site/assets/'
             //beforeEnter() {location.href = 'http://github.com'}
         },*/
        {
            path: '/objects/:id',
            name: 'object',
            meta: {breadcrumb: 'Objects'},
            component: ObjectSingle
        },
        {
            path: '/objects/rct/:reference+',
            name: 'rct-object',
            meta: {breadcrumb: 'Objects'},
            component: ObjectSingle
        },
        {
            path: '/story/:subpage',
            name: 'story',
            component: ObjectStory
        },
        {
            path: '/connection/:subpage',
            name: 'theme',
            meta: {breadcrumb: 'Connections'},
            component: ObjectTheme,
            props: {pageType: "editor.ThemeObjectCollection"},
        },
        {
            path: '/stories',
            name: 'object-stories',
            component: StoryList,
        },
        {
            path: '/connections',
            name: 'connections',
            component: StoryList,
            props: {pageType: "editor.ThemeObjectCollection"},
        },
        {
            path: '/timeline',
            name: 'timeline',
            component: TimelinePage,
        },
        {
            path: '/resources',
            name: 'resources',
            component: Resources
        },
        {
            path: '/about',
            name: 'about',
            component: About
        },
        {
            path: '/about/acknowledgements',
            name: 'acknowledgements',
            meta: {breadcrumb: 'About'},
            component: Secondary
        },
        {
            path: '/resources/bibliography',
            name: 'bibliography',
            meta: {breadcrumb: 'Resources'},
            component: Secondary
        },
        {
            path: '/resources/glossary',
            name: 'glossary',
            meta: {breadcrumb: 'Resources'},
            component: Secondary
        },
        {
            path: '/accessibility',
            name: 'accessibility',
            component: Secondary
        },
        {
            path: '/events',
            name: 'events',
            component: Secondary
        },
        {
            path: '/privacy-policy',
            name: 'privacy',
            component: Privacy
        },
        {
            path: '/information/:id',
            name: 'information',
            component: Secondary
        },
        {
            path: "*",
            name: 'not-found',
            component: PageNotFound
        }
    ],
    // scrollBehavior() {
    //   return { x: 0, y: 0 }
    // }
    scrollBehavior(to, from, savedPosition) {
        if (savedPosition) {
            return savedPosition
        } else if (to.hash) {
            return {selector: to.hash}
        } else if (from.path === to.path) {
            return {}
        }
        return {x: 0, y: 0}
    }
});
