import React, { useState, useRef } from "react";
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Mic, 
  FileText, 
  UploadCloud, 
  Volume2, 
  CheckCircle2, 
  XCircle, 
  Loader2, 
  RefreshCw,
  Info
} from "lucide-react";

/**
 * SatyaNet Dashboard Component
 * Production-ready React + Tailwind CSS interface for multi-modal misinformation
 * and audio deepfake detection in regional languages.
 */
export default function SatyaNetDashboard() {
  const [activeTab, setActiveTab] = useState("audio"); // 'audio' | 'text'
  const [backendUrl, setBackendUrl] = useState("http://127.0.0.1:8000");

  // --- Audio State ---
  const [audioFile, setAudioFile] = useState(null);
  const [audioPreviewUrl, setAudioPreviewUrl] = useState(null);
  const [isAudioLoading, setIsAudioLoading] = useState(false);
  const [audioResult, setAudioResult] = useState(null);
  const [audioError, setAudioError] = useState(null);
  const fileInputRef = useRef(null);

  // --- Text State ---
  const [textContent, setTextContent] = useState("");
  const [selectedLang, setSelectedLang] = useState("auto");
  const [isTextLoading, setIsTextLoading] = useState(false);
  const [textResult, setTextResult] = useState(null);
  const [textError, setTextError] = useState(null);

  // Quick Test Samples for Demos
  const sampleClaims = [
    {
      title: "Free Recharge Scam (Hinglish)",
      text: "Modi sarkar sabhi vidyarthiyo ko 3 mahine ka free recharge de rahi hai! Turant link bit.ly/free-recharge-2024 pe click karo aur 10 dosto ko bhejo.",
      lang: "hinglish"
    },
    {
      title: "Child Lifter WhatsApp Hoax (Hindi)",
      text: "सावधान! आपके इलाके में 5 बच्चा चोर गिरोह सक्रिय हैं। यह संदेश 10 ग्रुप में तुरंत भेजें ताकि कोई अनहोनी न हो।",
      lang: "hi"
    },
    {
      title: "Verified Fact (English)",
      text: "ISRO has successfully landed the Chandrayaan-3 lander near the south pole of the Moon.",
      lang: "en"
    }
  ];

  // Handle Audio File Selection / Drop
  const handleFileChange = (file) => {
    if (!file) return;
    setAudioFile(file);
    setAudioResult(null);
    setAudioError(null);
    setAudioPreviewUrl(URL.createObjectURL(file));
  };

  // Submit Audio to API
  const handleAudioSubmit = async () => {
    if (!audioFile) return;
    setIsAudioLoading(true);
    setAudioError(null);
    setAudioResult(null);

    const formData = new FormData();
    formData.append("file", audioFile);

    try {
      const response = await fetch(`${backendUrl}/api/detect-audio`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      setAudioResult(data);
    } catch (err) {
      setAudioError(err.message || "Failed to analyze audio.");
    } finally {
      setIsAudioLoading(false);
    }
  };

  // Submit Text to API
  const handleTextSubmit = async () => {
    if (!textContent.trim()) return;
    setIsTextLoading(true);
    setTextError(null);
    setTextResult(null);

    try {
      const response = await fetch(`${backendUrl}/api/detect-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: textContent,
          language: selectedLang,
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();
      setTextResult(data);
    } catch (err) {
      setTextError(err.message || "Failed to analyze text claim.");
    } finally {
      setIsTextLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 font-sans">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Top Header */}
        <header className="flex flex-col md:flex-row md:items-center justify-between border-b border-slate-800 pb-6 gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="p-2.5 bg-blue-600/20 border border-blue-500/30 rounded-xl text-blue-400">
                <ShieldCheck className="w-8 h-8" />
              </span>
              <div>
                <h1 className="text-3xl font-extrabold tracking-tight text-white flex items-center gap-2">
                  SatyaNet <span className="text-sm font-normal text-slate-400 px-2 py-0.5 rounded bg-slate-800 border border-slate-700">सत्य-नेट</span>
                </h1>
                <p className="text-sm text-slate-400">
                  Regional Multi-Modal Misinformation & Voice-Clone Deepfake Detector
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-xs text-slate-400 font-mono">16kHz Vernacular Engine: Active</span>
          </div>
        </header>

        {/* Tab Toggle Navigation */}
        <div className="flex justify-center">
          <div className="inline-flex p-1.5 bg-slate-900 border border-slate-800 rounded-xl shadow-inner">
            <button
              onClick={() => setActiveTab("audio")}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                activeTab === "audio"
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <Mic className="w-4 h-4" />
              Audio Deepfake Scanner
            </button>
            <button
              onClick={() => setActiveTab("text")}
              className={`flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all duration-200 ${
                activeTab === "text"
                  ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
                  : "text-slate-400 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <FileText className="w-4 h-4" />
              Text Claim Verifier
            </button>
          </div>
        </div>

        {/* ======================================================== */}
        {/* TAB 1: AUDIO DEEPFAKE SCANNER                            */}
        {/* ======================================================== */}
        {activeTab === "audio" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Input Column */}
            <div className="lg:col-span-5 space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
                  <Volume2 className="w-5 h-5 text-blue-400" />
                  Upload WhatsApp Voice Note
                </h2>
                <p className="text-xs text-slate-400 mb-4">
                  Normalized to 16 kHz mono. Supports WAV, MP3, OGG, M4A, FLAC.
                </p>

                {/* Drag & Drop Zone */}
                <div
                  onDragOver={(e) => e.preventDefault()}
                  onDrop={(e) => {
                    e.preventDefault();
                    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                      handleFileChange(e.dataTransfer.files[0]);
                    }
                  }}
                  onClick={() => fileInputRef.current?.click()}
                  className="border-2 border-dashed border-slate-700 hover:border-blue-500/60 bg-slate-950/60 hover:bg-blue-950/10 rounded-xl p-8 flex flex-col items-center justify-center cursor-pointer transition-colors text-center group"
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={(e) => e.target.files && handleFileChange(e.target.files[0])}
                    accept="audio/*"
                    className="hidden"
                  />
                  <UploadCloud className="w-12 h-12 text-slate-500 group-hover:text-blue-400 mb-3 transition-colors" />
                  <p className="text-sm font-medium text-slate-200">
                    {audioFile ? audioFile.name : "Click or drag audio clip here"}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Ideal for detecting ElevenLabs, Tortoise, or VITS voice cloning
                  </p>
                </div>

                {/* Audio Preview */}
                {audioPreviewUrl && (
                  <div className="mt-4 p-3 bg-slate-950 rounded-lg border border-slate-800">
                    <p className="text-xs text-slate-400 mb-2 font-mono">Audio Preview:</p>
                    <audio src={audioPreviewUrl} controls className="w-full h-9" />
                  </div>
                )}

                {/* Submit Action */}
                <button
                  onClick={handleAudioSubmit}
                  disabled={!audioFile || isAudioLoading}
                  className="mt-5 w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 transition-all"
                >
                  {isAudioLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Extracting Mel-Spectrogram & MFCCs...
                    </>
                  ) : (
                    "Run Forensic Analysis"
                  )}
                </button>

                {audioError && (
                  <div className="mt-4 p-3 bg-rose-950/50 border border-rose-800 rounded-lg text-rose-300 text-xs flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                    <span>{audioError}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Result Column */}
            <div className="lg:col-span-7">
              {audioResult ? (
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
                  {/* Risk Header Card */}
                  <div className={`p-5 rounded-xl border flex items-start gap-4 ${
                    audioResult.risk_category === "HIGH_RISK"
                      ? "bg-rose-950/40 border-rose-800 text-rose-200"
                      : audioResult.risk_category === "SUSPICIOUS"
                      ? "bg-amber-950/40 border-amber-800 text-amber-200"
                      : "bg-emerald-950/40 border-emerald-800 text-emerald-200"
                  }`}>
                    {audioResult.risk_category === "HIGH_RISK" ? (
                      <XCircle className="w-8 h-8 text-rose-400 shrink-0 mt-0.5" />
                    ) : audioResult.risk_category === "SUSPICIOUS" ? (
                      <AlertTriangle className="w-8 h-8 text-amber-400 shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="flex items-center gap-3">
                        <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                          audioResult.risk_category === "HIGH_RISK"
                            ? "bg-rose-900/80 text-rose-300"
                            : audioResult.risk_category === "SUSPICIOUS"
                            ? "bg-amber-900/80 text-amber-300"
                            : "bg-emerald-900/80 text-emerald-300"
                        }`}>
                          {audioResult.risk_category.replace("_", " ")}
                        </span>
                        <span className="text-sm font-semibold">{audioResult.verdict}</span>
                      </div>
                      <p className="text-sm mt-2 font-medium opacity-90">
                        {audioResult.recommendation}
                      </p>
                    </div>
                  </div>

                  {/* Probability Meter & Stats */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 text-center">
                      <span className="text-xs text-slate-400 block mb-1">Deepfake Risk</span>
                      <span className={`text-2xl font-black ${
                        audioResult.deepfake_probability > 0.6
                          ? "text-rose-400"
                          : audioResult.deepfake_probability > 0.35
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}>
                        {audioResult.deepfake_percentage}
                      </span>
                    </div>

                    <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 text-center">
                      <span className="text-xs text-slate-400 block mb-1">Confidence</span>
                      <span className="text-2xl font-black text-blue-400">
                        {audioResult.confidence_percentage}
                      </span>
                    </div>

                    <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800 text-center">
                      <span className="text-xs text-slate-400 block mb-1">Duration</span>
                      <span className="text-2xl font-black text-slate-200">
                        {audioResult.duration_seconds}s
                      </span>
                    </div>
                  </div>

                  {/* Flagged Indicators */}
                  <div>
                    <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wide mb-2 flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-amber-400" />
                      Forensic Biomarkers Identified:
                    </h3>
                    <ul className="space-y-2">
                      {audioResult.flagged_indicators.map((ind, i) => (
                        <li key={i} className="text-xs p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-slate-300 flex items-center gap-2">
                          <span className="text-amber-400 font-bold">•</span>
                          {ind}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Technical Feature Details */}
                  <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs">
                    <p className="text-slate-400 font-mono mb-2">Librosa Acoustic Metrics:</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-slate-300">
                      <div>Flatness: <span className="font-mono text-blue-400">{audioResult.acoustic_biomarkers.mean_spectral_flatness}</span></div>
                      <div>Pitch Mean: <span className="font-mono text-blue-400">{audioResult.acoustic_biomarkers.pitch_mean_hz} Hz</span></div>
                      <div>Jitter Proxy: <span className="font-mono text-blue-400">{audioResult.acoustic_biomarkers.pitch_jitter_proxy}</span></div>
                      <div>MFCC Delta Var: <span className="font-mono text-blue-400">{audioResult.acoustic_biomarkers.mfcc_delta_variance}</span></div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full border-2 border-dashed border-slate-800 rounded-2xl p-12 flex flex-col items-center justify-center text-center text-slate-500">
                  <Mic className="w-12 h-12 mb-3 text-slate-700" />
                  <p className="font-medium text-slate-400">No Audio Analyzed Yet</p>
                  <p className="text-xs text-slate-600 mt-1 max-w-sm">
                    Upload a voice note on the left to review spectral flatness, pitch monotony, and neural vocoder anomalies.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: TEXT CLAIM VERIFIER                              */}
        {/* ======================================================== */}
        {activeTab === "text" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Input Column */}
            <div className="lg:col-span-5 space-y-4">
              <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
                <h2 className="text-lg font-bold text-white mb-1 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-blue-400" />
                  Forwarded Social Message / Claim
                </h2>
                <p className="text-xs text-slate-400 mb-4">
                  Accepts vernacular script (Devanagari, Tamil, etc.) or Romanized Hinglish.
                </p>

                {/* Quick-load Test Chips */}
                <div className="mb-4 space-y-1.5">
                  <p className="text-xs text-slate-400 font-medium">Quick Demo Samples:</p>
                  <div className="flex flex-wrap gap-1.5">
                    {sampleClaims.map((sample, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setTextContent(sample.text);
                          setSelectedLang(sample.lang);
                        }}
                        className="text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-md transition-colors"
                      >
                        {sample.title}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Language Select */}
                <div className="mb-3">
                  <label className="block text-xs font-medium text-slate-400 mb-1">Regional Language Hint:</label>
                  <select
                    value={selectedLang}
                    onChange={(e) => setSelectedLang(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
                  >
                    <option value="auto">Auto-Detect Script</option>
                    <option value="hi">Hindi (हिंदी)</option>
                    <option value="hinglish">Hinglish (Roman script)</option>
                    <option value="bn">Bengali (বাংলা)</option>
                    <option value="ta">Tamil (தமிழ்)</option>
                    <option value="te">Telugu (తెలుగు)</option>
                    <option value="en">English</option>
                  </select>
                </div>

                {/* Text Area */}
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  placeholder="Paste WhatsApp forward or social media snippet here..."
                  rows={5}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-100 placeholder-slate-600 focus:outline-none focus:border-blue-500 resize-none font-sans"
                />

                {/* Submit Action */}
                <button
                  onClick={handleTextSubmit}
                  disabled={!textContent.trim() || isTextLoading}
                  className="mt-4 w-full py-3 px-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 transition-all"
                >
                  {isTextLoading ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Evaluating Claim & Vernacular Semantics...
                    </>
                  ) : (
                    "Verify Claim Credibility"
                  )}
                </button>

                {textError && (
                  <div className="mt-4 p-3 bg-rose-950/50 border border-rose-800 rounded-lg text-rose-300 text-xs flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 shrink-0" />
                    <span>{textError}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Results Column */}
            <div className="lg:col-span-7">
              {textResult ? (
                <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
                  {/* Verdict Badge Card */}
                  <div className={`p-5 rounded-xl border flex items-start gap-4 ${
                    textResult.risk_category === "HIGH_RISK" || textResult.verdict === "FALSE"
                      ? "bg-rose-950/40 border-rose-800 text-rose-200"
                      : textResult.risk_category === "SUSPICIOUS" || textResult.verdict === "MISLEADING"
                      ? "bg-amber-950/40 border-amber-800 text-amber-200"
                      : "bg-emerald-950/40 border-emerald-800 text-emerald-200"
                  }`}>
                    {textResult.risk_category === "HIGH_RISK" ? (
                      <XCircle className="w-8 h-8 text-rose-400 shrink-0 mt-0.5" />
                    ) : textResult.risk_category === "SUSPICIOUS" ? (
                      <AlertTriangle className="w-8 h-8 text-amber-400 shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 className="w-8 h-8 text-emerald-400 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <div className="flex items-center gap-3">
                        <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                          textResult.risk_category === "HIGH_RISK"
                            ? "bg-rose-900/80 text-rose-300"
                            : textResult.risk_category === "SUSPICIOUS"
                            ? "bg-amber-900/80 text-amber-300"
                            : "bg-emerald-900/80 text-emerald-300"
                        }`}>
                          VERDICT: {textResult.verdict}
                        </span>
                        <span className="text-xs text-slate-400">
                          Language: {textResult.detected_language}
                        </span>
                      </div>
                      <p className="text-sm mt-2 font-medium opacity-90">
                        {textResult.summary}
                      </p>
                    </div>
                  </div>

                  {/* Credibility Score Meter */}
                  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-xs font-semibold text-slate-400">Credibility Rating</span>
                      <span className={`text-lg font-bold ${
                        textResult.credibility_score < 40
                          ? "text-rose-400"
                          : textResult.credibility_score < 70
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}>
                        {textResult.credibility_score} / 100
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full transition-all duration-500 ${
                          textResult.credibility_score < 40
                            ? "bg-rose-500"
                            : textResult.credibility_score < 70
                            ? "bg-amber-500"
                            : "bg-emerald-500"
                        }`}
                        style={{ width: `${textResult.credibility_score}%` }}
                      />
                    </div>
                  </div>

                  {/* Core Claim */}
                  <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs text-slate-300">
                    <span className="font-semibold text-blue-400">Extracted Core Claim: </span>
                    {textResult.core_claim}
                  </div>

                  {/* Manipulation Factors */}
                  <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                      Manipulation Tactics & Flags:
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {textResult.manipulation_tactics.map((tactic, i) => (
                        <span key={i} className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300 text-xs font-medium">
                          🚩 {tactic}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Reasoning Bullets */}
                  <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
                      Reasoning & Context:
                    </h3>
                    <ul className="space-y-1.5 text-xs text-slate-300">
                      {textResult.reasoning.map((r, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-blue-400 font-bold">•</span>
                          <span>{r}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Recommendation */}
                  <div className="p-3 bg-blue-950/30 border border-blue-900/50 rounded-lg text-xs text-blue-200">
                    <span className="font-semibold text-blue-300">Action: </span>
                    {textResult.recommended_action}
                  </div>
                </div>
              ) : (
                <div className="h-full border-2 border-dashed border-slate-800 rounded-2xl p-12 flex flex-col items-center justify-center text-center text-slate-500">
                  <FileText className="w-12 h-12 mb-3 text-slate-700" />
                  <p className="font-medium text-slate-400">No Claim Analyzed Yet</p>
                  <p className="text-xs text-slate-600 mt-1 max-w-sm">
                    Paste a forwarded WhatsApp message or choose a demo sample on the left to extract claims and verify credibility.
                  </p>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
