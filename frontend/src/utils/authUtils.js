/**
 * 从cookie中获取user_id
 * @returns {number|null} 用户ID，如果cookie中没有或解析失败则返回null
 */
export function getUserIdFromCookie() {
  try {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('user_id='))
      ?.split('=')[1];
    return cookieValue ? parseInt(cookieValue) : null; // 如果cookie中没有，返回null
  } catch (error) {
    console.error('获取cookie中的user_id失败:', error);
    return null; // 出错时返回null
  }
}



/**
 * 从cookie中获取user_name
 * @returns {string|null} 用户名，如果cookie中没有或解析失败则返回null
 */
export function getUserNameFromCookie() {
  try {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('user_name='))
      ?.split('=')[1];
    return cookieValue || null; // 如果cookie中没有，返回null
  } catch (error) {
    console.error('获取cookie中的user_name失败:', error);
    return null; // 出错时返回null
  }
}



/**
 * 设置cookie中的user_id
 * @param {number|null} userId 用户ID，设为null表示清除cookie
 * @param {number} days 过期时间（天）
 */
export function setUserIdCookie(userId, days = 30) {
  if (userId === null) {
    // 清除cookie
    document.cookie = 'user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  } else {
    // 设置cookie
    const expires = new Date();
    expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `user_id=${userId}; expires=${expires.toUTCString()}; path=/;`;
  }
}

/**
 * 设置user_name
 * @param {string} userName 用户名
 */
export function setUserNameCookie(userName) {
  if (userName === null) {
    // 清除cookie
    document.cookie = 'user_name=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  } else {
    // 设置cookie
    const expires = new Date();
    expires.setTime(expires.getTime() + 1 * 24 * 60 * 60 * 1000);
    document.cookie = `user_name=${userName}; expires=${expires.toUTCString()}; path=/;`;
  }
}

/**
 * 清除登录状态（注销）
 */
export function logoutUser() {
  setUserIdCookie(null);
}