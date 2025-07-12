// // 文件路径: frontend/src/setupProxy.js

// const { createProxyMiddleware } = require('http-proxy-middleware');

// module.exports = function(app) {
//   // 规则1: 代理新的 AI 后端
//   // 所有发往 /api/summarize 的请求，都转发到 3001 端口
//   app.use(
//     '/api/summarize',
//     createProxyMiddleware({
//       target: 'http://localhost:3001',
//       changeOrigin: true,
//     })
//   );

//   // 规则2: 代理所有其他的 API 请求到旧的后端
//   // 所有其他以 /api 开头的请求，都转发到 5001 端口
//   // （请确保您的旧后端API路径也以/api开头，如果不是，请相应修改）
//   app.use(
//     '/api',
//     createProxyMiddleware({
//       target: 'http://localhost:5001', 
//       changeOrigin: true,
//     })
//   );
// };

// 文件路径: frontend/src/setupProxy.js
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // 将所有以 /api 开头的请求，全部转发到 5001 端口的 Python 后端
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:5001', 
      changeOrigin: true,
    })
  );
};