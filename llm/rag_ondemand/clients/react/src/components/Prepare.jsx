import {useState, useRef} from 'react'

import ResultModal from './ResultModal';

export default function Prepare({ sessionId, isPrepareDisabled, onPrepared, config }) {

    const [isPreparing, setPreparing] = useState(false);
    const [prepareResult, setPrepareResult] = useState(null);
    const dialog = useRef();

    async function handlePrepare(){
        try{
            setPreparing(true)
            const response = await fetch(config.api + 'prepare', { 
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({"session_id": sessionId, "recreate": "false"}),
            });    
            if (response.ok) {
                //alert('File indexing successful!');
                setPrepareResult('File indexing successful!')
                dialog.current.open();
                onPrepared(true);
            } else {
                //alert('File indexing failed.');
                setPrepareResult('File indexing failed.')
                dialog.current.open();
                onPrepared(false);
            }    
        }catch(error){
            //alert(`Failed to index file: ${error}`)
            setPrepareResult(`Failed to index file: ${error}`)
            dialog.current.open();
        }finally{
            setPreparing(false)
        }
    }

    return (
        <>
        <ResultModal ref={dialog} result_type={"Index File"} result={prepareResult} />
        <section>
          <div>
            <button onClick={handlePrepare}
              disabled={(isPreparing || isPrepareDisabled)?true: false}>{isPreparing?"Indexing...": "Index File"}</button>
          </div>
        </section>
        </>
    )
}