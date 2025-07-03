import {useState, useEffect, useRef} from 'react'
import UplodFile from './components/UploadFile.jsx'
import Prepare from './components/Prepare.jsx'
import Query from './components/Query.jsx'
import ResultModal from './components/ResultModal';
import './App.css'

function App() {

  const [sessionId, setSessionId] = useState(null);
  const [files, addSubmittedFile] = useState([]);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [isPrepared, setPrepared] = useState(false);
  const [sessionStatus, setSessionStatus] = useState(null);
  const [config, setConfig] = useState(null);
  const dialog = useRef();
  
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('/config.json'); // Relative path to public folder
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setConfig(data);
      } catch (e) {
        console.log(`Error loading config: ${e}`)
      } 
    };
    fetchConfig();
  }, []); 

  async function getSessionId(){
    const response = await fetch(config.api + 'create_session');
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
      //alert(`Failed to create new session: ${error}`)
      setSessionStatus(`Failed to create new session: ${error}`);
      dialog.current.open();
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
            <ResultModal ref={dialog} result_type={"Session Request"} result={sessionStatus} />
            <button onClick={handleSession}>{buttonTxt}</button>
            {sessionIdItem}
          </div>
        </section>
        <UplodFile sessionId={sessionId} 
          addFile={addFile} config={config} />
        <Prepare sessionId={sessionId} 
          isPrepareDisabled={(fileUploaded && files.length>0)?false: true} 
          onPrepared={handlePrepared} config={config} />
        <Query sessionId={sessionId} 
          isSubmitDisabled={isPrepared?false: true} 
          config={config} />
      </div>
    </>
  )
}

export default App
