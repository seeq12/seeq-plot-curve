<template>
  <v-card>

    <v-toolbar dark color = '#007960' rounded>
      <v-spacer/>
        <v-toolbar-title color = '#007960' justify = 'center' align="center">Plot Curve</v-toolbar-title>
      <v-spacer/>
    </v-toolbar>

    <v-stepper v-model="stepper_step" flat non-linear>

      <v-stepper-header color="#007960" justify="space-around">
        <v-spacer/>
        <v-stepper-step :complete="parseInt(stepper_step) > 1" @click.native="stepper_step='1'" complete-icon="mdi-check" color='#007960' step = "1" font-size=1.2em>Load</v-stepper-step>

        <divider/>
        <v-spacer/>
        <divider/>
        <v-stepper-step :complete="parseInt(stepper_step) > 2" @click.native="stepper_step='2'" color='#007960' step = "2">Plot</v-stepper-step>
        <v-spacer/>
      </v-stepper-header>

      <v-divider/>

      <v-stepper-items>

        <v-stepper-content step="1">

          <v-row justify='center' align='center'>
            <v-col md='11'>
                <b>Plot Curve</b> is an app to assist in fitting tabular data to polynomial equations and pushing the results to <b>Seeq</b>.
                <br/><br/>
                To get started, ensure the signals your formula depend on are in the active worksheet and load a csv file of the data you wish to fit.
                <br/><br/>
                The format of the csv file is as follows.  The first column indicates which curve the data in that row is assigned to. The remaining columns
                represent data for that particular curve. Units are provided in the second row.  The below example, shows a csv with a single curve (Pump Curve 1),
                and two parameters (Flow and Head).  Note that units with exponents require the use of the `^` symbol to denote exponent.

                The bold items (Curve and Units) are optional, but recommended to indicate <b>required</b> headers.

                Automated conversion of units is handled by Seeq provided the
                <a href='https://seeq.atlassian.net/wiki/spaces/KB/pages/112761878/Units+of+Measure+UOM' target='_blank'>units are supported</a>.
                <br/><br/>
                <v-card>
                <v-simple-table>
                  <thead>
                    <tr>
                      <td color='red'><b >Curve</b></td>
                      <td>Flow</td>
                      <td>Head</td>
                    </tr>
                  </thead>
                  <tbody>
                  <tr>
                    <td color='red'><b>Units</b></td>
                    <td>m^3/hr</td>
                    <td>m</td>
                  </tr>
                  <tr>
                    <td>Pump Curve 1</td>
                    <td>500</td>
                    <td>300</td>
                  </tr>
                                    <tr>
                    <td>Pump Curve 1</td>
                    <td>750</td>
                    <td>290</td>
                  </tr>
                  <tr>
                    <td>Pump Curve 1</td>
                    <td>1000</td>
                    <td>250</td>
                  </tr>
                  </tbody>
                </v-simple-table>
              </v-card>
            </v-col>
          </v-row>

          <v-row class="pa-3 ma-md-5 mx-lg-auto" justify="center">
              <v-col md='10'>
                  <v-snackbar :timeout="10000" :value="failure_snackbar" color="red lighten-3" absolute rounded="pill">
                    <span v-html="snackbar_msg"/>
                    <v-btn icon @click="failure_snackbar = false">
                      <v-icon x-small class="d-flex align-start">mdi-close</v-icon>
                    </v-btn>
                  </v-snackbar>
              </v-col>
              <v-col md='2' justify='center'>
                <file-reader :file_contents.sync="file_contents"/>
              </v-col>
          </v-row>

        </v-stepper-content>

        <v-stepper-content step="2">
          <tabbed-dataframe/>
          <chart-widget/>
        </v-stepper-content>

      </v-stepper-items>
    </v-stepper>
  </v-card>
</template>

<style>
.v-icon.notranslate.mdi.mdi-check.theme--light{
  font-size:1.2em; !important
}
.flex-column {
  display: flex;
  flex-flow: column wrap;
  justify-content: space-around;
}
.v-data-table tr:hover:not(.v-table__expanded__content) {
  background: transparent !important;
}
</style>

<script>
    module.exports = {
        watch:
        {
            stepper_step : function(new_step, old_step){
            if(parseInt(new_step) == 1){
              window.resizeTo(1200,930)
            }
            if(parseInt(new_step) == 2){
              window.resizeTo(1200,1400)
            }
            }
        },
        mounted: function(){
          window.resizeTo(1200,930)
        },

    }
</script>