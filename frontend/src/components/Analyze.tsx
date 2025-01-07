import React, { useState } from "react";
import { Upload, FileText, AlertCircle } from "lucide-react";

const FileAnalyzer = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState<any[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");
  const [eips, setEips] = useState<string[]>([]);
  const [results, setResults] = useState<any | null>(null);
  const [resultsData, setResultsData] = useState<any>(
    localStorage.getItem("formattedData") || ""
  );

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFiles = [...e.dataTransfer.files];
    setFiles(droppedFiles);
  };

  const analyzeFetch = async (filesToAnalyze: any, selectedEips?: any) => {
    try {
      setAnalyzing(true);
      setError("");
      console.log(filesToAnalyze);
      const formData = new FormData();
      formData.append("zipFile", filesToAnalyze[0]); // Assuming `filesToAnalyze` is the file input or file object
      formData.append("eips", JSON.stringify(selectedEips)); // Assuming `filesToAnalyze` is the file input or file object
      //   formData.append("eips", JSON.stringify(selectedEips));

      const res = await fetch("http://127.0.0.1:5000/analyze", {
        method: "POST",
        body: formData,
        // headers: { "Content-Type": "multipart/form-data" }, // Send the FormData with the file
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error);
      }

      // Assuming the server responds with JSON
      setResults(data);
      console.log(data);
      const formatted = Object.entries(data.data)
        .map(([key, value]) => {
          return `
          <h2 style="font-size: 1.5em; font-weight: bold;">${key}</h2>
          <ul>
            <li><strong>Compliance:</strong></li>
            <ul>
              <li><strong>ERC721:</strong> ${
                (value as any).compliance.ERC721
              }</li>
            </ul>
            <li><strong>oz_modules:</strong></li>
            <ul>
              ${(value as any).oz_modules
                .map((module: any) => `<li>${module}</li>`)
                .join("")}
            </ul>
          </ul>
          `;
        })
        .join("\n");
      localStorage.setItem("formattedData", formatted);
      setResultsData(formatted);
    } catch (err: any) {
      console.log(err);
      setError(err.message);
    } finally {
      setAnalyzing(false);
    }
  };
  console.log(error);
  const handleFileSelect = (e: any) => {
    const selectedFiles = [...e.target.files];
    setFiles(selectedFiles);
  };

  const handleEipChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value, checked } = e.target;
    setEips((prevEips) =>
      checked ? [...prevEips, value] : prevEips.filter((eip) => eip !== value)
    );
  };

  const handleAnalyze = () => {
    // setAnalyzing(true);
    // Simulate analysis
    analyzeFetch(files, eips);
    // setTimeout(() => setAnalyzing(false), 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-teal-950 to-gray-900 text-cyan-300">
      {/* Rain effect */}
      <div className="fixed inset-0 pointer-events-none">
        {[...Array(50)].map((_, i) => (
          <div
            key={i}
            className="absolute w-px h-20 bg-cyan-500/20"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `rain ${1 + Math.random() * 2}s linear infinite`,
            }}
          />
        ))}
      </div>

      <div className="container mx-auto px-4 py-12 relative">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-mono tracking-widest mb-4 text-cyan-400">
            PAPERS PLEASE
          </h1>
          <p className="text-lg text-cyan-300/80">
            Upload your files for analysis
          </p>
        </div>

        {/* Upload Area */}
        <div
          className={`max-w-2xl mx-auto mb-8 border-2 border-dashed rounded-lg p-12 text-center transition-all
            ${
              isDragging
                ? "border-cyan-400 bg-cyan-950/50"
                : "border-cyan-700 hover:border-cyan-500"
            }
            ${files.length > 0 ? "bg-cyan-950/30" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            type="file"
            multiple
            className="hidden"
            id="file-upload"
            onChange={handleFileSelect}
          />

          <label htmlFor="file-upload" className="cursor-pointer">
            <Upload className="w-16 h-16 mx-auto mb-4 text-cyan-400" />
            <p className="text-lg mb-2">Drag and drop files here</p>
            <p className="text-sm text-cyan-400/60">or click to select files</p>
          </label>
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-cyan-950/30 rounded-lg p-6 backdrop-blur-sm">
              <h2 className="text-xl mb-4 font-mono">Selected Files:</h2>
              {files.map((file, index) => (
                <div key={index} className="flex items-center mb-3 last:mb-0">
                  <FileText className="w-5 h-5 mr-3 text-cyan-400" />
                  <span>{file.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* EIP Checkboxes */}
        {files.length > 0 && (
          <div className="max-w-2xl mx-auto mb-8">
            <h2 className="text-xl mb-4 font-mono">Select EIPs:</h2>
            <div className="space-y-2">
              {["ERC20", "ERC721", "ERC1155"].map((eip) => (
                <div key={eip} className="flex items-center">
                  <input
                    type="checkbox"
                    value={eip}
                    checked={eips.includes(eip)}
                    onChange={handleEipChange}
                    className="mr-2"
                    id={eip}
                  />
                  <label htmlFor={eip} className="cursor-pointer">
                    {eip}
                  </label>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Button */}
        {files.length > 0 && (
          <div className="text-center">
            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className={`px-8 py-3 rounded-lg font-mono tracking-wider transition-all
                ${
                  analyzing
                    ? "bg-cyan-900 text-cyan-300/50"
                    : "bg-cyan-800 hover:bg-cyan-700 text-cyan-100"
                }
              `}
            >
              {analyzing ? (
                <span className="flex items-center">
                  <AlertCircle className="animate-pulse mr-2" />
                  ANALYZING...
                </span>
              ) : (
                "ANALYZE FILES"
              )}
            </button>
          </div>
        )}

        {error && <p className="text-red-600 mt-6">{error}</p>}
        {results?.message && (
          <p className="text-cyan-300 mt-4">
            <strong>Message: </strong>
            {results?.message}
          </p>
        )}
        {results?.progress && (
          <p className="text-cyan-300 mt-4">
            <strong>Progress: </strong>
            {results?.progress}%
          </p>
        )}
        {/* {results?.data} */}
        {/* {resultsData} */}
        <div className="">
          {/* {results?.data ? ( */}
          <div className="mt-4">
            <h2 className="text-xl font-bold my-3">Analysis Results:</h2>
            <pre
              dangerouslySetInnerHTML={{ __html: resultsData }}
              className="bg-gray-800 text-cyan-400 p-4 rounded text-wrap"
            >
              {/* {resultsData} */}
            </pre>
          </div>
          {/* )  */}
          {/* : (
            <p className="text-cyan-300 mt-4">No analysis results available.</p>
          )} */}
        </div>
      </div>

      <style jsx global>{`
        @keyframes rain {
          0% {
            transform: translateY(-100%);
            opacity: 0;
          }
          50% {
            opacity: 1;
          }
          100% {
            transform: translateY(100vh);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
};

export default FileAnalyzer;
