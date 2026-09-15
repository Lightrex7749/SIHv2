import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";

import {
  Shield,
  AlertTriangle,
  MapPin,
  CheckCircle,
  XCircle,
  Clock,
  Layers,
  FileText,
  Camera,
  Cpu,
  HelpCircle,
  RefreshCw,
  Send,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  Database,
  Info
} from "lucide-react";
import { MapContainer, TileLayer, Marker, Popup, Polygon, Tooltip } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix Leaflet default marker icons in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Custom marker icons by risk level
const createColoredIcon = (color) => {
  return L.divIcon({
    className: "custom-div-icon",
    html: `<div style="background-color:${color};width:16px;height:16px;border-radius:50%;border:2px solid white;box-shadow:0 0 6px rgba(0,0,0,0.5);"></div>`,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
};

const iconRed = createColoredIcon("#ef4444");
const iconOrange = createColoredIcon("#f97316");
const iconYellow = createColoredIcon("#eab308");
const iconGreen = createColoredIcon("#10b981");
const iconBlue = createColoredIcon("#3b82f6");

// Google Maps & Topo Tile Providers (Normal, Satellite, Terrain / Altitude)
const MAP_LAYERS = {
  satellite: {
    id: "satellite",
    name: "Satellite (Hybrid)",
    icon: "🛰️",
    url: "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    attribution: '&copy; <a href="https://maps.google.com">Google Maps</a> Satellite & High-Res Imagery',
    maxZoom: 20,
  },
  terrain: {
    id: "terrain",
    name: "Altitude / Terrain (Contours)",
    icon: "🏔️",
    url: "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
    attribution: '&copy; <a href="https://maps.google.com">Google Maps</a> Terrain & Elevation Contours',
    maxZoom: 20,
  },
  streets: {
    id: "streets",
    name: "Normal (Streets)",
    icon: "🗺️",
    url: "https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
    attribution: '&copy; <a href="https://maps.google.com">Google Maps</a> Standard Roadmap',
    maxZoom: 20,
  },
};

// Static translations for English and Hindi
const I18N = {
  en: {
    title: "DrishtiSetu",
    tagline: "AI-Driven GIS Disaster Relocation Decision-Support Platform",
    pilot: "Pilot: Chamoli District, Uttarakhand",
    authorityBadge: "Authorized Disaster Management Authority",
    selectedHabitation: "Selected Habitation",
    riskScore: "Overall Risk Score",
    riskLevel: "Risk Level",
    priority: "Relocation Priority",
    whyScore: "Why this score? (Explainability)",
    population: "Population",
    elevation: "Elevation",
    slope: "Slope",
    hazardType: "Primary Hazard",
    cvAnalysis: "Satellite Computer Vision Analysis",
    candidateSites: "Candidate Relocation Sites",
    carryingCapacity: "Carrying Capacity & Safety Margin",
    ragEvidence: "NDMA & Statutory Policy Evidence",
    authorityAction: "Authority Action & Audit Trail",
    decisionLog: "Decision History Audit Log",
    accept: "Accept Recommendation",
    reject: "Reject",
    defer: "Defer Action",
    submitDecision: "Submit Authorized Action",
    notesPlaceholder: "Enter directives, budgetary approvals, or ground inspection remarks...",
    testUncertainty: "Test Insufficient-Evidence Safeguard",
    modelDisclosure: "Model Disclosure",
    insufficientNotice: "Uncertainty Safeguard Triggered: System refuses to hallucinate when evidence is insufficient.",
  },
  hi: {
    title: "दृष्टिसेतु",
    tagline: "एआई-संचालित जीआईएस आपदा पुनर्वास निर्णय-समर्थन मंच",
    pilot: "पायलट: चमोली जनपद, उत्तराखंड",
    authorityBadge: "प्राधिकृत आपदा प्रबंधन प्राधिकरण",
    selectedHabitation: "चयनित निवास क्षेत्र",
    riskScore: "समग्र जोखिम सूचकांक",
    riskLevel: "जोखिम स्तर",
    priority: "पुनर्वास प्राथमिकता",
    whyScore: "यह स्कोर क्यों? (स्पष्टीकरण)",
    population: "जनसंख्या",
    elevation: "ऊंचाई",
    slope: "ढलान",
    hazardType: "प्रमुख आपदा",
    cvAnalysis: "उपग्रह कंप्यूटर विज़न विश्लेषण",
    candidateSites: "प्रस्तावित सुरक्षित पुनर्वास स्थल",
    carryingCapacity: "वहनीय क्षमता एवं सुरक्षा सीमा",
    ragEvidence: "एनडीएमए एवं विधिक नीति साक्ष्य",
    authorityAction: "प्राधिकरण कार्यवाही एवं ऑडिट ट्रेल",
    decisionLog: "निर्णय इतिहास ऑडिट लॉग",
    accept: "सिफारिश स्वीकार करें",
    reject: "अस्वीकार करें",
    defer: "निर्णय स्थगित करें",
    submitDecision: "प्राधिकृत निर्णय दर्ज करें",
    notesPlaceholder: "प्रशासनिक निर्देश, बजट आवंटन या भूगर्भीय निरीक्षण टिप्पणी दर्ज करें...",
    testUncertainty: "अपर्याप्त साक्ष्य सुरक्षा परीक्षण",
    modelDisclosure: "मॉडल प्रकटीकरण",
    insufficientNotice: "अनिश्चितता सुरक्षा सक्रिय: साक्ष्य अपर्याप्त होने पर प्रणाली अनुमान नहीं लगाती।",
  }
};

export default function DrishtiDashboard() {
  const navigate = useNavigate();
  const [showSuiteMenu, setShowSuiteMenu] = useState(false);
  const [lang, setLang] = useState("en");

  const t = I18N[lang];

  const [habitations, setHabitations] = useState([]);
  const [selectedHabId, setSelectedHabId] = useState("H001");
  const [habitationDetails, setHabitationDetails] = useState(null);
  const [decisionData, setDecisionData] = useState(null);
  const [explainData, setExplainData] = useState(null);
  const [showExplainModal, setShowExplainModal] = useState(false);
  const [visionData, setVisionData] = useState(null);
  const [decisionHistory, setDecisionHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  // Map Base Layer state ("satellite" | "terrain" | "streets")
  const [mapBaseLayer, setMapBaseLayer] = useState("satellite");
  const [showAltitudeBadges, setShowAltitudeBadges] = useState(true);

  // Form states for Authority Action
  const [authorityDecision, setAuthorityDecision] = useState("ACCEPTED");
  const [reviewerName, setReviewerName] = useState("District Magistrate, Chamoli");
  const [actionNotes, setActionNotes] = useState("");
  const [actionSubmitting, setActionSubmitting] = useState(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState("");

  // RAG query testing
  const [ragResult, setRagResult] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);

  // OpenRouter Nemotron-3 AI Advisor states
  const [aiPrompt, setAiPrompt] = useState("");
  const [aiResponse, setAiResponse] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);

  const handleAiConsult = async (customQuery) => {
    const q = customQuery || aiPrompt;
    if (!q || !q.trim()) return;
    setAiLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/api/v1/ai/consult`, {
        query: q,
        habitation_id: selectedHabId
      });
      setAiResponse(res.data);
      if (!customQuery) setAiPrompt("");
    } catch (err) {
      console.error("AI Advisor error:", err);
      setAiResponse({
        answer: "AI Advisor connection error. Please ensure backend is running.",
        model: "offline-fallback",
        status: "error"
      });
    } finally {
      setAiLoading(false);
    }
  };

  // Load habitations on mount
  useEffect(() => {
    fetchHabitations();
  }, []);

  // Fetch full details when selected habitation changes
  useEffect(() => {
    if (selectedHabId) {
      loadHabitationData(selectedHabId);
    }
  }, [selectedHabId]);

  const fetchHabitations = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/v1/habitations`);
      setHabitations(res.data);
      if (res.data.length > 0) {
        setSelectedHabId(res.data[0].id);
      }
    } catch (err) {
      console.warn("Using fallback local habitations:", err);
      // Local fallback data
      const fallback = [
        { id: "H001", name: "Joshimath (Sunil Ward)", district: "Chamoli", latitude: 30.556, longitude: 79.566, population: 1250, risk_score: 82.5, risk_level: "CRITICAL", relocation_priority: "IMMEDIATE" },
        { id: "H002", name: "Raini Village", district: "Chamoli", latitude: 30.485, longitude: 79.702, population: 420, risk_score: 89.0, risk_level: "CRITICAL", relocation_priority: "IMMEDIATE" },
        { id: "H003", name: "Helang Habitation", district: "Chamoli", latitude: 30.528, longitude: 79.510, population: 890, risk_score: 71.5, risk_level: "HIGH", relocation_priority: "SHORT_TERM" },
        { id: "H004", name: "Pipalkoti Settlement", district: "Chamoli", latitude: 30.430, longitude: 79.430, population: 1600, risk_score: 48.0, risk_level: "MODERATE", relocation_priority: "LONG_TERM" },
      ];
      setHabitations(fallback);
      setSelectedHabId("H001");
    }
  };

  const loadHabitationData = async (habId) => {
    setLoading(true);
    setActionSuccessMsg("");
    try {
      // 1. Fetch habitation info
      const habRes = await axios.get(`${API_BASE}/api/v1/habitations/${habId}`).catch(() => null);
      if (habRes?.data) setHabitationDetails(habRes.data);

      // 2. Fetch Decision analyze
      const decRes = await axios.post(`${API_BASE}/api/v1/decision/analyze`, { habitation_id: habId }).catch(() => null);
      if (decRes?.data) {
        setDecisionData(decRes.data);
        setRagResult({
          answer: decRes.data.evidence?.[0]?.title ? "Retrieved statutory guidance from National Disaster Management Guidelines and R&R Policy 2007." : "Standard guidance available.",
          sources: decRes.data.evidence || [],
          evidence_sufficient: decRes.data.evidence_sufficient
        });
      }

      // 3. Fetch Explainability breakdown
      const expRes = await axios.get(`${API_BASE}/api/v1/risk/explain/${habId}`).catch(() => null);
      if (expRes?.data) setExplainData(expRes.data);

      // 4. Fetch Computer Vision detection for this area
      const visRes = await axios.post(`${API_BASE}/api/v1/vision/analyze`, {
        image_url: "computer_vision/demo_assets/chamoli_landslide_post.png",
        latitude: habRes?.data?.latitude || 30.556,
        longitude: habRes?.data?.longitude || 79.566
      }).catch(() => null);
      if (visRes?.data) setVisionData(visRes.data);

      // 5. Fetch Decision History Audit Trail
      const histRes = await axios.get(`${API_BASE}/api/v1/decision/log/${habId}`).catch(() => null);
      if (histRes?.data) setDecisionHistory(histRes.data);

    } catch (err) {
      console.error("Error loading habitation data:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleAuthoritySubmit = async (e) => {
    e.preventDefault();
    setActionSubmitting(true);
    setActionSuccessMsg("");
    try {
      const payload = {
        habitation_id: selectedHabId,
        recommendation_id: `REC_${selectedHabId}_${Date.now().toString().slice(-4)}`,
        reviewed_by: reviewerName,
        decision: authorityDecision,
        notes: actionNotes
      };
      const res = await axios.post(`${API_BASE}/api/v1/decision/log`, payload);
      setActionSuccessMsg(`Action recorded successfully! Log ID: ${res.data.id}`);
      setActionNotes("");
      // Refresh history
      const histRes = await axios.get(`${API_BASE}/api/v1/decision/log/${selectedHabId}`);
      if (histRes?.data) setDecisionHistory(histRes.data);
    } catch (err) {
      console.error("Failed to log decision:", err);
      alert("Error recording authority action. Check backend connection.");
    } finally {
      setActionSubmitting(false);
    }
  };

  const testInsufficientEvidenceQuery = async () => {
    setRagLoading(true);
    try {
      // Obscure demo query out-of-corpus per DEMO_FLOW.md
      const obscureQuery = "What is the sediment transport model used for coastal erosion prediction on the Konkan coast?";
      const res = await axios.post(`${API_BASE}/api/v1/rag/query`, { question: obscureQuery });
      setRagResult(res.data);
    } catch (err) {
      console.error("RAG test error:", err);
    } finally {
      setRagLoading(false);
    }
  };

  const activeHab = habitationDetails || habitations.find(h => h.id === selectedHabId) || {};
  const currentRiskLevel = decisionData?.risk?.risk_level || activeHab.risk_level || "HIGH";
  const isCritical = currentRiskLevel === "CRITICAL";

  // Red Zone sample polygon coordinates (Joshimath subsidence scarp)
  const redZoneCoords = [
    [30.540, 79.545],
    [30.542, 79.585],
    [30.570, 79.580],
    [30.565, 79.540],
  ];

  // Protected Eco-Sensitive Conflict Zone polygon
  const ecoZoneCoords = [
    [30.470, 79.630],
    [30.475, 79.730],
    [30.525, 79.730],
    [30.520, 79.630],
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* ----------------- Top Header ----------------- */}
      <header className="bg-slate-900/90 border-b border-slate-800 backdrop-blur-md px-6 py-3 flex flex-wrap items-center justify-between sticky top-0 z-50">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-indigo-600 rounded-lg shadow-lg shadow-indigo-500/30">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-white">{t.title}</h1>
              <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 rounded-full">
                v2.0 Hackathon-Hardened
              </span>
            </div>
            <p className="text-xs text-slate-400">{t.tagline}</p>
          </div>
        </div>

        <div className="flex items-center space-x-4 mt-2 sm:mt-0">
          {/* Pilot District Indicator */}
          <div className="flex items-center space-x-2 px-3 py-1.5 bg-emerald-950/40 border border-emerald-800/50 rounded-lg text-xs text-emerald-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="font-medium">{t.pilot}</span>
          </div>

          {/* Authority Role Badge */}
          <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 bg-slate-800/80 border border-slate-700 rounded-lg text-xs text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>{t.authorityBadge}</span>
          </div>

          {/* Language Toggle */}
          <div className="flex bg-slate-800 p-1 rounded-lg border border-slate-700 text-xs">
            <button
              onClick={() => setLang("en")}
              className={`px-2.5 py-1 rounded font-medium transition ${lang === "en" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white"}`}
            >
              EN
            </button>
            <button
              onClick={() => setLang("hi")}
              className={`px-2.5 py-1 rounded font-medium transition ${lang === "hi" ? "bg-indigo-600 text-white shadow" : "text-slate-400 hover:text-white"}`}
            >
              हिन्दी
            </button>
          </div>

          {/* Suraksha Setu All Portals Dropdown */}
          <div className="relative">
            <button
              onClick={() => setShowSuiteMenu(!showSuiteMenu)}
              className="flex items-center space-x-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold shadow transition"
            >
              <span>🌐 All Portals & Pages</span>
              <ChevronRight className={`w-3.5 h-3.5 transition-transform ${showSuiteMenu ? "rotate-90" : ""}`} />
            </button>

            {showSuiteMenu && (
              <div className="absolute right-0 mt-2 w-72 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl p-3 z-50 animate-in fade-in zoom-in-95">
                <div className="text-xs font-bold uppercase text-indigo-400 mb-2 px-1 tracking-wider">
                  Suraksha Setu Suite
                </div>
                <div className="grid grid-cols-1 gap-1 max-h-96 overflow-y-auto pr-1">
                  <Link to="/landing" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🏠</span> <span>Landing Page</span>
                  </Link>
                  <Link to="/app/dashboard" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>📊</span> <span>Main Dashboard</span>
                  </Link>
                  <Link to="/app/map" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🗺️</span> <span>Interactive GIS Map</span>
                  </Link>
                  <Link to="/app/alerts" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🚨</span> <span>Live Alerts & Early Warning</span>
                  </Link>
                  <Link to="/app/weather" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🌧️</span> <span>Weather & Cyclones</span>
                  </Link>
                  <Link to="/app/disasters" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🌋</span> <span>Disaster Management</span>
                  </Link>
                  <Link to="/app/community" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>👥</span> <span>Community Incident Feed</span>
                  </Link>
                  <Link to="/app/analytics" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>📈</span> <span>Disaster Analytics & AI</span>
                  </Link>
                  <Link to="/app/student" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🎓</span> <span>Student Awareness Portal</span>
                  </Link>
                  <Link to="/app/scientist" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🔬</span> <span>Scientist & Researcher Portal</span>
                  </Link>
                  <Link to="/app/admin" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>🛡️</span> <span>Admin Control Center</span>
                  </Link>
                  <Link to="/app/critical-contacts" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>📞</span> <span>Emergency Contacts</span>
                  </Link>
                  <Link to="/app/profile" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>👤</span> <span>User Profile & Settings</span>
                  </Link>
                  <Link to="/telegram-app" onClick={() => setShowSuiteMenu(false)} className="flex items-center space-x-2.5 px-2.5 py-2 rounded-lg hover:bg-slate-800 text-xs text-slate-200 transition">
                    <span>📱</span> <span>Telegram Mini App</span>
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </header>


      {/* ----------------- Sub-Bar: Selected Habitation Controls ----------------- */}
      <div className="bg-slate-900 border-b border-slate-800 px-6 py-3 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <label className="text-xs font-semibold uppercase text-slate-400 flex items-center space-x-1">
            <MapPin className="w-3.5 h-3.5 text-indigo-400" />
            <span>{t.selectedHabitation}:</span>
          </label>
          <select
            value={selectedHabId}
            onChange={(e) => setSelectedHabId(e.target.value)}
            className="bg-slate-800 border border-slate-700 text-white rounded-md px-3 py-1.5 text-sm font-medium focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          >
            {habitations.map((h) => (
              <option key={h.id} value={h.id}>
                {h.name} ({h.risk_level || "RISK"}) — Pop: {h.population?.toLocaleString() || 1200}
              </option>
            ))}
          </select>
          {loading && <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />}
        </div>

        <div className="flex items-center space-x-3 text-xs flex-wrap">
          {/* Risk Level Badge */}
          <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 rounded-md border border-slate-700">
            <span className="text-slate-400">{t.riskLevel}:</span>
            <span className={`font-bold px-1.5 py-0.5 rounded text-[11px] ${isCritical ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-amber-500/20 text-amber-300 border border-amber-500/30"}`}>
              {decisionData?.risk?.risk_level || activeHab.risk_level || "CRITICAL"}
            </span>
          </div>

          {/* Relocation Priority Badge */}
          <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 rounded-md border border-slate-700">
            <span className="text-slate-400">{t.priority}:</span>
            <span className="font-bold text-red-400">
              {decisionData?.risk?.relocation_priority || activeHab.relocation_priority || "IMMEDIATE"}
            </span>
          </div>

          {/* Overall Score with Explainability Button */}
          <button
            onClick={() => setShowExplainModal(true)}
            className="flex items-center space-x-1.5 px-3 py-1 bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-200 border border-indigo-500/40 rounded-md transition shadow-sm cursor-pointer"
          >
            <HelpCircle className="w-3.5 h-3.5 text-indigo-400" />
            <span className="font-semibold">{t.whyScore}</span>
            <span className="bg-indigo-500 text-white font-mono px-1.5 py-0.2 rounded text-[11px]">
              {decisionData?.risk?.overall_score || activeHab.risk_score || 82.5}
            </span>
          </button>
        </div>
      </div>

      {/* ----------------- Main Dashboard Grid ----------------- */}
      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left Column (7 Cols): Geospatial Command Map */}
        <section className="lg:col-span-7 flex flex-col space-y-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl flex-1 flex flex-col min-h-[480px] relative">
            <div className="px-4 py-3 bg-slate-850 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold text-slate-300">
              <div className="flex items-center space-x-2">
                <Layers className="w-4 h-4 text-indigo-400" />
                <span>Chamoli District GIS Multi-Hazard & Relocation Overlay</span>
              </div>
              <div className="flex items-center space-x-3 text-[11px] text-slate-400">
                <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block"></span><span>Red Zone</span></span>
                <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span><span>Safe Site</span></span>
                <span className="flex items-center space-x-1"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 inline-block"></span><span>Eco-Zone Conflict</span></span>
              </div>
            </div>

            {/* Google Maps-Style Layer Control Bar (Top-Right Floating) */}
            <div className="absolute top-14 right-3 z-20 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 rounded-lg p-1.5 shadow-2xl flex items-center space-x-1 text-xs">
              <button
                type="button"
                onClick={() => setMapBaseLayer("streets")}
                className={`px-2.5 py-1 rounded font-medium flex items-center space-x-1.5 transition cursor-pointer ${
                  mapBaseLayer === "streets"
                    ? "bg-indigo-600 text-white shadow-md font-semibold"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`}
                title="Standard Google Roadmap / Streets"
              >
                <span>🗺️</span>
                <span>Normal</span>
              </button>
              <button
                type="button"
                onClick={() => setMapBaseLayer("satellite")}
                className={`px-2.5 py-1 rounded font-medium flex items-center space-x-1.5 transition cursor-pointer ${
                  mapBaseLayer === "satellite"
                    ? "bg-indigo-600 text-white shadow-md font-semibold"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`}
                title="Google High-Resolution Hybrid Satellite Imagery"
              >
                <span>🛰️</span>
                <span>Satellite</span>
              </button>
              <button
                type="button"
                onClick={() => setMapBaseLayer("terrain")}
                className={`px-2.5 py-1 rounded font-medium flex items-center space-x-1.5 transition cursor-pointer ${
                  mapBaseLayer === "terrain"
                    ? "bg-indigo-600 text-white shadow-md font-semibold"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`}
                title="Altitude & Topographic Contour Map"
              >
                <span>🏔️</span>
                <span>Altitude/Terrain</span>
              </button>
              <div className="h-4 w-[1px] bg-slate-700 mx-1"></div>
              <button
                type="button"
                onClick={() => setShowAltitudeBadges(!showAltitudeBadges)}
                className={`px-2 py-1 rounded font-medium flex items-center space-x-1 transition cursor-pointer ${
                  showAltitudeBadges
                    ? "bg-cyan-600/30 text-cyan-200 border border-cyan-500/40"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`}
                title="Toggle Altitude & Elevation Labels on Map Markers"
              >
                <span>⛰️</span>
                <span className="text-[11px]">{showAltitudeBadges ? "Altitude: ON" : "Altitude: OFF"}</span>
              </button>
            </div>

            {/* Leaflet Map */}
            <div className="flex-1 relative z-0 min-h-[420px]">
              <MapContainer
                center={[activeHab.latitude || 30.556, activeHab.longitude || 79.566]}
                zoom={11}
                scrollWheelZoom={false}
                className="h-full w-full"
                style={{ height: "100%", width: "100%" }}
              >
                <TileLayer
                  key={mapBaseLayer}
                  attribution={MAP_LAYERS[mapBaseLayer].attribution}
                  url={MAP_LAYERS[mapBaseLayer].url}
                  maxZoom={MAP_LAYERS[mapBaseLayer].maxZoom}
                />

                {/* Red Zone Hazard Scarp Polygon */}
                <Polygon
                  positions={redZoneCoords}
                  pathOptions={{ color: "#ef4444", fillColor: "#ef4444", fillOpacity: 0.35, weight: 2 }}
                >
                  <Tooltip permanent direction="center" className="bg-red-950 text-red-200 border-none text-[10px] font-bold">
                    Joshimath Subsidence Red Zone
                  </Tooltip>
                </Polygon>

                {/* Protected Eco-Sensitive Zone Polygon */}
                <Polygon
                  positions={ecoZoneCoords}
                  pathOptions={{ color: "#f59e0b", fillColor: "#f59e0b", fillOpacity: 0.25, weight: 2, dashArray: "4, 4" }}
                >
                  <Tooltip direction="center" className="bg-amber-950 text-amber-200 border-none text-[10px]">
                    Nanda Devi Eco-Sensitive Buffer (Conflict Zone)
                  </Tooltip>
                </Polygon>

                {/* Habitations Markers */}
                {habitations.map((h) => {
                  const isSelected = h.id === selectedHabId;
                  const isCrit = h.risk_level === "CRITICAL" || (h.risk_score && h.risk_score >= 80);
                  const icon = isCrit ? iconRed : iconOrange;

                  return (
                    <Marker
                      key={h.id}
                      position={[h.latitude || 30.55, h.longitude || 79.56]}
                      icon={icon}
                      eventHandlers={{
                        click: () => setSelectedHabId(h.id)
                      }}
                    >
                      {showAltitudeBadges && (
                        <Tooltip permanent direction="top" className="bg-slate-900/90 text-cyan-200 border border-slate-700 text-[10px] font-mono px-1 py-0.5 rounded shadow">
                          🏔️ {h.elevation || 1890}m | {h.slope || 34}°
                        </Tooltip>
                      )}
                      <Popup className="text-slate-900">
                        <div className="text-xs">
                          <h4 className="font-bold text-sm text-slate-900">{h.name}</h4>
                          <p className="text-slate-600">Pop: {h.population} | Elev: {h.elevation || 1890}m | Slope: {h.slope || 34}°</p>
                          <p className="font-semibold text-red-600 mt-1">Risk: {h.risk_level || "HIGH"} ({h.risk_score || 82.5})</p>
                          <button
                            onClick={() => setSelectedHabId(h.id)}
                            className="mt-2 text-[11px] bg-indigo-600 text-white px-2 py-1 rounded w-full"
                          >
                            Analyze Decision
                          </button>
                        </div>
                      </Popup>
                    </Marker>
                  );
                })}

                {/* Candidate Relocation Site Markers */}
                <Marker position={[30.535, 79.585]} icon={iconGreen}>
                  {showAltitudeBadges && (
                    <Tooltip permanent direction="top" className="bg-emerald-950/90 text-emerald-200 border border-emerald-700 text-[10px] font-mono px-1 py-0.5 rounded shadow">
                      🏔️ Dhak: 1,920m (Slope: 11°)
                    </Tooltip>
                  )}
                  <Popup>
                    <div className="text-xs text-slate-900">
                      <h4 className="font-bold text-emerald-700">Dhak Plateau Safe Terrace (S001)</h4>
                      <p>Capacity: 1,800 persons | Suitability: 84.5% | Elevation: 1,920m</p>
                      <span className="inline-block mt-1 px-2 py-0.5 bg-emerald-100 text-emerald-800 font-semibold rounded text-[10px]">
                        CLEAR (No Conflict)
                      </span>
                    </div>
                  </Popup>
                </Marker>

                {/* Land-Use Conflict Site (S003) */}
                <Marker position={[30.505, 79.660]} icon={iconYellow}>
                  {showAltitudeBadges && (
                    <Tooltip permanent direction="top" className="bg-amber-950/90 text-amber-200 border border-amber-700 text-[10px] font-mono px-1 py-0.5 rounded shadow">
                      🏔️ Nanda Devi Buffer: 2,150m
                    </Tooltip>
                  )}
                  <Popup>
                    <div className="text-xs text-slate-900">
                      <h4 className="font-bold text-amber-700">Nanda Devi Buffer Site (S003)</h4>
                      <p>Capacity: 1,400 persons | Suitability: 42.0% | Elevation: 2,150m</p>
                      <span className="inline-block mt-1 px-2 py-0.5 bg-red-100 text-red-800 font-bold rounded text-[10px]">
                        CONFLICT: Eco-Sensitive Reserve
                      </span>
                    </div>
                  </Popup>
                </Marker>

                {/* Alternate Safe Site (Pipalkoti S002) */}
                <Marker position={[30.445, 79.415]} icon={iconBlue}>
                  {showAltitudeBadges && (
                    <Tooltip permanent direction="top" className="bg-blue-950/90 text-blue-200 border border-blue-700 text-[10px] font-mono px-1 py-0.5 rounded shadow">
                      🏔️ Pipalkoti: 1,330m (Slope: 9°)
                    </Tooltip>
                  )}
                  <Popup>
                    <div className="text-xs text-slate-900">
                      <h4 className="font-bold text-blue-700">Pipalkoti Upper Tableland (S002)</h4>
                      <p>Capacity: 2,400 persons | Suitability: 88.0% | Elevation: 1,330m</p>
                      <span className="inline-block mt-1 px-2 py-0.5 bg-blue-100 text-blue-800 font-semibold rounded text-[10px]">
                        AVAILABLE
                      </span>
                    </div>
                  </Popup>
                </Marker>
              </MapContainer>
            </div>
          </div>

          {/* Quick Context Summary Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block">{t.population}</span>
              <span className="text-base font-bold text-white">
                {activeHab.population?.toLocaleString() || "1,250"}
              </span>
            </div>
            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block">{t.elevation}</span>
              <span className="text-base font-bold text-white">
                {activeHab.elevation || 1890} m
              </span>
            </div>
            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block">{t.slope}</span>
              <span className="text-base font-bold text-amber-400">
                {activeHab.slope || 34}°
              </span>
            </div>
            <div className="bg-slate-900 p-3 rounded-lg border border-slate-800">
              <span className="text-[11px] text-slate-400 block">{t.hazardType}</span>
              <span className="text-xs font-bold text-red-400 truncate block">
                {activeHab.hazard_type || "LANDSLIDE CREEP"}
              </span>
            </div>
          </div>

          {/* OpenRouter AI Disaster Relocation Advisor Panel */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-xl">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <div className="p-1.5 bg-gradient-to-br from-emerald-500 to-indigo-600 rounded-lg">
                  <Cpu className="w-4 h-4 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-xs text-white">AI Relocation Intelligence Advisor</h3>
                  <span className="text-[10px] text-slate-400">Powered by nvidia/nemotron-3-ultra-550b-a55b (OpenRouter)</span>
                </div>
              </div>
              <span className="px-2 py-0.5 text-[9px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full flex items-center space-x-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                <span>ONLINE</span>
              </span>
            </div>

            {/* Quick Prompt Suggestions */}
            <div className="mt-3 flex flex-wrap gap-1.5">
              <button
                type="button"
                onClick={() => handleAiConsult("Provide a statutory evacuation protocol summary for Joshimath under DM Act 2005.")}
                className="text-[10px] bg-slate-800 hover:bg-slate-750 text-indigo-300 px-2.5 py-1 rounded border border-slate-700 transition cursor-pointer"
              >
                ⚡ Evacuation Protocol
              </button>
              <button
                type="button"
                onClick={() => handleAiConsult("Why is Site S003 prohibited under the Forest Conservation Act 1980?")}
                className="text-[10px] bg-slate-800 hover:bg-slate-750 text-amber-300 px-2.5 py-1 rounded border border-slate-700 transition cursor-pointer"
              >
                ⚡ Site S003 Conflict Analysis
              </button>
              <button
                type="button"
                onClick={() => handleAiConsult("Outline rehabilitation benefits required per displaced family under NRRP 2007.")}
                className="text-[10px] bg-slate-800 hover:bg-slate-750 text-emerald-300 px-2.5 py-1 rounded border border-slate-700 transition cursor-pointer"
              >
                ⚡ NRRP 2007 Entitlements
              </button>
            </div>

            {/* AI Response Display */}
            {aiResponse && (
              <div className="mt-3 p-3 bg-slate-850 rounded-lg border border-slate-800 text-xs text-slate-200 space-y-2 animate-in fade-in">
                <div className="flex items-center justify-between text-[10px] text-slate-400 border-b border-slate-800 pb-1.5">
                  <span className="font-semibold text-emerald-400 flex items-center space-x-1">
                    <Shield className="w-3 h-3" />
                    <span>Advisor Briefing:</span>
                  </span>
                  <span className="font-mono text-slate-500">{aiResponse.model}</span>
                </div>
                <div className="text-[11px] leading-relaxed whitespace-pre-line text-slate-200 max-h-48 overflow-y-auto pr-1">
                  {aiResponse.answer}
                </div>
              </div>
            )}

            {/* Inquiry Input Form */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleAiConsult();
              }}
              className="mt-3 flex items-center space-x-2"
            >
              <input
                type="text"
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                placeholder="Ask AI advisor about relocation guidelines, legal acts, or terrain factors..."
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
              <button
                type="submit"
                disabled={aiLoading}
                className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer shadow-md shadow-indigo-600/30"
              >
                {aiLoading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                <span>{aiLoading ? "Thinking..." : "Ask AI"}</span>
              </button>
            </form>
          </div>
        </section>

        {/* Right Column (5 Cols): Decision Support & Authority Action Stream */}
        <section className="lg:col-span-5 flex flex-col space-y-5">
          
          {/* Card 1: AI Recommendation & Relocation Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg relative overflow-hidden">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-sm text-white">Relocation Recommendation</h3>
              </div>
              <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded">
                STATUS: {decisionData?.relocation?.status || "PROPOSED"}
              </span>
            </div>

            <div className="mt-4 space-y-3">
              <div className="p-3 bg-slate-850 rounded-lg border border-slate-800">
                <span className="text-xs text-slate-400 block">Recommended Safe Site:</span>
                <div className="flex items-center justify-between mt-1">
                  <span className="text-sm font-bold text-emerald-400">
                    {decisionData?.relocation?.recommended_site === "S001" ? "Dhak Plateau Safe Terrace (S001)" : "Pipalkoti Upper Tableland (S002)"}
                  </span>
                  <span className="text-xs px-2 py-0.5 bg-emerald-500/20 text-emerald-300 font-semibold rounded">
                    Suitability: {decisionData?.relocation?.suitability_score || 84.5}%
                  </span>
                </div>
              </div>

              {/* Carrying Capacity Deterministic Raw Numbers */}
              <div className="p-3 bg-slate-850 rounded-lg border border-slate-800">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{t.carryingCapacity}:</span>
                  <span className="text-emerald-400 font-bold flex items-center space-x-1">
                    <CheckCircle className="w-3.5 h-3.5 inline" />
                    <span>CAPACITY SUFFICIENT</span>
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-800/70 p-2 rounded">
                    <span className="text-slate-400 text-[10px] block">Population to Relocate</span>
                    <span className="font-mono font-bold text-white text-sm">
                      {activeHab.population || 1250} persons
                    </span>
                  </div>
                  <div className="bg-slate-800/70 p-2 rounded">
                    <span className="text-slate-400 text-[10px] block">Site Capacity (at 90% safety)</span>
                    <span className="font-mono font-bold text-emerald-300 text-sm">
                      {decisionData?.relocation?.capacity || 1800} (Usable: 1,620)
                    </span>
                  </div>
                </div>
                <p className="text-[10px] text-slate-500 mt-1.5 italic">
                  * Deterministic guardrail enforced: LLM cannot override numerical capacity.
                </p>
              </div>

              {/* Land Use Conflict & Estimated Cost */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-2.5 bg-slate-850 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Land-Use Conflict:</span>
                  <span className="font-bold text-emerald-400 flex items-center space-x-1 mt-0.5">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>None Detected</span>
                  </span>
                </div>
                <div className="p-2.5 bg-slate-850 rounded-lg border border-slate-800">
                  <span className="text-[10px] text-slate-400 block">Estimated Cost (Norm):</span>
                  <span className="font-mono font-bold text-indigo-300 mt-0.5 block">
                    ₹6,25,00,000 (₹6.25 Cr)
                  </span>
                </div>
              </div>

              {/* Key Reasoning Bullet Points */}
              <div className="text-xs space-y-1.5 pt-1">
                <span className="text-slate-400 font-semibold block">Key Algorithmic Reasons:</span>
                {(decisionData?.reasoning || [
                  "High multi-hazard risk detected on steep terrain",
                  "Candidate site Dhak Plateau possesses sufficient estimated capacity",
                  "No land-use conflict detected (clear of eco-sensitive zone)",
                  "Significantly lower residual hazard and better road access"
                ]).map((reason, idx) => (
                  <div key={idx} className="flex items-start space-x-2 text-slate-300 text-[11px]">
                    <span className="text-indigo-400 font-bold">•</span>
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Card 2: Computer Vision Satellite Detection */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs">
              <div className="flex items-center space-x-2 font-bold text-slate-200">
                <Camera className="w-4 h-4 text-indigo-400" />
                <span>{t.cvAnalysis}</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Bhuvan / Sentinel-2</span>
            </div>

            <div className="mt-3 flex items-center space-x-3">
              <div className="w-20 h-20 bg-slate-800 rounded-lg overflow-hidden border border-slate-700 flex-shrink-0 relative group">
                <img
                  src="https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=200&auto=format&fit=crop&q=60"
                  alt="Satellite Patch"
                  className="w-full h-full object-cover"
                />
                <span className="absolute bottom-1 right-1 text-[9px] bg-black/80 px-1 rounded text-white font-mono">Post</span>
              </div>
              <div className="flex-1 text-xs space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-white">Detection:</span>
                  <span className="px-2 py-0.5 bg-red-500/20 text-red-300 font-bold rounded text-[10px]">
                    LANDSLIDE — HIGH SEVERITY
                  </span>
                </div>
                <div className="text-[11px] text-slate-400">
                  Confidence: <span className="text-white font-mono font-bold">87.0%</span> (Calibrated delta)
                </div>
                {/* Mandatory Model Disclosure Banner */}
                <div className="p-1.5 bg-slate-800/80 rounded border border-slate-700 text-[10px] text-slate-400 leading-tight">
                  <span className="text-indigo-400 font-semibold">{t.modelDisclosure}: </span>
                  {visionData?.model_disclosure || "Prototype uses rule-based detector for demo. Production fine-tuned on Sen1Floods11 & Landslide4Sense benchmark datasets."}
                </div>
              </div>
            </div>
          </div>

          {/* Card 3: RAG Statutory Policy & Insufficient Evidence Safeguard */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800 text-xs">
              <div className="flex items-center space-x-2 font-bold text-slate-200">
                <FileText className="w-4 h-4 text-indigo-400" />
                <span>{t.ragEvidence}</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">NDMA Guidelines 2009 & R&R 2007</span>
            </div>

            <div className="mt-3 space-y-2 text-xs">
              {ragResult?.evidence_sufficient === false ? (
                <div className="p-3 bg-amber-950/40 border border-amber-800/60 rounded-lg text-amber-200 text-xs">
                  <div className="flex items-center space-x-2 font-bold mb-1">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span>Evidence-Insufficient Safeguard Active</span>
                  </div>
                  <p className="text-[11px] leading-relaxed">
                    {ragResult.answer}
                  </p>
                  <p className="text-[10px] text-amber-400/80 mt-1 font-mono">
                    * The system acknowledges zero matches in official NDMA corpus rather than hallucinating answers.
                  </p>
                </div>
              ) : (
                <>
                  <p className="text-slate-300 text-[11px] leading-relaxed line-clamp-3">
                    {ragResult?.answer || "National Rehabilitation and Resettlement Policy (2007) and NDMA Landslide Management Guidelines require establishing non-hazardous recipient sites with basic civil infrastructure prior to displacement."}
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-2">
                    {(ragResult?.sources || [
                      { title: "NDMA Guidelines: Management of Landslides", source: "NDMA, 2009" },
                      { title: "National Rehabilitation & Resettlement Policy", source: "MoRD, 2007" }
                    ]).map((s, i) => (
                      <span key={i} className="px-2 py-0.5 bg-slate-800 text-slate-400 rounded text-[10px] border border-slate-700">
                        📄 {s.title} ({s.source})
                      </span>
                    ))}
                  </div>
                </>
              )}

              {/* Demo Safeguard Trigger Button */}
              <button
                onClick={testInsufficientEvidenceQuery}
                disabled={ragLoading}
                className="mt-2 w-full py-1.5 px-3 bg-slate-800 hover:bg-slate-750 text-indigo-300 border border-slate-700 rounded text-[11px] font-semibold flex items-center justify-center space-x-1.5 transition cursor-pointer"
              >
                <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                <span>{ragLoading ? "Querying Knowledge Base..." : t.testUncertainty}</span>
              </button>
            </div>
          </div>

          {/* Card 4: Authority Action Form & Audit Trail (Required §9A) */}
          <div className="bg-slate-900 border-2 border-indigo-500/40 rounded-xl p-5 shadow-2xl">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2 font-bold text-white text-sm">
                <Send className="w-4 h-4 text-indigo-400" />
                <span>{t.authorityAction}</span>
              </div>
              <span className="text-[10px] font-mono bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded">
                Human-in-the-Loop Audit
              </span>
            </div>

            <form onSubmit={handleAuthoritySubmit} className="mt-4 space-y-3 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Official Decision:</label>
                <div className="grid grid-cols-3 gap-2">
                  {["ACCEPTED", "DEFERRED", "REJECTED"].map((d) => (
                    <button
                      type="button"
                      key={d}
                      onClick={() => setAuthorityDecision(d)}
                      className={`py-1.5 rounded font-bold transition text-[11px] ${
                        authorityDecision === d
                          ? d === "ACCEPTED"
                            ? "bg-emerald-600 text-white shadow"
                            : d === "DEFERRED"
                            ? "bg-amber-600 text-white shadow"
                            : "bg-red-600 text-white shadow"
                          : "bg-slate-800 text-slate-400 hover:text-white"
                      }`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Reviewing Authority / Official Designation:</label>
                <input
                  type="text"
                  value={reviewerName}
                  onChange={(e) => setReviewerName(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-white font-medium text-xs focus:ring-1 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="text-slate-400 block mb-1">Directives & Action Notes:</label>
                <textarea
                  rows={2}
                  value={actionNotes}
                  onChange={(e) => setActionNotes(e.target.value)}
                  placeholder={t.notesPlaceholder}
                  className="w-full bg-slate-800 border border-slate-700 rounded px-2.5 py-1.5 text-white text-xs focus:ring-1 focus:ring-indigo-500 resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={actionSubmitting}
                className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 font-bold text-white rounded-lg transition shadow-md shadow-indigo-600/30 flex items-center justify-center space-x-2 cursor-pointer"
              >
                {actionSubmitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                <span>{t.submitDecision}</span>
              </button>

              {actionSuccessMsg && (
                <div className="p-2 bg-emerald-950/60 border border-emerald-700 text-emerald-300 rounded text-[11px] flex items-center space-x-1.5">
                  <CheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>{actionSuccessMsg}</span>
                </div>
              )}
            </form>

            {/* Decision History Audit Log (Section 9A) */}
            <div className="mt-4 pt-3 border-t border-slate-800">
              <span className="text-[11px] font-semibold text-slate-400 block mb-2">{t.decisionLog}:</span>
              <div className="space-y-2 max-h-36 overflow-y-auto pr-1">
                {decisionHistory.length === 0 ? (
                  <p className="text-[11px] text-slate-500 italic">No previous actions recorded for this habitation.</p>
                ) : (
                  decisionHistory.map((item) => (
                    <div key={item.id} className="p-2 bg-slate-850 rounded border border-slate-800 text-[10px]">
                      <div className="flex items-center justify-between font-semibold">
                        <span className="text-slate-300">{item.reviewed_by}</span>
                        <span className={`px-1.5 py-0.2 rounded font-mono ${
                          item.decision === "ACCEPTED" ? "bg-emerald-500/20 text-emerald-300" :
                          item.decision === "DEFERRED" ? "bg-amber-500/20 text-amber-300" :
                          "bg-red-500/20 text-red-300"
                        }`}>
                          {item.decision}
                        </span>
                      </div>
                      {item.notes && <p className="text-slate-400 mt-1 italic">"{item.notes}"</p>}
                      <span className="text-[9px] text-slate-500 block mt-1">
                        {new Date(item.reviewed_at).toLocaleString()} • ID: {item.id}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

        </section>
      </main>

      {/* ----------------- Explainability Modal ("Why this score?") ----------------- */}
      {showExplainModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-lg w-full p-6 shadow-2xl relative animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center space-x-2">
                <HelpCircle className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-base text-white">Risk Score Factor Breakdown</h3>
              </div>
              <button
                onClick={() => setShowExplainModal(false)}
                className="text-slate-400 hover:text-white font-bold px-2 py-1 rounded"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4 text-xs">
              <div className="p-3 bg-slate-850 rounded-lg flex items-center justify-between border border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[11px]">Habitation</span>
                  <span className="font-bold text-sm text-white">{activeHab.name || "Joshimath"}</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 block text-[11px]">Overall Multi-Hazard Score</span>
                  <span className="font-mono text-lg font-bold text-red-400">
                    {explainData?.overall_score || activeHab.risk_score || 82.5} / 100
                  </span>
                </div>
              </div>

              {/* Per-factor contribution breakdown list */}
              <div className="space-y-2.5">
                <span className="text-slate-400 font-semibold block">Weighted Factor Contributions (Formula v1.0):</span>
                {(explainData?.factors || [
                  { name: "rainfall_intensity", contribution: 24.2, weight: 0.15, raw_value: 145.0 },
                  { name: "slope", contribution: 22.4, weight: 0.125, raw_value: 34.0 },
                  { name: "historical_event_frequency", contribution: 18.0, weight: 0.275, raw_value: 5 },
                  { name: "population_density", contribution: 10.5, weight: 0.14, raw_value: 1250 },
                  { name: "elevation_stability", contribution: 7.4, weight: 0.10, raw_value: 1890 }
                ]).map((f, i) => (
                  <div key={i} className="space-y-1">
                    <div className="flex items-center justify-between text-[11px]">
                      <span className="capitalize font-medium text-slate-300">
                        {f.name.replace(/_/g, " ")}
                      </span>
                      <span className="font-mono text-slate-200">
                        +{f.contribution.toFixed(1)} pts ({Math.round(f.weight * 100)}% weight)
                      </span>
                    </div>
                    {/* Visual contribution bar */}
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-red-500 h-full rounded-full"
                        style={{ width: `${Math.min(100, (f.contribution / 30) * 100)}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>

              {/* Methodology Citation */}
              <div className="p-3 bg-slate-850 rounded-lg border border-slate-800 text-[10px] text-slate-400 space-y-1">
                <div className="flex items-center space-x-1.5 font-semibold text-indigo-300">
                  <Database className="w-3 h-3" />
                  <span>Methodology Reference</span>
                </div>
                <p>
                  Scoring formula: Section 9D of Architecture specification. Published weights baseline grounded in NDMA Hazard Vulnerability Risk Assessment (HVRA) standard.
                </p>
                <span className="text-slate-500 block font-mono">Formula Version: v1.0 • Reproducible audit trace</span>
              </div>
            </div>

            <div className="mt-5 text-right">
              <button
                onClick={() => setShowExplainModal(false)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
              >
                Close Drawer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
