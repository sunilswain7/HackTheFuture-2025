"use client";

import { Shield, Brain, Zap, Lock, Users, Upload } from "lucide-react";
import { useRef, useState } from "react";

function TabButton({ id, icon: Icon, label, active, onClick }) {
  return (
    <button
      onClick={() => onClick(id)}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium ${
        active ? "bg-blue-600 text-white" : "bg-gray-200 text-gray-700"
      }`}
    >
      <Icon size={16} />
      <span>{label}</span>
    </button>
  );
}

export default function RedactionDashboard() {
  const fileInputRef = useRef(null);
  const [activeTab, setActiveTab] = useState("upload");
  const [processing, setProcessing] = useState(false);

  const uploadFileAndDownload = async (file) => {
    setProcessing(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8000/api/redact", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const blob = await response.blob();

      // Create temporary link to trigger file download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "redacted_output.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Upload error:", error);
      alert("Failed to process file. Please try again.");
    } finally {
      setProcessing(false);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      uploadFileAndDownload(file);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="text-blue-400 mr-3" size={40} />
            <h1 className="text-4xl font-bold text-white">
              AI Enabled Redaction
            </h1>
          </div>
          <p className="text-xl text-gray-300">
            The Ultimate Privacy Preservation Platform
          </p>
          <div className="flex items-center justify-center mt-4 space-x-6 text-sm text-gray-400">
            <div className="flex items-center space-x-1">
              <Brain size={16} />
              <span>AI-Powered</span>
            </div>
            <div className="flex items-center space-x-1">
              <Zap size={16} />
              <span>Real-time</span>
            </div>
            <div className="flex items-center space-x-1">
              <Lock size={16} />
              <span>Blockchain Secured</span>
            </div>
            <div className="flex items-center space-x-1">
              <Users size={16} />
              <span>Collaborative</span>
            </div>
          </div>
        </div>

        <div className="flex justify-center mb-8 space-x-4">
          {["upload", "collaborate"].map((tab) => (
            <TabButton
              key={tab}
              id={tab}
              icon={
                {
                  upload: Upload,
                  collaborate: Users,
                }[tab]
              }
              label={tab.charAt(0).toUpperCase() + tab.slice(1)}
              active={activeTab === tab}
              onClick={setActiveTab}
            />
          ))}
        </div>

        <div className="bg-white justify-self-center w-[60vw] rounded-2xl shadow-2xl p-8 min-h-[300px]">
          {activeTab === "upload" && (
            <div className="text-center">
              <div className="border-4 border-dashed border-gray-300 rounded-xl p-12 mb-6">
                <div className="flex flex-col items-center space-y-4">
                  <div className="bg-blue-100 p-6 rounded-full">
                    <Upload className="text-blue-600" size={48} />
                  </div>
                  <h3 className="text-2xl font-semibold text-gray-800">
                    Upload Your Document
                  </h3>
                  <p className="text-gray-600 max-w-md">
                    Support for multiple formats: PDF, Word, Images, Audio,
                    Video files
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileUpload}
                    className="hidden"
                    accept=".txt,.pdf,.docx,.jpg,.png,.mp3,.mp4"
                    disabled={processing}
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className={`px-8 py-3 rounded-lg font-medium transition-colors ${
                      processing
                        ? "bg-gray-400 cursor-not-allowed"
                        : "bg-blue-600 hover:bg-blue-700 text-white"
                    }`}
                    disabled={processing}
                  >
                    {processing ? "Processing..." : "Choose File"}
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "collaborate" && (
            <div className="text-center text-gray-700">
              <p>Collaborate functionality coming soon.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
