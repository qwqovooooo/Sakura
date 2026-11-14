# OBS Studio 直播配置指南

## 功能说明

已实现的直播功能包括：

1. 直播间创建和管理
2. 推流地址生成
3. 直播状态控制
4. 直播间列表查询
5. 观众观看支持

## API 接口

### 1. 创建直播间
```
POST /live/create
Authorization: Bearer {token}

Body:
{
  "title": "我的直播间",
  "description": "直播间描述",
  "category": "娱乐",
  "cover_image": "封面图片URL"
}
```

### 2. 获取推流地址
```
GET /live/stream-url
Authorization: Bearer {token}

Response:
{
  "rtmp_url": "rtmp://localhost/live",
  "stream_key": "room_xxx?key=xxx",
  "push_url": "rtmp://localhost/live/room_xxx?key=xxx",
  "hls_url": "http://localhost:8080/live/room_xxx.m3u8",
  "flv_url": "http://localhost:8080/live/room_xxx.flv"
}
```

### 3. 开始直播
```
POST /live/start
Authorization: Bearer {token}
```

### 4. 结束直播
```
POST /live/stop
Authorization: Bearer {token}
```

### 5. 获取直播间列表
```
GET /live/list?page=1&page_size=20&only_live=true
```

### 6. 获取直播间详情
```
GET /live/{room_id}
```

## 流媒体服务器部署

### 方案一：使用 SRS（推荐）

1. 下载 SRS
```bash
docker pull ossrs/srs:5
```

2. 启动 SRS
```bash
docker run -d -p 1935:1935 -p 1985:1985 -p 8080:8080 ossrs/srs:5
```

3. 配置文件（可选）
```nginx
listen              1935;
max_connections     1000;
daemon              off;
srs_log_tank        console;

vhost __defaultVhost__ {
    hls {
        enabled         on;
        hls_path        ./objs/nginx/html;
        hls_fragment    10;
        hls_window      60;
    }
    http_remux {
        enabled     on;
        mount       [vhost]/[app]/[stream].flv;
    }
}

http_server {
    enabled         on;
    listen          8080;
    dir             ./objs/nginx/html;
}
```

4. 修改代码中的地址
```python
# 在 live_stream.py 的 build_stream_urls 函数中
rtmp_server = "rtmp://你的服务器IP/live"
hls_server = "http://你的服务器IP:8080/live"
flv_server = "http://你的服务器IP:8080/live"
```

### 方案二：使用云服务

#### 七牛云直播
1. 注册七牛云账号
2. 创建直播空间
3. 获取推流域名和播放域名
4. 修改配置

#### 阿里云直播
1. 开通阿里云直播服务
2. 配置推流域名和播放域名
3. 获取鉴权密钥
4. 修改配置

## OBS Studio 配置

### 1. 下载安装
- 访问 https://obsproject.com/
- 下载并安装 OBS Studio

### 2. 添加场景和来源
1. 点击"场景" → 添加场景
2. 点击"来源" → 添加来源（摄像头/窗口捕获/显示器捕获等）

### 3. 配置推流
1. 打开"设置" → "推流"
2. 服务：选择"自定义"
3. 服务器：输入 `rtmp://你的服务器IP/live`
4. 串流密钥：输入从API获取的 stream_key

### 4. 开始推流
1. 点击"开始推流"按钮
2. 调用后端 `/live/start` 接口

## 前端播放器集成

### 使用 flv.js

```bash
npm install flv.js
```

```vue
<template>
  <div class="live-player">
    <video ref="videoElement" controls autoplay></video>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import flvjs from 'flv.js'

const props = defineProps({
  flvUrl: String
})

const videoElement = ref(null)
let flvPlayer = null

onMounted(() => {
  if (flvjs.isSupported()) {
    flvPlayer = flvjs.createPlayer({
      type: 'flv',
      url: props.flvUrl
    })
    flvPlayer.attachMediaElement(videoElement.value)
    flvPlayer.load()
    flvPlayer.play()
  }
})

onUnmounted(() => {
  if (flvPlayer) {
    flvPlayer.destroy()
  }
})
</script>
```

### 使用 video.js（HLS）

```bash
npm install video.js
```

```vue
<template>
  <div class="live-player">
    <video ref="videoElement" class="video-js"></video>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import videojs from 'video.js'
import 'video.js/dist/video-js.css'

const props = defineProps({
  hlsUrl: String
})

const videoElement = ref(null)
let player = null

onMounted(() => {
  player = videojs(videoElement.value, {
    controls: true,
    autoplay: true,
    preload: 'auto'
  })
  player.src({
    src: props.hlsUrl,
    type: 'application/x-mpegURL'
  })
})

onUnmounted(() => {
  if (player) {
    player.dispose()
  }
})
</script>
```

## 测试流程

1. 用户登录
2. 调用 `/live/create` 创建直播间
3. 调用 `/live/stream-url` 获取推流地址
4. 在 OBS 中配置推流地址
5. OBS 开始推流
6. 调用 `/live/start` 标记直播开始
7. 观众访问播放页面观看直播
8. 主播结束直播，调用 `/live/stop`

## 注意事项

1. 流媒体服务器需要单独部署
2. 推流需要较好的网络带宽
3. 播放延迟一般在 3-10 秒
4. 建议使用 CDN 加速播放
5. 生产环境需要配置鉴权和防盗链

## 下一步

- [ ] 创建前端直播间列表页面
- [ ] 创建前端直播播放页面
- [ ] 创建主播控制台页面
- [ ] 部署流媒体服务器（SRS）
- [ ] 配置 OBS Studio
- [ ] 进行推流测试
