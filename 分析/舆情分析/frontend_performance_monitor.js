// 前端性能监控脚本
// 可以在浏览器控制台中运行此脚本，监控页面加载和数据采集的性能指标

// 性能监控对象
const PerformanceMonitor = {
    // 记录开始时间
    startTime: {},
    
    // 记录结束时间
    endTime: {},
    
    // 记录性能数据
    performanceData: {},
    
    // 开始计时
    start: function(key) {
        this.startTime[key] = performance.now();
        console.log(`[${new Date().toISOString()}] ${key} - 开始计时`);
    },
    
    // 结束计时
    end: function(key) {
        if (this.startTime[key]) {
            this.endTime[key] = performance.now();
            const duration = this.endTime[key] - this.startTime[key];
            this.performanceData[key] = duration;
            console.log(`[${new Date().toISOString()}] ${key} - 完成，耗时: ${duration.toFixed(2)}ms`);
            return duration;
        } else {
            console.error(`[${new Date().toISOString()}] ${key} - 没有找到开始时间记录`);
            return null;
        }
    },
    
    // 记录页面加载性能
    logPageLoad: function() {
        if (performance.timing) {
            const timing = performance.timing;
            const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
            const domReadyTime = timing.domContentLoadedEventEnd - timing.navigationStart;
            const firstPaintTime = performance.getEntriesByType('paint')[0]?.startTime || 0;
            
            console.log('\n=== 页面加载性能指标 ===');
            console.log(`页面总加载时间: ${pageLoadTime}ms`);
            console.log(`DOM准备完成时间: ${domReadyTime}ms`);
            console.log(`首次绘制时间: ${firstPaintTime}ms`);
            console.log(`首屏时间: ${(timing.domContentLoadedEventEnd - timing.navigationStart)}ms`);
            console.log(`资源加载完成时间: ${(timing.loadEventEnd - timing.navigationStart)}ms`);
        } else {
            console.error('浏览器不支持performance.timing API');
        }
    },
    
    // 记录资源加载性能
    logResourceLoad: function() {
        const resources = performance.getEntriesByType('resource');
        console.log('\n=== 资源加载性能指标 ===');
        console.log(`总资源数: ${resources.length}`);
        
        // 按资源类型分组
        const resourceTypes = {};
        resources.forEach(resource => {
            const type = resource.initiatorType || 'other';
            if (!resourceTypes[type]) {
                resourceTypes[type] = [];
            }
            resourceTypes[type].push(resource);
        });
        
        // 输出各类型资源的加载情况
        Object.keys(resourceTypes).forEach(type => {
            const typeResources = resourceTypes[type];
            const totalLoadTime = typeResources.reduce((sum, res) => sum + res.duration, 0);
            const avgLoadTime = totalLoadTime / typeResources.length;
            
            console.log(`\n${type}资源:`);
            console.log(`  数量: ${typeResources.length}`);
            console.log(`  总加载时间: ${totalLoadTime.toFixed(2)}ms`);
            console.log(`  平均加载时间: ${avgLoadTime.toFixed(2)}ms`);
            
            // 输出加载时间最长的前5个资源
            const sortedResources = typeResources.sort((a, b) => b.duration - a.duration);
            console.log(`  最慢的5个资源:`);
            sortedResources.slice(0, 5).forEach((res, index) => {
                console.log(`    ${index + 1}. ${res.name} - ${res.duration.toFixed(2)}ms`);
            });
        });
    },
    
    // 监控AJAX请求
    monitorAjax: function() {
        const originalXHR = XMLHttpRequest.prototype.open;
        
        XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
            const xhr = this;
            const requestStartTime = performance.now();
            const requestInfo = {
                method: method,
                url: url,
                startTime: requestStartTime
            };
            
            // 记录请求开始
            console.log(`[${new Date().toISOString()}] AJAX请求开始 - ${method} ${url}`);
            
            // 监听请求完成
            xhr.addEventListener('loadend', function() {
                const requestEndTime = performance.now();
                const duration = requestEndTime - requestStartTime;
                requestInfo.endTime = requestEndTime;
                requestInfo.duration = duration;
                requestInfo.status = xhr.status;
                
                console.log(`[${new Date().toISOString()}] AJAX请求完成 - ${method} ${url} (${xhr.status}) - 耗时: ${duration.toFixed(2)}ms`);
                
                // 记录到性能数据中
                const requestKey = `ajax_${method}_${url}`;
                PerformanceMonitor.performanceData[requestKey] = duration;
            });
            
            // 监听错误
            xhr.addEventListener('error', function() {
                const requestEndTime = performance.now();
                const duration = requestEndTime - requestStartTime;
                console.error(`[${new Date().toISOString()}] AJAX请求错误 - ${method} ${url} - 耗时: ${duration.toFixed(2)}ms`);
            });
            
            return originalXHR.apply(this, arguments);
        };
        
        console.log('AJAX请求监控已启用');
    },
    
    // 监控DOM操作性能
    monitorDomOperations: function() {
        // 监控DOM节点创建
        const originalCreateElement = document.createElement;
        document.createElement = function(tagName) {
            const startTime = performance.now();
            const element = originalCreateElement.apply(this, arguments);
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            // 只记录耗时较长的操作
            if (duration > 1) {
                console.log(`[${new Date().toISOString()}] 创建DOM元素 <${tagName}> - 耗时: ${duration.toFixed(2)}ms`);
            }
            
            return element;
        };
        
        // 监控DOM插入
        const originalAppendChild = Element.prototype.appendChild;
        Element.prototype.appendChild = function(child) {
            const startTime = performance.now();
            const result = originalAppendChild.apply(this, arguments);
            const endTime = performance.now();
            const duration = endTime - startTime;
            
            // 只记录耗时较长的操作
            if (duration > 1) {
                console.log(`[${new Date().toISOString()}] 插入DOM元素 - 耗时: ${duration.toFixed(2)}ms`);
            }
            
            return result;
        };
        
        console.log('DOM操作监控已启用');
    },
    
    // 输出所有性能数据
    logAllData: function() {
        console.log('\n=== 所有性能数据 ===');
        Object.keys(this.performanceData).forEach(key => {
            console.log(`${key}: ${this.performanceData[key].toFixed(2)}ms`);
        });
    },
    
    // 导出性能数据
    exportData: function() {
        const data = {
            timestamp: new Date().toISOString(),
            performanceData: this.performanceData,
            pageLoad: performance.timing || {},
            resources: performance.getEntriesByType('resource') || []
        };
        
        const dataStr = JSON.stringify(data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `performance_${new Date().getTime()}.json`;
        link.click();
        
        URL.revokeObjectURL(url);
        console.log('性能数据已导出');
    }
};

// 初始化性能监控
window.addEventListener('load', function() {
    console.log('\n=== 前端性能监控初始化 ===');
    PerformanceMonitor.logPageLoad();
    PerformanceMonitor.logResourceLoad();
    PerformanceMonitor.monitorAjax();
    PerformanceMonitor.monitorDomOperations();
    
    // 3秒后输出所有性能数据
    setTimeout(function() {
        PerformanceMonitor.logAllData();
    }, 3000);
});

// 将性能监控对象暴露到全局
window.PerformanceMonitor = PerformanceMonitor;

console.log('\n=== 性能监控脚本说明 ===');
console.log('1. 页面加载完成后会自动输出性能指标');
console.log('2. 可以使用 PerformanceMonitor.start(key) 和 PerformanceMonitor.end(key) 手动计时');
console.log('3. 使用 PerformanceMonitor.logAllData() 输出所有性能数据');
console.log('4. 使用 PerformanceMonitor.exportData() 导出性能数据');
console.log('5. AJAX请求和DOM操作会自动被监控');