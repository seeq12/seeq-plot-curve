<template>
  <div>
    <v-row>
      <v-col md="6" class="flex-column">
        <v-spacer />
        <v-container align-self="center">
          <jupyter-widget :widget="plot_widget" />
        </v-container>
        <v-row align="center" justify="center">
          <jupyter-widget :widget="equation" class="equation-widget" />
        </v-row>

        <v-spacer />
      </v-col>

      <v-col md="6" align="center" justify="space-between">
        <v-row class="ma-md-4 mx-lg-auto">
          <v-col justify="space-between" align="center">
            <v-card class="ma-md-1 mx-lg-auto">
              <v-card-title>Plot Curve Variables</v-card-title>
              <v-row>
                <v-spacer />
                <v-col md="5">
                  <independent-picker />
                </v-col>
                <v-col md="5">
                  <dependent-picker />
                </v-col>
                <v-spacer />
              </v-row>
              <v-row align="center" justify="center" class="pa-3 mx-lg-auto">
                <order-picker />
              </v-row>
              <v-spacer />
            </v-card>

            <v-spacer />

            <v-card class="pa-2 ma-md-2 mx-lg-auto">
              <v-card-title>Seeq Signals</v-card-title>
              <v-row>
                <v-spacer />
                <v-col md="5">
                  <signal-picker-autocomplete />
                </v-col>
                <v-col md="5">
                  <output-field />
                </v-col>
                <v-spacer />
              </v-row>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
    <v-row class="pa-3 ma-md-5 mx-lg-auto" justify="center">
      <v-col md="10" justify="start">
        <!-- Snackbar code (unchanged) -->
      </v-col>

      <v-spacer />
      <v-col md="2">
        <v-btn
          @click="submit"
          class="white--text"
          color="#007960"
          :disabled="submit_disabled"
          raised
          ripple
          justify="center"
        >
          <v-progress-circular
            v-if="submission_in_progress"
            size="22"
            indeterminate
            color="white"
          ></v-progress-circular>
          <v-spacer />
          <span v-if="submission_in_progress">Pushing</span>
          <span v-else>Push to Seeq</span>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<!-- <script>
export default {
  name: 'OrderPicker',
  mounted() {
    this.$nextTick(() => {
      if (window.MathJax) {
        MathJax.Hub.Queue(['Typeset', MathJax.Hub]);
      }
    });
  },
};
</script> -->
<script>
export default {
  name: 'ChartComponent',
  mounted() {
    this.typesetMathWithRetry();
  },
  updated() {
    this.typesetMathWithRetry();
  },
  methods: {
    typesetMathWithRetry(retries = 5) {
      this.$nextTick(() => {
        setTimeout(() => {
          // Ensure MathJax processes the LaTeX after HTMLMath is rendered
          if (window.MathJax) {
            MathJax.Hub.Queue(['Typeset', MathJax.Hub, this.$el]);
          }
          if (retries > 0) {
            // Retry to ensure MathJax processes after widget rendering
            this.typesetMathWithRetry(retries - 1);
          }
        }, 1000); // Wait for widget to finish rendering
      });
    },
  },
};
</script>

<style>
.flex-column {
  display: flex;
  flex-flow: column wrap;
  justify-content: space-around;
}

.MathJax {
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}

.MathJax .math {
  font-size: 100%;
  line-height: normal;
}

.equation-widget .MathJax {
  overflow: hidden !important;
  white-space: nowrap !important;
  display: inline-block !important;
  vertical-align: middle !important;
}

.equation-widget .MathJax .math {
  font-size: 100% !important;
  line-height: normal !important;
}

.equation-widget {
  overflow: hidden;
  white-space: nowrap;
  display: inline-block;
  vertical-align: middle;
}
</style>
