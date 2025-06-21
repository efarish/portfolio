import {useState} from 'react'
import config from '../config.json'

export default function Prepare({ sessionId, isPrepareDisabled, onPrepared }) {

    const [isPreparing, setPreparing] = useState(false);
    const API = config.api;

    async function handlePrepare(){
        try{
            setPreparing(true)
            const response = await fetch(API + '/prepare', { 
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({"session_id": sessionId, "recreate": "false"}),
            });    
            if (response.ok) {
                alert('File indexing successful!');
                onPrepared(true);
            } else {
                alert('File indexing failed.');
                onPrepared(false);
            }    
        }catch(error){
            alert(`Failed to index file: ${error}`)
        }finally{
            setPreparing(false)
        }
    }

    return (
        <section>
          <div>
            <button onClick={handlePrepare}
              disabled={(isPreparing || isPrepareDisabled)?true: false}>Index File</button>
          </div>
        </section>
    )
}