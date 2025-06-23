import {useState} from 'react'

export default function Prepare({ sessionId, isPrepareDisabled, onPrepared, config }) {

    const [isPreparing, setPreparing] = useState(false);

    async function handlePrepare(){
        try{
            setPreparing(true)
            const response = await fetch(config.api + '/prepare', { 
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
              disabled={(isPreparing || isPrepareDisabled)?true: false}>{isPreparing?"Indexing...": "Index File"}</button>
          </div>
        </section>
    )
}