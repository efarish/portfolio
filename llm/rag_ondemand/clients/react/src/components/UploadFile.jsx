import { useState, useRef, useEffect } from 'react'

export default function UplodFile({ sessionId, addFile, config }) {

    const [uploadFile, setUploadFile] = useState(null);
    const fileInputRef = useRef(null);

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
            const response = await fetch(config.api + '/upload', { // Replace with your actual upload endpoint
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('File uploaded successfully!');
                if (fileInputRef.current) {
                    addFile(fileInputRef.current.value)
                    fileInputRef.current.value = '';
                }
                setUploadFile(null)
            } else {
                alert('File upload failed!');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
            alert('An error occurred during upload.');
        }
    };

    let isChooseFileDisabled = sessionId ? false : true;
    let isUploadDisabled = (uploadFile && !isChooseFileDisabled) ? false : true

    return (
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
    )

}