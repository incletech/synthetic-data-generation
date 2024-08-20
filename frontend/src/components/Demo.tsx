import React, { useEffect, useState } from "react";
import { useUser } from "@clerk/clerk-react";
import { useGetModelCardsQuery, useUploadFileMutation } from '../services/modelService';

const Demo = () => {
  const { user } = useUser();
  const [modelsByProvider, setModelsByProvider] = useState({});
  const [selectedModel, setSelectedModel] = useState("");
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedOutputFormat, setSelectedOutputFormat] = useState(""); 
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [fileHistory, setFileHistory] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState("");
  const [fileUrl, setFileUrl] = useState(null);

  const { data: modelData, error, isLoading } = useGetModelCardsQuery();
  const [uploadFile] = useUploadFileMutation();

  const apiToken = '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';

  useEffect(() => {
    const storedHistory = JSON.parse(localStorage.getItem('fileHistory'));
    if (storedHistory) {
      setFileHistory(storedHistory);
    }
  }, []);

  useEffect(() => {
    if (modelData) {
      const categorizedModels = modelData.reduce((acc, source) => {
        const provider = Object.keys(source)[0];
        acc[provider] = source[provider];
        return acc;
      }, {});

      setModelsByProvider(categorizedModels);
    }
  }, [modelData]);

  const handleFileUpload = (event) => {
    setUploadedFile(event.target.files[0]);
  };

  const handleFileSubmit = async () => {
    if (!uploadedFile || !selectedModel || !selectedProvider || !selectedOutputFormat) {
      setUploadStatus("Please select a model, output format, upload a file, and ensure provider is selected.");
      return;
    }

    setLoading(true);

    try {
      const uploadResponse = await uploadFile({
        file: uploadedFile,
        userId: user.id,
        model: selectedModel,
        modelProvider: selectedProvider,
        outputFormat: selectedOutputFormat,
      }).unwrap();

      setUploadStatus("File uploaded successfully!");

      const documentResponse = await fetch('https://incletech-incle-sdg.hf.space/get_documents/', {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${apiToken}`,
        },
        body: new URLSearchParams({
          document_id: uploadResponse.document_id,
          output_format: selectedOutputFormat,
        }),
      });

      const blob = await documentResponse.blob();
      const fileUrl = URL.createObjectURL(blob);

      const newFile = {
        document_id: uploadResponse.document_id,
        output_format: selectedOutputFormat,
        preview: await blob.text(),
        fileUrl: fileUrl,
      };
      const updatedHistory = [newFile, ...fileHistory];
      setFileHistory(updatedHistory);
      
      localStorage.setItem('fileHistory', JSON.stringify(updatedHistory));

      const preview = newFile.preview.split('\n').slice(0, 5).join('\n');
      setFilePreview(preview);
      setFileUrl(fileUrl);
      setSelectedFile(newFile);

    } catch (error) {
      console.error('Error during file upload or document retrieval:', error);
      setUploadStatus("Failed to upload file or retrieve document.");
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelection = (event) => {
    const fileId = event.target.value;
    const file = fileHistory.find((f) => f.document_id === fileId);
    if (file) {
      setSelectedFile(file);
      const preview = file.preview.split('\n').slice(0, 5).join('\n');
      setFilePreview(preview);
      setFileUrl(file.fileUrl);
    }
  };

  const handleDownloadSample = async () => {
    try {
      const response = await fetch('https://incletech-incle-sdg.hf.space/get_demo_csv/', {
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${apiToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch sample data');
      }

      const blob = await response.blob();
      const fileUrl = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = fileUrl;
      link.download = 'sample_data.csv';
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error downloading sample data:', error);
      setUploadStatus('Failed to download sample data.');
    }
  };

  if (isLoading) return <p>Loading models...</p>;
  if (error) return <p>Failed to load models: {error.message}</p>;

  return (
    <section className='mt-16 w-full max-w-xl'>
      <div className='flex justify-center gap-4 mb-8'>
        <div className='flex flex-col'>
          <label htmlFor='model-select' className='mb-2 font-medium'>
            Model
          </label>
          <select
            id='model-select'
            value={selectedModel}
            onChange={(e) => {
              const selectedOption = e.target.options[e.target.selectedIndex];
              setSelectedModel(e.target.value);
              setSelectedProvider(selectedOption.getAttribute('data-provider'));
            }}
            className='p-2 border rounded-md'
          >
            <option value=''>Select Model</option>
            {Object.entries(modelsByProvider).map(([provider, models]) => (
              <optgroup key={provider} label={provider.toUpperCase()}>
                {models.map((model, index) => (
                  <option key={index} value={model.model_id} data-provider={provider}>
                    {model.name}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div className='flex flex-col'>
          <label htmlFor='output-format-select' className='mb-2 font-medium'>
            Output Format
          </label>
          <select
            id='output-format-select'
            value={selectedOutputFormat}
            onChange={(e) => setSelectedOutputFormat(e.target.value)}
            className='p-2 border rounded-md'
          >
            <option value=''>Select Output Format</option>
            <option value='excel'>Excel</option>
            <option value='csv'>CSV</option>
          </select>
        </div>

        <div className='flex flex-col'>
          <br></br>
          <button
            type='button'
            onClick={handleDownloadSample}
            className='p-2 border rounded-md bg-green-500 text-white'
            id='sample-data'
          >
            Download
          </button>
        </div>
      </div>

      <div className='flex items-center gap-2 mb-4'>
        <input
          type='file'
          id='file-upload'
          onChange={handleFileUpload}
          className='p-2 border rounded-md w-full'
        />
        <button
          type='button'
          onClick={handleFileSubmit}
          className='px-4 py-2 bg-blue-500 text-white rounded-md'
          disabled={loading}
        >
          {loading ? (
            <svg
              className="animate-spin h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              ></circle>
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8v8H4z"
              ></path>
            </svg>
          ) : (
            "Upload"
          )}
        </button>
      </div>

      <div className='flex flex-col mb-4'>
        <label htmlFor='file-history-select' className='mb-2 font-medium'>
          Previously Generated Files
        </label>
        <select
          id='file-history-select'
          onChange={handleFileSelection}
          className='p-2 border rounded-md'
        >
          <option value=''>Select a file</option>
          {fileHistory.map((file) => (
            <option key={file.document_id} value={file.document_id}>
              {file.document_id} ({file.output_format})
            </option>
          ))}
        </select>
      </div>

      {filePreview && (
        <div className='relative bg-gray-100 p-4 rounded-md shadow-md'>
          <a
            href={fileUrl}
            download={`downloaded_file.${selectedOutputFormat}`}
            className='absolute top-2 right-2 inline-flex items-center justify-center bg-green-500 text-white rounded-full h-10 w-10'
          >
            <svg
              className="h-5 w-5"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          </a>
          <h3 className='font-medium text-lg'>File Preview</h3>
          <pre className='bg-gray-50 p-2 rounded-md'>
            {filePreview}
          </pre>
        </div>
      )}
    </section>
  );
};

export default Demo;
