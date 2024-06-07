document.addEventListener("DOMContentLoaded", function() {
    let comparisonData;
    try {
        comparisonData = JSON.parse(comparison_data);
    } catch (error) {
        console.error('Error parsing JSON:', error);
        return;
    }

    // Implement the error function (erf) in JavaScript
    function erf(x) {
        const a1 =  0.254829592;
        const a2 = -0.284496736;
        const a3 =  1.421413741;
        const a4 = -1.453152027;
        const a5 =  1.061405429;
        const p  =  0.3275911;

        const sign = x >= 0 ? 1 : -1;
        x = Math.abs(x);

        const t = 1.0 / (1.0 + p * x);
        const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

        return sign * y;
    }

    function zScoreToPercentile(zScore) {
        return (1 + erf(zScore / Math.sqrt(2))) / 2;
    }

    if (comparisonData && comparisonData.teams && comparisonData.teams.length >= 2) {
        const teamA = comparisonData.teams[0];
        const teamB = comparisonData.teams[1];

        const labels = [
            'Goals Scored',
            'Goals Allowed',
            'Shots on Target',
            'Saves',
            'Possession'
        ];

        const teamAData = [
            zScoreToPercentile(teamA.metrics.goals_scored),
            zScoreToPercentile(teamA.metrics.goals_allowed),
            zScoreToPercentile(teamA.metrics.shots_on_target),
            zScoreToPercentile(teamA.metrics.saves),
            zScoreToPercentile(teamA.metrics.possession)
        ];

        const teamBData = [
            zScoreToPercentile(teamB.metrics.goals_scored),
            zScoreToPercentile(teamB.metrics.goals_allowed),
            zScoreToPercentile(teamB.metrics.shots_on_target),
            zScoreToPercentile(teamB.metrics.saves),
            zScoreToPercentile(teamB.metrics.possession)
        ];

        const barData = {
            labels: labels,
            datasets: [
                {
                    label: teamA.name,
                    data: teamAData,
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    barPercentage: 0.5,
                    categoryPercentage: 0.5
                },
                {
                    label: teamB.name,
                    data: teamBData,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1,
                    barPercentage: 0.5,
                    categoryPercentage: 0.5
                }
            ]
        };

        const barOptions = {
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: 1,
                    min: 0,
                    title: {
                        display: true,
                        text: 'Percentile'
                    },
                    grid: {
                        color: function(context) {
                            return '#e0e0e0'; // Grid lines
                        }
                    },
                    ticks: {
                        callback: function(value) {
                            return `${Math.round(value * 100)}`;
                        }
                    }
                },
                y: {
                    stacked: false
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += `${Math.round(context.raw * 100)}`;
                            return label;
                        }
                    }
                },
                datalabels: {
                    anchor: 'end',
                    align: 'end',
                    formatter: function(value, context) {
                        return `${Math.round(value * 100)}`;
                    }
                }
            }
        };

        Chart.register({
            id: 'quartileBackground',
            beforeDraw: function(chart) {
                const ctx = chart.ctx;
                const chartArea = chart.chartArea;
                const left = chartArea.left;
                const right = chartArea.right;
                const top = chartArea.top;
                const bottom = chartArea.bottom;

                const quartiles = [
                    { value: 0.25, color: 'rgba(255, 0, 0, 0.1)' }, // 0-25th percentile (light red)
                    { value: 0.50, color: 'rgba(255, 165, 0, 0.1)' }, // 25-50th percentile (light orange)
                    { value: 0.75, color: 'rgba(255, 255, 0, 0.1)' }, // 50-75th percentile (light yellow)
                    { value: 1.00, color: 'rgba(0, 128, 0, 0.1)' }  // 75-100th percentile (light green)
                ];

                quartiles.forEach(function(quartile, index) {
                    ctx.fillStyle = quartile.color;
                    const x = left + (quartile.value * (right - left));
                    ctx.fillRect(index === 0 ? left : left + quartiles[index - 1].value * (right - left), top, quartile.value * (right - left), bottom - top);
                });
            }
        });

        const barCtx = document.getElementById('comparisonChart').getContext('2d');
        new Chart(barCtx, {
            type: 'bar',
            data: barData,
            options: barOptions,
            plugins: [ChartDataLabels, 'quartileBackground']
        });
    } else {
        console.error('Data structure is incorrect or incomplete');
    }
});
