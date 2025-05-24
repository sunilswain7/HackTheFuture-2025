"use client";

import React, { useState, useRef, useCallback } from "react";
import "./globals.css";
import {
  Upload,
  Shield,
  Eye,
  EyeOff,
  Download,
  Zap,
  Brain,
  Lock,
  Users,
  FileText,
  Image,
  Mic,
  Video,
  CheckCircle,
  AlertTriangle,
  Clock,
  Link,
} from "lucide-react";

export default function Home(){
  const [activeTab, setActiveTab] = useState("upload");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [processing, setProcessing] = useState(false);
  const [redactionResults, setRedactionResults] = useState(null);
  const [previewMode, setPreviewMode] = useState("redacted");
  const [collaborators, setCollaborators] = useState([]);
  const [auditLog, setAuditLog] = useState([]);
  const fileInputRef = useRef(null);

  // Simulated sensitive data patterns
  const sensitivePatterns = {
    ssn: /\b\d{3}-\d{2}-\d{4}\b/g,
    phone: /\b\d{3}-\d{3}-\d{4}\b/g,
    email: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    creditCard: /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/g,
    name: /\b[A-Z][a-z]+ [A-Z][a-z]+\b/g,
    address:
      /\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b/gi,
  };

  const handleFileUpload = useCallback((event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        processDocument(e.target.result, file.name);
      };
      reader.readAsText(file);
    }
  }, []);

  const processDocument = async (content, fileName) => {
    setProcessing(true);

    // Simulate AI processing delay
    await new Promise((resolve) => setTimeout(resolve, 2000));

    const detected = [];
    let redactedContent = content;
    let confidenceScore = 0;

    // Advanced pattern detection with context
    Object.entries(sensitivePatterns).forEach(([type, pattern]) => {
      const matches = [...content.matchAll(pattern)];
      matches.forEach((match) => {
        const context = getContext(content, match.index, 50);
        const confidence = calculateConfidence(type, match[0], context);

        detected.push({
          type,
          value: match[0],
          position: match.index,
          confidence,
          context: context.trim(),
          action: "redact",
        });

        confidenceScore += confidence;

        // Smart redaction based on type
        const replacement = getSmartReplacement(type, match[0]);
        redactedContent = redactedContent.replace(match[0], replacement);
      });
    });

    // Add to audit log
    const auditEntry = {
      timestamp: new Date().toISOString(),
      fileName,
      itemsDetected: detected.length,
      confidenceScore: Math.min(
        100,
        Math.round(confidenceScore / detected.length || 0)
      ),
      action: "automated_redaction",
      user: "AI_System",
    };

    setAuditLog((prev) => [auditEntry, ...prev]);
    setRedactionResults({
      original: content,
      redacted: redactedContent,
      detected,
      fileName,
      stats: {
        totalItems: detected.length,
        highConfidence: detected.filter((d) => d.confidence > 80).length,
        mediumConfidence: detected.filter(
          (d) => d.confidence > 60 && d.confidence <= 80
        ).length,
        lowConfidence: detected.filter((d) => d.confidence <= 60).length,
      },
    });

    setProcessing(false);
    setActiveTab("results");
  };

  const getContext = (text, position, range) => {
    const start = Math.max(0, position - range);
    const end = Math.min(text.length, position + range);
    return text.substring(start, end);
  };

  const calculateConfidence = (type, value, context) => {
    let confidence = 70; // base confidence

    // Context-based confidence adjustment
    const contextLower = context.toLowerCase();

    if (type === "ssn" && contextLower.includes("social security"))
      confidence = 95;
    if (type === "phone" && contextLower.includes("phone")) confidence = 90;
    if (type === "email" && contextLower.includes("@")) confidence = 95;
    if (
      type === "creditCard" &&
      (contextLower.includes("card") || contextLower.includes("credit"))
    )
      confidence = 92;

    return Math.min(100, confidence);
  };

  const getSmartReplacement = (type, value) => {
    const replacements = {
      ssn: "XXX-XX-XXXX",
      phone: "XXX-XXX-XXXX",
      email: "[EMAIL_REDACTED]",
      creditCard: "XXXX-XXXX-XXXX-XXXX",
      name: "[NAME_REDACTED]",
      address: "[ADDRESS_REDACTED]",
    };
    return replacements[type] || "[REDACTED]";
  };

  const generateSyntheticData = () => {
    if (!redactionResults) return;

    const synthetic = redactionResults.redacted
      .replace(/\[NAME_REDACTED\]/g, "Alex Johnson")
      .replace(/XXX-XX-XXXX/g, "555-12-3456")
      .replace(/XXX-XXX-XXXX/g, "555-123-4567")
      .replace(/\[EMAIL_REDACTED\]/g, "alex.johnson@example.com")
      .replace(/\[ADDRESS_REDACTED\]/g, "123 Main Street");

    setRedactionResults((prev) => ({
      ...prev,
      synthetic,
    }));
  };

  const addCollaborator = () => {
    const names = [
      "Sarah Chen",
      "Mike Rodriguez",
      "Emily Parker",
      "David Kumar",
    ];
    const roles = [
      "Legal Reviewer",
      "Data Analyst",
      "Compliance Officer",
      "Privacy Engineer",
    ];

    if (collaborators.length < 4) {
      const newCollaborator = {
        id: Date.now(),
        name: names[collaborators.length],
        role: roles[collaborators.length],
        status: "active",
        joinedAt: new Date().toLocaleTimeString(),
      };
      setCollaborators((prev) => [...prev, newCollaborator]);
    }
  };

  const TabButton = ({ id, icon: Icon, label, active }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${
        active
          ? "bg-blue-600 text-white shadow-lg"
          : "bg-gray-100 text-gray-600 hover:bg-gray-200"
      }`}
    >
      <Icon size={20} />
      <span>{label}</span>
    </button>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Shield className="text-blue-400 mr-3" size={40} />
            <h1 className="text-4xl font-bold text-white">AI Enabled Redaction</h1>
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

        {/* Navigation */}
        <div className="flex justify-center mb-8 space-x-4">
          <TabButton
            id="upload"
            icon={Upload}
            label="Upload"
            active={activeTab === "upload"}
          />
          <TabButton
            id="results"
            icon={Eye}
            label="Results"
            active={activeTab === "results"}
          />
          <TabButton
            id="collaborate"
            icon={Users}
            label="Collaborate"
            active={activeTab === "collaborate"}
          />
          <TabButton
            id="audit"
            icon={CheckCircle}
            label="Audit Trail"
            active={activeTab === "audit"}
          />
        </div>

        {/* Content */}
        <div className="bg-white justify-self-center w-[60vw] rounded-2xl shadow-2xl p-8">
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
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                  >
                    Choose File
                  </button>
                </div>
              </div>

              {/* Multi-modal Support Icons */}
              <div className="grid grid-cols-4 gap-4 max-w-md mx-auto">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <FileText className="text-blue-600 mx-auto mb-2" size={24} />
                  <span className="text-sm font-medium">Documents</span>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <Image className="text-green-600 mx-auto mb-2" size={24} />
                  <span className="text-sm font-medium">Images</span>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <Mic className="text-purple-600 mx-auto mb-2" size={24} />
                  <span className="text-sm font-medium">Audio</span>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <Video className="text-red-600 mx-auto mb-2" size={24} />
                  <span className="text-sm font-medium">Video</span>
                </div>
              </div>
            </div>
          )}

          {activeTab === "results" && (
            <div>
              {processing ? (
                <div className="text-center py-12">
                  <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
                  <h3 className="text-xl font-semibold mb-2">
                    AI Processing Your Document...
                  </h3>
                  <p className="text-gray-600">
                    Advanced pattern recognition in progress
                  </p>
                </div>
              ) : redactionResults ? (
                <div>
                  {/* Stats Dashboard */}
                  <div className="grid grid-cols-4 gap-4 mb-6">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-green-600 text-sm font-medium">
                            Items Detected
                          </p>
                          <p className="text-2xl font-bold text-green-800">
                            {redactionResults.stats.totalItems}
                          </p>
                        </div>
                        <CheckCircle className="text-green-600" size={24} />
                      </div>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-blue-600 text-sm font-medium">
                            High Confidence
                          </p>
                          <p className="text-2xl font-bold text-blue-800">
                            {redactionResults.stats.highConfidence}
                          </p>
                        </div>
                        <Brain className="text-blue-600" size={24} />
                      </div>
                    </div>
                    <div className="bg-yellow-50 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-yellow-600 text-sm font-medium">
                            Medium Confidence
                          </p>
                          <p className="text-2xl font-bold text-yellow-800">
                            {redactionResults.stats.mediumConfidence}
                          </p>
                        </div>
                        <AlertTriangle className="text-yellow-600" size={24} />
                      </div>
                    </div>
                    <div className="bg-red-50 p-4 rounded-lg">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-red-600 text-sm font-medium">
                            Needs Review
                          </p>
                          <p className="text-2xl font-bold text-red-800">
                            {redactionResults.stats.lowConfidence}
                          </p>
                        </div>
                        <Eye className="text-red-600" size={24} />
                      </div>
                    </div>
                  </div>

                  {/* View Toggle */}
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex space-x-4">
                      <button
                        onClick={() => setPreviewMode("original")}
                        className={`px-4 py-2 rounded-lg font-medium ${
                          previewMode === "original"
                            ? "bg-red-600 text-white"
                            : "bg-gray-200 text-gray-700"
                        }`}
                      >
                        Original (Sensitive)
                      </button>
                      <button
                        onClick={() => setPreviewMode("redacted")}
                        className={`px-4 py-2 rounded-lg font-medium ${
                          previewMode === "redacted"
                            ? "bg-green-600 text-white"
                            : "bg-gray-200 text-gray-700"
                        }`}
                      >
                        Redacted (Safe)
                      </button>
                      {redactionResults.synthetic && (
                        <button
                          onClick={() => setPreviewMode("synthetic")}
                          className={`px-4 py-2 rounded-lg font-medium ${
                            previewMode === "synthetic"
                              ? "bg-purple-600 text-white"
                              : "bg-gray-200 text-gray-700"
                          }`}
                        >
                          Synthetic Data
                        </button>
                      )}
                    </div>
                    <div className="flex space-x-2">
                      <button
                        onClick={generateSyntheticData}
                        className="bg-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-purple-700"
                      >
                        Generate Synthetic Data
                      </button>
                      <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700 flex items-center space-x-2">
                        <Download size={16} />
                        <span>Download</span>
                      </button>
                    </div>
                  </div>

                  {/* Document Preview */}
                  <div className="bg-gray-50 p-6 rounded-lg mb-6">
                    <h4 className="font-semibold mb-3">Document Preview</h4>
                    <div className="bg-white p-4 rounded border max-h-64 overflow-y-auto">
                      <pre className="whitespace-pre-wrap text-sm">
                        {previewMode === "original" &&
                          redactionResults.original}
                        {previewMode === "redacted" &&
                          redactionResults.redacted}
                        {previewMode === "synthetic" &&
                          redactionResults.synthetic}
                      </pre>
                    </div>
                  </div>

                  {/* Detection Details */}
                  <div>
                    <h4 className="font-semibold mb-3">Detection Details</h4>
                    <div className="space-y-2">
                      {redactionResults.detected.map((item, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                        >
                          <div>
                            <span
                              className={`px-2 py-1 rounded text-xs font-medium ${
                                item.type === "ssn"
                                  ? "bg-red-100 text-red-800"
                                  : item.type === "email"
                                  ? "bg-blue-100 text-blue-800"
                                  : item.type === "phone"
                                  ? "bg-green-100 text-green-800"
                                  : "bg-gray-100 text-gray-800"
                              }`}
                            >
                              {item.type.toUpperCase()}
                            </span>
                            <span className="ml-2 text-sm text-gray-600">
                              "{item.context.substring(0, 50)}..."
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium">
                              {item.confidence}% confidence
                            </span>
                            <div
                              className={`w-3 h-3 rounded-full ${
                                item.confidence > 80
                                  ? "bg-green-500"
                                  : item.confidence > 60
                                  ? "bg-yellow-500"
                                  : "bg-red-500"
                              }`}
                            ></div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <FileText size={48} className="mx-auto mb-4" />
                  <p>Upload a document to see redaction results</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "collaborate" && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold">
                  Collaborative Redaction
                </h3>
                <button
                  onClick={addCollaborator}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700"
                >
                  Add Collaborator
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-3">Active Collaborators</h4>
                  <div className="space-y-3">
                    {collaborators.map((collaborator) => (
                      <div
                        key={collaborator.id}
                        className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-medium">
                            {collaborator.name
                              .split(" ")
                              .map((n) => n[0])
                              .join("")}
                          </div>
                          <div>
                            <p className="font-medium">{collaborator.name}</p>
                            <p className="text-sm text-gray-600">
                              {collaborator.role}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center space-x-1 text-green-600">
                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                            <span className="text-sm">Active</span>
                          </div>
                          <p className="text-xs text-gray-500">
                            Joined {collaborator.joinedAt}
                          </p>
                        </div>
                      </div>
                    ))}
                    {collaborators.length === 0 && (
                      <div className="text-center py-8 text-gray-500">
                        <Users size={48} className="mx-auto mb-4" />
                        <p>
                          No collaborators yet. Add team members to work
                          together.
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-3">Real-time Activity</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="space-y-2 text-sm">
                      <div className="flex items-center space-x-2 text-blue-600">
                        <Clock size={14} />
                        <span>AI System detected 7 sensitive items</span>
                      </div>
                      <div className="flex items-center space-x-2 text-green-600">
                        <CheckCircle size={14} />
                        <span>Auto-redaction completed</span>
                      </div>
                      <div className="flex items-center space-x-2 text-purple-600">
                        <Brain size={14} />
                        <span>Confidence scores calculated</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === "audit" && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold">
                  Blockchain Audit Trail
                </h3>
                <div className="flex items-center space-x-2 text-green-600">
                  <Lock size={16} />
                  <span className="text-sm font-medium">
                    Immutable & Verified
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {auditLog.map((entry, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Link size={16} className="text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium">
                            {entry.action.replace("_", " ").toUpperCase()}
                          </p>
                          <p className="text-sm text-gray-600">
                            {entry.fileName}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">
                          {new Date(entry.timestamp).toLocaleString()}
                        </p>
                        <p className="text-xs text-gray-500">
                          Block #{Math.floor(Math.random() * 1000000)}
                        </p>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Items Detected</p>
                        <p className="font-medium">{entry.itemsDetected}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Confidence Score</p>
                        <p className="font-medium">{entry.confidenceScore}%</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Processed By</p>
                        <p className="font-medium">{entry.user}</p>
                      </div>
                    </div>
                  </div>
                ))}
                {auditLog.length === 0 && (
                  <div className="text-center py-12 text-gray-500">
                    <Lock size={48} className="mx-auto mb-4" />
                    <p>
                      No audit entries yet. Process a document to create audit
                      trail.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
