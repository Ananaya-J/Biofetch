import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";

// Import UI components
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { CheckCircle, XCircle, Clock, Download, Database, Activity, FileText, Beaker } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://biofetch-backend:8001';
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [databases, setDatabases] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);

  const [singleForm, setSingleForm] = useState({
    accession_id: '',
    database: '',
    validate_format: true
  });

  const [batchForm, setBatchForm] = useState({
    accession_ids: '',
    database: '',
    validate_format: true
  });

  useEffect(() => {
    loadDatabases();
    loadJobs();
    loadStats();
    
    const interval = setInterval(() => {
      loadJobs();
      loadStats();
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const loadDatabases = async () => {
    try {
      const response = await axios.get(`${API}/databases`);
      setDatabases(response.data);
    } catch (error) {
      console.error('Failed to load databases:', error);
    }
  };

  const loadJobs = async () => {
    try {
      const response = await axios.get(`${API}/jobs?limit=20`);
      setJobs(response.data);
    } catch (error) {
      console.error('Failed to load jobs:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleSingleDownload = async () => {
    if (!singleForm.accession_id || !singleForm.database) return;
    
    setLoading(true);
    try {
      await axios.post(`${API}/download`, singleForm);
      setSingleForm({ accession_id: '', database: '', validate_format: true });
      loadJobs();
    } catch (error) {
      console.error('Download failed:', error);
      alert('Download failed: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const handleBatchDownload = async () => {
    if (!batchForm.accession_ids || !batchForm.database) return;
    
    setLoading(true);
    try {
      const accession_ids = batchForm.accession_ids
        .split('\n')
        .map(id => id.trim())
        .filter(id => id.length > 0);
      
      await axios.post(`${API}/batch-download`, {
        ...batchForm,
        accession_ids
      });
      
      setBatchForm({ accession_ids: '', database: '', validate_format: true });
      loadJobs();
    } catch (error) {
      console.error('Batch download failed:', error);
      alert('Batch download failed: ' + (error.response?.data?.detail || error.message));
    }
    setLoading(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'downloading':
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return 'N/A';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Beaker className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">BioFetch</h1>
              <p className="text-gray-600">Unified Bioinformatics Data Downloader</p>
            </div>
          </div>
          
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Download className="h-5 w-5 text-blue-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Total Downloads</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.total_downloads || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Completed</p>
                    <p className="text-2xl font-bold text-gray-900">{stats.completed_downloads || 0}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-orange-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Success Rate</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stats.success_rate ? `${(stats.success_rate * 100).toFixed(1)}%` : '0%'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-purple-600" />
                  <div>
                    <p className="text-sm font-medium text-gray-600">Databases</p>
                    <p className="text-2xl font-bold text-gray-900">{databases.length}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="download" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="download">Download</TabsTrigger>
            <TabsTrigger value="jobs">Jobs</TabsTrigger>
            <TabsTrigger value="databases">Databases</TabsTrigger>
          </TabsList>

          {/* Download Tab */}
          <TabsContent value="download" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Single Download */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Download className="h-5 w-5" />
                    Single Download
                  </CardTitle>
                  <CardDescription>
                    Download a single biological data file by accession ID
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="single-accession">Accession ID</Label>
                    <Input
                      id="single-accession"
                      placeholder="e.g., SRR000001, NC_045512"
                      value={singleForm.accession_id}
                      onChange={(e) => setSingleForm({...singleForm, accession_id: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="single-database">Database</Label>
                    <Select 
                      value={singleForm.database}
                      onValueChange={(value) => setSingleForm({...singleForm, database: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select database" />
                      </SelectTrigger>
                      <SelectContent>
                        {databases.map((db) => (
                          <SelectItem key={db.id} value={db.id}>
                            {db.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <Button 
                    onClick={handleSingleDownload} 
                    disabled={loading || !singleForm.accession_id || !singleForm.database}
                    className="w-full"
                  >
                    {loading ? 'Starting Download...' : 'Download'}
                  </Button>
                </CardContent>
              </Card>

              {/* Batch Download */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Batch Download
                  </CardTitle>
                  <CardDescription>
                    Download multiple files by providing a list of accession IDs
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="batch-accessions">Accession IDs (one per line)</Label>
                    <Textarea
                      id="batch-accessions"
                      placeholder="SRR000001\nSRR000002\nSRR000003"
                      rows={4}
                      value={batchForm.accession_ids}
                      onChange={(e) => setBatchForm({...batchForm, accession_ids: e.target.value})}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="batch-database">Database</Label>
                    <Select 
                      value={batchForm.database}
                      onValueChange={(value) => setBatchForm({...batchForm, database: value})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select database" />
                      </SelectTrigger>
                      <SelectContent>
                        {databases.map((db) => (
                          <SelectItem key={db.id} value={db.id}>
                            {db.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <Button 
                    onClick={handleBatchDownload} 
                    disabled={loading || !batchForm.accession_ids || !batchForm.database}
                    className="w-full"
                  >
                    {loading ? 'Starting Batch Download...' : 'Batch Download'}
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Jobs Tab */}
          <TabsContent value="jobs">
            <Card>
              <CardHeader>
                <CardTitle>Download Jobs</CardTitle>
                <CardDescription>
                  Monitor your download progress and access completed files
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {jobs.length === 0 ? (
                    <Alert>
                      <AlertDescription>
                        No download jobs found. Start a download to see it here.
                      </AlertDescription>
                    </Alert>
                  ) : (
                    jobs.map((job) => (
                      <div key={job.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            {getStatusIcon(job.status)}
                            <div>
                              <p className="font-medium">{job.accession_id}</p>
                              <p className="text-sm text-gray-500">
                                {databases.find(db => db.id === job.database)?.name || job.database}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant={job.status === 'completed' ? 'default' : job.status === 'failed' ? 'destructive' : 'secondary'}>
                              {job.status}
                            </Badge>
                            {job.status === 'completed' && job.download_url && (
                              <Button 
                                size="sm" 
                                onClick={() => window.open(`${BACKEND_URL}${job.download_url}`, '_blank')}
                              >
                                Download File
                              </Button>
                            )}
                          </div>
                        </div>
                        
                        {job.status === 'downloading' && (
                          <div className="space-y-2">
                            <Progress value={job.progress * 100} className="h-2" />
                            <p className="text-sm text-gray-500">
                              {(job.progress * 100).toFixed(1)}% complete
                            </p>
                          </div>
                        )}
                        
                        <div className="flex justify-between text-sm text-gray-500">
                          <span>Size: {formatFileSize(job.file_size)}</span>
                          <span>
                            Created: {new Date(job.created_at).toLocaleString()}
                          </span>
                        </div>
                        
                        {job.error_message && (
                          <Alert variant="destructive">
                            <AlertDescription>{job.error_message}</AlertDescription>
                          </Alert>
                        )}
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Databases Tab */}
          <TabsContent value="databases">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {databases.map((db) => (
                <Card key={db.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Database className="h-5 w-5" />
                      {db.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm font-medium text-gray-600 mb-2">Example IDs:</p>
                      <div className="flex flex-wrap gap-1">
                        {db.example_ids.map((id) => (
                          <Badge key={id} variant="outline" className="text-xs">
                            {id}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    
                    {db.validation_prefixes.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-600 mb-2">Valid Prefixes:</p>
                        <div className="flex flex-wrap gap-1">
                          {db.validation_prefixes.map((prefix) => (
                            <Badge key={prefix} variant="secondary" className="text-xs">
                              {prefix}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <div className="pt-2 border-t">
                      <p className="text-sm text-gray-600">
                        Total Downloads: <span className="font-medium">{db.total_downloads}</span>
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App
