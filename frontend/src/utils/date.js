/**
 * 格式化日期对象为指定格式的字符串
 * @param {number} date - 从1970年开始的秒数
 * @param {string} [format='yyyy-MM-dd'] - 格式字符串，默认为 'yyyy-MM-dd'，可选值 'yyyy-MM-dd'、'yyyy-MM-dd HH:mm:ss'、'yyyy年MM月dd日 HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = 'yyyy-MM-dd') {
  // 将秒数转换为毫秒并创建 Date 对象
  // 将传入的秒数转换为毫秒，创建 Date 对象
  console.log(date);
  const dateObj = new Date(date * 1000);
  // 检查 dateObj 是否为有效的 Date 对象，若不是或者时间无效，则返回 'Invalid Date'
  if (!(dateObj instanceof Date) || isNaN(dateObj.getTime())) {
    return 'Invalid Date';
  }
  const options = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  };

  // 处理仅日期的情况
  if (format.includes('yyyy-MM-dd') && !format.includes('HH')) {
    options.hour = undefined;
    options.minute = undefined;
    options.second = undefined;
  }

  const formatted = dateObj.toLocaleString('zh-CN', options);

  // 转换为指定格式
  if (format === 'yyyy-MM-dd') {
    return formatted.split('/').join('-');
  } else if (format === 'yyyy-MM-dd HH:mm:ss') {
    const [datePart, timePart] = formatted.split(' ');
    return `${datePart.split('/').join('-')} ${timePart}`;
  } else if (format === 'yyyy年MM月dd日 HH:mm:ss') {
    const [datePart, timePart] = formatted.split(' ');
    const [year, month, day] = datePart.split('/');
      // 移除月份前导零
      const monthNum = parseInt(month, 10);
      return `${year}年${monthNum}月${day}日 ${timePart}`;
  }

  return formatted;
}