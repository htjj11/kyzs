import axios from "axios";
import { api_url } from "./config";
import {
    getUserIdFromCookie,
    setUserIdCookie,
    getUserNameFromCookie,
    setUserNameCookie,
    setExpireTimeCookie,
    getPermissionCookie,
    setPermissionCookie,
    getRagflowIdFromCookie,
    setRagflowIdCookie
} from "@/utils/authUtils";

// 验证授权状态的函数
const api = axios.create(
    {
        baseURL: api_url, //这里配置的是后端服务提供的接口
        timeout: 200000,
        // 大文件（如知识库 base64 上传）需放宽，否则浏览器/axios 可能按默认 ~10MB 限制请求体
        maxBodyLength: Infinity,
        maxContentLength: Infinity,
        headers: {
            'Content-Type': 'application/json;charset=utf-8',
        },
    },
);

// 请求拦截器
api.interceptors.request.use(
    config => {
        // 获取用户ID
        const userId = getUserIdFromCookie();

        // 每次发请求时自动续签 Cookie 的有效时间（30分钟）
        if (userId) {
            const expireTime = Date.now() + 30 * 60 * 1000; // 计算新的截止时间
            setExpireTimeCookie(expireTime, 30);
            setUserIdCookie(userId, 30);

            const userName = getUserNameFromCookie();
            if (userName) {
                setUserNameCookie(userName, 30);
            }

            const permission = getPermissionCookie();
            if (permission) {
                setPermissionCookie(permission, 30);
            }

            const ragflowId = getRagflowIdFromCookie();
            if (ragflowId) {
                setRagflowIdCookie(ragflowId, 30);
            }
        }

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