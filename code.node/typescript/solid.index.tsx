import { render } from 'solid-js/web'

function App() {

    switch (window.location.pathname) {
      // url based components rendering
  
      case '/welcome':
        return(<div>welcome!</div>)
  
      default: // Test page
        return(
          <div className="my-28">
  
            <h1 className="text-4xl lg:text-6xl text-pink-500 text-center italic">
              Welcome to Sweetheart </h1>
  
            <p className="text-center"><br/>
              get at {window.location.pathname} </p>
  
          </div>
        ) }}

        render(() => <App />, document.getElementById('app'))