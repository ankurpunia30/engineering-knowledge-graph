import React, { useState, useEffect } from 'react';
import { Upload, File, CheckCircle, XCircle, AlertCircle, Loader } from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || '';

const FileUpload = ({ onUploadSuccess, onClose }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileType, setFileType] = useState('docker-compose');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [supportedFormats, setSupportedFormats] = useState({});
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    // Fetch supported formats
    fetch(`${API_BASE}/api/supported-formats`)
      .then(res => res.json())
      .then(data => setSupportedFormats(data.formats))
      .catch(err => console.error('Failed to load supported formats:', err));
  }, []);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setUploadResult(null);
    
    // Auto-detect file type based on name
    const filename = file.name.toLowerCase();
    if (filename.includes('docker-compose')) {
      setFileType('docker-compose');
    } else if (filename.includes('k8s') || filename.includes('kubernetes')) {
      setFileType('kubernetes');
    } else if (filename.includes('teams') || filename.includes('team')) {
      setFileType('teams');
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('file_type', fileType);

    try {
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      setUploadResult(result);

      if (result.success) {
        // Call success callback after a brief delay to show success message
        setTimeout(() => {
          onUploadSuccess?.(result);
        }, 1500);
      }
    } catch (error) {
      setUploadResult({
        success: false,
        message: `Upload failed: ${error.message}`,
        errors: [error.message]
      });
    } finally {
      setIsUploading(false);
    }
  };

  const getFileTypeInfo = (type) => supportedFormats[type] || {};

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
      <div className="card-professional max-w-3xl w-full mx-4 max-h-[95vh] overflow-hidden shadow-2xl">
        {/* Header */}
        <div className="px-8 py-6 border-b border-slate-200/50 bg-gradient-to-r from-blue-50/80 to-indigo-50/80 backdrop-blur-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl shadow-lg">
                <Upload className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gradient">Upload Configuration File</h2>
                <p className="text-slate-600">Add new services and infrastructure to your knowledge graph</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-3 text-slate-500 hover:text-slate-700 rounded-xl hover:bg-white/80 hover:shadow-md transition-all duration-200 focus-ring"
            >
              <XCircle size={24} />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-8 space-y-8 max-h-[calc(95vh-120px)] overflow-y-auto">
          {/* File Type Selection */}
          <div>
            <label className="block text-base font-semibold text-slate-800 mb-4">📁 Choose File Type</label>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(supportedFormats).map(([type, info]) => (
                <button
                  key={type}
                  onClick={() => setFileType(type)}
                  className={`group p-5 rounded-2xl border-2 text-left transition-all duration-200 hover-lift ${
                    fileType === type
                      ? 'border-blue-500 bg-blue-50 shadow-professional'
                      : 'border-slate-200 hover:border-slate-300 hover:shadow-professional'
                  }`}
                >
                  <div className="font-medium text-slate-900">{info.name}</div>
                  <div className="text-xs text-slate-600 mt-1">{info.description}</div>
                  <div className="text-xs text-slate-500 mt-2">
                    {info.extensions?.join(', ')}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* File Upload Area */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-3">Select File</label>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-professional ${
                dragOver
                  ? 'border-blue-500 bg-blue-50'
                  : selectedFile
                  ? 'border-green-400 bg-green-50'
                  : 'border-slate-300 hover:border-slate-400'
              }`}
            >
              {selectedFile ? (
                <div className="space-y-3">
                  <div className="flex items-center justify-center">
                    <File className="w-12 h-12 text-green-600" />
                  </div>
                  <div>
                    <p className="font-medium text-slate-900">{selectedFile.name}</p>
                    <p className="text-sm text-slate-600">
                      {(selectedFile.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="text-sm text-slate-500 hover:text-slate-700 underline"
                  >
                    Remove file
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="flex items-center justify-center">
                    <Upload className="w-12 h-12 text-slate-400" />
                  </div>
                  <div>
                    <p className="text-slate-600">
                      Drop your {getFileTypeInfo(fileType).name || fileType} file here, or{' '}
                      <label className="text-blue-600 hover:text-blue-700 cursor-pointer underline">
                        browse files
                        <input
                          type="file"
                          className="hidden"
                          accept={getFileTypeInfo(fileType).extensions?.join(',')}
                          onChange={(e) => e.target.files[0] && handleFileSelect(e.target.files[0])}
                        />
                      </label>
                    </p>
                    <p className="text-sm text-slate-500 mt-2">
                      Supported formats: {getFileTypeInfo(fileType).extensions?.join(', ')}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Upload Result */}
          {uploadResult && (
            <div className={`p-4 rounded-lg border ${
              uploadResult.success 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-start space-x-3">
                {uploadResult.success ? (
                  <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                ) : (
                  <AlertCircle className="w-5 h-5 text-red-600 mt-0.5" />
                )}
                <div className="flex-1">
                  <p className={`font-medium ${
                    uploadResult.success ? 'text-green-800' : 'text-red-800'
                  }`}>
                    {uploadResult.message}
                  </p>
                  {uploadResult.success && (
                    <div className="text-sm text-green-700 mt-2">
                      <p>Added {uploadResult.nodes_added} nodes and {uploadResult.edges_added} edges</p>
                    </div>
                  )}
                  {uploadResult.errors && uploadResult.errors.length > 0 && (
                    <div className="text-sm text-red-700 mt-2">
                      {uploadResult.errors.map((error, idx) => (
                        <p key={idx}>• {error}</p>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-200">
            <button
              onClick={onClose}
              className="px-4 py-2 text-slate-600 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 rounded-lg transition-professional"
              disabled={isUploading}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading || (uploadResult && uploadResult.success)}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-professional shadow-professional hover:shadow-professional-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isUploading ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  <span>Uploading...</span>
                </>
              ) : uploadResult && uploadResult.success ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  <span>Uploaded</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload File</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
