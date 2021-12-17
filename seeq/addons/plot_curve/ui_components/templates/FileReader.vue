<template>
  <div>
    <v-btn id='button' @click="onPickFile">Load Data</v-btn>
    <input type="file" style="display: none" ref="fileInput" :accept="allowed_extensions" @change="onFileChange"/>
  </div>
</template>

<style>
#button {
  background-color: #007960;
  color: whitesmoke;
}
</style>

<script>
export default {
  methods:{
    onPickFile () {
      this.$refs.fileInput.click()
    },
    onFileChange(ev) {
      const file = ev.target.files[0];
      const reader = new FileReader();
      reader.onload = e => this.file_contents = e.target.result;
      reader.readAsText(file);
    }
  }
}
</script>
