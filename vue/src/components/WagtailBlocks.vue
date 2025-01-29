<template>
  <div v-bind:key="block.id">
    <h2 v-if="block.type == 'heading'">{{ block.value }}</h2>
    <span v-else-if="block.type == 'paragraph'" v-html="block.value"></span>
    <img v-else-if="block.type == 'image'" :src="block.value.full_url"
         :width="block.value.full_width"
         :height="block.value.full_height" alt=""/>


    <p v-else-if="block.type == 'document'">

      <a :href="block.value.url"><button class="button-secondary small pdf mgn-right">Download PDF</button></a>
      {{ block.value.title }}
    </p>

    <p v-else-if="block.type == 'embed'">
      <iframe width="200" height="113" :src="block.value.url" frameborder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen></iframe>

    </p>

    <!-- Image Gallery here -->
    <section class="image_row" v-else-if="block.type == 'gallery'">
      <figure v-for="image_block in block.value" v-bind:key="image_block.filename">

        <img v-if="image_block.full_url != 'PLACEHOLDER'" :src="image_block.full_url"
             :width="image_block.full_width"
             :height="image_block.full_height" alt=""/>
        <img v-else src="@/assets/images/sharc-imageplaceholder-light.jpg" height="1602" width="1644" alt="Image placeholder"/>
        <figcaption v-if="image_block.caption.length >0">{{ image_block.caption }}</figcaption>

      </figure>
    </section>


    <div v-else-if="block.type == 'two_column_section'" class="two-column-50-50">
      <div v-for="section_block in block.value" v-bind:key="section_block.heading">
        <div><h3 v-html="section_block.heading"></h3></div>
        <div v-if="section_block.subheading.length >0">
          <h4 v-html="section_block.subheading"></h4></div>
        <div v-html="section_block.body"></div>
      </div>
    </div>
  </div>
</template>
<script>

export default {
  name: "WagtailBlocks",
  props: ['block']
}
</script>
