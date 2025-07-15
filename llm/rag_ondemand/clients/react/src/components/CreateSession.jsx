import {useState, useRef, useContext} from 'react'
import { RagContext } from '../store/RagContext';
import ResultModal from './ResultModal';

export default function CreateSession({onSessionUpdate }){

  const { sessionId, config } = useContext(RagContext);
  const [sessionStatus, setSessionStatus] = useState(null);
  const dialog = useRef();

  const buttonTxt = sessionId?"New Session": "Create Session";
  const sessionIdItem = sessionId?<p>{sessionId}</p>: "";

  async function getSessionId(){
    const response = await fetch(config.api + 'create_session');
    const new_sessionId = await response.json();
    return new_sessionId.session_id;
  }  
  
  async function handleSession(){
    try{
      const newSessionId = await getSessionId();
      onSessionUpdate(newSessionId)
    }catch(error){
      setSessionStatus(`Failed to create new session: ${error}`);
      dialog.current.open();
    }
  }

  return (
    <section>
      <ResultModal ref={dialog} result_type={"Session Request"} result={sessionStatus} />
      <div>
        <button onClick={handleSession}>{buttonTxt}</button>
        {sessionIdItem}
      </div>
    </section>
  )

}