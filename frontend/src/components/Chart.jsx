import { createChart, ColorType, AreaSeries, HistogramSeries } from 'lightweight-charts';
import React, { useEffect, useRef } from 'react';

export const Chart = ({ data, color = '#00ff9d', timeRange }) => {
  const chartContainerRef = useRef();
  const chartRef = useRef();
  const seriesRef = useRef();
  const markersRef = useRef();

  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
      const chart = createChart(chartContainerRef.current, {
        layout: {
          background: { type: ColorType.Solid, color: 'transparent' },
          textColor: '#a0a0a0',
          fontFamily: 'Rajdhani, sans-serif',
        },
        grid: {
          vertLines: { visible: false },
          horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
        },
        width: chartContainerRef.current.clientWidth,
        height: chartContainerRef.current.clientHeight || 400,
        timeScale: {
          timeVisible: true,
          secondsVisible: true,
          borderColor: 'rgba(255, 255, 255, 0.1)',
        },
        rightPriceScale: {
          borderColor: 'rgba(255, 255, 255, 0.1)',
        },
      });

      const series = chart.addSeries(AreaSeries, {
        lineColor: color,
        topColor: 'rgba(0, 255, 157, 0.4)',
        bottomColor: 'rgba(0, 255, 157, 0.0)',
        lineWidth: 2,
      });

      // Markers Series (Histogram for vertical lines)
      const markersSeries = chart.addSeries(HistogramSeries, {
        color: 'rgba(255, 255, 255, 0.15)', // Visible vertical line color
        priceScaleId: 'overlay', // Separate scale
        priceFormat: { type: 'custom', formatter: () => '' },
      });

      chart.priceScale('overlay').applyOptions({
        scaleMargins: { top: 0, bottom: 0 },
        visible: false
      });

      chartRef.current = chart;
      seriesRef.current = series;
      markersRef.current = markersSeries;

      const resizeObserver = new ResizeObserver(entries => {
        if (entries.length === 0 || !entries[0].target) return;
        const newRect = entries[0].contentRect;
        chart.applyOptions({ width: newRect.width, height: newRect.height });
      });

      resizeObserver.observe(chartContainerRef.current);

      return () => {
        resizeObserver.disconnect();
        chart.remove();
      };
    } catch (e) {
      console.error("Failed to create chart:", e);
    }
  }, []);

  // Update data + Markers logic
  useEffect(() => {
    if (seriesRef.current && data && data.length > 0) {
      try {
        const uniqueData = [];
        const seenTimes = new Set();
        const sortedData = [...data].sort((a, b) => a.time - b.time);

        for (const item of sortedData) {
          if (!seenTimes.has(item.time)) {
            uniqueData.push(item);
            seenTimes.add(item.time);
          }
        }

        seriesRef.current.setData(uniqueData);

        // Vertical Lines Generation
        if (markersRef.current) {
          if (timeRange === '1s' || timeRange === '15m' || timeRange === '1H') {
            const markerData = [];
            const seenMinutes = new Set();

            for (const d of uniqueData) {
              const date = new Date(d.time * 1000);
              const minutes = date.getMinutes();
              const seconds = date.getSeconds();

              // Logic: Mark XX:00, XX:15, XX:30, XX:45
              // We need to find points where minutes % 15 == 0.
              // To avoid thick bars (multiple ticks in same minute), we ensure we only mark once per minute-block.

              if (minutes % 15 === 0) {
                // Create unique key for this specific 15-min interval (e.g. "12:15")
                const key = `${date.getHours()}:${minutes}`;

                // If we haven't marked this interval yet, add a marker
                if (!seenMinutes.has(key)) {
                  markerData.push({ time: d.time, value: 1 });
                  seenMinutes.add(key);
                }
              }
            }
            markersRef.current.setData(markerData);
          } else {
            markersRef.current.setData([]);
          }
        }

      } catch (err) {
        console.error("Error setting chart data:", err);
      }
    }
  }, [data, timeRange]);

  useEffect(() => {
    if (seriesRef.current) {
      const r = parseInt(color.slice(1, 3), 16) || 0;
      const g = parseInt(color.slice(3, 5), 16) || 0;
      const b = parseInt(color.slice(5, 7), 16) || 0;

      seriesRef.current.applyOptions({
        lineColor: color,
        topColor: `rgba(${r}, ${g}, ${b}, 0.4)`,
        bottomColor: `rgba(${r}, ${g}, ${b}, 0.0)`,
      });
    }
  }, [color]);

  return <div ref={chartContainerRef} className="w-full h-full" />;
};
