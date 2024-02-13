
import React, {FC,InputHTMLAttributes} from 'react'

export let FOCUS_COLOR = "pink-600"

interface TextInputProps
  extends InputHTMLAttributes<HTMLInputElement> {
    twClass?: string,
    spaces?: string,
    shape?: string }

export const TextInput: FC<TextInputProps> = (
  {twClass="",shape,spaces,...props}) => {

    spaces = spaces||"px-3 py-2"
    shape = shape||"border focus:outline-none focus:border-"+FOCUS_COLOR
    twClass += ` ${spaces} ${shape}`

    return(
      <input type="text" className={twClass} {...props} /> )}

export function SelectOption():
  React.JSX.Element {
    return(<>
      <select id=""
        className="w-full border px-3 py-2 focus:outline-none focus:border-pink-600">
        <option></option>
      </select>
      </>) }
