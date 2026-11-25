// 国家和城市的中英文翻译映射表
const countryTranslations = {
  // 欧洲国家
  '德国': 'Germany',
  '英国': 'United Kingdom',
  '法国': 'France',
  '意大利': 'Italy',
  '西班牙': 'Spain',
  '荷兰': 'Netherlands',
  '比利时': 'Belgium',
  '瑞士': 'Switzerland',
  '奥地利': 'Austria',
  '瑞典': 'Sweden',
  '挪威': 'Norway',
  '丹麦': 'Denmark',
  '芬兰': 'Finland',
  '波兰': 'Poland',
  '保加利亚': 'Bulgaria',
  '捷克': 'Czech Republic',
  '克罗地亚': 'Croatia',
  '匈牙利': 'Hungary',
  '葡萄牙': 'Portugal',
  '希腊': 'Greece',
  '俄罗斯': 'Russia',
  '土耳其': 'Turkey',
  
  // 亚洲国家
  '中国': 'China',
  '日本': 'Japan',
  '韩国': 'South Korea',
  '印度': 'India',
  '泰国': 'Thailand',
  '越南': 'Vietnam',
  '马来西亚': 'Malaysia',
  '新加坡': 'Singapore',
  '印度尼西亚': 'Indonesia',
  '菲律宾': 'Philippines',
  '缅甸': 'Myanmar',
  '柬埔寨': 'Cambodia',
  '老挝': 'Laos',
  '巴基斯坦': 'Pakistan',
  '孟加拉国': 'Bangladesh',
  '斯里兰卡': 'Sri Lanka',
  '阿联酋': 'United Arab Emirates',
  '沙特阿拉伯': 'Saudi Arabia',
  '以色列': 'Israel',
  '伊朗': 'Iran',
  '伊拉克': 'Iraq',
  
  // 北美洲
  '美国': 'United States',
  '加拿大': 'Canada',
  '墨西哥': 'Mexico',
  
  // 南美洲
  '巴西': 'Brazil',
  '阿根廷': 'Argentina',
  '智利': 'Chile',
  '秘鲁': 'Peru',
  '哥伦比亚': 'Colombia',
  '委内瑞拉': 'Venezuela',
  
  // 大洋洲
  '澳大利亚': 'Australia',
  '澳洲': 'Australia',
  '新西兰': 'New Zealand',
  
  // 非洲
  '南非': 'South Africa',
  '埃及': 'Egypt',
  '尼日利亚': 'Nigeria',
  '摩洛哥': 'Morocco',
  '肯尼亚': 'Kenya',
  '埃塞俄比亚': 'Ethiopia'
}

// 洲名翻译
const continentTranslations = {
  '亚洲': 'Asia',
  '欧洲': 'Europe',
  '北美洲': 'North America',
  '南美洲': 'South America',
  '非洲': 'Africa',
  '大洋洲': 'Oceania',
  '南极洲': 'Antarctica',
  // 地区翻译
  '北欧': 'Northern Europe',
  '南欧': 'Southern Europe',
  '西欧': 'Western Europe',
  '东欧': 'Eastern Europe',
  '中欧': 'Central Europe',
  '东南亚': 'Southeast Asia',
  '中东': 'Middle East',
  '北非': 'North Africa',
  '东非': 'East Africa',
  '西非': 'West Africa',
  '南非地区': 'Southern Africa'
}

// 常见城市翻译
const cityTranslations = {
  // 中国城市
  '北京': 'Beijing',
  '上海': 'Shanghai',
  '广州': 'Guangzhou',
  '深圳': 'Shenzhen',
  '天津': 'Tianjin',
  '重庆': 'Chongqing',
  '成都': 'Chengdu',
  '西安': 'Xi\'an',
  '杭州': 'Hangzhou',
  '苏州': 'Suzhou',
  '南京': 'Nanjing',
  '武汉': 'Wuhan',
  '青岛': 'Qingdao',
  '大连': 'Dalian',
  '宁波': 'Ningbo',
  '厦门': 'Xiamen',
  '福州': 'Fuzhou',
  '合肥': 'Hefei',
  '郑州': 'Zhengzhou',
  '长沙': 'Changsha',
  '济南': 'Jinan',
  '石家庄': 'Shijiazhuang',
  '沈阳': 'Shenyang',
  '长春': 'Changchun',
  '哈尔滨': 'Harbin',
  '昆明': 'Kunming',
  '南昌': 'Nanchang',
  '太原': 'Taiyuan',
  '呼和浩特': 'Hohhot',
  '乌鲁木齐': 'Urumqi',
  '拉萨': 'Lhasa',
  
  // 其他国家主要城市
  '东京': 'Tokyo',
  '大阪': 'Osaka',
  '京都': 'Kyoto',
  '首尔': 'Seoul',
  '釜山': 'Busan',
  '曼谷': 'Bangkok',
  '胡志明市': 'Ho Chi Minh City',
  '河内': 'Hanoi',
  '吉隆坡': 'Kuala Lumpur',
  '雅加达': 'Jakarta',
  '马尼拉': 'Manila',
  '新德里': 'New Delhi',
  '孟买': 'Mumbai',
  '迪拜': 'Dubai',
  '杜拜': 'Dubai',
  '阿布扎比': 'Abu Dhabi',
  '利雅得': 'Riyadh',
  '特拉维夫': 'Tel Aviv',
  '德黑兰': 'Tehran',
  '伊斯坦布尔': 'Istanbul',
  '莫斯科': 'Moscow',
  '圣彼得堡': 'Saint Petersburg',
  '伦敦': 'London',
  '曼彻斯特': 'Manchester',
  '伯明翰': 'Birmingham',
  '巴黎': 'Paris',
  '马赛': 'Marseille',
  '里昂': 'Lyon',
  '柏林': 'Berlin',
  '慕尼黑': 'Munich',
  '法兰克福': 'Frankfurt',
  '汉堡': 'Hamburg',
  '罗马': 'Rome',
  '米兰': 'Milan',
  '那不勒斯': 'Naples',
  '马德里': 'Madrid',
  '巴塞罗那': 'Barcelona',
  '阿姆斯特丹': 'Amsterdam',
  '鹿特丹': 'Rotterdam',
  '布鲁塞尔': 'Brussels',
  '苏黎世': 'Zurich',
  '日内瓦': 'Geneva',
  '维也纳': 'Vienna',
  '斯德哥尔摩': 'Stockholm',
  '奥斯陆': 'Oslo',
  '哥本哈根': 'Copenhagen',
  '赫尔辛基': 'Helsinki',
  '华沙': 'Warsaw',
  '布拉格': 'Prague',
  '布达佩斯': 'Budapest',
  '雅典': 'Athens',
  '里斯本': 'Lisbon',
  '纽约': 'New York',
  '洛杉矶': 'Los Angeles',
  '芝加哥': 'Chicago',
  '休斯顿': 'Houston',
  '费城': 'Philadelphia',
  '凤凰城': 'Phoenix',
  '圣安东尼奥': 'San Antonio',
  '圣地亚哥': 'San Diego',
  '达拉斯': 'Dallas',
  '圣何塞': 'San Jose',
  '奥斯汀': 'Austin',
  '多伦多': 'Toronto',
  '温哥华': 'Vancouver',
  '蒙特利尔': 'Montreal',
  '墨西哥城': 'Mexico City',
  '圣保罗': 'São Paulo',
  '里约热内卢': 'Rio de Janeiro',
  '布宜诺斯艾利斯': 'Buenos Aires',
  '圣地亚哥': 'Santiago',
  '利马': 'Lima',
  '波哥大': 'Bogotá',
  '加拉加斯': 'Caracas',
  '悉尼': 'Sydney',
  '墨尔本': 'Melbourne',
  '布里斯班': 'Brisbane',
  '珀斯': 'Perth',
  '奥克兰': 'Auckland',
  '开普敦': 'Cape Town',
  '约翰内斯堡': 'Johannesburg',
  '开罗': 'Cairo',
  '拉各斯': 'Lagos',
  '卡萨布兰卡': 'Casablanca',
  '内罗毕': 'Nairobi',
  '亚的斯亚贝巴': 'Addis Ababa'
}

/**
 * 翻译地址中的中文国家/城市名为英文
 * @param {string} address - 原始地址
 * @returns {object} - 包含原文和翻译的对象
 */
function translateAddress(address) {
  if (!address || typeof address !== 'string') {
    return {
      original: address || '',
      translated: address || '',
      hasTranslation: false
    }
  }

  let translatedAddress = address
  let hasTranslation = false

  // 先翻译洲名和地区名
  Object.entries(continentTranslations).forEach(([chinese, english]) => {
    if (address.includes(chinese)) {
      translatedAddress = translatedAddress.replace(new RegExp(chinese, 'g'), english)
      hasTranslation = true
    }
  })

  // 再翻译国家名
  Object.entries(countryTranslations).forEach(([chinese, english]) => {
    if (address.includes(chinese)) {
      translatedAddress = translatedAddress.replace(new RegExp(chinese, 'g'), english)
      hasTranslation = true
    }
  })

  // 最后翻译城市名
  Object.entries(cityTranslations).forEach(([chinese, english]) => {
    if (address.includes(chinese)) {
      translatedAddress = translatedAddress.replace(new RegExp(chinese, 'g'), english)
      hasTranslation = true
    }
  })

  return {
    original: address,
    translated: translatedAddress,
    hasTranslation: hasTranslation
  }
}

/**
 * 批量翻译地址列表
 * @param {Array} addresses - 地址列表
 * @returns {Array} - 翻译后的地址列表
 */
function translateAddresses(addresses) {
  if (!Array.isArray(addresses)) {
    return []
  }

  return addresses.map(item => {
    if (typeof item === 'string') {
      return translateAddress(item)
    } else if (item && item.address) {
      const translation = translateAddress(item.address)
      return {
        ...item,
        ...translation
      }
    }
    return item
  })
}

/**
 * 获取所有支持的国家翻译
 * @returns {object} - 国家翻译映射表
 */
function getCountryTranslations() {
  return { ...countryTranslations }
}

/**
 * 获取所有支持的城市翻译
 * @returns {object} - 城市翻译映射表
 */
function getCityTranslations() {
  return { ...cityTranslations }
}

/**
 * 获取所有支持的洲名翻译
 * @returns {object} - 洲名翻译映射表
 */
function getContinentTranslations() {
  return { ...continentTranslations }
}

export {
  translateAddress,
  translateAddresses,
  getCountryTranslations,
  getCityTranslations,
  getContinentTranslations
} 