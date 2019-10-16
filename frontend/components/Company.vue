<template>
  <div class="w-full lg:max-w-full p-3 border-b bg-white rounded-xl mb-1">
    <div class="flex">
      <img
        :src="company['logo_url']"
        class="w-16 h-16 mr-5 self-center rounded-lg"
      />
      <div class="flex-grow inline-block">
        <div class="text-gray-900 font-bold text-xl inline">
          <a :href="company['website']" class="link">{{ company['name'] }}</a>
        </div>
        <span> ({{ company['founded'] }}) </span>
        <a
          v-if="company['type'].includes('Public')"
          :href="`https://finance.yahoo.com/quote/${company['type']}/`"
          class="link"
          >{{ company['type'] }}
        </a>
        <span v-else>
          {{ company['type'] }}
        </span>
        <span v-if="!company['revenue'].includes('Unknown')" class="text-sm"
          >- {{ company['revenue'] }}</span
        >
        <br />
        <p class="-mt-1 mb-1">
          <star-rating
            :rating="parseFloat(company['rating'])"
            :increment="0.1"
            :read-only="true"
            :star-size="16"
            :inline="true"
            :show-rating="false"
          />
          {{ company['rating'] }}
          • {{ company['review_counts'] }} reviews
        </p>
        <!-- https://github.com/craigh411/vue-star-rating -->
        <div>
          <a :href="company['reviews_url']" class="link btn">Reviews </a>
          <a :href="company['overview_url']" class="link btn">Details</a>
          <a :href="company['linkedin_url']" class="link btn">LinkedIn </a>
        </div>
      </div>
      <div class="flex-grow-0 flex flex-col items-end content-center text-sm">
        <span>{{ company['headquarters'] }}</span>
        <span>{{ company['size'] }}</span>
        <span
          v-if="!company['industry'].includes('Unknown')"
          class="text-right"
          >{{ company['industry'] }}</span
        >
      </div>
    </div>
  </div>
</template>

<script>
import StarRating from 'vue-star-rating'

export default {
  components: {
    StarRating
  },
  props: {
    company: {
      type: Object,
      default: () => {
        return {}
      }
    }
  }
}
</script>

<style scoped>
.btn {
  @apply bg-transparent text-blue-700 text-sm py-1 mr-2 rounded;
}

.btn:hover {
  @apply text-blue-800 border-transparent;
}

.rounded-xl {
  border-radius: 0.65rem;
}
</style>
