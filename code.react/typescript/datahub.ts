// for testing

// const saferHeaders = new Headers({
//   // FIXME
//   "X-XSS-Protection": "0",
//   "X-Frame-Options:": "DENY",
//   "Content-Type": "application/json",
//   "X-Content-Type-Options": "nosniff",
//   "Cross-Origin-Resource-Policy": "same-site"
// })

async function fetchInit():
Promise<JSON> {
  const response = await fetch("/init",{
    headers:{
      "x-sweetheart-action": "init" }
    })
  return response.json()
}
