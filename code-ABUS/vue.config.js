const path = require('path');
  
  module.exports = {
    publicPath:'/',
    devServer: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8091', //后端
          changeOrigin: true, //允许跨域
          pathRewrite: {
            '^/api': '' 
          },
        },
        '/finished_qty': {
          target: 'http://127.0.0.1:8091', //后端
          changeOrigin: true, //允许跨域
        }
      },
      port:8092,
      allowedHosts:[
        'john.abushardware.com',
        '192.168.41.52'         
      ],
      historyApiFallback: true,
    },
    lintOnSave: process.env.NODE_ENV !== 'production',
    chainWebpack:config=>{
      config
        .plugin('html')
        .tap(args=>{
          args[0].title='万晖五金数据平台'
          return args
        })
    },
    configureWebpack: {
      resolve: {
        alias: {
          '@': path.resolve(__dirname, 'src') 
        }
      }
    }
  }
