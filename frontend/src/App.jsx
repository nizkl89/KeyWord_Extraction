const App = () => {
  const [text, setText] = React.useState('');
  const [file, setFile] = React.useState(null);
  const [keywords, setKeywords] = React.useState([]);
  const [error, setError] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [showProbabilities, setShowProbabilities] = React.useState(false);

  const handleTextSubmit = async () => {
    setLoading(true);
    setError('');
    setKeywords([]);
    try {
      const response = await fetch('http://localhost:5001/extract_keywords', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setKeywords(data.keywords);
      }
    } catch (err) {
      setError('Failed to connect to the server. Ensure the backend is running.');
    }
    setLoading(false);
  };

  const handleFileSubmit = async () => {
    if (!file) {
      setError('Please select a .txt file.');
      return;
    }
    setLoading(true);
    setError('');
    setKeywords([]);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('http://backend:5001/extract_keywords', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      if (data.error) {
        setError(data.error);
      } else {
        setKeywords(data.keywords);
      }
    } catch (err) {
      setError('Failed to connect to the server or invalid file format.');
    }
    setLoading(false);
    setFile(null);
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'text/plain') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a valid .txt file.');
      setFile(null);
    }
    e.target.value = null;
  };

  const toggleProbabilities = () => {
    setShowProbabilities(!showProbabilities);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-100 to-pink-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-3xl transform transition-all hover:shadow-2xl">
        <h1 className="text-3xl font-bold mb-6 text-center text-gray-800">Keyword Extraction System</h1>

        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Extract from Text</h2>
          <textarea
            className="w-full p-4 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-gray-700 placeholder-gray-400"
            rows="6"
            placeholder="Enter your text here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          ></textarea>
          <div className="flex justify-center">
            <button
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition-colors font-semibold"
              onClick={handleTextSubmit}
              disabled={loading || !text.trim()}
            >
              {loading ? 'Extracting...' : 'Extract Keywords'}
            </button>
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Extract from File</h2>
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center w-full p-4 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 transition-colors">
              <span className="text-gray-600">Upload a .txt file</span>
              <input
                type="file"
                accept=".txt"
                className="hidden"
                onChange={handleFileChange}
              />
              {file && <span className="text-blue-600 mt-2">{file.name}</span>}
            </label>
          </div>
          <div className="flex justify-center mt-4">
            <button
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition-colors font-semibold"
              onClick={handleFileSubmit}
              disabled={loading || !file}
            >
              {loading ? 'Extracting...' : 'Extract from File'}
            </button>
          </div>
        </div>

        {error && (
          <p className="text-red-500 text-center mb-4 bg-red-50 p-3 rounded-lg">{error}</p>
        )}
        {keywords.length > 0 && (
          <div className="mt-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800">Extracted Keywords</h2>
              <button
                className="text-blue-600 hover:text-blue-800 text-sm font-medium transition-colors underline"
                onClick={toggleProbabilities}
              >
                Toggle Scores
              </button>
            </div>
            <div className="flex flex-wrap gap-3">
              {keywords.map((kw, index) => (
                <div
                  key={index}
                  className="relative bg-blue-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium transition-transform transform hover:scale-105 group"
                >
                  {kw.keyword}
                  <span
                    className="absolute bottom-full mb-2 hidden group-hover:block bg-gray-800 text-white text-xs rounded px-2 py-1 z-10"
                  >
                    Score: {kw.score.toFixed(4)}
                  </span>
                  {showProbabilities && (
                    <span className="ml-2 text-xs text-blue-600">
                      ({kw.score.toFixed(4)})
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);