<template>
  <div class="max-w-4xl w-full m-3">
    <form
      class="w-full py-2 mb-4"
      @submit.prevent="getCompanies(inputCompanies)"
    >
      <div
        class="flex items-center py-2 border-2 bg-white rounded-lg border-gray-400 focus-within:border-blue-500"
      >
        <input
          v-model="inputCompanies"
          class="appearance-none bg-transparent w-full text-gray-700 mr-3 p-2 leading-tight focus:outline-none"
          type="text"
          placeholder="Facebook, Amazon, Netflix, Google, Lyft"
          aria-label="Company Names"
        />
        <button
          v-if="!loading"
          class="flex-shrink-0 bg-blue-500 font-bold hover:bg-blue-700 border-blue-500 hover:border-blue-700 border-4 text-white py-1 px-2 rounded"
          type="button"
          @click="getCompanies(inputCompanies)"
        >
          Get Companies Overview
        </button>
        <button
          v-else
          type="button"
          class="flex-shrink-0 bg-blue-500 font-bold border-blue-500 opacity-50 cursor-not-allowed border-4 text-white py-1 px-2 rounded"
        >
          Get Companies Overview
        </button>
        <button
          class="flex-shrink-0 border-transparent border-4 text-blue-500 hover:text-blue-800 text-sm py-1 px-2 rounded focus:outline-none"
          type="button"
          @click="clearInputCompanies()"
        >
          Clear
        </button>
      </div>
      <p v-if="!inputCompanies" class="ml-2 text-gray-700 text-sm">
        Enter a comma separated list of company names you're interested in.
      </p>
    </form>
    <div v-if="companies.length == 0 && !loading" class="relative mt-10">
      <img src="destinations_grey.svg" alt="Welcome" />
      <!-- <div class="absolute right-0 top-0 mt-10 text-gray-700"> -->
      <!-- <div class="absolute bottom-0 left-0 ml-6 mb-10 text-gray-700">
        <p>
          Not sure which companies to check out?
        </p>
        <button
          class="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded-full w-full mt-3 focus:outline-none"
          @click="getDefaultCompanies()"
        >
          Show Sample Overviews
        </button>
      </div> -->
    </div>
    <div v-if="loading" class="flex justify-center">
      <loader></loader>
    </div>
    <div v-for="company in companies" v-else :key="company['Name']">
      <Company :company="company"></Company>
    </div>
    <div
      v-if="companies.length == 0 && !loading"
      class="flex flex-col content-center items-center mt-10 text-gray-700 "
    >
      <p>
        Not sure which companies to check out?
      </p>
      <button
        class="bg-blue-500 hover:bg-blue-700 text-white py-2 px-4 rounded-full mt-3 focus:outline-none w-1/3"
        @click="getDefaultCompanies()"
      >
        Show Sample Overviews
      </button>
    </div>
  </div>
</template>

<script>
import axios from '~/plugins/axios'

import Loader from '~/components/Loader.vue'
import Company from '~/components/Company.vue'

export default {
  components: {
    Loader,
    Company
  },
  data() {
    return {
      inputCompanies: '',
      companies: [],
      loading: false,
      error: null
    }
  },
  mounted() {},
  methods: {
    getDefaultCompanies() {
      this.loading = true
      axios
        .get('/companies')
        .then((response) => {
          this.companies = response.data
          this.loading = false
        })
        .catch((err) => {
          console.error(err)
          this.loading = false
        })
    },
    getCompanies(companies) {
      console.debug(`getCompanies(${companies})`)
      this.loading = true
      axios
        .post('/companies', {
          companies
        })
        .then((response) => {
          console.debug(response)
          this.companies = response.data
          this.loading = false
        })
        .catch((err) => {
          console.error(err)
          this.loading = false
        })
    },
    clearInputCompanies() {
      this.inputCompanies = ''
    }
  }
}
</script>

<style>
/* */
</style>
