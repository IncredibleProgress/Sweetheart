// src/LineChart.tsx

import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface LineChartProps {
  data: { date: string; value: number }[];
  width: number;
  height: number;
}

const LineChart: React.FC<LineChartProps> = ({ data, width, height }) => {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg.selectAll('*').remove(); // Clear previous content

      const margin = { top: 20, right: 30, bottom: 30, left: 40 };
      const chartWidth = width - margin.left - margin.right;
      const chartHeight = height - margin.top - margin.bottom;

      const parseDate = d3.timeParse('%Y-%m-%d');

      const x = d3.scaleTime()
        .domain(d3.extent(data, d => parseDate(d.date) as Date) as [Date, Date])
        .range([0, chartWidth]);

      const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value) as number])
        // .domain([500, 1500])
        .nice()
        .range([chartHeight, 0]);

      const line = d3.line<{ date: string; value: number }>()
        .x(d => x(parseDate(d.date) as Date) as number)
        .y(d => y(d.value));

      const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      g.append('g')
        .attr('transform', `translate(0,${chartHeight})`)
        .call(d3.axisBottom(x));

      g.append('g')
        .call(d3.axisLeft(y).ticks(5));

      g.append('path')
        .datum(data)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 1.5)
        .attr('d', line);
    }
  }, [data, height, width]);

  return (
    <svg ref={svgRef} width={width} height={height} />
  );
};

export default LineChart;
