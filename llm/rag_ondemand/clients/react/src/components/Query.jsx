import { useRef, useEffect } from 'react'

export default function Query({ sessionId, isSubmitDisabled, onSubmit }) {

    const fileInputRef = useRef(null);

    useEffect(() => {
        return () => {
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        };
    }, [sessionId]); 

    return (
        <>
            <li>
                <p>Enter A Query:</p>
            </li>
            <li>
                <input type="text" disabled={isSubmitDisabled} ref={fileInputRef} />
            </li>
            <li>
                <button onClick={onSubmit} disabled={isSubmitDisabled}>Submit</button>
            </li>
        </>
    )

}