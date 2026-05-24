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
 * @param {number} minutes 过期时间（分钟）
 */
export function setUserIdCookie(userId, minutes = 30) {
  if (userId === null) {
    // 清除cookie
    document.cookie = 'user_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  } else {
    // 设置cookie
    const expires = new Date();
    expires.setTime(expires.getTime() + minutes * 60 * 1000);
    document.cookie = `user_id=${userId}; expires=${expires.toUTCString()}; path=/;`;
  }
}

/**
 * 设置user_name
 * @param {string} userName 用户名
 * @param {number} minutes 过期时间（分钟）
 */
export function setUserNameCookie(userName, minutes = 30) {
  if (userName === null) {
    // 清除cookie
    document.cookie = 'user_name=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  } else {
    // 设置cookie
    const expires = new Date();
    expires.setTime(expires.getTime() + minutes * 60 * 1000);
    document.cookie = `user_name=${userName}; expires=${expires.toUTCString()}; path=/;`;
  }
}

/**
 * 设置截止日期（过期时间）
 * @param {number|null} expireTime 时间戳，设为null表示清除cookie
 * @param {number} minutes 过期时间（分钟）
 */
export function setExpireTimeCookie(expireTime, minutes = 30) {
  if (expireTime === null) {
    // 清除cookie
    document.cookie = 'expire_time=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  } else {
    // 设置cookie
    const expires = new Date();
    expires.setTime(expires.getTime() + minutes * 60 * 1000);
    document.cookie = `expire_time=${expireTime}; expires=${expires.toUTCString()}; path=/;`;
  }
}

/**
 * 从cookie中获取截止日期
 * @returns {number|null} 截止日期时间戳
 */
export function getExpireTimeFromCookie() {
  try {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('expire_time='))
      ?.split('=')[1];
    return cookieValue ? parseInt(cookieValue) : null;
  } catch (error) {
    console.error('获取cookie中的expire_time失败:', error);
    return null;
  }
}

/**
 * 从cookie中获取ragflow_id
 * @returns {string|null}
 */
export function getRagflowIdFromCookie() {
  try {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('ragflow_id='))
      ?.split('=')[1];
    if (!cookieValue) return null;
    const decoded = decodeURIComponent(cookieValue);
    return decoded || null;
  } catch (error) {
    console.error('获取cookie中的ragflow_id失败:', error);
    return null;
  }
}

/**
 * 设置ragflow_id
 * @param {string|null} ragflowId
 * @param {number} minutes 过期时间（分钟）
 */
export function setRagflowIdCookie(ragflowId, minutes = 30) {
  if (ragflowId === null || ragflowId === undefined || ragflowId === '') {
    document.cookie = 'ragflow_id=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  } else {
    const encodedValue = encodeURIComponent(String(ragflowId));
    const expires = new Date();
    expires.setTime(expires.getTime() + minutes * 60 * 1000);
    document.cookie = `ragflow_id=${encodedValue}; expires=${expires.toUTCString()}; path=/;`;
  }
}

/**
 * 设置permission
 * @param {string|null|object} permission 用户权限，设为null表示清除cookie
 * @param {number} minutes 过期时间（分钟）
 */
export function setPermissionCookie(permission, minutes = 30) {
  if (permission === null) {
    document.cookie = 'permission=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
  } else {
    const encodedValue = encodeURIComponent(typeof permission === 'string' ? permission : JSON.stringify(permission));
    const expires = new Date();
    expires.setTime(expires.getTime() + minutes * 60 * 1000);
    document.cookie = `permission=${encodedValue}; expires=${expires.toUTCString()}; path=/;`;
  }
}

/**
 * 从cookie中获取permission
 * @returns {any} 用户权限
 */
export function getPermissionCookie() {
  try {
    const cookieValue = document.cookie
      .split('; ')
      .find(row => row.startsWith('permission='))
      ?.split('=')[1];
    if (cookieValue) {
        const decoded = decodeURIComponent(cookieValue);
        try {
            return JSON.parse(decoded);
        } catch {
            return decoded;
        }
    }
    return null;
  } catch (error) {
    console.error('获取cookie中的permission失败:', error);
    return null;
  }
}

/**
 * 是否拥有超级管理员权限（permission 含 admin:admin）
 * @returns {boolean}
 */
export function hasSuperAdminPermission() {
  const permissions = getPermissionCookie() || [];
  return Array.isArray(permissions) && permissions.includes('admin:admin');
}

/**
 * 清除登录状态（注销）
 */
export function logoutUser() {
  setUserIdCookie(null);
  setUserNameCookie(null);
  setExpireTimeCookie(null);
  setPermissionCookie(null);
  setRagflowIdCookie(null);
}