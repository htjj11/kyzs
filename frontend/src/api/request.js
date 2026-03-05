import axios from "axios";
import api_url from "./config";
import { getUserIdFromCookie } from "@/utils/authUtils";

// 验证授权状态的函数
const api = axios.create(
    {
        // baseURL: "http://10.68.249.12:33332", //这里配置的是后端服务提供的接口
        baseURL: api_url, //这里配置的是后端服务提供的接口
        timeout: 200000,
        headers: {
            'Content-Type': 'application/json;charset=utf-8',
            // '1token': Cookies.get('token'),
        },
    },
);

// 请求拦截器
api.interceptors.request.use(
    config => {
        // 获取用户ID
        const userId = getUserIdFromCookie();
        
        // 如果是POST请求且有请求体，添加user_id字段
        if (config.method === 'post' && config.data) {
            // 确保config.data是对象
            config.data = typeof config.data === 'object' ? config.data : {};
            // 添加user_id字段（如果存在且还未添加）
            if (userId && !config.data.user_id) {
                config.data.user_id = userId;
            }
        }
        
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

export default api;