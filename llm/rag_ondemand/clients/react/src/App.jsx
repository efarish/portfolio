import { useState, useRef } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [sessionId, setSessionId] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);

  const fileInputRef = useRef(null);

  function handleSession(){

    if(sessionId){
      console.log(`Old sessionId ${sessionId}, new ${count}.`);
      setSessionId(`Session Id ${count}`);
      setUploadFile(null)
      fileInputRef.current.value = null;
    }else{
      console.log("No session Id found.");
      setSessionId(`Session Id ${count}`);
    }
    setCount((count) => count + 1);
  }

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setUploadFile(selectedFile.name)
    console.log(`file selected ${selectedFile.name}`)
  };

  function handleUpload() {
    console.log(`File to upload: ${uploadFile}`)
    setUploadFile(null)
  };

  let buttonTxt = sessionId?"New Session": "Create Session";
  let sessionIdItem = sessionId?<li>{sessionId}</li>: "";
  let isChooseFileDisabled = sessionId?false: true;
  let isUploadDisabled = uploadFile?false: true

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
            <li>
              <input type="file" onChange={handleFileChange} disabled={isChooseFileDisabled} ref={fileInputRef}  />
            </li>
            <li>
              <button onClick={handleUpload} disabled={isUploadDisabled}>Upload</button>
            </li>            
          </ol>
      </div>
    </>
  )
}

export default App
