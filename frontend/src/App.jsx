import React, { useState, useEffect } from 'react';
import { ChartWidget } from './components/ChartWidget';
import { Search, Plus, Zap } from 'lucide-react';

function App() {
  const [charts, setCharts] = useState([
    { id: 1, ticker: 'BTC/USDT' }
  ]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Autocomplete
  useEffect(() => {
    const delayDebounceFn = setTimeout(async () => {
      if (searchQuery.length > 1) {
        try {
          const res = await fetch(`http://localhost:8000/search?q=${searchQuery}`);
          const suggestions = await res.json();
          setSearchResults(suggestions);
          setShowSuggestions(true);
        } catch (e) {
          console.error("Search failed", e);
        }
      } else {
        setSearchResults([]);
        setShowSuggestions(false);
      }
    }, 300);

    return () => clearTimeout(delayDebounceFn);
  }, [searchQuery]);

  const addChart = (ticker) => {
    if (charts.length >= 9) {
      alert("Maximum 9 charts allowed.");
      return;
    }
    const newId = Math.max(...charts.map(c => c.id), 0) + 1;
    setCharts([...charts, { id: newId, ticker }]);
    setSearchQuery('');
    setShowSuggestions(false);
  };

  const removeChart = (id) => {
    setCharts(charts.filter(c => c.id !== id));
  };

  const getGridClass = () => {
    const count = charts.length;
    if (count <= 1) return 'grid-cols-1';
    if (count === 2) return 'grid-cols-2';
    if (count === 3) return 'grid-cols-3';
    if (count === 4) return 'grid-cols-2';
    return 'grid-cols-3';
  };

  return (
    <div className="w-full h-screen flex flex-col p-[2.5%] gap-6 overflow-hidden">
      {/* Header & Global Search */}
      <header className="flex flex-row items-center justify-between gap-6 animate-in fade-in slide-in-from-top-4 duration-700">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-tr from-green-400 to-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/20">
            <Zap size={28} className="text-black fill-current" />
          </div>
          <div className="flex flex-col justify-center">
            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-br from-white to-gray-400 bg-clip-text text-transparent leading-none">
              BakuFinances
            </h1>
            <p className="text-xs text-gray-500 tracking-[0.2em] font-mono mt-1">LIQUID MARKET TERMINAL</p>
          </div>
        </div>

        {/* Search Bar (Add Chart) */}
        <div className="relative w-full md:w-96 z-50">
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-green-400 transition-colors" size={18} />
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full liquid-input rounded-full py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-green-500/20"
              placeholder="Search asset to ADD..."
            />
          </div>

          {/* Suggestions */}
          {showSuggestions && searchResults.length > 0 && (
            <div className="absolute top-full mt-2 w-full bg-[#0a0a0a]/90 backdrop-blur-xl border border-white/10 rounded-xl shadow-2xl overflow-hidden max-h-80 overflow-y-auto z-50">
              {searchResults.map((item) => (
                <button
                  key={item.symbol}
                  onClick={() => addChart(item.symbol)}
                  className="w-full text-left px-4 py-3 hover:bg-white/5 flex items-center justify-between group transition-colors border-b border-white/5 last:border-0"
                >
                  <span className="font-bold text-white group-hover:text-green-400 font-mono">{item.symbol}</span>
                  <span className="text-xs text-gray-500">{item.name}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </header>

      {/* Grid Content */}
      <main className={`grid ${getGridClass()} auto-rows-fr gap-4 flex-1 h-full min-h-0 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-200`}>
        {charts.map((chart) => (
          <ChartWidget
            key={chart.id}
            id={chart.id}
            ticker={chart.ticker}
            onClose={removeChart}
          />
        ))}
      </main>
    </div>
  );
}

export default App;
