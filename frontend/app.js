class GDPFertilityVisualization {
    constructor() {
        this.data = null;
        this.countries = [];
        this.currentYear = 2020;
        this.isPlaying = false;
        this.playInterval = null;
        
        this.margin = { top: 20, right: 100, bottom: 60, left: 80 };
        this.width = 900 - this.margin.left - this.margin.right;
        this.height = 600 - this.margin.top - this.margin.bottom;
        
        this.svg = null;
        this.g = null;
        this.xScale = null;
        this.yScale = null;
        this.colorScale = null;
        
        this.init();
    }
    
    async init() {
        await this.fetchData();
        this.setupSVG();
        this.setupScales();
        this.setupAxes();
        this.setupControls();
        this.populateCountrySelect();
        this.updateVisualization();
    }
    
    async fetchData() {
        try {
            const response = await axios.get('http://localhost:5000/data');
            this.data = response.data;
            
            const countriesResponse = await axios.get('http://localhost:5000/countries');
            this.countries = countriesResponse.data.countries;
            
            console.log('Data loaded successfully');
        } catch (error) {
            console.error('Error fetching data:', error);
            this.showError('Failed to load data. Please ensure the backend is running.');
        }
    }
    
    setupSVG() {
        this.svg = d3.select('#scatter-plot')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom);
        
        this.g = this.svg.append('g')
            .attr('transform', `translate(${this.margin.left},${this.margin.top})`);
    }
    
    setupScales() {
        const gdpExtent = this.getGDPExtent();
        const fertilityExtent = this.getFertilityExtent();
        
        this.xScale = d3.scaleLog()
            .domain([Math.max(gdpExtent[0], 100), gdpExtent[1]])
            .range([0, this.width])
            .nice();
        
        this.yScale = d3.scaleLinear()
            .domain(fertilityExtent)
            .range([this.height, 0])
            .nice();
        
        this.colorScale = d3.scaleOrdinal(d3.schemeCategory10);
    }
    
    getGDPExtent() {
        let min = Infinity, max = -Infinity;
        
        if (!this.data) return [100, 100000];
        
        for (const country in this.data.countries) {
            const gdpData = this.data.countries[country].gdp;
            for (const year in gdpData) {
                const value = gdpData[year];
                if (value && value > 0) {
                    min = Math.min(min, value);
                    max = Math.max(max, value);
                }
            }
        }
        
        return min === Infinity ? [100, 100000] : [min, max];
    }
    
    getFertilityExtent() {
        let min = Infinity, max = -Infinity;
        
        if (!this.data) return [0, 8];
        
        for (const country in this.data.countries) {
            const fertilityData = this.data.countries[country].fertility;
            for (const year in fertilityData) {
                const value = fertilityData[year];
                if (value && value > 0) {
                    min = Math.min(min, value);
                    max = Math.max(max, value);
                }
            }
        }
        
        return min === Infinity ? [0, 8] : [min, max];
    }
    
    setupAxes() {
        const xAxis = d3.axisBottom(this.xScale)
            .tickFormat(d3.format('$,.0s'));
        
        const yAxis = d3.axisLeft(this.yScale);
        
        this.g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${this.height})`)
            .call(xAxis);
        
        this.g.append('g')
            .attr('class', 'y-axis')
            .call(yAxis);
        
        this.g.append('text')
            .attr('class', 'x-axis-label')
            .attr('text-anchor', 'middle')
            .attr('x', this.width / 2)
            .attr('y', this.height + 40)
            .text('GDP per capita (USD)');
        
        this.g.append('text')
            .attr('class', 'y-axis-label')
            .attr('text-anchor', 'middle')
            .attr('transform', 'rotate(-90)')
            .attr('x', -this.height / 2)
            .attr('y', -50)
            .text('Fertility rate (births per woman)');
        
        this.g.append('text')
            .attr('class', 'chart-title')
            .attr('text-anchor', 'middle')
            .attr('x', this.width / 2)
            .attr('y', -5)
            .text(`GDP vs Fertility Rate - ${this.currentYear}`);
    }
    
    setupControls() {
        const yearSlider = d3.select('#year-slider');
        const yearDisplay = d3.select('#year-display');
        const playButton = d3.select('#play-button');
        
        yearSlider.on('input', (event) => {
            this.currentYear = +event.target.value;
            yearDisplay.text(this.currentYear);
            this.updateVisualization();
        });
        
        playButton.on('click', () => {
            this.togglePlay();
        });
    }
    
    populateCountrySelect() {
        const select = d3.select('#country-select');
        
        this.countries.forEach(country => {
            select.append('option')
                .attr('value', country.code)
                .text(country.name);
        });
        
        select.on('change', (event) => {
            this.highlightCountry(event.target.value);
        });
    }
    
    updateVisualization() {
        if (!this.data) return;
        
        const yearData = this.getDataForYear(this.currentYear);
        
        d3.select('.chart-title')
            .text(`GDP vs Fertility Rate - ${this.currentYear}`);
        
        const circles = this.g.selectAll('.country-circle')
            .data(yearData, d => d.country);
        
        circles.exit().remove();
        
        const circlesEnter = circles.enter()
            .append('circle')
            .attr('class', 'country-circle')
            .attr('r', 0)
            .style('opacity', 0.7)
            .style('stroke', '#fff')
            .style('stroke-width', 1);
        
        circles.merge(circlesEnter)
            .transition()
            .duration(500)
            .attr('cx', d => this.xScale(d.gdp))
            .attr('cy', d => this.yScale(d.fertility))
            .attr('r', 6)
            .style('fill', d => this.colorScale(d.region || 'Unknown'));
        
        this.addTooltips();
    }
    
    getDataForYear(year) {
        if (!this.data) return [];
        
        const yearData = [];
        
        for (const countryCode in this.data.countries) {
            const country = this.data.countries[countryCode];
            const gdp = country.gdp[year];
            const fertility = country.fertility[year];
            
            if (gdp && fertility && gdp > 0 && fertility > 0) {
                const countryInfo = this.countries.find(c => c.code === countryCode);
                yearData.push({
                    country: countryCode,
                    name: countryInfo ? countryInfo.name : countryCode,
                    gdp: gdp,
                    fertility: fertility,
                    region: countryInfo ? countryInfo.region : 'Unknown'
                });
            }
        }
        
        return yearData;
    }
    
    addTooltips() {
        const tooltip = d3.select('body').selectAll('.tooltip')
            .data([0])
            .enter().append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('padding', '10px')
            .style('background', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('border-radius', '5px')
            .style('pointer-events', 'none')
            .style('opacity', 0);
        
        this.g.selectAll('.country-circle')
            .on('mouseover', (event, d) => {
                tooltip.transition()
                    .duration(200)
                    .style('opacity', 0.9);
                
                tooltip.html(`
                    <strong>${d.name}</strong><br/>
                    GDP per capita: $${d3.format(',.0f')(d.gdp)}<br/>
                    Fertility rate: ${d3.format('.2f')(d.fertility)}
                `)
                    .style('left', (event.pageX + 10) + 'px')
                    .style('top', (event.pageY - 28) + 'px');
            })
            .on('mouseout', () => {
                tooltip.transition()
                    .duration(500)
                    .style('opacity', 0);
            });
    }
    
    highlightCountry(countryCode) {
        this.g.selectAll('.country-circle')
            .style('stroke-width', d => d.country === countryCode ? 3 : 1)
            .style('stroke', d => d.country === countryCode ? '#ff6b35' : '#fff')
            .style('opacity', d => {
                if (!countryCode) return 0.7;
                return d.country === countryCode ? 1 : 0.3;
            });
    }
    
    togglePlay() {
        const playButton = d3.select('#play-button');
        
        if (this.isPlaying) {
            this.stopAnimation();
            playButton.text('Play');
        } else {
            this.startAnimation();
            playButton.text('Pause');
        }
        
        this.isPlaying = !this.isPlaying;
    }
    
    startAnimation() {
        const yearSlider = d3.select('#year-slider');
        const yearDisplay = d3.select('#year-display');
        
        this.playInterval = setInterval(() => {
            this.currentYear++;
            
            if (this.currentYear > 2023) {
                this.currentYear = 1960;
            }
            
            yearSlider.property('value', this.currentYear);
            yearDisplay.text(this.currentYear);
            this.updateVisualization();
        }, 500);
    }
    
    stopAnimation() {
        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
    }
    
    showError(message) {
        const container = d3.select('.visualization-container');
        container.selectAll('*').remove();
        
        container.append('div')
            .attr('class', 'error-message')
            .style('text-align', 'center')
            .style('padding', '50px')
            .style('color', '#dc3545')
            .text(message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new GDPFertilityVisualization();
});