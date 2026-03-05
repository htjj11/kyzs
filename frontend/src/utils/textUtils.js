/**
 * 格式化标题文本，将多语言标题对象转换为"语言：标题"格式
 * @param {Object} title - 包含多语言标题的对象，格式如 { "en": [ "英文标题" ] }
 * @returns {string} 格式化后的标题文本
 */
export function formatTitle(title) {
  if (!title) return '';

  // 语言代码到中文名称的映射
  const languageMap = {
    'en': '英文',
    'zh': '中文',
    'jp': '日文',
    'de': '德文',
    'fr': '法文',
    'es': '西班牙文',
    'ru': '俄文'
  };

  // 获取第一个可用语言的标题
  const firstLang = Object.keys(title)[0];
  if (!firstLang) return '';

  const langName = languageMap[firstLang] || firstLang;
  const titleText = title[firstLang][0] || '';

  return `${langName}：${titleText}`;
}

/**
 * 格式化摘要文本（摘要），获取第一个可用语言的摘要并截断到指定长度
 * @param {Object} abstract - 包含多语言摘要的对象
 * @param {number} [maxLength=100] - 最大长度
 * @returns {string} 格式化后的摘要文本
 */
export function formatAbstract(abstract, maxLength = 100) {
  if (!abstract) return '';
  const firstAbstract = Object.values(abstract)[0] || '';
  const str = String(firstAbstract);
  if (str.length > maxLength) {
    return str.slice(0, maxLength) + '...';
  }
  return str;
}

 
/**
 * 格式化发明人列表，按顺序排列为"第1名：xxx 第二名：xxx"格式
 * @param {Array} inventors - 发明人数组，每个对象包含name和sequence属性
 * @returns {string} 格式化后的发明人列表字符串
 */
export function formatInventors(inventors) {
  console.log('格式化发明人列表', inventors);
  if (!Array.isArray(inventors) || inventors.length === 0) return '';

  // 按照sequence排序
  const sortedInventors = [...inventors].sort((a, b) => {
    return (a.sequence || 0) - (b.sequence || 0);
  });

  // 生成格式化字符串
  const formatted = sortedInventors.map((inventor, index) => {
    // 处理中文序数词：第1名、第二名、第三名...
    let ordinal;
    if (index === 0) {
      ordinal = '第1名';
    } else if (index === 1) {
      ordinal = '第2名';
    } else if (index === 2) {
      ordinal = '第3名';
    } else {
      ordinal = `第${index + 1}名`;
    }
    return `${ordinal}：${inventor.name}`;
  });

  return formatted.join('\n');
}
/**
 * 格式化多段落摘要文本，将多语言多段落摘要对象转换为"语言：1. 段落1，2. 段落2，..."格式
 * @param {Object} abstract - 包含多语言多段落摘要的对象，格式如 { "ru": [ "段落1", "段落2", ... ] }
 * @returns {string} 格式化后的多段落摘要文本
 */
export function formatMultiParagraphAbstract(abstract) {
  if (!abstract) return '';

  // 语言代码到中文名称的映射
  const languageMap = {
    'en': '英文',
    'zh': '中文',
    'jp': '日文',
    'de': '德文',
    'fr': '法文',
    'es': '西班牙文',
    'ru': '俄文'
  };

  // 获取第一个可用语言的摘要段落
  const firstLang = Object.keys(abstract)[0];
  if (!firstLang) return '';

  const langName = languageMap[firstLang] || firstLang;
  const paragraphs = abstract[firstLang] || [];

  if (paragraphs.length === 0) return '';

  // 格式化段落为带序号的字符串
  const formattedParagraphs = paragraphs.map((paragraph, index) => {
    return `${index + 1}. ${paragraph}`;
  });

  return `${langName}：${formattedParagraphs.join('\n')}`;
}

/**
 * 格式化申请人列表，按顺序排列为"第一名：xxx，第二名：xxx"格式
 * @param {Array} applicants - 申请人数组，每个对象包含name和sequence属性
 * @returns {string} 格式化后的申请人列表字符串
 */
export function formatApplicants(applicants) {
  if (!Array.isArray(applicants) || applicants.length === 0) return '';

  // 按照sequence排序
  const sortedApplicants = [...applicants].sort((a, b) => {
    return (a.sequence || 0) - (b.sequence || 0);
  });

  // 生成格式化字符串
  const formatted = sortedApplicants.map((applicant, index) => {
    // 处理中文序数词：第一名、第二名、第三名...
    let ordinal;
    if (index === 0) {
      ordinal = '第1名';
    } else if (index === 1) {
      ordinal = '第2名';
    } else if (index === 2) {
      ordinal = '第3名';
    } else {
      ordinal = `第${index + 1}名`;
    }
    return `${ordinal}：${applicant.name}`;
  });

  return formatted.join('\n');
}

/**
 * 格式化权利要求文本，将多语言权利要求对象转换为"语言：1.xxx 2.xxx"格式
 * @param {Object} claims - 包含多语言权利要求的对象，格式如 { "en": [ "1. 权利要求1文本", "2. 权利要求2文本", ... ] }
 * @returns {string} 格式化后的权利要求文本字符串
 */
export function formatClaims(claims) {
  if (!claims) return '';

  // 语言代码到中文名称的映射
  const languageMap = {
    'en': '英文',
    'zh': '中文',
    'jp': '日文',
    'de': '德文',
    'fr': '法文',
    'es': '西班牙文',
    'ru': '俄文'
  };

  // 获取第一个可用语言的权利要求列表
  const firstLang = Object.keys(claims)[0];
  if (!firstLang) return '';

  const langName = languageMap[firstLang] || firstLang;
  const claimList = claims[firstLang] || [];
  if (claimList.length === 0) return '';

  // 处理权利要求，确保按序号排序
  const formattedClaims = claimList.map(claim => {
    // 提取权利要求序号
    const match = claim.match(/^(\d+)\./);
    const number = match ? parseInt(match[1], 10) : 0;
    return {
      number,
      text: claim
    };
  }).sort((a, b) => {
    return a.number - b.number;
  }).map(claim => claim.text);

  return `${langName}：${formattedClaims.join('\n')}`;
}


/**
 * 格式化IPC分类号列表，转换为"1.xxx 2.xxx"格式
 * @param {Array} ipcList - IPC分类号数组，每个对象包含l1-l4字段
 * @returns {string} 格式化后的IPC分类号字符串
 */
export function formatIPC(ipcList) {
  if (!Array.isArray(ipcList) || ipcList.length === 0) return '';

  // 提取l4字段并添加序号
  const formatted = ipcList.map((ipc, index) => {
    return `${index + 1}.${ipc.l4}`;
  });

  return formatted.join('\n');
}


export function formatAssignees(assignees) {
  if (!Array.isArray(assignees) || assignees.length === 0) return '';
  
  // 处理嵌套数组结构，提取所有专利权人对象
  let flatAssignees = [];
  assignees.forEach(group => {
    if (Array.isArray(group)) {
      flatAssignees = flatAssignees.concat(group);
    } else {
      flatAssignees.push(group);
    }
  });
  
  // 按照sequence排序
  const sortedAssignees = [...flatAssignees].sort((a, b) => {
    return (a.sequence || 0) - (b.sequence || 0);
  });
  
  // 生成格式化字符串
  const formatted = sortedAssignees.map((assignee, index) => {
    return `第${index + 1}名：${assignee.name}`;
  });
  
  return formatted.join('\n');
}



/**
 * 格式化国家代码，转换为中文国家名称
 * @param {string} countryCode - 国家代码，如 "us"
 * @returns {string} 格式化后的中文国家名称
 */
export function formatCountry(countryCode) {
  if (!countryCode) return '';

  // 国家代码到中文名称的映射
  const countryMap = {
    'us': '美国',
    'cn': '中国',
    'jp': '日本',
    'de': '德国',
    'fr': '法国',
    'uk': '英国',
    'es': '西班牙',
    'ru': '俄罗斯',
    'kr': '韩国',
    'ca': '加拿大',
    'au': '澳大利亚'
  };

  return countryMap[countryCode.toLowerCase()] || countryCode;
}