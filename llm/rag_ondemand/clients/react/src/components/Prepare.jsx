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
                alert('Query prepared successful!');
                onPrepared(true);
            } else {
                alert('Query prepare failed.');
                onPrepared(false);
            }    
        }catch(error){
            alert(`Failed to prepare query: ${error}`)
        }finally{
            setPreparing(false)
        }
    }

    return (
        <section>
          <div>
            <button onClick={handlePrepare}
              disabled={(isPreparing || isPrepareDisabled)?true: false}>Prepare Query</button>
          </div>
        </section>
    )
}