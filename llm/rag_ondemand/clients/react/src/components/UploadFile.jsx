import { useState, useRef, useEffect } from 'react'
import { useContext } from 'react';
import { RagContext } from '../store/RagContext';
import ResultModal from './ResultModal';

export default function UplodFile({ addFile }) {

    const { sessionId, config } = useContext(RagContext);
    const [uploadFile, setUploadFile] = useState(null);
    const [uploadResult, setUploadResult] = useState(null);
    const fileInputRef = useRef(null);
    const dialog = useRef();

    useEffect(() => {
        return () => {
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
                setUploadFile(null)
            }
        };
    }, [sessionId]); 

    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        setUploadFile(selectedFile)
        console.log(`file selected ${selectedFile.name}`)
    };

    const handleUpload = async () => {
        if (!uploadFile) {
            alert('Please select a file first!');
            return;
        }

        const formData = new FormData();
        formData.append('session_id', sessionId )
        formData.append('file', uploadFile);    

        try {
            const response = await fetch(config.api + 'upload', { // Replace with your actual upload endpoint
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                setUploadResult('File uploaded successfully!');
                dialog.current.open()
                if (fileInputRef.current) {
                    addFile(fileInputRef.current.value);
                    fileInputRef.current.value = '';
                }
                setUploadFile(null)
            } else {
                setUploadResult('File upload failed!');
                dialog.current.open();
            }
        } catch (error) {
            setUploadResult(`Error uploading file: ${error}`)
            dialog.current.open()
        }
    };

    let isChooseFileDisabled = sessionId ? false : true;
    let isUploadDisabled = (uploadFile && !isChooseFileDisabled) ? false : true

    return (
            <>
            <ResultModal ref={dialog} result_type={"File Upload"} result={uploadResult} />
            <section id="user-input">
                <div className="input-group">
                    <p>
                        <input type="file" onChange={handleFileChange} disabled={isChooseFileDisabled}
                            ref={fileInputRef} />
                    </p>
                    <p>
                        <button onClick={handleUpload} disabled={isUploadDisabled}>Upload</button>
                    </p>
                </div>
            </section>
            </>
    )

}