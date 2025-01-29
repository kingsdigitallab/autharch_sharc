<template v-if="api_content.meta">
  <div>
    <template v-if="api_content.meta.type == 'editor.RichTextPage'">

      <div v-if="api_content.introduction" class="introduction" v-html="api_content.introduction"></div>
      <img v-if="api_content.resource && api_content.resource != ''" :src="api_content.resource"
           :alt="api_content.alt"/>
      <div class="description" v-html="api_content.body"></div>
    </template>
    <template
        v-else-if="api_content.meta.type == 'editor.StreamFieldPage' || api_content.meta.type == 'editor.StoryObjectCollection' || api_content.meta.type == 'editor.ThemeObjectCollection'">
      <template v-for="(block, index) in api_content.body">
        <WagtailBlocks v-bind:block="block" v-bind:key="index"/>
      </template>

    </template>
  </div>
</template>

<script>
import WagtailBlocks from "@/components/WagtailBlocks";
export default {
  name: 'WagtailContent',
  components: {WagtailBlocks},
  props: ['api_content']
}
</script>