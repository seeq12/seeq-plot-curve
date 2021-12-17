<template>
  <div>
    <v-row>
      <v-col md="6" class="flex-column">
        <v-spacer/>
        <v-container align-self="center"><jupyter-widget :widget="plot_widget"/></v-container>
        <v-row align-self="center">
          <v-spacer/>
          <jupyter-widget align-self="center" :widget="equation"/>
          <v-spacer/>
        </v-row>
        <v-spacer/>
      </v-col>

      <v-col md="6" align="center" justify="space-between">
        <v-row class="ma-md-4 mx-lg-auto">
          <v-col justify="space-between" align="center">
            <v-card class="ma-md-1 mx-lg-auto">
              <v-card-title>Plot Curve Variables</v-card-title>
              <v-row>
                <v-spacer/>
                <v-col md="5">
                  <independent-picker/>
                </v-col>
                <v-col md="5">
                  <dependent-picker/>
                </v-col>
                <v-spacer/>
              </v-row>
              <v-row align='center' justify="center" class="pa-3 mx-lg-auto">
                <order-picker/>
              </v-row>
              <v-spacer/>
            </v-card>

            <v-spacer/>

            <v-card class="pa-2 ma-md-2 mx-lg-auto">
              <v-card-title>Seeq Signals</v-card-title>
              <v-row>
                <v-spacer/>
                <v-col md="5">
                  <signal-picker-autocomplete/>
                </v-col>
                <v-col md="5">
                  <output-field/>
                </v-col>
                <v-spacer/>
              </v-row>
            </v-card>
          </v-col>
        </v-row>


      </v-col>



    </v-row>
    <v-row class="pa-3 ma-md-5 mx-lg-auto" justify="center">

      <v-col md='10' justify="start">
          <v-spacer/>
          <v-snackbar :timeout="10000" :value="success_snackbar" color="green lighten-3" absolute rounded="pill">
              <span v-html="snackbar_msg"/>
              <v-spacer/>
              <v-btn icon @click="success_snackbar = false">
                  <v-icon x-small class="d-flex align-start">mdi-close</v-icon>
              </v-btn>
          </v-snackbar>
          <v-snackbar :timeout="10000" :value="failure_snackbar" color="red lighten-3" absolute rounded="pill">
              <span v-html="snackbar_msg"/>
              <v-btn icon @click="failure_snackbar = false">
                  <v-icon x-small class="d-flex align-start">mdi-close</v-icon>
              </v-btn>
          </v-snackbar>
          <v-snackbar :timeout="10000" :value="info_snackbar" color="blue lighten-3" absolute rounded="pill">
              <span v-html="snackbar_msg"/>
              <v-btn icon @click="info_snackbar = false">
                  <v-icon x-small class="d-flex align-start">mdi-close</v-icon>
              </v-btn>
          </v-snackbar>
          <v-snackbar :timeout="10000" :value="multiple_signal_prompt" color="blue lighten-3" absolute rounded="pill">
                There are multiple tabs with valid output signals.  Push all?
              <v-btn x-small color='green' @click='submit_all'> Push All </v-btn>
              <v-btn x-small color='blue' @click='submit_active'> Push Active </v-btn>
              <v-btn icon @click="multiple_signal_prompt = false">
                  <v-icon x-small class="d-flex align-start">mdi-close</v-icon>
              </v-btn>
          </v-snackbar>
          <v-spacer/>
      </v-col>

      <v-spacer/>
      <v-col md='2'>
      <v-btn @click='submit' class="white--text" color="#007960" :disabled='submit_disabled' raised ripple justify="center">
        <v-progress-circular v-if="submission_in_progress" size='22' indeterminate color="white"></v-progress-circular>
        <v-spacer/>
        <span v-if='submission_in_progress'>Pushing</span>
        <span v-else>Push to Seeq</span>

      </v-btn>
      </v-col>

    </v-row>
  </div>
</template>

<style>
.flex-column {
  display: flex;
  flex-flow: column wrap;
  justify-content: space-around;
</style>