import { useState, useRef, useEffect } from 'react'

export default function UplodFile({ sessionId }) {

    const [uploadFile, setUploadFile] = useState(null);
    const fileInputRef = useRef(null);

    useEffect(() => {
        return () => {
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
                setUploadFile(null)
            }
        };
    }, [sessionId]); // Dependency array: effect runs when sessionId

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
            const response = await fetch('http://localhost/upload', { // Replace with your actual upload endpoint
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                alert('File uploaded successfully!');
                if (fileInputRef.current) {
                    fileInputRef.current.value = '';
                }
                setSelectedFile(null)
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
        <>
            <li>
                <input type="file" onChange={handleFileChange} disabled={isChooseFileDisabled}
                    ref={fileInputRef} />
            </li>
            <li>
                <button onClick={handleUpload} disabled={isUploadDisabled}>Upload</button>
            </li>
        </>
    )

}