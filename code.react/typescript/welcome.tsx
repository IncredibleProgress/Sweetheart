// Welcome page of Sweetheart

import React from 'react'
import '../resources/tailwind.css'
import { SvgGamepad, SvgIphone, SvgLifeBuoy, SvgRocket, SvgWrench, render } from './components'

render(
  <div className="container max-w-screen-lg mx-auto">

    <div className="mt-32 mb-28">
      <h1 className="text-8xl text-pink-500 text-center italic">
        Sweetheart
      </h1>
      <p className="text-3xl text-center text-pink-600 italic mt-4">
        innovative foundations for enterprise-grade solutions
      </p>
    </div>

    <div className="flex border rounded-lg shadow-xl p-6 mb-20
    transition-all hover:scale-110 hover:border-pink-200 hover:border-2 p-6 mb-20">
      <SvgIphone className="size-1/4 p-4" />
      <p className="size-3/4 text-center p-4">
        <span className="text-3xl">
          Just build Apps you need, in the brightest way.
        </span><br/><br/><span className="text-2xl">
          Start from scratch, and create with ease and efficiency the apps you really need embedding reliable open-source code.
        </span>
      </p>
    </div>

    <div className="flex border rounded-lg shadow-xl p-6 mb-20
    transition-all hover:scale-110 hover:border-pink-200 hover:border-2">
      <p className="size-3/4 text-center p-4">
        <span className="text-3xl">
          Be master of your data models and capabilities.
        </span><br/><br/><span className="text-2xl">
          The Python language becomes with Sweetheart an ideal toolkit for data processing,
          the calculations and AI in the industry.
        </span>
      </p>
      <SvgRocket className="size-1/4 p-4" />
    </div>

    <div className="flex border rounded-lg shadow-xl p-6 mb-20
    transition-all hover:scale-110 hover:border-pink-200 hover:border-2">
      <SvgGamepad className="size-1/4 p-4" />
      <p className="size-3/4 text-center p-4">
        <span className="text-3xl">
          Enjoy fast approaches that fits for newbies.
        </span><br/><br/><span className="text-2xl">
          No experience needed to use good things in the right way.
          Be quiete, under the hood, security and performances are ensured.
        </span>
      </p>
    </div>

    <div className="flex border rounded-lg shadow-xl p-6 mb-20
    transition-all hover:scale-110 hover:border-pink-200 hover:border-2">
      <p className="size-3/4 text-center p-4">
        <span className="text-3xl">
          Use provided high quality patterns and resources.
        </span><br/><br/><span className="text-2xl">
          Go one step further, learn to write great React and Python code
          with efficiency including up-to-date best practices.
        </span>
      </p>
      <SvgLifeBuoy className="size-1/4 p-4" />
    </div>

    <div className="flex border rounded-lg shadow-xl p-6 mb-20
    transition-all hover:scale-110 hover:border-pink-200 hover:border-2">
      <SvgWrench className="size-1/4 p-4" />
      <p className="size-3/4 text-center p-4">
        <span className="text-3xl">
          Rely on hardened and maintainable foundations.
        </span><br/><br/><span className="text-2xl">
          Sweetheart is full stack featured and reduces drastically
          the volume of code and committed libraries in your projects.
        </span>
      </p>
    </div>

  </div> )