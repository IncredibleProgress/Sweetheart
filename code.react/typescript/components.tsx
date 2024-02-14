
import React, {FC,
  InputHTMLAttributes,
  SelectHTMLAttributes,
  HTMLAttributes } from 'react'

export const colors = {
  // provided default colors
  title: "text-pink-500",
  focus: "focus:border-pink-600" }


interface StyleProps {
  // allow specific attributes in HTML elements
  tClass?: string,
  spaces?: string,
  shape?: string }

export const preset: StyleProps = {
  // provided default values
  tClass: "",
  spaces: "px-3 py-2",
  shape: "border focus:outline-none" }

function set_tClass(props:StyleProps) {
  props.tClass = `${props.tClass+" "||""}${props.spaces} ${props.shape}` }

function set_style(props:StyleProps): StyleProps
  { // set tailwindcss className as tClass
    props.spaces= props.spaces || preset.spaces
    props.shape= props.shape || preset.shape + colors.focus
    set_tClass(props)
    return(props) }


interface HeadingProps extends StyleProps,
  HTMLAttributes<HTMLHeadingElement> {}

export const Title: FC<HeadingProps> = (
  {...props}) => {
    props.id= props.id || "title"
    props.spaces= props.spaces || "mt-3 mb-9"
    props.shape= props.shape || preset.shape + colors.title
    set_tClass(props)
    return( <h1 {...props} /> )}


export const TextInput: InputHTMLAttributes<HTMLInputElement> = (
  {...props}) => { set_style(props)
    return(
      <input type="text" className={props.tClass} {...props} />
    )}


// interface SelectProps
//   extends SelectHTMLAttributes<HTMLSelectElement> {
//     tClass?: string,
//     spaces?: string,
//     shape?: string }

// export const Select: FC<SelectProps> = (
//   {tClass="",shape,spaces,...props}) => {

//     spaces = spaces||"px-3 py-2"
//     shape = shape||"border focus:outline-none focus:border-"+colors.focus
//     tClass += ` ${spaces} ${shape}`

//     return(
//       <select className={tClass} {...props} >
//         <option></option>
//       </select> )}
