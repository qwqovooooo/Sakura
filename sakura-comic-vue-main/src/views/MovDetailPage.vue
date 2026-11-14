<template>
  <MovDetail :vod_id="vod_id"/>
  <MovieQA :vod_id="vod_id" style="margin: 20px auto;"/>
  <CommentVue :vod_id="vod_id"/>
  <el-backtop :right="50" :bottom="80" />
</template>

<script>
// 详情页
import MovDetail from '../components/MovDetail.vue'
import MovieQA from '../components/MovieQA.vue'
import CommentVue from '../components/Comments.vue'

export default {
  name: 'MovDetailPage',
  props: {
        vod_id: String
    },
  components: {
    MovDetail,
    MovieQA,
    CommentVue
  }
}
</script>
