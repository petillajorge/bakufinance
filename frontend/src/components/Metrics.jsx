import React from 'react';
import { ArrowUp, ArrowDown, Activity } from 'lucide-react';

export const Metrics = ({ ticker, price, change, volume, type }) => {
    const isPositive = change >= 0;
    const colorClass = isPositive ? 'text-[#00ff9d]' : 'text-[#ff3d71]';

    return (
        <div className="flex flex-col md:flex-row items-start md:items-end justify-between w-full mb-8 z-10 relative">
            <div>
                <div className="flex items-center gap-3 mb-1">
                    <h2 className="text-5xl md:text-6xl font-black tracking-tighter text-white">
                        {ticker}
                    </h2>
                    <span className="text-xs font-bold tracking-widest px-2 py-0.5 rounded-full bg-white/10 text-gray-400 border border-white/5 backdrop-blur-md">
                        {type ? type.toUpperCase() : 'ASSET'}
                    </span>
                </div>

                <div className="flex items-baseline gap-4 mt-2">
                    <span className="text-6xl md:text-8xl font-mono font-medium text-white tracking-tighter drop-shadow-[0_0_15px_rgba(255,255,255,0.1)]">
                        ${price ? price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}
                    </span>
                </div>

                <div className={`flex items-center gap-2 text-2xl md:text-3xl font-bold ${colorClass} mt-2 animate-in slide-in-from-left-2 duration-500`}>
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full ${isPositive ? 'bg-[#00ff9d]/20' : 'bg-[#ff3d71]/20'}`}>
                        {isPositive ? <ArrowUp size={20} /> : <ArrowDown size={20} />}
                    </div>
                    <span>{change ? Math.abs(change).toFixed(2) : '0.00'}%</span>
                    <span className="text-sm text-gray-500 font-normal ml-2">Today</span>
                </div>
            </div>

            <div className="flex flex-col gap-2 mt-6 md:mt-0 text-right">
                <div className="glass-card px-6 py-3 flex items-center gap-4 border-l-4 border-l-blue-500">
                    <div className="flex flex-col items-end">
                        <span className="text-gray-400 text-xs font-bold tracking-widest uppercase mb-1">24h Volume</span>
                        <span className="font-mono text-xl text-white font-bold">
                            {volume ? volume.toLocaleString(undefined, { maximumFractionDigits: 0 }) : '--'}
                        </span>
                    </div>
                    <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center text-blue-400">
                        <Activity size={20} />
                    </div>
                </div>
            </div>
        </div>
    );
};
