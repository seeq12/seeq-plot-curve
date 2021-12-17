<template>
<v-div>
    <v-row nogutters>
      <v-col md="12">
        <v-tabs @change='tab_change' color='#007960'>
          <v-tab v-for="tab in tabs" :key="tab">{{tab}}</v-tab>
          <v-tabs-slider color="#007960 darken-3"></v-tabs-slider>
        </v-tabs>
      </v-col>
    </v-row>

    <v-row nogutters>
      <v-layout child-flex>
        <v-data-table :headers="headers" :items="items" :footer-props="footer_props"
                      :items-per-page="5" hide-default-header>
          <template v-slot:header="{props:{headers}}">
            <thead>
            <tr>
              <th v-for="header in headers">
                <span>{{header.text}}</span>
              </th>
            </tr>
            </thead>
          </template>
          <template v-slot:no-data>
            Click the load button to read a csv or xls file
          </template>
        </v-data-table>
      </v-layout>
    </v-row>
</v-div>
</template>


<style>
#load_widget{
  alignment: bottom;
}
</style>
<script>
</script>