const http = require('http')
var fs = require('fs')
var server = http.createServer()

const hostname = process.env.HOST_NAME
const port = process.env.PORT

// const server = http.createServer((req, res) => {
//   console.log(req.url)

//   if (0 <= req.url.indexOf("404_responce")) {
//     res.writeHead(404)
//     res.end()
//   } else {
//     fs.readFile("test.html", (err, data) => {
//         if (!err) {
//           res.writeHead(200, {"Content-Type": "text/html"})
//           res.end(data)
//         }
//     })
//   }
// })

server.on('request', function(req, res) {
  console.log(req.url)
  res.writeHead(200, {'Content-Type' : 'text/html'})

  switch (req.url) {
      case '/1':
          fs.readFile("1.html", (err, data) => {
              if (!err) {
                  res.write(data)
                  res.end()
              }
          })
          break
      case '/2':
          fs.readFile("2.html", (err, data) => {
              if (!err) {
                  res.write(data)
                  res.end()
              }
          })
          break
      default:
          break
  }
})

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`)
})
