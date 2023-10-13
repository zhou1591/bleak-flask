python bleak 包 实现得蓝牙

用于解决 浏览器的webble 只有20mtu 的问题 windows

优点  可以突破 20mtu 限制  不需要 noble 和bleno 这两个node 包一样需要覆盖通用蓝牙驱动

缺点 慢  读写读大概50毫秒一次 写100-150毫秒  根据数据量大小波动   webble 20毫秒  不能扫描bt 蓝牙



