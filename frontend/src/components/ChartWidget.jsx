import React, { useState, useEffect, useRef } from 'react';
import { Chart } from './Chart';
import { ArrowUp, ArrowDown, X, Clock, Activity, Maximize2 } from 'lucide-react';

export const ChartWidget = ({ id, ticker, onClose }) => {
    const [timeRange, setTimeRange] = useState('1D');
    const [currentPrice, setCurrentPrice] = useState(null);
    const [data, setData] = useState([]);
    const [status, setStatus] = useState('connecting');
    const ws = useRef(null);

    // Fetch History
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                let period = '1d';
                let interval = '5m';

                switch (timeRange) {
                    case '1s': period = '1d'; interval = '1m'; break; // 1s not supported by API history, relying on ticks
                    case '15m': period = '1d'; interval = '5m'; break;
                    case '1H': period = '1h'; interval = '1m'; break;
                    case '1D': period = '1d'; interval = '5m'; break;
                    case '1W': period = '5d'; interval = '1d'; break;
                    case '1M': period = '1mo'; interval = '1d'; break;
                    case '1Y': period = '1y'; interval = '1d'; break;
                    default: period = '1d'; interval = '5m';
                }

                // Encode ticker (e.g., BTC/USDT -> BTC%2FUSDT)
                const encodedTicker = ticker.replace('/', '%2F');
                const res = await fetch(`http://localhost:8000/history/${encodedTicker}?period=${period}&interval=${interval}`);
                const history = await res.json();

                if (Array.isArray(history)) {
                    history.sort((a, b) => a.time - b.time);
                    setData(history);
                }
            } catch (e) {
                console.error("Failed to fetch history:", e);
                // Don't clear data immediately if error, keeps old cache potentially
            }
        };

        fetchHistory();

        // Re-establish WS on ticker change or just init
        if (ws.current) ws.current.close();

        const socket = new WebSocket(`ws://127.0.0.1:8000/ws/${ticker}`);
        ws.current = socket;

        socket.onopen = () => setStatus('connected');

        socket.onmessage = (event) => {
            const message = JSON.parse(event.data);
            setCurrentPrice(message);

            setData((prev) => {
                const newPoint = {
                    time: message.timestamp / 1000,
                    value: message.price
                };
                // Append and slice
                const newData = [...prev, newPoint];
                // Keep performance sane
                if (newData.length > 3000) return newData.slice(-3000);
                return newData;
            });
        };

        socket.onclose = () => setStatus('disconnected');

        return () => socket.close();
    }, [ticker, timeRange]);


    // Metrics Display Logic
    const isPositive = currentPrice?.change >= 0;
    const priceColor = isPositive ? 'text-[#00ff9d]' : 'text-[#ff3d71]';
    const chartColor = isPositive ? '#00ff9d' : '#ff3d71';

    return (
        <div className={`liquid-card p-6 flex flex-col relative group animate-in zoom-in-95 duration-500 h-full min-h-[300px] min-w-0 border-2 transition-all ${isPositive ? 'border-green-500/30 bg-gradient-to-br from-green-500/5 to-transparent' : 'border-red-500/30 bg-gradient-to-br from-red-500/5 to-transparent'}`}>
            {/* Header / Overlay */}
            <div className="flex justify-between items-start mb-2 relative z-10">
                <div>
                    <div className="flex items-center gap-2">
                        <h3 className="text-2xl font-bold tracking-widest text-white">{ticker}</h3>
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full border border-white/10 ${status === 'connected' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                            {status === 'connected' ? 'LIVE' : 'OFFLINE'}
                        </span>
                    </div>

                    {currentPrice ? (
                        <div className="flex items-baseline gap-4 mt-2">
                            <span className={`text-4xl md:text-5xl font-mono font-black tracking-tighter ${priceColor} drop-shadow-[0_0_10px_rgba(0,0,0,0.5)]`}>
                                ${currentPrice.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                            <div className={`flex items-center text-lg font-bold px-3 py-1 rounded-full bg-black/40 backdrop-blur-md border border-white/5 ${priceColor}`}>
                                {isPositive ? <ArrowUp size={20} strokeWidth={3} /> : <ArrowDown size={20} strokeWidth={3} />}
                                {Math.abs(currentPrice.change).toFixed(2)}%
                            </div>
                        </div>
                    ) : (
                        <div className="h-10 w-32 bg-white/5 animate-pulse rounded mt-1"></div>
                    )}
                </div>

                <div className="flex gap-2">
                    <button
                        onClick={() => onClose && onClose(id)}
                        className="p-1.5 rounded-lg hover:bg-white/10 text-gray-500 hover:text-white transition-colors"
                    >
                        <X size={16} />
                    </button>
                </div>
            </div>

            {/* Chart */}
            <div className="flex-1 relative w-full min-h-0">
                <div className="absolute inset-0 top-4 bottom-8">
                    <Chart data={data} color={currentPrice ? chartColor : '#22c55e'} timeRange={timeRange} />
                </div>
            </div>

            {/* Controls */}
            <div className="mt-2 flex justify-end gap-1 relative z-10">
                {['1s', '15m', '1H', '1D', '1W', '1M', '1Y'].map(tf => (
                    <button
                        key={tf}
                        onClick={() => setTimeRange(tf)}
                        className={`text-[10px] font-bold px-2 py-1 rounded backdrop-blur-sm transition-all ${timeRange === tf
                            ? 'bg-white text-black shadow-[0_0_10px_rgba(255,255,255,0.5)]'
                            : 'bg-black/20 text-gray-400 hover:bg-white/10 hover:text-white'}`}
                    >
                        {tf}
                    </button>
                ))}
            </div>
        </div>
    );
};
