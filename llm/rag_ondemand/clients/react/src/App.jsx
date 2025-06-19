import {useState} from 'react'
import UplodFile from './components/UploadFile.jsx'
import './App.css'

function App() {
  const [sessionId, setSessionId] = useState(null);
  
  async function getSessionId(){
    const response = await fetch('http://localhost/create_session');
    const new_sessionId = await response.json();
    return new_sessionId.session_id;
  }

  async function handleSession(){
    const newSessionId = await getSessionId();
    setSessionId(newSessionId);
  }

  const buttonTxt = sessionId?"New Session": "Create Session";
  const sessionIdItem = sessionId?<li><p>{sessionId}</p></li>: "";

  return (
    <>
      <div>
        <h1>RAG OnDemand</h1>
          <ol >
            <li>
              <button onClick={handleSession}>
                {buttonTxt}
              </button>
            </li>
            {sessionIdItem}
            <UplodFile sessionId={sessionId} />
          </ol>
      </div>
    </>
  )
}

export default App
