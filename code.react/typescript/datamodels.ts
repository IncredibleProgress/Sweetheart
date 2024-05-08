// datamodels.ts given for tests
// intends to evaluate TS capabilities for data validation
// FIXME: could prepare for using TypeSpec in the future

interface BaseField {
    info? : string
    apply? : Array<CallableFunction>
    assert? : Array<CallableFunction> }

interface BooleanField extends BaseField {
    default? : boolean }

interface TextField extends BaseField {
    default? : string
    minlength? : number
    maxlength? : number
    regex? : string }

interface NumberField extends BaseField {
    default? : number
    min? : number
    max? : number }

interface DateField extends BaseField {
    default? : Date
    min? : Date
    max? : Date }



// --- legacy ---

// const saferHeaders = new Headers({
//   // FIXME
//   "X-XSS-Protection": "0",
//   "X-Frame-Options:": "DENY",
//   "Content-Type": "application/json",
//   "X-Content-Type-Options": "nosniff",
//   "Cross-Origin-Resource-Policy": "same-site"
// })

// async function fetchInit():
// Promise<JSON> {
//   const response = await fetch("/init",{
//     headers:{
//       "x-sweetheart-action": "init" }
//     })
//   return response.json()
// }