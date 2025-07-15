import {useState, useEffect} from 'react'
import UplodFile from './components/UploadFile.jsx'
import Prepare from './components/Prepare.jsx'
import Query from './components/Query.jsx'
import { RagContext } from './store/RagContext.jsx';
import CreateSession from './components/CreateSession.jsx';
import './App.css'

function App() {

  const [sessionId, setSessionId] = useState(null);
  const [files, addSubmittedFile] = useState([]);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [isPrepared, setPrepared] = useState(false);
  const [config, setConfig] = useState(null);
  
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

  async function updateSession(newSessionId){  
    setSessionId(newSessionId);
    addSubmittedFile([])
    setPrepared(false);
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

  const ctx = {
    config: config,
    sessionId: sessionId
  };

  return (
    <RagContext.Provider value={ctx}>
      <div>
        <h1>RAG OnDemand</h1>
        <CreateSession onSessionUpdate={updateSession} />
        <UplodFile addFile={addFile} />
        <Prepare isPrepareDisabled={(fileUploaded && files.length>0)?false: true} onPrepared={handlePrepared} />
        <Query isSubmitDisabled={isPrepared?false: true} />
      </div>
    </RagContext.Provider>
  )
}

export default App
