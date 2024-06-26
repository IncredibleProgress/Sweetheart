import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface BarChartProps {
  data: { name: string; value: number }[];
}

const BarChart: React.FC<BarChartProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (svgRef.current) {
      // Set the dimensions and margins of the graph
      const margin = { top: 20, right: 30, bottom: 40, left: 40 };
      const width = 600 - margin.left - margin.right;
      const height = 148 - margin.top - margin.bottom;

      // Append the svg object to the body of the page
      const svg = d3
        .select(svgRef.current)
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

      // X axis
      const x = d3
        .scaleBand()
        .range([0, width])
        .domain(data.map(d => d.name))
        .padding(0.1);

      svg
        .append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));

      // Y axis
      const y = d3.scaleLinear().domain([0, d3.max(data, d => d.value)!]).range([height, 0]);

      svg.append('g').call(d3.axisLeft(y));

      // Bars
      svg
        .selectAll('bars')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => x(d.name)!)
        .attr('y', d => y(d.value))
        .attr('width', x.bandwidth())
        .attr('height', d => height - y(d.value))
        .attr('fill', '#69b3a2');
    }
  }, [data]);

  return <svg ref={svgRef}></svg>;
};

export default BarChart;
