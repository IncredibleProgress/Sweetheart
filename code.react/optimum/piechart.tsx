import React, { useRef, useEffect } from 'react';
import * as d3 from 'd3';

interface PieChartProps {
  data: { name: string; value: number }[];
}

const PieChart: React.FC<PieChartProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (svgRef.current) {
      // Set the dimensions and margins of the graph
      const width = 450;
      const height = 450;
      const margin = 40;

      // The radius of the pie chart is half the smallest side
      const radius = Math.min(width, height) / 2 - margin;

      // Append the svg object to the div called 'my_dataviz'
      const svg = d3
        .select(svgRef.current)
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${width / 2},${height / 2})`);

      // Set the color scale
      const color = d3.scaleOrdinal()
        .domain(data.map(d => d.name))
        .range(d3.schemeCategory10);

      // Compute the position of each group on the pie
      const pie = d3.pie<{ name: string; value: number }>()
        .value(d => d.value);

      const data_ready = pie(data);

      // Build the pie chart
      svg
        .selectAll('whatever')
        .data(data_ready)
        .enter()
        .append('path')
        .attr('d', d3.arc<any>()
          .innerRadius(0)
          .outerRadius(radius)
        )
        .attr('fill', d => color(d.data.name))
        .attr("stroke", "white")
        .style("stroke-width", "2px")
        .style("opacity", 0.7);

      // Add labels
      svg
        .selectAll('whatever')
        .data(data_ready)
        .enter()
        .append('text')
        .text(d => d.data.name)
        .attr("transform", d => {
          const _d = d3.arc<any>()
            .innerRadius(0)
            .outerRadius(radius).centroid(d);
          return `translate(${_d})`;
        })
        .style("text-anchor", "middle")
        .style("font-size", 15);
    }
  }, [data]);

  return <svg ref={svgRef}></svg>;
};

export default PieChart;
