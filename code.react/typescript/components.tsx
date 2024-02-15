
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
  tclass?: string,
  spaces?: string,
  shape?: string }

export const preset: StyleProps = {
  // provided default values
  spaces: "px-3 py-2",
  shape: "border focus:outline-none" }

function set_class(props:StyleProps): string
  { 
    // autoset default tailwind classes
    const spaces = props.spaces || preset.spaces
    const shape = props.shape || `${preset.shape} ${colors.focus}`

    // set tailwindcss className value
    if (props.tclass != undefined ) {
      props.tclass =`${props.tclass} ${spaces} ${shape}`
    } else { props.tclass =`${spaces} ${shape}` }

    return(props.tclass)
  }

interface HeadingProps extends StyleProps,
  HTMLAttributes<HTMLHeadingElement> {}

export const Title: FC<HeadingProps> = (
  { tclass,spaces,shape,...props }) => {
    // set specific presets
    spaces = spaces || "mt-3 mb-9"
    shape = shape || `${preset.shape} ${colors.title}`
    props.className = set_class({tclass,spaces,shape})
    // return <h1 id="title" children ... >
    props.id= props.id || "title"
    return( <h1 {...props} /> ) }


interface TextInputProps extends StyleProps,
InputHTMLAttributes<HTMLInputElement> {}

export const TextInput: FC<TextInputProps> = (
  { tclass,spaces,shape,...props }) => {
    props.type = "text"
    props.className = set_class({tclass,spaces,shape})
    return( <input {...props} />) }


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
