
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
