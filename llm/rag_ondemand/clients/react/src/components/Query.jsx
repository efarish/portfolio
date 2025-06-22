import { useRef, useEffect, useState } from 'react'

export default function Query({ sessionId, isSubmitDisabled, config}) {

    const [isQuerying, setQuerying] = useState(false);
    const [queryResult, setQueryResult] = useState("");
    const inputRef = useRef(null);

    useEffect(() => {
        return () => {
            if (inputRef.current) {
                inputRef.current.value = '';
            }
        };
    }, [sessionId]);
    
    async function handleSubmit(){

        const inputQuery = inputRef.current.value;

        if (inputQuery.trim() === ''){
            return;
        }

        try{
            setQuerying(true)
            const response = await fetch(config.api + '/query', { 
                method: 'POST',
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({"session_id": sessionId, "query": inputQuery}),
            });    
            if (!response.ok) {
                alert('Query failed.');
            }else{
                const queryJSON = await response.json()
                setQueryResult(queryJSON.body)
            }    
        }catch(error){
            alert(`Failed to submit query: ${error}`)
        }finally{
            setQuerying(false)
        }

    }

    return (
        <section id="user-input">
            <div className="input-group">
                <p>
                <label>Enter A Query:</label>
                <input type="text" disabled={isSubmitDisabled} ref={inputRef} />
                <button onClick={handleSubmit} disabled={(isQuerying || isSubmitDisabled)}>Submit Query</button>
                </p>
            </div>
            <div>
                <p>
                <label>Query Results:</label>
                <textarea id="queryResult" 
                    name="queryResult" 
                    rows="10" cols="50" 
                    readOnly
                    value={queryResult}/>
                </p>
            </div>
        </section>
    )

}