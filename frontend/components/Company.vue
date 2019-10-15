<template>
  <div class="w-full lg:max-w-full p-3 border-b bg-white rounded-xl mb-1">
    <div class="flex">
      <img
        :src="company['Logo URL']"
        class="w-16 h-16 mr-5 self-center rounded-lg"
      />
      <div class="flex-grow inline-block">
        <div class="text-gray-900 font-bold text-xl inline">
          <a :href="company['Website']" class="link">{{ company['Name'] }}</a>
        </div>
        <span> ({{ company['Founded'] }}) </span>
        <a
          v-if="company['Type'].includes('Public')"
          :href="`https://finance.yahoo.com/quote/${company['Type']}/`"
          class="link"
          >{{ company['Type'] }}
        </a>
        <span v-else>
          {{ company['Type'] }}
        </span>
        <span v-if="!company['Revenue'].includes('Unknown')" class="text-sm"
          >- {{ company['Revenue'] }}</span
        >
        <br />
        <p class="-mt-1 mb-1">
          <star-rating
            :rating="parseFloat(company['Rating'])"
            :increment="0.1"
            :read-only="true"
            :star-size="16"
            :inline="true"
            :show-rating="false"
          />
          {{ company['Rating'] }}
          • {{ company['Review Counts'] }} reviews
        </p>
        <!-- https://github.com/craigh411/vue-star-rating -->
        <div>
          <a :href="company['Reviews URL']" class="link btn">Reviews </a>
          <a :href="company['Overview URL']" class="link btn">Details</a>
          <a :href="company['LinkedIn URL']" class="link btn">LinkedIn </a>
        </div>
      </div>
      <div class="flex-grow-0 flex flex-col items-end content-center text-sm">
        <span>{{ company['Headquarters'] }}</span>
        <span>{{ company['Size'] }}</span>
        <span
          v-if="!company['Industry'].includes('Unknown')"
          class="text-right"
          >{{ company['Industry'] }}</span
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
