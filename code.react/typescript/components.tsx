
import ReactDOM from 'react-dom/client'

import React, {FC,
  InputHTMLAttributes,
  SelectHTMLAttributes,
  TextareaHTMLAttributes,
  HTMLAttributes } from 'react'

  interface StyleProps {
    // allow specific attributes in HTML elements
    spaces?: string,
    shape?: string }


// default style settings
export const colors = {
  // provided default colors
  title: "text-pink-400",
  focus: "focus:border-pink-600" }

export const preset: StyleProps = {
  // provided default values
  spaces: "px-3 py-2 ml-1",
  shape: "border rounded-sm focus:outline-none" }


export function render(elementJSX:React.JSX.Element) {
  // // set title from the first <h1> element
  // const heading = document.getElementsByTagName("h1")[0]
  // if (heading != null) document.title = heading.innerText
  // render the React app
  const app: HTMLElement | null = document.getElementById('ReactApp')
  ReactDOM.createRoot(app!).render(elementJSX) }


function genClassName(
  className: string | undefined,
  spaces: string | undefined,
  shape: string | undefined ): string {

    // autoset default tailwind classes
    spaces = spaces ?? preset.spaces
    shape = shape ?? `${preset.shape} ${colors.focus}`
    // set tailwindcss className value
    return(`${className||""} ${spaces} ${shape}`.trim()) }


// provide a styled <MiniApp /> component
export const MiniApp: FC<HTMLAttributes<HTMLDivElement>> = (
  {...props}) => {
    const shape = "mt-16 max-w-lg m-auto space-y-3"
    props.className = `${props.className||""} ${shape}`.trim()
    return( <div {...props} /> ) }


// provide a styled <Title /> component
interface HeadingProps extends StyleProps,
  HTMLAttributes<HTMLHeadingElement> {}

export const Title: FC<HeadingProps> = (
  { spaces,shape,...props }) => {
    // set specific presets
    spaces = spaces ?? "mt-3 mb-9"
    shape = shape ?? `${colors.title}`
    props.className = `${props.className||""} ${spaces} ${shape}`.trim()
    // return <h1 id="title" children ... >
    props.id= props.id ?? "title"
    return( <h1 {...props} /> ) }


// provide a styled <TextInput /> component
interface TextInputProps extends StyleProps,
  InputHTMLAttributes<HTMLInputElement> {}

export const TextInput: FC<TextInputProps> = (
  { spaces,shape,...props }) => {
    props.type = "text"
    props.className = genClassName(props.className,spaces,shape)
    return( <input {...props} /> )}


// provide a styled <SelectInput /> component
interface SelectOptionProps extends StyleProps,
  SelectHTMLAttributes<HTMLSelectElement> {
    options: Array<string> }

export const SelectOption: FC<SelectOptionProps> = (
  {shape,spaces,options,...props}) => {
    props.className = genClassName(props.className,spaces,shape)
    return(
      <select {...props}>
        { options.map((option) => ( <option children={option}/> )) }
      </select> )}


// provide a styled <TextArea /> component
interface TextAreaProps extends StyleProps,
TextareaHTMLAttributes<HTMLTextAreaElement> {}

export const TextArea: FC<TextAreaProps> = (
  { spaces, shape, ...props }) => {
    props.className = genClassName(props.className,spaces,shape);
    return ( <textarea {...props} /> )}


// export default {
//   // const
//   colors, preset,
//   // components
//   Title,
//   TextInput,
//   TextArea,
//   SelectOption,
// }