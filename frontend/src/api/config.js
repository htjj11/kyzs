// 服务的统一url
let api_url = 'http://10.68.202.238:8000'; // 正式部署 (Win10 Server)

// 针对调试机 (Win11) 自动切换
// 提示：Win11 调试通常在本地环境，故使用 hostname 判断最为准确
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    api_url = 'http://127.0.0.1:8000'; // 调试机地址 (Win11)
}

export default api_url;