import { useImperativeHandle, useRef } from "react";
import {createPortal} from "react-dom"


export default function ResultModal({ref, result_type, result}){

    const dialog = useRef();

    useImperativeHandle(ref, ()=>{
        return {
            open: () => {
                dialog.current.showModal();
            },
            close: () => {
                dialog.current.close();
            },
        }
    });

    return (
        createPortal(<dialog ref={dialog} className="result-modal">
            <h2>{result_type} Result</h2>
            <p>
                {result}
            </p>
            <form method="dialog">
                <button>Close</button>
            </form>                
        </dialog>,
        document.getElementById("modal")    
    )
    )
}