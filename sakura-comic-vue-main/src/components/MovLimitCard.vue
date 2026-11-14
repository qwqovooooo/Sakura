<template>  
  <div class="home-card" v-show="contentshow">
    <el-row style="margin: 15px 0 0 0">
        <span class="home-card-type">{{ type_id_names[movtype] }}</span>
        <router-link :to="'/movtype/'+ movtype" class="home-card-type" style="text-decoration: none; color:#8B5A2B;">
          &nbsp; 更多>
        </router-link>
    </el-row>
    
    <!-- 加载动画 -->
    <div v-if="loading" style="text-align: center; padding: 40px;">
      <el-icon class="is-loading" :size="40" color="#FF9A3C">
        <Loading />
      </el-icon>
      <p style="color: #A0826D; margin-top: 10px;">加载中...</p>
    </div>
    
    <!-- 视频列表 -->
    <el-row v-else alignment="flex-start">
      <el-col 
        v-for="o in movieList"
        :key="o.vod_id"
        :xs="8" :sm="4" :md="4" 
        style="padding: 9px;">
        <router-link :to="'/movdetail/'+ o.vod_id" style="text-decoration: none;" target="_blank">   
        <el-card
        class="box-card" 
        @click="selectMovie"
        shadow="hover"
        :body-style="{ padding: '8px 5px', background: 'rgba(255, 248, 235, 0.8)', borderRadius: '12px' }">
        <div class="card-div">
          <img :src="o.vod_pic" class="card-image" loading="lazy"/>
          <span class="card-remark">{{ o.vod_remarks }}</span>
        </div>
      
        <div style="padding: 0px;">
          
          <span style="line-height: 26px; font-size: 15px; color:#8B5A2B; display: flex; margin-top: 4px; text-overflow: ellipsis; overflow: hidden; width: 80%; white-space: nowrap;">
            <el-tooltip class="box-item" effect="dark" :content="o.vod_name" placement="bottom-end" :show-after="1000">
            {{ o.vod_name }}
            </el-tooltip>
          </span>
          <!-- <div class="bottom">
            <p style="font-size:smaller; color:#777; margin: 4px 0">{{ o.vod_remarks }}</p>
          </div> -->
        </div>
      
      </el-card>
      </router-link>
      </el-col>
   </el-row>
  </div>
</template>

<script>
// 有限展示视频卡片列表
import apiGetMovList from '../apis/getMovInfo'
import SakuraBigImg from './SakuraBigImg.vue'
import { Loading } from '@element-plus/icons-vue'
import { useStore } from 'vuex'

export default {
    name: "MovLimitCard",
    props: {
        movtype: Number
    },
    components: {
      SakuraBigImg,
      Loading
    },

    setup() {
      const store = useStore()  // 该方法用于返回store 实例
      const type_id_names = {
        1: "电影",
        2: "电视剧",
        3: "综艺",
        4: "动漫",
        5: "咨询"
    }
      return {
            store,
            type_id_names
        }
    },

    data() {
      return {
        page: 1,
        contentshow: true,
        loading: true,  // 添加加载状态
        movieList: []
      }
    },

    methods: {
        selectMovie(h) {
            console.log(h)
        },

        getMovList() {
          this.loading = true  // 开始加载
          const param =  { 
              page: this.page,
              movtype: this.movtype 
              }

          apiGetMovList(param).then(
            (res) => {
              console.log('API响应:', res)  // 添加日志
              // axios 拦截器已经返回了 response.data，所以 res 就是 {code: 200, message: 'success', data: [...]}
              if (res && res.code === 200 && res.data && res.data.length > 0) {
                  for (var i in res.data) {
                    this.movieList.push(res.data[i])
                 }
              } else {
                console.log('没有数据或响应格式错误', res)
                this.contentshow = false
              }
              this.loading = false  // 加载完成
             }
          ).catch(
            (error) => {
                console.error('API请求错误:', error)
                this.contentshow = false
                this.loading = false  // 加载失败
            }
          )
      }
   },

   created() {
    this.getMovList()
   }

}
</script>


<style>
span.home-card-type {
    float: left;
    margin: 10px;
    font-size: 20px; 
    font-weight: bold;
    line-height: 20px;
    color: #8B5A2B;
}

.home-card-type {
    float: left;
    margin: 10px;
    line-height: 20px;
}

a.home-card-type:hover {
    color: #FF9A3C !important;
}

.box-card {
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s;
  background: rgba(255, 248, 235, 0.6);
  border: 1px solid rgba(255, 173, 96, 0.2);
}

.box-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 20px rgba(255, 154, 60, 0.25);
}

.card-image {
  border-radius: 8px;
}

.card-remark {
  background: linear-gradient(135deg, #FFB366 0%, #FF9A3C 100%);
  color: white;
  font-weight: 500;
}
</style>
