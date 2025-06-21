import {useState} from 'react'
import config from './config.json'
import UplodFile from './components/UploadFile.jsx'
import Prepare from './components/Prepare.jsx'
import Query from './components/Query.jsx'
import './App.css'

function App() {

  const [sessionId, setSessionId] = useState(null);
  const [files, addSubmittedFile] = useState([]);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [isPrepared, setPrepared] = useState(false);
  const API = config.api;

  
  async function getSessionId(){
    const response = await fetch(API + '/create_session');
    const new_sessionId = await response.json();
    return new_sessionId.session_id;
  }

  async function handleSession(){
    try{
      const newSessionId = await getSessionId();
      setSessionId(newSessionId);
      addSubmittedFile([])
      setPrepared(false);
    }catch(error){
      alert(`Failed to create new session: ${error}`)
    }
  }

  function addFile(file){
    addSubmittedFile((prevFiles) => {
      const updatedFiles = [
        { file, ...prevFiles,}
      ];
      setFileUploaded(true)
      return updatedFiles;
    });
  }

  async function handlePrepared(prepared) {
    setPrepared(prepared);
    if (prepared){
      setFileUploaded(false)
    }
  }

  const buttonTxt = sessionId?"New Session": "Create Session";
  const sessionIdItem = sessionId?<p>{sessionId}</p>: "";

  return (
    <>
      <div>
        <h1>RAG OnDemand</h1>
        <section>
          <div>
            <button onClick={handleSession}>{buttonTxt}</button>
            {sessionIdItem}
          </div>
        </section>
        <UplodFile sessionId={sessionId} 
          addFile={addFile} />
        <Prepare sessionId={sessionId} 
          isPrepareDisabled={(fileUploaded && files.length>0)?false: true} onPrepared={handlePrepared} />
        <Query sessionId={sessionId} 
          isSubmitDisabled={isPrepared?false: true} />
      </div>
    </>
  )
}

export default App
